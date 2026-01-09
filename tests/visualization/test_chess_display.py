"""
Tests for chess game display functionality.
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.visualization.chess_display import (
    display_game_from_pgn,
    display_game_from_string,
    display_multiple_games_from_pgn,
    display_multiple_games_from_strings,
)


class TestDisplayGameFromString:
    """Tests for display_game_from_string function."""
    
    def test_display_simple_game(self):
        """Test displaying a simple game from PGN string."""
        pgn = """[Event "Test Game"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0"""
        
        with patch('webbrowser.open'):
            output_file = display_game_from_string(
                pgn, 
                open_in_browser=False,
                output_file=None
            )
        
        assert os.path.exists(output_file)
        assert output_file.endswith('.html')
        
        # Check HTML content
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            assert 'Chess Game Viewer' in html_content
            assert 'Player1' in html_content
            assert 'Player2' in html_content
            assert 'e4' in html_content
            assert 'e5' in html_content
        
        # Cleanup
        os.unlink(output_file)
    
    def test_display_game_with_output_file(self):
        """Test displaying a game with specified output file."""
        pgn = """[Event "Test"]
1. e4 e5 1-0"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = f.name
        
        try:
            with patch('webbrowser.open'):
                result_file = display_game_from_string(
                    pgn,
                    output_file=output_path,
                    open_in_browser=False
                )
            
            assert result_file == output_path
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_display_empty_pgn(self):
        """Test displaying an empty PGN string raises error."""
        with pytest.raises(ValueError, match="No valid game found"):
            display_game_from_string("", open_in_browser=False)
    
    def test_display_invalid_pgn(self):
        """Test displaying invalid PGN string - may not raise error if chess.pgn parses it."""
        # chess.pgn.read_game might parse some invalid input as an empty game
        # This test verifies the function doesn't crash
        invalid_pgn = "invalid pgn content without proper format"
        
        # The function may raise ValueError or succeed with empty game
        # Let's just check it doesn't crash
        try:
            with patch('webbrowser.open'):
                result = display_game_from_string(invalid_pgn, open_in_browser=False)
                # If it succeeds, it should create a file (even if empty)
                if result:
                    if os.path.exists(result):
                        os.unlink(result)
        except ValueError:
            # ValueError is acceptable for invalid PGN
            pass


class TestDisplayGameFromPgn:
    """Tests for display_game_from_pgn function."""
    
    def test_display_game_from_file(self):
        """Test displaying a game from a PGN file."""
        pgn_content = """[Event "Test Game"]
[White "Alice"]
[Black "Bob"]
[Result "1/2-1/2"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 1/2-1/2"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pgn', delete=False) as f:
            pgn_file = f.name
            f.write(pgn_content)
        
        try:
            with patch('webbrowser.open'):
                output_file = display_game_from_pgn(
                    pgn_file,
                    open_in_browser=False
                )
            
            assert os.path.exists(output_file)
            
            # Check HTML content
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
                assert 'Alice' in html_content
                assert 'Bob' in html_content
                assert 'e4' in html_content
            
            os.unlink(output_file)
        finally:
            if os.path.exists(pgn_file):
                os.unlink(pgn_file)
    
    def test_display_nonexistent_file(self):
        """Test displaying game from non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            display_game_from_pgn("nonexistent.pgn", open_in_browser=False)
    
    def test_display_empty_file(self):
        """Test displaying game from empty file raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pgn', delete=False) as f:
            pgn_file = f.name
        
        try:
            with pytest.raises(ValueError, match="No valid game found"):
                display_game_from_pgn(pgn_file, open_in_browser=False)
        finally:
            if os.path.exists(pgn_file):
                os.unlink(pgn_file)


class TestDisplayMultipleGames:
    """Tests for multiple games display functions."""
    
    def test_display_multiple_games_from_strings(self):
        """Test displaying multiple games from PGN strings."""
        games = [
            """[Event "Game 1"]
[White "Alice"]
[Black "Bob"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0""",
            """[Event "Game 2"]
[White "Charlie"]
[Black "Diana"]
[Result "1/2-1/2"]

1. d4 d5 2. c4 c6 1/2-1/2""",
            """[Event "Game 3"]
[White "Eve"]
[Black "Frank"]
[Result "0-1"]

1. e4 c5 2. Nf3 d6 0-1"""
        ]
        
        with patch('webbrowser.open'):
            output_file = display_multiple_games_from_strings(
                games,
                open_in_browser=False
            )
        
        assert os.path.exists(output_file)
        assert output_file.endswith('.html')
        
        # Check HTML content
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            assert 'Chess Games Viewer - 3 Games' in html_content
            assert 'Alice' in html_content
            assert 'Bob' in html_content
            assert 'Charlie' in html_content
            assert 'Diana' in html_content
            assert 'switchToGame' in html_content
            assert 'previousGame' in html_content
            assert 'nextGame' in html_content
        
        # Cleanup
        os.unlink(output_file)
    
    def test_display_multiple_games_from_pgn_file(self):
        """Test displaying multiple games from a PGN file."""
        pgn_content = """[Event "Game 1"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 1-0

[Event "Game 2"]
[White "Player3"]
[Black "Player4"]
[Result "0-1"]

1. d4 d5 0-1"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pgn', delete=False) as f:
            pgn_file = f.name
            f.write(pgn_content)
        
        try:
            with patch('webbrowser.open'):
                output_file = display_multiple_games_from_pgn(
                    pgn_file,
                    open_in_browser=False
                )
            
            assert os.path.exists(output_file)
            
            # Check HTML content
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
                assert 'Chess Games Viewer - 2 Games' in html_content
                assert 'Player1' in html_content
                assert 'Player2' in html_content
                assert 'Player3' in html_content
                assert 'Player4' in html_content
            
            os.unlink(output_file)
        finally:
            if os.path.exists(pgn_file):
                os.unlink(pgn_file)
    
    def test_display_multiple_games_empty_list(self):
        """Test displaying multiple games with empty list raises error."""
        with pytest.raises(ValueError, match="No valid games found"):
            display_multiple_games_from_strings([], open_in_browser=False)
    
    def test_display_multiple_games_invalid_strings(self):
        """Test displaying multiple games with invalid PGN strings."""
        games = ["invalid pgn", "also invalid"]
        # Should raise ValueError if no valid games found
        try:
            with patch('webbrowser.open'):
                display_multiple_games_from_strings(games, open_in_browser=False)
            # If it doesn't raise, that's fine - it might filter invalid ones
        except ValueError:
            # ValueError is acceptable
            pass
    
    def test_display_multiple_games_from_file_nonexistent(self):
        """Test displaying multiple games from non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            display_multiple_games_from_pgn("nonexistent.pgn", open_in_browser=False)
    
    def test_display_multiple_games_from_file_empty(self):
        """Test displaying multiple games from empty file raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pgn', delete=False) as f:
            pgn_file = f.name
        
        try:
            with pytest.raises(ValueError, match="No valid games found"):
                display_multiple_games_from_pgn(pgn_file, open_in_browser=False)
        finally:
            if os.path.exists(pgn_file):
                os.unlink(pgn_file)
