from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.recipe_search import analyze_recipe
from services.recipedb_service import fetch_recipe_by_title
from utils.helpers import split_ingredients

app = FastAPI()

# Allow the HTML frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend HTML file
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")


# ── Request Models ─────────────────────────────────────────────
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


# ── Endpoint 1: Search Recipes ─────────────────────────────────
@app.post("/api/search-recipes")
def search_recipes(req: SearchRequest):
    recipes = fetch_recipe_by_title(req.recipe_name)

    if not recipes:
        return {"recipes": []}

    results = []
    for i, r in enumerate(recipes[:req.num_recipes]):
        results.append({
            "name": r.get("Recipe_title", "Unknown"),
            "description": f"A {r.get('Region', '')} recipe from {r.get('Continent', '')}.",
            "time": f"{r.get('total_time', '?')} min",
            "servings": r.get("servings", 4),
            "difficulty": "Medium",
            "diet": "Vegan" if r.get("vegan") == "1.0" else "Balanced",
            "cuisine": r.get("Region", "International"),
            "match_score": max(0, 90 - i * 8),
            "nutrition": {
                "calories": int(float(r.get("Calories", 0) or 0)),
                "protein": round(float(r.get("Protein (g)", 0) or 0), 1),
                "carbs": round(float(r.get("Carbohydrate, by difference (g)", 0) or 0), 1),
                "fat": round(float(r.get("Total lipid (fat) (g)", 0) or 0), 1),
            }
        })

    return {"recipes": results}


# ── Endpoint 2: Recipe Detail ──────────────────────────────────
@app.post("/api/recipe-detail")
def recipe_detail(req: DetailRequest):
    result = analyze_recipe(req.recipe_name, req.checked_ingredients)

    if not result:
        return _fallback_detail(req.recipe_name)

    recipes = fetch_recipe_by_title(req.recipe_name)
    recipe = recipes[0] if recipes else {}

    # Build ingredients list
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

    # Build substitutions
    substitutions = []
    for ing, sub in result.get("substitutions", {}).items():
        if sub != "No substitute found":
            substitutions.append({
                "original": ing,
                "substitute": sub,
                "qty": "same amount",
                "score": 80,
                "note": "Suggested by FlavorDB based on flavor profile",
                "role": "Flavor component"
            })

    # Build procedure from utensils/processes if available
    processes = recipe.get("Processes", "").split("||") if recipe.get("Processes") else []
    procedure = []
    for i, step in enumerate(processes[:8]):
        if step.strip():
            procedure.append({
                "title": step.strip().capitalize(),
                "instruction": f"{step.strip().capitalize()} the ingredients as needed for this recipe.",
                "tip": ""
            })

    if not procedure:
        procedure = [
            {"title": "Prepare Ingredients", "instruction": "Gather and prepare all ingredients.", "tip": "Read the full recipe before starting."},
            {"title": "Cook", "instruction": f"Follow the standard method for {req.recipe_name}.", "tip": "Taste as you go."},
            {"title": "Serve", "instruction": "Plate and serve hot.", "tip": "Garnish for presentation."}
        ]

    calories = int(float(recipe.get("Calories", 0) or 0))

    return {
        "overview": {
            "name": result["recipe_title"],
            "description": f"A {recipe.get('Region', 'classic')} recipe.",
            "time": f"{recipe.get('total_time', '?')} min",
            "servings": recipe.get("servings", 4),
            "difficulty": "Medium",
            "diet": "Vegan" if recipe.get("vegan") == "1.0" else "Balanced",
            "cuisine": recipe.get("Region", "International"),
        },
        "nutrition": {
            "calories": calories,
            "protein": round(float(recipe.get("Protein (g)", 0) or 0), 1),
            "carbs": round(float(recipe.get("Carbohydrate, by difference (g)", 0) or 0), 1),
            "fat": round(float(recipe.get("Total lipid (fat) (g)", 0) or 0), 1),
        },
        "ingredients": ingredients,
        "substitutions": substitutions,
        "procedure": procedure,
        "match_score": result["match_percent"],
        "sub_count": len(substitutions)
    }


# ── Endpoint 3: Find by Ingredients ───────────────────────────
@app.post("/api/find-by-ingredients")
def find_by_ingredients(req: IngredientRequest):
    results = []

    for ing in req.ingredients[:3]:
        recipes = fetch_recipe_by_title(ing)
        for r in recipes[:2]:
            recipe_ings = r.get("ingredients", [])
            user_set = set(i.lower().strip() for i in req.ingredients)
            recipe_set = set(i.lower().strip() for i in recipe_ings)

            matched = list(recipe_set & user_set)
            missing = list(recipe_set - user_set)
            score = round((len(matched) / len(recipe_set)) * 100, 1) if recipe_set else 0

            if score >= req.min_match:
                results.append({
                    "name": r.get("Recipe_title", "Unknown"),
                    "match_score": score,
                    "matched": matched,
                    "missing": missing[:5],
                    "nutrition": {
                        "calories": int(float(r.get("Calories", 0) or 0)),
                        "protein": round(float(r.get("Protein (g)", 0) or 0), 1),
                        "carbs": 0,
                        "fat": 0,
                    },
                    "diet": "Balanced",
                    "time": f"{r.get('total_time', '?')} min"
                })

    results.sort(key=lambda x: x["match_score"], reverse=True)
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