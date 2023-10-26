from typing import Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import text

from db import User


class RegistrationCheck(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:
        async_session = data['session_maker']
        async with async_session() as session:
            async with session.begin():
                user_id = event.from_user.id
                response = await session.execute(text(f"select * from user where user_id = {user_id};"))
                user = response.one_or_none()
                if user and user.allowed:
                    return await handler(event, data)
                elif user and not user.allowed:
                    await event.answer('Access Denied.')
                else:
                    user = User(user_id=user_id, username=event.from_user.username, allowed=False)
                    await session.merge(user)
                    await event.answer("Please call administrator to get access. "
                                       "May be you will get help, but I'm not sure.")
