"""
Chess.com API integration for fetching games.
"""

import requests
from typing import List, Dict, Optional, Union
from datetime import datetime


def _filter_game(
    game: Dict,
    username: str,
    time_control: Optional[str] = None,
    time_class: Optional[str] = None,
    color: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    rated: Optional[bool] = None,
    rules: Optional[str] = None
) -> bool:
    """
    Check if a game matches the specified filter criteria.
    
    Args:
        game: Game dictionary from Chess.com API
        username: Username to check color against
        time_control: Filter by time control string (e.g., "600+0")
        time_class: Filter by time class (e.g., "blitz", "bullet", "rapid", "classical")
        color: Filter by color played ("white" or "black")
        start_date: Filter games after this date
        end_date: Filter games before this date
        rated: Filter by rated status (True for rated, False for unrated)
        rules: Filter by rules/variant (e.g., "chess", "chess960")
        
    Returns:
        bool: True if game matches all filters, False otherwise
    """
    # Filter by time control string
    if time_control is not None:
        if game.get("time_control") != time_control:
            return False
    
    # Filter by time class
    if time_class is not None:
        if game.get("time_class") != time_class:
            return False
    
    # Filter by color (white or black)
    if color is not None:
        color_lower = color.lower()
        if color_lower not in ["white", "black"]:
            raise ValueError(f"color must be 'white' or 'black', got '{color}'")
        
        # Get username from white or black player dict
        white_username = game.get("white", {}).get("username", "").lower() if isinstance(game.get("white"), dict) else ""
        black_username = game.get("black", {}).get("username", "").lower() if isinstance(game.get("black"), dict) else ""
        
        # Also check PGN headers as fallback
        pgn = game.get("pgn", "")
        if not white_username and "[White" in pgn:
            for line in pgn.split("\n"):
                if line.startswith("[White"):
                    white_username = line.split('"')[1].lower() if '"' in line else ""
                    break
        if not black_username and "[Black" in pgn:
            for line in pgn.split("\n"):
                if line.startswith("[Black"):
                    black_username = line.split('"')[1].lower() if '"' in line else ""
                    break
        
        username_lower = username.lower()
        if color_lower == "white" and white_username != username_lower:
            return False
        if color_lower == "black" and black_username != username_lower:
            return False
    
    # Filter by date range
    if start_date is not None or end_date is not None:
        end_time = game.get("end_time")
        if end_time is None:
            # Try to parse from PGN or skip
            return False
        
        # Convert timestamp to datetime if needed
        if isinstance(end_time, (int, float)):
            game_date = datetime.fromtimestamp(end_time)
        else:
            return False
        
        if start_date is not None and game_date < start_date:
            return False
        if end_date is not None and game_date > end_date:
            return False
    
    # Filter by rated status
    if rated is not None:
        if game.get("rated") != rated:
            return False
    
    # Filter by rules/variant
    if rules is not None:
        if game.get("rules") != rules:
            return False
    
    return True


def _apply_filters(
    games: List[Dict],
    username: str,
    **filter_kwargs
) -> List[Dict]:
    """
    Apply filters to a list of games.
    
    Args:
        games: List of game dictionaries
        username: Username for color filtering
        **filter_kwargs: Filter parameters (time_control, time_class, color, etc.)
        
    Returns:
        List[Dict]: Filtered list of games
    """
    if not filter_kwargs:
        return games
    
    filtered_games = []
    for game in games:
        if _filter_game(game, username, **filter_kwargs):
            filtered_games.append(game)
    
    return filtered_games


def get_games_from_chesscom(
    username: str,
    year: str,
    month: Union[str, List[str]],
    time_control: Optional[str] = None,
    time_class: Optional[str] = None,
    color: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    rated: Optional[bool] = None,
    rules: Optional[str] = None
) -> List[Dict]:
    """
    Fetch games from Chess.com API for a given username, year, and month(s).
    
    Args:
        username: Chess.com username
        year: Year in format "YYYY" (e.g., "2024")
        month: Month in format "MM" (e.g., "01") or list of months ["01", "02"]
        time_control: Filter by time control string (e.g., "600+0")
        time_class: Filter by time class (e.g., "blitz", "bullet", "rapid", "classical")
        color: Filter by color played ("white" or "black")
        start_date: Filter games after this date (datetime object)
        end_date: Filter games before this date (datetime object)
        rated: Filter by rated status (True for rated, False for unrated)
        rules: Filter by rules/variant (e.g., "chess", "chess960")
        
    Returns:
        List[Dict]: List of filtered game dictionaries, each containing game data including PGN
        
    Raises:
        Exception: If API request fails or returns an error
        ValueError: If invalid filter values are provided
        
    Example:
        >>> games = get_games_from_chesscom("magnuscarlsen", "2024", "01")
        >>> print(f"Found {len(games)} games")
        >>> 
        >>> # Filter by time class and color
        >>> blitz_as_white = get_games_from_chesscom(
        ...     "magnuscarlsen", "2024", "01",
        ...     time_class="blitz", color="white"
        ... )
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
    
    # Apply filters
    filter_kwargs = {
        "time_control": time_control,
        "time_class": time_class,
        "color": color,
        "start_date": start_date,
        "end_date": end_date,
        "rated": rated,
        "rules": rules
    }
    # Remove None values
    filter_kwargs = {k: v for k, v in filter_kwargs.items() if v is not None}
    
    return _apply_filters(games, username, **filter_kwargs)


def get_user_games(
    username: str,
    year: Optional[str] = None,
    month: Optional[Union[str, List[str]]] = None,
    time_control: Optional[str] = None,
    time_class: Optional[str] = None,
    color: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    rated: Optional[bool] = None,
    rules: Optional[str] = None
) -> List[Dict]:
    """
    Convenience function to get games for a user with optional filters.
    
    If year and month are not specified, fetches games from all available archives.
    If only year is specified, fetches all months for that year.
    If both are specified, fetches games for that specific month(s).
    
    Args:
        username: Chess.com username
        year: Optional year in format "YYYY" (e.g., "2024")
        month: Optional month in format "MM" (e.g., "01") or list of months
        time_control: Filter by time control string (e.g., "600+0")
        time_class: Filter by time class (e.g., "blitz", "bullet", "rapid", "classical")
        color: Filter by color played ("white" or "black")
        start_date: Filter games after this date (datetime object)
        end_date: Filter games before this date (datetime object)
        rated: Filter by rated status (True for rated, False for unrated)
        rules: Filter by rules/variant (e.g., "chess", "chess960")
        
    Returns:
        List[Dict]: List of filtered game dictionaries, each containing game data including PGN
        
    Example:
        >>> # Get all games
        >>> games = get_user_games("magnuscarlsen")
        >>> 
        >>> # Get games for specific month with filters
        >>> games = get_user_games(
        ...     "magnuscarlsen", year="2024", month="01",
        ...     time_class="blitz", color="white", rated=True
        ... )
        >>> 
        >>> # Get games for multiple months with date filter
        >>> from datetime import datetime
        >>> games = get_user_games(
        ...     "magnuscarlsen", year="2024", month=["01", "02"],
        ...     start_date=datetime(2024, 1, 15),
        ...     end_date=datetime(2024, 2, 15)
        ... )
    """
    # Prepare filter kwargs (only include non-None values)
    filter_kwargs = {}
    if time_control is not None:
        filter_kwargs["time_control"] = time_control
    if time_class is not None:
        filter_kwargs["time_class"] = time_class
    if color is not None:
        filter_kwargs["color"] = color
    if start_date is not None:
        filter_kwargs["start_date"] = start_date
    if end_date is not None:
        filter_kwargs["end_date"] = end_date
    if rated is not None:
        filter_kwargs["rated"] = rated
    if rules is not None:
        filter_kwargs["rules"] = rules
    
    if year is None and month is None:
        # Get all available archives
        return get_all_user_games(username, **filter_kwargs)
    elif year is not None and month is None:
        # Get all months for the year
        months = [f"{i:02d}" for i in range(1, 13)]
        return get_games_from_chesscom(username, year, months, **filter_kwargs)
    elif year is not None and month is not None:
        # Get specific month(s)
        return get_games_from_chesscom(username, year, month, **filter_kwargs)
    else:
        raise ValueError("If month is specified, year must also be specified")


def get_all_user_games(
    username: str,
    time_control: Optional[str] = None,
    time_class: Optional[str] = None,
    color: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    rated: Optional[bool] = None,
    rules: Optional[str] = None
) -> List[Dict]:
    """
    Fetch all available games for a user from Chess.com API with optional filters.
    
    This function first retrieves the list of archive URLs (one per month)
    and then fetches games from each archive, applying filters.
    
    Args:
        username: Chess.com username
        time_control: Filter by time control string (e.g., "600+0")
        time_class: Filter by time class (e.g., "blitz", "bullet", "rapid", "classical")
        color: Filter by color played ("white" or "black")
        start_date: Filter games after this date (datetime object)
        end_date: Filter games before this date (datetime object)
        rated: Filter by rated status (True for rated, False for unrated)
        rules: Filter by rules/variant (e.g., "chess", "chess960")
        
    Returns:
        List[Dict]: List of filtered game dictionaries, each containing game data including PGN
        
    Raises:
        Exception: If API request fails or returns an error
        ValueError: If invalid filter values are provided
        
    Example:
        >>> games = get_all_user_games("magnuscarlsen")
        >>> print(f"Found {len(games)} total games")
        >>> 
        >>> # Get only blitz games as white
        >>> blitz_white = get_all_user_games(
        ...     "magnuscarlsen",
        ...     time_class="blitz", color="white"
        ... )
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
    
    # Apply filters (only include non-None values)
    filter_kwargs = {}
    if time_control is not None:
        filter_kwargs["time_control"] = time_control
    if time_class is not None:
        filter_kwargs["time_class"] = time_class
    if color is not None:
        filter_kwargs["color"] = color
    if start_date is not None:
        filter_kwargs["start_date"] = start_date
    if end_date is not None:
        filter_kwargs["end_date"] = end_date
    if rated is not None:
        filter_kwargs["rated"] = rated
    if rules is not None:
        filter_kwargs["rules"] = rules
    
    return _apply_filters(all_games, username, **filter_kwargs)
