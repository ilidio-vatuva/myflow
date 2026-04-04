import os

from fastapi import FastAPI, Request
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import get_goals_by_user_id, get_progress_stats, get_projects_by_goal_id, get_tasks_by_project_id, get_tasks_by_user_id, get_user_by_dashboard_token, update_user, get_user_by_telegram_id, init_db, get_user_by_telegram_id
from oauth import fetch_token
from bot import get_bot
from telegram import Update
from bot import app as telegram_app
from translations import t
from contextlib import asynccontextmanager
from session import get_session, clear_session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from briefing import send_daily_briefing, send_weekly_planning

load_dotenv()

scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Madrid'))
templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await telegram_app.initialize()
    scheduler.add_job(send_daily_briefing, 'cron', hour=8, minute=0)
    scheduler.add_job(send_weekly_planning, 'cron', day_of_week='sun', hour=17, minute=0)
    scheduler.start()
    if os.path.exists('.env'):
        await telegram_app.start()
        await telegram_app.updater.start_polling()
    else:
        webhook_url = os.getenv('WEBHOOK_URL')
        await telegram_app.bot.set_webhook(f"{webhook_url}/telegram/webhook")
    yield
    if os.path.exists('.env'):
        await telegram_app.updater.stop()
        await telegram_app.stop()
    scheduler.shutdown()
    await telegram_app.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/oauth/callback")
async def oauth_callback(code: str, state: str):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    token = fetch_token(state, code)
    user_telegram_id = int(state)
    conn, cursor = init_db()
    user = get_user_by_telegram_id(cursor, user_telegram_id)
    if user:
        update_user(conn, cursor, user.id, google_token=token.to_json())
        bot = get_bot()
        session = get_session(user_telegram_id)
        preferred_language = session.get("preferred_language", user.language)
        clear_session(user_telegram_id)
        await bot.bot.send_message(chat_id=user_telegram_id, text=t("calendar_connected", preferred_language))
        return {"message": "Google Calendar connected successfully!"}
    else:
        return {"message": "User not found. Please contact the administrator."}

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"OK": True}

@app.get("/test/daily-briefing") # http://localhost:8000/test/daily-briefing
async def test_daily_briefing():
    await send_daily_briefing()
    return {"message": "Daily briefing sent!"}

@app.get("/test/weekly-planning") # http://localhost:8000/test/weekly-planning
async def test_weekly_planning():
    await send_weekly_planning()
    return {"message": "Weekly planning sent!"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, token: str):
    conn, cursor = init_db()
    user = get_user_by_dashboard_token(cursor, token)
    if not user:
        return HTMLResponse("<h1>Link expired or invalid.</h1>", status_code=401)
    
    stats = get_progress_stats(cursor, user.id)
    goals = get_goals_by_user_id(cursor, user.id)
    pending_tasks = get_tasks_by_user_id(cursor, user.id, status="pending")
    
    # Build goals with projects
    goals_with_projects = []
    for goal in goals:
        projects = get_projects_by_goal_id(cursor, goal.id)
        projects_with_tasks = []
        for project in projects:
            tasks = get_tasks_by_project_id(cursor, project.id, status="pending")
            projects_with_tasks.append({"project": project, "task_count": len(tasks)})
        goals_with_projects.append({"goal": goal, "projects": projects_with_tasks})

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "goals_with_projects": goals_with_projects,
        "pending_tasks": pending_tasks[:10],
        "total_tasks": stats['pending_tasks'] + stats['completed_tasks'],
        "total_projects": stats['active_projects'] + stats['completed_projects'],
        "total_goals": stats['active_goals'] + stats['completed_goals'],
        "task_pct": round((stats['completed_tasks'] / (stats['pending_tasks'] + stats['completed_tasks']) * 100) if (stats['pending_tasks'] + stats['completed_tasks']) > 0 else 0),
        "project_pct": round((stats['completed_projects'] / (stats['active_projects'] + stats['completed_projects']) * 100) if (stats['active_projects'] + stats['completed_projects']) > 0 else 0),
        "goal_pct": round((stats['completed_goals'] / (stats['active_goals'] + stats['completed_goals']) * 100) if (stats['active_goals'] + stats['completed_goals']) > 0 else 0),
    })