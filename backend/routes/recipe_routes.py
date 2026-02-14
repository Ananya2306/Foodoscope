"""
Recipe-related routes.
Registered in backend/main.py.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from services.recipedb_service import fetch_recipe_by_title, fetch_recipes_by_title
from logic.ingredient_match import detect_missing
from logic.scoring import calculate_confidence
from logic.tradeoff import generate_tradeoff_line
from services.flavordb_service import fetch_flavor_entity

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
            "description": f"A {r.get('Region', '')} recipe from {r.get('Continent', '')}.",
            "time": f"{r.get('total_time', '?')} min",
            "servings": r.get("servings", 4),
            "difficulty": "Medium",
            "diet": "Vegan" if str(r.get("vegan", "0")) == "1.0" else "Balanced",
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
    recipes = fetch_recipe_by_title(req.recipe_name)
    if not recipes:
        return {"error": "Recipe not found"}

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

    substitutions = []
    for ing in match_data["missing"][:5]:
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

    processes = recipe.get("Processes", "")
    procedure = []
    if processes:
        for step in processes.split("||")[:8]:
            step = step.strip()
            if step:
                procedure.append({
                    "title": step.capitalize(),
                    "instruction": f"{step.capitalize()} the ingredients carefully.",
                    "tip": ""
                })

    if not procedure:
        procedure = [
            {"title": "Prepare Ingredients", "instruction": "Gather and prepare all ingredients.", "tip": ""},
            {"title": "Cook", "instruction": f"Cook {req.recipe_name} as per standard method.", "tip": "Taste as you go."},
            {"title": "Serve", "instruction": "Plate and serve hot.", "tip": ""}
        ]

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
            "difficulty": "Medium",
            "diet": "Vegan" if str(recipe.get("vegan", "0")) == "1.0" else "Balanced",
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
        "sub_count": len(substitutions)
    }