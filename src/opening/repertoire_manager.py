import chess
import chess.pgn
import io
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from src.opening.definitions import classify_opening, get_filename_from_category

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
