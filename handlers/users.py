from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.formatting import as_list, as_marked_section, Bold, as_key_value
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncEngine

from db.requests import get_all_users, get_user, drop_user, edit_user_permission
from middlewares.registrationcheck import AdminProtect

users_router = Router()
users_router.message.middleware(AdminProtect())


async def get_users_inline_kb(async_session):
    all_users = await get_all_users(async_session)
    keyboard = InlineKeyboardBuilder()
    for person in all_users:
        text = '✅ ' if person.allowed else '❌ '
        text += person.username
        keyboard.add(InlineKeyboardButton(text=text, callback_data=f'user_{person.user_id}'))
    return keyboard.adjust(1).as_markup()


@users_router.message(Command("users"))
async def command_users_handler(message: Message, db_session: AsyncEngine):
    msg = f'Все пользователи: '
    await message.answer(msg, reply_markup=await get_users_inline_kb(db_session), disable_notification=True)


@users_router.callback_query(F.data.startswith('user_'))
async def user(callback: CallbackQuery, db_session: AsyncEngine):
    db_user = await get_user(int(callback.data.split('_')[1]), db_session)
    await callback.answer('')
    allowed_marker = '🟢 Разрешен' if db_user.allowed else '🔴 Запрещен'
    content = as_list(
        as_marked_section(
            Bold("Пользователь:"),
            as_key_value("ID", db_user.user_id),
            as_key_value("FULLNAME", f'@{db_user.username}'),
            as_key_value("REG DATE", db_user.reg_date),
            marker="🔸 ",
        ),
        as_marked_section(
            Bold("Доступ:"),
            f"{allowed_marker}",
            marker="",
        ),
        sep="\n",
    )
    buttons = []
    if db_user.allowed:
        buttons.append([InlineKeyboardButton(text=f"Убрать доступ?", callback_data=f"awd_{db_user.user_id}_0")])
    else:
        buttons.append([InlineKeyboardButton(text=f"Предоставить доступ?", callback_data=f"awd_{db_user.user_id}_1")])
    buttons.append([InlineKeyboardButton(text=f"Оставить как есть", callback_data=f"awd_{db_user.user_id}_2")])
    buttons.append([InlineKeyboardButton(text=f"Удалить?", callback_data=f"awd_{db_user.user_id}_3")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(**content.as_kwargs(), reply_markup=keyboard)


@users_router.callback_query(F.data.startswith('awd_'))
async def give_permissions(callback: CallbackQuery, bot: Bot, db_session: AsyncEngine):
    user_id = callback.data.split('_')[1]
    privileges = callback.data.split('_')[2]
    await callback.answer('')
    if privileges == '3':  # delete user from db
        await drop_user(int(user_id), db_session)
        await callback.message.answer('Пользователь удален!')
        await callback.message.delete_reply_markup()
        return
    if privileges == '2':  # leave the same
        await callback.message.delete_reply_markup()
        return
    await edit_user_permission(int(user_id), bool(int(privileges)), db_session)
    await callback.message.answer('Привилегии изменены', disable_notification=True)
    await callback.message.delete_reply_markup()
    msg = '✅ You have been granted access!' if bool(int(privileges)) else '❌ You have been denied!'
    await bot.send_message(chat_id=user_id, text=msg)
