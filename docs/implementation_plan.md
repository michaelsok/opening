# Implementation Plan - Variation Switching UI

The goal is to allow users to switch between the "Opening Repertoire" and "Game Continuation" paths after a divergence point is reached in the chess game.

## Proposed Changes

### [Visualization Component]

#### [MODIFY] [single_game.html](file:///home/msok/projects/opening/src/visualization/templates/single_game.html)
- Add CSS for a "variation-toggle" UI.
- Add a UI element (e.g., buttons) to switch between "Opening Repertoire" and "Game Continuation" when a divergence is present.
- Update `switchToVariant(mode)` to support `mode === 'game'` using `gameVariantBoards` and `gameVariantPositions`.
- Display the Game Continuation moves as a clickable list when in 'game' mode, similar to how the main moves or opening variations are displayed.
- Ensure that clicking a move in the main list correctly switches back to 'main' mode.

## Verification Plan

### Automated Tests
- No automated tests for UI changes, but I will manually verify using the example script.

### Manual Verification
- Run `examples/display_game_example.py`.
- Open a generated HTML file with a divergence (e.g., `game_4_with_divergence.html`).
- Click on an opening variation move to switch to "Opening" mode.
- Verify that a button or toggle exists to switch to "Game Continuation".
- Click "Game Continuation" and verify the board updates to the moves actually played in the game.
- Verify navigation works in both modes.
- Verify clicking a move in the main list switches back to 'main' mode.
