import os
import random
import string

from aiogram import Bot, Dispatcher, executor, types
from aiogram.bot.api import TelegramAPIServer
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

from youtube import download_video, delete_video

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

local_server = TelegramAPIServer.from_base('http://localhost:8081')

bot = Bot(
    token=TELEGRAM_TOKEN,
    server=local_server
)
dp = Dispatcher(bot)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_help = KeyboardButton('/help')
button_desc = KeyboardButton('/desc')
keyboard.add(button_help).insert(button_desc)


async def on_startup(_):
    print('Я запустился!')


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(text='Бот запущен!',
                         reply_markup=keyboard)


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer(text='Нужна помощь?')
    await message.delete()


@dp.message_handler(commands=['desc'])
async def desc_command(message: types.Message):
    await message.answer(text='Описание бота.')
    await message.delete()


@dp.message_handler(commands=['large'])
async def desc_command(message: types.Message):
    await bot.send_video(message.chat.id, open('temp.mp4', 'rb'), supports_streaming=True)


@dp.message_handler()
async def youtube(message: types.Message):
    if 'https://www.youtube.com/' in message.text:
        link = message.text

        filename = download_video(link)
        await bot.send_video(message.chat.id, open(filename, 'rb', ), supports_streaming=True)
        delete_video(link)
    else:
        await message.reply(text='Please, sent youtube link')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
