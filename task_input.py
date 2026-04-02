import datetime
import os
import secrets

from oauthlib.uri_validate import query
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from calendar_manager import TokenExpiredError, delete_event
from main import process_task
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
from database import clear_google_token, complete_goal, complete_project, create_dashboard_token, create_dashboard_token, delete_goal, delete_project, delete_task, get_goal_by_id, get_progress_stats, get_project_by_id, get_projects_by_user_id, get_task_by_id, get_tasks_by_project_id, get_tasks_by_user_id, init_db, insert_goal, insert_project, insert_user, get_user_by_telegram_id, get_goals_by_user_id, get_projects_by_goal_id, insert_task, reopen_goal, reopen_project, update_goal, update_project, update_task, update_task_status, update_user
from session import SessionState, get_session, clear_session, update_session
from prompts import MAIN_MENU_KEYBOARD, send_confirmation_prompt, send_due_date_prompt, send_edit_due_date_prompt, send_edit_goal_importance_prompt, send_edit_goal_menu, send_edit_preferred_language_prompt, send_edit_project_frequency_prompt, send_edit_project_hours_prompt, send_edit_project_menu, send_goal_importance_prompt, send_goals_list, send_main_menu, send_oauth_prompt, send_preferred_language_prompt, send_project_daily_hours_prompt, send_project_frequency_prompt, send_project_monthly_hours_prompt, send_project_planning_menu, send_project_weekly_hours_prompt, send_projects_list, send_projects_prompt, send_goals_prompt, send_deadline_prompt, send_tasks_list, send_settings_menu
from translations import t

if os.path.exists('.env'):
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
        session = get_session(telegram_user_id)
        if session["state"] == SessionState.WAITING_FOR_NICKNAME:
            preferred_language = session.get("preferred_language", "en-US")
            nickname = update.message.text
            user_id = insert_user(conn, cursor, nickname, telegram_user_id, None, preferred_language)
            if not user_id:
                await update.message.reply_text(t("registration_error", preferred_language))
                return
            await send_oauth_prompt(update.message, update.message.from_user.id, t("oauth_welcome_nickname", preferred_language).format(nickname=nickname))
            return
        else:
            update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PREFERRED_LANGUAGE})
            await send_preferred_language_prompt(update.message)
            return
    else:
        if user and not user.google_token:
            await send_oauth_prompt(update.message, update.message.from_user.id, t("oauth_reconnect", user.language))
            return
        else:
            if update.message.text == "📋 Menu":
                await send_main_menu(update.message, user)
                return
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
                await send_projects_prompt(update.message, user_projects, user.language)

            elif session["state"] == SessionState.WAITING_FOR_PROJECT_NAME:
                update_session(telegram_user_id, {"project_name": update.message.text })
                update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PROJECT_DESC})
                await update.message.reply_text(t("project_description_prompt", user.language))

            elif session["state"] == SessionState.WAITING_FOR_PROJECT_DESC:
                update_session(telegram_user_id, {"project_description": update.message.text})
                update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PROJECT_FREQUENCY})
                await send_project_frequency_prompt(update.message, user.language)

            elif session["state"] == SessionState.WAITING_FOR_GOAL_NAME:
                update_session(telegram_user_id, {"goal_name": update.message.text})
                update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_GOAL_DESC})
                await update.message.reply_text(t("goal_description_prompt", user.language))

            elif session["state"] == SessionState.WAITING_FOR_GOAL_DESC:
                update_session(telegram_user_id, {"goal_description": update.message.text})
                update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_GOAL_IMPORTANCE})
                await send_goal_importance_prompt(update.message, user.language)

            elif session["state"] == SessionState.EDITING_GOAL_NAME:
                goal_id = session.get("goal_id")
                update_goal(conn, cursor, goal_id, name=update.message.text)
                clear_session(telegram_user_id)
                await update.message.reply_text(t("goal_updated", user.language))
                goals = get_goals_by_user_id(cursor, user.id)
                await send_goals_list(update.message, goals, user.language)

            elif session["state"] == SessionState.EDITING_GOAL_DESC:
                goal_id = session.get("goal_id")
                update_goal(conn, cursor, goal_id, description=update.message.text)
                clear_session(telegram_user_id)
                await update.message.reply_text(t("goal_updated", user.language))
                goals = get_goals_by_user_id(cursor, user.id)
                await send_goals_list(update.message, goals, user.language)
                
            elif session["state"] == SessionState.EDITING_PROJECT_NAME:
                project_id = session.get("project_id")
                update_project(conn, cursor, project_id, name=update.message.text)
                clear_session(telegram_user_id)
                await update.message.reply_text(t("project_updated", user.language))
                projects = get_projects_by_user_id(cursor, user.id)
                await send_projects_list(update.message, projects, user.language)

            elif session["state"] == SessionState.EDITING_PROJECT_DESC:
                project_id = session.get("project_id")
                update_project(conn, cursor, project_id, description=update.message.text)
                clear_session(telegram_user_id)
                await update.message.reply_text(t("project_updated", user.language))
                projects = get_projects_by_user_id(cursor, user.id)
                await send_projects_list(update.message, projects, user.language)

            elif session["state"] == SessionState.EDITING_NICKNAME:
                new_nickname = update.message.text
                update_user(conn, cursor, user.id, nickname=new_nickname)
                clear_session(telegram_user_id)
                user = get_user_by_telegram_id(cursor, user.telegram_id)
                await update.message.reply_text(t("nickname_updated", user.language).format(nickname=new_nickname))
                await send_main_menu(update.message, user)

            else:
                await update.message.reply_text(t("processing_error", user.language))
                clear_session(telegram_user_id)
                return


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    conn , cursor = init_db()
    
    telegram_user_id = update.effective_user.id
    user = get_user_by_telegram_id(cursor=cursor, telegram_id=telegram_user_id)
    if user and not user.google_token:
        await send_oauth_prompt(query.message, user.telegram_id, t("oauth_reconnect", user.language))
        return
    session = get_session(telegram_user_id)
    data = query.data

    if data == "new_project":
        goals = get_goals_by_user_id(cursor=cursor, user_id=user.id)
        await send_goals_prompt(query.message, goals, user.language)
    
    elif data.startswith("project_tasks_"):
        project_id = int(data.split("_")[-1])
        tasks = get_tasks_by_project_id(cursor, project_id, status="pending")
        update_session(telegram_user_id, {"project_id": project_id})
        await send_tasks_list(query.message, tasks, user.language)

    elif data.startswith("project_"):
        project_id = int(data.split("_")[1])
        update_session(telegram_user_id, {"project": project_id})
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_DEADLINE})
        await send_deadline_prompt(query.message, user.language)

    elif data.startswith("deadline_"):
        deadline = data.split("_")[1]
        project_id = session.get("project")
        task = session.get("task")

        project = get_project_by_id(cursor, project_id)
        goal = get_goal_by_id(cursor, project.goal_id)

        if task:
            metadata = {
                        "user_nickname": user.nickname,
                        "current_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "current_time_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M UTC"),
                        "earliest_schedule_time": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)).isoformat(),
                        "goal_name": goal.name, "goal_description": goal.description, "goal_importance": goal.importance, 
                        "project_name": project.name, "project_description": project.description, "project_due_date": project.due_date, "project_hours": project.hours, "project_frequency": project.frequency,
                        "task": task, "deadline": deadline }
            await query.message.reply_text(t("scheduling_task", user.language))
            try:
                result = process_task(user.google_token, metadata)
            except TokenExpiredError:
                clear_google_token(conn, cursor, user.id)
                await send_oauth_prompt(query.message, user.telegram_id, t("oauth_reconnect", user.language))
                return
            insert_task(
                conn, cursor,
                project_id=project_id,
                title=result["calendar_event"]["title"],
                status="pending",
                start_date=result["calendar_event"]["suggested_start_time"],
                end_date=result["calendar_event"]["suggested_end_time"],
                planned_duration=result["calendar_event"]["duration"],
                calendar_event_id=result["calendar_event"].get("id")
            )
            clear_session(telegram_user_id)
            await query.message.reply_text(format_output_msg(result))
            await query.message.reply_text("👇", reply_markup=MAIN_MENU_KEYBOARD)
        else:
            await query.message.reply_text(t("project_created_success", user.language))
            clear_session(telegram_user_id)
            projects = get_projects_by_user_id(cursor, user.id)
            await send_projects_list(query.message, projects, user.language)

    elif data.startswith("frequency_"):
        frequency = data.split("_")[1]
        update_session(telegram_user_id, {"project_frequency": frequency})
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PROJECT_HOURS})
        if frequency == "daily":
            await send_project_daily_hours_prompt(query.message, user.language)
        elif frequency == "weekly":
            await send_project_weekly_hours_prompt(query.message, user.language)
        elif frequency == "monthly":
            await send_project_monthly_hours_prompt(query.message, user.language)

    elif data.startswith("hours_"):
        hours = int(data.split("_")[1])
        update_session(telegram_user_id, {"project_hours": hours})
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PROJECT_DUE_DATE})
        await send_due_date_prompt(query.message, user.language)

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
        task = session.get("task")
        if task:
            # came from task creation flow
            update_session(telegram_user_id, {"project": project_id})
            update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_DEADLINE})
            await send_deadline_prompt(query.message, user.language)
        else:
            # came from project management flow
            await query.message.reply_text(t("project_created_success", user.language))
            clear_session(telegram_user_id)
            projects = get_projects_by_user_id(cursor, user.id)
            await send_projects_list(query.message, projects, user.language)
    
    elif data == "new_goal":
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_GOAL_NAME})
        await query.message.reply_text(t("new_goal_name", user.language))

    elif data.startswith("goal_importance_"):
        importance = int(data.split("_")[2])
        goal_name = session.get("goal_name")
        goal_description = session.get("goal_description")
        goal_id = insert_goal(conn, cursor, user.id, goal_name, importance, goal_description)
        if not goal_id:
            await query.message.reply_text(t("goal_creation_error", user.language))
            clear_session(telegram_user_id)
            return
        update_session(telegram_user_id, {"goal_id": goal_id})
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PROJECT_NAME})
        await query.message.reply_text(t("new_project_name", user.language))

    elif data.startswith("goalId_"):
        goal_id = int(data.split("_")[1])
        update_session(telegram_user_id, {"goal_id": goal_id})
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PROJECT_NAME})
        await query.message.reply_text(t("new_project_name", user.language))

    elif data.startswith("language_"):
        language = data.split("_")[1]
        update_session(telegram_user_id, {"preferred_language": language})
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_NICKNAME})
        await query.message.reply_text(t("welcome", language))   

    elif data.startswith("edit_language_"):
        language = data.split("_")[-1]
        update_user(conn, cursor, user.id, language=language)
        clear_session(telegram_user_id)
        user = get_user_by_telegram_id(cursor, user.telegram_id) 
        await query.message.reply_text(t("language_updated", language).format(language=t(f"language_name_{language}", language)))
        await send_main_menu(query.message, user)

    elif data == "menu_new_task":    
        goals = get_goals_by_user_id(cursor, user.id)
        if not goals:
            await query.message.reply_text(t("no_goals_yet", user.language))
            return
        clear_session(telegram_user_id)
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_TASK})
        await query.message.reply_text(t("send_task", user.language))

    elif data == "menu_goals":        
        goals = get_goals_by_user_id(cursor, user.id)
        await send_goals_list(query.message, goals, user.language)

    elif data.startswith("edit_goal_importance_"):
        importance = int(data.split("_")[-1])
        goal_id = session.get("goal_id")
        update_goal(conn, cursor, goal_id, importance=importance)
        clear_session(telegram_user_id)
        await query.message.reply_text(t("goal_updated", user.language))
        goals = get_goals_by_user_id(cursor, user.id)
        await send_goals_list(query.message, goals, user.language)

    elif data.startswith("edit_goal_"):
        goal_id = int(data.split("_")[-1])
        goal = get_goal_by_id(cursor, goal_id)
        update_session(telegram_user_id, {"goal_id": goal_id})
        await send_edit_goal_menu(query.message, goal, user.language)

    elif data.startswith("delete_goal_"):
        goal_id = int(data.split("_")[-1])
        update_session(telegram_user_id, {"goal_id": goal_id})
        await send_confirmation_prompt(query.message, "delete_goal", user.language)

    elif data.startswith("goal_projects_"):
        goal_id = int(data.split("_")[-1])
        projects = get_projects_by_goal_id(cursor, goal_id)
        await send_projects_list(query.message, projects, user.language)

    elif data.startswith("confirm_delete_goal_"):
        goal_id = session.get("goal_id")
        delete_goal(conn, cursor, goal_id)
        await query.message.reply_text(t("goal_deleted", user.language))
        await query.message.reply_text("👇", reply_markup=MAIN_MENU_KEYBOARD) 

    elif data.startswith("egoal_name_"):
        goal_id = int(data.split("_")[-1])
        update_session(telegram_user_id, {"goal_id": goal_id})
        update_session(telegram_user_id, {"state": SessionState.EDITING_GOAL_NAME})
        await query.message.reply_text(t("edit_goal_name", user.language))

    elif data.startswith("egoal_desc_"):
        goal_id = int(data.split("_")[-1])
        update_session(telegram_user_id, {"goal_id": goal_id})
        update_session(telegram_user_id, {"state": SessionState.EDITING_GOAL_DESC})
        await query.message.reply_text(t("edit_goal_desc", user.language))

    elif data.startswith("egoal_importance_"):
        goal_id = int(data.split("_")[-1])
        update_session(telegram_user_id, {"goal_id": goal_id})
        update_session(telegram_user_id, {"state": SessionState.EDITING_GOAL_IMPORTANCE})
        await send_edit_goal_importance_prompt(query.message, user.language)

    elif data == "menu_projects":
        goals = get_goals_by_user_id(cursor, user.id)
        user_projects = get_projects_by_user_id(cursor, user.id)
        await send_projects_list(query.message, user_projects, user.language)

    elif data.startswith("edit_project_"):
        project_id = int(data.split("_")[-1])
        project = get_project_by_id(cursor, project_id)
        update_session(telegram_user_id, {"project_id": project_id})
        update_session(telegram_user_id, {"goal_id": project.goal_id})
        await send_edit_project_menu(query.message, project, user.language)
    
    elif data.startswith("delete_project_"):
        project_id = int(data.split("_")[-1])
        update_session(telegram_user_id, {"project_id": project_id})
        await send_confirmation_prompt(query.message, "delete_project", user.language)
    
    elif data.startswith("confirm_delete_project"):
        project_id = session.get("project_id")
        delete_project(conn, cursor, project_id)
        await query.message.reply_text(t("project_deleted", user.language))
        await query.message.reply_text("👇", reply_markup=MAIN_MENU_KEYBOARD)

    elif data.startswith("eproject_name_"):
        project_id = int(data.split("_")[-1])
        update_session(telegram_user_id, {"project_id": project_id, "state": SessionState.EDITING_PROJECT_NAME})
        await query.message.reply_text(t("edit_project_name", user.language))
    
    elif data.startswith("eproject_desc_"):
        project_id = int(data.split("_")[-1])
        update_session(telegram_user_id, {"project_id": project_id, "state": SessionState.EDITING_PROJECT_DESC})
        await query.message.reply_text(t("edit_project_desc", user.language))
    
    elif data.startswith("eproject_frequency_"):
        project_id = int(data.split("_")[-1])
        update_session(telegram_user_id, {"project_id": project_id, "state": SessionState.EDITING_PROJECT_FREQUENCY})
        await send_edit_project_frequency_prompt(query.message, user.language)
    
    elif data.startswith("eproject_time_"):
        project_id = int(data.split("_")[-1])
        update_session(telegram_user_id, {"project_id": project_id, "state": SessionState.EDITING_PROJECT_HOURS})
        await send_edit_project_hours_prompt(query.message, user.language) 
    
    elif data.startswith("eproject_due_date_"):
        project_id = int(data.split("_")[-1])
        update_session(telegram_user_id, {"project_id": project_id, "state": SessionState.EDITING_PROJECT_DUE_DATE})
        await send_edit_due_date_prompt(query.message, user.language)

    elif data.startswith("edit_due_date_"):
        project_id = session.get("project_id")
        due_date = data.split("_")[-1]
        due_date = None if due_date == "none" else due_date
        update_project(conn, cursor, project_id, due_date=due_date)
        clear_session(telegram_user_id)
        await query.message.reply_text(t("project_updated", user.language))
        projects = get_projects_by_user_id(cursor, user.id)
        await send_projects_list(query.message, projects, user.language)

    elif data.startswith("edit_frequency_"):
        project_id = session.get("project_id")
        frequency = data.split("_")[-1]
        update_project(conn, cursor, project_id, frequency=frequency)
        clear_session(telegram_user_id)
        await query.message.reply_text(t("project_updated", user.language))
        projects = get_projects_by_user_id(cursor, user.id)
        await send_projects_list(query.message, projects, user.language)

    elif data.startswith("edit_hours_"):
        project_id = session.get("project_id")
        hours = int(data.split("_")[-1])
        update_project(conn, cursor, project_id, hours=hours)
        clear_session(telegram_user_id)
        await query.message.reply_text(t("project_updated", user.language))
        projects = get_projects_by_user_id(cursor, user.id)
        await send_projects_list(query.message, projects, user.language)

    elif data.startswith("complete_task_"):
        task_id = int(data.split("_")[-1])
        update_task_status(conn, cursor, task_id, "completed")
        await query.message.reply_text(t("task_completed", user.language))
        project_id = session.get("project_id")
        if project_id:
            tasks = get_tasks_by_project_id(cursor, project_id, status="pending")
        else:
            tasks = get_tasks_by_user_id(cursor, user.id, status="pending")
        await send_tasks_list(query.message, tasks, user.language)

    elif data.startswith("delete_task_"):
        task_id = int(data.split("_")[-1])
        update_session(telegram_user_id, {"task_id": task_id})
        await send_confirmation_prompt(query.message, "delete_task", user.language)

    elif data.startswith("confirm_delete_task"):
        task_id = session.get("task_id")
        task = get_task_by_id(cursor, task_id)
        if task.calendar_event_id:
            delete_event(user.google_token, task.calendar_event_id)
        delete_task(conn, cursor, task_id)
        await query.message.reply_text(t("task_deleted", user.language))
        project_id = session.get("project_id")
        if project_id:
            tasks = get_tasks_by_project_id(cursor, project_id, status="pending")
        else:
            tasks = get_tasks_by_user_id(cursor, user.id, status="pending")
        await send_tasks_list(query.message, tasks, user.language)

    elif data.startswith("reschedule_task_"):
        task_id = int(data.split("_")[-1])
        task = get_task_by_id(cursor, task_id)
        project = get_project_by_id(cursor, task.project_id)
        goal = get_goal_by_id(cursor, project.goal_id)
        
        metadata = {
            "user_nickname": user.nickname,
            "current_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "current_time_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M UTC"),
            "earliest_schedule_time": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)).isoformat(),
            "goal_name": goal.name, "goal_description": goal.description, "goal_importance": goal.importance,
            "project_name": project.name, "project_description": project.description, "project_due_date": project.due_date, "project_hours": project.hours, "project_frequency": project.frequency,
            "task": task.title, "deadline": "reschedule"
        }
        await query.message.reply_text(t("scheduling_task", user.language))
        try:
            result = process_task(user.google_token, metadata)
        except TokenExpiredError:
            clear_google_token(conn, cursor, user.id)
            await send_oauth_prompt(query.message, user.telegram_id, t("oauth_reconnect", user.language))
            return
        update_task(conn, cursor, task_id,
            start_date=result["calendar_event"]["suggested_start_time"],
            end_date=result["calendar_event"]["suggested_end_time"]
        )
        await query.message.reply_text(format_output_msg(result))
        await query.message.reply_text("👇", reply_markup=MAIN_MENU_KEYBOARD)
        project_id = session.get("project_id")
        if project_id:
            tasks = get_tasks_by_project_id(cursor, project_id, status="pending")
        else:
            tasks = get_tasks_by_user_id(cursor, user.id, status="pending")
        await send_tasks_list(query.message, tasks, user.language)
    
    elif data.startswith("new_task"):
        project_id = session.get("project_id")
        if not project_id:
            await query.message.reply_text(t("processing_error", user.language))
            return
        clear_session(telegram_user_id)
        update_session(telegram_user_id, {"project": project_id, "state": SessionState.WAITING_FOR_TASK})
        await query.message.reply_text(t("send_task", user.language))
    
    elif data == "menu_settings":
        await send_settings_menu(query.message, user)

    elif data.startswith("settings_nickname"):
        update_session(telegram_user_id, {"state": SessionState.EDITING_NICKNAME})
        await query.message.reply_text(t("enter_new_nickname", user.language))

    elif data.startswith("settings_language"):
        await send_edit_preferred_language_prompt(query.message)

    elif data == "main_menu":
        await send_main_menu(query.message, user)

    elif data == "menu_tasks":
        tasks = get_tasks_by_user_id(cursor, user.id, status="pending")
        await send_tasks_list(query.message, tasks, user.language)

    elif data.startswith("plan_project_"):
        project_id = int(data.split("_")[-1])
        project = get_project_by_id(cursor, project_id)
        await send_project_planning_menu(query.message, project, user.language)
    
    elif data.startswith("plan_suggest_"):
        project_id = int(data.split("_")[-1])
        project = get_project_by_id(cursor, project_id)
        goal = get_goal_by_id(cursor, project.goal_id)
        metadata = {
            "user_nickname": user.nickname,
            "current_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "current_time_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M UTC"),
            "earliest_schedule_time": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)).isoformat(),
            "goal_name": goal.name, "goal_description": goal.description, "goal_importance": goal.importance,
            "project_name": project.name, "project_description": project.description, 
            "project_due_date": project.due_date, "project_hours": project.hours, 
            "project_frequency": project.frequency,
            "task": "suggest a relevant next task for this project",
            "deadline": "this_week"
        }
        await query.message.reply_text(t("scheduling_task", user.language))
        result = process_task(user.google_token, metadata)
        insert_task(conn, cursor,
            project_id=project_id,
            title=result["calendar_event"]["title"],
            status="pending",
            start_date=result["calendar_event"]["suggested_start_time"],
            end_date=result["calendar_event"]["suggested_end_time"],
            planned_duration=result["calendar_event"]["duration"],
            calendar_event_id=result["calendar_event"].get("id")
        )
        await query.message.reply_text(format_output_msg(result))

    elif data.startswith("plan_create_"):
        project_id = int(data.split("_")[-1])
        update_session(telegram_user_id, {"project": project_id, "state": SessionState.WAITING_FOR_TASK})
        await query.message.reply_text(t("send_task", user.language))

    elif data.startswith("plan_skip_"):
        await query.message.reply_text(t("planning_skipped", user.language))
        await query.message.reply_text("👇", reply_markup=MAIN_MENU_KEYBOARD)

    elif data.startswith("complete_project_"):
        project_id = int(data.split("_")[-1])
        complete_project(conn, cursor, project_id)
        await query.message.reply_text(t("project_completed", user.language))
        # Check if all projects in goal are completed
        project = get_project_by_id(cursor, project_id)
        goal_projects = get_projects_by_goal_id(cursor, project.goal_id)
        if all(p.status == "completed" for p in goal_projects):
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🏁 " + t("btn_yes", user.language), callback_data=f"complete_goal_{project.goal_id}"),
                InlineKeyboardButton("📋 " + t("btn_no", user.language), callback_data="main_menu")
            ]])
            await query.message.reply_text(t("all_projects_done", user.language), reply_markup=keyboard)
        else:
            projects = get_projects_by_user_id(cursor, user.id)
            await send_projects_list(query.message, projects, user.language)
    
    elif data.startswith("complete_goal_"):
        goal_id = int(data.split("_")[-1])
        complete_goal(conn, cursor, goal_id)
        await query.message.reply_text(t("goal_completed", user.language))
        goals = get_goals_by_user_id(cursor, user.id)
        await send_goals_list(query.message, goals, user.language)
    
    elif data.startswith("reopen_project_"):
        project_id = int(data.split("_")[-1])
        reopen_project(conn, cursor, project_id)
        await query.message.reply_text(t("project_reopened", user.language))
        projects = get_projects_by_user_id(cursor, user.id)
        await send_projects_list(query.message, projects, user.language)
    
    elif data.startswith("reopen_goal_"):
        goal_id = int(data.split("_")[-1])
        reopen_goal(conn, cursor, goal_id)
        await query.message.reply_text(t("goal_reopened", user.language))
        goals = get_goals_by_user_id(cursor, user.id)
        await send_goals_list(query.message, goals, user.language)
    
    elif data == "menu_progress":
        token = secrets.token_urlsafe(32)
        create_dashboard_token(conn, cursor, user.id, token)
        webhook_url = os.getenv('WEBHOOK_URL', 'http://localhost:8000')
        dashboard_url = f"{webhook_url}/dashboard?token={token}"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("📊 " + t("open_dashboard", user.language), url=dashboard_url)
        ]])
        await query.message.reply_text(t("dashboard_ready", user.language), reply_markup=keyboard)

async def error_handler(update, context):
    print(f"Error: {context.error}")
    import traceback
    traceback.print_exc()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn, cursor = init_db()
    telegram_user_id = update.message.from_user.id
    user = get_user_by_telegram_id(cursor, telegram_user_id)
    
    if not user:
        # New user — start onboarding
        update_session(telegram_user_id, {"state": SessionState.WAITING_FOR_PREFERRED_LANGUAGE})
        await send_preferred_language_prompt(update.message)
        return
    await send_main_menu(update.message, user)



token=os.getenv('TELEGRAM_BOT_TOKEN')
app = ApplicationBuilder().token(token).build() if token else None

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_telegram))
app.add_handler(CallbackQueryHandler(handle_button))
app.add_error_handler(error_handler)
app.add_handler(CommandHandler("start", start_command))

