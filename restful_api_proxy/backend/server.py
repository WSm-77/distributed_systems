from fastapi import Body, FastAPI, status
from fastapi.responses import JSONResponse
from services.recipe_service import get_recipe

server = FastAPI()

@server.get("/v1/recipe")
async def get_recipe_api(diet_preferences: str = ""):
    try:
        recipe = get_recipe(diet_preferences)
        return JSONResponse(content=recipe.model_dump(), status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

