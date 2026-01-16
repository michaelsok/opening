# Refactor chess_display.py to use Jinja2 templates

## User Review Required
> [!NOTE]
> This refactor extracts large HTML string blocks into separate Jinja2 template files for better maintainability.

## Proposed Changes

### `src/visualization`

#### [NEW] `templates/single_game.html`
- Extracted from `_generate_html_content`
- Will use Jinja2 syntax for loops and conditionals

#### [NEW] `templates/multi_game.html`
- Extracted from `_generate_multi_game_html_content`

#### [NEW] `templates/index.html`
- Extracted from `_generate_index_html_content`

#### [MODIFY] `chess_display.py`
- Import `jinja2`
- Initialize Jinja2 Environment pointing to `src/visualization/templates`
- Update `_generate_html_content` to render `single_game.html`
- Update `_generate_multi_game_html_content` to render `multi_game.html`
- Update `_generate_index_html_content` to render `index.html`

## Verification Plan

### Automated Tests
Run existing tests to ensure no regression:
```bash
pytest tests/visualization/test_chess_display.py tests/visualization/test_divergence_display.py tests/visualization/test_index_html.py
```

### Manual Verification
- None required as automated tests cover the file generation and basic content checks.
