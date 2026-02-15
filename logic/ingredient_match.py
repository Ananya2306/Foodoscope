# Match % calculator
from utils.helpers import normalize


def detect_missing(recipe_ingredients, user_ingredients):

    recipe_set = set(normalize(i) for i in recipe_ingredients)
    user_set = set(normalize(i) for i in user_ingredients)

    missing = recipe_set - user_set
    matched = recipe_set & user_set

    match_percent = (
        (len(matched) / len(recipe_set)) * 100
        if recipe_set else 0
    )

    return {
        "missing": list(missing),
        "matched": list(matched),
        "match_percent": round(match_percent, 2)
    }
