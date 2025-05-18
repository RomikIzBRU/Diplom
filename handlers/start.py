from aiogram import Router, types
from keyboards.main import main_keyboard
from config import ADMIN_USERS
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    username = message.from_user.username
    if username in ADMIN_USERS:
        await message.answer("Вы зарегистрированы как администратор. Введите /admin для входа в панель.")
    await message.answer("Привет! Выберите действие:", reply_markup=main_keyboard)