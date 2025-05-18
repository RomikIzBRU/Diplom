import sqlite3
from typing import List, Dict

DB_PATH = "data/database.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_users() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, active FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
