# Mobile Friendly Templates

Add mobile-optimized HTML templates to provide a better viewing experience on phones and small screens.

## Proposed Changes

### Visualization Templates

#### [NEW] [mobile/index.html](file:///home/msok/projects/opening/src/visualization/templates/mobile/index.html)
- Responsive list layout.
- Larger game items for easier tapping.
- Simplified header for mobile screens.

#### [NEW] [mobile/single_game.html](file:///home/msok/projects/opening/src/visualization/templates/mobile/single_game.html)
- Vertical layout (Board on top, controls in middle, moves at bottom).
- Full-width board with `aspect-ratio: 1/1`.
- Large touch-friendly navigation buttons.
- Sticky header for player info.

#### [NEW] [mobile/multi_game.html](file:///home/msok/projects/opening/src/visualization/templates/mobile/multi_game.html)
- Similar to `single_game_mobile` but with an easy-to-use game selection dropdown or slider.

### Visualization Logic

#### [MODIFY] [chess_display.py](file:///home/msok/projects/opening/src/visualization/chess_display.py)
- Update `display_game_from_string` and `create_index_html` to accept a `template_variant` parameter (defaulting to "standard").
- If `template_variant="mobile"`, load templates from the `mobile/` subdirectory.

## Verification Plan

### Manual Verification
- Generate a report using the `mobile` variant.
- Open the resulting HTML and resize the browser to phone dimensions (e.g., 375x667).
- Verify that the board is correctly sized and buttons are easy to click.
- Ensure all JS logic (move navigation, divergence highlighting) works correctly.
