from aiogram import Router, types
from handlers.start import start as start_handler
from keyboards.help import faq_keyboard
from aiogram.types import ReplyKeyboardRemove

router = Router()


@router.callback_query(lambda c: c.data == "help")
async def help_command(callback: types.CallbackQuery):
    await callback.message.answer("Раздел помощи. Выберите вопрос:", reply_markup=faq_keyboard)
    await callback.answer()

@router.message(lambda msg: msg.text == "🗺 Как нас найти?")
async def faq_location(message: types.Message):
    await message.answer("📍 Мы находимся по адресу: Республика Беларусь, г. Могилев, ул. Гришина 96.")


@router.message(lambda msg: msg.text == "🏢 График работы")
async def faq_hours(message: types.Message):
    await message.answer("🕘 Мы работаем с понедельника по пятницу с 9:00 до 18:00.")


# ☎ Ответ: Контакты
@router.message(lambda msg: msg.text == "☎ Контакты")
async def faq_contacts(message: types.Message):
    await message.answer("📞 Телефон: +375 (222) 42-17-52\n📧 Email: olsa@olsa.by\n 🌐 Сайт: https://olsa.by/ ")


@router.message(lambda msg: msg.text == "◀️ Назад")
async def back_to_main(message: types.Message):
    await message.answer("Возврат в главное меню", reply_markup=types.ReplyKeyboardRemove())
    await start_handler(message)
