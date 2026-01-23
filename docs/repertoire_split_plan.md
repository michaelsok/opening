# Splitting Opening Repertoire by Category

This plan outlines the creation of a function to split a single large repertoire PGN file into multiple smaller files, categorized by opening type (e.g., Sicilian Defense, Italian Game).

## User Review Required

> [!NOTE]
> Categorization will be based on hardcoded move prefixes for major openings. Variations that don't match a specific major opening will be grouped into broader categories (e.g., "1. e4 Miscellaneous") or kept in a "General" file.

## Proposed Changes

### Opening Logic

#### [NEW] [repertoire_manager.py](file:///home/msok/projects/opening/src/opening/repertoire_manager.py)
Implement `split_repertoire_by_opening` function and opening classification logic.

- Define `OPENING_CLASSIFICATIONS`: A list of tuples `(name, move_list)` ordered from most specific to least specific.
- Implement `classify_opening(moves: List[str]) -> str`: Returns the category name.
- Implement `split_repertoire_by_opening(pgn_file: str, output_dir: str)`:
    - Reads the PGN.
    - If it's a single game tree (like the user's example), it "unrolls" the variations into separate paths.
    - Each path is classified.
    - Paths are grouped by classification and merged back into trees.
    - Each grouped tree is written to a unique PGN file.

## Verification Plan

### Automated Tests
- Create `tests/opening/test_repertoire_manager.py`.
- Test with a small PGN containing `1. e4 e5`, `1. e4 c5`, and `1. e4 e6`.
- Verify that three files are created: `italian_game.pgn` (if path matches), `sicilian_defense.pgn`, and `french_defense.pgn`.

### Manual Verification
- Run the script on the user's white repertoire file: `/home/msok/projects/opening/openings/white/White-2026-01-19T23_02_45.457Z.pgn`.
- Inspect the `openings/white/split/` directory for categorized files.
