# app/routes_tasks.py (SECURE BRANCH)
# In this file I focused on fixing:
#   - SQL injection in the task queries and search,
#   - stored, reflected and DOM-based XSS in comments and the search banner,
#   - lack of input validation,
#   - lack of logging for task operations.

from flask import Blueprint, render_template, request, redirect, url_for, abort, current_app
from .db import get_db

bp = Blueprint("tasks", __name__, url_prefix="/")

def _normalize_query(text, max_length=100):
    # I normalise the search query to keep it predictable:
    # trim whitespace and limit length to avoid extremely large inputs.
    return (text or "").strip()[:max_length]

@bp.route("/tasks")
def tasks():
    # This route lists tasks.
    # I switched to a simple ordered SELECT so I can show the newest task first.
    db = get_db()
    rows = db.execute("SELECT id, title FROM tasks ORDER BY id DESC").fetchall()
    current_app.logger.info("Tasks listed, count=%s", len(rows))
    return render_template("tasks.html", rows=rows)

@bp.route("/task/<int:task_id>")
def task_detail(task_id):
    # This route shows a single task and its comments.
    # The insecure version built SQL using f-strings, which was vulnerable to injection.
    # Here I use parameterized queries instead.
    db = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    if not task:
        abort(404)

    comments = db.execute(
        "SELECT * FROM comments WHERE task_id = ? ORDER BY id DESC", (task_id,)
    ).fetchall()

    # I rely on Jinja's autoescaping here so comments are rendered safely.
    return render_template("task_detail.html", task=task, comments=comments)

@bp.route("/task/<int:task_id>/comment", methods=("POST",))
def add_comment(task_id):
    # This route adds a comment to a task.
    # In the insecure branch I was inserting raw HTML directly into the DB and rendering it with |safe,
    # which gave a classic stored XSS. Here I:
    #   - trim the input,
    #   - reject empty comments,
    #   - insert the text safely using a parameterized query.
    body = (request.form.get("body") or "").strip()
    if not body:
        current_app.logger.warning("Empty comment rejected for task_id=%s", task_id)
        return redirect(url_for("tasks.task_detail", task_id=task_id))

    db = get_db()
    db.execute(
        "INSERT INTO comments (task_id, user_id, body) VALUES (?, ?, ?)",
        (task_id, 1, body)
    )
    db.commit()
    current_app.logger.info("Comment added for task_id=%s", task_id)
    return redirect(url_for("tasks.task_detail", task_id=task_id))

@bp.route("/search")
def search():
    # This route searches tasks by keyword in title or description.
    # The insecure version concatenated the search string directly into SQL.
    # Here I normalise the query and use parameterized LIKE queries instead.
    q = _normalize_query(request.args.get("q", ""))
    like = f"%{q}%"

    db = get_db()
    rows = db.execute(
        "SELECT id, title FROM tasks WHERE title LIKE ? OR description LIKE ? ORDER BY id DESC",
        (like, like)
    ).fetchall()

    current_app.logger.info("Search executed for q='%s', results=%s", q, len(rows))
    return render_template("tasks.html", rows=rows, q=q)
