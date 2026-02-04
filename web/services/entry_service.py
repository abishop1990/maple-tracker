import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from database.compute_stats import calculate_drink_amount
from database.db_operations import (
    read_bowl_weight,
    read_previous_entry,
    create_entry as db_create_entry,
    delete_entry_by_id as db_delete_entry,
    read_all_entries, SortOrder,
)


class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass


@dataclass
class EntryInput:
    """Validated input for creating an entry."""
    total_weight: int
    date: str | None = None
    time: str | None = None
    drink_manual: int | None = None
    refill_to: int | None = None
    notes: str = ""
    is_refill_only: bool = False

    MIN_WEIGHT = 0
    MAX_WEIGHT = 5000  # 5kg should cover any cat bowl
    MAX_NOTES_LENGTH = 500

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EntryInput":
        """Create EntryInput from request data with validation."""
        if data is None:
            raise ValidationError("Request body is required")

        if not isinstance(data, dict):
            raise ValidationError("Request body must be a JSON object")

        total_weight = cls._parse_weight(data.get("total_weight"), "total_weight", required=True)
        drink_manual = cls._parse_weight(data.get("drink_manual"), "drink_manual", required=False)
        refill_to = cls._parse_weight(data.get("refill_to"), "refill_to", required=False)
        date = cls._parse_date(data.get("date"))
        time = cls._parse_time(data.get("time"))
        notes = cls._parse_notes(data.get("notes", ""))
        is_refill_only = bool(data.get("is_refill_only", False))

        return cls(
            total_weight=total_weight,
            date=date,
            time=time,
            drink_manual=drink_manual,
            refill_to=refill_to,
            notes=notes,
            is_refill_only=is_refill_only,
        )

    @classmethod
    def _parse_weight(cls, value: Any, field_name: str, required: bool) -> int | None:
        """Validate and parse a weight value."""
        if value is None or value == "":
            if required:
                raise ValidationError(f"{field_name} is required")
            return None

        try:
            weight = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid number")

        if not cls.MIN_WEIGHT <= weight <= cls.MAX_WEIGHT:
            raise ValidationError(
                f"{field_name} must be between {cls.MIN_WEIGHT} and {cls.MAX_WEIGHT} grams"
            )

        return weight

    @classmethod
    def _parse_date(cls, value: Any) -> str | None:
        """Validate and parse a date value."""
        if value is None or value == "":
            return None

        if not isinstance(value, str):
            raise ValidationError("date must be a string")

        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, value):
            raise ValidationError("date must be in YYYY-MM-DD format")

        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("date is not a valid calendar date")

        return value

    @classmethod
    def _parse_time(cls, value: Any) -> str | None:
        """Validate and parse a time value."""
        if value is None or value == "":
            return None

        if not isinstance(value, str):
            raise ValidationError("time must be a string")

        time_pattern = r"^\d{2}:\d{2}$"
        if not re.match(time_pattern, value):
            raise ValidationError("time must be in HH:MM format")

        try:
            datetime.strptime(value, "%H:%M")
        except ValueError:
            raise ValidationError("time is not a valid time")

        return value

    @classmethod
    def _parse_notes(cls, value: Any) -> str:
        """Validate and parse notes."""
        if value is None:
            return ""

        if not isinstance(value, str):
            raise ValidationError("notes must be a string")

        if len(value) > cls.MAX_NOTES_LENGTH:
            raise ValidationError(f"notes must be {cls.MAX_NOTES_LENGTH} characters or less")

        return value.strip()


@dataclass
class EntryResult:
    """Result of creating an entry."""
    id: int
    drink: int
    water_weight: int


def create_entry(conn: sqlite3.Connection, entry_input: EntryInput) -> EntryResult:
    """
    Create a new water tracking entry with calculated drink amount.

    Calculates drink amount unless it's a refill-only entry

    :param conn: Database connection
    :param entry_input: Validated entry input data
    :return: EntryResult with the new entry details
    """
    bowl_weight = read_bowl_weight(conn)
    water_weight = entry_input.total_weight - bowl_weight

    drink = 0
    if not entry_input.is_refill_only:
        prev = read_previous_entry(conn)
        drink = calculate_drink_amount(water_weight, prev, bowl_weight)

    if entry_input.drink_manual is not None:
        drink = entry_input.drink_manual

    now = datetime.now()
    new_id = db_create_entry(
        conn=conn,
        date=entry_input.date or now.strftime("%Y-%m-%d"),
        time=entry_input.time or now.strftime("%H:%M"),
        total_weight=entry_input.total_weight,
        water_weight=water_weight,
        drink=drink,
        refill_to=entry_input.refill_to,
        notes=entry_input.notes,
    )

    return EntryResult(id=new_id, drink=drink, water_weight=water_weight)


def delete_entry(conn: sqlite3.Connection, entry_id: int) -> None:
    """Delete an entry by ID."""
    db_delete_entry(conn, entry_id)


def get_all_entries(conn: sqlite3.Connection) -> tuple[int, list[dict]]:
    """
    Get all entries with bowl weight.

    :param conn: Database connection
    :return: Tuple of (bowl_weight, entries_list)
    """
    bowl_weight = read_bowl_weight(conn)
    entries = read_all_entries(conn, order=SortOrder.ASC)
    return bowl_weight, entries
