# app/routes_auth.py (SECURE BRANCH)
# In this file I cleaned up the authentication logic:
# - switched from weak hashing to PBKDF2-HMAC-SHA256 via Werkzeug,
# - removed SQL injection by using parameterized queries,
# - added basic logging so I can see login/register activity.
# The insecure version used SHA1 and built SQL with string formatting,
# which was very easy to attack.

from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_db

bp = Blueprint("auth", __name__, url_prefix="/")

@bp.route("/register", methods=("GET", "POST"))
def register():
    # Registration endpoint in the secure branch.
    # I now:
    #   - normalise the email,
    #   - hash the password using PBKDF2,
    #   - use a parameterized INSERT to avoid SQL injection.
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        # Insecure branch used SHA1; this uses PBKDF2-HMAC-SHA256 instead.
        pw_hash = generate_password_hash(password)

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (email, password_hash, display_name) VALUES (?, ?, ?)",
                (email, pw_hash, email.split("@")[0])
            )
            db.commit()
            current_app.logger.info("User registered: %s", email)
            return redirect(url_for("auth.login"))
        except Exception as e:
            # I only log the detailed error on the server side.
            # The user sees a generic message so I do not leak internals.
            current_app.logger.warning("Registration failed for %s: %s", email, str(e))
            return "Registration failed. Try a different email.", 400

    return render_template("register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    # Login endpoint in the secure branch.
    # Here I:
    #   - fetch the user by email using a parameterized query,
    #   - verify the password using check_password_hash,
    #   - log both successful and failed login attempts.
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            current_app.logger.info("Login successful for: %s", email)
            return redirect(url_for("index"))

        current_app.logger.warning("Login failed for: %s", email)
        return "Invalid credentials", 401

    return render_template("login.html")

@bp.route("/logout")
def logout():
    # Logging out is simple: clear the session and redirect.
    # I also log the event so I have a basic audit trail.
    session.clear()
    current_app.logger.info("User logged out.")
    return redirect(url_for("auth.login"))
