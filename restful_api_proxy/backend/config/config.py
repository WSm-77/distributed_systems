from pydantic_settings import BaseSettings
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

CONFIG = Settings()
