import asyncio
import logging
import os

from aiogram.types import BotCommand
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from handlers import start_router, help_router, video_router


load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot_commands = [
    BotCommand(command='start', description='Start the bot'),
    BotCommand(command='help', description='Help info')
]


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # logout = await bot.log_out()
    # print(logout)
    await bot.set_my_commands(commands=bot_commands)
    dp = Dispatcher()
    dp.include_routers(start_router, help_router, video_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
