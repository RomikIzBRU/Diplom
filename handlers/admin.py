from aiogram import Router, types, F
from aiogram.filters import Command
from keyboards.admin import admin_panel_keyboard
from services.auth import verify_admin_password
from services.stats import get_user_stats
from services.pdf_export import export_stats_to_pdf
from handlers.start import start as start_handler

router = Router()
admin_sessions = {}

@router.message(Command("admin"))
async def admin_start(message: types.Message):
    user_id = message.from_user.id
    print(f"/admin вызван от пользователя {message.from_user.id}")
    admin_sessions[user_id] = {"awaiting_password": True}
    await message.answer("Введите пароль администратора:")
@router.message(F.from_user.id.in_(admin_sessions.keys()))
async def handle_admin_message(message: types.Message):
    user_id = message.from_user.id
    session = admin_sessions.get(user_id, {})

    if session.get("awaiting_password"):
        if verify_admin_password(message.text):
            session["authenticated"] = True
            session.pop("awaiting_password")
            await message.answer("Добро пожаловать в панель администратора:", reply_markup=admin_panel_keyboard)
        else:
            await message.answer("Неверный пароль. Попробуйте снова.")

    elif session.get("authenticated"):
        if message.text == "📊 Статистика":
            stats = get_user_stats()
            await message.answer(f"Пользовательская статистика:\n{stats}")
        elif message.text == "📄 Экспорт в PDF":
            file_path = export_stats_to_pdf()
            await message.answer_document(types.FSInputFile(file_path))
        elif message.text == "🛠 Редактировать товары":
            await message.answer("Редактирование товаров пока не реализовано.")
        elif message.text == "🔙 Выйти":
            admin_sessions.pop(message.from_user.id, None)
            await message.answer("Вы вышли из панели администратора.", reply_markup=types.ReplyKeyboardRemove())
            await start_handler(message)
        else:
            await message.answer("Выберите опцию из меню.", reply_markup=admin_panel_keyboard)


