# Goal: Convert Verification Scripts to Unit Tests

Convert existing ad-hoc verification scripts into a proper `pytest` test suite to ensure long-term maintainability and automated verification.

## Proposed Changes

### Tests [NEW]

#### [NEW] [test_divergence.py](file:///home/msok/projects/opening/tests/test_divergence.py)
- Convert `reproduce_divergence_bug.py` logic into a pytest test case.
- Assert correct `divergenceMoveIndex` in the generated HTML.

#### [NEW] [test_orientation.py](file:///home/msok/projects/opening/tests/test_orientation.py)
- Convert `verify_board_orientation.py` logic into pytest test cases for White and Black orientations.
- Assert that HTML content differs as expected.

#### [NEW] [test_repertoire_loading.py](file:///home/msok/projects/opening/tests/test_repertoire_loading.py)
- Convert `verify_directory_repertoire.py` logic into pytest test cases using temporary directories for test PGNs.
- Assert correct repertoire matching for multiple PGNs in subdirectories.

#### [NEW] [test_index_labels.py](file:///home/msok/projects/opening/tests/test_index_labels.py)
- Convert `verify_index_labels.py` logic into pytest test cases.
- Assert correct labels ("Opponent diverges at:", etc.) and green styling.

### Cleanup

#### [DELETE] [reproduce_divergence_bug.py](file:///home/msok/projects/opening/reproduce_divergence_bug.py)
#### [DELETE] [verify_board_orientation.py](file:///home/msok/projects/opening/verify_board_orientation.py)
#### [DELETE] [verify_directory_repertoire.py](file:///home/msok/projects/opening/verify_directory_repertoire.py)
#### [DELETE] [verify_index_labels.py](file:///home/msok/projects/opening/verify_index_labels.py)

## Verification Plan

### Automated Tests
- Run `pytest` and ensure all tests pass.
- Example: `pytest tests/`
