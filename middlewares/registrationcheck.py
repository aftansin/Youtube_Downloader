import os
from typing import Dict, Any, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import select

from db import User
from db.requests import add_user_registration

load_dotenv()
ADMIN_ID = os.getenv("ADMIN_ID")


class AdminProtect(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        user_id = event.from_user.id
        if user_id == int(ADMIN_ID):
            return await handler(event, data)
        await event.answer('You dont have permissions to use this command.')


class RegistrationCheck(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:
        async_session = data['db_session']
        async with async_session() as session:
            async with session.begin():
                user_id = event.from_user.id
                username = event.from_user.username
                full_name = event.from_user.full_name
                statement = select(User).filter_by(user_id=user_id)
                response = await session.execute(statement)
                user = response.scalar()

                # если админ, то дадим доступ сразу
                if event.from_user.id == int(ADMIN_ID):
                    # запишем в бд админа, если его еще нет.
                    if not user:
                        await add_user_registration(user_id=user_id,
                                                    username=username,
                                                    allowed=True,
                                                    async_session=async_session)
                    return await handler(event, data)

                # проверим есть ли уже пользователь в базе
                # если нет, то запишем в бд и отправим сообщение
                if not user:
                    await add_user_registration(user_id=user_id,
                                                username=username,
                                                allowed=False,
                                                async_session=async_session)
                    msg = f'Hi, <b>{full_name}!</b> To use Bot please call admin @aftansin'
                    await event.answer(msg)
                    logger.info(f'Added new user: {full_name}')
                    return

                # если есть пользователь в бд, то проверим, может ли он им пользоваться
                if not user.allowed:
                    msg = (f'<b>{full_name}</b>, you dont have permissions.\n'
                           f'To use Bot please call admin @aftansin')
                    await event.answer(msg)
                    return

                return await handler(event, data)
