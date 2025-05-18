from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Магазин", callback_data="shop")],
    [InlineKeyboardButton(text="📰 Новости", callback_data="news")],
    [InlineKeyboardButton(text="❓ Часто задаваемые вопросы", callback_data="help")],
    [InlineKeyboardButton(text="📞 Связь с сотрудником", callback_data="support")]
])
