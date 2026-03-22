import datetime
import os

from telegram import Update
from main import process_task
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
from database import get_goal_by_id, get_project_by_id, init_db, insert_goal, insert_project, insert_user, get_user_by_telegram_id, get_goals_by_user_id, get_projects_by_goal_id, insert_task
from session import SessionState, get_session, clear_session, update_session
from prompts import send_due_date_prompt, send_goal_importance_prompt, send_oauth_prompt, send_project_daily_hours_prompt, send_project_frequency_prompt, send_project_monthly_hours_prompt, send_project_weekly_hours_prompt, send_projects_prompt, send_goals_prompt, send_deadline_prompt

load_dotenv()

def format_output_msg(data):
    assumptions=''
    for assumption in data["notes"]["assumptions"]:
        assumptions = assumptions + f'- {assumption} \n'

    risks=''
    for risk in data["notes"]["risks"]:
        risks = risks + f'- {risk} \n'

    return f"""✅ Scheduled: {data["calendar_event"]["title"]} — {data["schedule"]["recommended_slot"]}\n\n\n📝 Assumptions:\n{assumptions}\n\n⚠️ Risks:\n{risks}"""

def get_bot():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    return ApplicationBuilder().token(token).build()

async def reply_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    conn , cursor = init_db()
    telegram_user_id = update.message.from_user.id
    
    user = get_user_by_telegram_id(cursor, telegram_user_id)

    if not user:
        user_id = insert_user(conn, cursor, update.message.from_user.username, telegram_user_id)
        if not user_id:
            await update.message.reply_text("An error occurred while registering you. Please contact the administrator.")
            return
        await send_oauth_prompt(update.message, update.message.from_user.id, "Welcome to Sir Agent 👑! 👋 Please connect your Google Calendar to get started:")
        return
    else:
        if user and not user.google_token:
            await send_oauth_prompt(update.message, update.message.from_user.id, "Please connect your Google Calendar to use Sir Agent 👑:")
            return
        else:
            session = get_session(telegram_user_id)
            if session["state"] == SessionState.WAITING_FOR_TASK:
                clear_session(telegram_user_id)
                update_session(telegram_user_id, {"task": update.message.text})
                update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PROJECT})
                goals = get_goals_by_user_id(cursor, user.id)
                user_projects = []
                for goal in goals:
                    projects = get_projects_by_goal_id(cursor, goal.id)
                    user_projects.extend(projects)
                await send_projects_prompt(update.message, user_projects)
            elif session["state"] == SessionState.WAITING_FOR_PROJECT_NAME:
                update_session(telegram_user_id, {"project_name": update.message.text })
                update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PROJECT_DESC})
                await update.message.reply_text("Please provide a description for your project 📁")
            elif session["state"] == SessionState.WAITING_FOR_PROJECT_DESC:
                update_session(telegram_user_id, {"project_description": update.message.text})
                update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PROJECT_FREQUENCY})
                await send_project_frequency_prompt(update.message)
            elif session["state"] == SessionState.WAITING_FOR_GOAL_NAME:
                update_session(telegram_user_id, {"goal_name": update.message.text})
                update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_GOAL_DESC})
                await update.message.reply_text("Please provide a description for your goal 🎯")
            elif session["state"] == SessionState.WAITING_FOR_GOAL_DESC:
                update_session(telegram_user_id, {"goal_description": update.message.text})
                update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_GOAL_IMPORTANCE})
                await send_goal_importance_prompt(update.message)
            else:
                await update.message.reply_text("An error occurred while processing your request. Please try again.")
                clear_session(telegram_user_id)
                return


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    conn , cursor = init_db()
    
    telegram_user_id = update.effective_user.id
    user = get_user_by_telegram_id(cursor=cursor, telegram_id=telegram_user_id)
    session = get_session(telegram_user_id)
    data = query.data

    if data == "new_project":

        goals = get_goals_by_user_id(cursor=cursor, user_id=user.id)
        await send_goals_prompt(query.message, goals)

    elif data.startswith("project_"):

        project_id = int(data.split("_")[1])
        update_session(telegram_user_id, {"project": project_id})
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_DEADLINE})
        await send_deadline_prompt(query.message)

    elif data.startswith("deadline_"):

        deadline = data.split("_")[1]
        project_id = session.get("project")
        task = session.get("task")

        project = get_project_by_id(cursor, project_id)
        goal = get_goal_by_id(cursor, project.goal_id)

        metadata = {
                    "current_date": datetime.datetime.now().isoformat(),
                    "goal_name": goal.name, "goal_description": goal.description, "goal_importance": goal.importance, 
                    "project_name": project.name, "project_description": project.description, "project_due_date": project.due_date, "project_hours": project.hours, "project_frequency": project.frequency,
                    "task": task, "deadline": deadline }
        
        result = process_task(user.google_token, metadata)
        # TODO: handle result and save task
        await query.message.reply_text(format_output_msg(result))
        clear_session(telegram_user_id)

    elif data.startswith("frequency_"):

        frequency = data.split("_")[1]
        update_session(telegram_user_id, {"project_frequency": frequency})
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PROJECT_HOURS})
        if frequency == "daily":
            await send_project_daily_hours_prompt(query.message)
        elif frequency == "weekly":
            await send_project_weekly_hours_prompt(query.message)
        elif frequency == "monthly":
            await send_project_monthly_hours_prompt(query.message)

    elif data.startswith("hours_"):

        hours = int(data.split("_")[1])
        update_session(telegram_user_id, {"project_hours": hours})
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PROJECT_DUE_DATE})
        await send_due_date_prompt(query.message)

    elif data.startswith("due_date_"):

        due_date = data.split("_")[2]
        due_date = None if due_date == "none" else due_date
        update_session(telegram_user_id, {"project_due_date": due_date})
        project_name = session.get("project_name")
        project_description = session.get("project_description")
        project_frequency = session.get("project_frequency")
        project_hours = session.get("project_hours")
        goal_id = session.get("goal_id")

        project_id = insert_project(conn, cursor, goal_id, project_name, project_description, due_date, project_hours, project_frequency)
        if not project_id:
            await query.message.reply_text("An error occurred while creating the project. Please try again.")
            clear_session(telegram_user_id)
            return
        update_session(telegram_user_id, {"project": project_id})
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_DEADLINE})
        await send_deadline_prompt(query.message)

    elif data == "new_goal":
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_GOAL_NAME})
        await query.message.reply_text("What is the name of your new goal? 🎯")

    elif data.startswith("goal_importance_"):

        importance = int(data.split("_")[2])
        goal_name = session.get("goal_name")
        goal_description = session.get("goal_description")
        goal_id = insert_goal(conn, cursor, user.id, goal_name, importance, goal_description)
        if not goal_id:
            await query.message.reply_text("An error occurred while creating the goal. Please try again.")
            clear_session(telegram_user_id)
            return
        update_session(telegram_user_id, {"goal_id": goal_id})
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PROJECT_NAME})
        await query.message.reply_text("What is the name of your new project? 📁")

    elif data.startswith("goalId_"):

        goal_id = int(data.split("_")[1])
        update_session(telegram_user_id, {"goal_id": goal_id})
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PROJECT_NAME})
        await query.message.reply_text("What is the name of your new project? 📁")
            

token=os.getenv('TELEGRAM_BOT_TOKEN')
app = ApplicationBuilder().token(token).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_telegram))
app.add_handler(CallbackQueryHandler(handle_button))

