import chess
import chess.pgn
import io
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# List of major opening move sequences (SAN)
# Ordered from most specific to least specific within each move-1 branch
OPENING_DEFINITIONS = [
    # e4 e5
    ("Italian Game", ["e4", "e5", "Nf3", "Nc6", "Bc4"]),
    ("Ruy Lopez", ["e4", "e5", "Nf3", "Nc6", "Bb5"]),
    ("Scotch Game", ["e4", "e5", "Nf3", "Nc6", "d4"]),
    ("Four Knights Game", ["e4", "e5", "Nf3", "Nc6", "Nc3", "Nf6"]),
    ("Petrov's Defense", ["e4", "e5", "Nf3", "Nf6"]),
    ("Philidor Defense", ["e4", "e5", "Nf3", "d6"]),
    ("King's Gambit", ["e4", "e5", "f4"]),
    ("Vienna Game", ["e4", "e5", "Nc3"]),
    ("Center Game", ["e4", "e5", "d4", "exd4", "Qxd4"]),
    
    # e4 Semi-Open
    ("Sicilian Defense", ["e4", "c5"]),
    ("French Defense", ["e4", "e6"]),
    ("Caro-Kann Defense", ["e4", "c6"]),
    ("Scandinavian Defense", ["e4", "d5"]),
    ("Alekhine's Defense", ["e4", "Nf6"]),
    ("Pirc Defense", ["e4", "d6", "d4", "Nf6"]),
    ("Modern Defense", ["e4", "g6"]),
    
    # d4
    ("Nimzo-Indian Defense", ["d4", "Nf6", "c4", "e6", "Nc3", "Bb4"]),
    ("Queen's Indian Defense", ["d4", "Nf6", "c4", "e6", "Nf3", "b6"]),
    ("King's Indian Defense", ["d4", "Nf6", "c4", "g6"]),
    ("Grunfeld Defense", ["d4", "Nf6", "c4", "g6", "Nc3", "d5"]),
    ("Catalan Opening", ["d4", "Nf6", "c4", "e6", "g3"]),
    ("Benoni Defense", ["d4", "Nf6", "c4", "c5"]),
    ("Queen's Gambit", ["d4", "d5", "c4"]),
    ("Slav Defense", ["d4", "d5", "c4", "c6"]),
    ("London System", ["d4", "d5", "Bf4"]),
    ("Trompowsky Attack", ["d4", "Nf6", "Bg5"]),
    ("Dutch Defense", ["d4", "f5"]),
    
    # Flank Openings
    ("English Opening", ["c4"]),
    ("Reti Opening", ["Nf3"]),
    ("Bird's Opening", ["f4"]),
    ("Benko Opening", ["g3"]),
    
    # Broader / Fallback
    ("1. e4 Open Game", ["e4", "e5"]),
    ("1. d4 Closed Game", ["d4", "d5"]),
    ("1. d4 Indian Systems", ["d4", "Nf6"]),
]

def classify_opening(moves: List[str]) -> str:
    """
    Classifies an opening based on a sequence of moves.
    Returns the name of the most specific matching opening.
    """
    best_match = "Miscellaneous"
    best_match_len = 0
    
    for name, prefix in OPENING_DEFINITIONS:
        if len(moves) >= len(prefix):
            match = True
            for i in range(len(prefix)):
                if moves[i] != prefix[i]:
                    match = False
                    break
            if match and len(prefix) > best_match_len:
                best_match = name
                best_match_len = len(prefix)
                
    return best_match

def _get_all_paths(node: chess.pgn.GameNode, current_path: List[str]) -> List[List[str]]:
    """
    Recursively extracts all paths (main line + variations) from a PGN node.
    """
    paths = []
    if not node.variations:
        return [current_path]
    
    for variation in node.variations:
        move_san = node.board().san(variation.move)
        paths.extend(_get_all_paths(variation, current_path + [move_san]))
        
    return paths

def split_repertoire_by_opening(pgn_file_path: str, output_dir_path: str):
    """
    Splits a repertoire PGN into multiple files based on opening type.
    """
    pgn_path = Path(pgn_file_path)
    output_dir = Path(output_dir_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Classification -> list of paths
    categorized_paths: Dict[str, List[List[str]]] = {}
    
    with open(pgn_path, encoding="utf-8") as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            
            # Extract all distinct paths in the tree
            paths = _get_all_paths(game, [])
            
            for path in paths:
                if not path:
                    continue
                category = classify_opening(path)
                if category not in categorized_paths:
                    categorized_paths[category] = []
                categorized_paths[category].append(path)
                
    # Write files
    for category, paths in categorized_paths.items():
        filename = category.lower().replace(" ", "_").replace("'", "") + ".pgn"
        out_file = output_dir / filename
        
        # Build a game object for this category
        new_game = chess.pgn.Game()
        new_game.headers["Event"] = f"{category} Repertoire"
        
        # Merge all paths into this game's tree
        for path in paths:
            node = new_game
            board = new_game.board()
            for move_san in path:
                try:
                    move = board.parse_san(move_san)
                    # Find existing variation or create new one
                    found_node = None
                    for variation in node.variations:
                        if variation.move == move:
                            found_node = variation
                            break
                    
                    if found_node:
                        node = found_node
                    else:
                        node = node.add_variation(move)
                    
                    board.push(move)
                except ValueError:
                    break
        
        with open(out_file, "w", encoding="utf-8") as out_f:
            print(new_game, file=out_f, end="\n\n")
            
    print(f"Split completed. Categorized files created in {output_dir}")
    return list(categorized_paths.keys())

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        split_repertoire_by_opening(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python3 repertoire_manager.py <source_pgn> <output_dir>")
