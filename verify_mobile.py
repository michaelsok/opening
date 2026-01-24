
import logging
from src.visualization.chess_display import create_index_html
from pathlib import Path

def verify_mobile():
    logging.basicConfig(level=logging.INFO)
    
    # Use a small set of games for testing
    games = [
        """[Event "Casual Game"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O 1-0""",
        """[Event "Blitz Game"]
[White "Opponent"]
[Black "ChessMDB"]
[Result "0-1"]

1. d4 Nf6 2. c4 e6 3. Nf3 d5 0-1"""
    ]
    
    # Reports directory
    output_dir = Path("reports/mobile_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate mobile report
    output_path = create_index_html(
        games=games,
        opening_repertoire="openings",
        target_username="ChessMDB",
        output_file=output_dir / "index.html",
        open_in_browser=False,
        template_variant="mobile"
    )
    
    print(f"Mobile report generated at: {output_path}")

if __name__ == "__main__":
    verify_mobile()
