"""
Ingredient search routes.
Registered in backend/main.py via app.include_router()
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.recipedb_service import fetch_recipe_by_title, fetch_recipes_by_title
from logic.ingredient_match import detect_missing
from utils.validators import validate_ingredients

router = APIRouter()


class IngredientRequest(BaseModel):
    ingredients: list
    diet_goal: str = "Any"
    min_match: int = 50


@router.post("/find-by-ingredients")
def find_by_ingredients(req: IngredientRequest):

    valid, error = validate_ingredients(req.ingredients)
    if not valid:
        raise HTTPException(status_code=400, detail=error)

    results = []
    seen = set()

    for ing in req.ingredients[:2]:
        recipes = fetch_recipes_by_title(ing, limit=3)

        for r in recipes:
            name = r.get("Recipe_title", "")
            if name in seen:
                continue
            seen.add(name)

            # Fetch full recipe to get real ingredients for matching
            full = fetch_recipe_by_title(name)
            if not full:
                continue

            recipe_ingredients = full[0].get("ingredients", [])
            if not recipe_ingredients:
                continue

            match_data = detect_missing(recipe_ingredients, req.ingredients)

            if match_data["match_percent"] < req.min_match:
                continue

            try:
                calories = int(float(r.get("Calories", 0) or 0))
                protein = round(float(r.get("Protein (g)", 0) or 0), 1)
            except Exception:
                calories = protein = 0

            is_vegan = str(r.get("vegan", "0")) == "1.0"
            diet_tag = "Vegan" if is_vegan else "Balanced"

            results.append({
                "name": name,
                "match_score": match_data["match_percent"],
                "matched": match_data["matched"],
                "missing": match_data["missing"][:5],
                "nutrition": {
                    "calories": calories,
                    "protein": protein,
                    "carbs": 0,
                    "fat": 0,
                },
                "diet": diet_tag,
                "time": f"{r.get('total_time', '?')} min"
            })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return {"recipes": results[:5]}