import sqlite3

def init_db():
    conn = sqlite3.connect('myflow.db')
    cursor = conn.cursor()
    create_tables(conn, cursor)
    return conn, cursor

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

def insert_user(conn, cursor, nickname, telegram_id, google_token=None):
    cursor.execute('''
        insert into user (nickname, telegram_id, google_token)
        values (?, ?, ?)
    ''', (nickname, telegram_id, google_token))
    conn.commit()
    return cursor.lastrowid

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

def get_user_by_telegram_id(cursor, telegram_id):
    cursor.execute('''
        select id, nickname, telegram_id, google_token from user where telegram_id = ?
    ''', (telegram_id,))
    return cursor.fetchone()

def insert_goal(conn, cursor, user_id, name, importance, description=None):
    cursor.execute('''
        insert into goals (user_id, name, importance, description)
        values (?, ?, ?, ?)
    ''', (user_id, name, importance, description))
    conn.commit()
    return cursor.lastrowid

def get_goals_by_user_id(cursor, user_id):
    cursor.execute('''
        select id, name, importance, description from goals where user_id = ?
    ''', (user_id,))
    return cursor.fetchall()

def insert_project(conn, cursor, goal_id, name, description=None, due_date=None, hours=None, frequency=None):
    cursor.execute('''
        insert into projects (goal_id, name, description, due_date, hours, frequency)
        values (?, ?, ?, ?, ?, ?)
    ''', (goal_id, name, description, due_date, hours, frequency))
    conn.commit()
    return cursor.lastrowid

def get_projects_by_goal_id(cursor, goal_id):
    cursor.execute('''
        select id, name, description, due_date, hours, frequency from projects where goal_id = ?
    ''', (goal_id,))
    return cursor.fetchall()

def insert_task(conn, cursor, project_id, title, status, start_date=None, end_date=None, planned_duration=None, spent_time=None):
    cursor.execute('''
        insert into tasks (project_id, title, status, start_date, end_date, planned_duration, spent_time)
        values (?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, title, status, start_date, end_date, planned_duration, spent_time))
    conn.commit()
    return cursor.lastrowid

def update_task_status(conn, cursor, task_id, status, spent_time=None):
    cursor.execute('''
        update tasks set status = ?, spent_time = ? where id = ?
    ''', (status, spent_time, task_id))
    conn.commit()

def get_tasks_by_project_id(cursor, project_id):
    cursor.execute('''
        select id, title, status, start_date, end_date, planned_duration, spent_time from tasks where project_id = ?
    ''', (project_id,))
    return cursor.fetchall()

def insert_message(conn, cursor, user_id, role, message):
    cursor.execute('''
        insert into conversations (user_id, role, message)
        values (?, ?, ?)
    ''', (user_id, role, message))
    conn.commit()
    return cursor.lastrowid

def get_conversations_by_user_id(cursor, user_id):
    cursor.execute('''
        select role, message, created_at from conversations where user_id = ? order by created_at
    ''', (user_id,))
    return cursor.fetchall()

if __name__ == "__main__":
    conn, cursor = init_db()
    user_id = insert_user(conn, cursor, "Boss", "your_telegram_id")
    print(f"User created with id: {user_id}")
    conn.close()