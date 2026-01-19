
import os
from pathlib import Path
from src.visualization.chess_display import create_index_html

def test_directory_repertoire_matching(tmp_path):
    # Setup repertoire structure
    opening_base = tmp_path / "openings"
    white_dir = opening_base / "white"
    black_dir = opening_base / "black"
    white_dir.mkdir(parents=True)
    black_dir.mkdir(parents=True)
    
    # White repertoire 1: Ruy Lopez (1. e4 e5 2. Nf3 Nc6 3. Bb5)
    with open(white_dir / "ruy_lopez.pgn", "w") as f:
        f.write('[Event "Ruy Lopez"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bb5 *')
        
    # White repertoire 2: Italian (1. e4 e5 2. Nf3 Nc6 3. Bc4)
    with open(white_dir / "italian.pgn", "w") as f:
        f.write('[Event "Italian Game"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bc4 *')

    # Black repertoire 1: Sicilian (1. e4 c5)
    with open(black_dir / "sicilian.pgn", "w") as f:
        f.write('[Event "Sicilian Defense"]\n\n1. e4 c5 *')
        
    # Black repertoire 2: French (1. e4 e6)
    with open(black_dir / "french.pgn", "w") as f:
        f.write('[Event "French Defense"]\n\n1. e4 e6 *')

    # Test games
    games = [
        # User is White, follows Italian
        '[Event "User Italian"]\n[White "ChessMDB"]\n[Black "Opponent"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bc4 *',
        
        # User is White, follows Ruy Lopez
        '[Event "User Ruy Lopez"]\n[White "ChessMDB"]\n[Black "Opponent"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bb5 *',
        
        # User is Black, follows Sicilian
        '[Event "User Sicilian"]\n[White "Opponent"]\n[Black "ChessMDB"]\n\n1. e4 c5 *',
        
        # User is Black, follows French
        '[Event "User French"]\n[White "Opponent"]\n[Black "ChessMDB"]\n\n1. e4 e6 *',
        
        # User is White, diverges from both
        '[Event "User Divergence"]\n[White "ChessMDB"]\n[Black "Opponent"]\n\n1. d4 *'
    ]

    output_file = tmp_path / "index.html"
    
    # Generate index HTML
    create_index_html(
        games=games,
        opening_repertoire=opening_base,
        target_username="ChessMDB",
        output_file=output_file,
        open_in_browser=False
    )
    
    assert output_file.exists()
    
    with open(output_file, 'r') as f:
        content = f.read()
        
    # Verification: 4 games should follow repertoire, 1 should diverge
    assert content.count("Follows opening repertoire") == 4
    assert "✓ Follows opening repertoire" in content
    assert "Player diverges at: 1. d4" in content
