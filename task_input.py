import requests
import os

from telegram import Update
from main import process_task
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

async def reply_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task=update.message.text
    data=process_task(task)
    message=format_output_msg(data)
    await update.message.reply_text(message)

def format_output_msg(data):
    assumptions=''
    for assumption in data["notes"]["assumptions"]:
        assumptions = assumptions + f'- {assumption} \n'

    risks=''
    for risk in data["notes"]["risks"]:
        risks = risks + f'- {risk} \n'

    return f"""✅ Scheduled: {data["calendar_event"]["title"]} — {data["schedule"]["recommended_slot"]}\n\n\n📝 Assumptions:\n{assumptions}\n\n⚠️ Risks:\n{risks}"""

token=os.getenv('TELEGRAM_BOT_TOKEN')
app = ApplicationBuilder().token(token).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_telegram))

webhook_url = os.getenv('WEBHOOK_URL')
app.run_webhook(
    listen="0.0.0.0",
    port=8000,
    webhook_url=webhook_url
)