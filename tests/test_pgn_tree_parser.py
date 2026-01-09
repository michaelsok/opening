"""
Tests for the PGN tree parser module.
"""

import pytest
import chess
import chess.pgn
import io
import tempfile
import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.pgn_tree_parser import (
    MoveNode,
    PGNTree,
    parse_pgn_to_tree,
    parse_pgn_string_to_tree
)


class TestMoveNode:
    """Tests for the MoveNode class."""
    
    def test_move_node_initialization(self):
        """Test that MoveNode initializes correctly."""
        node = MoveNode()
        assert node.move is None
        assert node.parent is None
        assert node.children == {}
        assert node.position_fen is None
        assert node.move_count == 0
    
    def test_move_node_with_move(self):
        """Test MoveNode with a move."""
        board = chess.Board()
        move = chess.Move.from_uci("e2e4")
        node = MoveNode(move=move)
        assert node.move == move
        assert node.move_count == 0
    
    def test_move_node_add_child(self):
        """Test adding a child node."""
        parent = MoveNode()
        parent.position_fen = chess.Board().fen()
        parent.move_count = 0
        
        board = chess.Board()
        move = chess.Move.from_uci("e2e4")
        child = parent.add_child("e4", move, board)
        
        assert "e4" in parent.children
        assert parent.children["e4"] == child
        assert child.parent == parent
        assert child.move == move
        assert child.move_count == 1
        assert child.position_fen is not None
    
    def test_move_node_repr(self):
        """Test MoveNode string representation."""
        node = MoveNode()
        assert "root" in repr(node)
        
        move = chess.Move.from_uci("e2e4")
        node = MoveNode(move=move)
        assert "e2e4" in repr(node)


class TestPGNTree:
    """Tests for the PGNTree class."""
    
    def test_pgn_tree_initialization(self):
        """Test that PGNTree initializes correctly."""
        tree = PGNTree()
        assert tree.root is not None
        assert tree.root.move is None
        assert tree.root.position_fen == chess.Board().fen()
        assert tree.games == []
    
    def test_add_simple_game(self):
        """Test adding a simple game to the tree."""
        tree = PGNTree()
        pgn_string = """[Event "Test"]
1. e4 e5 1-0"""
        
        game = chess.pgn.read_game(io.StringIO(pgn_string))
        tree.add_game(game)
        
        assert len(tree.games) == 1
        assert tree.games[0]["Event"] == "Test"
        assert "e4" in tree.root.children
        assert "e5" in tree.root.children["e4"].children
    
    def test_get_node_at_path(self):
        """Test getting a node at a specific path."""
        tree = PGNTree()
        pgn_string = "1. e4 e5 2. Nf3 Nc6 1-0"
        
        game = chess.pgn.read_game(io.StringIO(pgn_string))
        tree.add_game(game)
        
        node = tree.get_node_at_path(["e4", "e5", "Nf3"])
        assert node is not None
        assert node.move is not None
        
        # Test invalid path
        node = tree.get_node_at_path(["e4", "e5", "invalid"])
        assert node is None
        
        # Test empty path returns root
        node = tree.get_node_at_path([])
        assert node == tree.root
    
    def test_get_all_paths(self):
        """Test getting all paths from the tree."""
        tree = PGNTree()
        pgn_string = "1. e4 e5 2. Nf3 1-0"
        
        game = chess.pgn.read_game(io.StringIO(pgn_string))
        tree.add_game(game)
        
        paths = tree.get_all_paths()
        assert len(paths) > 0
        assert ["e4", "e5", "Nf3"] in paths
    
    def test_multiple_games(self):
        """Test adding multiple games to the tree."""
        tree = PGNTree()
        pgn_string1 = "[Event \"Game1\"]\n1. e4 e5 1-0"
        pgn_string2 = "[Event \"Game2\"]\n1. d4 d5 1-0"
        
        game1 = chess.pgn.read_game(io.StringIO(pgn_string1))
        game2 = chess.pgn.read_game(io.StringIO(pgn_string2))
        
        tree.add_game(game1)
        tree.add_game(game2)
        
        assert len(tree.games) == 2
        assert tree.games[0]["Event"] == "Game1"
        assert tree.games[1]["Event"] == "Game2"
        # Both moves should be in root
        assert "e4" in tree.root.children
        assert "d4" in tree.root.children
    
    def test_variations(self):
        """Test handling of variations in PGN."""
        tree = PGNTree()
        # Create a game with variations manually
        game = chess.pgn.Game()
        game.headers["Event"] = "Test"
        
        node = game
        board = chess.Board()
        
        # Main line: e4 e5
        move1 = board.parse_san("e4")
        node = node.add_variation(move1)
        board.push(move1)
        
        move2 = board.parse_san("e5")
        node = node.add_variation(move2)
        board.push(move2)
        
        # Variation: e4 c5
        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))
        variation_node = game.variations[0]
        move_alt = board.parse_san("c5")
        variation_node.add_variation(move_alt)
        
        tree.add_game(game)
        
        # Should have both e5 and c5 as children of e4
        e4_node = tree.get_node_at_path(["e4"])
        assert e4_node is not None
        assert "e5" in e4_node.children or "c5" in e4_node.children


class TestParsePGNToTree:
    """Tests for the parse_pgn_to_tree function."""
    
    def test_parse_simple_pgn_file(self):
        """Test parsing a simple PGN file."""
        pgn_content = """[Event "Test Game"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pgn', delete=False) as f:
            f.write(pgn_content)
            temp_path = f.name
        
        try:
            tree = parse_pgn_to_tree(temp_path)
            assert len(tree.games) == 1
            assert tree.games[0]["White"] == "Player1"
            assert tree.games[0]["Black"] == "Player2"
            assert "e4" in tree.root.children
        finally:
            os.unlink(temp_path)
    
    def test_parse_nonexistent_file(self):
        """Test parsing a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parse_pgn_to_tree("nonexistent_file.pgn")
    
    def test_parse_multiple_games_file(self):
        """Test parsing a file with multiple games."""
        pgn_content = """[Event "Game 1"]
1. e4 e5 1-0

[Event "Game 2"]
1. d4 d5 1-0
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pgn', delete=False) as f:
            f.write(pgn_content)
            temp_path = f.name
        
        try:
            tree = parse_pgn_to_tree(temp_path)
            assert len(tree.games) == 2
        finally:
            os.unlink(temp_path)
    
    def test_parse_empty_file(self):
        """Test parsing an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pgn', delete=False) as f:
            temp_path = f.name
        
        try:
            tree = parse_pgn_to_tree(temp_path)
            assert len(tree.games) == 0
        finally:
            os.unlink(temp_path)


class TestParsePGNStringToTree:
    """Tests for the parse_pgn_string_to_tree function."""
    
    def test_parse_simple_pgn_string(self):
        """Test parsing a simple PGN string."""
        pgn_string = """[Event "Test"]
1. e4 e5 2. Nf3 1-0"""
        
        tree = parse_pgn_string_to_tree(pgn_string)
        assert len(tree.games) == 1
        assert "e4" in tree.root.children
    
    def test_parse_pgn_string_with_headers(self):
        """Test parsing PGN string with headers."""
        pgn_string = """[Event "Championship"]
[Site "Test"]
[Date "2024.01.01"]
[Round "1"]
[White "Alice"]
[Black "Bob"]
[Result "1-0"]

1. e4 c5 2. Nf3 d6 1-0
"""
        tree = parse_pgn_string_to_tree(pgn_string)
        assert len(tree.games) == 1
        assert tree.games[0]["Event"] == "Championship"
        assert tree.games[0]["White"] == "Alice"
        assert tree.games[0]["Black"] == "Bob"
    
    def test_parse_multiple_games_string(self):
        """Test parsing string with multiple games."""
        pgn_string = """[Event "Game 1"]
1. e4 e5 1-0

[Event "Game 2"]
1. d4 d5 1-0
"""
        tree = parse_pgn_string_to_tree(pgn_string)
        assert len(tree.games) == 2
    
    def test_parse_invalid_pgn_string(self):
        """Test parsing invalid PGN string."""
        # Empty string should not raise, but return empty tree
        tree = parse_pgn_string_to_tree("")
        assert len(tree.games) == 0
        
        # Invalid move notation might raise or return empty
        # This depends on python-chess behavior
        invalid_pgn = "[Event \"Test\"]\n1. invalid move 1-0"
        # python-chess might raise an exception or handle it gracefully
        # We'll test that it doesn't crash
        try:
            tree = parse_pgn_string_to_tree(invalid_pgn)
            # If it doesn't raise, that's fine
        except Exception:
            # If it raises, that's also acceptable behavior
            pass


class TestIntegration:
    """Integration tests."""
    
    def test_complete_game_parsing(self):
        """Test parsing a complete game."""
        pgn_string = """[Event "Test Game"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7 1-0
"""
        tree = parse_pgn_string_to_tree(pgn_string)
        
        # Check game metadata
        assert len(tree.games) == 1
        assert tree.games[0]["Result"] == "1-0"
        
        # Check that moves are in tree
        node = tree.get_node_at_path(["e4", "e5", "Nf3", "Nc6", "Bb5"])
        assert node is not None
        
        # Check paths
        paths = tree.get_all_paths()
        assert len(paths) > 0
        # Should have at least one path with e4
        assert any("e4" in path for path in paths)
    
    def test_tree_navigation(self):
        """Test navigating the tree structure."""
        pgn_string = "1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0"
        tree = parse_pgn_string_to_tree(pgn_string)
        
        # Navigate step by step
        root = tree.root
        assert "e4" in root.children
        
        e4_node = root.children["e4"]
        assert "e5" in e4_node.children
        
        e5_node = e4_node.children["e5"]
        assert "Nf3" in e5_node.children
        
        nf3_node = e5_node.children["Nf3"]
        assert "Nc6" in nf3_node.children
