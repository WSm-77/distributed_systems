from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv
import os, logging

PARENT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(PARENT_DIR)
ENV_PATH = os.path.join(ROOT_DIR, ".env")
load_dotenv(ENV_PATH)

class Settings(BaseSettings):
    food_data_central_api_key: str
    the_meal_db_api_key: str
    max_meals_to_return: int = 3
    log_level: int = logging.INFO

    @field_validator("log_level", mode="before")
    @classmethod
    def parse_log_level(cls, value: object) -> int:
        if isinstance(value, int):
            return value

        if isinstance(value, str):
            normalized = value.strip().upper()

            if not normalized:
                raise ValueError("LOG_LEVEL cannot be empty")

            if normalized.isdigit():
                return int(normalized)

            level_map = logging.getLevelNamesMapping()
            if normalized in level_map:
                return level_map[normalized]

            raise ValueError(f"Invalid LOG_LEVEL '{value}'")

        raise ValueError("LOG_LEVEL must be a logging level name or integer")

CONFIG = Settings()
