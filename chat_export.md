# Chat Export - Add index.html for Chess Game Redirect

## Task
Add an index.html file in src/visualization/ that can directly redirect to any chess game.

## Implementation Summary

### Test-Driven Development Process
1. **Created Tests First** (`tests/visualization/test_index_html.py`)
   - Test for creating index.html in default location
   - Test for creating index.html in custom location
   - Test that index.html contains a form for input
   - Test that index.html handles URL parameters
   - Test that index.html has redirect logic

2. **Implemented Function** (`src/visualization/chess_display.py`)
   - Added `create_index_html()` function that generates an HTML landing page
   - The HTML includes:
     - A form to input PGN content (textarea)
     - File upload capability for PGN files
     - URL parameter support (`?pgn=YOUR_PGN`)
     - Example game loader
     - JavaScript to handle form submission and redirect

3. **Updated Module Exports** (`src/visualization/__init__.py`)
   - Added `create_index_html` to the module exports

## Files Modified
- `src/visualization/chess_display.py` - Added `create_index_html()` function
- `src/visualization/__init__.py` - Added export for new function
- `tests/visualization/test_index_html.py` - New test file (5 tests)

## Test Results
All 87 tests passed, including:
- 5 new tests for index.html functionality
- All existing visualization tests still pass
- All other module tests still pass

## Function Signature
```python
def create_index_html(
    output_file: Optional[Union[str, Path]] = None,
    open_in_browser: bool = True
) -> str:
    """
    Create an index.html file that can redirect to any chess game.
    
    Creates an HTML file with a form that allows users to input PGN content
    (either via form input or URL parameters) and redirects to a generated
    chess game viewer.
    
    Args:
        output_file: Optional path to save the index.html file. 
                     If None, saves to src/visualization/index.html
        open_in_browser: If True, automatically opens the HTML file in the default browser
        
    Returns:
        str: Path to the generated index.html file
    """
```

## Features of index.html
- Beautiful, modern UI with gradient background
- Form input for PGN content
- File upload support for .pgn files
- URL parameter support: `index.html?pgn=YOUR_PGN_HERE`
- Example game loader button
- Instructions on how to use
- JavaScript handling for form submission and redirect logic

## Usage
```python
from src.visualization.chess_display import create_index_html

# Create index.html in default location (src/visualization/index.html)
index_path = create_index_html()

# Create in custom location
index_path = create_index_html("my_index.html", open_in_browser=False)
```

## Notes
The index.html file provides a landing page for chess game visualization. While the HTML itself cannot directly call Python functions from JavaScript, it provides:
- A user-friendly interface for PGN input
- Support for URL parameters to pre-fill PGN
- Client-side JavaScript to handle form submission
- Instructions for using with the Python backend

For full server-side integration, a backend service would be needed to process the PGN and generate game viewers using `display_game_from_string()`.

## Additional Update - Examples
Added `example_create_index_html()` function to `examples/display_game_example.py`:
- Demonstrates how to create and use the index.html page
- Shows all available features and usage options
- Includes helpful documentation about the index page capabilities
- Updated imports to include `create_index_html` function
