import json, logging, random, requests
from config.config import CONFIG
from data_models.recipe import Recipe, RecipeResponse
from services.find_substitute_service import find_substitute

logger = logging.getLogger(__name__)

def get_random_recipe():
    logger.debug("Fetching random recipe from TheMealDB")
    response = requests.get(
        f"https://www.themealdb.com/api/json/v1/{CONFIG.the_meal_db_api_key}/random.php",
        timeout=15,
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

def get_recipe_by_id(meal_id: str) -> Recipe | None:
    logger.debug("Fetching recipe details for id=%s", meal_id)
    response = requests.get(
        f"https://www.themealdb.com/api/json/v1/{CONFIG.the_meal_db_api_key}/lookup.php",
        params={"i": meal_id},
        timeout=15,
    )
    response.raise_for_status()

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

    logger.info(
        "Fetching recipe (main_ingredient=%s, area=%s, category=%s, exclusions=%d)",
        main_ingredient,
        area,
        category,
        len(ingredients_to_exclude),
    )
    logger.debug("TheMealDB filter parameters: %s", params)

    detailed_recipe = None

    if not params:
        logger.info("No filters provided, using random recipe")
        detailed_recipe = get_random_recipe()
    else:
        url = f"https://www.themealdb.com/api/json/v1/{CONFIG.the_meal_db_api_key}/filter.php"
        response = requests.get(url, params=params, timeout=15)

        if not response.ok:
            logger.error(
                "Failed to fetch recipes from TheMealDB API (status=%s, body=%s)",
                response.status_code,
                response.text[:500],
            )
            return None

        recipies = response.json()
        logger.debug("Raw response from TheMealDB API: %s", json.dumps(recipies)[:1000])

        if not recipies.get("meals"):
            logger.warning("No recipes returned for the provided filters")
            return None

        recipe = random.choice(recipies["meals"])

        logger.debug("Selected recipe: %s", json.dumps(recipe))

        detailed_recipe = get_recipe_by_id(recipe["idMeal"])

    if not detailed_recipe:
        logger.warning("Failed to fetch details for recipe id=%s", recipe["idMeal"])
        return None

    if ingredients_to_exclude:
        logger.info("Applying ingredient exclusions: %s", ", ".join(ingredients_to_exclude))

        modified_recipe = find_substitute(detailed_recipe, ingredients_to_exclude)

        if modified_recipe:
            logger.info("Successfully found substitute recipe for exclusions")
            return modified_recipe
        else:
            logger.warning("Failed to find substitute recipe for exclusions, returning original recipe")
            return detailed_recipe

    return detailed_recipe
