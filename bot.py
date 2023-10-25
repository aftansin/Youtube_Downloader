import logging
from random import randint

import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.bot.api import TelegramAPIServer
from aiogram.dispatcher.filters import Text

from config import TELEGRAM_TOKEN, ADMIN_ID
from _pytube import download_video, delete_video

local_server = TelegramAPIServer.from_base('http://localhost:8081/')
# Объект бота
bot = Bot(
    token=TELEGRAM_TOKEN,
    # server=local_server
)
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


async def on_startup(_):
    await bot.send_message(ADMIN_ID, f'Я запущен!')


@dp.message_handler()
async def youtube(message: types.Message):
    if 'youtu' in message.text:
        link = message.text

        filename = download_video(link)
        await bot.send_video(message.chat.id, open(filename, 'rb', ), supports_streaming=True)
        delete_video(link)
        await message.delete()
    else:
        await message.reply(text='Please, sent youtube link')


if __name__ == "__main__":
    # r = requests.get(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/logOut')
    # logging.info(r.json())
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
