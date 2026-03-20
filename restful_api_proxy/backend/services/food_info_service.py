import os, requests
from config.config import CONFIG
from data_models.food_info import FoodInfoResponse, FoodInfo

def get_food_info(food_name: str):
    # TODO
    response = requests.get(f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&pageSize=5&adataType=SR%20Legacy&api_key={CONFIG.food_data_central_api_key}")

    print(f"Raw response from Food Data Central API: {response.text}")

    response_data = response.json()

    food_response = FoodInfoResponse.model_validate(response_data)

    print(f"FoodResponse:")
    print(food_response.model_dump_json())

    food = food_response.foods[0]

    return food

def get_nutrition_score(food_name: str):
    # TODO
    pass
