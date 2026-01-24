# Database Integration for Repertoires

This plan outlines the steps to store uploaded chess repertoires in a local SQLite database instead of only relying on the filesystem. This will improve data management and provide a foundation for future features like repertoire history and user-specific filtered analysis.

## Proposed Changes

### [NEW] [database.py](file:///home/msok/projects/opening/src/web/database.py)
A new module to manage SQLite database connections and operations.
- Initialize database at `src/web/data/opening.db`.
- Create `repertoires` table: `id`, `username`, `color`, `filename`, `pgn_content`, `created_at`.
- Functions: `save_repertoire`, `get_repertoires_by_user`, `delete_repertoire`.

### [MODIFY] [repertoire.py](file:///home/msok/projects/opening/src/web/repertoire.py)
Update `handle_repertoire_upload` to integrate with the database.
- Import functions from `database.py`.
- After splitting the repertoire (for classification), save the original PGN and classification results to the database.
- Maintain existing filesystem split logic for now to avoid breaking the divergence analysis which relies on directory structures (or update it to use DB content).

### [MODIFY] [main.py](file:///home/msok/projects/opening/src/web/main.py)
Ensure the FastAPI app initializes the database on startup.
- Add an `on_event("startup")` handler to run DB migrations/initialization.

## Verification Plan

### Automated Tests
- Create `tests/web/test_database.py` to verify:
    - DB initialization.
    - Saving a repertoire correctly stores the PGN.
    - Retrieving repertoires by username returns correct data.
    - Duplicate uploads (same user/color) are handled (overwrite or new entry).

### Manual Verification
1.  Connect to the web application.
2.  Upload a White repertoire.
3.  Upload a Black repertoire.
4.  Check the database file `src/web/data/opening.db` (using `sqlite3` CLI) to confirm data is present.
