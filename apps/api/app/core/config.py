from collections.abc import Sequence

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "db"
    postgres_internal_port: int = 5432
    allowed_origins: Sequence[str]

    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_internal_port}/{self.postgres_db}"


settings = Settings()  # type: ignore[call-arg]
