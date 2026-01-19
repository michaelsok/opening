# Chess Opening Analysis & Repertoire Tracker

A powerful tool to analyze your chess games against a personal opening repertoire. It fetches games from Chess.com, identifies where they diverge from your repertoire, and generates beautiful interactive HTML reports.

## Key Features

- **Automated Game Fetching**: Fetch games directly from Chess.com for any user with date and time-class filters.
- **Smart Repertoire Matching**: 
  - Matches games against a personal repertoire stored as PGN files.
  - Supports color-specific matching: uses `white.pgn` for games as White and `black.pgn` for games as Black.
  - Automatically handles variations and identifies the first point of divergence.
- **Interactive Visualizations**:
  - Generates interactive HTML reports for individual games and an index page for a series of games.
  - Dynamic SVG chessboards with move-by-move navigation.
  - Highlights repertoire moves (green) and divergence points (red).
  - **Opponent Divergence Detection**: Specifically highlights when an opponent leaves your known repertoire with a unique styling (red border, transparent background).

## Project Structure

```
opening/
├── src/
│   ├── api/                   # Chess.com API integration
│   ├── parsers/               # PGN tree parsing logic
│   ├── opening/               # Core analysis coordination
│   └── visualization/         # Interactive HTML report generation
├── openings/                  # Your repertoire files (white.pgn, black.pgn)
│   ├── white/                 # PGN files for games as White
│   └── black/                 # PGN files for games as Black
├── reports/                   # Generated analysis reports (git-ignored)
├── docs/                      # Implementation plans and walkthroughs
├── run_final_mdb_analysis.py  # Example script for ChessMDB analysis
└── requirements.txt
```

## Installation

1. Clone the repository.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Analyzing Your Games

You can analyze games for a specific user using the `analyze_user_openings` function:

```python
from src.opening.user_opening_analysis import analyze_user_openings
from datetime import datetime, timedelta

# Analyze last 7 days of blitz games
analyze_user_openings(
    username="YourUsername",
    opening_repertoire="openings",
    time_class="blitz",
    start_date=datetime.now() - timedelta(days=7),
    output_file="reports/analysis.html"
)
```

### Repertoire Setup

Place your opening repertoire in the `openings/` directory using the following structure:
- `openings/white/`: Put all your PGN files for playing as White here.
- `openings/black/`: Put all your PGN files for playing as Black here.

The tool will load all `.pgn` files within these subdirectories and use them to match your games based on your color.

**Backward Compatibility**: The tool still supports single `white.pgn` and `black.pgn` files in the root `openings/` directory if the subdirectories are missing or empty.

## Features in Detail

### Interactive Move Lists
The generated reports feature a move list where:
- Moves within your repertoire are highlighted in **green**.
- The highlight stops exactly at the last matched move.
- The move that diverges from the repertoire is highlighted in **red**.
- If the **opponent** diverged, the move has a **red border** with a transparent background.

### Navigation
- Click on any move to jump to that position on the board.
- Use keyboard arrows (Left/Right) to navigate through the game.
- View alternative variations from your repertoire directly in the move list.

## Running Tests

Run the test suite with pytest:

```bash
pytest tests/
```

## License

MIT
