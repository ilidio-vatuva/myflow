import sqlite3
from models import User, Goal, Project, Task, Conversation
from typing import Optional

_conn = None
_cursor = None

def init_db():
    global _conn, _cursor
    if not _conn:
        _conn = sqlite3.connect('myflow.db')
        _cursor = _conn.cursor()
        create_tables(_conn, _cursor)
    return _conn, _cursor

def create_tables(conn, cursor):
    cursor.execute('''
        create table if not exists user (
            id integer primary key autoincrement,
            nickname text not null,
            telegram_id text not null unique,
            google_token text
        )
    ''')
    cursor.execute('''
        create table if not exists goals (
            id integer primary key autoincrement,
            user_id integer not null references user(id) on delete cascade,
            name text not null,
            importance integer not null,
            description text
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
            frequency text
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
            spent_time integer
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
def insert_user(conn, cursor, nickname, telegram_id, google_token=None):
    cursor.execute('''
        insert into user (nickname, telegram_id, google_token)
        values (?, ?, ?)
    ''', (nickname, telegram_id, google_token))
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

def insert_task(conn, cursor, project_id, title, status, start_date=None, end_date=None, planned_duration=None, spent_time=None):
    cursor.execute('''
        insert into tasks (project_id, title, status, start_date, end_date, planned_duration, spent_time)
        values (?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, title, status, start_date, end_date, planned_duration, spent_time))
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
def update_task_status(conn, cursor, task_id, status, spent_time=None):
    cursor.execute('''
        update tasks set status = ?, spent_time = ? where id = ?
    ''', (status, spent_time, task_id))
    conn.commit()

def update_user(conn, cursor, user_id, nickname=None, telegram_id=None, google_token=None):
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
    values.append(user_id)
    cursor.execute(f'''
        update user set {', '.join(fields)} where id = ?
    ''', values)
    conn.commit()

# Queries
def get_user_by_telegram_id(cursor, telegram_id) -> Optional[User]:
    cursor.execute('''
        select id, nickname, telegram_id, google_token from user where telegram_id = ?
    ''', (telegram_id,))
    row = cursor.fetchone()
    if row:
        return User(id=row[0], nickname=row[1], telegram_id=row[2], google_token=row[3])
    return None

def get_goals_by_user_id(cursor, user_id) -> list[Goal]:
    cursor.execute('''
        select id, user_id, name, importance, description from goals where user_id = ?
    ''', (user_id,))
    rows = cursor.fetchall()
    if rows:
        return [Goal(id=row[0], user_id=row[1], name=row[2], importance=row[3], description=row[4]) for row in rows]
    return []

def get_projects_by_goal_id(cursor, goal_id) -> list[Project]:
    cursor.execute('''
        select id, name, description, due_date, hours, frequency from projects where goal_id = ?
    ''', (goal_id,))
    rows = cursor.fetchall()
    if rows:
        return [Project(id=row[0], goal_id=goal_id, name=row[1], description=row[2], due_date=row[3], hours=row[4], frequency=row[5]) for row in rows]
    return []

def get_tasks_by_project_id(cursor, project_id) -> list[Task]:
    cursor.execute('''
        select id, title, status, start_date, end_date, planned_duration, spent_time from tasks where project_id = ?
    ''', (project_id,))
    rows = cursor.fetchall()
    if rows:
        return [Task(id=row[0], project_id=project_id, title=row[1], status=row[2], start_date=row[3], end_date=row[4], planned_duration=row[5], spent_time=row[6]) for row in rows]
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
        select id, goal_id, name, description, due_date, hours, frequency from projects where id = ?
    ''', (project_id,))
    row = cursor.fetchone()
    if row:
        return Project(id=row[0], goal_id=row[1], name=row[2], description=row[3], due_date=row[4], hours=row[5], frequency=row[6])
    return None

def get_goal_by_id(cursor, goal_id) -> Optional[Goal]:
    cursor.execute('''
        select id, user_id, name, importance, description from goals where id = ?
    ''', (goal_id,))
    row = cursor.fetchone()
    if row:
        return Goal(id=row[0], user_id=row[1], name=row[2], importance=row[3], description=row[4])
    return None
