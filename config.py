import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
SECONDARY_BOT_TOKEN = os.getenv("SECONDARY_BOT_TOKEN")
ADMIN_USERS = os.getenv("ADMIN_USERS")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
RESPONSABLE_EMPLOYER = os.getenv("RESPONSABLE_EMPLOYER")
BOT_PAYMENT_TOKEN= os.getenv("BOT_PAYMENT_TOKEN")