import io
from datetime import datetime
from typing import Any

import pandas as pd
from database.compute_stats import compute_daily_totals


def generate_csv_export(entries: list[dict[str, Any]]) -> io.BytesIO:
    """
    Generate CSV export from entries.

    :param entries:  List of entry dictionaries
    :return:  BytesIO buffer containing CSV data
    """
    df = pd.DataFrame(entries)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    bytes_output = io.BytesIO(output.getvalue().encode())
    bytes_output.seek(0)
    return bytes_output


def generate_vet_report(entries: list[dict[str, Any]], bowl_weight: int) -> io.BytesIO:
    """
    Generate formatted vet report from entries.

    :param entries: List of entry dictionaries
    :param bowl_weight: Weight of the bowl in grams
    :return: BytesIO buffer containing the report text
    """
    daily_totals = compute_daily_totals(entries)
    daily_values = [v for v in daily_totals.values() if v > 0]
    avg = sum(daily_values) / len(daily_values) if daily_values else 0

    report = _build_report_header(entries, daily_totals, bowl_weight, avg, daily_values)
    report += _build_daily_breakdown(daily_totals)
    report += _build_detailed_log(entries)

    output = io.BytesIO(report.encode())
    output.seek(0)
    return output


# fmt: off
def _build_report_header(
        entries: list[dict[str, Any]],
        daily_totals: dict[str, int],
        bowl_weight: int,
        avg: float,
        daily_values: list[int],
) -> str:
    # fmt: on
    """Build the report header section."""
    return f"""MAPLE - WATER INTAKE REPORT
Generated: {datetime.now().strftime("%Y/%m/%d %H:%M")}
{"=" * 50}

SUMMARY
{"-" * 50}
Tracking Period: {entries[0]["date"]} to {entries[-1]["date"]}
Total Days Tracked: {len(daily_totals)}
Total Measurements: {len(entries)}
Bowl Weight: {bowl_weight}g

Daily Average Intake: {avg:.1f}g
Maximum Daily Intake: {max(daily_values) if daily_values else 0}g
Minimum Daily Intake: {min(daily_values) if daily_values else 0}g

"""


def _build_daily_breakdown(daily_totals: dict[str, int]) -> str:
    """Build the daily breakdown section."""
    lines = ["DAILY BREAKDOWN", "-" * 50]

    for date, total in sorted(daily_totals.items(), key=lambda x: _safe_parse_date(x[0])):
        lines.append(f"{date}: {total}g")

    lines.append("\n")
    return "\n".join(lines)


def _build_detailed_log(entries: list[dict[str, Any]]) -> str:
    """Build the detailed log section."""
    lines = ["DETAILED LOG (Raw Data)", "-" * 50]

    for entry in entries:
        line = (
            f"{entry['date']} - {entry['time']} -> "
            f"{entry['total_weight']}g total | "
            f"{entry['water_weight']}g water | "
            f"{entry.get('drink') or 0}g drink"
        )

        if entry.get("refill_to"):
            line += f" | {entry['refill_to']}g refill"
        if entry.get("notes"):
            line += f" | Notes: {entry['notes']}"

        lines.append(line)

    return "\n".join(lines)


def _safe_parse_date(date_str: str) -> str:
    """Safely parse date for sorting, returning original on failure."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").isoformat()
    except ValueError:
        return date_str


def get_export_filename(prefix: str, extension: str) -> str:
    """Generate timestamped export filename."""
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"{prefix}_{timestamp}.{extension}"
