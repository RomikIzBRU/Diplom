import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env

TOKEN = os.getenv("TOKEN")
SECONDARY_BOT_TOKEN = os.getenv("SECONDARY_BOT_TOKEN")
ADMIN_USERS = os.getenv("ADMIN_USERS").split(",")  # если будет несколько через запятую
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
RESPONSABLE_EMPLOYER = os.getenv("RESPONSABLE_EMPLOYER")
