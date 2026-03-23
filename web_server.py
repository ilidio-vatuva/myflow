import os

from fastapi import FastAPI, Request
from dotenv import load_dotenv
from database import update_user, get_user_by_telegram_id, init_db
from oauth import fetch_token
from task_input import get_bot
from telegram import Update
from task_input import app as telegram_app
from translations import t
from contextlib import asynccontextmanager
from session import get_session, clear_session

load_dotenv()

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await telegram_app.initialize()
    if os.path.exists('.env'):
        await telegram_app.start()
        await telegram_app.updater.start_polling()
    else:
        webhook_url = os.getenv('WEBHOOK_URL')
        await telegram_app.bot.set_webhook(f"{webhook_url}/telegram/webhook")
    yield
    # Shutdown
    if os.path.exists('.env'):
        await telegram_app.updater.stop()
        await telegram_app.stop()
    await telegram_app.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/oauth/callback")
async def oauth_callback(code: str, state: str):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # only for development!
    token = fetch_token(state, code)
    user_telegram_id = int(state)
    conn, cursor = init_db()
    user = get_user_by_telegram_id(cursor, user_telegram_id)
    if user:
        update_user(conn, cursor, user.id, google_token=token.to_json())
        bot = get_bot()
        session = get_session(user_telegram_id)
        preferred_language = session.get("preferred_language", user.language)
        clear_session(user_telegram_id)  # clear session after successful connection
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


