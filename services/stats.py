from services.db import get_all_users
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64


def get_user_stats() -> str:
    users = get_all_users()
    total_users = len(users)
    active_users = sum(1 for user in users if user.get('active'))

    percent_active = round((active_users / total_users) * 100, 2) if total_users > 0 else 0

    now = datetime.now()
    account_ages = [
        (now - datetime.fromisoformat(user['created_at'])).days
        for user in users if 'created_at' in user
    ]
    avg_account_age = round(sum(account_ages) / len(account_ages), 2) if account_ages else 0

    stats_text = (
        f"📊 Общая статистика пользователей:\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"✅ Активных: {active_users} ({percent_active}%)\n"
        f"📆 Средний возраст аккаунта: {avg_account_age} дней\n"
    )

    return stats_text

