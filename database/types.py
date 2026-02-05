from typing import TypedDict


class Entry(TypedDict, total=False):
    """Represents a water tracking entry from the database."""

    id: int
    date: str
    time: str
    total_weight: int
    water_weight: int
    drink: int
    refill_to: int | None
    notes: str
