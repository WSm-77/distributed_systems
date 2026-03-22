import logging

from data_models.meal import Meal
from services.food_info_service import get_food_info
from services.recipe_service import get_recipe

logger = logging.getLogger(__name__)

async def get_meal(
    main_ingredient: str | None = None,
    ingredients_to_exclude: list[str] | None = None,
    area: str | None = None,
    category: str | None = None,
) -> Meal:
    logger.debug("Building meal object from recipe and nutrition sources")
    recipe = await get_recipe(main_ingredient, ingredients_to_exclude, area, category)

    if recipe is None:
        logger.error("Cannot build meal because no recipe matched input filters")
        raise ValueError("Recipe not found for provided filters.")

    food_info = None
    try:
        food_info = await get_food_info(recipe.strMeal)
    except Exception:
        logger.exception("Failed to fetch food info for meal: %s", recipe.strMeal)

    vitamines: set[str] = set()
    if food_info:
        vitamines = set(food_info.get_vitamin_nutrients())
        logger.debug("Extracted %d vitamins for meal %s", len(vitamines), recipe.strMeal)
    else:
        logger.info("Proceeding without vitamin enrichment for %s", recipe.strMeal)


    meal = Meal(
        strMeal=recipe.strMeal,
        strCategory=recipe.strCategory,
        strArea=recipe.strArea,
        strInstructions=recipe.strInstructions,
        ingredients=recipe.get_ingredients(),
        vitamines=list(vitamines)
    )

    logger.info("Meal created successfully: %s", meal.strMeal)

    return meal
