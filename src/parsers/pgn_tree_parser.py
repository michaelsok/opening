"""
Chess PGN file parser that converts moves into a tree structure.

This module provides functionality to read PGN files and parse chess moves
into a tree structure where each node represents a position, and edges represent moves.
"""

import chess
import chess.pgn
import io
from typing import Optional, Dict, List, Tuple
from collections import defaultdict


class MoveNode:
    """Represents a node in the move tree."""
    
    def __init__(self, move: Optional[chess.Move] = None, parent: Optional['MoveNode'] = None):
        self.move = move  # The move that led to this position
        self.parent = parent
        self.children: Dict[str, 'MoveNode'] = {}  # Dictionary of move_san -> MoveNode
        self.position_fen: Optional[str] = None  # FEN representation of the position
        self.move_count: int = 0  # Move number in the game
        
    def add_child(self, move_san: str, move: chess.Move, board: chess.Board) -> 'MoveNode':
        """Add a child node for a given move."""
        child = MoveNode(move, self)
        child.position_fen = board.fen()
        child.move_count = self.move_count + 1
        self.children[move_san] = child
        return child
    
    def __repr__(self):
        move_str = self.move.uci() if self.move else "root"
        return f"MoveNode(move={move_str}, children={len(self.children)})"


class PGNTree:
    """Represents a tree of chess moves parsed from a PGN file."""
    
    def __init__(self):
        self.root = MoveNode()  # Root node (starting position)
        self.root.position_fen = chess.Board().fen()
        self.games: List[Dict] = []  # Store game metadata
        
    def add_game(self, game: chess.pgn.Game):
        """Add a game to the tree, merging moves with existing tree."""
        # Store game metadata
        headers = dict(game.headers)
        self.games.append(headers)
        
        # Traverse the game and add moves to tree
        # The game root doesn't have a move, so start from its variations
        board = chess.Board()
        for variation in game.variations:
            self._add_variation(variation, self.root, board.copy())
    
    def _add_variation(self, node: chess.pgn.GameNode, tree_node: MoveNode, board: chess.Board):
        """Recursively add moves from a PGN game node to the tree."""
        if node.move:
            # Get the move in standard algebraic notation
            move_san = board.san(node.move)
            
            # If this variation already exists, use it; otherwise create new
            if move_san in tree_node.children:
                next_tree_node = tree_node.children[move_san]
            else:
                board.push(node.move)
                next_tree_node = tree_node.add_child(move_san, node.move, board)
                board.pop()
            
            # Push the move to the board
            board.push(node.move)
            
            # Process all variations (main line and alternatives)
            for variation in node.variations:
                # Create a copy of the board for each variation
                alt_board = board.copy()
                self._add_variation(variation, next_tree_node, alt_board)
            
            board.pop()
    
    def get_all_paths(self, node: Optional[MoveNode] = None, path: List[str] = None) -> List[List[str]]:
        """Get all paths (sequences of moves) from the tree."""
        if node is None:
            node = self.root
        if path is None:
            path = []
        
        if not node.children:
            return [path] if path else []
        
        all_paths = []
        for move_san, child in node.children.items():
            new_path = path + [move_san]
            child_paths = self.get_all_paths(child, new_path)
            all_paths.extend(child_paths)
        
        return all_paths
    
    def get_node_at_path(self, moves: List[str]) -> Optional[MoveNode]:
        """Get a node at a specific path of moves."""
        current = self.root
        for move_san in moves:
            if move_san not in current.children:
                return None
            current = current.children[move_san]
        return current


def parse_pgn_to_tree(pgn_file_path: str) -> PGNTree:
    """
    Read a PGN file and parse the moves into a tree structure.
    
    Args:
        pgn_file_path: Path to the PGN file to read
        
    Returns:
        PGNTree: A tree structure containing all moves from the PGN file
        
    Example:
        >>> tree = parse_pgn_to_tree("games.pgn")
        >>> # Access the root node
        >>> root = tree.root
        >>> # Get all paths
        >>> paths = tree.get_all_paths()
        >>> # Get a specific node
        >>> node = tree.get_node_at_path(["e4", "e5", "Nf3"])
    """
    tree = PGNTree()
    
    try:
        with open(pgn_file_path, 'r', encoding='utf-8') as pgn_file:
            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break
                tree.add_game(game)
    except FileNotFoundError:
        raise FileNotFoundError(f"PGN file not found: {pgn_file_path}")
    except Exception as e:
        raise Exception(f"Error reading PGN file: {e}")
    
    return tree


def parse_pgn_string_to_tree(pgn_string: str) -> PGNTree:
    """
    Parse a PGN string and convert moves into a tree structure.
    
    Args:
        pgn_string: PGN content as a string
        
    Returns:
        PGNTree: A tree structure containing all moves from the PGN string
    """
    tree = PGNTree()
    
    try:
        pgn_io = io.StringIO(pgn_string)
        while True:
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                break
            tree.add_game(game)
    except Exception as e:
        raise Exception(f"Error parsing PGN string: {e}")
    
    return tree


def find_divergence_point(game_tree: PGNTree, opening_tree: PGNTree) -> List[str]:
    """
    Find the move where the game diverges from the opening.
    
    This function compares the game tree's main line against the opening tree
    and returns the path (list of moves in SAN notation) up to and including
    the first move where the game diverges from the opening.
    
    Args:
        game_tree: PGNTree representing the game to analyze
        opening_tree: PGNTree representing the opening repertoire
        
    Returns:
        List[str]: A list of moves (in SAN notation with move numbers) representing 
                  the path up to and including the divergence point. 
                  Format: ["1. e4", "1... e5", "2. Nf3", "2... Nc6", ...]
                  Returns empty list if:
                  - Game matches opening completely (all moves exist in opening)
                  - Game tree is empty
                  
    Example:
        >>> opening_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
        >>> game_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bc4 1-0"
        >>> opening_tree = parse_pgn_string_to_tree(opening_pgn)
        >>> game_tree = parse_pgn_string_to_tree(game_pgn)
        >>> divergence = find_divergence_point(game_tree, opening_tree)
        >>> print(divergence)  # ['1. e4', '1... e5', '2. Nf3', '2... Nc6', '3. Bc4']
    """
    # Get the main line (first path) from the game tree
    game_paths = game_tree.get_all_paths()
    
    # If game tree is empty, return empty list
    if not game_paths or not game_paths[0]:
        return []
    
    game_main_line = game_paths[0]
    divergence_path = []
    
    # Navigate through the opening tree following the game's moves
    current_opening_node = opening_tree.root
    
    for move_index, move_san in enumerate(game_main_line):
        # Calculate move number: moves are numbered in pairs (white, black)
        # Index 0,1 = move 1; index 2,3 = move 2; etc.
        move_number = (move_index // 2) + 1
        
        # Check if this move exists in the opening tree at the current position
        if move_san in current_opening_node.children:
            # Move exists in opening, continue following the path
            # Format: "1. e4" for white, "1. e5" for black (or "1... e5" for black)
            if move_index % 2 == 0:  # White move
                divergence_path.append(f"{move_number}. {move_san}")
            else:  # Black move
                divergence_path.append(f"{move_number}... {move_san}")
            current_opening_node = current_opening_node.children[move_san]
        else:
            # Move doesn't exist in opening - this is the divergence point
            if move_index % 2 == 0:  # White move
                divergence_path.append(f"{move_number}. {move_san}")
            else:  # Black move
                divergence_path.append(f"{move_number}... {move_san}")
            return divergence_path
    
    # All moves in game exist in opening - game follows opening completely
    return []


def get_diverging_move(divergence_point: List[str], game_tree: PGNTree) -> Optional[str]:
    """
    Determine if the game diverges from the opening and return the diverging move.
    
    This function takes the divergence point (from find_divergence_point) and
    returns only the move that actually diverges from the opening, if any.
    
    Args:
        divergence_point: List of moves (with move numbers) from find_divergence_point
        game_tree: PGNTree representing the game (currently unused but kept for API consistency)
        
    Returns:
        Optional[str]: The diverging move with move number (e.g., "3. Bc4" or "1... c5"),
                      or None if the game does not diverge from the opening.
                      
    Example:
        >>> opening_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
        >>> game_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bc4 1-0"
        >>> opening_tree = parse_pgn_string_to_tree(opening_pgn)
        >>> game_tree = parse_pgn_string_to_tree(game_pgn)
        >>> divergence_point = find_divergence_point(game_tree, opening_tree)
        >>> diverging_move = get_diverging_move(divergence_point, game_tree)
        >>> print(diverging_move)  # "3. Bc4"
    """
    # If divergence point is empty, game matches opening completely
    if not divergence_point:
        return None
    
    # The last move in the divergence point is the one that actually diverges
    return divergence_point[-1]


def find_first_divergence_across_openings(game_tree, opening_trees):
    """
    Given a game_tree and a list of opening_trees, returns the first divergence point and index
    of the matching opening. If the game does not match any opening, returns the divergence point and None.
    Args:
        game_tree: PGNTree of the game
        opening_trees: list of PGNTree (openings)
    Returns:
        (divergence_point: List[str], matching_opening_index: Optional[int])
    """
    best_idx = None
    best_divergence = None
    best_match_len = -1

    for idx, opening_tree in enumerate(opening_trees):
        divergence = find_divergence_point(game_tree, opening_tree)
        if divergence == []:
            return divergence, idx
        # The best match is the opening that shares the most moves before diverging
        match_len = len(divergence)
        # If idx==0 or if we have a longer prefix that matches (i.e., later divergence), update
        if best_divergence is None or match_len > best_match_len:
            best_divergence = divergence
            best_idx = None  # Not a complete match
            best_match_len = match_len
    return best_divergence, best_idx

# Example usage
if __name__ == "__main__":
    # Example: Create a sample PGN file for testing
    sample_pgn = """[Event "Test Game"]
[Site "Test"]
[Date "2024.01.01"]
[Round "1"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7 11. c4 c6 12. cxb5 axb5 13. Nc3 Bb7 14. Bg5 b4 15. Nb1 h6 16. Bh4 c5 17. dxe5 Nxe4 18. Bxe7 Qxe7 19. exd6 Qf6 20. Nbd2 Nxd6 21. Nc4 Nxc4 22. Bxc4 Nb6 23. Ne5 Rae8 24. Bxf7+ Rxf7 25. Nxf7 Rxe1+ 26. Qxe1 Kxf7 27. Qe3 Qg5 28. Qxg5 hxg5 29. b3 Ke6 30. a3 Kd6 31. axb4 cxb4 32. Ra5 Nd5 33. f3 Bc8 34. Kf2 Bf5 35. Ra7 g6 36. Ra6+ Kc5 37. Ke1 Nf4 38. g3 Nxh3 39. Kd2 Kb5 40. Rd6 Kc5 41. Ra6 Nf2 42. g4 Bd3 43. Re6 1-0
"""
    
    # Parse from string
    tree = parse_pgn_string_to_tree(sample_pgn)
    
    print(f"Number of games: {len(tree.games)}")
    print(f"\nGame headers: {tree.games[0]}")
    
    # Get some paths
    paths = tree.get_all_paths()
    print(f"\nNumber of unique paths: {len(paths)}")
    print(f"\nFirst 5 moves of main line: {paths[0][:5] if paths else 'No paths'}")
    
    # Get a specific node
    node = tree.get_node_at_path(["e4", "e5", "Nf3"])
    if node:
        print(f"\nNode at ['e4', 'e5', 'Nf3']: {node}")
        print(f"Possible moves from this position: {list(node.children.keys())}")
