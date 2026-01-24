# Divergence Analysis Integration Walkthrough

I have integrated the Chess.com divergence analysis feature into the web dashboard, allowing users to analyze their actual games against their uploaded repertoires.

## Changes Made

### 1. Analysis Engine & Backend
- Implemented `/analysis/run` endpoint in [main.py](file:///home/msok/projects/opening/src/web/main.py).
- The engine fetches all stored repertoires for the user from the SQLite database.
- It then uses the Chess.com API to fetch games for the specified Year and Month.
- Automatically generates a complete analysis report (including individual game viewers) using `create_index_html`.
- Reports are stored in a new `reports/` directory and served statically.

### 2. Frontend Dashboard
- Updated [index.html](file:///home/msok/projects/opening/src/web/static/index.html) to include Year and Month filters in the success step.
- Added a "Find Games & Divergences" button that triggers the analysis.
- Implemented state handling in [app.js](file:///home/msok/projects/opening/src/web/static/js/app.js) to show loading states and the final report link.
- Added styling for dropdown selects in [styles.css](file:///home/msok/projects/opening/src/web/static/css/styles.css).

### 3. Styling & Fixes
- Fixed the broken Jinja2 CSS loading syntax in both [single_game.html](file:///home/msok/projects/opening/src/visualization/templates/single_game.html) and [multi_game.html](file:///home/msok/projects/opening/src/visualization/templates/multi_game.html).
- Ensured consistent glassmorphism design across all generated reports.
- Verified that move background selection (highlighting current move) works correctly.

## Verification

### Automated Tests
- Verified database and persistence logic with existing tests.
```bash
pytest tests/web/test_database.py
# Output: 4 passed
```

### Manual Verification
- Verified `/analysis/run` endpoint using `curl` for both existing and non-existent games.
- Verified that without a repertoire, the system correctly prompts the user to upload one first.
- Confirmed that the server correctly mount and serves the `reports/` directory.

## How to use
1. Connect with your Chess.com username.
2. Upload your repertoire PGN (White or Black).
3. Select the Year and Month.
4. Click "Find Games & Divergences".
5. Click "View Analysis Report" to see your results!
