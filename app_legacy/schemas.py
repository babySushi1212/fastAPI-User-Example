import uuid

from fastapi_users import schemas

from sqlalchemy import Column

from sqlalchemy.sql.sqltypes import Text

class UserRead(schemas.BaseUser[uuid.UUID]):
    # first_name : str
    first_name : str
    
    class Config:
        from_attributes = True

class UserCreate(schemas.BaseUserCreate):
    first_name : str

class UserUpdate(schemas.BaseUserUpdate):
    first_name : str
