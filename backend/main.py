import sys
import os

# MUST be first — before any local imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.routes.recipe_routes import router as recipe_router
from backend.routes.ingredient import router as ingredient_router

app = FastAPI(
    title="AlgoMinds ACDSS API",
    description="Smart Recipe Decision Support System",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(recipe_router, prefix="/api")
app.include_router(ingredient_router, prefix="/api")


@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0"}