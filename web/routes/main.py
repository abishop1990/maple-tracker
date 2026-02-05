from database.db_operations import read_bowl_weight
from flask import Blueprint, render_template, g

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index() -> str:
    """Render main page with form and charts."""
    bowl_weight = read_bowl_weight(g.db)
    return render_template("index.html", bowl_weight=bowl_weight)
