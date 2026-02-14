"""
Data model for a recipe object.
Used for type hints and validation across the project.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Recipe:
    recipe_id: str
    title: str
    calories: float
    cook_time: str
    prep_time: str
    total_time: str
    servings: str
    region: str
    continent: str
    ingredients: List[str] = field(default_factory=list)
    processes: str = ""
    vegan: str = "0.0"

    @staticmethod
    def from_api(data: dict) -> "Recipe":
        return Recipe(
            recipe_id=data.get("Recipe_id", ""),
            title=data.get("Recipe_title", ""),
            calories=float(data.get("Calories", 0) or 0),
            cook_time=data.get("cook_time", "0"),
            prep_time=data.get("prep_time", "0"),
            total_time=data.get("total_time", "0"),
            servings=data.get("servings", "4"),
            region=data.get("Region", ""),
            continent=data.get("Continent", ""),
            ingredients=data.get("ingredients", []),
            processes=data.get("Processes", ""),
            vegan=data.get("vegan", "0.0"),
        )