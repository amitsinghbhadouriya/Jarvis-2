"""
Database access and persistence layer for Jarvis 2.
Utilizes SQLite for conversation history, contacts, notes, and preferences.
"""

import os
import csv
import sqlite3
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from backend.config import config
from backend.logger import get_logger

logger = get_logger("Database")


@contextmanager
def get_db(db_path: Optional[str] = None):
    """Context manager for SQLite database connection."""
    target_path = str(db_path or config.db_path)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise
    finally:
        conn.close()


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database tables if they do not exist."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()

        # Commands & conversation history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commands_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT NOT NULL,
                response TEXT NOT NULL,
                source TEXT DEFAULT 'voice',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Contacts management
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL COLLATE NOCASE,
                phone TEXT,
                email TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Key-value user settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Quick notes / reminders
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_time ON commands_history(timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name)")

    logger.info("Database schema verified and initialized.")


def log_command(user_input: str, response: str, source: str = "voice", db_path: Optional[str] = None) -> int:
    """Record an interaction in command history."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO commands_history (user_input, response, source) VALUES (?, ?, ?)",
            (user_input, response, source),
        )
        return cursor.lastrowid or 0


def get_recent_history(limit: int = 50, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve recent conversation interactions."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, user_input, response, source, timestamp FROM commands_history ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows][::-1]


def clear_history(db_path: Optional[str] = None) -> None:
    """Clear conversation history."""
    with get_db(db_path) as conn:
        conn.execute("DELETE FROM commands_history")
    logger.info("Command history cleared.")


def add_contact(name: str, phone: str = "", email: str = "", notes: str = "", db_path: Optional[str] = None) -> int:
    """Insert or update a contact."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contacts (name, phone, email, notes) VALUES (?, ?, ?, ?)",
            (name.strip(), phone.strip(), email.strip(), notes.strip()),
        )
        return cursor.lastrowid or 0


def get_contacts(search: Optional[str] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search or list all contacts."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        if search:
            cursor.execute(
                "SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? ORDER BY name ASC",
                (f"%{search}%", f"%{search}%", f"%{search}%"),
            )
        else:
            cursor.execute("SELECT * FROM contacts ORDER BY name ASC")
        return [dict(row) for row in cursor.fetchall()]


def find_contact_by_name(name: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Find a single contact by name."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE name LIKE ? LIMIT 1", (f"%{name}%",))
        row = cursor.fetchone()
        return dict(row) if row else None


def import_contacts_csv(csv_path: str, db_path: Optional[str] = None) -> int:
    """Import contacts from a CSV file."""
    if not os.path.exists(csv_path):
        return 0

    count = 0
    with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name") or row.get("Name")
            if name:
                phone = row.get("phone") or row.get("Phone") or ""
                email = row.get("email") or row.get("Email") or ""
                notes = row.get("notes") or row.get("Notes") or ""
                add_contact(name, phone, email, notes, db_path=db_path)
                count += 1
    logger.info(f"Imported {count} contacts from {csv_path}")
    return count


def set_setting(key: str, value: str, db_path: Optional[str] = None) -> None:
    """Store or update a setting value."""
    with get_db(db_path) as conn:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
            (key, str(value)),
        )


def get_setting(key: str, default: Optional[str] = None, db_path: Optional[str] = None) -> Optional[str]:
    """Retrieve a setting value with fallback."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default


def add_note(title: str, content: str, db_path: Optional[str] = None) -> int:
    """Create a new user note."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        return cursor.lastrowid or 0


def get_notes(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all user notes."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]
