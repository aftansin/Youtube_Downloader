import asyncio
import logging
import os

from aiogram.types import BotCommand
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from handlers.help import help_router
from handlers.start import start_router
from handlers.video import video_router

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot_commands = [
    BotCommand(command='start', description='Начало работы'),
    BotCommand(command='help', description='Справка')
]


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await bot.set_my_commands(commands=bot_commands)
    dp = Dispatcher()
    dp.include_routers(start_router, help_router, video_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
