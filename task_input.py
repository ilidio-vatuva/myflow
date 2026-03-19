from turtle import update

import requests
import os

from telegram import Update
from main import process_task
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from database import init_db, insert_user, get_user_by_telegram_id
from web_server import generate_oauth_url
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

async def reply_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn , cursor = init_db()
    user = get_user_by_telegram_id(cursor, update.message.from_user.id)
    if not user:
        user_id = insert_user(conn, cursor, update.message.from_user.username, update.message.from_user.id)
        if not user_id:
            await update.message.reply_text("An error occurred while registering you. Please contact the administrator.")
            return
        send_oauth_prompt(update, update.message.from_user.id, "Welcome to Sir Agent! 👋 Please connect your Google Calendar to get started:")
        return
    else:
        if user and not user[3]:  # Check if google_token is not set
            send_oauth_prompt(update, update.message.from_user.id, "Please connect your Google Calendar to use Sir Agent:")
            return
        else:
            task=update.message.text
            data=process_task(task)
            message=format_output_msg(data)
            await update.message.reply_text(message)

async def send_oauth_prompt(update, telegram_user_id, message):
    auth_url = generate_oauth_url(telegram_user_id)
    keyboard = [[InlineKeyboardButton("🔗 Connect Google Calendar", url=auth_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)

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

token=os.getenv('TELEGRAM_BOT_TOKEN')
app = ApplicationBuilder().token(token).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_telegram))

webhook_url = os.getenv('WEBHOOK_URL')
app.run_webhook(
    listen="0.0.0.0",
    port=8000,
    webhook_url=webhook_url
)