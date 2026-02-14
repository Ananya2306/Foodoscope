import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.recipedb_service import fetch_recipe_by_title, fetch_recipes_by_title
from logic.ingredient_match import detect_missing
from logic.scoring import calculate_confidence
from logic.tradeoff import generate_tradeoff_line
from logic.recipe_search import get_procedure
from services.flavordb_service import fetch_flavor_entity
from utils.validators import validate_recipe_name

router = APIRouter()


class SearchRequest(BaseModel):
    recipe_name: str
    num_recipes: int = 5
    diet_goal: str = "Any"


class DetailRequest(BaseModel):
    recipe_name: str
    checked_ingredients: list = []
    serving_multiplier: float = 1.0


@router.post("/search-recipes")
def search_recipes(req: SearchRequest):
    valid, error = validate_recipe_name(req.recipe_name)
    if not valid:
        raise HTTPException(status_code=400, detail=error)

    recipes = fetch_recipes_by_title(req.recipe_name, limit=req.num_recipes)
    if not recipes:
        return {"recipes": []}

    results = []
    for i, r in enumerate(recipes):
        try:
            calories = int(float(r.get("Calories", 0) or 0))
        except Exception:
            calories = 0

        results.append({
            "name": r.get("Recipe_title", "Unknown"),
            "description": f"A {r.get('Region', 'International')} recipe.",
            "time": f"{r.get('total_time', '?')} min",
            "servings": r.get("servings", 4),
            "difficulty": _get_difficulty(str(r.get("total_time", "30"))),
            "diet": "Balanced",
            "cuisine": r.get("Region", "International"),
            "match_score": max(0, 90 - i * 8),
            "nutrition": {
                "calories": calories,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
            }
        })

    return {"recipes": results}


@router.post("/recipe-detail")
def recipe_detail(req: DetailRequest):
    valid, error = validate_recipe_name(req.recipe_name)
    if not valid:
        raise HTTPException(status_code=400, detail=error)

    recipes = fetch_recipe_by_title(req.recipe_name)
    if not recipes:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe = recipes[0]
    raw_ingredients = recipe.get("ingredients", [])
    checked_set = set(i.lower().strip() for i in req.checked_ingredients)

    ingredients = [
        {
            "name": ing,
            "qty": "as needed",
            "available": ing.lower() in checked_set,
            "role": "Ingredient"
        }
        for ing in raw_ingredients
    ]

    match_data = detect_missing(raw_ingredients, req.checked_ingredients) if raw_ingredients else {
        "missing": [], "matched": [], "match_percent": 0
    }
    confidence = calculate_confidence(match_data["match_percent"], len(match_data["missing"]))
    explanation = generate_tradeoff_line(match_data["match_percent"], len(match_data["missing"]))

    substitutions = []
    for ing in match_data["missing"][:3]:
        entity = fetch_flavor_entity(ing)
        if entity:
            sub_name = entity.get("entity_readable_name", "")
            if sub_name:
                substitutions.append({
                    "original": ing,
                    "substitute": sub_name,
                    "qty": "same amount",
                    "score": 80,
                    "note": "Suggested by FlavorDB based on flavor profile",
                    "role": "Flavor component"
                })

    recipe_id = recipe.get("Recipe_id", "")
    processes = recipe.get("Processes", "")
    procedure = get_procedure(recipe_id, processes)

    try:
        calories = int(float(recipe.get("Calories", 0) or 0))
        protein = round(float(recipe.get("Protein (g)", 0) or 0), 1)
        carbs = round(float(recipe.get("Carbohydrate, by difference (g)", 0) or 0), 1)
        fat = round(float(recipe.get("Total lipid (fat) (g)", 0) or 0), 1)
    except Exception:
        calories = protein = carbs = fat = 0

    return {
        "overview": {
            "name": recipe.get("Recipe_title", req.recipe_name),
            "description": f"A {recipe.get('Region', 'classic')} recipe from {recipe.get('Continent', 'the world')}.",
            "time": f"{recipe.get('total_time', '?')} min",
            "servings": recipe.get("servings", 4),
            "difficulty": _get_difficulty(str(recipe.get("total_time", "30"))),
            "diet": "Balanced",
            "cuisine": recipe.get("Region", "International"),
        },
        "nutrition": {
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
        },
        "ingredients": ingredients,
        "substitutions": substitutions,
        "procedure": procedure,
        "match_score": match_data["match_percent"],
        "confidence": confidence,
        "explanation": explanation,
        "sub_count": len(substitutions)
    }


def _get_difficulty(total_time_str: str) -> str:
    try:
        mins = int(total_time_str)
        if mins <= 20:
            return "Easy"
        if mins <= 45:
            return "Medium"
        return "Hard"
    except Exception:
        return "Medium"