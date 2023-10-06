## Introduction

A registration and authentication system to the FastAPI project. 
According to [official flow chart](https://fastapi-users.github.io/fastapi-users/12.1/configuration/overview/)
1. prepare a model (User) for the `UserManager`, which manages user repository behavior and partial service automatically.
    - `UserManager` provides a hook for us to do something after the endpoint has been called.
2. prepare `Authentication stratagy` - [official document](https://fastapi-users.github.io/fastapi-users/12.1/configuration/authentication/)
3. provide `UserManager`, `Authentication stratagy` and `Schemas` for `FastAPIUsers`
    - `FastAPIUsers` is a router factory
    - `FastAPIUsers` is also a repository for user with condition like `active`, `verified`

> fastapi-users[sqlalchemy] version 12.1.2

## UserManager

[Official Document](https://fastapi-users.github.io/fastapi-users/12.1/configuration/user-manager/)
- on_after_register
- on_after_forgot_password
    - we can send emails to users through this function.

## FastAPIUsers

router factory [Official Document](https://fastapi-users.github.io/fastapi-users/12.1/usage/routes/)
```python
fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

# router for login, logout endpoint
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=base_config.LOGIN_URI_PREFIX,
    tags=["auth"]
)

# router for register endpoint
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# router for POST/forgot-password, POST/reset-password endpoint
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

# router for POST/request-verify-token, POST/verify
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

# router for GET/me, PATCH/me, GET/{user_id}, PATCH/{user_id}, DELETE/{user_id}
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
```


## Model

default `User` model

```python
"""
    Table('user', MetaData(), 
    Column('email', String(length=320), table=<user>, nullable=False),
    Column('hashed_password', String(length=1024), table=<user>, nullable=False),
    Column('is_active', Boolean(), table=<user>, nullable=False, default=ColumnDefault(True)),
    Column('is_superuser', Boolean(), table=<user>, nullable=False, default=ColumnDefault(False)), 
    Column('is_verified', Boolean(), table=<user>, nullable=False, default=ColumnDefault(False)),
    Column('id', GUID(), table=<user>, primary_key=True, nullable=False, default=ColumnDefault(<function uuid4 at 0x1057a5b40>)), schema=None)
"""
```


## Schemas

schemas must match the User model. - [Official Document](https://fastapi-users.github.io/fastapi-users/12.1/configuration/schemas/)

```python
# User model
class User(SQLAlchemyBaseUserTableUUID, Base):
    first_name = Column(Text, nullable=True)
    is_superuser: ClassVar[bool] = False

# schemas
class UserCreate(schemas.BaseUserCreate):
    first_name: str
    is_superuser: ClassVar[bool] = False

```

## Customize

In `app/configs/authentication_configs.py`, we subclass `fastapi_users.authentication JWTStrategy` for cutomizing token payload purposes.
- We hardcoded the session into Strategies. See the [official flow chart](https://fastapi-users.github.io/fastapi-users/12.1/configuration/overview/)
- add `async def get_user_role(self) -> str` to get user role
- In `async def write_token(self, user: models.UP) -> str:`, we add user role into token payload

```python
# code snippet from app/configs/authentication_configs.py
async def get_user_role(self) -> str:
    async with async_session_maker() as session:
        stmt = text("SELECT first_name FROM demo_users WHERE email = 'user@example.com'")
        result = await session.execute(stmt)
        return result.fetchone()[0]

async def write_token(self, user: models.UP) -> str:
    first_name = await self.get_user_role()
    data = {"sub": str(user.id), "aud": self.token_audience, "first_name": first_name}
    return generate_jwt(
        data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm
    )

```

When using the `http://127.0.0.1:8000/docs#/` login endpoint, we demonstrate successfully adding customized data to the payload by printing the `"first_name": first_name` decoded from the token.

```python
# code snippet from app/services/user_service.py
async def on_after_login(
    self, user: User, request: Optional[Request] = None, response: Optional[Response] = None,
):
    import json
    response_data = json.loads(response.body)
    access_token = response_data.get('access_token')
    print(f"User {user.id} login. Custom token payload of first name is {parse_jwt(access_token)}")
    print(f"If needed, storing back the token {access_token}")

```

## Legacy

### Dependency

- If you need to stay on SQLAlchemy 1.4, you can pin this dependency: fastapi-users-db-sqlalchemy<5.0.0 - [release notes](https://github.com/fastapi-users/fastapi-users/releases)
- SQLAlchemy<=1.4.41 for sqlmodel dependency

### Code

- sqlalchemy create engine [docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- sqlalchemy base model [docs](https://docs.sqlalchemy.org/en/14/orm/declarative_styles.html)

```bash
pydantic.errors.PydanticUserError: You must set the config attribute `from_attributes=True` to use from_orm
```
- [issue](https://github.com/pydantic/pydantic/discussions/5393)
- and a queryset part is also need some hook for conversion:
- add below nested class config 
```python
class Config:
    from_attributes = True
```

## Migration

### assign new primary-key

add `__table_args__ = {'extend_existing': True}`
If A table inherit B, C table which have same table name.
we have to add above attributes to one of B or C

- [stackoverflow](https://stackoverflow.com/questions/37908767/table-roles-users-is-already-defined-for-this-metadata-instance)

## TODO

- [OAuth2](https://fastapi-users.github.io/fastapi-users/12.1/configuration/oauth/)
- [password hash](https://fastapi-users.github.io/fastapi-users/12.1/configuration/password-hash/)
