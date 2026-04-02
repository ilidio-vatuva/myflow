import os

from fastapi import FastAPI, Request
from dotenv import load_dotenv
from database import update_user, get_user_by_telegram_id, init_db, get_user_by_telegram_id
from oauth import fetch_token
from task_input import get_bot
from telegram import Update
from task_input import app as telegram_app
from translations import t
from contextlib import asynccontextmanager
from session import get_session, clear_session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from briefing import send_daily_briefing, send_weekly_planning

load_dotenv()

scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Madrid'))

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
