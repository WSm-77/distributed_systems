from config.config import CONFIG
from data_models.meal import Meal
from services.recipe_service import get_recipe
from services.food_info_service import get_food_info

def get_meal(main_ingredient: str | None = None, ingredients_to_exclude: list[str] = [], area: str | None = None, category: str | None = None):
    recipie = get_recipe(main_ingredient, ingredients_to_exclude, area, category)

    food_info = None
    try:
        food_info = get_food_info(recipie.strMeal)
    except Exception as e:
        print(f"Error occurred while fetching food info for {recipie.strMeal}: {e}")

    vitamines = set()
    if food_info:
        vitamines = set(food_info.get_vitamin_nutrients())


    meal = Meal(
        strMeal=recipie.strMeal,
        strCategory=recipie.strCategory,
        strArea=recipie.strArea,
        strInstructions=recipie.strInstructions,
        ingredients=recipie.get_ingredients(),
        vitamines=vitamines
    )

    return meal
