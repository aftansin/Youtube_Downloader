# import random
# import string
# import logging
# import requests
#
# from aiogram import Bot, Dispatcher, executor, types
# from aiogram.bot.api import TelegramAPIServer
# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
#
#
# from youtube import download_video, delete_video
# from config import TELEGRAM_TOKEN, ADMIN_ID, CHAT_ID
#
# logging.basicConfig(
#     format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)
#
#
# local_server = TelegramAPIServer.from_base('http://localhost:8081/')
#
# # r = requests.get('https://api.telegram.org/bot5605913205:AAEi20ubh7RK2PRA5F01XEjfP2Sr7mk2cAI/logOut')
# # print(r.json())
#
#
# bot = Bot(
#     token=TELEGRAM_TOKEN,
#     # server=local_server
# )
# dp = Dispatcher(bot)
#
#
# keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
# button_help = KeyboardButton('/help')
# button_desc = KeyboardButton('/desc')
# keyboard.add(button_help).insert(button_desc)
#
#
# async def on_startup(_):
#     await bot.send_message(ADMIN_ID, f'Я запущен!')
#
#
# # @dp.message_handler(commands=['start'])
# # async def start_command(message: types.Message):
# #     await message.answer(text='Бот запущен!',
# #                          reply_markup=keyboard)
#
#
# # @dp.message_handler(commands=['help'])
# # async def help_command(message: types.Message):
# #     await message.answer(text='Нужна помощь?')
# #     await message.delete()
#
#
# @dp.message_handler(commands=['check'])
# async def check_command(message: types.Message):
#     url = bot.get_me()
#     await message.answer(text=str(url))
#
#
# # @dp.message_handler(commands=['desc'])
# # async def desc_command(message: types.Message):
# #     await message.answer(text='Описание бота.')
# #     await message.delete()
#
#
# @dp.message_handler()
# async def youtube(message: types.Message):
#     if 'https://www.youtube.com/' in message.text:
#         link = message.text
#
#         filename = download_video(link)
#         await bot.send_video(message.chat.id, open(filename, 'rb', ), supports_streaming=True)
#         delete_video(link)
#         await message.delete()
#     else:
#         await message.reply(text='Please, sent youtube link')
#
#
# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
#
