# logic/substitution_engine.py

import requests

# FlavorDB base URL
FLAVOR_BASE_URL = "https://api.foodoscope.com/flavordb"

# Your API key (WITHOUT Bearer here)
API_KEY = "xPtdt8S0PblDqUJgxsi_So76_i2-LyTwG4XM8mSUROjFIx88"


def get_substitute_for_ingredient(ingredient_name):
    """
    Calls FlavorDB to find substitute for one ingredient
    """

    url = f"{FLAVOR_BASE_URL}/entities/by-readable-name"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    params = {
        "readable_name": ingredient_name
    }

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print("FlavorDB error:", response.text)
            return None

        data = response.json()

        if not data.get("data"):
            return None

        entity = data["data"][0]

        substitute = {
            "original": ingredient_name,
            "substitute": entity.get("entity_alias_readable", "No substitute found"),
            "role": entity.get("entity_category", "Flavor enhancer"),
            "confidence": 85
        }

        return substitute

    except Exception as e:
        print("Substitution error:", str(e))
        return None


def get_substitutions_for_missing(missing_ingredients):
    """
    Gets substitutes for all missing ingredients
    """

    results = []

    for ingredient in missing_ingredients:
        substitute = get_substitute_for_ingredient(ingredient)

        if substitute:
            results.append(substitute)
        else:
            results.append({
                "original": ingredient,
                "substitute": "No substitute found",
                "role": "Unknown",
                "confidence": 0
            })

    return results
