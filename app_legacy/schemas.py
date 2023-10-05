import uuid

from fastapi_users import schemas

class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name : str
    last_name: str
    create_from: str
    country: str
    default_display_name: str
    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    first_name : str
    last_name: str
    create_from: str
    country: str
    default_display_name: str


class UserUpdate(schemas.BaseUserUpdate):
    first_name : str
    last_name: str
    create_from: str
    country: str
    default_display_name: str

