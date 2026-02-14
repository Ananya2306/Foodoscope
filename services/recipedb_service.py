import requests
import time

BASE = "http://cosylab.iiitd.edu.in:6969/recipe2-api"


def _get_headers():
    from utils.constants import API_KEY
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


def fetch_recipes_by_title(title: str, limit: int = 5):
    """Returns basic info for multiple recipes — used for search listing."""
    try:
        r = requests.get(
            f"{BASE}/recipe-bytitle/recipeByTitle",
            headers=_get_headers(),
            params={"title": title},
            timeout=8
        )
        if r.status_code != 200:
            return []
        data = r.json()
        if not data.get("success") or not data.get("data"):
            return []
        return data["data"][:limit]
    except Exception:
        return []


def fetch_recipe_by_title(title: str):
    """Returns one recipe with full ingredients — used for detail view."""
    try:
        recipes = fetch_recipes_by_title(title, limit=1)
        if not recipes:
            return []

        recipe_basic = recipes[0]
        recipe_id = recipe_basic.get("Recipe_id")

        if not recipe_id:
            return [recipe_basic]

        time.sleep(0.5)

        r2 = requests.get(
            f"{BASE}/search-recipe/{recipe_id}",
            headers=_get_headers(),
            timeout=8
        )

        if r2.status_code != 200:
            return [recipe_basic]

        full_data = r2.json()
        recipe_full = full_data.get("recipe", {})
        ingredients_raw = full_data.get("ingredients", [])

        ingredient_names = [
            ing["ingredient"]
            for ing in ingredients_raw
            if ing.get("ingredient")
        ]

        merged = {
            **recipe_basic,
            **recipe_full,
            "ingredients": ingredient_names
        }

        return [merged]

    except Exception:
        return []


def fetch_recipe_instructions(recipe_id: str):
    """Returns step-by-step instructions for a recipe using its ID."""
    try:
        r = requests.get(
            f"{BASE}/instructions/{recipe_id}",
            headers=_get_headers(),
            timeout=8
        )
        if r.status_code != 200:
            return []
        data = r.json()
        return data.get("steps", [])
    except Exception:
        return []