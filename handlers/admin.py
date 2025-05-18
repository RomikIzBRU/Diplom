from aiogram import Router, types, F
from aiogram.filters import Command
from keyboards.admin import admin_panel_keyboard, edit_goods_keyboard
from services.auth import verify_admin_password
from services.stats import get_user_stats
from services.pdf_export import export_stats_to_pdf
from handlers.start import start as start_handler
from services.db import (
    add_category, add_product, get_categories,
    get_products, delete_product, delete_category,
    update_product, update_category
)

router = Router()
admin_sessions = {}

@router.message(Command("admin"))
async def admin_start(message: types.Message):
    user_id = message.from_user.id
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
        return

    if not session.get("authenticated"):
        return

    if message.text == "📊 Статистика":
        stats = get_user_stats()
        await message.answer(f"Пользовательская статистика:\n{stats}")

    elif message.text == "📄 Экспорт в PDF":
        file_path = export_stats_to_pdf()
        await message.answer_document(types.FSInputFile(file_path))

    elif message.text == "🛠 Редактировать товары":
        session["state"] = "edit_goods"
        await message.answer("Выберите действие:", reply_markup=edit_goods_keyboard)

    elif message.text == "🔙 Назад в панель администратора":
        session["state"] = None
        await message.answer("Вы вернулись в панель администратора.", reply_markup=admin_panel_keyboard)

    elif message.text == "🔙 Выйти":
        admin_sessions.pop(user_id, None)
        await message.answer("Вы вышли из панели администратора.", reply_markup=types.ReplyKeyboardRemove())
        await start_handler(message)

    elif message.text == "➕ Добавить категорию":
        session["state"] = "awaiting_category_name"
        await message.answer("Введите название новой категории:")

    elif session.get("state") == "awaiting_category_name":
        category_name = message.text.strip()
        add_category(category_name)
        session["state"] = None
        await message.answer(f"Категория '{category_name}' добавлена ✅", reply_markup=edit_goods_keyboard)

    elif message.text == "🗑️ Удалить категорию":
        categories = get_categories()
        category_list = "\n".join([f"{c['id']}: {c['name']}" for c in categories])
        session["state"] = "awaiting_delete_category"
        await message.answer(f"Введите ID категории для удаления:\n{category_list}")

    elif session.get("state") == "awaiting_delete_category":
        try:
            category_id = int(message.text.strip())
            delete_category(category_id)
            session["state"] = None
            await message.answer("✅ Категория удалена!", reply_markup=edit_goods_keyboard)
        except:
            await message.answer("Ошибка удаления категории. Убедитесь, что ID корректный.")

    # === Изменение категории ===
    elif message.text == "✏️ Изменить категорию":
        categories = get_categories()
        category_list = "\n".join([f"{c['id']}: {c['name']}" for c in categories])
        session["state"] = "awaiting_edit_category_id"
        await message.answer(f"Введите ID категории для изменения:\n{category_list}")

    elif session.get("state") == "awaiting_edit_category_id":
        try:
            session["edit_category_id"] = int(message.text.strip())
            session["state"] = "awaiting_edit_category_name"
            await message.answer("Введите новое имя категории:")
        except ValueError:
            await message.answer("ID должен быть числом.")

    elif session.get("state") == "awaiting_edit_category_name":
        name = message.text.strip()
        update_category(session["edit_category_id"], name)
        session["state"] = None
        session.pop("edit_category_id", None)
        await message.answer("✅ Категория обновлена!", reply_markup=edit_goods_keyboard)

    elif message.text == "➕ Добавить товар":
        categories = get_categories()
        if not categories:
            await message.answer("Сначала добавьте хотя бы одну категорию.")
            return
        session["state"] = "awaiting_product_name"
        session["product_data"] = {}
        await message.answer("Введите название товара:")

    elif session.get("state") == "awaiting_product_name":
        session["product_data"]["name"] = message.text.strip()
        session["state"] = "awaiting_product_price"
        await message.answer("Введите цену товара:")

    elif session.get("state") == "awaiting_product_price":
        try:
            price = float(message.text.strip())
            session["product_data"]["price"] = price
            session["state"] = "awaiting_product_quantity"
            await message.answer("Введите количество товара:")
        except ValueError:
            await message.answer("Цена должна быть числом. Повторите ввод.")

    elif session.get("state") == "awaiting_product_quantity":
        try:
            quantity = int(message.text.strip())
            session["product_data"]["quantity"] = quantity
            categories = get_categories()
            category_list = "\n".join([f"{c['id']}: {c['name']}" for c in categories])
            session["state"] = "awaiting_product_category"
            await message.answer(f"Выберите категорию товара (введите ID):\n{category_list}")
        except ValueError:
            await message.answer("Количество должно быть числом.")

    elif session.get("state") == "awaiting_product_category":
        try:
            category_id = int(message.text.strip())
            data = session["product_data"]
            add_product(category_id, data["name"], data["price"], data["quantity"])
            session["state"] = None
            session.pop("product_data", None)
            await message.answer("✅ Товар добавлен!", reply_markup=edit_goods_keyboard)
        except:
            await message.answer("Ошибка добавления. Проверьте ID категории.")

    # === Удаление товара ===
    elif message.text == "🗑️ Удалить товар":
        products = get_products()
        product_list = "\n".join([f"{p['id']}: {p['name']}" for p in products])
        session["state"] = "awaiting_delete_product"
        await message.answer(f"Введите ID товара для удаления:\n{product_list}")

    elif session.get("state") == "awaiting_delete_product":
        try:
            product_id = int(message.text.strip())
            delete_product(product_id)
            session["state"] = None
            await message.answer("✅ Товар удалён!", reply_markup=edit_goods_keyboard)
        except:
            await message.answer("Ошибка удаления товара. Убедитесь, что ID верный.")

    elif message.text == "✏️ Изменить товар":
        products = get_products()
        product_list = "\n".join([f"{p['id']}: {p['name']}" for p in products])
        session["state"] = "awaiting_edit_product_id"
        await message.answer(f"Введите ID товара для редактирования:\n{product_list}")

    elif session.get("state") == "awaiting_edit_product_id":
        try:
            session["edit_product_id"] = int(message.text.strip())
            session["state"] = "awaiting_edit_product_name"
            await message.answer("Введите новое название товара:")
        except:
            await message.answer("ID товара должен быть числом.")

    elif session.get("state") == "awaiting_edit_product_name":
        session["edit_product_name"] = message.text.strip()
        session["state"] = "awaiting_edit_product_price"
        await message.answer("Введите новую цену:")

    elif session.get("state") == "awaiting_edit_product_price":
        try:
            session["edit_product_price"] = float(message.text.strip())
            session["state"] = "awaiting_edit_product_quantity"
            await message.answer("Введите новое количество:")
        except ValueError:
            await message.answer("Цена должна быть числом.")

    elif session.get("state") == "awaiting_edit_product_quantity":
        try:
            quantity = int(message.text.strip())
            update_product(
                session["edit_product_id"],
                session["edit_product_name"],
                session["edit_product_price"],
                quantity
            )
            session["state"] = None
            session.pop("edit_product_id", None)
            session.pop("edit_product_name", None)
            session.pop("edit_product_price", None)
            await message.answer("✅ Товар обновлён!", reply_markup=edit_goods_keyboard)
        except:
            await message.answer("Ошибка. Убедитесь, что количество — целое число.")

    else:
        await message.answer("Выберите действие из меню.", reply_markup=admin_panel_keyboard)
