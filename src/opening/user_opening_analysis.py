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
