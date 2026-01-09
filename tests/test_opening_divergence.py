"""
Tests for the opening divergence detection function.
"""

import pytest
import chess
import chess.pgn
import io
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.pgn_tree_parser import (
    PGNTree,
    parse_pgn_string_to_tree,
    find_divergence_point,
)


class TestFindDivergencePoint:
    """Tests for the find_divergence_point function."""
    
    def test_exact_match(self):
        """Test when game exactly matches opening."""
        opening_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
        game_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0"
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence = find_divergence_point(game_tree, opening_tree)
        # Should return empty list if game matches opening completely
        assert divergence == []
    
    def test_divergence_at_first_move(self):
        """Test when game diverges immediately."""
        opening_pgn = "1. e4"
        game_pgn = "1. d4 1-0"
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence = find_divergence_point(game_tree, opening_tree)
        assert divergence == ["1. d4"]
    
    def test_divergence_after_several_moves(self):
        """Test when game diverges after following opening for several moves."""
        opening_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
        game_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bc4 1-0"  # Bc4 instead of Bb5
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence = find_divergence_point(game_tree, opening_tree)
        # Should return path up to and including Bc4 with move numbers
        assert divergence == ["1. e4", "1... e5", "2. Nf3", "2... Nc6", "3. Bc4"]
    
    def test_game_is_longer_than_opening(self):
        """Test when game continues beyond opening."""
        opening_pgn = "1. e4 e5 2. Nf3"
        game_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0"
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence = find_divergence_point(game_tree, opening_tree)
        # Opening ends at 2. Nf3, so game diverges at 2... Nc6 (not in opening tree)
        assert divergence == ["1. e4", "1... e5", "2. Nf3", "2... Nc6"]
    
    def test_opening_has_variations(self):
        """Test when opening has variations and game follows one."""
        # Opening with variation: e4 e5 Nf3, with alternative Nc6
        opening_pgn = "1. e4 e5 2. Nf3"
        game_pgn = "1. e4 e5 2. Nf3 Nc6 1-0"
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence = find_divergence_point(game_tree, opening_tree)
        # Opening ends at 2. Nf3, so game diverges at 2... Nc6 (not in opening tree)
        assert divergence == ["1. e4", "1... e5", "2. Nf3", "2... Nc6"]
    
    def test_complete_mismatch(self):
        """Test when game has no moves in common with opening."""
        opening_pgn = "1. e4 e5"
        game_pgn = "1. d4 d5 1-0"
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence = find_divergence_point(game_tree, opening_tree)
        assert divergence == ["1. d4"]
    
    def test_empty_opening_tree(self):
        """Test when opening tree is empty."""
        opening_pgn = ""
        game_pgn = "1. e4 e5 1-0"
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence = find_divergence_point(game_tree, opening_tree)
        assert divergence == ["1. e4"]
    
    def test_empty_game_tree(self):
        """Test when game tree is empty."""
        opening_pgn = "1. e4 e5"
        game_pgn = ""
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence = find_divergence_point(game_tree, opening_tree)
        assert divergence == []
    
    def test_complex_opening_with_multiple_lines(self):
        """Test with a more complex opening that has multiple lines."""
        # Ruy Lopez opening
        opening_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4"
        # Game follows opening then diverges
        game_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Bxc6 1-0"
        
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        
        divergence = find_divergence_point(game_tree, opening_tree)
        # Should show divergence at Bxc6 (instead of Ba4) with move numbers
        assert "4. Bxc6" in divergence
        assert len(divergence) == 7  # ["1. e4", "1... e5", "2. Nf3", "2... Nc6", "3. Bb5", "3... a6", "4. Bxc6"]
        assert divergence == ["1. e4", "1... e5", "2. Nf3", "2... Nc6", "3. Bb5", "3... a6", "4. Bxc6"]

    def test_opening_with_explicit_variation_game_main(self):
        """Game follows the main line despite variations in the opening."""
        opening_pgn = "1. e4 e5 2. Nf3 Nc6 (2... Nf6 3. Nxe5 Nxe4) 3. Bb5"
        game_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0"
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        divergence = find_divergence_point(game_tree, opening_tree)
        assert divergence == []

    def test_opening_with_explicit_variation_game_branch(self):
        """Game follows the variation - should not count as divergence."""
        opening_pgn = "1. e4 e5 2. Nf3 Nc6 (2... Nf6 3. Nxe5 Nxe4) 3. Bb5"
        game_pgn = "1. e4 e5 2. Nf3 Nf6 3. Nxe5 Nxe4 1-0"
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        divergence = find_divergence_point(game_tree, opening_tree)
        assert divergence == []

    def test_opening_with_deep_variation_game_takes_var(self):
        """Game takes a variation at a deep node."""
        opening_pgn = "1. e4 e5 2. Nf3 Nc6 (2... Nf6 3. Nxe5 Nxe4 (3... d6 4. Nf3 Be7)) 3. Bb5"
        game_pgn = "1. e4 e5 2. Nf3 Nf6 3. Nxe5 Nxe4 3... d6 4. Nf3 Be7 1-0"
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        divergence = find_divergence_point(game_tree, opening_tree)
        assert divergence == []  # No divergence, game is in the opening tree

    def test_opening_with_variation_game_diverges(self):
        """Game diverges from all defined lines."""
        opening_pgn = "1. e4 e5 2. Nf3 Nc6 (2... Nf6 3. Nxe5 Nxe4) 3. Bb5"
        game_pgn = "1. e4 e5 2. Nf3 d6 3. d4 1-0"  # d6 not in any opening branch
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        game_tree = parse_pgn_string_to_tree(game_pgn)
        divergence = find_divergence_point(game_tree, opening_tree)
        assert divergence == ["1. e4", "1... e5", "2. Nf3", "2... d6"]
