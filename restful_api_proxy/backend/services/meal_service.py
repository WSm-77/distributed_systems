from config.config import CONFIG
from data_models.meal import Meal
from services.recipe_service import get_recipe

def get_meal(main_ingredient: str | None = None, ingredients_to_exclude: list[str] = [], area: str | None = None, category: str | None = None):
    recipie = get_recipe(main_ingredient, ingredients_to_exclude, area, category)

    return recipie
