import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "")
RECIPE_BASE_URL = os.getenv("RECIPE_BASE_URL", "")
FLAVOR_BASE_URL = os.getenv("FLAVOR_BASE_URL", "")