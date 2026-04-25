from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(REPO_ROOT_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    rabbitmq_url: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "admin"
    rabbitmq_password: str = "admin"

    # exchange names
    topic_exchange: str = "space-delivery"

    # queue names
    admin_bradcaset_queue: str = "admin-braodcast-queue"
    admin_all_messages_queue: str = "admin-all-messages-queue"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
