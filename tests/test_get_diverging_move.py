"""
Tests for the get_diverging_move function.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.pgn_tree_parser import (
    PGNTree,
    parse_pgn_string_to_tree,
    find_divergence_point,
    get_diverging_move,
)


class TestGetDivergingMove:
    """Tests for the get_diverging_move function."""
    
    def test_no_divergence(self):
        """Test when game matches opening completely."""
        opening_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
        game_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0"
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence_point = find_divergence_point(game_tree, opening_tree)
        diverging_move = get_diverging_move(divergence_point, game_tree)
        
        assert diverging_move is None
    
    def test_divergence_at_first_move(self):
        """Test when game diverges at first move."""
        opening_pgn = "1. e4"
        game_pgn = "1. d4 1-0"
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence_point = find_divergence_point(game_tree, opening_tree)
        diverging_move = get_diverging_move(divergence_point, game_tree)
        
        assert diverging_move == "1. d4"
    
    def test_divergence_after_several_moves(self):
        """Test when game diverges after following opening."""
        opening_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
        game_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bc4 1-0"  # Bc4 instead of Bb5
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence_point = find_divergence_point(game_tree, opening_tree)
        diverging_move = get_diverging_move(divergence_point, game_tree)
        
        # Should return only the diverging move (Bc4)
        assert diverging_move == "3. Bc4"
    
    def test_game_continues_beyond_opening(self):
        """Test when game continues beyond opening (not a true divergence)."""
        opening_pgn = "1. e4 e5 2. Nf3"
        game_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0"
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence_point = find_divergence_point(game_tree, opening_tree)
        diverging_move = get_diverging_move(divergence_point, game_tree)
        
        # Opening ends, so first move after opening is the divergence
        assert diverging_move == "2... Nc6"
    
    def test_complete_mismatch(self):
        """Test when game has no moves in common with opening."""
        opening_pgn = "1. e4 e5"
        game_pgn = "1. d4 d5 1-0"
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence_point = find_divergence_point(game_tree, opening_tree)
        diverging_move = get_diverging_move(divergence_point, game_tree)
        
        assert diverging_move == "1. d4"
    
    def test_empty_divergence_point(self):
        """Test when divergence point is empty."""
        game_pgn = "1. e4 e5 1-0"
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence_point = []
        diverging_move = get_diverging_move(divergence_point, game_tree)
        
        assert diverging_move is None
    
    def test_divergence_at_black_move(self):
        """Test when divergence happens at a black move."""
        opening_pgn = "1. e4 e5 2. Nf3"
        game_pgn = "1. e4 c5 2. Nf3 1-0"  # c5 instead of e5
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence_point = find_divergence_point(game_tree, opening_tree)
        diverging_move = get_diverging_move(divergence_point, game_tree)
        
        assert diverging_move == "1... c5"
    
    def test_complex_divergence(self):
        """Test with a complex divergence scenario."""
        opening_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4"
        game_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Bxc6 1-0"
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence_point = find_divergence_point(game_tree, opening_tree)
        diverging_move = get_diverging_move(divergence_point, game_tree)
        
        # Should return only the diverging move
        assert diverging_move == "4. Bxc6"
