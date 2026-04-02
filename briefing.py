import datetime
import pytz
from database import get_all_users, init_db, get_tasks_by_user_id, get_projects_by_user_id, get_tasks_by_project_id
from calendar_manager import get_today_events
from translations import t
from task_input import get_bot
from prompts import send_projects_list
from models import User

madrid_tz = pytz.timezone('Europe/Madrid')

def get_idle_projects(cursor, user_id):
    projects = get_projects_by_user_id(cursor, user_id)
    idle = []
    for project in projects:
        tasks = get_tasks_by_project_id(cursor, project.id, status="pending")
        if not tasks:
            idle.append(project)
    return idle

def format_event_time(event):
    start = event.get("start", {})
    if "dateTime" in start:
        dt = datetime.datetime.fromisoformat(start["dateTime"])
        return dt.astimezone(madrid_tz).strftime("%H:%M")
    return t("all_day", "en-US")

def format_daily_briefing(user, events, pending_tasks):
    lang = user.language
    lines = [t("briefing_greeting", lang).format(nickname=user.nickname), ""]
    
    lines.append(t("briefing_calendar", lang))
    if events:
        for event in events:
            time = format_event_time(event)
            title = event.get("summary", "No title")
            lines.append(f"  • {time} — {title}")
    else:
        lines.append(f"  {t('briefing_no_events', lang)}")
    
    lines.append("")
    lines.append(t("briefing_tasks", lang))
    if pending_tasks:
        for task in pending_tasks:
            lines.append(f"  • {task.title}")
    else:
        lines.append(f"  {t('briefing_no_tasks', lang)}")
    
    return "\n".join(lines)

async def send_daily_briefing():
    bot = get_bot()
    conn, cursor = init_db()
    users = get_all_users(cursor)
    
    for user in users:
        try:
            events = get_today_events(user.google_token)
            pending_tasks = get_tasks_by_user_id(cursor, user.id, status="pending")
            message = format_daily_briefing(user, events, pending_tasks)
            await bot.bot.send_message(chat_id=user.telegram_id, text=message)
        except Exception as e:
            print(f"Error sending daily briefing to {user.nickname}: {e}")

async def send_weekly_planning():
    bot = get_bot()
    conn, cursor = init_db()
    users = get_all_users(cursor)

    for user in users:
        try:
            idle_projects = get_idle_projects(cursor, user.id)
            lang = user.language
            message = t("planning_greeting", lang).format(nickname=user.nickname)
            if idle_projects:
                message += f"\n\n{t('planning_idle_projects', lang)}"
            else:
                message += f"\n\n{t('planning_no_idle', lang)}"
            await bot.bot.send_message(chat_id=user.telegram_id, text=message)
            if idle_projects:
                await send_projects_list(
                    await bot.bot.send_message(chat_id=user.telegram_id, text="👇"),
                    idle_projects,
                    lang
                )
        except Exception as e:
            print(f"Error sending weekly planning to {user.nickname}: {e}")