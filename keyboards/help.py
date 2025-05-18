from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

faq_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗺 Как нас найти?")],
        [KeyboardButton(text="🏢 График работы")],
        [KeyboardButton(text="☎ Контакты")],
        [KeyboardButton(text="◀️ Назад")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)