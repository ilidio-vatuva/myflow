import datetime
import sqlite3
import os

from models import User, Goal, Project, Task, Conversation
from typing import Optional

_conn = None
_cursor = None
DB_PATH = os.getenv('DB_PATH', 'myflow.db')

def init_db():
    global _conn, _cursor
    if not _conn:
        _conn = sqlite3.connect(DB_PATH)
        _cursor = _conn.cursor()
        create_tables(_conn, _cursor)
    return _conn, _cursor

def create_tables(conn, cursor):
    cursor.execute('''
        create table if not exists user (
            id integer primary key autoincrement,
            nickname text not null,
            telegram_id text not null unique,
            google_token text,
            language text default 'en-US'
        )
    ''')
    cursor.execute('''
        create table if not exists goals (
            id integer primary key autoincrement,
            user_id integer not null references user(id) on delete cascade,
            name text not null,
            importance integer not null,
            description text,
            status text default 'active'
        )
    ''')
    cursor.execute('''
        create table if not exists projects (
            id integer primary key autoincrement,
            goal_id integer not null references goals(id) on delete cascade,
            name text not null,
            description text,
            due_date date,
            hours integer,
            frequency text,
            status text default 'active'
        )
    ''')
    cursor.execute('''
        create table if not exists tasks (
            id integer primary key autoincrement,
            project_id integer not null references projects(id) on delete cascade,
            title text not null,
            status varchar(50) not null,
            start_date date,
            end_date date,
            planned_duration integer,
            spent_time integer,
            calendar_event_id text
        )
    ''')
    cursor.execute('''
        create table if not exists conversations (
            id integer primary key autoincrement,
            user_id integer not null references user(id) on delete cascade,
            role varchar(50) not null,
            message text not null,
            created_at datetime default current_timestamp
        )
    ''')
    conn.commit()

# Inserts
def insert_user(conn, cursor, nickname, telegram_id, google_token=None, language='en-US'):
    cursor.execute('''
        insert into user (nickname, telegram_id, google_token, language)
        values (?, ?, ?, ?)
    ''', (nickname, telegram_id, google_token, language))
    conn.commit()
    return cursor.lastrowid

def insert_goal(conn, cursor, user_id, name, importance, description=None):
    cursor.execute('''
        insert into goals (user_id, name, importance, description)
        values (?, ?, ?, ?)
    ''', (user_id, name, importance, description))
    conn.commit()
    return cursor.lastrowid

def insert_project(conn, cursor, goal_id, name, description=None, due_date=None, hours=None, frequency=None):
    cursor.execute('''
        insert into projects (goal_id, name, description, due_date, hours, frequency)
        values (?, ?, ?, ?, ?, ?)
    ''', (goal_id, name, description, due_date, hours, frequency))
    conn.commit()
    return cursor.lastrowid

def insert_task(conn, cursor, project_id, title, status, start_date=None, end_date=None, planned_duration=None, spent_time=None, calendar_event_id=None):
    cursor.execute('''
        insert into tasks (project_id, title, status, start_date, end_date, planned_duration, spent_time, calendar_event_id)
        values (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, title, status, start_date, end_date, planned_duration, spent_time, calendar_event_id))
    conn.commit()
    return cursor.lastrowid

def insert_message(conn, cursor, user_id, role, message):
    cursor.execute('''
        insert into conversations (user_id, role, message)
        values (?, ?, ?)
    ''', (user_id, role, message))
    conn.commit()
    return cursor.lastrowid

# Updates
def complete_project(conn, cursor, project_id):
    cursor.execute('UPDATE projects SET status = "completed" WHERE id = ?', (project_id,))
    conn.commit()

def reopen_project(conn, cursor, project_id):
    cursor.execute('UPDATE projects SET status = "active" WHERE id = ?', (project_id,))
    conn.commit()

def complete_goal(conn, cursor, goal_id):
    cursor.execute('UPDATE goals SET status = "completed" WHERE id = ?', (goal_id,))
    conn.commit()

def reopen_goal(conn, cursor, goal_id):
    cursor.execute('UPDATE goals SET status = "active" WHERE id = ?', (goal_id,))
    conn.commit()

def update_task_status(conn, cursor, task_id, status, spent_time=None):
    update_task(conn, cursor, task_id, status=status, spent_time=spent_time)

def update_user(conn, cursor, user_id, nickname=None, telegram_id=None, google_token=None, language=None):
    fields = []
    values = []
    if nickname:
        fields.append("nickname = ?")
        values.append(nickname)
    if telegram_id:
        fields.append("telegram_id = ?")
        values.append(telegram_id)
    if google_token:
        fields.append("google_token = ?")
        values.append(google_token)
    if language:
        fields.append("language = ?")
        values.append(language)

    values.append(user_id)
    cursor.execute(f'''
        update user set {', '.join(fields)} where id = ?
    ''', values)
    conn.commit()

def update_goal(conn, cursor, goal_id, name=None, importance=None, description=None):
    fields = []
    values = []
    if name:
        fields.append("name = ?")
        values.append(name)
    if importance:
        fields.append("importance = ?")
        values.append(importance)
    if description is not None:
        fields.append("description = ?")
        values.append(description)

    values.append(goal_id)
    cursor.execute(f'''
        update goals set {', '.join(fields)} where id = ?
    ''', values)
    conn.commit()

def update_project(conn, cursor, project_id, name=None, description=None, due_date=None, hours=None, frequency=None):
    fields = []
    values = []
    if name:
        fields.append("name = ?")
        values.append(name)
    if description is not None:
        fields.append("description = ?")
        values.append(description)
    if due_date is not None:
        fields.append("due_date = ?")
        values.append(due_date)
    if hours is not None:
        fields.append("hours = ?")
        values.append(hours)
    if frequency is not None:
        fields.append("frequency = ?")
        values.append(frequency)

    values.append(project_id)
    cursor.execute(f'''
        update projects set {', '.join(fields)} where id = ?
    ''', values)
    conn.commit()

def update_task(conn, cursor, task_id, title=None, status=None, start_date=None, end_date=None, planned_duration=None, spent_time=None, calendar_event_id=None):
    fields = []
    values = []
    if title:
        fields.append("title = ?")
        values.append(title)
    if status:
        fields.append("status = ?")
        values.append(status)
    if start_date is not None:
        fields.append("start_date = ?")
        values.append(start_date)
    if end_date is not None:
        fields.append("end_date = ?")
        values.append(end_date)
    if planned_duration is not None:
        fields.append("planned_duration = ?")
        values.append(planned_duration)
    if spent_time is not None:
        fields.append("spent_time = ?")
        values.append(spent_time)
    if calendar_event_id is not None:
        fields.append("calendar_event_id = ?")
        values.append(calendar_event_id)

    values.append(task_id)
    cursor.execute(f'''
        update tasks set {', '.join(fields)} where id = ?
    ''', values)
    conn.commit()
    
def clear_google_token(conn, cursor, user_id):
    cursor.execute('UPDATE user SET google_token = NULL WHERE id = ?', (user_id,))
    conn.commit()

# Queries
def get_user_by_telegram_id(cursor, telegram_id) -> Optional[User]:
    cursor.execute('''
        select id, nickname, telegram_id, google_token, language from user where telegram_id = ?
    ''', (telegram_id,))
    row = cursor.fetchone()
    if row:
        return User(id=row[0], nickname=row[1], telegram_id=row[2], google_token=row[3], language=row[4])
    return None

def get_all_users(cursor) -> list[User]:
    cursor.execute('SELECT id, nickname, telegram_id, google_token, language FROM user WHERE google_token IS NOT NULL')
    rows = cursor.fetchall()
    return [User(id=row[0], nickname=row[1], telegram_id=row[2], google_token=row[3], language=row[4]) for row in rows]

def get_goals_by_user_id(cursor, user_id) -> list[Goal]:
    cursor.execute('''
        select id, user_id, name, importance, description, status from goals where user_id = ?
    ''', (user_id,))
    rows = cursor.fetchall()
    if rows:
        return [Goal(id=row[0], user_id=row[1], name=row[2], importance=row[3], description=row[4], status=row[5]) for row in rows]
    return []

def get_projects_by_goal_id(cursor, goal_id) -> list[Project]:
    cursor.execute('''
        select id, name, description, due_date, hours, frequency, status from projects where goal_id = ?
    ''', (goal_id,))
    rows = cursor.fetchall()
    if rows:
        return [Project(id=row[0], goal_id=goal_id, name=row[1], description=row[2], due_date=row[3], hours=row[4], frequency=row[5], status=row[6]) for row in rows]
    return []

def get_tasks_by_project_id(cursor, project_id, status=None) -> list[Task]:
    if status:
        cursor.execute('''
            select id, title, status, start_date, end_date, planned_duration, spent_time, calendar_event_id from tasks where project_id = ? and status like ?
        ''', (project_id, f'%{status}%'))
    else:
        cursor.execute('''
            select id, title, status, start_date, end_date, planned_duration, spent_time, calendar_event_id from tasks where project_id = ?
        ''', (project_id,))
    rows = cursor.fetchall()
    if rows:
        return [Task(id=row[0], project_id=project_id, title=row[1], status=row[2], start_date=row[3], end_date=row[4], planned_duration=row[5], spent_time=row[6], calendar_event_id=row[7]) for row in rows]
    return []

def get_tasks_by_user_id(cursor, user_id, status=None) -> list[Task]:
    if status:
        cursor.execute('''
            select t.id, t.project_id, t.title, t.status, t.start_date, t.end_date, 
                   t.planned_duration, t.spent_time, t.calendar_event_id
            from tasks t
            join projects p on t.project_id = p.id
            join goals g on p.goal_id = g.id
            where g.user_id = ? and t.status like ?
        ''', (user_id, f'%{status}%'))
    else:
        cursor.execute('''
            select t.id, t.project_id, t.title, t.status, t.start_date, t.end_date,
                   t.planned_duration, t.spent_time, t.calendar_event_id
            from tasks t
            join projects p on t.project_id = p.id
            join goals g on p.goal_id = g.id
            where g.user_id = ?
        ''', (user_id,))
    rows = cursor.fetchall()
    if rows:
        return [Task(id=row[0], project_id=row[1], title=row[2], status=row[3],
                    start_date=row[4], end_date=row[5], planned_duration=row[6],
                    spent_time=row[7], calendar_event_id=row[8]) for row in rows]
    return []

def get_conversations_by_user_id(cursor, user_id) -> list[Conversation]:
    cursor.execute('''
        select id, role, message, created_at from conversations where user_id = ? order by created_at
    ''', (user_id,))
    rows = cursor.fetchall()
    if rows:
        return [Conversation(id=row[0], user_id=user_id, role=row[1], message=row[2], created_at=row[3]) for row in rows]
    return []

def get_project_by_id(cursor, project_id) -> Optional[Project]:
    cursor.execute('''
        select id, goal_id, name, description, due_date, hours, frequency, status from projects where id = ?
    ''', (project_id,))
    row = cursor.fetchone()
    if row:
        return Project(id=row[0], goal_id=row[1], name=row[2], description=row[3], due_date=row[4], hours=row[5], frequency=row[6], status=row[7])
    return None

def get_goal_by_id(cursor, goal_id) -> Optional[Goal]:
    cursor.execute('''
        select id, user_id, name, importance, description, status from goals where id = ?
    ''', (goal_id,))
    row = cursor.fetchone()
    if row:
        return Goal(id=row[0], user_id=row[1], name=row[2], importance=row[3], description=row[4], status=row[5])
    return None

def get_projects_by_user_id(cursor, user_id) -> list[Project]:
    cursor.execute('''
        select p.id, p.goal_id, p.name, p.description, p.due_date, p.hours, p.frequency, p.status
        from projects p
        join goals g on p.goal_id = g.id
        where g.user_id = ?
    ''', (user_id,))
    rows = cursor.fetchall()
    if rows:
        return [Project(id=row[0], goal_id=row[1], name=row[2], description=row[3], due_date=row[4], hours=row[5], frequency=row[6]) for row in rows]
    return []

def get_task_by_id(cursor, task_id) -> Optional[Task]:
    cursor.execute('''
        select id, project_id, title, status, start_date, end_date, planned_duration, spent_time, calendar_event_id from tasks where id = ?
    ''', (task_id,))
    row = cursor.fetchone()
    if row:
        return Task(id=row[0], project_id=row[1], title=row[2], status=row[3], start_date=row[4], end_date=row[5], planned_duration=row[6], spent_time=row[7], calendar_event_id=row[8])
    return None

def get_progress_stats(cursor, user_id) -> dict:
    # Goals
    cursor.execute('SELECT COUNT(*) FROM goals WHERE user_id = ? AND status = "active"', (user_id,))
    active_goals = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM goals WHERE user_id = ? AND status = "completed"', (user_id,))
    completed_goals = cursor.fetchone()[0]

    # Projects
    cursor.execute('''
        SELECT COUNT(*) FROM projects p 
        JOIN goals g ON p.goal_id = g.id 
        WHERE g.user_id = ? AND p.status = "active"
    ''', (user_id,))
    active_projects = cursor.fetchone()[0]
    cursor.execute('''
        SELECT COUNT(*) FROM projects p 
        JOIN goals g ON p.goal_id = g.id 
        WHERE g.user_id = ? AND p.status = "completed"
    ''', (user_id,))
    completed_projects = cursor.fetchone()[0]

    # Tasks
    cursor.execute('''
        SELECT COUNT(*) FROM tasks t
        JOIN projects p ON t.project_id = p.id
        JOIN goals g ON p.goal_id = g.id
        WHERE g.user_id = ? AND t.status = "pending"
    ''', (user_id,))
    pending_tasks = cursor.fetchone()[0]
    cursor.execute('''
        SELECT COUNT(*) FROM tasks t
        JOIN projects p ON t.project_id = p.id
        JOIN goals g ON p.goal_id = g.id
        WHERE g.user_id = ? AND t.status = "completed"
    ''', (user_id,))
    completed_tasks = cursor.fetchone()[0]

    # This week
    week_start = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)).isoformat()
    cursor.execute('''
        SELECT COUNT(*) FROM tasks t
        JOIN projects p ON t.project_id = p.id
        JOIN goals g ON p.goal_id = g.id
        WHERE g.user_id = ? AND t.status = "completed" AND t.end_date >= ?
    ''', (user_id, week_start))
    weekly_completed = cursor.fetchone()[0]

    return {
        "active_goals": active_goals,
        "completed_goals": completed_goals,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "weekly_completed": weekly_completed
    }

# Delete
def delete_goal(conn, cursor, goal_id):
    cursor.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
    conn.commit()

def delete_project(conn, cursor, project_id):
    cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()

def delete_task(conn, cursor, task_id):
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()