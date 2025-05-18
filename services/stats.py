from services.db import get_all_users, get_all_purchases
from datetime import datetime

def get_user_stats() -> str:
    users = get_all_users()
    total_users = len(users)
    active_users = sum(1 for user in users if user.get('active'))
    percent_active = round((active_users / total_users) * 100, 2) if total_users > 0 else 0

    weekday_counts = [0] * 7
    for user in users:
        created_at = user.get('created_at')
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at)
                weekday_counts[dt.weekday()] += 1
            except ValueError:
                continue

    weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    weekday_lines = [
        f"   {weekdays_ru[i]}: {count}" for i, count in enumerate(weekday_counts)
    ]
    weekday_stats = "\n".join(weekday_lines)

    user_stats_text = (
        f"📊 Общая статистика пользователей:\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"✅ Активных: {active_users} ({percent_active}%)\n"
        f"📅 Регистрации по дням недели:\n{weekday_stats}"
    )

    purchases = get_all_purchases()
    if purchases:
        prices = [p['price'] for p in purchases]
        avg_price = round(sum(prices) / len(prices), 2)
        max_price = max(prices)
        min_price = min(prices)

        product_count = {}
        user_purchase_counts = {}

        for p in purchases:
            pid = p['product_id']
            uid = p['user_id']
            product_count[pid] = product_count.get(pid, 0) + 1
            user_purchase_counts[uid] = user_purchase_counts.get(uid, 0) + 1

        repeat_ratio = round(
            (sum(1 for count in user_purchase_counts.values() if count > 1) / len(user_purchase_counts)) * 100, 2
        ) if user_purchase_counts else 0

        purchase_stats_text = (
            f"\n\n🛒 Статистика покупок:\n"
            f"📈 Средняя цена: {avg_price} BYN\n"
            f"💰 Мин. цена: {min_price} BYN, Макс. цена: {max_price} BYN\n"
            f"📦 Куплено товаров: {len(purchases)}\n"
            f"🔢 Уникальных товаров: {len(product_count)}\n"
            f"🔁 Повторных покупателей: {repeat_ratio}%"
        )
    else:
        purchase_stats_text = "\n\n🛒 Статистика покупок:\nНет данных о покупках."

    return user_stats_text + purchase_stats_text
