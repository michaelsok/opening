import sqlite3
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "opening.db")

def get_connection(db_path: str = DEFAULT_DB_PATH):
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db(db_path: str = DEFAULT_DB_PATH):
    """Initializes the database schema."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repertoires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            color TEXT NOT NULL,
            filename TEXT NOT NULL,
            pgn_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username, color)
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {db_path}")

def save_repertoire(username: str, color: str, filename: str, pgn_content: str, db_path: str = DEFAULT_DB_PATH):
    """Saves or updates a repertoire in the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO repertoires (username, color, filename, pgn_content, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(username, color) DO UPDATE SET
            filename = excluded.filename,
            pgn_content = excluded.pgn_content,
            created_at = excluded.created_at
    """, (username, color, filename, pgn_content, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_repertoires_by_user(username: str, db_path: str = DEFAULT_DB_PATH) -> List[Dict]:
    """Retrieves all repertoires for a given user."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM repertoires WHERE username = ?", (username,))
    rows = cursor.fetchall()
    
    results = [dict(row) for row in rows]
    conn.close()
    return results

def delete_repertoire(username: str, color: str, db_path: str = DEFAULT_DB_PATH):
    """Deletes a repertoire from the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM repertoires WHERE username = ? AND color = ?", (username, color))
    
    conn.commit()
    conn.close()
