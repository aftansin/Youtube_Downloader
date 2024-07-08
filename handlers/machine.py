import os
import shutil

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from middlewares.registrationcheck import AdminProtect

machine_router = Router()
machine_router.message.middleware(AdminProtect())


@machine_router.message(Command("machine"))
async def command_users_handler(message: Message):
    total, used, free = shutil.disk_usage("/")
    total = total / (1024.0 ** 3)
    used = used / (1024.0 ** 3)
    free = free / (1024.0 ** 3)
    msg = (f'Сведения о системе: \n'
           f'Total: {round(total, 2)}\n'
           f'Used: {round(used, 2)}\n'
           f'Free: {round(free, 2)}\n')
    # check media folder is empty or not
    if len(os.listdir('./media')) == 0:
        msg += "Media directory is empty"
        await message.answer(msg)
    else:
        msg += "Media directory is NOT empty"
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text='Clear Media folder', callback_data=f'clear_folder'))
        await message.answer(msg, reply_markup=keyboard.as_markup(), disable_notification=True)


@machine_router.callback_query(F.data.startswith('clear_folder'))
async def clear_media_folder(callback: CallbackQuery):
    await callback.answer('')
    folder = './media'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            await callback.message.answer('Folder now is empty', disable_notification=True)
        except Exception as e:
            await callback.message.answer('Failed to delete %s. Reason: %s' % (file_path, e),
                                          disable_notification=True)


