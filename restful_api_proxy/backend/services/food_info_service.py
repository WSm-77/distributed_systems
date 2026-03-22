import logging

import httpx

from config.config import CONFIG
from data_models.food_info import FoodInfo, FoodInfoResponse

logger = logging.getLogger(__name__)

async def get_food_info(food_name: str) -> FoodInfo | None:
    logger.debug("Fetching food info from USDA for query: %s", food_name)
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            "https://api.nal.usda.gov/fdc/v1/foods/search",
            params={
                "query": food_name,
                "pageSize": 5,
                "adataType": "SR Legacy",
                "api_key": CONFIG.food_data_central_api_key,
            },
        )
    response.raise_for_status()

    logger.debug("USDA response size: %d chars", len(response.text))

    response_data = response.json()
    food_response = FoodInfoResponse.model_validate(response_data)

    if not food_response.foods:
        logger.warning("No foods returned by USDA for query: %s", food_name)
        return None

    food = food_response.foods[0]
    logger.info("Selected USDA food item: %s", food.description)

    return food
