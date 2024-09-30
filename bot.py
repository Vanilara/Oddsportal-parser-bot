from aiogram import Bot, Dispatcher
from handlers import hand_login, hand_admin, hand_filters
import asyncio
from config import Config

async def main():
    bot = Bot(token=Config.Bot.TOKEN)
    dp = Dispatcher()
    dp.include_routers(hand_login.r, hand_admin.r, hand_filters.r)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())