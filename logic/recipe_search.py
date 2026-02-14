from services.recipedb_service import fetch_recipe_by_title
from services.flavordb_service import fetch_flavor_entity
from logic.ingredient_match import detect_missing
from logic.scoring import calculate_confidence
from logic.tradeoff import generate_tradeoff_line


def analyze_recipe(recipe_name: str, user_ingredients: list):

    recipes = fetch_recipe_by_title(recipe_name)

    if not recipes:
        return None

    recipe = recipes[0]

    # ⚠️ Replace with real ingredient API when available
    recipe_ingredients = [
        "chicken", "onion", "garlic",
        "salt", "pepper", "oil"
    ]

    match_data = detect_missing(
        recipe_ingredients,
        user_ingredients
    )

    substitutions = {}

    for ingredient in match_data["missing"]:
        entity = fetch_flavor_entity(ingredient)

        if entity:
            substitutions[ingredient] = entity.get("entity_readable_name")
        else:
            substitutions[ingredient] = "No substitute found"

    confidence = calculate_confidence(
        match_data["match_percent"],
        len(match_data["missing"])
    )

    explanation = generate_tradeoff_line(
        match_data["match_percent"],
        len(match_data["missing"])
    )

    return {
        "recipe_title": recipe["Recipe_title"],
        "match_percent": match_data["match_percent"],
        "confidence": confidence,
        "missing": match_data["missing"],
        "substitutions": substitutions,
        "explanation": explanation
    }
