from sqlalchemy import select, update

from db import User


async def get_user(user_id: int, async_session):
    async with async_session() as session:
        statement = select(User).filter_by(user_id=user_id)
        db_response = await session.execute(statement)
        user = db_response.scalar()
        return user


async def edit_user_quality(user_id: int, quality: str, async_session):
    async with async_session() as session:
        new_data = {'quality': quality}
        stmt = update(User).where(User.user_id == user_id).values(new_data)
        await session.execute(stmt)
        await session.commit()
