import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import start, shop, help, support, admin
from services.db import create_users_table,create_shop_tables,create_purchases_table

create_users_table()
create_shop_tables()
create_purchases_table()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(admin.router)
dp.include_router(shop.router)
dp.include_router(help.router)
dp.include_router(support.router)
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
