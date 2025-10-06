import os

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    api_v1_prefix: str = "api/v1"
    sqlite_db_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/fb.db"
    db_echo: bool = True

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_days: int

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_db: str

    @property
    def postgres_sync_db_url(self) -> str:
        """Get a database URL for a synchronous PostgreSQL connection.

        This property returns a database URL that can be used with
        synchronous database drivers such as psycopg2.

        The URL is constructed from the following settings:

            - `postgres_user`
            - `postgres_password`
            - `postgres_host`
            - `postgres_port`
            - `postgres_db`

        The URL will be in the following format:
            postgresql+psycopg://<user>:<password>@<host>:<port>/<db>
        """
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )

    @property
    def postgres_async_db_url(self) -> str:
        """Get a database URL for an asynchronous PostgreSQL connection.

        This property returns a database URL that can be used with
        asynchronous database drivers such as asyncpg.

        The URL is constructed from the following settings:

            - `postgres_user`
            - `postgres_password`
            - `postgres_host`
            - `postgres_port`
            - `postgres_db`

        The URL will be in the following format:
            postgresql+asyncpg://<user>:<password>@<host>:<port>/<db>
        """
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
