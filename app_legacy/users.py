import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport
)
from app_legacy.db import User, get_user_db, async_session_maker
from app_legacy.customized import CustomizedBaseUserManager, CustomizablePayloadJWTStrategy, CustomizedSQLAlchemyUserDatabase

SECRET = "SECRET"

## Cutomize BaseUserManager


class UserManager(UUIDIDMixin, CustomizedBaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.user_id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.user_id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.user_id}. Verification token: {token}")


# async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
async def get_user_manager(user_db: CustomizedSQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


# def get_jwt_strategy() -> JWTStrategy:
#     return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

def get_jwt_strategy() -> CustomizablePayloadJWTStrategy:
    return CustomizablePayloadJWTStrategy(secret=SECRET,
                                          lifetime_seconds=3600,
                                          token_audience=["fastapi-users:auth"],
                                          algorithm="HS256",
                                          get_session=async_session_maker
            )

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
