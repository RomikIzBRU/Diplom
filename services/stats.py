from services.db import get_all_users

def get_user_stats() -> str:
    users = get_all_users()
    total_users = len(users)
    active_users = sum(1 for user in users if user['active'])
    stats_text = (
        f"Общая статистика пользователей:\n"
        f"Всего пользователей: {total_users}\n"
        f"Активных пользователей: {active_users}\n"
    )
    return stats_text
