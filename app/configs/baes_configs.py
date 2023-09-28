
class BaseConfig:
    SECRET: str = "SECRET"
    LOGIN_URI_PREFIX: str = "/vsx/auth/jwt"
    DATABASE_URL: str = 'postgresql+asyncpg://postgres:admin@localhost:8080/postgres'


base_config = BaseConfig