import sqlite3
from typing import List, Dict
from datetime import datetime

DB_PATH = "data/database.db"

def create_users_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            active BOOLEAN DEFAULT 0,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Таблица users создана или уже существует.")

def add_user(user_id: int, username: str, active: bool = True):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (id, username, active, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, int(active), datetime.now().isoformat()))

    conn.commit()
    conn.close()
    print(f"✅ Пользователь {username} добавлен.")
def user_exists(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE id = ?", (user_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_users() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, active, created_at FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

