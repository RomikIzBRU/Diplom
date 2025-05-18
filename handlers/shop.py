from aiogram import Router, types, F,Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
    PreCheckoutQuery,
    Message,
)
from keyboards.shop import get_categories_keyboard, get_products_keyboard
from keyboards.main import main_keyboard
from services.db import (
    get_products_by_category,
    get_product_by_id,
    get_category_by_id,
    add_purchase
)
from config import RESPONSABLE_EMPLOYER, BOT_PAYMENT_TOKEN, SECONDARY_BOT_TOKEN
import asyncio

router = Router()

try:
    secondary_bot = Bot(token=SECONDARY_BOT_TOKEN) if SECONDARY_BOT_TOKEN else None
except Exception as e:
    print(f"❌ Ошибка инициализации бота: {e}")
    secondary_bot = None
def get_purchase_options_keyboard(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить через Telegram", callback_data=f"pay_{product_id}")],
        [InlineKeyboardButton(text="📩 Заказать через сотрудника", callback_data=f"buy_{product_id}")],
        [InlineKeyboardButton(text="⬅ Назад к категориям", callback_data="shop")]
    ])


@router.callback_query(F.data == "shop")
async def show_categories(call: CallbackQuery):
    await call.message.edit_text("Выберите категорию товара:", reply_markup=get_categories_keyboard())


@router.callback_query(F.data.startswith("category_"))
async def show_products(call: CallbackQuery):
    category_id = int(call.data.split("_")[1])
    category = get_category_by_id(category_id)

    if not category:
        await call.answer("Категория не найдена", show_alert=True)
        return

    products = get_products_by_category(category_id)

    if not products:
        await call.message.edit_text(
            f"В категории «{category['name']}» пока нет товаров.",
            reply_markup=get_categories_keyboard()
        )
    else:
        await call.message.edit_text(
            f"📦 Товары в категории «{category['name']}»:",
            reply_markup=get_products_keyboard(products)
        )


@router.callback_query(F.data.startswith("product_"))
async def show_purchase_options(call: CallbackQuery):
    product_id = int(call.data.split("_")[1])
    product = get_product_by_id(product_id)

    if not product:
        await call.answer("Товар не найден.", show_alert=True)
        return

    await call.message.edit_text(
        f"Вы выбрали:\n📦 {product['name']}\n💵 Цена: {product['price']} BYN\n\nКак хотите продолжить?",
        reply_markup=get_purchase_options_keyboard(product_id)
    )


@router.callback_query(F.data.startswith("buy_"))
async def buy_product(call: CallbackQuery):
    product_id = int(call.data.split("_")[1])
    product = get_product_by_id(product_id)

    if not product:
        await call.answer("Товар не найден.", show_alert=True)
        return

    message = (
        f"🛍 Новый заказ!\n"
        f"📦 Товар: {product['name']}\n"
        f"💵 Цена: {product['price']} BYN\n"
        f"👤 Покупатель: @{call.from_user.username or 'без ника'} (ID: {call.from_user.id})"
    )
    try:
        if not secondary_bot:
            raise RuntimeError("Бот для уведомлений не настроен")

        employer_nick = RESPONSABLE_EMPLOYER
        chat = await secondary_bot.get_chat(f"{employer_nick}")
        print(f"✅ Чат найден: {chat.id}")

        await secondary_bot.send_message(chat_id=chat.id,text=message)
    except Exception as e:
        print(f"🔥 Ошибка: {repr(e)}")
        await message.answer("❌ Ошибка отправки. Сообщите администратору.")


    await call.message.answer("✅ Ваш заказ отправлен сотруднику. С вами свяжутся для оформления.")


@router.callback_query(F.data.startswith("pay_"))
async def pay_via_telegram(call: CallbackQuery):
    product_id = int(call.data.split("_")[1])
    product = get_product_by_id(product_id)

    if not product:
        await call.answer("Товар не найден.", show_alert=True)
        return

    await call.bot.send_invoice(
        chat_id=call.from_user.id,
        title=product['name'],
        description=f"Оплата товара: {product['name']}",
        payload=f"purchase_{product_id}",
        provider_token=BOT_PAYMENT_TOKEN,
        currency="BYN",
        prices=[LabeledPrice(label=product['name'], amount=int(product['price'] * 100))],
        start_parameter="buy_product",
        photo_url="",
        photo_width=600,
        photo_height=400,
        need_email=False,
        need_name=False,
        is_flexible=False,
    )


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout: PreCheckoutQuery):
    await pre_checkout.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    payload = message.successful_payment.invoice_payload
    product_id = int(payload.split("_")[1])
    product = get_product_by_id(product_id)
    user_id = message.from_user.id
    price = product['price']
    await asyncio.to_thread(add_purchase, user_id, product_id, price)
    await message.answer(f"✅ Оплата прошла успешно!\n📦 Товар: {product['name']}\n💵 Сумма: {product['price']} BYN")

    text = (
        f"💰 Оплата получена!\n"
        f"📦 Товар: {product['name']}\n"
        f"💵 Сумма: {product['price']} BYN\n"
        f"👤 Покупатель: @{message.from_user.username or 'без ника'} (ID: {message.from_user.id})"
    )

    try:
        if not secondary_bot:
            raise RuntimeError("Бот для уведомлений не настроен")

        chat = await secondary_bot.get_chat(RESPONSABLE_EMPLOYER)
        await secondary_bot.send_message(chat_id=chat.id, text=text)
        print("✅ Уведомление об оплате отправлено через secondary_bot")
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомления через secondary_bot: {e}")


@router.callback_query(F.data == "back")
async def back_to_main_menu(call: CallbackQuery):
    await call.message.edit_text("Вы вернулись в главное меню.", reply_markup=main_keyboard)
