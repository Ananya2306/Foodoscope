# AlgoMinds ACDSS
**Smart Recipe Decision Support System**

A recipe analyzer that helps you decide what to cook based on the
ingredients you have. Built with Python + FastAPI backend and a
custom HTML/CSS/JS frontend.

---

## Features
- Search recipes by name
- Get ingredient match percentage
- See missing ingredients and suggested substitutes
- Step-by-step cooking procedure
- Nutrition info per serving
- Ingredient search — find recipes from what you have

---

## Project Structure
```
Foodoscope/
├── app.py                  # Streamlit interface (simple version)
├── run.py                  # FastAPI server entry point
├── backend/
│   ├── main.py             # FastAPI app + all endpoints
│   ├── config.py           # App configuration
│   └── routes/
│       ├── recipe_routes.py
│       └── ingredient.py
├── frontend/
│   └── index.html          # Full HTML/CSS/JS frontend
├── logic/
│   ├── recipe_search.py    # Core orchestrator
│   ├── ingredient_match.py # Missing ingredient detection
│   ├── scoring.py          # Confidence score calculator
│   └── tradeoff.py         # Match quality explanation
├── services/
│   ├── recipedb_service.py # Foodoscope RecipeDB API
│   └── flavordb_service.py # Foodoscope FlavorDB API
├── models/
│   ├── recipe_model.py     # Recipe dataclass
│   └── substitution_model.py
└── utils/
    ├── constants.py        # Loads .env variables
    ├── helpers.py          # normalize, split_ingredients
    └── validators.py       # Input validation
```

---

## Setup
```bash
# 1. Clone the repo
git clone <your-repo-url>
cd Foodoscope-main

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
# Add these lines:
# API_KEY=your_key_here
# RECIPE_BASE_URL=https://api.foodoscope.com/recipe2-api/recipe-bytitle
# FLAVOR_BASE_URL=https://api.foodoscope.com/flavordb
```

---

## Running

**HTML Frontend (recommended):**
```bash
python run.py
# Open http://localhost:8000
```

**Streamlit (simple version):**
```bash
streamlit run app.py
```

---

## Team
AlgoMinds — ACDSS Project