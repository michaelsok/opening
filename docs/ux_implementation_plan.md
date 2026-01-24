# UX and Navigation Improvements Plan

This plan addresses the UI/UX issues in the divergence analysis, including progress reporting, filters, navigation, and styling.

## Proposed Changes

### Backend: Enhanced Analysis and Unique Reports

#### [MODIFY] [chesscom_api.py](file:///home/msok/projects/opening/src/api/chesscom_api.py)
- Update `get_all_user_games` and intermediate functions to accept an optional `progress_callback(current, total, message)`.
- Use this callback to report progress while fetching and parsing Chess.com monthly archives.

#### [MODIFY] [main.py](file:///home/msok/projects/opening/src/web/main.py)
- Update `/analysis/run` request parameters:
    - Replace `year`/`month` with `start_date` and `end_date`.
    - Add `time_class` (e.g., blitz, rapid).
- Logic updates:
    - Create a unique directory for each report: `reports/<username>_<timestamp>/`.
    - Provide a `progress_callback` to `get_all_user_games` to stream fetching status.
    - Path the final report to `.../index.html`.

### Frontend: Granular Filtering and Feedback

#### [MODIFY] [index.html](file:///home/msok/projects/opening/src/web/static/index.html)
- Overhaul the analysis filter section:
    - Remove Year and Month dropdowns.
    - Add "Start Date" and "End Date" (`<input type="date">`).
    - Add "Time Control" select (Blitz, Bullet, Rapid, Daily).

#### [MODIFY] [app.js](file:///home/msok/projects/opening/src/web/static/js/app.js)
- Update `runAnalysisBtn` handler to collect new filter values.
- Handle potential new SSE/Stream message types if needed.

### Templating and Styling Fixes

#### [MODIFY] [single_game.html](file:///home/msok/projects/opening/src/visualization/templates/single_game.html)
#### [MODIFY] [multi_game.html](file:///home/msok/projects/opening/src/visualization/templates/multi_game.html)
#### [MODIFY] [index.html](file:///home/msok/projects/opening/src/visualization/templates/index.html)
- **CRITICAL**: Fix Jinja2 CSS syntax `{{ 'reports.css' | load_css | safe }}`.
- Ensure the background is consistently applied from `reports.css`.

## Verification Plan

### Automated Tests
- Update tests in `tests/api/test_chesscom.py` (if any) to verify date range fetching.

### Manual Verification
1.  Run the dashboard.
2.  Start an analysis for a 3-month range.
3.  Verify the progress bar updates while archives are being fetched ("Fetching archive 1/3...").
4.  Verify the report opens in a unique directory and all game links work.
5.  Verify the background matches the main connection page.
