from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from app.configs.baes_configs import base_config


# this path must be same as login endpoint
bearer_transport = BearerTransport(tokenUrl=base_config.LOGIN_URI_PREFIX + "/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=base_config.SECRET,
                       lifetime_seconds=3600,
                       token_audience=["fastapi-users:auth"],
                       algorithm="HS256",
            )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)