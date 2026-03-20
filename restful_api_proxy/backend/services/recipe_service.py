import requests, os
from dotenv import load_dotenv
from data_models.recipe import RecipeResponse

load_dotenv(os.path.dirname(os.path.dirname(__file__)) + "/.env")

THE_MEAL_DB_API_KEY = os.getenv("THE_MEAL_DB_API_KEY")
print(f"Using TheMealDB API key: {THE_MEAL_DB_API_KEY}")

def get_recipe(diet_preferences: str):
    response = requests.get(f"https://www.themealdb.com/api/json/v1/{THE_MEAL_DB_API_KEY}/random.php")
    data = response.json()
    validated_recipe = RecipeResponse.model_validate(data)

    return validated_recipe
