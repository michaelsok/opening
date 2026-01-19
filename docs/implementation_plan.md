# Plan: Refine Opening Analysis and Visualization

This plan covers three main improvements:
1. Color-based repertoire matching (White vs Black).
2. UI: Stop repertoire highlighting (green) at the end of the matched repertoire.
3. UI: Add a red border around the divergence move if it was made by the opponent.

## User Review Required

> [!IMPORTANT]
> - The tool will now expect `white.pgn` and `black.pgn` in the openings directory for color-specific matching. If they don't exist, it falls back to matching against all PGNs in the directory.
> - The highlighting behavior in the board viewer is changing: moves after the repertoire ends will no longer be highlighted in green.

## Proposed Changes

### [Component Name] Opening Analysis

#### [MODIFY] [user_opening_analysis.py](file:///home/msok/projects/opening/src/opening/user_opening_analysis.py)
- Pass `username` as `target_username` to `create_index_html`.

### [Component Name] Visualization Logic

#### [MODIFY] [chess_display.py](file:///home/msok/projects/opening/src/visualization/chess_display.py)
- **`create_index_html`**:
    - Add `target_username` parameter.
    - Implement logic to select `white.pgn` or `black.pgn` from the opening directory based on the user's color in each game.
    - Pass `user_color` to `display_game_from_string`.
- **`display_game_from_string`**:
    - Add `user_color` parameter.
    - Calculate `repertoire_length` (number of matching moves before divergence).
    - Pass `user_color` and `repertoire_length` to `_generate_html_content`.
- **`_create_html_viewer`** (internal name for the display function):
    - Update signature and data passing.

### [Component Name] Visualization Templates

#### [MODIFY] [single_game.html](file:///home/msok/projects/opening/src/visualization/templates/single_game.html)
- **CSS**:
    - Add `.move.opponent-divergence` class with `border: 2px solid red !important`.
- **JS**:
    - Store `userColor` and `repertoireLength` in the global state.
    - Update `goToMove(index)` to only apply the `active` class if `index <= repertoireLength`.
- **HTML**:
    - Add logic to apply `opponent-divergence` class to the divergence move if it matches the opponent's turn.

### [Component Name] Git and API Maintenance

#### [MODIFY] [chesscom_api.py](file:///home/msok/projects/opening/src/api/chesscom_api.py)
- Resolved merge conflict in headers (minimal `User-Agent`).
- Ensure `User-Agent` complies with Chess.com requirements without exposing personal info.

#### [MODIFY] [.gitignore](file:///home/msok/projects/opening/.gitignore)
- Add `reports/*.html` to ensure newly generated reports are not tracked by git.

#### [CLEANUP] Git History
- Remove all `reports/*.html` files from the entire git history using `git filter-branch`.
- Prune git objects to reduce repo size.

### [Component Name] Index Page Refinement [NEW]

#### [MODIFY] [chess_display.py](file:///home/msok/projects/opening/src/visualization/chess_display.py)
- **`_generate_index_html_content`**:
    - Calculate `is_opponent_divergence` using `user_color` and `divergence_point`.
    - Update `divergence_html` to use "Player diverges at:" or "Opponent diverges at:".
    - Pass an `is_opponent` flag or use a specific CSS class in the generated HTML.

#### [MODIFY] [index.html](file:///home/msok/projects/opening/src/visualization/templates/index.html)
- **CSS**:
    - Add `.game-divergence.opponent-divergence` style with green background and green left border.
- **HTML**:
    - Add conditional class `opponent-divergence` to the game divergence div.

## Verification Plan

### Automated Tests
- Create a test script `verify_index_labels.py` that generates the index and checks for "Player" vs "Opponent" strings and CSS classes.
- Manually inspect generated `reports/chessmdb_refined_analysis.html`.
