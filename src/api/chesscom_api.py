"""
Chess.com API integration for fetching games.
"""

import requests
from typing import List, Dict, Optional, Union
from datetime import datetime


def get_games_from_chesscom(
    username: str,
    year: str,
    month: Union[str, List[str]]
) -> List[Dict]:
    """
    Fetch games from Chess.com API for a given username, year, and month(s).
    
    Args:
        username: Chess.com username
        year: Year in format "YYYY" (e.g., "2024")
        month: Month in format "MM" (e.g., "01") or list of months ["01", "02"]
        
    Returns:
        List[Dict]: List of game dictionaries, each containing game data including PGN
        
    Raises:
        Exception: If API request fails or returns an error
        
    Example:
        >>> games = get_games_from_chesscom("magnuscarlsen", "2024", "01")
        >>> print(f"Found {len(games)} games")
    """
    games = []
    
    # Handle single month or list of months
    months = [month] if isinstance(month, str) else month
    
    for month_str in months:
        # Construct API URL for the specific month
        url = f"https://api.chess.com/pub/player/{username}/games/{year}/{month_str}"
        
        try:
            header = requests.get('https://api.chess.com/context/Match.jsonld')
            response = requests.get(url, timeout=10, headers=header)
            response.raise_for_status()
            
            data = response.json()
            month_games = data.get("games", [])
            games.extend(month_games)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching games from Chess.com API: {e}")
        except (KeyError, ValueError) as e:
            raise Exception(f"Error parsing API response: {e}")
    
    return games


def get_user_games(
    username: str,
    year: Optional[str] = None,
    month: Optional[Union[str, List[str]]] = None
) -> List[Dict]:
    """
    Convenience function to get games for a user.
    
    If year and month are not specified, fetches games from all available archives.
    If only year is specified, fetches all months for that year.
    If both are specified, fetches games for that specific month(s).
    
    Args:
        username: Chess.com username
        year: Optional year in format "YYYY" (e.g., "2024")
        month: Optional month in format "MM" (e.g., "01") or list of months
        
    Returns:
        List[Dict]: List of game dictionaries, each containing game data including PGN
        
    Example:
        >>> # Get all games
        >>> games = get_user_games("magnuscarlsen")
        >>> 
        >>> # Get games for specific month
        >>> games = get_user_games("magnuscarlsen", year="2024", month="01")
        >>> 
        >>> # Get games for multiple months
        >>> games = get_user_games("magnuscarlsen", year="2024", month=["01", "02"])
    """
    if year is None and month is None:
        # Get all available archives
        return get_all_user_games(username)
    elif year is not None and month is None:
        # Get all months for the year
        months = [f"{i:02d}" for i in range(1, 13)]
        return get_games_from_chesscom(username, year, months)
    elif year is not None and month is not None:
        # Get specific month(s)
        return get_games_from_chesscom(username, year, month)
    else:
        raise ValueError("If month is specified, year must also be specified")


def get_all_user_games(username: str) -> List[Dict]:
    """
    Fetch all available games for a user from Chess.com API.
    
    This function first retrieves the list of archive URLs (one per month)
    and then fetches games from each archive.
    
    Args:
        username: Chess.com username
        
    Returns:
        List[Dict]: List of game dictionaries, each containing game data including PGN
        
    Raises:
        Exception: If API request fails or returns an error
        
    Example:
        >>> games = get_all_user_games("magnuscarlsen")
        >>> print(f"Found {len(games)} total games")
    """
    # First, get the list of archive URLs
    archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    
    try:
        response = requests.get(archives_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        archive_urls = data.get("archives", [])
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching archives from Chess.com API: {e}")
    except (KeyError, ValueError) as e:
        raise Exception(f"Error parsing archives response: {e}")
    
    # Fetch games from each archive
    all_games = []
    
    for archive_url in archive_urls:
        try:
            response = requests.get(archive_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            games = data.get("games", [])
            all_games.extend(games)
            
        except requests.exceptions.RequestException as e:
            # Log error but continue with other archives
            print(f"Warning: Error fetching games from {archive_url}: {e}")
            continue
        except (KeyError, ValueError) as e:
            print(f"Warning: Error parsing games from {archive_url}: {e}")
            continue
    
    return all_games
