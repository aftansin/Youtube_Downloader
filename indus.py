import logging
import os

import telegram.constants
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def check(update: Update, context: CallbackContext):
    update.message.reply_text(f'The base URL is {context.bot.base_url}')


def send_large_file(update, context):
    update.message.reply_chat_action(telegram.constants.CHATACTION_UPLOAD_VIDEO)
    with open('temp.mp4', 'rb') as file:
        update.message.reply_video(file)


def main():
    updater = Updater('5605913205:AAEi20ubh7RK2PRA5F01XEjfP2Sr7mk2cAI',
                      # base_url='http://localhost:8081/bot'

                      )

    # updater.bot.logOut()
    # a = updater.bot.logOut()
    # b = updater.bot.close()
    # print(a)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('large', send_large_file))
    dispatcher.add_handler(CommandHandler('check', check))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
