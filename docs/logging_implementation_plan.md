# Implementing Logging

Replace all `print` statements in the `src/` directory with a structured `logging` system.

## Proposed Changes

### Logging setup
- Use the standard Python `logging` module.
- In each module, define a logger using `logger = logging.getLogger(__name__)`.

### Affected Files

#### [MODIFY] [chesscom_api.py](file:///home/msok/projects/opening/src/api/chesscom_api.py)
Replace warning prints with `logger.warning`.

#### [MODIFY] [chess_display.py](file:///home/msok/projects/opening/src/visualization/chess_display.py)
Replace error and warning prints with `logger.error` and `logger.warning`.

#### [MODIFY] [repertoire_manager.py](file:///home/msok/projects/opening/src/opening/repertoire_manager.py)
Replace status prints with `logger.info`.

#### [MODIFY] [pgn_tree_parser.py](file:///home/msok/projects/opening/src/parsers/pgn_tree_parser.py)
Replace prints in the `__main__` block and examples with `logger.info`.

## Verification Plan

### Automated Tests
- Run existing tests to ensure no regressions.

### Manual Verification
- Run `run_final_mdb_analysis.py` and verify that output is correctly controlled by logging configuration (if any) or defaults to stderr.
