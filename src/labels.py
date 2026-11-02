from __future__ import annotations

import json
from pathlib import Path

NUM_CLASSES = 37


def load_class_names(path: str | Path) -> list[str]:
    """Load class names and return them in the model's output order."""
    with open(path, "r", encoding="utf-8") as f:
        names = json.load(f)
    if len(names) != NUM_CLASSES:
        raise ValueError(f"Expected {NUM_CLASSES} class names, found {len(names)}.")
    return sorted(names)


def species_of(breed: str) -> str:
    """Oxford-IIIT Pet convention: cat breeds start with an uppercase letter."""
    return "Cat" if breed[0].isupper() else "Dog"


def pretty_name(breed: str) -> str:
    """'american_pit_bull_terrier' -> 'American Pit Bull Terrier'."""
    return breed.replace("_", " ").title()
