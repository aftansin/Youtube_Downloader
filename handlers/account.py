from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from db.requests import get_user, edit_user_quality
from middlewares import RegistrationCheck


account_router = Router()
account_router.message.middleware(RegistrationCheck())


@account_router.message(Command("account"))
async def command_account_handler(message: Message, db_session) -> None:
    user = await get_user(message.from_user.id, db_session)
    allowed = 'Доступ разрешен' if user.allowed else 'Доступ запрещен'
    msg = (f'Мой профиль: \n'
           f'id: {user.user_id}\n'
           f'username: {user.username}\n'
           f'reg. date: {user.reg_date}\n'
           f'{allowed}\n'
           f'Качество видео: {user.quality}\n'
           f'Изменить качество скачивания: ')
    available_buttons = [
        [InlineKeyboardButton(text=f"mp3", callback_data=f"qlt mp3"),
         InlineKeyboardButton(text=f"480p", callback_data=f"qlt 480p"),
         InlineKeyboardButton(text=f"720p", callback_data=f"qlt 720p"),
         InlineKeyboardButton(text=f"1080p", callback_data=f"qlt 1080p")],
        [InlineKeyboardButton(text=f"Оставить как есть", callback_data=f"qlt 0")]
    ]
    for i, item in enumerate(['mp3', '480p', '720p', '1080p']):
        if item == user.quality:
            available_buttons[0].pop(i)
    keyboard = InlineKeyboardMarkup(inline_keyboard=available_buttons)

    await message.answer(msg, reply_markup=keyboard)


@account_router.callback_query(F.data.startswith('qlt'))
async def change_user_quality(callback: CallbackQuery, db_session):
    requested_quality = callback.data.split()[1]
    await callback.answer('')
    if requested_quality != '0':
        await edit_user_quality(callback.from_user.id, requested_quality, db_session)
        await callback.message.answer('Изменения сохранены!')
        await callback.message.delete_reply_markup()
    else:
        await callback.message.delete_reply_markup()
