from typing import List
from pydantic import BaseModel

class Ingredient(BaseModel):
    name: str
    measure: str

class Recipe(BaseModel):
    idMeal: str
    strMeal: str
    strMealAlternate: str | None = None
    strCategory: str | None = None
    strArea: str | None = None
    strInstructions: str | None = None
    strMealThumb: str | None = None
    strTags: str | None = None
    strYoutube: str | None = None
    strIngredient1: str | None = None
    strIngredient2: str | None = None
    strIngredient3: str | None = None
    strIngredient4: str | None = None
    strIngredient5: str | None = None
    strIngredient6: str | None = None
    strIngredient7: str | None = None
    strIngredient8: str | None = None
    strIngredient9: str | None = None
    strIngredient10: str | None = None
    strIngredient11: str | None = None
    strIngredient12: str | None = None
    strIngredient13: str | None = None
    strIngredient14: str | None = None
    strIngredient15: str | None = None
    strIngredient16: str | None = None
    strIngredient17: str | None = None
    strIngredient18: str | None = None
    strIngredient19: str | None = None
    strIngredient20: str | None = None
    strMeasure1: str | None = None
    strMeasure2: str | None = None
    strMeasure3: str | None = None
    strMeasure4: str | None = None
    strMeasure5: str | None = None
    strMeasure6: str | None = None
    strMeasure7: str | None = None
    strMeasure8: str | None = None
    strMeasure9: str | None = None
    strMeasure10: str | None = None
    strMeasure11: str | None = None
    strMeasure12: str | None = None
    strMeasure13: str | None = None
    strMeasure14: str | None = None
    strMeasure15: str | None = None
    strMeasure16: str | None = None
    strMeasure17: str | None = None
    strMeasure18: str | None = None
    strMeasure19: str | None = None
    strMeasure20: str | None = None
    strSource: str | None = None
    strImageSource: str | None = None
    strCreativeCommonsConfirmed: str | None = None
    dateModified: str | None = None

    def get_ingredients(self) -> List[Ingredient]:
        ingredients = []
        for i in range(1, 21):
            ingredient: str | None = getattr(self, f'strIngredient{i}')
            measure: str | None = getattr(self, f'strMeasure{i}')
            if ingredient and ingredient.strip():
                ingredients.append(Ingredient(name=ingredient.strip(), measure=measure.strip() if measure else "1"))
        return ingredients

class RecipeResponse(BaseModel):
	meals: list[Recipe]

