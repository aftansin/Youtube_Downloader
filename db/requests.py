import datetime

from sqlalchemy import select, update, insert

from db import User


async def get_user(user_id: int, async_session):
    async with async_session() as session:
        statement = select(User).filter_by(user_id=user_id)
        db_response = await session.execute(statement)
        user = db_response.scalar()
        return user


async def get_all_users(async_session):
    async with async_session() as session:
        statement = select(User)
        db_response = await session.execute(statement)
        users = db_response.scalars()
        return users.fetchall()


async def edit_user_quality(user_id: int, quality: str, async_session):
    async with async_session() as session:
        new_data = {'quality': quality}
        statement = update(User).where(User.user_id == user_id).values(new_data)
        await session.execute(statement)
        await session.commit()


async def edit_user_permission(user_id: int, allowed: bool, async_session):
    async with async_session() as session:
        new_data = {'allowed': allowed}
        statement = update(User).where(User.user_id == user_id).values(new_data)
        await session.execute(statement)
        await session.commit()


async def add_user_registration(user_id, username, allowed, async_session):
    async with async_session() as session:
        reg_date = datetime.datetime.now().date()
        statement = insert(User).values(user_id=user_id,
                                        username=username,
                                        reg_date=reg_date,
                                        allowed=allowed,
                                        quality='480p')
        await session.execute(statement)
        await session.commit()
