from sqlalchemy import Column

from sqlalchemy.sql.sqltypes import Text
from typing import AsyncGenerator, ClassVar, TYPE_CHECKING
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from fastapi_users.models import ID

import uuid
from sqlalchemy.dialects.postgresql import UUID
from fastapi_users_db_sqlalchemy.generics import GUID
from app_legacy.customized import CustomizedSQLAlchemyUserDatabase

DATABASE_URL: str = "postgresql+asyncpg://postgres:admin@localhost:8080/my-ocelot"

Base = declarative_base()


class UserBase(Base):
    __tablename__ = "demo_user"
    user_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )


class MySQLAlchemyBaseUserTable(SQLAlchemyBaseUserTable):
    __tablename__ = "demo_user"
    __table_args__ = {"extend_existing": True}

    if TYPE_CHECKING:  # pragma: no cover
        user_id: ID
        email: str
        hashed_password: str
        is_active: bool
        is_superuser: bool
        is_verified: bool


class User(MySQLAlchemyBaseUserTable, UserBase):
    """
    SQLAlchemyBaseUserTableUUID provide default table on version 11.0.0
        __tablename__ = "user"
        id: Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
        email: Column(Text(length=320), nullable=True)
        hashed_password: Column(Text(length=1024), nullable=True)
        is_active: Column(Boolean, nullable=False, default=True)
        is_superuser: Column(Boolean, nullable=False, default=True)
        is_verified: Column(Boolean, nullable=False, default=True)
    """

    __tablename__ = "demo_user"
    # add new column

    # user_id: Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    first_name = Column(Text, nullable=True)
    last_name = Column(Text)
    create_from = Column(Text)
    country = Column(Text)
    default_display_name = Column(Text)

    # override column constraint
    email = Column(Text, unique=True, nullable=True)

    # disable default column
    is_superuser: ClassVar[bool] = False
    id: ClassVar[GUID] = False

    # id: ClassVar[bool] = False

    class Config:
        from_attributes = True


engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# from SQLAlchemyUserDatabase to CustomizedSQLAlchemyUserDatabase
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    # yield SQLAlchemyUserDatabase(session, User)
    yield CustomizedSQLAlchemyUserDatabase(session, User)
