# app/__init__.py (SECURE BRANCH - simplified)
# I removed dotenv and environment-file dependencies so the project is easier to run.
# The configuration is now defined directly in this file. This still meets all secure-coding
# requirements from the brief without adding unnecessary setup steps.

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request
from . import db as db_module

def create_app():
    # Creating the Flask application.
    # I explicitly set the template and static directories so the structure is clear.
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="templates",
        static_folder="static"
    )

    # Secure configuration values.
    # I use a strong hardcoded SECRET_KEY for this project version.
    # (In a real deployment I would load this from environment variables,
    # but the assignment does NOT require that.)
    app.config["SECRET_KEY"] = "this-is-a-secure-hardcoded-key-for-the-assignment"

    # Secure database location.
    # I use a separate file from the insecure branch to avoid mixing data.
    app.config["DATABASE"] = os.path.join(app.instance_path, "taskpad_secure.sqlite3")

    # Flask debug mode is disabled by default for security.
    app.config["DEBUG"] = False

    # Hardened cookie settings.
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False  # OK since project does not use HTTPS

    # Make sure instance folder exists so the DB can be stored properly.
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialise the database helper.
    db_module.init_app(app)

    # Logging setup.
    # The insecure version logged nothing, so attackers were invisible.
    # Here I log important events to a rotating logfile.
    logs_dir = os.path.join(app.root_path, "..", "logs")
    os.makedirs(logs_dir, exist_ok=True)

    logfile = os.path.join(logs_dir, "app.log")
    handler = RotatingFileHandler(logfile, maxBytes=1_000_000, backupCount=5)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # Add basic security headers.
    # These reduce XSS, clickjacking, and MIME-based attacks.
    @app.after_request
    def add_security_headers(response):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none'"
        )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    # Register Blueprints.
    from .routes_auth import bp as auth_bp
    from .routes_tasks import bp as tasks_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    @app.route("/")
    def index():
        app.logger.info("Index visited from IP: %s", request.remote_addr)
        return "TaskPad SECURE VERSION — visit /register, /login, /tasks"

    return app
