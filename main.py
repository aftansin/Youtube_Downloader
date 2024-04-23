import asyncio
import logging
import os

from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.types import BotCommand
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from db import BaseModel, get_async_engine, get_session_maker, update_schemas
from handlers import start_router, help_router, video_router


load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot_commands = [
    BotCommand(command='start', description='Start the bot'),
    BotCommand(command='help', description='Help info')
]


async def main() -> None:
    api_server = TelegramAPIServer.from_base('http://localhost:8081')  # локальный сервер в Docker
    bot = Bot(
        TOKEN,
        parse_mode=ParseMode.HTML,
        session=AiohttpSession(api=api_server)
    )
    await bot.set_my_commands(commands=bot_commands)
    dp = Dispatcher()
    dp.include_routers(start_router, help_router, video_router)
    async_engine = get_async_engine("sqlite+aiosqlite:///users.db")
    session_maker = get_session_maker(async_engine)
    await update_schemas(async_engine, BaseModel.metadata)
    await dp.start_polling(bot, session_maker=session_maker)


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
