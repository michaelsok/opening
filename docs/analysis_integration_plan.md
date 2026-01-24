# Divergence Analysis Integration Plan

This plan outlines the steps to allow users to fetch Chess.com games and analyze them against their stored repertoires through the web dashboard.

## User Review Required

> [!IMPORTANT]
> The analysis might take some time depending on the number of games fetched from Chess.com. I will implement a basic loading state for this.

## Proposed Changes

### Backend Implementation

#### [MODIFY] [main.py](file:///home/msok/projects/opening/src/web/main.py)
- Create a new POST endpoint `/analysis/run`.
- Parameters: `username`, `year`, `month`, `color` (optional).
- Logic:
    1.  Fetch user's repertoire(s) from the SQLite database.
    2.  Fetch games from Chess.com for the given year/month.
    3.  Generate a report using `create_index_html`.
    4.  Return the path to the report.

### Frontend Implementation

#### [MODIFY] [index.html](file:///home/msok/projects/opening/src/web/static/index.html)
- Update `success-step` to include:
    - Game filter inputs (Year, Month).
    - "Find Divergences" button.
    - Result container for the report link.

#### [MODIFY] [app.js](file:///home/msok/projects/opening/src/web/static/js/app.js)
- Implement `findDivergences` logic.
- Handle state transitions during analysis.
- Link the final report for the user to open.

### Styling & Fixes

#### [MODIFY] [single_game.html](file:///home/msok/projects/opening/src/visualization/templates/single_game.html)
- Fix Jinja2 CSS loading syntax.
- Ensure `.move.current` highlight is clearly visible.

#### [MODIFY] [multi_game.html](file:///home/msok/projects/opening/src/visualization/templates/multi_game.html)
- Fix Jinja2 CSS loading syntax.

## Verification Plan

### Automated Tests
- Create `tests/web/test_analysis.py` to test the new endpoint logic (mocking external API calls).

### Manual Verification
1.  Upload a repertoire.
2.  Select a Year/Month where games exist on Chess.com.
3.  Click "Find Divergences".
4.  Verify the report is generated and opens correctly with glassmorphism styling.
5.  Navigate moves in the report and verify background selection works.
