import os

from fastapi import FastAPI
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv
from database import update_user, get_user_by_telegram_id, init_db
from task_input import get_bot

load_dotenv()

app = FastAPI()
@app.get("/oauth/callback")
async def oauth_callback(code: str, state: str):
    flow = get_oauth_flow()
    flow.fetch_token(code=code)
    token = flow.credentials
    user_telegram_id = int(state)
    conn, cursor = init_db()
    user = get_user_by_telegram_id(cursor, user_telegram_id)
    if user:
        update_user(conn, cursor, user[0], google_token=token.to_json())
        bot = get_bot()
        await bot.bot.send_message(chat_id=user_telegram_id, text="✅ Google Calendar connected! You're ready to use Sir Agent!")
        return {"message": "Google Calendar connected successfully!"}
    else:
        return {"message": "User not found. Please contact the administrator."}

def generate_oauth_url(telegram_user_id):
    flow = get_oauth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent', state=str(telegram_user_id))
    return auth_url

def get_oauth_flow():
    webhook_url = os.getenv('WEBHOOK_URL')
    return Flow.from_client_secrets_file(
        'web_credentials.json',
        scopes=['https://www.googleapis.com/auth/calendar.events'],
        redirect_uri=f'{webhook_url}/oauth/callback'
    )