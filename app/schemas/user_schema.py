import uuid

from fastapi_users import schemas
from typing import ClassVar

"""
using Pydantic models to validate request payloads and serialize responses
- BaseUser: which provides the basic fields and validation;
- BaseCreateUser: dedicated to user registration, which consists of compulsory email and password fields;
- BaseUpdateUser: dedicated to user profile update, which adds an optional password field;

"""

class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str
    is_superuser: ClassVar[bool] = False


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    is_superuser: ClassVar[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    pass