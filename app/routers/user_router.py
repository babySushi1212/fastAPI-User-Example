import uuid

from fastapi import Depends, APIRouter
from fastapi_users import FastAPIUsers

from app.models.User import User
from app.configs.db import create_db_and_tables
from app.configs import auth_backend
from app.services.user_service import get_user_manager

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

api_router = APIRouter(
    prefix="", tags=["author"]
)

# this event is for demoing database intialization
@api_router.on_event("startup")
def on_startup():
    # Not needed if you setup a migration system like Alembic
    create_db_and_tables()

# fastapi_users as a repository
@api_router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(fastapi_users.current_user(active=True))):
    return {"message": f"Hello {user.email}!"}
