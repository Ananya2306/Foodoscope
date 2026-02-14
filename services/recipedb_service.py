import requests
from utils.constants import API_KEY, RECIPE_BASE_URL


def fetch_recipe_by_title(title: str):

    url = f"{RECIPE_BASE_URL}/recipeByTitle"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    params = {"title": title}

    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=8
        )

        if response.status_code != 200:
            return []

        data = response.json()

        if not data.get("success"):
            return []

        return data["data"]

    except Exception:
        return []