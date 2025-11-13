# create_db.py (SECURE BRANCH)
# This script initialises the secure SQLite database.
# The main change compared to the insecure version is that I now:
#   - store a properly hashed password instead of a plaintext or weak value,
#   - use a separate DB file so I do not mix insecure and secure data.

import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

# I keep the DB file under the instance folder so it is not committed to Git.
instance = Path("instance")
instance.mkdir(parents=True, exist_ok=True)

# Separate DB name for the secure version.
db_path = instance / "taskpad_secure.sqlite3"

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create tables if they are not already present.
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

# Seed user for testing.
# In the insecure branch I used "password123" directly or a weak hash.
# Here I use PBKDF2-HMAC-SHA256 via generate_password_hash.
email = "alice@example.com"
plain_password = "Password123!"
password_hash = generate_password_hash(plain_password)
display_name = "Alice"

c.execute(
    "INSERT OR IGNORE INTO users (id, email, password_hash, display_name) VALUES (1, ?, ?, ?)",
    (email, password_hash, display_name)
)

# Seed a basic task so the UI has something to display.
c.execute(
    "INSERT OR IGNORE INTO tasks (id, user_id, title, description) VALUES (1, 1, 'Sample Task', 'This is a sample task in the secure DB.')"
)

conn.commit()
conn.close()

print("Secure database created at", db_path)
print("Seeded user:", email, "with password:", plain_password)
