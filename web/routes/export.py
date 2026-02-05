from database.db_operations import read_bowl_weight, read_all_entries, SortOrder
from flask import Blueprint, g, send_file, Response

from web.services.export_service import generate_csv_export, generate_vet_report, get_export_filename

export_bp = Blueprint("export", __name__, url_prefix="/export")


@export_bp.route("/csv")
def export_csv() -> Response | tuple[str, int]:
    """Export all data as CSV."""
    entries = read_all_entries(g.db, order=SortOrder.ASC)

    if not entries:
        return "No data to export", 404

    csv_buffer = generate_csv_export(entries)
    filename = get_export_filename("maple_water_log", "csv")

    return send_file(
        csv_buffer,
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename,
    )


@export_bp.route("/vet-report")
def export_vet_report() -> Response | tuple[str, int]:
    """Export formatted report for veterinarian."""
    entries = read_all_entries(g.db, order=SortOrder.ASC)

    if not entries:
        return "No data to export", 404

    bowl_weight = read_bowl_weight(g.db)
    report_buffer = generate_vet_report(entries, bowl_weight)
    filename = get_export_filename("maple_vet_report", "txt")

    return send_file(
        report_buffer,
        mimetype="text/plain",
        as_attachment=True,
        download_name=filename,
    )
