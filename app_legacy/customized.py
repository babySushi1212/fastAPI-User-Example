import jwt
from typing import Optional, List, AsyncGenerator, Generic
from sqlalchemy import select

from fastapi import Request
from fastapi_users import models, exceptions, BaseUserManager
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.authentication import JWTStrategy
from fastapi_users.jwt import decode_jwt, generate_jwt, SecretType


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
        get_session: AsyncGenerator = None
    ):
        super().__init__(secret, lifetime_seconds, token_audience, algorithm, public_key)
        self.get_session = get_session

    async def customized_payload(self) -> str:
        async with self.get_session() as session:
            # some query result
            return {"role": "guest"}


    async def write_token(self, user: models.UP) -> str:
        payload = await self.customized_payload()
        data = {"sub": str(user.user_id), "aud": self.token_audience}
        data = {**data, **payload}
        return generate_jwt(
            data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm
        )



class CustomizedBaseUserManager(BaseUserManager, Generic[models.UP, models.ID]):
    async def request_verify(
        self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        if not user.is_active:
            raise exceptions.UserInactive()
        if user.is_verified:
            raise exceptions.UserAlreadyVerified()

        token_data = {
            "sub": str(user.user_id),
            "email": user.email,
            "aud": self.verification_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.verification_token_secret,
            self.verification_token_lifetime_seconds,
        )
        await self.on_after_request_verify(user, token, request)

    async def verify(self, token: str, request: Optional[Request] = None) -> models.UP:
        try:
            data = decode_jwt(
                token,
                self.verification_token_secret,
                [self.verification_token_audience],
            )
        except jwt.PyJWTError:
            raise exceptions.InvalidVerifyToken()

        try:
            user_id = data["sub"]
            email = data["email"]
        except KeyError:
            raise exceptions.InvalidVerifyToken()

        try:
            user = await self.get_by_email(email)
        except exceptions.UserNotExists:
            raise exceptions.InvalidVerifyToken()

        try:
            parsed_id = self.parse_id(user_id)
        except exceptions.InvalidID:
            raise exceptions.InvalidVerifyToken()

        if parsed_id != user.user_id:
            raise exceptions.InvalidVerifyToken()

        if user.is_verified:
            raise exceptions.UserAlreadyVerified()

        verified_user = await self._update(user, {"is_verified": True})

        await self.on_after_verify(verified_user, request)

        return verified_user

    async def forgot_password(
        self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        if not user.is_active:
            raise exceptions.UserInactive()

        token_data = {
            "sub": str(user.user_id),
            "password_fgpt": self.password_helper.hash(user.hashed_password),
            "aud": self.reset_password_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.reset_password_token_secret,
            self.reset_password_token_lifetime_seconds,
        )
        await self.on_after_forgot_password(user, token, request)


class CustomizedSQLAlchemyUserDatabase(SQLAlchemyUserDatabase):
    async def get(self, id: models.ID) -> Optional[models.UP]:
        statement = select(self.user_table).where(self.user_table.user_id == id)
        return await self._get_user(statement)
