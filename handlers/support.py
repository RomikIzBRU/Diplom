from aiogram import Router, types, F, Bot
import re
from config import RESPONSABLE_EMPLOYER, SECONDARY_BOT_TOKEN

router = Router()
support_data = {}

try:
    secondary_bot = Bot(token=SECONDARY_BOT_TOKEN) if SECONDARY_BOT_TOKEN else None
except Exception as e:
    print(f"❌ Ошибка инициализации бота: {e}")
    secondary_bot = None

phone_pattern = re.compile(r"^\+375 \((25|29|33|44)\) \d{3}-\d{2}-\d{2}$")


@router.callback_query(F.data == "support")
async def request_support(call: types.CallbackQuery):
    user_id = call.from_user.id
    await call.message.answer("Пожалуйста, введите ваше имя:")
    support_data[user_id] = {"stage": "name"}
    print(f"🆕 Сессия запущена | User: {user_id}")


@router.message(F.from_user.id.in_(support_data.keys()))
async def collect_support_info(message: types.Message):
    user_id = message.from_user.id
    data = support_data.get(user_id)

    if not data:
        return await message.answer("❌ Сессия устарела. Начните заново.")

    stage = data.get("stage")
    print(f"🔧 Этап: {stage} | User: {user_id}")

    if stage == "name":
        data["name"] = message.text.strip()
        data["stage"] = "phone"
        await message.answer("📱 Введите телефон в формате: +375 (XX) XXX-XX-XX")
        return

    elif stage == "phone":
        phone = message.text.strip()
        if not phone_pattern.match(phone):
            return await message.answer("❌ Неверный формат. Пример ввода: +375 (29) 123-45-67")

        data["phone"] = phone
        data["stage"] = "question"
        await message.answer("❓ Опишите ваш вопрос:")
        return

    elif stage == "question":
        data["question"] = message.text.strip()

        try:
            if not secondary_bot:
                raise RuntimeError("Бот для уведомлений не настроен")

            employer_nick = RESPONSABLE_EMPLOYER
            chat = await secondary_bot.get_chat(f"{employer_nick}")
            print(f"✅ Чат найден: {chat.id}")

            await secondary_bot.send_message(
                chat_id=chat.id,
                text=f"📩 Вопрос от @{message.from_user.username or user_id}\n"
                     f"👤 Имя: {data['name']}\n"
                     f"📞 Телефон: {data['phone']}\n"
                     f"❓ Вопрос: {data['question']}"
            )
            await message.answer("✅ Ваш вопрос отправлен! Наш сотрудник свяжется с вами в ближайшее время!")

        except Exception as e:
            print(f"🔥 Ошибка: {repr(e)}")
            await message.answer("❌ Ошибка отправки. Сообщите администратору.")

        finally:
            del support_data[user_id]
            print(f"🗑 Сессия завершена | User: {user_id}")