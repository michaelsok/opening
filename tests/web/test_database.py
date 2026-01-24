import pytest
import sqlite3
import os
from pathlib import Path
from src.web.database import (
    initialize_db,
    save_repertoire,
    get_repertoires_by_user,
    delete_repertoire
)

@pytest.fixture
def test_db(tmp_path):
    """Fixture to create a temporary test database."""
    db_path = tmp_path / "test_opening.db"
    # Ensure the parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize the database
    initialize_db(str(db_path))
    return str(db_path)

def test_initialize_db(test_db):
    """Test that the database is correctly initialized with the expected table."""
    assert os.path.exists(test_db)
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='repertoires'")
    assert cursor.fetchone() is not None
    conn.close()

def test_save_and_get_repertoire(test_db):
    """Test saving and retrieving a repertoire."""
    username = "testuser"
    color = "white"
    filename = "repertoire_white.pgn"
    pgn_content = '[Event "Test"]\n1. e4 e5 *'
    
    # Save
    save_repertoire(username, color, filename, pgn_content, db_path=test_db)
    
    # Retrieve
    repertoires = get_repertoires_by_user(username, db_path=test_db)
    assert len(repertoires) == 1
    assert repertoires[0]['username'] == username
    assert repertoires[0]['color'] == color
    assert repertoires[0]['filename'] == filename
    assert repertoires[0]['pgn_content'] == pgn_content

def test_overwrite_repertoire(test_db):
    """Test that uploading the same color repertoire for a user overwrites the previous one."""
    username = "testuser"
    color = "white"
    PGN1 = '[Event "P1"]\n1. e4 *'
    PGN2 = '[Event "P2"]\n1. d4 *'
    
    save_repertoire(username, color, "f1.pgn", PGN1, db_path=test_db)
    save_repertoire(username, color, "f2.pgn", PGN2, db_path=test_db)
    
    repertoires = get_repertoires_by_user(username, db_path=test_db)
    assert len(repertoires) == 1
    assert repertoires[0]['pgn_content'] == PGN2
    assert repertoires[0]['filename'] == "f2.pgn"

def test_delete_repertoire(test_db):
    """Test deleting a repertoire."""
    username = "testuser"
    save_repertoire(username, "white", "f1.pgn", "...", db_path=test_db)
    
    delete_repertoire(username, "white", db_path=test_db)
    
    repertoires = get_repertoires_by_user(username, db_path=test_db)
    assert len(repertoires) == 0
