from datetime import datetime
from typing import TypedDict

from database.compute_stats import compute_daily_totals, compute_time_of_day_breakdown, compute_summary_stats


class DailyTotal(TypedDict):
    date: str
    total: int
    sort_key: str


class StatsResponse(TypedDict):
    daily: list[DailyTotal]
    periods: dict[str, int]
    summary: dict


def compute_stats(entries: list[dict]) -> StatsResponse:
    """
    Compute all statistics from entries.

    :param entries: List of entry dictionaries
    :return: StatsResponse with daily totals, period breakdown, and summary
    """
    if not entries:
        return {"daily": [], "periods": {}, "summary": {}}

    daily_totals = compute_daily_totals(entries)
    daily_list = _format_daily_totals(daily_totals)
    periods = compute_time_of_day_breakdown(entries)
    summary = compute_summary_stats(daily_totals)

    return {
        "daily": daily_list,
        "periods": periods,
        "summary": summary,
    }


def _format_daily_totals(daily_totals: dict[str, int]) -> list[DailyTotal]:
    """Format daily totals with sortable keys."""
    daily_list = []

    for date, total in daily_totals.items():
        sort_key = _parse_date_for_sorting(date)
        daily_list.append({"date": date, "total": total, "sort_key": sort_key})

    daily_list.sort(key=lambda x: x["sort_key"])
    return daily_list


def _parse_date_for_sorting(date_str: str) -> str:
    """Parse date string to ISO format for sorting."""
    formats = ["%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d"]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).isoformat()
        except ValueError:
            continue

    return date_str
