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

def create_shop_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Таблицы categories и products созданы или уже существуют.")

def get_categories() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_products_by_category(category_id: int) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products WHERE category_id = ?", (category_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_product_by_id(product_id: int) -> Dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, category_id FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_category(name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    print(f"✅ Категория '{name}' добавлена.")

def add_product(category_id: int, name: str, price: float, quantity: int = 0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (category_id, name, price, quantity)
        VALUES (?, ?, ?, ?)
    """, (category_id, name, price, quantity))
    conn.commit()
    conn.close()
    print(f"✅ Товар '{name}' добавлен.")
def get_category_by_id(category_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_product(product_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    print(f"🗑️ Товар с ID {product_id} удалён.")

def delete_category(category_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE category_id = ?", (category_id,))
    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()
    print(f"🗑️ Категория с ID {category_id} удалена.")

def update_product(product_id: int, name: str, price: float, quantity: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET name = ?, price = ?, quantity = ?
        WHERE id = ?
    """, (name, price, quantity, product_id))
    conn.commit()
    conn.close()
    print(f"✏️ Товар с ID {product_id} обновлён.")

def update_category(category_id: int, new_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE categories
        SET name = ?
        WHERE id = ?
    """, (new_name, category_id))
    conn.commit()
    conn.close()
    print(f"✏️ Категория с ID {category_id} переименована в '{new_name}'.")

def get_products() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, quantity FROM products")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def create_purchases_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            price REAL,
            timestamp TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Таблица purchases создана или уже существует.")

def add_purchase(user_id: int, product_id: int, price: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO purchases (user_id, product_id, price, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, product_id, price, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    print(f"✅ Покупка товара {product_id} пользователем {user_id} добавлена.")

def get_all_purchases():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, product_id, price, timestamp FROM purchases")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
