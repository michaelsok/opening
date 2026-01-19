
import os
import re
from pathlib import Path
from src.visualization.chess_display import create_index_html

def test_first_move_divergence(tmp_path):
    # Setup repertoire with something that doesn't start with 1. d4
    # Repertoire: only Ruy Lopez (1. e4)
    opening_pgn = '[Event "Ruy Lopez"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bb5 *'
    
    # Game: starts with 1. d4
    game_pgn = '[Event "Divergence at Move 1"]\n[White "ChessMDB"]\n[Black "Opponent"]\n\n1. d4 d5 2. c4 *'
    
    output_file = tmp_path / "index.html"
    
    # Generate report
    create_index_html(
        games=[game_pgn],
        opening_repertoire=[opening_pgn],
        target_username="ChessMDB",
        output_file=output_file,
        open_in_browser=False
    )
    
    assert output_file.exists()
    
    # Check index file content
    with open(output_file, 'r') as f:
        index_content = f.read()
    
    assert "Player diverges at: 1. d4" in index_content
    
    # Check individual game file
    game_file = tmp_path / "game_0.html"
    assert game_file.exists()
    
    with open(game_file, 'r') as f:
        game_content = f.read()
            
    # Check if the board viewer JS has divergenceMoveIndex = 0
    assert "const divergenceMoveIndex = 0" in game_content
