import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from src.api.chesscom_api import get_all_user_games

class TestChesscomApiOptimization:
    @patch('requests.get')
    def test_get_all_user_games_filters_archives(self, mock_get):
        """Test that get_all_user_games only requests archives within the date range."""
        username = "testuser"
        
        # Mock archives response with several months across two years
        mock_archives_response = Mock()
        mock_archives_response.status_code = 200
        mock_archives_response.json.return_value = {
            "archives": [
                f"https://api.chess.com/pub/player/{username}/games/2025/11",
                f"https://api.chess.com/pub/player/{username}/games/2025/12",
                f"https://api.chess.com/pub/player/{username}/games/2026/01",
                f"https://api.chess.com/pub/player/{username}/games/2026/02"
            ]
        }
        mock_archives_response.raise_for_status = Mock()
        
        # Mock games response (empty is fine for this test)
        mock_games_response = Mock()
        mock_games_response.status_code = 200
        mock_games_response.json.return_value = {"games": []}
        mock_games_response.raise_for_status = Mock()
        
        # Side effect: first call is for archives, subsequent calls for filtered games archives
        mock_get.side_effect = [mock_archives_response, mock_games_response]
        
        # Request only current month (Jan 2026)
        start_date = datetime(2026, 1, 10)
        end_date = datetime(2026, 1, 20)
        
        get_all_user_games(username, start_date=start_date, end_date=end_date)
        
        # Should be called 2 times: 1 for archives list, 1 for Jan 2026 games
        assert mock_get.call_count == 2
        
        # Verify the second call was indeed for Jan 2026
        called_urls = [call.args[0] for call in mock_get.call_args_list]
        assert f"https://api.chess.com/pub/player/{username}/games/2026/01" in called_urls
        # Verify Dec 2025 was NOT called (it ends before Jan 10)
        assert f"https://api.chess.com/pub/player/{username}/games/2025/12" not in called_urls
        # Verify Feb 2026 was NOT called (it starts after Jan 20)
        assert f"https://api.chess.com/pub/player/{username}/games/2026/02" not in called_urls

    @patch('requests.get')
    def test_get_all_user_games_cross_month_archives(self, mock_get):
        """Test that get_all_user_games requests multiple archives when range spans months."""
        username = "testuser"
        
        mock_archives_response = Mock()
        mock_archives_response.status_code = 200
        mock_archives_response.json.return_value = {
            "archives": [
                f"https://api.chess.com/pub/player/{username}/games/2025/12",
                f"https://api.chess.com/pub/player/{username}/games/2026/01",
                f"https://api.chess.com/pub/player/{username}/games/2026/02"
            ]
        }
        mock_archives_response.raise_for_status = Mock()
        
        mock_games_response = Mock()
        mock_games_response.status_code = 200
        mock_games_response.json.return_value = {"games": []}
        mock_games_response.raise_for_status = Mock()
        
        # Expect 3 calls: 1 archives + 2 relevant months
        mock_get.side_effect = [mock_archives_response, mock_games_response, mock_games_response]
        
        # Range spans Dec 2025 and Jan 2026
        start_date = datetime(2025, 12, 15)
        end_date = datetime(2026, 1, 5)
        
        get_all_user_games(username, start_date=start_date, end_date=end_date)
        
        assert mock_get.call_count == 3
        called_urls = [call.args[0] for call in mock_get.call_args_list]
        assert f"https://api.chess.com/pub/player/{username}/games/2025/12" in called_urls
        assert f"https://api.chess.com/pub/player/{username}/games/2026/01" in called_urls
        assert f"https://api.chess.com/pub/player/{username}/games/2026/02" not in called_urls
