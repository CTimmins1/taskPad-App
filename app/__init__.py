# app/__init__.py — Flask application factory.
# Loads .env, configures the app, registers blueprints, and sets up DB helper.

import os
from flask import Flask
from dotenv import load_dotenv

from . import db as db_module  # local sqlite helper

def create_app():
    """
    Create and configure the Flask app (insecure branch).
    DEBUG is enabled via .env.example to make it easy to see errors locally.
    """
    app = Flask(
        __name__,
        instance_relative_config=True,  # place local files under instance/
        template_folder="templates",
        static_folder="static"
    )

    # Load environment variables from repo root .env if present
    load_dotenv(os.path.join(app.root_path, "..", ".env"))

    # Minimal configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "devkey"),  # NEVER for prod
        DATABASE=os.environ.get(
            "DATABASE",
            os.path.join(app.instance_path, "taskpad_insecure.sqlite3")
        ),
        DEBUG=os.environ.get("FLASK_DEBUG", "True") == "True",  # INSECURE default
    )

    # Ensure instance/ exists for the SQLite file
    os.makedirs(app.instance_path, exist_ok=True)

    # Hook up DB helper (open/close per request)
    db_module.init_app(app)

    # Register route blueprints
    from .routes_auth import bp as auth_bp
    from .routes_tasks import bp as tasks_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    # Minimal landing page
    @app.route("/")
    def index():
        return "TaskPad (INSECURE) - visit /register, /login, /tasks"

    return app
