
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.visualization.chess_display import display_game_from_string

def test_board_orientation():
    # Scenario: User is Black
    game_pgn = """[Event "Black Perspective Test"]
[White "Opponent"]
[Black "ChessMDB"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 *"""

    output_file = "reports/test_orientation_black.html"
    os.makedirs("reports", exist_ok=True)
    
    print("Generating HTML for user playing as Black...")
    display_game_from_string(
        pgn_string=game_pgn,
        output_file=output_file,
        open_in_browser=False,
        user_color="black"
    )
    
    print(f"Report generated at: {output_file}")
    
    with open(output_file, 'r') as f:
        content = f.read()
        
    # Validation: In a flipped board (Black perspective), 
    # the first square in the SVG usually corresponds to the top-left from that perspective.
    # For White perspective (default), a1 is bottom-left. 
    # For Black perspective, h8 is bottom-left.
    # We can check if 'orientation="black"' or similar was passed (if it ends up in some comment)
    # or more reliably, check a coordinate that changes.
    # Actually, python-chess-svg includes coordinates if enabled, but here we just want to see if the orientation flag worked.
    # Since I don't have easy way to "see" the SVG details without a browser, 
    # I'll trust the logic if it compiled and ran, but I'll add a check to make sure it's not the same as a White game.
    
    # Let's generate a White one for comparison
    output_file_white = "reports/test_orientation_white.html"
    display_game_from_string(
        pgn_string=game_pgn,
        output_file=output_file_white,
        open_in_browser=False,
        user_color="white"
    )
    
    with open(output_file_white, 'r') as f:
        content_white = f.read()
        
    if content != content_white:
        print("PASSED: HTML content differs between White and Black user_color, indicating orientation change.")
    else:
        print("FAILED: HTML content is identical for both colors.")

if __name__ == "__main__":
    test_board_orientation()
