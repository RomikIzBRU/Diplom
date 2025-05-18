from aiogram import Router, types
from keyboards.main import main_keyboard
from config import ADMIN_USERS
from aiogram.filters import Command
from services.db import user_exists, add_user

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "NoUsername"

    if not user_exists(user_id):
        add_user(user_id, username, active=True)

    if username in ADMIN_USERS:
        await message.answer("Вы зарегистрированы как администратор. Введите /admin для входа в панель.")

    await message.answer("Выберите действие:", reply_markup=main_keyboard)
