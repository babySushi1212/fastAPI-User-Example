from sqlalchemy import Column

from sqlalchemy.sql.sqltypes import Text

from typing import AsyncGenerator, ClassVar
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL: str = "postgresql+asyncpg://postgres:admin@localhost:8080/my-ocelot"

Base = declarative_base()


class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    SQLAlchemyBaseUserTableUUID provide default table as below
       __tablename__ = "user"
        id: ID
        email: str
        hashed_password: str
        is_active: bool
        is_superuser: bool
        is_verified: bool
    """

    __tablename__ = "demo_user"
    # add new column
    first_name = Column(Text, nullable=True)

    # override column constraint
    email = Column(Text, unique=True, nullable=True)

    # disable default column
    is_superuser: ClassVar[bool] = False

    class Config:
        from_attributes = True



engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
