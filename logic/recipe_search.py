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

    # Get real ingredients from the API response
    recipe_ingredients = (
        recipe.get("ingredients") or
        recipe.get("Ingredients") or
        recipe.get("ingredient_list") or
        recipe.get("Ingredient_list") or
        []
    )

    if not recipe_ingredients:
        return {
            "recipe_title": recipe.get("Recipe_title", recipe_name),
            "match_percent": 0,
            "confidence": 0,
            "missing": [],
            "substitutions": {},
            "explanation": "Recipe found but ingredient list unavailable from API."
        }

    match_data = detect_missing(recipe_ingredients, user_ingredients)

    substitutions = {}
    for ingredient in match_data["missing"]:
        entity = fetch_flavor_entity(ingredient)
        if entity:
            substitutions[ingredient] = entity.get(
                "entity_readable_name", "No substitute found"
            )
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
        "recipe_title": recipe.get("Recipe_title", recipe_name),
        "match_percent": match_data["match_percent"],
        "confidence": confidence,
        "missing": match_data["missing"],
        "substitutions": substitutions,
        "explanation": explanation
    }