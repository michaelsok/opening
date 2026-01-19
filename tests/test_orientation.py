
import os
from src.visualization.chess_display import display_game_from_string

def test_board_orientation_differs_by_color(tmp_path):
    # Scenario: User playing Black vs White
    game_pgn = """[Event "Perspective Test"]
[White "Opponent"]
[Black "ChessMDB"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 *"""

    output_black = tmp_path / "black.html"
    output_white = tmp_path / "white.html"
    
    # Generate HTML for Black perspective
    display_game_from_string(
        pgn_string=game_pgn,
        output_file=output_black,
        open_in_browser=False,
        user_color="black"
    )
    
    # Generate HTML for White perspective
    display_game_from_string(
        pgn_string=game_pgn,
        output_file=output_white,
        open_in_browser=False,
        user_color="white"
    )
    
    assert output_black.exists()
    assert output_white.exists()
    
    with open(output_black, 'r') as f:
        content_black = f.read()
    with open(output_white, 'r') as f:
        content_white = f.read()
        
    # The content MUST be different because SVGs are generated with different orientations
    assert content_black != content_white
