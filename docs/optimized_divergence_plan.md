# Optimized Divergence Finding

This plan outlines the optimization of the repertoire divergence analysis by filtering games by opening category first and lazily loading only the necessary repertoire files.

## User Review Required

> [!NOTE]
> Categorization will be based on hardcoded move prefixes for major openings. Variations that don't match a specific major opening will be grouped into broader categories (e.g., "1. e4 Miscellaneous") or kept in a "General" file.

## Proposed Changes

### Opening Logic

#### [NEW] [definitions.py](file:///home/msok/projects/opening/src/opening/definitions.py)
Centralize `OPENING_DEFINITIONS`, `classify_opening`, and `get_filename_from_category`.

#### [MODIFY] [repertoire_manager.py](file:///home/msok/projects/opening/src/opening/repertoire_manager.py)
Use the centralized definitions.

### Visualization and Analysis

#### [MODIFY] [chess_display.py](file:///home/msok/projects/opening/src/visualization/chess_display.py)
Optimize `create_index_html` (and diverge point finding):
- Map the repertoire directory into a dictionary of `category -> path`.
- For each game:
    1. Extract the move sequence.
    2. Use `classify_opening` to get the category.
    3. Look up the PGN file(s) for that category.
    4. Only load and parse the tree for the relevant opening.
    5. Cache the parsed trees for subsequent games of the same opening.
- This avoids building trees for the entire repertoire directory upfront.

## Verification Plan

### Performance Check
- Compare the execution time of `analyze_user_openings` before and after optimization on a large set of games.

### Correctness Check
- Ensure that the divergence points found are identical to the non-optimized version.
