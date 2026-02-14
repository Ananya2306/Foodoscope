"""
Data model for an ingredient substitution.
"""

from dataclasses import dataclass


@dataclass
class Substitution:
    original: str
    substitute: str
    role: str
    confidence: int

    @staticmethod
    def from_flavor_entity(ingredient_name: str, entity: dict) -> "Substitution":
        return Substitution(
            original=ingredient_name,
            substitute=entity.get("entity_readable_name", "Unknown"),
            role=entity.get("entity_category", "Flavor component"),
            confidence=85,
        )

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "substitute": self.substitute,
            "role": self.role,
            "confidence": self.confidence,
        }