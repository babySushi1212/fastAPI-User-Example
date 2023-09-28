from typing import AsyncGenerator, List

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text
from app.configs.baes_configs import base_config
from app.models.User import User, Base

engine = create_async_engine(base_config.DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def main():
    async with async_session_maker() as session:
        stmt = text("SELECT first_name FROM demo_users WHERE email = 'user@example.com'")
        result = await session.execute(stmt)

        first_name = result.fetchone()[0]
        print(first_name)
