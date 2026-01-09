"""
Example: Display a chess game from PGN with an interactive board viewer.

This example demonstrates how to use the display_game_from_string and
display_game_from_pgn functions to visualize chess games.
"""

from src.visualization.chess_display import (
    display_game_from_string,
    display_game_from_pgn,
    display_multiple_games_from_strings,
    display_multiple_games_from_pgn,
)
from src.parsers.pgn_tree_parser import (
    parse_pgn_string_to_tree,
    find_divergence_point,
    find_first_divergence_across_openings,
)
from pathlib import Path


def example_display_from_string():
    """Example: Display a game from a PGN string."""
    # Sample game (Ruy Lopez opening)
    pgn = """[Event "Example Game"]
[Site "Local"]
[Date "2024.01.01"]
[Round "1"]
[White "Player 1"]
[Black "Player 2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7 11. c4 c6 12. cxb5 axb5 13. Nc3 Bb7 14. Bg5 b4 15. Nb1 h6 16. Bh4 c5 17. dxe5 Nxe4 18. Bxe7 Qxe7 19. exd6 Qf6 20. Nbd2 Nxd6 21. Nc4 Nxc4 22. Bxc4 Nb6 23. Ne5 Rae8 24. Bxf7+ Rxf7 25. Nxf7 Rxe1+ 26. Qxe1 Kxf7 27. Qe3 Qg5 28. Qxg5 hxg5 29. b3 Ke6 30. a3 Kd6 31. axb4 cxb4 32. Ra5 Nd5 33. f3 Bc8 34. Kf2 Bf5 35. Ra7 g6 36. Ra6+ Kc5 37. Ke1 Nf4 38. g3 Nxh3 39. Kd2 Kb5 40. Rd6 Kc5 41. Ra6 Nf2 42. g4 Bd3 43. Re6 1-0"""
    
    print("Displaying game from PGN string...")
    # This will create an HTML file and open it in the browser
    output_file = display_game_from_string(
        pgn,
        open_in_browser=True,
        size=500  # Larger board
    )
    print(f"Game displayed! HTML file saved to: {output_file}")


def example_display_from_file():
    """Example: Display a game from a PGN file."""
    # Assuming you have a PGN file
    pgn_file = "game.pgn"  # Replace with your PGN file path
    
    try:
        print(f"Displaying game from file: {pgn_file}")
        output_file = display_game_from_pgn(
            pgn_file,
            output_file="chess_game_viewer.html",  # Save to specific file
            open_in_browser=True
        )
        print(f"Game displayed! HTML file saved to: {output_file}")
    except FileNotFoundError:
        print(f"File not found: {pgn_file}")
    except ValueError as e:
        print(f"Error parsing PGN file: {e}")


def example_display_without_browser():
    """Example: Generate HTML without opening in browser."""
    pgn = """[Event "Quick Game"]
1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 g6 1/2-1/2"""
    
    output_file = display_game_from_string(
        pgn,
        output_file="my_chess_game.html",
        open_in_browser=False,  # Don't auto-open
        size=400
    )
    print(f"HTML file generated at: {output_file}")
    print(f"Open it manually in your browser to view the game.")


def example_display_multiple_games_from_strings():
    """Example: Display multiple games from PGN strings."""
    # Multiple games as PGN strings
    games = [
        """[Event "Ruy Lopez"]
[White "Player 1"]
[Black "Player 2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7 1-0""",
        
        """[Event "Sicilian Defense"]
[White "Player 3"]
[Black "Player 4"]
[Result "1/2-1/2"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 g6 1/2-1/2""",
        
        """[Event "Queen's Gambit"]
[White "Player 5"]
[Black "Player 6"]
[Result "0-1"]

1. d4 d5 2. c4 e6 3. Nc3 Nf6 4. cxd5 exd5 0-1"""
    ]
    
    print("Displaying multiple games from PGN strings...")
    output_file = display_multiple_games_from_strings(
        games,
        open_in_browser=True,
        size=500
    )
    print(f"Games displayed! HTML file saved to: {output_file}")
    print("Use Previous Game/Next Game buttons or Shift+Arrow keys to navigate between games.")


def example_display_multiple_games_from_file():
    """Example: Display multiple games from a PGN file."""
    # Assuming you have a PGN file with multiple games
    pgn_file = "games.pgn"  # Replace with your PGN file path
    
    try:
        print(f"Displaying multiple games from file: {pgn_file}")
        output_file = display_multiple_games_from_pgn(
            pgn_file,
            output_file="chess_games_viewer.html",
            open_in_browser=True
        )
        print(f"Games displayed! HTML file saved to: {output_file}")
        print("Navigation controls:")
        print("  - Previous Game/Next Game buttons to switch games")
        print("  - Select Game dropdown to jump to a specific game")
        print("  - Move navigation within each game")
        print("  - Shift+Arrow Left/Right to navigate between games")
        print("  - Arrow Left/Right to navigate moves within current game")
    except FileNotFoundError:
        print(f"File not found: {pgn_file}")
    except ValueError as e:
        print(f"Error parsing PGN file: {e}")


def example_display_with_divergence():
    """Example: Display a game with divergence highlighting from opening repertoire."""
    # Game that diverges from opening
    game_pgn = """[Event "Ruy Lopez - Divergence"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 4. d4 exd4 1-0"""
    
    # Opening repertoire (Ruy Lopez)
    opening_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4"
    
    # Find divergence point
    game_tree = parse_pgn_string_to_tree(game_pgn)
    opening_tree = parse_pgn_string_to_tree(opening_pgn)
    divergence_point = find_divergence_point(game_tree, opening_tree)
    
    print(f"Divergence point: {divergence_point}")
    print("Displaying game with divergence highlighted in red...")
    
    # Display with divergence highlighting
    output_file = display_game_from_string(
        game_pgn,
        opening_pgn=opening_pgn,
        divergence_point=divergence_point,
        open_in_browser=True,
        size=500
    )
    
    print(f"Game displayed! HTML file saved to: {output_file}")
    print("Features:")
    print("  - Divergence move (Bc4) highlighted in RED")
    print("  - Opening repertoire continuation shown below move list")
    print("  - Board shows red arrow for divergence move when viewing that position")


def example_display_with_opening_repertoire():
    """Example: Display games with divergence highlighting using opening repertoire from openings/ directory."""
    # Sample games to analyze - longer games for better demonstration
    games = [
        """[Event "Ruy Lopez - Italian Game Divergence"]
[Site "Local Tournament"]
[Date "2024.01.15"]
[Round "1"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 4. d4 exd4 5. e5 Ne4 6. O-O Be7 7. Re1 d5 8. Bxd5 Nxd5 9. Nxd4 Nxd4 10. Qxd4 O-O 11. Nc3 Nxc3 12. Qxc3 c6 13. Bf4 Bf6 14. Rad1 Qb6 15. Qc4 Be6 16. Qb4 Qc7 17. Bd6 Qd7 18. Bxf8 Rxf8 19. Qxb7 Bc8 20. Qc7 Qe6 21. Qxc6 Qxc6 22. Rxe6 Bf5 23. Re1 Rc8 24. Rc1 Rxc1+ 25. Bxc1 h6 26. b4 a6 27. a4 Be4 28. f3 Bd5 29. Bb2 f6 30. exf6 gxf6 31. Re1 Kf7 32. Re7+ Kg6 33. Qd3+ Kh5 34. Qg3 Bc4 35. Qh3+ Kg5 36. Qg3+ Kh5 37. Qh3+ Kg5 38. f4+ Kf5 39. Qg4# 1-0""",
        
        """[Event "Modern Defense - Long Game"]
[Site "Club Championship"]
[Date "2024.02.20"]
[Round "3"]
[White "Player3"]
[Black "Player4"]
[Result "1/2-1/2"]

1. e4 g6 2. d4 Bg7 3. Nf3 d6 4. Bc4 Nf6 5. Qe2 O-O 6. O-O Nc6 7. c3 e5 8. dxe5 dxe5 9. Bg5 h6 10. Bh4 Be6 11. Bxe6 fxe6 12. Nbd2 Qe7 13. Rad1 Rad8 14. Rfe1 Kh7 15. Bxf6 Bxf6 16. Nc4 Rd6 17. Nd2 Rfd8 18. Nb3 b6 19. Nc1 Nd4 20. Nxd4 exd4 21. Qd2 c5 22. e5 Bg7 23. f4 a5 24. a4 Qe6 25. h3 h5 26. Kh2 Qf5 27. Qe2 R6d7 28. Re4 Rf7 29. Qd3 Qe6 30. Re1 Rfd7 31. Qe4 Qxe4 32. Rxe4 Bf8 33. Re2 Be7 34. Re4 Bf8 35. Re2 Be7 36. Re4 1/2-1/2""",
        
        """[Event "Sicilian Defense - Taimanov Variation"]
[Site "Online Blitz"]
[Date "2024.03.10"]
[Round "?"]
[White "Player5"]
[Black "Player6"]
[Result "0-1"]

1. e4 c5 2. Nf3 e6 3. d4 cxd4 4. Nxd4 Nc6 5. Nc3 a6 6. Be2 Nf6 7. O-O Be7 8. Be3 O-O 9. f4 d6 10. Kh1 Qc7 11. Qe1 Nxd4 12. Bxd4 e5 13. Bxe5 dxe5 14. f5 Bc5 15. Qg3 Kh8 16. Rad1 Bd7 17. Rf3 Rac8 18. Rd3 b5 19. a3 Rfd8 20. Rfd1 Qb6 21. b4 Bb7 22. Qf2 Qc6 23. g4 h6 24. h4 Bc4 25. Nd5 Nxd5 26. exd5 Qc7 27. g5 hxg5 28. hxg5 Bxd3 29. Rxd3 Rxd5 30. Qh4 Rg8 31. Qh7+ Kxh7 32. Rh3+ Kg7 33. Rh7+ Kf8 34. Rxf7+ Ke8 35. Re7+ Kd8 36. Rxe5 Qc6 37. Re3 Rd4 38. Rg3 Rxg4 39. Rxg4 Qxg4 40. Bf3 Qg6 41. c4 bxc4 42. Bxc6 Rf8 43. Bb5 Rf2 44. Kg1 Rxg5+ 45. Kf1 Rf5+ 46. Ke2 Re5+ 47. Kf3 Re3+ 48. Kg4 Rg3+ 49. Kh4 Bf2+ 50. Kh5 Rg5# 0-1""",
        
        """[Event "Ruy Lopez - Complete Game"]
[Site "Rapid Tournament"]
[Date "2024.04.05"]
[Round "5"]
[White "Player7"]
[Black "Player8"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7 11. c4 c6 12. cxb5 axb5 13. Nc3 Bb7 14. Bg5 b4 15. Nb1 h6 16. Bh4 c5 17. dxe5 Nxe4 18. Bxe7 Qxe7 19. exd6 Qf6 20. Nbd2 Nxd6 21. Nc4 Nxc4 22. Bxc4 Nb6 23. Ne5 Rae8 24. Bxf7+ Rxf7 25. Nxf7 Rxe1+ 26. Qxe1 Kxf7 27. Qe3 Qg5 28. Qxg5 hxg5 29. b3 Ke6 30. a3 Kd6 31. axb4 cxb4 32. Ra5 Nd5 33. f3 Bc8 34. Kf2 Bf5 35. Ra7 g6 36. Ra6+ Kc5 37. Ke1 Nf4 38. g3 Nxh3 39. Kd2 Kb5 40. Rd6 Kc5 41. Ra6 Nf2 42. g4 Bd3 43. Re6 1-0""",
    ]
    
    # Load opening repertoire from openings directory
    openings_dir = Path(__file__).parent.parent / "openings"
    opening_trees = []
    opening_pgns = []
    
    print(f"Loading opening repertoire from: {openings_dir}")
    for pgn_file in openings_dir.glob("*.pgn"):
        print(f"  - Loading {pgn_file.name}")
        with open(pgn_file, encoding="utf-8") as f:
            pgn_str = f.read()
            opening_pgns.append(pgn_str)
            opening_trees.append(parse_pgn_string_to_tree(pgn_str))
    
    if not opening_trees:
        print("Warning: No opening PGN files found in openings/ directory")
        return
    
    print(f"Loaded {len(opening_trees)} opening repertoire files\n")
    
    # Analyze each game and display with divergence
    for idx, game_pgn in enumerate(games, 1):
        print(f"\n{'='*60}")
        print(f"Analyzing Game {idx}")
        print(f"{'='*60}")
        
        # Find the best matching opening and divergence point
        game_tree = parse_pgn_string_to_tree(game_pgn)
        divergence_point, opening_idx = find_first_divergence_across_openings(
            game_tree, opening_trees
        )
        
        # Find the best matching opening index
        # opening_idx is None when no exact match, so we need to find which opening
        # has the longest match (which is already calculated, but index not returned)
        best_opening_idx = opening_idx
        
        if best_opening_idx is None:
            # Find the opening with the longest match by checking each opening individually
            best_match_length = -1
            for i, opening_tree in enumerate(opening_trees):
                temp_div = find_divergence_point(game_tree, opening_tree)
                if not temp_div:
                    # Exact match found
                    best_opening_idx = i
                    break
                match_len = len(temp_div)
                if match_len > best_match_length:
                    best_match_length = match_len
                    best_opening_idx = i
        
        # Get the matching opening PGN
        opening_pgn = None
        opening_file_name = None
        if best_opening_idx is not None and 0 <= best_opening_idx < len(opening_pgns):
            opening_pgn = opening_pgns[best_opening_idx]
            opening_files = sorted(openings_dir.glob("*.pgn"))
            if best_opening_idx < len(opening_files):
                opening_file_name = opening_files[best_opening_idx].name
        
        if divergence_point:
            print(f"Divergence found at move: {divergence_point[-1]}")
            path_display = ' '.join(divergence_point[:5]) + '...' if len(divergence_point) > 5 else ' '.join(divergence_point)
            print(f"Divergence path: {path_display}")
            if opening_file_name:
                print(f"Best matching opening: {opening_file_name}")
        else:
            print("Game follows opening repertoire completely (no divergence)")
            if opening_file_name:
                print(f"Matching opening: {opening_file_name}")
        
        # Display game with divergence highlighting
        output_file = display_game_from_string(
            game_pgn,
            opening_pgn=opening_pgn,
            divergence_point=divergence_point if divergence_point else None,
            output_file=f"game_{idx}_with_divergence.html",
            open_in_browser=(idx == 1),  # Only open first game in browser
            size=500
        )
        print(f"Game {idx} displayed: {output_file}")
    
    print(f"\n{'='*60}")
    print("All games analyzed and displayed!")
    print("Features:")
    print("  - Divergence moves highlighted in RED")
    print("  - Opening repertoire continuation shown below move list")
    print("  - Red arrow on board when viewing divergence position")


if __name__ == "__main__":
    # Run the first example
    example_display_from_string()
    
    # Uncomment to try other examples:
    # example_display_from_file()
    # example_display_without_browser()
    # example_display_multiple_games_from_strings()
    # example_display_multiple_games_from_file()
    # example_display_with_divergence()
    example_display_with_opening_repertoire()
