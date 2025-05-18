from aiogram import Router, types
from keyboards.shop import shop_keyboard, shop_categories

router = Router()

@router.callback_query(lambda call: call.data == "shop")
async def shop(call: types.CallbackQuery):
    await call.message.edit_text("Выберите категорию товара:", reply_markup=shop_keyboard)

@router.callback_query(lambda call: call.data.startswith("category_"))
async def shop_category(call: types.CallbackQuery):
    category_index = int(call.data.split("_")[1])
    category_name = shop_categories[category_index]
    await call.message.edit_text(f"Вы выбрали: {category_name}\nПодробнее о товаре можно узнать на сайте.", reply_markup=shop_keyboard)

@router.callback_query(lambda call: call.data == "back")
async def back_to_main(call: types.CallbackQuery):
    from keyboards.main import main_keyboard
    await call.message.edit_text("Вы вернулись в главное меню.", reply_markup=main_keyboard)