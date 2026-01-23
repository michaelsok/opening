# Repertoire Splitting Walkthrough

I have implemented a repertoire splitting tool that categorizes large PGN repertoire files (e.g., from chessbook.com) into smaller, opening-specific files.

## Changes Made

### Opening Logic
- **[repertoire_manager.py](file:///home/msok/projects/opening/src/opening/repertoire_manager.py)**: Implemented `split_repertoire_by_opening`. This function:
    1. Unrolls a PGN game tree into individual move paths.
    2. Classifies each path using a predefined list of major opening sequences.
    3. Re-merges these paths into a clean, hierarchical tree for each category.
    4. Writes the results to separate files (e.g., `sicilian_defense.pgn`, `french_defense.pgn`).

### Testing
- **[test_repertoire_manager.py](file:///home/msok/projects/opening/tests/opening/test_repertoire_manager.py)**: Added unit tests for classification and the splitting process.

## Verification Results

### Automated Tests
Ran `pytest tests/opening/test_repertoire_manager.py`:
```text
tests/opening/test_repertoire_manager.py ...                             [100%]
============================== 3 passed in 0.34s ===============================
```

### Manual Verification
Processed the user's repertoire files:
- **White Repertoire**: Generated files in `openings/white/split/` (Sicilian, French, King's Gambit, etc.).
- **Black Repertoire**: Generated files in `openings/black/split/`.

Example output (`openings/white/split/sicilian_defense.pgn`):
Vertical merging was successful, showing a clean tree starting from `1. e4 c5`.

```pgn
[Event "Sicilian Defense Repertoire"]
...
9: 1. e4 c5 2. Nf3 Nc6 ( 2... d6 3. d4 cxd4 4. Nxd4 Nf6 ...
```
