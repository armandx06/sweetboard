from collections.abc import Sequence
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def find_repo_root(start: Path) -> Path:
    for directory in (start, *start.parents):
        if (directory / "pnpm-workspace.yaml").exists():
            return directory
    return start


ROOT_DIR = find_repo_root(Path(__file__).resolve())


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "db"
    postgres_internal_port: int = 5432
    allowed_origins: Sequence[str]

    postgres_testdb_user: str | None = None
    postgres_testdb_password: str | None = None
    postgres_testdb_db: str | None = None
    postgres_testdb_host: str = "test_db"
    postgres_testdb_internal_port: int = 5432

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_internal_port}/{self.postgres_db}"

    @property
    def test_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_testdb_user}:{self.postgres_testdb_password}@{self.postgres_testdb_host}:{self.postgres_testdb_internal_port}/{self.postgres_testdb_db}"


settings = Settings()  # type: ignore[call-arg]
