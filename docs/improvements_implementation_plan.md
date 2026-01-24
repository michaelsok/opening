# Divergence Analysis Improvements Plan

This plan addresses the new requirements: real-time progress display, date filtering, and performance optimization for large repertoires.

## Proposed Changes

### Backend: Progress and Date Filter

#### [MODIFY] [chess_display.py](file:///home/msok/projects/opening/src/visualization/chess_display.py)
- Update `create_index_html` to accept an optional `progress_callback(current, total)`.
- Trigger the callback after each game is processed.
- **Optimization**: Modify the loading logic to merge all relevant repertoire PGNs into a single `PGNTree`. This will drastically speed up divergence finding for large repertoires.

#### [MODIFY] [main.py](file:///home/msok/projects/opening/src/web/main.py)
- Refactor `/analysis/run` to yield progress updates.
- Accept a `start_date` parameter (e.g., "YYYY-MM-DD").
- Use `get_user_games` with the `start_date` filter.
- Stream JSON chunks representing progress: `{ "type": "progress", "remaining": N, "total": M }`.
- Final chunk: `{ "type": "complete", "report_url": "..." }`.

### Frontend: Dashboard Updates

#### [MODIFY] [index.html](file:///home/msok/projects/opening/src/web/static/index.html)
- Add a "Start Date" date picker next to Year/Month.
- Add a progress tracker UI (e.g., a progress bar or text indicator).

#### [MODIFY] [app.js](file:///home/msok/projects/opening/src/web/static/js/app.js)
- Update `runAnalysisBtn` handler to handle streaming responses using the Fetch API's `ReadableStream`.
- Update the UI in real-time as progress chunks are received.

## Verification Plan

### Automated Tests
- Test date filtering by mocking Chess.com API responses.
- Verify merged PGN tree correctly identifies divergence points.

### Manual Verification
1.  Upload a large repertoire (e.g., 500+ lines).
2.  Set a start date to filter recent games.
3.  Click "Find Games & Divergences" and verify:
    -   Progress updates in real-time.
    -   Analysis completes much faster than before.
    -   Report only contains games played on/after the start date.
