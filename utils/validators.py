"""
Input validation helpers.
"""


def validate_recipe_name(name: str) -> tuple:
    """
    Returns (is_valid, error_message).
    """
    if not name or not name.strip():
        return False, "Recipe name cannot be empty."
    if len(name.strip()) < 2:
        return False, "Recipe name is too short."
    if len(name.strip()) > 100:
        return False, "Recipe name is too long."
    return True, ""


def validate_ingredients(ingredients: list) -> tuple:
    """
    Returns (is_valid, error_message).
    """
    if not ingredients:
        return False, "Ingredient list cannot be empty."
    if len(ingredients) > 50:
        return False, "Too many ingredients provided (max 50)."
    return True, ""


def validate_serving_multiplier(multiplier: float) -> tuple:
    """
    Returns (is_valid, error_message).
    """
    if multiplier not in [0.5, 1.0, 2.0, 3.0]:
        return False, "Serving multiplier must be 0.5, 1, 2, or 3."
    return True, ""