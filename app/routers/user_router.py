from fastapi import Depends, APIRouter

from app.configs.db import User, create_db_and_tables
from app.schemas.user_schema import UserCreate, UserRead, UserUpdate
from app.services.user_service import current_active_user


api_router = APIRouter(
    prefix="", tags=["author"]
)

# this event is for demoing database intialization
@api_router.on_event("startup")
def on_startup():
    # Not needed if you setup a migration system like Alembic
    create_db_and_tables()

# TODO
@api_router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
