
import os
import sys
import shutil
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.visualization.chess_display import create_index_html

def test_directory_repertoire():
    # Setup repertoire structure
    opening_base = Path("test_openings")
    if opening_base.exists():
        shutil.rmtree(opening_base)
    
    white_dir = opening_base / "white"
    black_dir = opening_base / "black"
    os.makedirs(white_dir, exist_ok=True)
    os.makedirs(black_dir, exist_ok=True)
    
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

    output_file = "reports/test_directory_repertoire.html"
    os.makedirs("reports", exist_ok=True)
    
    print("Generating index HTML with directory-based repertoire...")
    create_index_html(
        games=games,
        opening_repertoire=opening_base,
        target_username="ChessMDB",
        output_file=output_file,
        open_in_browser=False
    )
    
    print(f"Index generated at: {output_file}")
    
    with open(output_file, 'r') as f:
        content = f.read()
        
    # Verification
    expected_count = content.count("Follows opening repertoire")
    print(f"Games following repertoire: {expected_count}/5")
    
    if expected_count == 4:
        print("\nPASSED: All 4 repertoire games correctly matched multiple PGNs in subdirectories!")
    else:
        print(f"\nFAILED: Expected 4 matches, found {expected_count}")

    # Clean up test directories
    # shutil.rmtree(opening_base)

if __name__ == "__main__":
    test_directory_repertoire()
