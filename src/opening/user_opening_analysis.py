"""
Analysis: Compare user games with openings from a directory and compute divergences.
"""
import os
from pathlib import Path
from typing import List, Dict, Union
from src.parsers.pgn_tree_parser import (
    parse_pgn_string_to_tree,
    find_first_divergence_across_openings,
)
from src.api.chesscom_api import get_user_games
from src.visualization.chess_display import create_index_html


def analyze_user_games_divergence(
    username: str,
    opening_dir: Union[str, Path],
    year: str = None,
    month: Union[str, List[str]] = None
) -> List[Dict]:
    """
    Loads openings from a directory; fetches all (optionally filtered) games; matches games to best opening and divergence point.
    Args:
        username: Chess.com username
        opening_dir: Path to directory containing PGN files (openings)
        year: Optional, for fetching only a specific year
        month: Optional, for fetching a specific month or list of months
    Returns:
        List[{"url": str, "divergence": List[str], "opening_idx": int or None, "pgn": str}]
    """
    opening_dir = Path(opening_dir)
    opening_trees = []
    for file in opening_dir.iterdir():
        if file.is_file() and file.suffix.lower() == ".pgn":
            with open(file, encoding="utf-8") as f:
                pgn_str = f.read()
            opening_trees.append(parse_pgn_string_to_tree(pgn_str))
    games = get_user_games(username, year, month)
    result = []
    for game in games:
        pgn = game.get("pgn", "")
        url = game.get("url", None)
        if not pgn:
            continue
        game_tree = parse_pgn_string_to_tree(pgn)
        divergence, idx = find_first_divergence_across_openings(game_tree, opening_trees)
        result.append({
            "url": url,
            "divergence": divergence,
            "opening_idx": idx,
            "pgn": pgn,
        })
    return result

def analyze_user_openings(
    username: str,
    opening_repertoire: Union[str, Path, List[str]],
    year: str = None,
    month: Union[str, List[str]] = None,
    time_class: str = None,
    color: str = None,
    start_date: 'datetime' = None,
    end_date: 'datetime' = None,
    output_file: Union[str, Path] = None,
    open_in_browser: bool = True,
    size: int = 400,
    template_variant: str = "standard"
) -> str:
    """
    Fetch games from Chess.com and generate an interactive HTML report comparing them
    against an opening repertoire.

    Args:
        username: Chess.com username
        opening_repertoire: Path to directory with PGNs OR list of PGN strings
        year: Optional year filter (e.g., "2024")
        month: Optional month filter (e.g., "01" or ["01", "02"])
        time_class: Optional time class filter (e.g., "blitz", "rapid")
        color: Optional color filter ("white" or "black")
        start_date: Optional start date filter (datetime)
        end_date: Optional end date filter (datetime)
        output_file: Optional path for the generated HTML
        open_in_browser: Whether to automatically open the report
        size: Board size in pixels

    Returns:
        str: Absolute path to the generated index.html
    """
    # Fetch games from Chess.com
    games_data = get_user_games(
        username=username,
        year=year,
        month=month,
        time_class=time_class,
        color=color,
        start_date=start_date,
        end_date=end_date
    )

    # Extract PGN strings
    game_pgns = [game.get("pgn", "") for game in games_data if game.get("pgn")]

    if not game_pgns:
        raise ValueError(f"No games found for user '{username}' with the specified filters.")

    # Pass everything to the visualization tool
    return create_index_html(
        games=game_pgns,
        opening_repertoire=opening_repertoire,
        target_username=username,
        output_file=output_file,
        open_in_browser=open_in_browser,
        size=size,
        template_variant=template_variant
    )
