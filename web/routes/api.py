from database.db_operations import update_bowl_weight as db_update_bowl_weight, read_all_entries, SortOrder
from flask import Blueprint, request, jsonify, g

from web.services.entry_service import (
    EntryInput,
    EntryUpdateInput,
    create_entry,
    update_entry,
    delete_entry,
    get_entry,
    get_all_entries,
    ValidationError,
    NotFoundError,
)
from web.services.import_service import import_raw_text
from web.services.stats_service import compute_stats

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/entries", methods=["GET"])
def get_entries():
    """Get all entries with bowl weight."""
    bowl_weight, entries = get_all_entries(g.db)
    return jsonify({"bowl_weight": bowl_weight, "entries": entries})


@api_bp.route("/entries/<int:entry_id>", methods=["GET"])
def get_entry_by_id(entry_id: int):
    """Get a single entry by ID."""
    if entry_id < 1:
        return jsonify({"success": False, "error": "Invalid entry ID"}), 400

    try:
        entry = get_entry(g.db, entry_id)
        return jsonify({"success": True, "entry": entry})
    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception:
        return jsonify({"success": False, "error": "An unexpected error occurred"}), 500


@api_bp.route("/entries", methods=["POST"])
def add_entry():
    """Add a new water tracking entry."""
    if not request.json:
        return jsonify({"error": "JSON body required"}), 400
    try:
        entry_input = EntryInput.from_dict(request.json)
        result = create_entry(g.db, entry_input)

        return jsonify(
            {
                "success": True,
                "id": result.id,
                "drink": result.drink,
                "water_weight": result.water_weight,
            }
        )
    except ValidationError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception:
        return jsonify({"success": False, "error": "An unexpected error occurred"}), 500


@api_bp.route("/entries/<int:entry_id>", methods=["PUT"])
def update_entry_endpoint(entry_id: int):
    """Update an existing water tracking entry."""
    if entry_id < 1:
        return jsonify({"success": False, "error": "Invalid entry ID"}), 400

    if not request.json:
        return jsonify({"success": False, "error": "JSON body required"}), 400

    try:
        update_input = EntryUpdateInput.from_dict(request.json)
        result = update_entry(g.db, entry_id, update_input)

        return jsonify(
            {
                "success": True,
                "entry": {
                    "id": result.id,
                    "date": result.date,
                    "time": result.time,
                    "total_weight": result.total_weight,
                    "water_weight": result.water_weight,
                    "drink": result.drink,
                    "refill_to": result.refill_to,
                    "notes": result.notes,
                },
            }
        )
    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except ValidationError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception:
        return jsonify({"success": False, "error": "An unexpected error occurred"}), 500


@api_bp.route("/entries/<int:entry_id>", methods=["DELETE"])
def remove_entry(entry_id: int):
    """Delete an entry by ID."""
    if entry_id < 1:
        return jsonify({"success": False, "error": "Invalid entry ID"}), 400

    try:
        delete_entry(g.db, entry_id)
        return jsonify({"success": True})
    except Exception:
        return jsonify({"success": False, "error": "Failed to delete entry"}), 500


@api_bp.route("/bowl-weight", methods=["POST"])
def update_bowl_weight():
    """Update the bowl weight setting."""
    min_bowl_weight = 10
    max_bowl_weight = 2000
    if not request.json:
        return jsonify({"success": False, "error": "JSON body required"}), 400

    new_weight = request.json.get("bowl_weight")

    if new_weight is None:
        return jsonify({"success": False, "error": "bowl_weight is required"}), 400

    try:
        new_weight = int(new_weight)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "bowl_weight must be a number"}), 400

    if not min_bowl_weight <= new_weight <= max_bowl_weight:
        return jsonify(
            {"success": False, "error": f"bowl_weight must be between {min_bowl_weight} and {max_bowl_weight} grams"}
        ), 400

    try:
        db_update_bowl_weight(g.db, new_weight)
        return jsonify({"success": True})
    except (ValueError, TypeError) as e:
        return jsonify({"success": False, "error": f"Invalid weight: {e}"}), 400


@api_bp.route("/stats", methods=["GET"])
def get_stats():
    """Get computed statistics for charts."""
    entries = read_all_entries(g.db, order=SortOrder.ASC)
    stats = compute_stats(entries)
    return jsonify(stats)


@api_bp.route("/import-raw", methods=["POST"])
def import_raw():
    """Import data from raw text format."""
    if not request.json:
        return jsonify({"success": False, "error": "JSON body required"}), 400

    raw_text = request.json.get("raw_text", "")

    if not isinstance(raw_text, str):
        return jsonify({"success": False, "error": "raw_text must be a string"}), 400

    if not raw_text.strip():
        return jsonify({"success": False, "error": "No data provided"}), 400

    max_length_for_text = 100_000  # ~100KB
    if len(raw_text) > max_length_for_text:
        return jsonify({"success": False, "error": "Import data too large"}), 400

    try:
        imported = import_raw_text(g.db, raw_text)
        return jsonify({"success": True, "imported": imported})
    except Exception:
        return jsonify({"success": False, "error": "Failed to import data"}), 500
