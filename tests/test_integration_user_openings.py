"""
Integration test: get all user games & divergence with a set of opening PGNs.
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, Mock
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.pgn_tree_parser import (
    parse_pgn_string_to_tree,
    find_first_divergence_across_openings,
)
from src.api.chesscom_api import (
    get_user_games,
)
from src.opening.user_opening_analysis import analyze_user_games_divergence

def write_tmp_opening_pgns(dirpath, pgns):
    files = []
    for idx, pgncontent in enumerate(pgns):
        fname = dirpath / f"opening{idx+1}.pgn"
        with open(fname, "w") as f:
            f.write(pgncontent)
        files.append(fname)
    return files

@patch('src.opening.user_opening_analysis.get_user_games')
def test_integration_user_games_divergence(mock_get_games):
    # Setup: create fake opening PGNs (main and with variation)
    opening_simple = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
    opening_var = "1. e4 e5 2. Nf3 Nc6 (2... Nf6 3. Nxe5 Nxe4) 3. Bb5"
    # Prepare directory
    with tempfile.TemporaryDirectory() as d:
        dpath = Path(d)
        write_tmp_opening_pgns(dpath, [opening_simple, opening_var])
        # Prep fake games (PGN strings returned as if from API)
        mock_get_games.return_value = [
            {"pgn": "1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0", "url": "g1"},
            {"pgn": "1. e4 e5 2. Nf3 Nf6 3. Nxe5 Nxe4 1-0", "url": "g2"},
            {"pgn": "1. d4 d5 2. c4 c6 1-0", "url": "g3"},
        ]
        # Do full analysis
        result = analyze_user_games_divergence("testuser", dpath)
        # Each returned item: {"url": ..., "divergence": [...], "opening_idx": ..., "pgn": ...}
        assert len(result) == 3
        # The first matches mainline
        assert result[0]["divergence"] == []
        assert result[0]["opening_idx"] == 0
        # The second matches variation in opening_var
        assert result[1]["divergence"] == []
        assert result[1]["opening_idx"] == 1
        # The third matches neither
        assert result[2]["divergence"] == ['1. d4']
        assert result[2]["opening_idx"] is None
