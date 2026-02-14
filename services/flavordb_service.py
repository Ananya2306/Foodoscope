import requests
from utils.constants import API_KEY, FLAVOR_BASE_URL


def fetch_flavor_entity(name: str):

    url = f"{FLAVOR_BASE_URL}/entities/by-readable-name"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    params = {"readable_name": name}

    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("success") and data["data"]:
            return data["data"][0]

        return None

    except Exception:
        return None