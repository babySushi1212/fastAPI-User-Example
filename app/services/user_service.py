import uuid
from typing import Optional, Dict, Any

from fastapi import Depends, Request
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

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")
        print('[request] ', request.__dict__)


    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        print('[request] ', request)

    async def on_after_update(
        self, user: User, update_dict: Dict[str, Any], request: Optional[Request] = None
    ):
        print(f"{user}")
        
    
    # async def on_after_verify(
    #     self, user: models.UP, request: Optional[Request] = None
    # ) -> None:


    # async def on_after_reset_password(
    #     self, user: models.UP, request: Optional[Request] = None
    # ) -> None:

    # async def on_after_login(
    #     self,
    #     user: models.UP,
    #     request: Optional[Request] = None,
    #     response: Optional[Response] = None,
    # )
        
    # async def on_before_delete(
    #     self, user: models.UP, request: Optional[Request] = None
    # ) -> None:

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)