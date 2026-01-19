# Goal: Optimize Chess.com API Fetching

Minimize API calls to Chess.com by filtering monthly archive URLs based on the provided `start_date` and `end_date` before fetching game data.

## Proposed Changes

### API Integration [MODIFY]

#### [MODIFY] [chesscom_api.py](file:///home/msok/projects/opening/src/api/chesscom_api.py)
- **`get_all_user_games`**:
  - Extract year and month from each archive URL.
  - Filter `archive_urls` to only include those that could contain games within the `[start_date, end_date]` range.
  - Fetch games only from the filtered archives.

## Verification Plan

### Automated Tests
- Create a new unit test in `tests/api/test_chesscom_api_optimization.py`:
  - Mock the archives response with multiple months.
  - Call `get_all_user_games` with a specific date range (e.g., last 7 days).
  - Assert that `requests.get` is only called for the relevant archives.
  - Assert that the final result is correctly filtered.
- Run existing tests to ensure no regressions.

### Manual Verification
- Run `run_final_mdb_analysis.py` and observe that it behaves correctly and (if logging were added) shows fewer requests.
