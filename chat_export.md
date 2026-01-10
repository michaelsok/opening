# Chat Export - Add index.html for Chess Games with Divergence Analysis

## Task
Change the function for the index.html by creating an index of all games given with the function of displaying games with their divergence point against an opening repertoire.

## Implementation Summary

### Test-Driven Development Process
1. **Created Tests First** (`tests/visualization/test_index_html.py`)
   - Test for creating index.html with games and opening repertoire
   - Test for creating index.html with opening directory
   - Test that index.html lists all provided games
   - Test that index.html shows divergence points
   - Test that games are clickable/redirectable
   - Test error handling for empty games list
   - Test default and custom output locations

2. **Updated Function** (`src/visualization/chess_display.py`)
   - Completely rewrote `create_index_html()` function
   - Now accepts `games` (list of PGN strings) and `opening_repertoire` (list or directory path)
   - For each game:
     - Parses PGN and finds divergence point against opening repertoire
     - Generates individual game viewer HTML files with divergence highlighting
   - Creates index.html page that:
     - Lists all games with their divergence information
     - Shows divergence moves for games that diverge
     - Marks games that follow the opening repertoire completely
     - Makes each game clickable to open its viewer

3. **Added Helper Function** (`_generate_index_html_content()`)
   - Generates HTML content for the games index page
   - Includes modern styling and game list display

4. **Updated Imports**
   - Added imports for divergence analysis (`parse_pgn_string_to_tree`, `find_first_divergence_across_openings`)

## Files Modified
- `src/visualization/chess_display.py` - Completely rewrote `create_index_html()` function, added `_generate_index_html_content()` helper
- `tests/visualization/test_index_html.py` - Updated tests for new functionality (8 tests)
- `examples/display_game_example.py` - Updated `example_create_index_html()` function

## Test Results
All 90 tests passed, including:
- 8 tests for index.html functionality with games and divergence
- All existing visualization tests still pass
- All other module tests still pass

## Function Signature
```python
def create_index_html(
    games: List[str],
    opening_repertoire: Union[List[str], str, Path],
    output_file: Optional[Union[str, Path]] = None,
    open_in_browser: bool = True,
    size: int = 400
) -> str:
    """
    Create an index.html file that displays all games with their divergence points.
    
    Creates an HTML index page that lists all provided games with their divergence
    information against an opening repertoire. Each game is clickable and redirects
    to a game viewer with divergence highlighting.
    
    Args:
        games: List of PGN strings representing the games to index
        opening_repertoire: List of PGN strings or path to directory containing opening PGN files
        output_file: Optional path to save the index.html file. 
                     If None, saves to src/visualization/index.html
        open_in_browser: If True, automatically opens the HTML file in the default browser
        size: Size of chess board in pixels (default: 400)
        
    Returns:
        str: Path to the generated index.html file
        
    Raises:
        ValueError: If games list is empty or no valid games found
    """
```

## Features of index.html
- Beautiful, modern UI with gradient background
- Lists all provided games with game information (event, players, result, date)
- Shows divergence analysis for each game:
  - Games that follow the opening repertoire are marked with ✓
  - Games that diverge show the divergence move(s) highlighted
- Clickable games that open individual game viewers in new tabs
- Each individual game viewer shows:
  - Full interactive chess board
  - Divergence move highlighted in red
  - Opening repertoire continuation (if applicable)
  - Move navigation and analysis

## Usage
```python
from src.visualization.chess_display import create_index_html

# With list of games and opening repertoire as strings
games = [
    "[Event \"Game 1\"]\n1. e4 e5 2. Nf3 Nc6 3. Bc4 1-0",
    "[Event \"Game 2\"]\n1. d4 d5 1-0"
]
opening_repertoire = ["1. e4 e5 2. Nf3 Nc6 3. Bb5"]

index_path = create_index_html(games, opening_repertoire)

# With opening directory
index_path = create_index_html(
    games, 
    opening_repertoire="openings/",  # Path to directory with .pgn files
    size=500
)
```

## Notes
The index.html file provides a comprehensive index of all games analyzed against an opening repertoire. Key features:

1. **Automatic Divergence Analysis**: Each game is automatically analyzed to find where it diverges from the opening repertoire using `find_first_divergence_across_openings()`.

2. **Individual Game Viewers**: For each game, a separate HTML viewer file is generated (game_0.html, game_1.html, etc.) with full interactive board and divergence highlighting.

3. **Opening Repertoire Support**: The opening repertoire can be provided as:
   - A list of PGN strings
   - A directory path containing .pgn files

4. **User Experience**: The index page shows:
   - Game metadata (event, players, result, date)
   - Divergence information (which move diverged, or if it follows the opening)
   - Clickable cards that open the full game viewer

## Updated Example Function
Updated `example_create_index_html()` function in `examples/display_game_example.py`:
- Now demonstrates the new functionality with games and opening repertoire
- Shows how to create an index with multiple games
- Includes sample games with different divergence scenarios
