
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.visualization.chess_display import create_index_html

def reproduce_first_move_divergence():
    # Setup repertoire with something that doesn't start with 1. d4
    # Repertoire: only Ruy Lopez (1. e4)
    opening_pgn = '[Event "Ruy Lopez"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bb5 *'
    
    # Game: starts with 1. d4
    game_pgn = '[Event "Divergence at Move 1"]\n[White "ChessMDB"]\n[Black "Opponent"]\n\n1. d4 d5 2. c4 *'
    
    output_file = "reports/test_reproduce_bug.html"
    os.makedirs("reports", exist_ok=True)
    
    print("Generating report for first move divergence...")
    create_index_html(
        games=[game_pgn],
        opening_repertoire=[opening_pgn],
        target_username="ChessMDB",
        output_file=output_file,
        open_in_browser=False
    )
    
    print(f"Index generated at: {output_file}")
    
    # Check index file first
    with open(output_file, 'r') as f:
        index_content = f.read()
    
    if "Player diverges at: 1. d4" in index_content:
        print("SUCCESS: Index page shows divergence at 1. d4")
    else:
        print("FAILURE: Index page DOES NOT show divergence at 1. d4")
        if "Follows opening repertoire" in index_content:
             print("Reason: Index page incorrectly says it follows repertoire")
    
    # Check individual game file
    game_file = "reports/game_0.html"
    if os.path.exists(game_file):
        with open(game_file, 'r') as f:
            game_content = f.read()
            
        # Check if the board viewer JS has divergenceMoveIndex
        if "const divergenceMoveIndex = 0" in game_content:
            print("SUCCESS: Individual game has divergenceMoveIndex = 0")
        else:
            print("FAILURE: Individual game DOES NOT have divergenceMoveIndex = 0")
            # See what it has
            import re
            match = re.search(r'const divergenceMoveIndex = (.*);', game_content)
            if match:
                print(f"Found: {match.group(0)}")
            else:
                print("Could not find divergenceMoveIndex in JS")

if __name__ == "__main__":
    reproduce_first_move_divergence()
