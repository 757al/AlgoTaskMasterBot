import sqlite3
from datetime import datetime

def init_db():
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task_text TEXT,
                created_at TEXT,
                is_done INTEGER DEFAULT 0
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_date TEXT
            )
        ''')

def add_user(user_id, username, first_name):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, joined_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

def add_task(user_id, text):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO tasks (user_id, task_text, created_at)
            VALUES (?, ?, ?)
        ''', (user_id, text, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

def get_tasks(user_id):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute('SELECT id, task_text FROM tasks WHERE user_id = ? AND is_done = 0', (user_id,))
        return c.fetchall()

def complete_task(task_id, user_id):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute('UPDATE tasks SET is_done = 1 WHERE id = ? AND user_id = ?', (task_id, user_id))

def delete_task(task_id, user_id):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))

def get_user_stats():
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        total_users = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        total_tasks = c.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
        active = c.execute('SELECT COUNT(*) FROM tasks WHERE is_done = 0').fetchone()[0]
        done = c.execute('SELECT COUNT(*) FROM tasks WHERE is_done = 1').fetchone()[0]
        return total_users, total_tasks, active, done

def get_all_users():
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        return c.execute('SELECT user_id, first_name, username, joined_date FROM users').fetchall()

def delete_user_by_id(uid):
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute('DELETE FROM tasks WHERE user_id = ?', (uid,))
        c.execute('DELETE FROM users WHERE user_id = ?', (uid,))