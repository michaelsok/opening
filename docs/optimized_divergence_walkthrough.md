# Optimized Divergence Finding Walkthrough

I have optimized the divergence finding logic to be significantly more efficient and targeted.

## Changes Made

### Opening Definitions
- **[definitions.py](file:///home/msok/projects/opening/src/opening/definitions.py)**: Created a centralized location for opening move sequences and classification logic. This ensures consistency between repertoire splitting and game analysis.

### Optimized Analysis Logic
- **[chess_display.py](file:///home/msok/projects/opening/src/visualization/chess_display.py)**: Refactored `create_index_html` to:
    1. **Map Repertoire Directory**: Index all categorized PGN files (e.g., `sicilian_defense.pgn`, `kings_gambit.pgn`) from the `split/` directories.
    2. **Classify Each Game**: For every user game, classify it first to determine its opening category.
    3. **Lazy Loading and Caching**: Only load and parse the repertoire tree for the specific category a game belongs to. Use a cache to store previously parsed trees, avoiding redundant work for multiple games of the same opening.
    4. **Targeted Comparison**: Find divergence by comparing the game only against the relevant repertoire tree.

## Verification Results

### Success
Ran `run_final_mdb_analysis.py` for user **ChessMDB**:
- The report was generated successfully at `/home/msok/projects/opening/reports/chessmdb_refined_analysis.html`.
- Games are correctly classified into their respective categories before comparison.
- Processing remains fast even as the number of repertoire files increases.

### Performance
The script no longer builds the entire repertoire tree upfront, which reduces initial memory usage and startup time, especially when many split PGNs are present.
