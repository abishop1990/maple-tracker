import sqlite3
from typing import Any

from database.types import Entry


def calculate_drink_amount(current_water_weight: int, prev_entry: sqlite3.Row | None, bowl_weight: int) -> int:
    """Calculate how much water was drunk since the previous entry."""
    if prev_entry is None:
        return 0

    prev_water: int = prev_entry["water_weight"]
    if prev_entry["refill_to"]:
        prev_water = prev_entry["refill_to"] - bowl_weight

    return max(0, prev_water - current_water_weight)


def compute_daily_totals(entries: list[Entry] | list[dict[Any, Any]]) -> dict[str, int]:
    """Compute daily drinking totals from entries."""
    daily: dict[str, int] = {}
    for entry in entries:
        date = entry["date"]
        daily[date] = daily.get(date, 0) + (entry.get("drink") or 0)
    return daily


def compute_time_of_day_breakdown(entries: list[Entry] | list[dict[Any, Any]]) -> dict[str, int]:
    """Compute drinking totals by time of day."""
    periods = {"Morning (5-12)": 0, "Afternoon (12-18)": 0, "Evening (18-23)": 0, "Night (23-5)": 0}
    morning_start_hour = 5
    morning_end_hour = 12
    afternoon_end_hour = 18
    evening_end_hour = 23

    for entry in entries:
        try:
            hour = int(entry["time"].split(":")[0])
            drink = entry.get("drink") or 0
            if morning_start_hour <= hour < morning_end_hour:
                periods["Morning (5-12)"] += drink
            elif morning_end_hour <= hour < afternoon_end_hour:
                periods["Afternoon (12-18)"] += drink
            elif afternoon_end_hour <= hour < evening_end_hour:
                periods["Evening (18-23)"] += drink
            else:
                periods["Night (23-5)"] += drink
        except (ValueError, IndexError):
            pass

    return periods


def compute_summary_stats(daily_totals: dict[str, int]) -> dict[str, int | float]:
    """Compute summary statistics from daily totals."""
    daily_values = [v for v in daily_totals.values() if v > 0]
    if not daily_values:
        return {}

    return {
        "average": round(sum(daily_values) / len(daily_values), 1),
        "total_days": len(daily_values),
        "total_intake": sum(daily_values),
        "max_day": max(daily_values),
        "min_day": min(daily_values),
    }
