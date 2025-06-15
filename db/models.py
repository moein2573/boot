import sqlite3
from datetime import datetime

DB_PATH = 'db/database.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER UNIQUE,
        email TEXT,
        phone TEXT,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        query TEXT,
        created_at TEXT
    )''')
    conn.commit()
    conn.close()

def save_user(chat_id, email, phone):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('INSERT OR REPLACE INTO users (chat_id, email, phone, created_at) VALUES (?, ?, ?, ?)',
              (chat_id, email, phone, now))
    conn.commit()
    conn.close()

def get_user_by_chat_id(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE chat_id=?', (chat_id,))
    user = c.fetchone()
    conn.close()
    return user

def save_search(chat_id, query):
    user = get_user_by_chat_id(chat_id)
    if not user:
        return
    user_id = user[0]
    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO searches (user_id, query, created_at) VALUES (?, ?, ?)',
              (user_id, query, now))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT email, phone FROM users')
    users = [{'email': row[0], 'phone': row[1]} for row in c.fetchall()]
    conn.close()
    return users

def get_all_searches():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT users.email, searches.query, searches.created_at
                 FROM searches JOIN users ON searches.user_id = users.id
                 ORDER BY searches.created_at DESC''')
    searches = [{'user': row[0], 'query': row[1], 'dt': row[2]} for row in c.fetchall()]
    conn.close()
    return searches

def get_popular_searches(limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT query, COUNT(*) as count
                 FROM searches
                 GROUP BY query
                 ORDER BY count DESC
                 LIMIT ?''', (limit,))
    result = [{'query': row[0], 'count': row[1]} for row in c.fetchall()]
    conn.close()
    return result