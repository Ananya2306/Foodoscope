import requests

API_KEY = "xPtdt8S0PblDqUJgxsi_So76_i2-LyTwG4XM8mSUROjFIx88"

BASE_URL = "https://api.foodoscope.com/recipe2-api/recipe-bytitle"


def search_recipe_by_title(title):
    url = f"{BASE_URL}/recipeByTitle"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    params = {
        "title": title
    }

    response = requests.get(url, headers=headers, params=params)

    print("Request URL:", response.url)
    print("Status:", response.status_code)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.text)
        return None
