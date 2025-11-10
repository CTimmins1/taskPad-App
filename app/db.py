# app/db.py — very small SQLite helper.
# Provides get_db() to reuse one connection per request,
# and closes it automatically at the end of the request.

import sqlite3
from flask import current_app, g

def get_db():
    """
    Return a sqlite3 connection stored on Flask's 'g'.
    Rows are dict-like via row_factory.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close the DB connection if one exists in this request context."""
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_app(app):
    """Register close_db to run after each request."""
    app.teardown_appcontext(close_db)
