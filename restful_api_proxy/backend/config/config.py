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
    rate_limit_storage_uri: str = "redis://redis:6379"
    log_level: int = logging.INFO
    ollama_api: str = "http://localhost:11434/api/chat"
    model: str = "llama3.1:8b"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    system_prompt: str = """
    You are a helpful assistant that get's Recipe objects as an input and suggests substitutes for ingredients that the user wants to exclude. You should suggest substitutes that are as close as possible to the original ingredient in terms of taste and texture, and that would work well in the recipe. In the response, substitute the ingredient in the strIngredientX fields and the ingredient in the strInstructions field. Return recipe with all fields unchanged except the ones that need to be modified to replace the ingredient. If the ingredient to be replaced is not present in the recipe, return the original recipe without any modifications.
    """.strip()

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
