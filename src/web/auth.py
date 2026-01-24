import requests
import logging

logger = logging.getLogger(__name__)

def verify_chess_user(username: str):
    """
    Verifies if a Chess.com user exists and returns their profile info.
    """
    username = username.lower().strip()
    url = f"https://api.chess.com/pub/player/{username}"
    # Including contact info as per Chess.com API guidelines
    headers = {"User-Agent": "ChessOpeningAnalysisWeb/1.0 (contact: github.com/michaelsok/opening)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logger.warning(f"Chess.com user {username} not found (404)")
            return None
        elif response.status_code == 429:
            logger.error(f"Chess.com API rate limit hit (429) while verifying {username}")
            return {"error": "rate_limit"}
        else:
            logger.warning(f"Chess.com API returned {response.status_code} for user {username}")
            return None
    except Exception as e:
        logger.error(f"Error verifying Chess.com user {username}: {e}")
        return None
