import asyncio
import logging
import os

from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.methods import DeleteWebhook
from aiogram.types import BotCommand
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from loguru import logger
from notifiers.logging import NotificationHandler

from db import BaseModel, get_async_engine, get_session_maker, update_schemas
from handlers import start_router, help_router, video_router
from handlers.account import account_router

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

bot_commands = [
    BotCommand(command='start', description='Restart the bot'),
    BotCommand(command='help', description='Help info'),
    BotCommand(command='account', description='Account info')
]


async def main() -> None:
    api_server = TelegramAPIServer.from_base('http://localhost:8081')  # локальный сервер в Docker
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML, session=AiohttpSession(api=api_server))
    dp = Dispatcher()
    dp.include_routers(start_router, help_router, account_router,  video_router)
    async_engine = get_async_engine("sqlite+aiosqlite:///users.db")
    session_maker = get_session_maker(async_engine)
    await update_schemas(async_engine, BaseModel.metadata)
    await bot.set_my_commands(commands=bot_commands)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot, db_session=session_maker)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Конфигурируем логирование
    params = {'token': TOKEN, 'chat_id': ADMIN_ID}
    telegram_handler = NotificationHandler("telegram", defaults=params)
    logger.add(telegram_handler, level="INFO", format="{level} {message}")
    logger.add("debug.log", rotation="1 MB")
    try:
        logger.info(f'Youtube Bot Started...')
        asyncio.run(main())
    except Exception as e:
        logger.info(e)
