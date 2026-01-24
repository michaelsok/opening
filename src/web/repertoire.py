import os
import logging
import re
from pathlib import Path
from src.opening.repertoire_manager import split_repertoire_by_opening
from src.web.database import save_repertoire

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("src/web/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def handle_repertoire_upload(username: str, file_content: bytes, filename: str, color: str = 'white'):
    """
    Saves the uploaded PGN to disk, database and splits it into categorized openings.
    Ensures the username is sanitized to prevent directory traversal.
    """
    # Sanitize username (alphanumeric, underscores, hyphens only)
    safe_username = re.sub(r'[^a-zA-Z0-9_\-]', '', username)
    if not safe_username:
        return {"status": "error", "message": "Invalid username"}

    # Save to database
    try:
        pgn_str = file_content.decode('utf-8', errors='replace')
        save_repertoire(username, color.lower(), filename, pgn_str)
    except Exception as e:
        logger.error(f"Failed to save repertoire to database for {username}: {e}")
        # We'll continue with disk saving for now to maintain existing functionality
        # but in a stricter system, we might want to fail here.

    # Use color-specific directory
    user_upload_dir = UPLOAD_DIR / safe_username / color.lower()
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Use a fixed filename instead of user-provided filename to prevent path traversal
    source_pgn_path = user_upload_dir / f"repertoire_{color.lower()}.pgn"
    with open(source_pgn_path, "wb") as f:
        f.write(file_content)
    
    split_dir = user_upload_dir / "split"
    split_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        categories = split_repertoire_by_opening(str(source_pgn_path), str(split_dir))
        return {
            "status": "success",
            "categories": categories,
            "filename": filename
        }
    except Exception as e:
        logger.error(f"Failed to split repertoire for {username}: {e}")
        return {"status": "error", "message": str(e)}
