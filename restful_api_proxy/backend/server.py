from fastapi import Body, FastAPI, status
from fastapi.responses import JSONResponse
from services.meal_service import get_meal
from services.recipe_service import get_recipe
from services.food_info_service import get_food_info

server = FastAPI()

@server.get("/v1/recipe")
async def get_recipe_api(main_ingredient: str | None = None, ingredients_to_exclude: list[str] = [], area: str | None = None, category: str | None = None):
    try:
        recipie = get_recipe(main_ingredient, ingredients_to_exclude, area, category)

        print(f"Recipe found: {recipie}")

        if not recipie:
            return JSONResponse(content={"message": "No recipe found with the given criteria."}, status_code=status.HTTP_404_NOT_FOUND)

        return JSONResponse(content=recipie.model_dump(), status_code=status.HTTP_200_OK)
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

@server.get("/v1/meal")
async def get_meal_api(main_ingredient: str | None = None, ingredients_to_exclude: list[str] = [], area: str | None = None, category: str | None = None):
    try:

        # print(f"Received request with parameters: main_ingredient={main_ingredient}, ingredients_to_exclude={ingredients_to_exclude}, area={area}, category={category}")
        # return JSONResponse(content={"message": "This endpoint is under construction. Please check back later."}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

        meal = get_meal(main_ingredient, ingredients_to_exclude, area, category)

        return JSONResponse(content=meal.model_dump(), status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
