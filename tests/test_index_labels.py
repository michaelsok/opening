
import os
from pathlib import Path
from src.visualization.chess_display import create_index_html

def test_index_labels_and_styling(tmp_path):
    # Setup repertoires
    opening_dir = tmp_path / "openings"
    opening_dir.mkdir()
    
    # White repertoire: 1. e4 e5
    white_pgn = '[Event "White Repertoire"]\n\n1. e4 e5 *'
    (opening_dir / "white.pgn").write_text(white_pgn)
        
    # Black repertoire: 1. e4 c5
    black_pgn = '[Event "Black Repertoire"]\n\n1. e4 c5 *'
    (opening_dir / "black.pgn").write_text(black_pgn)

    # Scenarios
    games = [
        # Scenario 1: User is White, diverges at move 2
        '[Event "White Player Divergence"]\n[White "ChessMDB"]\n[Black "Opponent"]\n\n1. e4 e5 2. Bc4 *',
        
        # Scenario 2: User is White, opponent diverges at move 1...
        '[Event "White Opponent Divergence"]\n[White "ChessMDB"]\n[Black "Opponent"]\n\n1. e4 d5 *',
        
        # Scenario 3: User is Black, diverges at move 1...
        '[Event "Black Player Divergence"]\n[White "Opponent"]\n[Black "ChessMDB"]\n\n1. e4 e5 *',
        
        # Scenario 4: User is Black, opponent diverges at move 2
        '[Event "Black Opponent Divergence"]\n[White "Opponent"]\n[Black "ChessMDB"]\n\n1. e4 c5 2. a3 *'
    ]

    output_file = tmp_path / "index.html"
    
    # Generate index HTML
    create_index_html(
        games=games,
        opening_repertoire=opening_dir,
        target_username="ChessMDB",
        output_file=output_file,
        open_in_browser=False
    )
    
    assert output_file.exists()
    
    with open(output_file, 'r') as f:
        content = f.read()
        
    # Verification
    assert "Player diverges at: 2. Bc4" in content
    assert "Opponent diverges at: 1... d5" in content
    assert "Player diverges at: 1... e5" in content
    assert "Opponent diverges at: 2. a3" in content
    
    # Check for green styling class for opponent divergence
    assert 'opponent-divergence' in content
