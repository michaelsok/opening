import requests
import logging

logger = logging.getLogger(__name__)

def verify_chess_user(username: str):
    """
    Verifies if a Chess.com user exists and returns their profile info.
    """
    url = f"https://api.chess.com/pub/player/{username}"
    headers = {"User-Agent": "ChessOpeningAnalysisWeb/1.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Chess.com user {username} not found or API error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error verifying Chess.com user {username}: {e}")
        return None
