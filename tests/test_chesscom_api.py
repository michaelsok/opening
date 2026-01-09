"""
Tests for the Chess.com API integration function.
"""

import pytest
import sys
import requests
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.chesscom_api import (
    get_games_from_chesscom,
    get_user_games,
    get_all_user_games,
)


class TestGetGamesFromChesscom:
    """Tests for the get_games_from_chesscom function."""
    
    @patch('requests.get')
    def test_get_games_success(self, mock_get):
        """Test successfully fetching games from Chess.com API."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "games": [
                {
                    "url": "https://www.chess.com/game/live/12345",
                    "pgn": "[Event \"Live Chess\"]\n[White \"player1\"]\n[Black \"player2\"]\n[Result \"1-0\"]\n\n1. e4 e5 2. Nf3 Nc6 1-0",
                    "time_control": "600+0",
                    "end_time": 1234567890,
                    "rated": True,
                    "rules": "chess"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        games = get_games_from_chesscom("testuser", "2024", "01")
        
        assert len(games) == 1
        assert games[0]["pgn"] is not None
        assert "e4" in games[0]["pgn"]
        mock_get.call_count == 2
    
    @patch('requests.get')
    def test_get_games_empty_response(self, mock_get):
        """Test when API returns empty games list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"games": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        games = get_games_from_chesscom("testuser", "2024", "01")
        
        assert games == []
    
    @patch('requests.get')
    def test_get_games_api_error(self, mock_get):
        """Test when API returns an error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception):
            get_games_from_chesscom("testuser", "2024", "01")
    
    @patch('requests.get')
    def test_get_games_network_error(self, mock_get):
        """Test when network request fails."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        with pytest.raises(Exception):
            get_games_from_chesscom("testuser", "2024", "01")
    
    @patch('requests.get')
    def test_get_games_multiple_pages(self, mock_get):
        """Test fetching games from multiple months."""
        # Mock responses for different months
        mock_header1 = Mock()
        mock_header1.status_code = 200
        mock_header1.json.return_value = {
            "games": [{"pgn": "1. e4 e5 1-0", "url": "game1"}]
        }
        mock_header1.raise_for_status = Mock()

        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            "games": [{"pgn": "1. e4 e5 1-0", "url": "game1"}]
        }
        mock_response1.raise_for_status = Mock()

        mock_header2 = Mock()
        mock_header2.status_code = 200
        mock_header2.json.return_value = {
            "games": [{"pgn": "1. e4 e5 1-0", "url": "game1"}]
        }
        mock_header2.raise_for_status = Mock()

        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "games": [{"pgn": "1. d4 d5 1-0", "url": "game2"}]
        }
        mock_response2.raise_for_status = Mock()
        
        mock_get.side_effect = [mock_header1, mock_response1, mock_header2, mock_response2]
        
        games = get_games_from_chesscom("testuser", "2024", ["01", "02"])
        
        assert len(games) == 2
        assert mock_get.call_count == 4


class TestGetUserGames:
    """Tests for the get_user_games convenience function."""
    
    @patch('src.api.chesscom_api.get_all_user_games')
    def test_get_user_games_all_games(self, mock_get_all):
        """Test getting all games when no parameters specified."""
        mock_get_all.return_value = [
            {"pgn": "1. e4 e5 1-0", "url": "game1"}
        ]
        
        games = get_user_games("testuser")
        
        assert len(games) == 1
        mock_get_all.assert_called_once_with("testuser")
    
    @patch('src.api.chesscom_api.get_games_from_chesscom')
    def test_get_user_games_specific_month(self, mock_get_games):
        """Test getting games for a specific month."""
        mock_get_games.return_value = [
            {"pgn": "1. e4 e5 1-0", "url": "game1"}
        ]
        
        games = get_user_games("testuser", year="2024", month="03")
        
        assert len(games) == 1
        mock_get_games.assert_called_once_with("testuser", "2024", "03")
    
    @patch('src.api.chesscom_api.get_games_from_chesscom')
    def test_get_user_games_year_range(self, mock_get_games):
        """Test getting games for multiple months."""
        mock_get_games.return_value = [
            {"pgn": "1. e4 e5 1-0", "url": "game1"}
        ]
        
        games = get_user_games("testuser", year="2024", month=["01", "02", "03"])
        
        mock_get_games.assert_called_once_with("testuser", "2024", ["01", "02", "03"])
    
    @patch('requests.get')
    def test_get_all_user_games(self, mock_get):
        """Test getting all games from archives."""
        # Mock archives response
        mock_archives_response = Mock()
        mock_archives_response.status_code = 200
        mock_archives_response.json.return_value = {
            "archives": [
                "https://api.chess.com/pub/player/testuser/games/2024/01",
                "https://api.chess.com/pub/player/testuser/games/2024/02"
            ]
        }
        mock_archives_response.raise_for_status = Mock()
        
        # Mock game responses
        mock_games_response1 = Mock()
        mock_games_response1.status_code = 200
        mock_games_response1.json.return_value = {
            "games": [{"pgn": "1. e4 e5 1-0", "url": "game1"}]
        }
        mock_games_response1.raise_for_status = Mock()
        
        mock_games_response2 = Mock()
        mock_games_response2.status_code = 200
        mock_games_response2.json.return_value = {
            "games": [{"pgn": "1. d4 d5 1-0", "url": "game2"}]
        }
        mock_games_response2.raise_for_status = Mock()
        
        mock_get.side_effect = [mock_archives_response, mock_games_response1, mock_games_response2]
        
        from src.api.chesscom_api import get_all_user_games
        games = get_all_user_games("testuser")
        
        assert len(games) == 2
        assert mock_get.call_count == 3  # 1 for archives + 2 for games
