import sqlite3

from flask import Flask, g

from database.db_operations import init_database
from database.path_manager import PathManager
from web.routes.api import api_bp
from web.routes.export import export_bp
from web.routes.main import main_bp


def _register_db_handlers(app: Flask) -> None:
    """Register database connection handlers."""

    @app.before_request
    def open_db():
        """Open database connection for each request."""
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row

    @app.teardown_appcontext
    def close_db(exception):
        """Close database connection at end of request."""
        db = g.pop("db", None)
        if db is not None:
            db.close()


def create_app(database_path: str | None = None) -> Flask:
    """
    Application factory for creating Flask app instances.

    Args:
        database_path: Optional path to database file.
                      Defaults to PathManager.MAPLE_DATABASE_PATH

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    app.config["DATABASE"] = database_path if database_path is not None else PathManager.MAPLE_DATABASE_PATH

    _register_db_handlers(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(export_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    init_database()
    application.run(host="0.0.0.0", port=5000, debug=True)
