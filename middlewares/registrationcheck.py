from typing import Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import select

from db import User


class RegistrationCheck(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:
        async_session = data['db_session']
        async with async_session() as session:
            async with session.begin():
                user_id = event.from_user.id
                # statement = select(User).filter_by(user_id=user_id)
                # response = await session.execute(statement)
                # user = response.scalar()
                if user_id in [1046454890, 438391677]:
                    return await handler(event, data)
                # if user and user.allowed:
                #     return await handler(event, data)
                # elif user and not user.allowed:
                #     await event.answer('Access Denied.')
                # else:
                #     user = User(user_id=user_id, username=event.from_user.username, allowed=False)
                #     await session.merge(user)
                #     await event.answer("Please call administrator to get access.")
