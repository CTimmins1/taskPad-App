# app/routes_auth.py — authentication endpoints (INTENTIONALLY INSECURE).
# Insecure patterns shown for the assignment:
#  - SHA1 password hashing (weak, no salt)
#  - SQL built via string formatting (vulnerable to SQL injection)

from flask import Blueprint, render_template, request, redirect, url_for, session
import hashlib
from .db import get_db

bp = Blueprint("auth", __name__, url_prefix="/")

@bp.route("/register", methods=("GET", "POST"))
def register():
    """
    Register a new user.
    INSECURE: Weak hashing and SQL string formatting used on purpose.
    """
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # INSECURE: SHA1 without salt (demonstration only)
        password_hash = hashlib.sha1(password.encode()).hexdigest()

        db = get_db()
        # INSECURE: string formatting inserts user input directly into SQL
        db.execute(
            "INSERT INTO users (email, password_hash, display_name) "
            "VALUES ('%s','%s','%s')" %
            (email, password_hash, email.split("@")[0])
        )
        db.commit()
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    """
    Log in a user.
    INSECURE: Query uses string formatting so you can demo SQL injection.
    """
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Same weak hashing to compare with stored hash
        password_hash = hashlib.sha1(password.encode()).hexdigest()

        db = get_db()
        # INSECURE: vulnerable to SQL injection
        user = db.execute(
            "SELECT * FROM users WHERE email = '%s' AND password_hash = '%s'" %
            (email, password_hash)
        ).fetchone()

        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        return "Invalid credentials", 401

    return render_template("login.html")

@bp.route("/logout")
def logout():
    """Clear session and send user back to login page."""
    session.clear()
    return redirect(url_for("auth.login"))
