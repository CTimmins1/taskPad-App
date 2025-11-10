# create_db.py — creates a small SQLite database with demo data.
# Safe to re-run (uses IF NOT EXISTS / INSERT OR IGNORE).

import sqlite3
from pathlib import Path

# Ensure the instance/ folder exists (Flask default place for local data)
instance = Path("instance")
instance.mkdir(parents=True, exist_ok=True)

db_path = instance / "taskpad_insecure.sqlite3"

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create tables
c.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password_hash TEXT,
    display_name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    user_id INTEGER,
    body TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
""")

# Seed a user + a task (so the app has something to show)
c.execute("INSERT OR IGNORE INTO users (id, email, password_hash, display_name) VALUES (1,'alice@example.com','demo','Alice')")
c.execute("INSERT OR IGNORE INTO tasks (id, user_id, title, description) VALUES (1,1,'Sample Task','This is a sample task.')")

conn.commit()
conn.close()
print("Database created at", db_path)
