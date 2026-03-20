from pydantic import BaseModel
from data_models.recipe import Ingredient


class Meal(BaseModel):
    strMeal: str
    strCategory: str | None = None
    strArea: str | None = None
    strInstructions: str | None = None
    ingredients: list[Ingredient] = []
    vitamines: list[str] = []
