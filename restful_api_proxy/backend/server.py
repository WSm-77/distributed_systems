import logging

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from config.logging_config import setup_logging
from services.food_info_service import get_food_info
from services.meal_service import get_meal
from services.recipe_service import get_recipe

setup_logging()
logger = logging.getLogger(__name__)

server = FastAPI()

@server.get("/v1/recipe")
async def get_recipe_api(main_ingredient: str | None = None, ingredients_to_exclude: list[str] = [], area: str | None = None, category: str | None = None):
    logger.info(
        "GET /v1/recipe called (main_ingredient=%s, area=%s, category=%s, exclusions=%d)",
        main_ingredient,
        area,
        category,
        len(ingredients_to_exclude),
    )
    try:
        recipe = get_recipe(main_ingredient, ingredients_to_exclude, area, category)

        if not recipe:
            logger.warning("No recipe found for the provided filters")
            return JSONResponse(content={"message": "No recipe found with the given criteria."}, status_code=status.HTTP_404_NOT_FOUND)

        logger.info("Recipe found: %s", recipe.strMeal)
        logger.debug("Recipe payload: %s", recipe.model_dump_json())

        return JSONResponse(content=recipe.model_dump(), status_code=status.HTTP_200_OK)
    except Exception:
        logger.exception("Unhandled error in /v1/recipe")
        return JSONResponse(content={"error": "Internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@server.get("/v1/food_info")
async def get_food_info_api(food_name: str):
    logger.info("GET /v1/food_info called (food_name=%s)", food_name)
    try:
        food = get_food_info(food_name)

        if food is None:
            logger.warning("No food info found for query: %s", food_name)
            return JSONResponse(content={"message": "No food info found."}, status_code=status.HTTP_404_NOT_FOUND)

        logger.info("Food info found for: %s", food.description)
        logger.debug("Food payload: %s", food.model_dump_json())

        return JSONResponse(content=food.model_dump(), status_code=status.HTTP_200_OK)
    except Exception:
        logger.exception("Unhandled error in /v1/food_info")
        return JSONResponse(content={"error": "Internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@server.get("/v1/meal")
async def get_meal_api(main_ingredient: str | None = None, ingredients_to_exclude: list[str] = [], area: str | None = None, category: str | None = None):
    logger.info(
        "GET /v1/meal called (main_ingredient=%s, area=%s, category=%s, exclusions=%d)",
        main_ingredient,
        area,
        category,
        len(ingredients_to_exclude),
    )
    try:
        meal = get_meal(main_ingredient, ingredients_to_exclude, area, category)
        logger.info("Meal assembled: %s", meal.strMeal)

        return JSONResponse(content=meal.model_dump(), status_code=status.HTTP_200_OK)
    except Exception:
        logger.exception("Unhandled error in /v1/meal")
        return JSONResponse(content={"error": "Internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
