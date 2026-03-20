import requests
from data_models.recipe import RecipeResponse
from config.config import CONFIG

def get_recipe(diet_preferences: str):
    print(f"Config values: {CONFIG.food_data_central_api_key}, {CONFIG.the_meal_db_api_key}")
    response = requests.get(f"https://www.themealdb.com/api/json/v1/{CONFIG.the_meal_db_api_key}/random.php")
    data = response.json()
    validated_recipe = RecipeResponse.model_validate(data)

    return validated_recipe
