#Main orchestration
from services.recipedb_service import fetch_recipe_by_title, fetch_recipe_instructions
from services.flavordb_service import fetch_flavor_entity
from logic.ingredient_match import detect_missing
from logic.scoring import calculate_confidence
from logic.tradeoff import generate_tradeoff_line


def analyze_recipe(recipe_name: str, user_ingredients: list):

    recipes = fetch_recipe_by_title(recipe_name)

    if not recipes:
        return None

    recipe = recipes[0]

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
            "recipe_id": recipe.get("Recipe_id", ""),
            "match_percent": 0,
            "confidence": 0,
            "missing": [],
            "matched": [],
            "substitutions": {},
            "explanation": "Recipe found but ingredient list unavailable from API."
        }

    match_data = detect_missing(recipe_ingredients, user_ingredients)

    substitutions = {}
    # Limit FlavorDB calls to 3 to protect rate limit
    for ingredient in match_data["missing"][:3]:
        entity = fetch_flavor_entity(ingredient)
        if entity:
            substitutions[ingredient] = entity.get(
                "entity_readable_name", "No substitute found"
            )
        else:
            substitutions[ingredient] = "No substitute found"

    # Mark remaining missing as no substitute (without API call)
    for ingredient in match_data["missing"][3:]:
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
        "recipe_id": recipe.get("Recipe_id", ""),
        "match_percent": match_data["match_percent"],
        "confidence": confidence,
        "missing": match_data["missing"],
        "matched": match_data["matched"],
        "substitutions": substitutions,
        "explanation": explanation
    }


def get_procedure(recipe_id: str, processes_str: str):
    """
    Gets step-by-step procedure.
    Tries real instructions endpoint first, falls back to processes field.
    """
    # Try real instructions first
    steps = fetch_recipe_instructions(recipe_id)
    if steps:
        return [
            {
                "title": f"Step {i + 1}",
                "instruction": step,
                "tip": ""
            }
            for i, step in enumerate(steps)
        ]

    # Fall back to processes field
    if processes_str:
        procedure = []
        for step in processes_str.split("||")[:8]:
            step = step.strip()
            if step:
                procedure.append({
                    "title": step.capitalize(),
                    "instruction": f"{step.capitalize()} the ingredients carefully.",
                    "tip": ""
                })
        if procedure:
            return procedure

    return [
        {"title": "Prepare Ingredients", "instruction": "Gather and prepare all ingredients.", "tip": "Read the full recipe before starting."},
        {"title": "Cook", "instruction": "Follow the standard cooking method.", "tip": "Taste as you go."},
        {"title": "Serve", "instruction": "Plate and serve hot.", "tip": "Garnish for presentation."}
    ]
