# Improve Divergence Display

## Goal Description
Update the divergence display in the chess game viewer to mimic Lichess style. This means showing the opening repertoire moves (from which the game diverged) as an inline variation within the move list, rather than as a separate block or modal.

## User Review Required
> [!NOTE]
> This change modifies how divergence is presented. Instead of a "Choose your path" interaction, the divergence will be shown as a variation line `(move ...)` within the main text.

## Proposed Changes

### `src/visualization`

#### [MODIFY] [chess_display.py](file:///home/msok/projects/opening/src/visualization/chess_display.py)
- Update data preparation logic to format the opening repertoire variant moves as a secondary "line" or pass them structured for inline rendering.
- Remove logic related to the "variant selection" modal/buttons if they are no longer needed, or keep them as auxiliary controls.

#### [MODIFY] [templates/single_game.html](file:///home/msok/projects/opening/src/visualization/templates/single_game.html)
- Remove the `divergence-choice` div.
- Update the move list rendering loop:
    - Identify the divergence point.
    - Insert the opening variant moves as a variation block `( ... )` immediately after the divergence point (or before/parallel to the game move depending on Lichess exact style effectively).
    - Style the variation moves (e.g., grey color, smaller font).
    - Ensure variation moves are clickable and update the board state.
- Update JavaScript:
    - Handle clicking on variation moves.
    - Implement `showVariantMove(index)` to switch context and update board.
    - Maintain state for "viewing main line" vs "viewing variation".
    - Update highlighting logic to show current selected move within variation (blue highlight).

#### [MODIFY] [templates/multi_game.html](file:///home/msok/projects/opening/src/visualization/templates/multi_game.html)
- Apply similar styling changes to the multi-game viewer if consistent.

## Verification Plan

### Automated Tests
- Run existing tests: `pytest tests/visualization/test_chess_display.py`
- Verify that the HTML output contains the variation structure.

- [x] Generate a game with known divergence.
- [x] Open the HTML file in a browser.
- [x] Verify that the opening moves appear as a parenthesized variation inline.
- [x] Click variation moves to ensure the board updates correctly.
