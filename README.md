# Chess PGN Tree Parser

A Python module for reading chess PGN (Portable Game Notation) files and parsing moves into a tree structure.

## Features

- Reads PGN files and parses chess moves into a tree structure
- Handles multiple games in a single PGN file
- Supports variations (alternative moves) in the tree
- Provides utilities to navigate and query the move tree

## Installation

Install the required dependency:

```bash
pip install -r requirements.txt
```

## Project Structure

```
opening/
├── src/
│   └── parsers/
│       ├── __init__.py
│       └── pgn_tree_parser.py
├── tests/
│   ├── __init__.py
│   └── test_pgn_tree_parser.py
├── requirements.txt
└── README.md
```

## Usage

### Basic Usage

```python
from src.parsers.pgn_tree_parser import parse_pgn_to_tree

# Parse a PGN file
tree = parse_pgn_to_tree("games.pgn")

# Access the root node (starting position)
root = tree.root

# Get all unique paths through the tree
paths = tree.get_all_paths()

# Get a specific node at a path of moves
node = tree.get_node_at_path(["e4", "e5", "Nf3"])
if node:
    print(f"Possible moves: {list(node.children.keys())}")
```

### Parse from String

```python
from src.parsers.pgn_tree_parser import parse_pgn_string_to_tree

pgn_content = """
[Event "Test Game"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0
"""

tree = parse_pgn_string_to_tree(pgn_content)
```

### Tree Structure

The tree is built using `MoveNode` objects:
- Each node represents a chess position
- Edges represent moves
- The root node represents the starting position
- Children are stored as a dictionary mapping move notation (SAN) to child nodes

### Accessing Game Information

```python
tree = parse_pgn_to_tree("games.pgn")

# Access game metadata
for game_info in tree.games:
    print(f"Event: {game_info.get('Event')}")
    print(f"White: {game_info.get('White')}")
    print(f"Black: {game_info.get('Black')}")
```

## Running Tests

Run the test suite with pytest:

```bash
pytest tests/
```

## Example

See the `__main__` section in `src/parsers/pgn_tree_parser.py` for a complete example.
