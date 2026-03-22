import json, logging, random, httpx
from config.config import CONFIG
from data_models.recipe import Recipe, RecipeResponse
from services.find_substitute_service import find_substitute

logger = logging.getLogger(__name__)

async def get_random_recipe() -> Recipe | None:
    logger.debug("Fetching random recipe from TheMealDB")
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"https://www.themealdb.com/api/json/v1/{CONFIG.the_meal_db_api_key}/random.php",
        )
    response.raise_for_status()

    data = response.json()
    validated_recipe = RecipeResponse.model_validate(data)
    recipe = validated_recipe.meals[0] if validated_recipe.meals else None

    if recipe:
        logger.info("Random recipe selected: %s", recipe.strMeal)
    else:
        logger.warning("TheMealDB returned no random recipe")

    return recipe

async def get_recipe_by_id(meal_id: str) -> Recipe | None:
    logger.debug("Fetching recipe details for id=%s", meal_id)
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"https://www.themealdb.com/api/json/v1/{CONFIG.the_meal_db_api_key}/lookup.php",
            params={"i": meal_id},
        )
    response.raise_for_status()

    data = response.json()
    validated_recipe = RecipeResponse.model_validate(data)

    return validated_recipe.meals[0] if validated_recipe.meals else None

async def get_recipe(
    main_ingredient: str | None = None,
    ingredients_to_exclude: list[str] | None = None,
    area: str | None = None,
    category: str | None = None,
) -> Recipe | None:
    exclusions = ingredients_to_exclude or []
    params: dict[str, str] = {}
    if main_ingredient:
        params["i"] = main_ingredient
    if area:
        params["a"] = area
    if category:
        params["c"] = category

    logger.info(
        "Fetching recipe (main_ingredient=%s, area=%s, category=%s, exclusions=%d)",
        main_ingredient,
        area,
        category,
        len(exclusions),
    )
    logger.debug("TheMealDB filter parameters: %s", params)

    detailed_recipe = None
    selected_recipe_id: str | None = None

    if not params:
        logger.info("No filters provided, using random recipe")
        detailed_recipe = await get_random_recipe()
    else:
        url = f"https://www.themealdb.com/api/json/v1/{CONFIG.the_meal_db_api_key}/filter.php"
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, params=params)

        if response.is_error:
            logger.error(
                "Failed to fetch recipes from TheMealDB API (status=%s, body=%s)",
                response.status_code,
                response.text[:500],
            )
            return None

        recipes = response.json()
        logger.debug("Raw response from TheMealDB API: %s", json.dumps(recipes)[:1000])

        if not recipes.get("meals"):
            logger.warning("No recipes returned for the provided filters")
            return None

        recipe = random.choice(recipes["meals"])
        selected_recipe_id = recipe["idMeal"]

        logger.debug("Selected recipe: %s", json.dumps(recipe))

        detailed_recipe = await get_recipe_by_id(selected_recipe_id)

    if not detailed_recipe:
        logger.warning("Failed to fetch details for recipe id=%s", selected_recipe_id)
        return None

    if exclusions:
        logger.info("Applying ingredient exclusions: %s", ", ".join(exclusions))

        modified_recipe = await find_substitute(detailed_recipe, exclusions)

        if modified_recipe:
            logger.info("Successfully found substitute recipe for exclusions")
            return modified_recipe
        else:
            logger.warning("Failed to find substitute recipe for exclusions, returning original recipe")
            return detailed_recipe

    return detailed_recipe
