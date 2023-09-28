from fastapi import FastAPI

from app.schemas.user_schema import UserCreate, UserRead, UserUpdate
from app.configs import auth_backend, base_config
from app.services.user_service import fastapi_users
from app.routers.user_router import api_router


"""
Each fastapi_users's factory will generate a relative endpoints.
For example:
    fastapi_users.get_auth_router(auth_backend), will generate /login and /logout
    Refer to the fastapi swagger documentation for more information.
"""

app = FastAPI()

app.include_router(api_router)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=base_config.LOGIN_URI_PREFIX,
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
