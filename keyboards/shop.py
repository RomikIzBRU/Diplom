from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.db import get_categories
from typing import List, Dict
def get_categories_keyboard() -> InlineKeyboardMarkup:
    categories = get_categories()
    keyboard = [
        [InlineKeyboardButton(text=category['name'], callback_data=f"category_{category['id']}")]
        for category in categories
    ]
    keyboard.append([InlineKeyboardButton(text="⬅ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_products_keyboard(products: list) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(
            text=f"{product['name']} — {product['price']} BYN",
            callback_data=f"product_{product['id']}")]
        for product in products
    ]
    keyboard.append([InlineKeyboardButton(text="⬅ Назад к категориям", callback_data="shop")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_products_keyboard(products: List[Dict]) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(
            text=f"{product['name']} — {product['price']} BYN",
            callback_data=f"product_{product['id']}")
        ]
        for product in products
    ]
    keyboard.append([InlineKeyboardButton(text="⬅ Назад к категориям", callback_data="shop")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_purchase_options_keyboard(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить через Telegram", callback_data=f"pay_{product_id}")],
        [InlineKeyboardButton(text="📩 Заказать через сотрудника", callback_data=f"buy_{product_id}")],
        [InlineKeyboardButton(text="⬅ Назад к товарам", callback_data="shop")]
    ])
