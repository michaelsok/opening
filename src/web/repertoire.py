import os
import logging
from pathlib import Path
from src.opening.repertoire_manager import split_repertoire_by_opening

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("src/web/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def handle_repertoire_upload(username: str, file_content: bytes, filename: str):
    """
    Saves the uploaded PGN and splits it into categorized openings.
    """
    user_upload_dir = UPLOAD_DIR / username
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    
    source_pgn_path = user_upload_dir / "full_repertoire.pgn"
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
