
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.visualization.chess_display import create_index_html

def test_index_labels():
    # Setup repertoires
    os.makedirs("openings", exist_ok=True)
    
    # White repertoire: 1. e4 e5
    white_pgn = '[Event "White Repertoire"]\n\n1. e4 e5 *'
    with open("openings/white.pgn", "w") as f:
        f.write(white_pgn)
        
    # Black repertoire: 1. e4 c5
    black_pgn = '[Event "Black Repertoire"]\n\n1. e4 c5 *'
    with open("openings/black.pgn", "w") as f:
        f.write(black_pgn)

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

    output_file = "reports/test_index_labels.html"
    os.makedirs("reports", exist_ok=True)
    
    print("Generating index HTML...")
    create_index_html(
        games=games,
        opening_repertoire="openings",
        target_username="ChessMDB",
        output_file=output_file,
        open_in_browser=False
    )
    
    print(f"Index generated at: {output_file}")
    
    with open(output_file, 'r') as f:
        content = f.read()
        
    # Verification
    checks = {
        "Scenario 1 (Player White 2. Bc4)": "Player diverges at: 2. Bc4",
        "Scenario 2 (Opponent Black 1... d5)": "Opponent diverges at: 1... d5",
        "Scenario 3 (Player Black 1... e5)": "Player diverges at: 1... e5",
        "Scenario 4 (Opponent White 2. a3)": "Opponent diverges at: 2. a3",
    }
    
    all_passed = True
    for scenario, expected in checks.items():
        if expected in content:
            print(f"PASSED: {scenario}")
        else:
            print(f"FAILED: {scenario}. Expected '{expected}' not found.")
            all_passed = False
            
    # Check for green styling class
    if 'opponent-divergence' in content:
        print("PASSED: opponent-divergence class found")
    else:
        print("FAILED: opponent-divergence class NOT found")
        all_passed = False

    if all_passed:
        print("\nAll index label verifications PASSED!")
    else:
        print("\nSome index label verifications FAILED!")

if __name__ == "__main__":
    test_index_labels()
