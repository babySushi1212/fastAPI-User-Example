from sqlalchemy import Column

from sqlalchemy.sql.sqltypes import Text
from typing import ClassVar
from sqlalchemy.orm import DeclarativeBase
from fastapi_users.db import SQLAlchemyBaseUserTableUUID

class Base(DeclarativeBase):
    """
    Due to this Base model being only for User, we don't
    split the class into another module
    """
    pass


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

    __tablename__ = "demo_users"

    # add new column
    first_name = Column(Text, nullable=True)

    # override column constraint
    email = Column(Text, unique=True, nullable=True)

    # disable default column
    is_superuser: ClassVar[bool] = False
