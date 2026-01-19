# Goal: Add Navigation Buttons to Individual Game Pages

Enhance user experience by adding buttons to navigate between games and back to the index page directly from the game viewer.

## Proposed Changes

### Visualization [MODIFY]

#### [MODIFY] [chess_display.py](file:///home/msok/projects/opening/src/visualization/chess_display.py)
- **`create_index_html`**: Pass `game_index` and `total_games` to `display_game_from_string`.
- **`display_game_from_string`**: Accept `game_index` and `total_games` and pass them to `_create_html_viewer`.
- **`_create_html_viewer`**: Pass `game_index` and `total_games` to `_generate_html_content`.
- **`_generate_html_content`**: Pass `game_index` and `total_games` to the Jinja2 template.

#### [MODIFY] [single_game.html](file:///home/msok/projects/opening/src/visualization/templates/single_game.html)
- Add a new CSS class for navigation buttons.
- Add a navigation bar at the top of the container.
- Implement "Back to Index", "Previous Game", and "Next Game" buttons using Jinja2 conditional logic.

## Verification Plan

### Automated Tests
- Run `run_final_mdb_analysis.py` to generate the report.
- Verify the navigation buttons exist in the generated HTML and link to the correct pages.

### Manual Verification
- Open the generated `reports/chessmdb_refined_analysis.html`.
- Click on several games and verify that the navigation buttons work as expected.
