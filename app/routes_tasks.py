# app/routes_tasks.py — task pages (INTENTIONALLY INSECURE).
# Insecure patterns:
#  - SQL built with f-strings / string formatting (SQL injection)
#  - Stores raw comment bodies (stored XSS)
#  - Template echoes 'q' with |safe and uses innerHTML on the client (reflected/DOM XSS)

from flask import Blueprint, render_template, request, redirect, url_for
from .db import get_db

bp = Blueprint("tasks", __name__, url_prefix="/")

@bp.route("/tasks")
def tasks():
    """List tasks."""
    rows = get_db().execute("SELECT id, title FROM tasks").fetchall()
    return render_template("tasks.html", rows=rows)

@bp.route("/task/<int:task_id>")
def task_detail(task_id):
    """Show one task and its comments (SQL built unsafely for demo)."""
    db = get_db()
    # INSECURE: f-string SQL
    task = db.execute(f"SELECT * FROM tasks WHERE id = {task_id}").fetchone()
    comments = db.execute(f"SELECT * FROM comments WHERE task_id = {task_id}").fetchall()
    return render_template("task_detail.html", task=task, comments=comments)

@bp.route("/task/<int:task_id>/comment", methods=("POST",))
def add_comment(task_id):
    """
    Store a new comment.
    INSECURE: stores raw HTML in 'body' -> stored XSS.
    """
    body = request.form.get("body", "")
    db = get_db()
    # INSECURE: string formatted SQL with user input
    db.execute("INSERT INTO comments (task_id, user_id, body) VALUES (%d, %d, '%s')" % (task_id, 1, body))
    db.commit()
    return redirect(url_for("tasks.task_detail", task_id=task_id))

@bp.route("/search")
def search():
    """
    Search tasks.
    INSECURE: concatenates user input into SQL -> SQL injection.
    """
    q = request.args.get("q", "")
    sql = "SELECT id, title FROM tasks WHERE title LIKE '%%%s%%' OR description LIKE '%%%s%%'" % (q, q)
    rows = get_db().execute(sql).fetchall()
    # Pass 'q' to the template; the insecure template renders it with |safe (reflected XSS)
    return render_template("tasks.html", rows=rows, q=q)
