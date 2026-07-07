"""
Database setup for the DevSecOps demo app.
Creates a simple SQLite database with a users table.
"""

import sqlite3
import os


DB_PATH = os.getenv("DB_PATH", "users.db")


def init_db():
    """Initialize the database with sample data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)

    # Insert sample data if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        sample_users = [
            ("alice", "alice@example.com", "admin"),
            ("bob", "bob@example.com", "user"),
            ("charlie", "charlie@example.com", "user"),
        ]
        cursor.executemany(
            "INSERT INTO users (username, email, role) VALUES (?, ?, ?)",
            sample_users
        )

    conn.commit()
    conn.close()


def get_connection():
    """Return a database connection."""
    return sqlite3.connect(DB_PATH)
