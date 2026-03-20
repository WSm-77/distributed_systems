from fastapi import Body, FastAPI, status
from fastapi.responses import JSONResponse
from services.recipe_service import get_recipe
from services.food_info_service import get_food_info, get_nutrition_score

server = FastAPI()

@server.get("/v1/recipe")
async def get_recipe_api(diet_preferences: str = ""):
    try:
        recipeResponse = get_recipe(diet_preferences)
        top_recipe = recipeResponse.meals[0]

        vitamines = set()

        for ingredient in top_recipe.get_ingredients():
            food_info = get_food_info(ingredient.name)
            vitamins = food_info.get_vitamin_nutrients()
            vitamines.update(vitamins)

        return JSONResponse(content=top_recipe.model_dump(), status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@server.get("/v1/food_info")
async def get_food_info_api(food_name: str):
    try:
        food = get_food_info(food_name)
        print(food.model_dump_json())
        return JSONResponse(content=food.model_dump(), status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
