import json
import logging

import requests
from data_models.recipe import Recipe
from config.logging_config import setup_logging

from pydantic import BaseModel, ConfigDict
from typing import Any

setup_logging()

OLLAMA_API = "http://localhost:11434/api/chat"
MODEL = "llama3.1:8b"

headers = {"Content-Type": "application/json"}

SYSTEM_PROMPT = """
You are a helpful assistant that get's Recipe objects as an input and suggests substitutes for ingredients that the user wants to exclude. You should suggest substitutes that are as close as possible to the original ingredient in terms of taste and texture, and that would work well in the recipe. In the response, substitute the ingredient in the strIngredientX fields and the ingredient in the strInstructions field. Return recipe with all fields unchanged except the ones that need to be modified to replace the ingredient. If the ingredient to be replaced is not present in the recipe, return the original recipe without any modifications.
""".strip()

class ResponseMessage(BaseModel):
    model_config = ConfigDict(extra="allow")

    content: str


class OllamaResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str
    message: ResponseMessage


recipe_model_schema = Recipe.model_json_schema()
recipe_field_names = list(
    filter(
        lambda x:
        "strIngredient" in x or "strMeasure" in x or "strInstructions" == x,
        Recipe.model_fields.keys()
    )
)

def find_substitute(recipe: Recipe, ingredient: str) -> Recipe | None:

    # logging.info(recipe_field_names)

    # return
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Modify following recipe by replacing {ingredient} with a suitable substitute? {recipe.model_dump_json()}"}
        ],
        "stream": False,
        "format": {
            "type": "object",
            "properties": recipe_model_schema.get("properties", {}),
            "required": recipe_field_names
        }
    }

    # logging.debug("Ollama API request payload: %s", json.dumps(payload, indent=2))
    # return None

    try:
        response = requests.post(OLLAMA_API, data=json.dumps(payload), headers=headers, timeout=120)

        logging.debug("Ollama API response status: %d", response.status_code)
        logging.debug("Ollama API response: %s", response.text)
        logging.debug("Ollama API request payload: %s", json.dumps(payload))
        logging.debug("Ollama API response: %s", response)
        logging.debug("Ollama API response: %s", response.text)

        response.raise_for_status()
        raw_data = response.json()

        logging.debug("Raw response from Ollama: %s", raw_data)

        ollama_response = OllamaResponse.model_validate(raw_data)

        message = ollama_response.message

        logging.debug("Message from Ollama: %s", message)

        content_raw = message.content.strip()
        # if content_raw.startswith("```"):
        #     # Some models return fenced JSON blocks.
        #     content_raw = content_raw.strip("`")
        #     if content_raw.startswith("json"):
        #         content_raw = content_raw[4:].strip()

        content: Any = json.loads(content_raw)
        # if not isinstance(content, dict):
        #     raise ValueError("Ollama message content must be a JSON object")

        logging.debug("Content from Ollama: %s", content)

        # Merge model output onto the original recipe in case Ollama returns partial fields.
        merged_recipe = recipe.model_dump()
        merged_recipe.update(content)
        modified_recipe_validated = Recipe.model_validate(merged_recipe)

        logging.info("Substitute recipe generated for ingredient: %s", ingredient)

        return modified_recipe_validated
    except Exception:
        logging.exception("Error while finding substitute for ingredient: %s", ingredient)
        return None

if __name__ == "__main__":
    test_ingredient = "garlic"
    recipe_data = {
            "idMeal": "52771",
            "strMeal": "Spicy Arrabiata Penne",
            "strMealAlternate": None,
            "strCategory": "Vegetarian",
            "strArea": "Italian",
            "strInstructions": "Bring a large pot of water to a boil. Add kosher salt to the boiling water, then add the pasta. Cook according to the package instructions, about 9 minutes.\r\nIn a large skillet over medium-high heat, add the olive oil and heat until the oil starts to shimmer. Add the garlic and cook, stirring, until fragrant, 1 to 2 minutes. Add the chopped tomatoes, red chile flakes, Italian seasoning and salt and pepper to taste. Bring to a boil and cook for 5 minutes. Remove from the heat and add the chopped basil.\r\nDrain the pasta and add it to the sauce. Garnish with Parmigiano-Reggiano flakes and more basil and serve warm.",
            "strMealThumb": "https:\/\/www.themealdb.com\/images\/media\/meals\/ustsqw1468250014.jpg",
            "strTags": "Pasta,Curry",
            "strYoutube": "https:\/\/www.youtube.com\/watch?v=1IszT_guI08",
            "strIngredient1": "penne rigate",
            "strIngredient2": "olive oil",
            "strIngredient3": "garlic",
            "strIngredient4": "chopped tomatoes",
            "strIngredient5": "red chilli flakes",
            "strIngredient6": "italian seasoning",
            "strIngredient7": "basil",
            "strIngredient8": "Parmigiano-Reggiano",
            "strIngredient9": "",
            "strIngredient10": "",
            "strIngredient11": "",
            "strIngredient12": "",
            "strIngredient13": "",
            "strIngredient14": "",
            "strIngredient15": "",
            "strIngredient16": None,
            "strIngredient17": None,
            "strIngredient18": None,
            "strIngredient19": None,
            "strIngredient20": None,
            "strMeasure1": "1 pound",
            "strMeasure2": "1\/4 cup",
            "strMeasure3": "3 cloves",
            "strMeasure4": "1 tin ",
            "strMeasure5": "1\/2 teaspoon",
            "strMeasure6": "1\/2 teaspoon",
            "strMeasure7": "6 leaves",
            "strMeasure8": "sprinkling",
            "strMeasure9": "",
            "strMeasure10": "",
            "strMeasure11": "",
            "strMeasure12": "",
            "strMeasure13": "",
            "strMeasure14": "",
            "strMeasure15": "",
            "strMeasure16": None,
            "strMeasure17": None,
            "strMeasure18": None,
            "strMeasure19": None,
            "strMeasure20": None,
            "strSource": None,
            "strImageSource": None,
            "strCreativeCommonsConfirmed": None,
            "dateModified": None
        }

    recipe = Recipe.model_validate(recipe_data)

    substitute = find_substitute(recipe, test_ingredient)
    if substitute:
        logging.info("Substitute recipe found:")
        logging.info(f"Substitute type: {type(substitute)}")
        logging.info(f"A good substitute for {test_ingredient} is: {substitute}")
    else:
        logging.info(f"No substitute found for {test_ingredient}.")
