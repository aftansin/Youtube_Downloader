from typing import Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import select

from db import User


# class RegistrationCheck(BaseMiddleware):
#     async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:
#         user_id = event.from_user.id
#         if int(user_id) in [1046454890, 438391677]:
#             return await handler(event, data)


class RegistrationCheck(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:
        async_session = data['db_session']
        async with async_session() as session:
            async with session.begin():
                user_id = event.from_user.id
                statement = select(User).filter_by(user_id=user_id)
                response = await session.execute(statement)
                user = response.scalar()
                if user and user.allowed:
                    return await handler(event, data)
                await event.answer('Access Denied.')
