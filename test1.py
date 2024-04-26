import asyncio
import os

from aiogram import Bot, types, Dispatcher, Router

import yt_dlp
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv


start_router = Router()
download_router = Router()


def download_video(url):
    ydl_opts = {'format': 'best'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)


async def download_video_async(url):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, download_video, url)


@start_router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hi, <b>{message.from_user.full_name}!</b>")


@download_router.message()
async def handle_youtube_url(message: types.Message):
    url = message.text
    await message.answer(f"Начинаю скачивать видео с Youtube: {url}")
    await download_video_async(url)
    await message.answer("Видео успешно скачано.")


async def main():
    load_dotenv()
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    dp = Dispatcher()
    dp.include_routers(start_router, download_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
