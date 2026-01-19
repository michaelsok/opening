"""
Display chess games with interactive board visualization.

This module provides functionality to display chess games from PGN format
with an interactive board viewer similar to Lichess.
"""

import chess
import chess.pgn
import chess.svg
import io
import json
from typing import Optional, Union, List
from pathlib import Path
import webbrowser
import tempfile
import os
import jinja2

# Import for divergence analysis
from src.parsers.pgn_tree_parser import (
    parse_pgn_string_to_tree,
    find_first_divergence_across_openings,
)


def _get_jinja_env() -> jinja2.Environment:
    """Get the Jinja2 environment for loading templates."""
    template_dir = Path(__file__).parent / "templates"
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )


def display_game_from_pgn(
    pgn_file_path: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    open_in_browser: bool = True,
    size: int = 400,
    opening_pgn: Optional[str] = None,
    divergence_point: Optional[List[str]] = None
) -> str:
    """
    Display a chess game from a PGN file with an interactive board viewer.
    
    Creates an HTML file with an interactive chess board that allows navigation
    through the game moves, similar to Lichess game viewer.
    
    Args:
        pgn_file_path: Path to the PGN file containing the game
        output_file: Optional path to save the HTML file. If None, creates a temporary file.
        open_in_browser: If True, automatically opens the HTML file in the default browser
        size: Size of the chess board in pixels (default: 400)
        
    Returns:
        str: Path to the generated HTML file
        
    Raises:
        FileNotFoundError: If PGN file doesn't exist
        ValueError: If PGN file contains no valid game
        
    Example:
        >>> display_game_from_pgn("game.pgn")
        '/tmp/tmpXXXXXX.html'
        
        >>> display_game_from_pgn("game.pgn", "output.html", open_in_browser=False)
        'output.html'
    """
    pgn_file_path = Path(pgn_file_path)
    
    if not pgn_file_path.exists():
        raise FileNotFoundError(f"PGN file not found: {pgn_file_path}")
    
    with open(pgn_file_path, 'r', encoding='utf-8') as pgn_file:
        game = chess.pgn.read_game(pgn_file)
        
    if game is None:
        raise ValueError(f"No valid game found in PGN file: {pgn_file_path}")
    
    return _create_html_viewer(
        game, output_file, open_in_browser, size,
        opening_pgn=opening_pgn, divergence_point=divergence_point
    )


def display_game_from_string(
    pgn_string: str,
    output_file: Optional[Union[str, Path]] = None,
    open_in_browser: bool = True,
    size: int = 400,
    opening_pgn: Optional[str] = None,
    divergence_point: Optional[List[str]] = None,
    user_color: Optional[str] = None
) -> str:
    """
    Display a chess game from a PGN string with an interactive board viewer.
    
    Creates an HTML file with an interactive chess board that allows navigation
    through the game moves, similar to Lichess game viewer.
    
    Args:
        pgn_string: PGN string containing the game
        output_file: Optional path to save the HTML file. If None, creates a temporary file.
        open_in_browser: If True, automatically opens the HTML file in the default browser
        size: Size of the chess board in pixels (default: 400)
        opening_pgn: Optional PGN string of the opening repertoire to compare against
        divergence_point: Optional list of moves (with move numbers) where game diverges from opening.
                         Format: ["1. e4", "1... e5", "2. Nf3", "2... Nc6", "3. Bc4"]
                         If provided with opening_pgn, will highlight divergence move in red
                         and show opening variant continuation.
        user_color: Optional color played by the user ("white" or "black")
        
    Returns:
        str: Path to the generated HTML file
        
    Raises:
        ValueError: If PGN string contains no valid game
    """
    game = chess.pgn.read_game(io.StringIO(pgn_string))
    
    if game is None:
        raise ValueError("No valid game found in PGN string")
    
    return _create_html_viewer(
        game, output_file, open_in_browser, size,
        opening_pgn=opening_pgn, divergence_point=divergence_point,
        user_color=user_color
    )


def display_multiple_games_from_pgn(
    pgn_file_path: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    open_in_browser: bool = True,
    size: int = 400
) -> str:
    """
    Display multiple chess games from a PGN file with navigation between games.
    
    Creates an HTML file with an interactive chess board viewer that allows
    navigation between multiple games and through moves within each game.
    
    Args:
        pgn_file_path: Path to the PGN file containing one or more games
        output_file: Optional path to save the HTML file. If None, creates a temporary file.
        open_in_browser: If True, automatically opens the HTML file in the default browser
        size: Size of the chess board in pixels (default: 400)
        
    Returns:
        str: Path to the generated HTML file
        
    Raises:
        FileNotFoundError: If PGN file doesn't exist
        ValueError: If PGN file contains no valid games
        
    Example:
        >>> display_multiple_games_from_pgn("games.pgn")
        '/tmp/tmpXXXXXX.html'
    """
    pgn_file_path = Path(pgn_file_path)
    
    if not pgn_file_path.exists():
        raise FileNotFoundError(f"PGN file not found: {pgn_file_path}")
    
    games = []
    with open(pgn_file_path, 'r', encoding='utf-8') as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            games.append(game)
    
    if not games:
        raise ValueError(f"No valid games found in PGN file: {pgn_file_path}")
    
    return _create_multi_game_html_viewer(games, output_file, open_in_browser, size)


def display_multiple_games_from_strings(
    pgn_strings: List[str],
    output_file: Optional[Union[str, Path]] = None,
    open_in_browser: bool = True,
    size: int = 400
) -> str:
    """
    Display multiple chess games from PGN strings with navigation between games.
    
    Creates an HTML file with an interactive chess board viewer that allows
    navigation between multiple games and through moves within each game.
    
    Args:
        pgn_strings: List of PGN strings, each containing one game
        output_file: Optional path to save the HTML file. If None, creates a temporary file.
        open_in_browser: If True, automatically opens the HTML file in the default browser
        size: Size of the chess board in pixels (default: 400)
        
    Returns:
        str: Path to the generated HTML file
        
    Raises:
        ValueError: If no valid games found in the PGN strings
        
    Example:
        >>> games = [
        ...     '[Event "Game 1"]\\n1. e4 e5 1-0',
        ...     '[Event "Game 2"]\\n1. d4 d5 1-0'
        ... ]
        >>> display_multiple_games_from_strings(games)
        '/tmp/tmpXXXXXX.html'
    """
    games = []
    for pgn_string in pgn_strings:
        game = chess.pgn.read_game(io.StringIO(pgn_string))
        if game is not None:
            games.append(game)
    
    if not games:
        raise ValueError("No valid games found in PGN strings")
    
    return _create_multi_game_html_viewer(games, output_file, open_in_browser, size)


def _extract_opening_variant(
    opening_pgn: str,
    divergence_point: List[str]
) -> List[str]:
    """
    Extract the opening variant continuation from the divergence point.
    
    Args:
        opening_pgn: PGN string of the opening repertoire (can be complex multi-game PGN)
        divergence_point: List of moves up to and including the divergence point
        
    Returns:
        List[str]: List of moves (SAN) that continue from the divergence point in the opening
    """
    from src.parsers.pgn_tree_parser import parse_pgn_string_to_tree
    
    # Extract move SANs from divergence_point (remove move numbers)
    divergence_moves = []
    for move_str in divergence_point[:-1]:  # All moves except the last (diverging) one
        # Extract SAN from "1. e4" or "1... e5" format
        if '...' in move_str:
            # Black move: "1... e5" -> split on '...' and take part after
            parts = move_str.split('...', 1)
            if len(parts) > 1:
                san = parts[1].strip()
            else:
                continue
        else:
            # White move: "1. e4" -> split on first '.' and take part after
            parts = move_str.split('.', 1)
            if len(parts) > 1:
                san = parts[1].strip()
            else:
                continue
        divergence_moves.append(san)
    
    try:
        # Use the existing parser to build the full tree of all openings
        opening_tree = parse_pgn_string_to_tree(opening_pgn)
        
        # Navigate to the position just before divergence
        current_node = opening_tree.root
        for move_san in divergence_moves:
            if move_san in current_node.children:
                current_node = current_node.children[move_san]
            else:
                return []  # Can't find matching position in the opening tree
        
        # Get the main variant continuation from this position
        variant_moves = []
        while current_node.children:
            # Get the first (main) variant
            first_move = list(current_node.children.keys())[0]
            variant_moves.append(first_move)
            current_node = current_node.children[first_move]
        
        return variant_moves
    except Exception:
        return []


def _find_divergence_move_index(
    divergence_point: List[str],
    moves_san: List[str]
) -> Optional[int]:
    """
    Find the index of the divergence move in the moves_san list.
    
    Args:
        divergence_point: List of moves with move numbers, e.g., ["1. e4", "1... e5", "2. Nf3", "2... Nc6", "3. Bc4"]
        moves_san: List of moves in SAN notation without move numbers
        
    Returns:
        Optional[int]: Index of the divergence move, or None if not found
    """
    if not divergence_point:
        return None
    
    # Get the last move from divergence_point (the actual diverging move)
    last_divergence = divergence_point[-1]
    
    # Extract SAN from "3. Bc4" or "1... c5" format
    # Handle black moves: "1... c5" -> extract "c5"
    if '...' in last_divergence:
        # Black move: split on '...' and take the part after
        parts = last_divergence.split('...', 1)
        if len(parts) > 1:
            san = parts[1].strip()
        else:
            return None
    else:
        # White move: "3. Bc4" -> split on first '.' and take part after
        parts = last_divergence.split('.', 1)
        if len(parts) > 1:
            san = parts[1].strip()
        else:
            return None
    
    # Find this move in moves_san
    for idx, move in enumerate(moves_san):
        if move == san:
            return idx
    
    return None


def _create_html_viewer(
    game: chess.pgn.Game,
    output_file: Optional[Union[str, Path]],
    open_in_browser: bool,
    size: int,
    opening_pgn: Optional[str] = None,
    divergence_point: Optional[List[str]] = None,
    user_color: Optional[str] = None
) -> str:
    """Create an HTML viewer for a chess game."""
    # Collect all moves and positions
    board = game.board()
    positions = []
    moves_san = []
    moves_uci = []
    
    # Store initial position
    positions.append(board.fen())
    
    # Collect all moves
    for move in game.mainline_moves():
        moves_san.append(board.san(move))
        moves_uci.append(move.uci())
        board.push(move)
        positions.append(board.fen())
    
    # Find divergence move index and extract opening variant if provided
    divergence_move_index = None
    opening_variant = []
    game_variant = []  # Moves actually played after divergence
    opening_variant_boards = []  # SVG boards for opening variant positions
    opening_variant_positions = []  # FEN positions for opening variant
    opening_variant_moves_uci = []  # UCI moves for opening variant
    game_variant_boards = []  # SVG boards for game variant positions (from divergence)
    game_variant_positions = []  # FEN positions for game variant (from divergence)
    
    # New metadata for highlighting
    repertoire_length = len(moves_san)
    is_opponent_divergence = False

    if opening_pgn and divergence_point:
        divergence_move_index = _find_divergence_move_index(divergence_point, moves_san)
        opening_variant = _extract_opening_variant(opening_pgn, divergence_point)
        
        # Calculate repertoire length (moves that matched before the divergence)
        if divergence_move_index is not None:
            repertoire_length = divergence_move_index # Moves up to (but not including) divergence
            
            # Check if divergence was by opponent
            # index 0 (White), 1 (Black), 2 (White)...
            divergence_color = 'white' if divergence_move_index % 2 == 0 else 'black'
            if user_color and divergence_color != user_color.lower():
                is_opponent_divergence = True

        # Extract game variant - moves played after the divergence point
        if divergence_move_index is not None and divergence_move_index + 1 < len(moves_san):
            game_variant = moves_san[divergence_move_index + 1:]
        
        # Generate board positions for game variant (from divergence point onward)
        if game_variant and divergence_move_index is not None:
            # Start from the position at divergence
            variant_board = game.board()
            variant_board.reset()
            # Play all moves up to and including the divergence move
            for i in range(divergence_move_index + 1):
                if i < len(moves_uci):
                    move = chess.Move.from_uci(moves_uci[i])
                    variant_board.push(move)
            
            # Store the divergence position (starting point for game variant)
            game_variant_positions.append(variant_board.fen())
            game_variant_boards.append(chess.svg.board(variant_board, size=size))
            
            # Play through the game variant moves
            for idx, move_san in enumerate(game_variant):
                try:
                    move = variant_board.parse_san(move_san)
                    move_uci = move.uci()
                    
                    # Generate SVG showing the move
                    board_before = chess.Board(variant_board.fen())
                    svg = chess.svg.board(board_before, size=size, lastmove=move)
                    game_variant_boards.append(svg)
                    
                    # Push the move to get position after
                    variant_board.push(move)
                    game_variant_positions.append(variant_board.fen())
                except (ValueError, AssertionError):
                    break
            
            # Add final position if we have moves
            if game_variant_positions:
                final_board = chess.Board(game_variant_positions[-1])
                game_variant_boards.append(chess.svg.board(final_board, size=size))
        
        # Generate board positions for opening variant if it exists
        if opening_variant and divergence_move_index is not None:
            # Start from the position at divergence
            variant_board = game.board()
            # Reset to initial position
            variant_board.reset()
            # Play all moves up to (but not including) the divergence move
            for i in range(divergence_move_index):
                if i < len(moves_uci):
                    move = chess.Move.from_uci(moves_uci[i])
                    variant_board.push(move)
            
            # Store the position BEFORE the divergence (starting point for variants)
            opening_variant_positions.append(variant_board.fen())
            # First board shows the position at divergence (before any variant moves)
            opening_variant_boards.append(chess.svg.board(variant_board, size=size))
            
            # Play through the opening variant moves
            for idx, move_san in enumerate(opening_variant):
                try:
                    # Parse the move
                    move = variant_board.parse_san(move_san)
                    move_uci = move.uci()
                    opening_variant_moves_uci.append(move_uci)
                    
                    # Generate SVG showing the move (position before move with arrow)
                    board_before = chess.Board(variant_board.fen())
                    svg = chess.svg.board(board_before, size=size, lastmove=move)
                    opening_variant_boards.append(svg)
                    
                    # Now push the move to get the position after
                    variant_board.push(move)
                    opening_variant_positions.append(variant_board.fen())
                except (ValueError, AssertionError) as e:
                    # Invalid move, skip the rest
                    break
            
            # Add final position board if we have moves
            if opening_variant_positions:
                final_board = chess.Board(opening_variant_positions[-1])
                opening_variant_boards.append(chess.svg.board(final_board, size=size))
    
    # Get game headers
    headers = dict(game.headers)
    white = headers.get('White', 'Unknown')
    black = headers.get('Black', 'Unknown')
    event = headers.get('Event', 'Unknown Event')
    result = headers.get('Result', '*')
    date = headers.get('Date', '')
    site = headers.get('Site', '')
    
    # Generate SVG boards for all positions with divergence highlighting
    svg_boards = []
    board_state = game.board()
    
    for idx, fen in enumerate(positions):
        board = chess.Board(fen)
        
        # Highlight divergence move if this is the position after the divergence move
        lastmove = None
        if divergence_move_index is not None and idx > 0:
            # If we're at the position after the divergence move, highlight it
            if idx == divergence_move_index + 1:
                # Get the move that was just played
                if divergence_move_index < len(moves_uci):
                    lastmove = chess.Move.from_uci(moves_uci[divergence_move_index])
        
        svg = chess.svg.board(
            board,
            size=size,
            lastmove=lastmove
        )
        
        # If this is the divergence move position, add red styling
        if divergence_move_index is not None and idx == divergence_move_index + 1:
            # Inject red color into the SVG for the last move arrow and squares
            # Replace the arrow stroke color
            svg = svg.replace('stroke="#5881b8"', 'stroke="#ff0000"')
            svg = svg.replace('stroke="#0000ff"', 'stroke="#ff0000"')
            # Replace square fill color for highlighted squares
            svg = svg.replace('fill="#cdd26a"', 'fill="#ff6b6b"')
            svg = svg.replace('fill="#aaa23b"', 'fill="#ff4444"')
            # Make the arrow more visible
            svg = svg.replace('stroke-width="0.03"', 'stroke-width="0.06"')
            svg = svg.replace('stroke-width="0.04"', 'stroke-width="0.06"')
        
        svg_boards.append(svg)
    
    # Create output file if not specified
    if output_file is None:
        fd, output_file = tempfile.mkstemp(suffix='.html', prefix='chess_game_')
        os.close(fd)
    else:
        output_file = Path(output_file)
    
    # Generate HTML content
    html_content = _generate_html_content(
        svg_boards, moves_san, moves_uci, positions,
        white, black, event, result, date, site, size,
        divergence_move_index=divergence_move_index,
        opening_variant=opening_variant,
        game_variant=game_variant,
        divergence_point=divergence_point,
        opening_variant_boards=opening_variant_boards,
        opening_variant_positions=opening_variant_positions,
        opening_variant_moves_uci=opening_variant_moves_uci,
        game_variant_boards=game_variant_boards,
        game_variant_positions=game_variant_positions,
        repertoire_length=repertoire_length,
        is_opponent_divergence=is_opponent_divergence,
        user_color=user_color
    )
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Open in browser if requested
    if open_in_browser:
        webbrowser.open(f'file://{os.path.abspath(output_file)}')
    
    return str(output_file)


def _generate_html_content(
    svg_boards: list,
    moves_san: list,
    moves_uci: list,
    positions: list,
    white: str,
    black: str,
    event: str,
    result: str,
    date: str,
    site: str,
    size: int,
    divergence_move_index: Optional[int] = None,
    opening_variant: Optional[List[str]] = None,
    game_variant: Optional[List[str]] = None,
    divergence_point: Optional[List[str]] = None,
    opening_variant_boards: Optional[List[str]] = None,
    opening_variant_positions: Optional[List[str]] = None,
    opening_variant_moves_uci: Optional[List[str]] = None,
    game_variant_boards: Optional[List[str]] = None,
    game_variant_positions: Optional[List[str]] = None,
    **kwargs
) -> str:
    """Generate HTML content for the chess game viewer."""
    

    boards_json = json.dumps(svg_boards)
    positions_json = json.dumps(positions)
    moves_san_json = json.dumps(moves_san)
    moves_uci_json = json.dumps(moves_uci)
    opening_variant_boards_json = json.dumps(opening_variant_boards if opening_variant_boards else [])
    opening_variant_positions_json = json.dumps(opening_variant_positions if opening_variant_positions else [])
    game_variant_boards_json = json.dumps(game_variant_boards if game_variant_boards else [])
    game_variant_positions_json = json.dumps(game_variant_positions if game_variant_positions else [])
    game_variant_json = json.dumps(game_variant if game_variant else [])
    opening_variant_san_json = json.dumps(opening_variant if opening_variant else [])
    
    # New metadata
    repertoire_length = kwargs.get('repertoire_length', len(moves_san))
    is_opponent_divergence = kwargs.get('is_opponent_divergence', False)
    user_color = kwargs.get('user_color', None)
    
    # Render template
    env = _get_jinja_env()
    template = env.get_template("single_game.html")
    
    return template.render(
        event=event,
        white=white,
        black=black,
        result=result,
        date=date,
        site=site,
        boards_json=boards_json,
        positions_json=positions_json,
        moves_san_json=moves_san_json,
        moves_uci_json=moves_uci_json,
        divergence_move_index=divergence_move_index,
        opening_variant_boards_json=opening_variant_boards_json,
        opening_variant_positions_json=opening_variant_positions_json,
        game_variant_boards_json=game_variant_boards_json,
        game_variant_positions_json=game_variant_positions_json,
        game_variant_json=game_variant_json,
        opening_variant_san_json=opening_variant_san_json,
        positions=positions,
        moves_san=moves_san,
        opening_variant=opening_variant,
        repertoire_length=repertoire_length,
        is_opponent_divergence=is_opponent_divergence,
        user_color=user_color
    )


def create_index_html(
    games: List[str],
    opening_repertoire: Union[str, Path, List[str]],
    target_username: Optional[str] = None,
    output_file: Optional[Union[str, Path]] = None,
    open_in_browser: bool = True,
    size: int = 400
) -> str:
    """
    Create an index.html file with a list of chess games and their divergence points.

    Args:
        games: List of PGN strings representing the games to index
        opening_repertoire: List of PGN strings or path to directory containing opening PGN files
        target_username: Optional username to determine which color repertoire to use
        output_file: Optional path to save the index.html file. 
                     If None, saves to src/visualization/index.html
        open_in_browser: If True, automatically opens the HTML file in the default browser
        size: Size of chess board in pixels (default: 400)
        
    Returns:
        str: Path to the generated index.html file
        
    Raises:
        ValueError: If games list is empty
    """
    if not games:
        raise ValueError("games list cannot be empty")
    
    # Pre-parse opening directory PGNs for color matching if directory provided
    all_opening_pgns = []
    white_opening_pgns = []
    black_opening_pgns = []
    
    if isinstance(opening_repertoire, (str, Path)):
        opening_dir = Path(opening_repertoire)
        if opening_dir.is_dir():
            # 1. Search for subdirectories white/ and black/
            white_dir = opening_dir / "white"
            black_dir = opening_dir / "black"
            
            if white_dir.is_dir():
                for pgn_file in white_dir.glob("*.pgn"):
                    with open(pgn_file, encoding="utf-8") as f:
                        pgn_str = f.read()
                        white_opening_pgns.append(pgn_str)
                        all_opening_pgns.append(pgn_str)
            
            if black_dir.is_dir():
                for pgn_file in black_dir.glob("*.pgn"):
                    with open(pgn_file, encoding="utf-8") as f:
                        pgn_str = f.read()
                        black_opening_pgns.append(pgn_str)
                        all_opening_pgns.append(pgn_str)
                        
            # 2. Fallback to white.pgn and black.pgn if subdirectories didn't provide any
            if not white_opening_pgns:
                white_pgn_file = opening_dir / "white.pgn"
                if white_pgn_file.exists():
                    with open(white_pgn_file, encoding="utf-8") as f:
                        pgn_str = f.read()
                        white_opening_pgns.append(pgn_str)
                        if pgn_str not in all_opening_pgns:
                            all_opening_pgns.append(pgn_str)

            if not black_opening_pgns:
                black_pgn_file = opening_dir / "black.pgn"
                if black_pgn_file.exists():
                    with open(black_pgn_file, encoding="utf-8") as f:
                        pgn_str = f.read()
                        black_opening_pgns.append(pgn_str)
                        if pgn_str not in all_opening_pgns:
                            all_opening_pgns.append(pgn_str)

            # 3. Add any other PGN files from the root directory
            for pgn_file in opening_dir.glob("*.pgn"):
                if pgn_file.name.lower() not in ["white.pgn", "black.pgn"]:
                    with open(pgn_file, encoding="utf-8") as f:
                        pgn_str = f.read()
                        if pgn_str not in all_opening_pgns:
                            all_opening_pgns.append(pgn_str)
        else:
            raise ValueError(f"Opening repertoire path is not a directory: {opening_repertoire}")
    else:
        all_opening_pgns = opening_repertoire

    # Pre-build trees
    all_opening_trees = [parse_pgn_string_to_tree(pgn) for pgn in all_opening_pgns]
    white_opening_trees = [parse_pgn_string_to_tree(pgn) for pgn in white_opening_pgns]
    black_opening_trees = [parse_pgn_string_to_tree(pgn) for pgn in black_opening_pgns]
    
    # Results container
    game_data_list = []
    
    for idx, game_pgn in enumerate(games):
        try:
            game_obj = chess.pgn.read_game(io.StringIO(game_pgn))
            if game_obj is None:
                continue
                
            headers = dict(game_obj.headers)
            user_color = None
            if target_username:
                target_username_lower = target_username.lower()
                if headers.get('White', '').lower() == target_username_lower:
                    user_color = 'white'
                elif headers.get('Black', '').lower() == target_username_lower:
                    user_color = 'black'

            # Decide which trees to use
            current_opening_pgns = all_opening_pgns
            current_opening_trees = all_opening_trees
            
            if user_color == 'white' and white_opening_trees:
                current_opening_pgns = white_opening_pgns
                current_opening_trees = white_opening_trees
            elif user_color == 'black' and black_opening_trees:
                current_opening_pgns = black_opening_pgns
                current_opening_trees = black_opening_trees

            # Find divergence point
            game_tree = parse_pgn_string_to_tree(game_pgn)
            divergence_point, opening_idx = find_first_divergence_across_openings(game_tree, current_opening_trees)
            
            # Get matching opening PGN
            matching_opening_pgn = current_opening_pgns[opening_idx] if opening_idx is not None else None
            
            game_data_list.append({
                'index': idx,
                'pgn': game_pgn,
                'game': game_obj,
                'headers': headers,
                'divergence_point': divergence_point,
                'opening_pgn': matching_opening_pgn,
                'opening_idx': opening_idx,
                'user_color': user_color
            })
        except Exception:
            continue
    
    if not game_data_list:
        raise ValueError("No valid games found in games list")
    
    # Set default output location
    if output_file is None:
        visualization_dir = Path(__file__).parent
        output_file = visualization_dir / "index.html"
    else:
        output_file = Path(output_file)
    
    # Generate HTML content for index page with game list
    html_content = _generate_index_html_content(game_data_list, size)
    
    # Write HTML file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Generate individual game viewer files
    game_viewer_files = []
    for game_data in game_data_list:
        viewer_file = output_file.parent / f"game_{game_data['index']}.html"
        try:
            display_game_from_string(
                game_data['pgn'],
                output_file=str(viewer_file),
                open_in_browser=False,
                size=size,
                opening_pgn=game_data['opening_pgn'],
                divergence_point=game_data['divergence_point'] if game_data['divergence_point'] else None,
                user_color=game_data.get('user_color')
            )
            game_viewer_files.append(str(viewer_file.name))
        except Exception as e:
            print(f"Warning: Failed to generate viewer for game {game_data['index']}: {e}")
            game_viewer_files.append(None)
    
    # Open in browser if requested
    if open_in_browser:
        webbrowser.open(f'file://{output_file.absolute()}')
    
    return str(output_file.absolute())


def _generate_index_html_content(game_data_list: List[dict], size: int) -> str:
    """Generate HTML content for the games index page."""
    num_games = len(game_data_list)
    
    # Prepare data for template
    game_list = []
    for game_data in game_data_list:
        headers = game_data['headers']
        event = headers.get('Event', f"Game {game_data['index'] + 1}")
        white = headers.get('White', 'Unknown')
        black = headers.get('Black', 'Unknown')
        result = headers.get('Result', '*')
        date = headers.get('Date', '')
        
        # Format divergence info
        divergence = game_data['divergence_point']
        is_opponent_divergence = False
        if divergence:
            diverging_move_str = divergence[-1]
            # Determine if white or black move (black moves have "...")
            is_black_move = "..." in diverging_move_str
            divergence_color = 'black' if is_black_move else 'white'
            
            user_color = game_data.get('user_color')
            if user_color:
                is_opponent_divergence = (user_color != divergence_color)
                label = "Opponent diverges at:" if is_opponent_divergence else "Player diverges at:"
            else:
                label = "Diverges at:"
                
            divergence_html = f'<span class="divergence-info">{label} {diverging_move_str}</span>'
        else:
            divergence_html = '<span class="divergence-info no-divergence">✓ Follows opening repertoire</span>'
        
        game_img = {
            'index': game_data['index'] + 1,
            'viewer_file': f"game_{game_data['index']}.html",
            'event': event,
            'result': result,
            'white': white,
            'black': black,
            'date': date,
            'divergence_html': divergence_html,
            'is_opponent_divergence': is_opponent_divergence
        }
        game_list.append(game_img)
        
    env = _get_jinja_env()
    template = env.get_template("index.html")
    
    return template.render(
        num_games=num_games,
        game_list=game_list
    )

def _process_game(game, size: int) -> dict:
    """Process a single game and extract all data needed for display."""
    board = game.board()
    positions = []
    moves_san = []
    moves_uci = []
    
    # Store initial position
    positions.append(board.fen())
    
    # Collect all moves
    for move in game.mainline_moves():
        moves_san.append(board.san(move))
        moves_uci.append(move.uci())
        board.push(move)
        positions.append(board.fen())
    
    # Get game headers
    headers = dict(game.headers)
    
    # Generate SVG boards for all positions
    svg_boards = []
    for fen in positions:
        board = chess.Board(fen)
        svg = chess.svg.board(board, size=size)
        svg_boards.append(svg)
    
    return {
        'svg_boards': svg_boards,
        'moves_san': moves_san,
        'moves_uci': moves_uci,
        'positions': positions,
        'headers': headers
    }


def _create_multi_game_html_viewer(
    games,
    output_file,
    open_in_browser: bool,
    size: int
) -> str:
    """Create an HTML viewer for multiple chess games."""
    # Process all games
    games_data = []
    for game in games:
        game_data = _process_game(game, size)
        games_data.append(game_data)
    
    # Create output file if not specified
    if output_file is None:
        fd, output_file = tempfile.mkstemp(suffix='.html', prefix='chess_games_')
        os.close(fd)
    else:
        output_file = Path(output_file)
    
    # Generate HTML content
    html_content = _generate_multi_game_html_content(games_data, size)
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Open in browser if requested
    if open_in_browser:
        webbrowser.open(f'file://{os.path.abspath(output_file)}')
    
    return str(output_file)


def _generate_multi_game_html_content(games_data, size: int) -> str:
    """Generate HTML content for multiple games viewer."""
    num_games = len(games_data)
    
    # Format game list for navigation
    game_list_html = []
    for i, game_data in enumerate(games_data):
        headers = game_data['headers']
        event = headers.get('Event', f'Game {i + 1}')
        white = headers.get('White', 'Unknown')
        black = headers.get('Black', 'Unknown')
        result = headers.get('Result', '*')
        date = headers.get('Date', '')
        
        game_list_html.append(
            f'<div class="game-item" onclick="switchToGame({i})">'
            f'<strong>Game {i + 1}:</strong> {event} - {white} vs {black} ({result})'
            f'{f" - {date}" if date else ""}'
            f'</div>'
        )
    
    # Get current game data for initial display
    current_game = games_data[0]
    headers = current_game['headers']
    white = headers.get('White', 'Unknown')
    black = headers.get('Black', 'Unknown')
    event = headers.get('Event', 'Unknown Event')
    result = headers.get('Result', '*')
    date = headers.get('Date', '')
    site = headers.get('Site', '')
    
    # Format moves for first game
    moves_san = current_game['moves_san']
    move_list_html = []
    move_number = 1
    for i in range(0, len(moves_san), 2):
        white_move = moves_san[i] if i < len(moves_san) else ''
        black_move = moves_san[i + 1] if i + 1 < len(moves_san) else ''
        move_list_html.append(
            f'<span class="move-number">{move_number}.</span> '
            f'<span class="move white-move" data-index="{i}">{white_move}</span> '
            f'<span class="move black-move" data-index="{i + 1}">{black_move}</span>'
        )
        move_number += 1
    
    # Escape strings for JavaScript/HTML
    all_games_data = []
    for game_data in games_data:
        all_games_data.append({
            'boards': game_data['svg_boards'],
            'positions': game_data['positions'],
            'moves_san': game_data['moves_san'],
            'moves_uci': game_data['moves_uci'],
            'headers': game_data['headers']
        })
    
    games_json = json.dumps(all_games_data)
    
    # Generate move navigation buttons for first game
    first_game_positions = games_data[0]['positions']
    move_buttons_html = ''.join([
        f'<button class="move-btn" data-move="{i}">{i}</button>'
        for i in range(len(first_game_positions))
    ])
    
    env = _get_jinja_env()
    template = env.get_template("multi_game.html")
    
    return template.render(
        num_games=num_games,
        white=white,
        black=black,
        result=result,
        date=date,
        site=site,
        game_list_html=''.join(game_list_html),
        move_buttons_html=move_buttons_html,
        move_list_html=' '.join(move_list_html),
        games_json=games_json,
        first_game_moves_count=len(first_game_positions)
    )
