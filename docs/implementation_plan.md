# Plan: Fix Main Variant Interactivity

The user reported that clicking main game moves no longer works once an opening variation has been selected. This is likely due to an issue in the `switchToVariant('main')` logic or the click handlers in `single_game.html`.

## Proposed Changes

### [Component Name] Visualization Templates

#### [MODIFY] [single_game.html](file:///home/msok/projects/opening/src/visualization/templates/single_game.html)
- Remove the call to `setupMoveButtons()` in the `init()` function as it is not defined and causes a script execution error.
- Refactor move list click handlers to use event delegation on the `.move-list` container. This will make the interaction more robust and ensure that switching between main game and variations works correctly.
- Ensure that clicking a main game move while in 'opening' view mode correctly triggers `switchToVariant('main')`.

### [Component Name] Visualization Logic

#### [MODIFY] [chess_display.py](file:///home/msok/projects/opening/src/visualization/chess_display.py)
- Double check that `positions_json` and `boards_json` are correctly passed and that `positions_json` matches the moves in `moves_san`.

## Verification Plan

### Automated Tests
- Regenerate games using `display_game_example.py`.
- Inspect the generated HTML for valid click handlers and state management.

### Manual Verification
- Manually check the behavior in the browser (if possible through instructions to the user or by inspecting the code logic).
