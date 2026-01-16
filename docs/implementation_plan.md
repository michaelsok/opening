# Plan: Implement User Opening Analysis

This plan outlines the creation of a new module to analyze a user's Chess.com games against an opening repertoire and visualize the results.

## Proposed Changes

### [Component Name] Opening Analysis

#### [MODIFY] [user_opening_analysis.py](file:///home/msok/projects/opening/src/opening/user_opening_analysis.py)
- Implement `analyze_user_openings(username, opening_repertoire, ...)` function.
- It will fetch games using `get_user_games`.
- It will then use `create_index_html` from `src.visualization.chess_display` to generate the interactive visualization.
- This function builds upon the logic of `analyze_user_games_divergence` but focuses on generating the final visualization.

## Verification Plan

### Automated Tests
- Create a test script `verify_user_analysis.py` that mocks the Chess.com API or uses a known user to verify the flow.

### Manual Verification
- Run the script with a real Chess.com username and a sample repertoire to ensure the `index.html` is generated correctly.
