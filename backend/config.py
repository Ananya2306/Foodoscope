"""
Central app configuration.
Loaded by backend/main.py at startup.
"""

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "")
RECIPE_BASE_URL = os.getenv("RECIPE_BASE_URL", "")
FLAVOR_BASE_URL = os.getenv("FLAVOR_BASE_URL", "")

APP_HOST = "0.0.0.0"
APP_PORT = 8000
APP_RELOAD = True