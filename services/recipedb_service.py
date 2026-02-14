import requests

BASE = "https://api.foodoscope.com/recipe2-api"


def _get_headers():
    from utils.constants import API_KEY
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


def fetch_recipe_by_title(title: str):
    try:
        # Step 1 — search by title to get recipe + ID
        r1 = requests.get(
            f"{BASE}/recipe-bytitle/recipeByTitle",
            headers=_get_headers(),
            params={"title": title},
            timeout=8
        )

        if r1.status_code != 200:
            return []

        data = r1.json()
        if not data.get("success") or not data.get("data"):
            return []

        recipe_basic = data["data"][0]
        recipe_id = recipe_basic.get("Recipe_id")

        if not recipe_id:
            return [recipe_basic]

        # Step 2 — fetch full details using the ID
        r2 = requests.get(
            f"{BASE}/search-recipe/{recipe_id}",
            headers=_get_headers(),
            timeout=8
        )

        if r2.status_code != 200:
            return [recipe_basic]

        full_data = r2.json()

        # Extract recipe info and ingredients
        recipe_full = full_data.get("recipe", {})
        ingredients_raw = full_data.get("ingredients", [])

        # Pull just the ingredient names into a clean list
        ingredient_names = [
            ing["ingredient"]
            for ing in ingredients_raw
            if ing.get("ingredient")
        ]

        # Merge everything together
        merged = {
            **recipe_basic,
            **recipe_full,
            "ingredients": ingredient_names
        }

        return [merged]

    except Exception:
        return []