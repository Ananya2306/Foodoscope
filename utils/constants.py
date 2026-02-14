import os
from dotenv import load_dotenv

load_dotenv()

RECIPEDB_API_KEY = os.getenv("RECIPEDB_API_KEY", "")
RECIPEDB_BASE_URL = os.getenv("RECIPEDB_BASE_URL", "")

FLAVORDB_API_KEY = os.getenv("FLAVORDB_API_KEY", "")
FLAVORDB_BASE_URL = os.getenv("FLAVORDB_BASE_URL", "")