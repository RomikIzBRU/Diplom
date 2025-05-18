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

