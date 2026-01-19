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
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.chesscom_api import (
    get_games_from_chesscom,
    get_user_games,
    get_all_user_games,
)
from datetime import datetime


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
        assert mock_get.call_count == 1
    
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
        
        mock_get.side_effect = [mock_response1, mock_response2]
        
        games = get_games_from_chesscom("testuser", "2024", ["01", "02"])
        
        assert len(games) == 2
        assert mock_get.call_count == 2


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


class TestFiltering:
    """Tests for filtering functionality."""
    
    @patch('requests.get')
    def test_filter_by_time_control_string(self, mock_get):
        """Test filtering games by time control string (e.g., '600+0')."""
        mock_header = Mock()
        mock_header.status_code = 200
        mock_header.json.return_value = {}
        mock_header.raise_for_status = Mock()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "games": [
                {
                    "url": "game1",
                    "pgn": "1. e4 e5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent1"},
                    "end_time": 1234567890,
                    "rated": True,
                    "rules": "chess"
                },
                {
                    "url": "game2",
                    "pgn": "1. d4 d5 1-0",
                    "time_control": "180+2",
                    "time_class": "bullet",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent2"},
                    "end_time": 1234567900,
                    "rated": True,
                    "rules": "chess"
                },
                {
                    "url": "game3",
                    "pgn": "1. e4 e5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "opponent3"},
                    "black": {"username": "testuser"},
                    "end_time": 1234567910,
                    "rated": True,
                    "rules": "chess"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        games = get_games_from_chesscom("testuser", "2024", "01", time_control="600+0")
        
        assert len(games) == 2
        assert all(game["time_control"] == "600+0" for game in games)
    
    @patch('requests.get')
    def test_filter_by_time_class(self, mock_get):
        """Test filtering games by time class (blitz, bullet, rapid, classical)."""
        mock_header = Mock()
        mock_header.status_code = 200
        mock_header.json.return_value = {}
        mock_header.raise_for_status = Mock()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "games": [
                {
                    "url": "game1",
                    "pgn": "1. e4 e5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent1"},
                    "end_time": 1234567890,
                    "rated": True,
                    "rules": "chess"
                },
                {
                    "url": "game2",
                    "pgn": "1. d4 d5 1-0",
                    "time_control": "180+2",
                    "time_class": "bullet",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent2"},
                    "end_time": 1234567900,
                    "rated": True,
                    "rules": "chess"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        games = get_games_from_chesscom("testuser", "2024", "01", time_class="blitz")
        
        assert len(games) == 1
        assert games[0]["time_class"] == "blitz"
    
    @patch('requests.get')
    def test_filter_by_color_white(self, mock_get):
        """Test filtering games where user played as white."""
        mock_header = Mock()
        mock_header.status_code = 200
        mock_header.json.return_value = {}
        mock_header.raise_for_status = Mock()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "games": [
                {
                    "url": "game1",
                    "pgn": "[White \"testuser\"]\n[Black \"opponent1\"]\n1. e4 e5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent1"},
                    "end_time": 1234567890,
                    "rated": True,
                    "rules": "chess"
                },
                {
                    "url": "game2",
                    "pgn": "[White \"opponent2\"]\n[Black \"testuser\"]\n1. d4 d5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "opponent2"},
                    "black": {"username": "testuser"},
                    "end_time": 1234567900,
                    "rated": True,
                    "rules": "chess"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        games = get_games_from_chesscom("testuser", "2024", "01", color="white")
        
        assert len(games) == 1
        assert games[0]["white"]["username"].lower() == "testuser"
    
    @patch('requests.get')
    def test_filter_by_color_black(self, mock_get):
        """Test filtering games where user played as black."""
        mock_header = Mock()
        mock_header.status_code = 200
        mock_header.json.return_value = {}
        mock_header.raise_for_status = Mock()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "games": [
                {
                    "url": "game1",
                    "pgn": "[White \"opponent1\"]\n[Black \"testuser\"]\n1. e4 e5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "opponent1"},
                    "black": {"username": "testuser"},
                    "end_time": 1234567890,
                    "rated": True,
                    "rules": "chess"
                },
                {
                    "url": "game2",
                    "pgn": "[White \"testuser\"]\n[Black \"opponent2\"]\n1. d4 d5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent2"},
                    "end_time": 1234567900,
                    "rated": True,
                    "rules": "chess"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        games = get_games_from_chesscom("testuser", "2024", "01", color="black")
        
        assert len(games) == 1
        assert games[0]["black"]["username"].lower() == "testuser"
    
    @patch('requests.get')
    def test_filter_by_date_range(self, mock_get):
        """Test filtering games by date range."""
        mock_header = Mock()
        mock_header.status_code = 200
        mock_header.json.return_value = {}
        mock_header.raise_for_status = Mock()
        
        # Create timestamps for different dates
        start_ts = int(datetime(2024, 1, 15).timestamp())
        mid_ts = int(datetime(2024, 1, 20).timestamp())
        end_ts = int(datetime(2024, 1, 25).timestamp())
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "games": [
                {
                    "url": "game1",
                    "pgn": "1. e4 e5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent1"},
                    "end_time": start_ts - 100,  # Before start date
                    "rated": True,
                    "rules": "chess"
                },
                {
                    "url": "game2",
                    "pgn": "1. d4 d5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent2"},
                    "end_time": mid_ts,  # Within range
                    "rated": True,
                    "rules": "chess"
                },
                {
                    "url": "game3",
                    "pgn": "1. e4 e5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent3"},
                    "end_time": end_ts + 100,  # After end date
                    "rated": True,
                    "rules": "chess"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        games = get_games_from_chesscom(
            "testuser", "2024", "01",
            start_date=datetime(2024, 1, 15),
            end_date=datetime(2024, 1, 25)
        )
        
        assert len(games) == 1
        assert games[0]["end_time"] == mid_ts
    
    @patch('requests.get')
    def test_filter_by_rated(self, mock_get):
        """Test filtering games by rated/unrated status."""
        mock_header = Mock()
        mock_header.status_code = 200
        mock_header.json.return_value = {}
        mock_header.raise_for_status = Mock()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "games": [
                {
                    "url": "game1",
                    "pgn": "1. e4 e5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent1"},
                    "end_time": 1234567890,
                    "rated": True,
                    "rules": "chess"
                },
                {
                    "url": "game2",
                    "pgn": "1. d4 d5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent2"},
                    "end_time": 1234567900,
                    "rated": False,
                    "rules": "chess"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        games = get_games_from_chesscom("testuser", "2024", "01", rated=True)
        
        assert len(games) == 1
        assert games[0]["rated"] is True
    
    @patch('requests.get')
    def test_filter_by_rules(self, mock_get):
        """Test filtering games by rules/variant."""
        mock_header = Mock()
        mock_header.status_code = 200
        mock_header.json.return_value = {}
        mock_header.raise_for_status = Mock()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "games": [
                {
                    "url": "game1",
                    "pgn": "1. e4 e5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent1"},
                    "end_time": 1234567890,
                    "rated": True,
                    "rules": "chess"
                },
                {
                    "url": "game2",
                    "pgn": "1. d4 d5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent2"},
                    "end_time": 1234567900,
                    "rated": True,
                    "rules": "chess960"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        games = get_games_from_chesscom("testuser", "2024", "01", rules="chess")
        
        assert len(games) == 1
        assert games[0]["rules"] == "chess"
    
    @patch('requests.get')
    def test_filter_combination(self, mock_get):
        """Test combining multiple filters."""
        mock_header = Mock()
        mock_header.status_code = 200
        mock_header.json.return_value = {}
        mock_header.raise_for_status = Mock()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "games": [
                {
                    "url": "game1",
                    "pgn": "[White \"testuser\"]\n[Black \"opponent1\"]\n1. e4 e5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent1"},
                    "end_time": int(datetime(2024, 1, 20).timestamp()),
                    "rated": True,
                    "rules": "chess"
                },
                {
                    "url": "game2",
                    "pgn": "[White \"opponent2\"]\n[Black \"testuser\"]\n1. d4 d5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "opponent2"},
                    "black": {"username": "testuser"},
                    "end_time": int(datetime(2024, 1, 20).timestamp()),
                    "rated": True,
                    "rules": "chess"
                },
                {
                    "url": "game3",
                    "pgn": "[White \"testuser\"]\n[Black \"opponent3\"]\n1. e4 e5 1-0",
                    "time_control": "180+2",
                    "time_class": "bullet",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent3"},
                    "end_time": int(datetime(2024, 1, 20).timestamp()),
                    "rated": True,
                    "rules": "chess"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        games = get_games_from_chesscom(
            "testuser", "2024", "01",
            color="white",
            time_class="blitz",
            rated=True,
            start_date=datetime(2024, 1, 15),
            end_date=datetime(2024, 1, 25)
        )
        
        assert len(games) == 1
        assert games[0]["white"]["username"].lower() == "testuser"
        assert games[0]["time_class"] == "blitz"
        assert games[0]["rated"] is True
    
    @patch('src.api.chesscom_api.get_all_user_games')
    def test_get_user_games_with_filters(self, mock_get_all):
        """Test get_user_games with filters."""
        # Mock should return already filtered games (matching what the real function would return)
        filtered_games = [
            {
                "url": "game1",
                "pgn": "[White \"testuser\"]\n[Black \"opponent1\"]\n1. e4 e5 1-0",
                "time_control": "600+0",
                "time_class": "blitz",
                "white": {"username": "testuser"},
                "black": {"username": "opponent1"},
                "end_time": 1234567890,
                "rated": True,
                "rules": "chess"
            }
        ]
        mock_get_all.return_value = filtered_games
        
        games = get_user_games("testuser", color="white", time_class="blitz")
        
        assert len(games) == 1
        assert games[0]["white"]["username"].lower() == "testuser"
        assert games[0]["time_class"] == "blitz"
        # Verify that get_all_user_games was called with the correct filter parameters
        mock_get_all.assert_called_once_with("testuser", color="white", time_class="blitz")
    
    @patch('requests.get')
    def test_get_all_user_games_with_filters(self, mock_get):
        """Test get_all_user_games with filters."""
        mock_archives_response = Mock()
        mock_archives_response.status_code = 200
        mock_archives_response.json.return_value = {
            "archives": [
                "https://api.chess.com/pub/player/testuser/games/2024/01"
            ]
        }
        mock_archives_response.raise_for_status = Mock()
        
        mock_games_response = Mock()
        mock_games_response.status_code = 200
        mock_games_response.json.return_value = {
            "games": [
                {
                    "url": "game1",
                    "pgn": "[White \"testuser\"]\n[Black \"opponent1\"]\n1. e4 e5 1-0",
                    "time_control": "600+0",
                    "time_class": "blitz",
                    "white": {"username": "testuser"},
                    "black": {"username": "opponent1"},
                    "end_time": 1234567890,
                    "rated": True,
                    "rules": "chess"
                },
                {
                    "url": "game2",
                    "pgn": "[White \"opponent2\"]\n[Black \"testuser\"]\n1. d4 d5 1-0",
                    "time_control": "180+2",
                    "time_class": "bullet",
                    "white": {"username": "opponent2"},
                    "black": {"username": "testuser"},
                    "end_time": 1234567900,
                    "rated": True,
                    "rules": "chess"
                }
            ]
        }
        mock_games_response.raise_for_status = Mock()
        
        mock_get.side_effect = [mock_archives_response, mock_games_response]
        
        from src.api.chesscom_api import get_all_user_games
        games = get_all_user_games("testuser", time_class="blitz")
        
        assert len(games) == 1
        assert games[0]["time_class"] == "blitz"
