

## Customize

In `app/configs/authentication_configs.py`, we subclass `fastapi_users.authentication JWTStrategy` for cutomizing token payload purposes.
- add `async def get_user_role(self) -> str` to get user role
- In `async def write_token(self, user: models.UP) -> str:`, we add user role into token payload

```python=
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

```python=
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