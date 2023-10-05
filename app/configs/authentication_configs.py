from sqlalchemy import text
from typing import List, Optional
from fastapi_users import models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.jwt import SecretType, generate_jwt
from app.configs.baes_configs import base_config
from app.configs.db import async_session_maker

# this path must be same as login endpoint
bearer_transport = BearerTransport(tokenUrl=base_config.LOGIN_URI_PREFIX + "/login")

class CustomizablePayloadJWTStrategy(JWTStrategy):
    """
    this subclass is for customize token payload purpose
    TODO: decoupling
    """
    def __init__(
        self,
        secret: SecretType,
        lifetime_seconds: Optional[int],
        token_audience: List[str] = ["fastapi-users:auth"],
        algorithm: str = "HS256",
        public_key: Optional[SecretType] = None,
        custom_value: str = "",  # Add custom initialization parameter
    ):
        super().__init__(secret, lifetime_seconds, token_audience, algorithm, public_key)
    

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

def get_jwt_strategy() -> CustomizablePayloadJWTStrategy:
    return CustomizablePayloadJWTStrategy(secret=base_config.SECRET,
                                          lifetime_seconds=3600,
                                          token_audience=["fastapi-users:auth"],
                                          algorithm="HS256",
            )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)