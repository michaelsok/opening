# Database Integration for Repertoires Walkthrough

I have successfully integrated a local SQLite database to store and manage uploaded chess repertoires. This fulfills the first step of the project expansion plan.

## Changes Made

### 1. Database Layer
- Created [database.py](file:///home/msok/projects/opening/src/web/database.py) which handles SQLite connections and schema initialization.
- Repertoires are stored in a table with fields for `username`, `color`, `filename`, and `pgn_content`.
- Implemented robust "Upsert" logic where uploading a new repertoire for the same user and color overwrites the previous one.

### 2. Refactored Upload Flow
- Updated `handle_repertoire_upload` in [repertoire.py](file:///home/msok/projects/opening/src/web/repertoire.py) to save the PGN content to the database before proceeding with the filesystem-based splitting.
- Added a startup event in [main.py](file:///home/msok/projects/opening/src/web/main.py) to ensure the database is ready as soon as the application launches.

### 3. Verification

#### Automated Tests
- Created [test_database.py](file:///home/msok/projects/opening/tests/web/test_database.py) to verify all CRUD operations.
- All tests passed:
```bash
pytest tests/web/test_database.py
# Output: 4 passed in 0.10s
```

#### Manual Verification
- Verified the complete flow using `curl` to upload repertoires to a running instance of the server.
- Confirmed the data was correctly written to the SQLite database file at `src/web/data/opening.db`.

```bash
sqlite3 src/web/data/opening.db "SELECT username, color FROM repertoires;"
# Output:
# tester|white
# tester|black
```

## Next steps
- Implement the feature to find divergences on chess.com games using these stored repertoires.
- Fix broken move background selection on game pages.
