
import pytest
from fastapi.testclient import TestClient
from src.web.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_root_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text
    assert "Connect Chess.com" in response.text

@patch("src.web.main.verify_chess_user")
def test_verify_user_returns_html_dashboard(mock_verify):
    # Mock successful user verification
    mock_verify.return_value = {
        "avatar": "https://example.com/avatar.png",
        "name": "Magnus Carlsen",
        "location": "Norway"
    }

    response = client.post("/auth/verify", data={"username": "magnuscarlsen"})
    
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check for dashboard partial content
    assert "Game Repertoire" in response.text
    assert "Magnus Carlsen" in response.text
    assert "id=\"dashboard-step\"" in response.text

@patch("src.web.main.verify_chess_user")
def test_verify_user_not_found_returns_error_html(mock_verify):
    mock_verify.return_value = None

    response = client.post("/auth/verify", data={"username": "fakeuser"})
    
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Chess.com user not found" in response.text
    assert "text-red-400" in response.text

@patch("src.web.main.handle_repertoire_upload")
def test_upload_repertoire_returns_html_success(mock_handle):
    mock_handle.return_value = {
        "status": "success",
        "categories": ["Ruy Lopez", "Sicilian"]
    }

    # Create dummy PGN file
    files = {"file": ("test.pgn", b"[Event \"Test\"]\n1. e4 e5", "application/x-chess-pgn")}
    data = {"username": "magnuscarlsen", "color": "white"}

    response = client.post("/repertoire/upload", data=data, files=files)

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check for success partial content
    assert "Repertoire Loaded!" in response.text
    assert "Ruy Lopez" in response.text
    assert "Sicilian" in response.text
    assert "id=\"success-step\"" in response.text
