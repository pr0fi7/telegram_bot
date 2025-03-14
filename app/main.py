import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from handlers import nocv_flow, start, cv_flow, admin, person_flow, bot_flow
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Register routers/handlers from different modules
dp.include_router(start.router)
dp.include_router(cv_flow.router)
dp.include_router(nocv_flow.router)
dp.include_router(admin.router)
dp.include_router(person_flow.router)
dp.include_router(bot_flow.router)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
