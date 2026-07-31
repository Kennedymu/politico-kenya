import sqlite3
from pathlib import Path

# Backend directory
BASE_DIR = Path(__file__).resolve().parent

# SQLite database file
DATABASE = BASE_DIR / "database.db"


def get_connection():
    """
    Create and return a SQLite database connection.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn