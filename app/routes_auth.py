# Implements OWASP-compliant password handling using Werkzeug’s PBKDF2-HMAC-SHA256.
# Fixes SQL injection vulnerabilities by using parameterized SQL queries.
# Removes verbose error messages and logs events for accountability.

from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_db

bp = Blueprint("auth", __name__, url_prefix="/")

@bp.route("/register", methods=("GET", "POST"))
def register():
    # Registration endpoint (SECURE)
    #  Uses parameterized SQL to prevent injection
    #  Hashes passwords using PBKDF2 with unique salt (handled by Werkzeug)
    #  Logs registration activity
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        # Generate a salted PBKDF2-HMAC-SHA256 hash (OWASP compliant)
        pw_hash = generate_password_hash(password)

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (email, password_hash, display_name) VALUES (?, ?, ?)",
                (email, pw_hash, email.split("@")[0])
            )
            db.commit()
            current_app.logger.info("User registered successfully: %s", email)
            return redirect(url_for("auth.login"))
        except Exception as e:
            # Generic error message to avoid leaking DB structure
            current_app.logger.warning("Registration failed for %s: %s", email, str(e))
            return "Registration failed. Try again with a different email.", 400

    return render_template("register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    # Login endpoint (SECURE)
    #  Uses parameterized SQL for lookup
    #  Uses constant-time hash comparison to verify passwords
    #  Logs success and failure for monitoring
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            current_app.logger.info("Login successful for: %s", email)
            return redirect(url_for("index"))

        # Authentication failed – log attempt
        current_app.logger.warning("Login failed for: %s", email)
        return "Invalid credentials", 401

    return render_template("login.html")

@bp.route("/logout")
def logout():
    # Logout endpoint (SECURE)
    #  Clears the user session
    #  Logs the logout event for traceability
    session.clear()
    current_app.logger.info("User logged out.")
    return redirect(url_for("auth.login"))