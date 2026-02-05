import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any


from database.compute_stats import calculate_drink_amount
from database.db_operations import (
    read_bowl_weight,
    read_previous_entry,
    read_entry_by_id,
    create_entry as db_create_entry,
    update_entry_by_id as db_update_entry,
    delete_entry_by_id as db_delete_entry,
    read_all_entries,
    SortOrder,
)
from database.types import Entry


class ValidationError(ValueError):
    """Raised when input validation fails."""

    pass


class NotFoundError(Exception):
    """Raised when a requested resource is not found."""

    pass


@dataclass
class EntryValidatorBase:
    """Shared constants and validation logic."""

    MIN_WEIGHT = 10
    MAX_WEIGHT = 5000  # 5kg should cover any cat bowl
    MAX_NOTES_LENGTH = 500

    @classmethod
    def _validate_base_dict(cls, data: object) -> dict[str, object]:
        if data is None:
            raise ValidationError("Request body is required")
        if not isinstance(data, dict):
            raise ValidationError("Request body must be a JSON object")
        return data

    @classmethod
    def _parse_weight(cls, value: Any, name: str, required: bool = False) -> int | None:
        if value is None or value == "":
            if required:
                raise ValidationError(f"{name} is required")
            return None
        try:
            weight = int(value)
        except (ValueError, TypeError) as exc:
            raise ValidationError(f"{name} must be a valid number") from exc

        if not cls.MIN_WEIGHT <= weight <= cls.MAX_WEIGHT:
            raise ValidationError(f"{name} must be between {cls.MIN_WEIGHT} and {cls.MAX_WEIGHT}")
        return weight

    @classmethod
    def _parse_date(cls, value: str | object) -> str | None:
        """Validate and parse a date value."""
        if value is None or value == "":
            return None
        if not isinstance(value, str):
            raise ValidationError("date must be a string")

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            raise ValidationError("date must be in YYYY-MM-DD format")

        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValidationError("date is not a valid calendar date") from exc
        return value

    @classmethod
    def _parse_time(cls, value: str | object) -> str | None:
        """Validate and parse a time value."""
        if value is None or value == "":
            return None
        if not isinstance(value, str):
            raise ValidationError("time must be a string")

        if not re.match(r"^\d{2}:\d{2}$", value):
            raise ValidationError("time must be in HH:MM format")

        try:
            datetime.strptime(value, "%H:%M")
        except ValueError as exc:
            raise ValidationError("time is not a valid time") from exc
        return value

    @classmethod
    def _parse_notes(cls, value: str | object, required: bool = False) -> str | None:
        """Validate and parse notes."""
        if value is None:
            return "" if required else None
        if not isinstance(value, str):
            raise ValidationError("notes must be a string")

        if len(value) > cls.MAX_NOTES_LENGTH:
            raise ValidationError(f"notes must be {cls.MAX_NOTES_LENGTH} characters or less")
        return value.strip()


@dataclass
class EntryInput(EntryValidatorBase):
    """Validated input for creating an entry."""

    total_weight: int
    date: str | None = None
    time: str | None = None
    drink_manual: int | None = None
    refill_to: int | None = None
    notes: str | None = ""
    is_refill_only: bool = False

    @classmethod
    def from_dict(cls, data: object) -> "EntryInput":
        """Create EntryInput from request data with validation."""
        data = cls._validate_base_dict(data)

        total_weight = cls._parse_weight(data.get("total_weight"), "total_weight", required=True)
        drink_manual = cls._parse_weight(data.get("drink_manual"), "drink_manual", required=False)
        refill_to = cls._parse_weight(data.get("refill_to"), "refill_to", required=False)
        date = cls._parse_date(data.get("date"))
        time = cls._parse_time(data.get("time"))
        notes = cls._parse_notes(data.get("notes", ""))
        is_refill_only = bool(data.get("is_refill_only", False))

        if total_weight is None or total_weight < 0:
            raise ValidationError("total_weight must be greater than 0")

        return cls(
            total_weight=total_weight,
            date=date,
            time=time,
            drink_manual=drink_manual,
            refill_to=refill_to,
            notes=notes,
            is_refill_only=is_refill_only,
        )


@dataclass
class EntryUpdateInput(EntryValidatorBase):
    """Validated input for updating an entry."""

    total_weight: int | None = None
    date: str | None = None
    time: str | None = None
    drink: int | None = None
    refill_to: int | None = None
    notes: str | None = None

    @classmethod
    def from_dict(cls, data: object) -> "EntryUpdateInput":
        """Create EntryUpdateInput from request data with validation."""
        data = cls._validate_base_dict(data)

        total_weight = cls._parse_weight(data.get("total_weight"), "total_weight") if "total_weight" in data else None
        drink = cls._parse_weight(data.get("drink"), "drink") if "drink" in data else None
        refill_to = cls._parse_weight(data.get("refill_to"), "refill_to") if "refill_to" in data else None
        date = cls._parse_date(data.get("date")) if "date" in data else None
        time = cls._parse_time(data.get("time")) if "time" in data else None
        notes = cls._parse_notes(data.get("notes")) if "notes" in data else None

        return cls(
            total_weight=total_weight,
            date=date,
            time=time,
            drink=drink,
            refill_to=refill_to,
            notes=notes,
        )

    def has_updates(self) -> bool:
        """Check if any field has an update value."""
        return any(
            [
                self.total_weight is not None,
                self.date is not None,
                self.time is not None,
                self.drink is not None,
                self.refill_to is not None,
                self.notes is not None,
            ]
        )


@dataclass
class EntryResult:
    """Result of creating an entry."""

    id: int
    drink: int
    water_weight: int


@dataclass
class EntryUpdateResult:
    """Result of updating an entry."""

    id: int
    date: str
    time: str
    total_weight: int
    water_weight: int
    drink: int
    refill_to: int | None
    notes: str


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

    if new_id is None:
        raise RuntimeError(f"Entry with id {new_id} can't be created")

    return EntryResult(id=new_id, drink=drink, water_weight=water_weight)


def update_entry(conn: sqlite3.Connection, entry_id: int, update_input: EntryUpdateInput) -> EntryUpdateResult:
    """
    Update an existing water tracking entry.

    Only updates fields that are provided in update_input.
    Recalculates water_weight if total_weight is changed.

    :param conn: Database connection
    :param entry_id: ID of the entry to update
    :param update_input: Validated update input data
    :return: EntryUpdateResult with the updated entry details
    """
    existing = read_entry_by_id(conn, entry_id)
    if existing is None:
        raise NotFoundError(f"Entry with ID {entry_id} not found")

    if not update_input.has_updates():
        raise ValidationError("No fields to update")

    bowl_weight = read_bowl_weight(conn)

    new_date = update_input.date if update_input.date is not None else existing["date"]
    new_time = update_input.time if update_input.time is not None else existing["time"]
    new_total_weight = update_input.total_weight if update_input.total_weight is not None else existing["total_weight"]
    new_drink = update_input.drink if update_input.drink is not None else existing["drink"]
    new_notes = update_input.notes if update_input.notes is not None else existing["notes"]

    if "refill_to" in update_input.__dict__ and update_input.refill_to is None:
        new_refill_to = None
    elif update_input.refill_to is not None:
        new_refill_to = update_input.refill_to
    else:
        new_refill_to = existing["refill_to"]

    new_water_weight = new_total_weight - bowl_weight

    success = db_update_entry(
        conn=conn,
        entry_id=entry_id,
        date=new_date,
        time=new_time,
        total_weight=new_total_weight,
        water_weight=new_water_weight,
        drink=new_drink,
        refill_to=new_refill_to,
        notes=new_notes,
    )

    if not success:
        raise NotFoundError(f"Entry with ID {entry_id} not found")

    return EntryUpdateResult(
        id=entry_id,
        date=new_date,
        time=new_time,
        total_weight=new_total_weight,
        water_weight=new_water_weight,
        drink=new_drink,
        refill_to=new_refill_to,
        notes=new_notes,
    )


def get_entry(conn: sqlite3.Connection, entry_id: int) -> Entry | dict[Any, Any]:
    """
    Get a single entry by ID.

    :param conn: Database connection
    :param entry_id: ID of the entry to retrieve
    :return: Entry dictionary
    """
    entry = read_entry_by_id(conn, entry_id)
    if entry is None:
        raise NotFoundError(f"Entry with ID {entry_id} not found")
    return entry


def delete_entry(conn: sqlite3.Connection, entry_id: int) -> None:
    """Delete an entry by ID."""
    db_delete_entry(conn, entry_id)


def get_all_entries(conn: sqlite3.Connection) -> tuple[int, list[dict[Any, Any]] | list[Entry] | None]:
    """
    Get all entries with bowl weight.

    :param conn: Database connection
    :return: Tuple of (bowl_weight, entries_list)
    """
    bowl_weight = read_bowl_weight(conn)
    entries = read_all_entries(conn, order=SortOrder.ASC)
    return bowl_weight, entries
