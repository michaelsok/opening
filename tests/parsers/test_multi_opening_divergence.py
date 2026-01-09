"""
Tests for finding divergence point from multiple opening PGN files.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.parsers.pgn_tree_parser import (
    parse_pgn_string_to_tree,
    find_divergence_point,
    find_first_divergence_across_openings,
)


class TestMultiOpeningDivergence:
    def test_matches_first_opening(self):
        game_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0"
        opening1 = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
        opening2 = "1. d4 d5 2. c4 c6"
        trees = [parse_pgn_string_to_tree(opening1), parse_pgn_string_to_tree(opening2)]
        game_tree = parse_pgn_string_to_tree(game_pgn)
        divergence, idx = find_first_divergence_across_openings(game_tree, trees)
        assert divergence == []
        assert idx == 0  # matched first opening

    def test_matches_second_opening(self):
        game_pgn = "1. d4 d5 2. c4 c6 1-0"
        opening1 = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
        opening2 = "1. d4 d5 2. c4 c6"
        trees = [parse_pgn_string_to_tree(opening1), parse_pgn_string_to_tree(opening2)]
        game_tree = parse_pgn_string_to_tree(game_pgn)
        divergence, idx = find_first_divergence_across_openings(game_tree, trees)
        assert divergence == []
        assert idx == 1  # matched second opening

    def test_no_match_in_any_opening(self):
        game_pgn = "1. Nf3 d5 1-0"
        opening1 = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
        opening2 = "1. d4 d5 2. c4 c6"
        trees = [parse_pgn_string_to_tree(opening1), parse_pgn_string_to_tree(opening2)]
        game_tree = parse_pgn_string_to_tree(game_pgn)
        divergence, idx = find_first_divergence_across_openings(game_tree, trees)
        assert divergence == ["1. Nf3"]
        assert idx is None

    def test_matches_variation_in_opening(self):
        game_pgn = "1. e4 e5 2. Nf3 Nf6 3. Nxe5 Nxe4 1-0"
        opening1 = "1. e4 e5 2. Nf3 Nc6"
        opening2 = "1. e4 e5 2. Nf3 Nc6 (2... Nf6 3. Nxe5 Nxe4) 3. Bb5"
        trees = [parse_pgn_string_to_tree(opening1), parse_pgn_string_to_tree(opening2)]
        game_tree = parse_pgn_string_to_tree(game_pgn)
        divergence, idx = find_first_divergence_across_openings(game_tree, trees)
        assert divergence == []  # exact in variation
        assert idx == 1

    def test_matches_none_due_to_deep_divergence(self):
        game_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bc4 1-0"
        opening1 = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
        opening2 = "1. d4 d5 2. c4 c6"
        trees = [parse_pgn_string_to_tree(opening1), parse_pgn_string_to_tree(opening2)]
        game_tree = parse_pgn_string_to_tree(game_pgn)
        divergence, idx = find_first_divergence_across_openings(game_tree, trees)
        assert divergence == ["1. e4", "1... e5", "2. Nf3", "2... Nc6", "3. Bc4"]
        assert idx is None
