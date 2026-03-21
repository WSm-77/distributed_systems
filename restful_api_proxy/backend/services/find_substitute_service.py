import json, logging, requests
from data_models.recipe import Recipe
from config.config import CONFIG
from data_models.ollama import OllamaResponse

recipe_model_schema = Recipe.model_json_schema()
recipe_field_names = list(
    filter(
        lambda x:
        "strIngredient" in x or "strMeasure" in x or "strInstructions" == x,
        Recipe.model_fields.keys()
    )
)

def find_substitute(recipe: Recipe, ingredients: list[str]) -> Recipe | None:
    ingredients_str = ", ".join(ingredients)

    logging.info("Finding substitute for ingredients: %s in recipe: %s", ingredients_str, recipe.strMeal)

    payload = {
        "model": CONFIG.model,
        "messages": [
            {"role": "system", "content": CONFIG.system_prompt},
            {"role": "user", "content": f"Modify following recipe by replacing {ingredients_str} with a suitable substitute: {recipe.model_dump_json()}"}
        ],
        "stream": False,
        "format": {
            "type": "object",
            "properties": recipe_model_schema.get("properties", {}),
            "required": recipe_field_names
        }
    }

    try:
        response = requests.post(CONFIG.ollama_api, data=json.dumps(payload), headers=CONFIG.headers, timeout=120)

        logging.debug("Ollama API response status: %d", response.status_code)
        logging.debug("Ollama API response: %s", response.text)
        logging.debug("Ollama API request payload: %s", json.dumps(payload))
        logging.debug("Ollama API response: %s", response)
        logging.debug("Ollama API response text: %s", response.text)

        response.raise_for_status()
        raw_data = response.json()

        logging.debug("Raw response from Ollama: %s", raw_data)

        ollama_response = OllamaResponse.model_validate(raw_data)

        message = ollama_response.message

        logging.debug("Message from Ollama: %s", message)

        content_raw = message.content.strip()
        content: dict = json.loads(content_raw)

        logging.debug("Content from Ollama: %s", content)

        merged_recipe = recipe.model_dump()
        merged_recipe.update(content)
        modified_recipe_validated = Recipe.model_validate(merged_recipe)

        logging.info("Substitute recipe generated for ingredients: %s", ingredients_str)

        return modified_recipe_validated
    except Exception:
        logging.exception("Error while finding substitute for ingredients: %s", ingredients_str)
        return None
