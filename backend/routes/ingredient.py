#Ingredient search endpoint
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.recipedb_service import fetch_recipes_by_title
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

            try:
                calories = int(float(r.get("Calories", 0) or 0))
            except Exception:
                calories = 0

            results.append({
                "name": name,
                "match_score": 70,
                "matched": req.ingredients,
                "missing": [],
                "nutrition": {
                    "calories": calories,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                },
                "diet": "Balanced",
                "time": f"{r.get('total_time', '?')} min"
            })

    return {"recipes": results[:5]}
