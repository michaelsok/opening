from typing import List, Tuple

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

def get_filename_from_category(category: str) -> str:
    """
    Converts a category name to the expected PGN filename.
    """
    return category.lower().replace(" ", "_").replace("'", "") + ".pgn"
