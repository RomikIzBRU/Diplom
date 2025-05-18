from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

shop_categories = [
    "Мебель садовая, террасная",
    "Бытовая мебель, потребительские товары",
    "Мебель для кафе, ресторанов и баров",
    "Мебель для медицинских учреждений",
    "Детские игровые комплексы",
    "Мебель по индивидуальным заказам",
    "Электронасосы бытовые",
    "Трансформируемая мебель",
    "Спортивные уличные тренажеры"
]

shop_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=category, callback_data=f"category_{i}")]
        for i, category in enumerate(shop_categories)
    ] + [[InlineKeyboardButton(text="⬅ Назад", callback_data="back")]]
)
