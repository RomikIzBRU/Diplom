from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_panel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="📄 Экспорт в PDF")],
        [KeyboardButton(text="🛠 Редактировать товары")],
        [KeyboardButton(text="🔙 Выйти")],
    ],
    resize_keyboard=True
)

edit_goods_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить категорию"), KeyboardButton(text="➕ Добавить товар")],
        [KeyboardButton(text="✏️ Изменить категорию"), KeyboardButton(text="✏️ Изменить товар")],
        [KeyboardButton(text="🗑️ Удалить категорию"), KeyboardButton(text="🗑️ Удалить товар")],
        [KeyboardButton(text="🔙 Назад в админ-панель")]
    ],
    resize_keyboard=True
)
