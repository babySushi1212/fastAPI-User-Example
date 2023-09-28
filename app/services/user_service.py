import uuid
from typing import Optional, Dict, Any

from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager, UUIDIDMixin, FastAPIUsers
from fastapi_users.db import SQLAlchemyUserDatabase

from app.models.User import User
from app.configs import auth_backend, base_config
from app.configs.db import get_user_db

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """
    register, forgot_password, ...'s repository are handle by fastaip|user
    """
    reset_password_token_secret = base_config.SECRET
    verification_token_secret = base_config.SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_login(
        self, user: User, request: Optional[Request] = None, response: Optional[Response] = None,
    ):
        import json
        response_data = json.loads(response.body)
        access_token = response_data.get('access_token')
        print(f"User {user.id} login. Custom token payload of first name is {parse_jwt(access_token)}")
        print(f"If needed, storing back the token {access_token}")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_update(
        self, user: User, update_dict: Dict[str, Any], request: Optional[Request] = None
    ):
        print(f"{user}")
        
    async def on_after_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Successful user verification. {user.id}. Verification token: {token}")

    async def on_after_reset_password(
        self, user: User, request: Optional[Request] = None
    ):
        print(f"User {user.id} reset the password")

    async def on_before_delete(
        self, user: User, request: Optional[Request] = None, response: Optional[Response] = None,
    ):
        print(f"User {user.id} been deleted")

def parse_jwt(token: str) -> str:
    import jwt
    secret_key = "SECRET"
    decoded_token = jwt.decode(token, secret_key, audience=["fastapi-users:auth"], algorithms='HS256')

    # Access the claims (payload) of the JWT
    return decoded_token.get('first_name')

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
