from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.recipe_search import analyze_recipe
from services.recipedb_service import fetch_recipe_by_title, fetch_recipes_by_title

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")


class SearchRequest(BaseModel):
    recipe_name: str
    num_recipes: int = 5
    diet_goal: str = "Any"


class DetailRequest(BaseModel):
    recipe_name: str
    checked_ingredients: list = []
    serving_multiplier: float = 1.0


class IngredientRequest(BaseModel):
    ingredients: list
    diet_goal: str = "Any"
    min_match: int = 50


@app.post("/api/search-recipes")
def search_recipes(req: SearchRequest):
    # Use basic search — doesn't fetch full details, saves rate limit
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


@app.post("/api/recipe-detail")
def recipe_detail(req: DetailRequest):
    # Single call — fetch_recipe_by_title already gets full details + ingredients
    recipes = fetch_recipe_by_title(req.recipe_name)

    if not recipes:
        return _fallback_detail(req.recipe_name)

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

    # Run scoring logic on checked ingredients
    from logic.ingredient_match import detect_missing
    from logic.scoring import calculate_confidence

    match_data = detect_missing(raw_ingredients, req.checked_ingredients) if raw_ingredients else {"missing": [], "matched": [], "match_percent": 0}
    confidence = calculate_confidence(match_data["match_percent"], len(match_data["missing"]))

    # Get substitutions for missing ingredients
    from services.flavordb_service import fetch_flavor_entity
    substitutions = []
    for ing in match_data["missing"][:5]:  # limit to 5 to save rate limit
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

    # Build procedure from processes field
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
            {"title": "Prepare Ingredients", "instruction": "Gather and prepare all ingredients.", "tip": "Read the full recipe before starting."},
            {"title": "Cook", "instruction": f"Follow the standard method for {req.recipe_name}.", "tip": "Taste as you go."},
            {"title": "Serve", "instruction": "Plate and serve hot.", "tip": "Garnish for presentation."}
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


@app.post("/api/find-by-ingredients")
def find_by_ingredients(req: IngredientRequest):
    results = []
    seen = set()

    for ing in req.ingredients[:2]:  # limit to 2 searches to save rate limit
        recipes = fetch_recipes_by_title(ing, limit=3)
        for r in recipes:
            name = r.get("Recipe_title", "")
            if name in seen:
                continue
            seen.add(name)

            # We don't have ingredients at this level — show partial match
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


def _fallback_detail(name):
    return {
        "overview": {"name": name, "description": f"Recipe for {name}.", "time": "30 min", "servings": 4, "difficulty": "Medium", "diet": "Balanced", "cuisine": "International"},
        "nutrition": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
        "ingredients": [],
        "substitutions": [],
        "procedure": [{"title": "Cook", "instruction": f"Prepare {name} as usual.", "tip": ""}],
        "match_score": 0,
        "sub_count": 0
    }