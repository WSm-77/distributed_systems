import requests
from data_models.recipe import RecipeResponse, Recipe
from config.config import CONFIG
import random
import json

def get_random_recipies():
    print(f"Config values: {CONFIG.food_data_central_api_key}, {CONFIG.the_meal_db_api_key}")
    response = requests.get(f"https://www.themealdb.com/api/json/v1/{CONFIG.the_meal_db_api_key}/random.php")
    data = response.json()
    validated_recipe = RecipeResponse.model_validate(data)

    return validated_recipe.meals[0] if validated_recipe.meals else None

def get_recipe_by_id(meal_id: str) -> Recipe | None:
    response = requests.get(f"https://www.themealdb.com/api/json/v1/{CONFIG.the_meal_db_api_key}/lookup.php?i={meal_id}")
    data = response.json()
    validated_recipe = RecipeResponse.model_validate(data)

    return validated_recipe.meals[0] if validated_recipe.meals else None

def get_recipe(main_ingredient: str | None = None, ingredients_to_exclude: list[str] = [], area: str | None = None, category: str | None = None) -> Recipe | None:
    params = {}
    if main_ingredient:
        params["i"] = main_ingredient
    if area:
        params["a"] = area
    if category:
        params["c"] = category

    print(f"Getting recipe with parameters: {params} and ingredients to exclude: {ingredients_to_exclude}")

    if not params:
        return get_random_recipies()

    url = f"https://www.themealdb.com/api/json/v1/{CONFIG.the_meal_db_api_key}/filter.php"
    response = requests.get(url, params=params)

    if not response.ok:
        print(f"Failed to fetch recipes from TheMealDB API. Status code: {response.status_code}, Response: {response.text}")
        return None

    recipies = response.json()
    print(f"Raw response from TheMealDB API: {json.dumps(recipies)}")

    random.shuffle(recipies["meals"])

    for meal in recipies["meals"]:

        recipe = get_recipe_by_id(meal["idMeal"])

        ingredient_names = set(map(lambda x: x.name.strip("s"), recipe.get_ingredients()))

        if not any(ingredient_to_exclude in ingredient_names for ingredient_to_exclude in ingredients_to_exclude):
            return recipe

    print(f"No recipe found with the given criteria. Returning a random recipe.")

    return None
