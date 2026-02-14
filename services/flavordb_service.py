import requests
from utils.constants import FLAVORDB_API_KEY, FLAVORDB_BASE_URL


def fetch_flavor_entity(name: str):

    # Try full name first, then first word only
    attempts = [name, name.split()[0]]

    for attempt in attempts:
        url = f"{FLAVORDB_BASE_URL}/entities/by-readable-name"

        headers = {
            "Authorization": f"Bearer {FLAVORDB_API_KEY}",
            "Content-Type": "application/json"
        }

        params = {"readable_name": attempt}

        try:
            response = requests.get(
                url, headers=headers, params=params, timeout=10
            )

            if response.status_code != 200:
                continue

            data = response.json()

            if data.get("success") and data["data"]:
                return data["data"][0]

        except Exception:
            continue

    return None