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

# Import for divergence analysis
from src.parsers.pgn_tree_parser import (
    parse_pgn_string_to_tree,
    find_first_divergence_across_openings,
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
    divergence_point: Optional[List[str]] = None
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
        
    Returns:
        str: Path to the generated HTML file
        
    Raises:
        ValueError: If PGN string contains no valid game
        
    Example:
        >>> pgn = \"\"\"[Event "Test Game"]
        ... [White "Player1"]
        ... [Black "Player2"]
        ... [Result "1-0"]
        ...
        ... 1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0\"\"\"
        >>> display_game_from_string(pgn)
        '/tmp/tmpXXXXXX.html'
        
        >>> # With opening repertoire and divergence
        >>> opening = "1. e4 e5 2. Nf3 Nc6 3. Bb5"
        >>> divergence = ["1. e4", "1... e5", "2. Nf3", "2... Nc6", "3. Bc4"]
        >>> display_game_from_string(pgn, opening_pgn=opening, divergence_point=divergence)
        '/tmp/tmpXXXXXX.html'
    """
    game = chess.pgn.read_game(io.StringIO(pgn_string))
    
    if game is None:
        raise ValueError("No valid game found in PGN string")
    
    return _create_html_viewer(
        game, output_file, open_in_browser, size,
        opening_pgn=opening_pgn, divergence_point=divergence_point
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
        opening_pgn: PGN string of the opening repertoire
        divergence_point: List of moves up to and including the divergence point
        
    Returns:
        List[str]: List of moves (SAN) that continue from the divergence point in the opening
    """
    from src.parsers.pgn_tree_parser import parse_pgn_string_to_tree
    
    opening_tree = parse_pgn_string_to_tree(opening_pgn)
    
    # Navigate to the position just before divergence
    current_node = opening_tree.root
    divergence_moves = []
    
    # Extract move SANs from divergence_point (remove move numbers)
    for move_str in divergence_point[:-1]:  # All moves except the last (diverging) one
        # Extract SAN from "1. e4" or "1... e5" format
        parts = move_str.split('.', 1)
        if len(parts) > 1:
            san = parts[1].strip()
            if san.startswith('...'):
                san = san[3:].strip()
            divergence_moves.append(san)
    
    # Navigate to the position before divergence
    for move_san in divergence_moves:
        if move_san in current_node.children:
            current_node = current_node.children[move_san]
        else:
            return []  # Can't find the position in opening
    
    # Get the main variant continuation from this position
    variant_moves = []
    while current_node.children:
        # Get the first (main) variant
        first_move = list(current_node.children.keys())[0]
        variant_moves.append(first_move)
        current_node = current_node.children[first_move]
    
    return variant_moves


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
    parts = last_divergence.split('.', 1)
    if len(parts) > 1:
        san = parts[1].strip()
        if san.startswith('...'):
            san = san[3:].strip()
        
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
    divergence_point: Optional[List[str]] = None
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
    if opening_pgn and divergence_point:
        divergence_move_index = _find_divergence_move_index(divergence_point, moves_san)
        opening_variant = _extract_opening_variant(opening_pgn, divergence_point)
    
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
        divergence_point=divergence_point
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
    divergence_point: Optional[List[str]] = None
) -> str:
    """Generate HTML content for the chess game viewer."""
    # Format moves for display with divergence highlighting
    move_list_html = []
    move_number = 1
    for i in range(0, len(moves_san), 2):
        white_move = moves_san[i] if i < len(moves_san) else ''
        black_move = moves_san[i + 1] if i + 1 < len(moves_san) else ''
        
        # Check if this is the divergence move
        white_divergence = (divergence_move_index is not None and i == divergence_move_index)
        black_divergence = (divergence_move_index is not None and i + 1 == divergence_move_index)
        
        white_class = 'move white-move' + (' divergence-move' if white_divergence else '')
        black_class = 'move black-move' + (' divergence-move' if black_divergence else '')
        
        move_list_html.append(
            f'<span class="move-number">{move_number}.</span> '
            f'<span class="{white_class}" data-index="{i}">{white_move}</span> '
            f'<span class="{black_class}" data-index="{i + 1}">{black_move}</span>'
        )
        move_number += 1
    
    # Format opening variant for display
    opening_variant_html = ''
    if opening_variant:
        variant_moves = []
        move_num = len(divergence_point) // 2 + 1 if divergence_point else 1
        for idx, move in enumerate(opening_variant):
            if idx % 2 == 0:
                variant_moves.append(f'{move_num}. {move}')
            else:
                variant_moves.append(f'{move_num}... {move}')
                move_num += 1
        if len(opening_variant) % 2 == 1:
            # Last move was white, don't increment
            pass
        
        opening_variant_html = f'''
            <div class="opening-variant-container">
                <div class="opening-variant-title">Opening Repertoire Continuation:</div>
                <div class="opening-variant-moves">{' '.join(variant_moves)}</div>
            </div>
        '''
    
    # Generate move navigation buttons HTML
    move_buttons_html = ''.join([
        f'<button class="move-btn" data-move="{i}">{i}</button>'
        for i in range(len(positions))
    ])
    
    # Escape strings for JavaScript/HTML
    boards_json = json.dumps(svg_boards)
    positions_json = json.dumps(positions)
    moves_san_json = json.dumps(moves_san)
    moves_uci_json = json.dumps(moves_uci)
    event_escaped = event.replace('"', '&quot;')
    white_escaped = white.replace('"', '&quot;')
    black_escaped = black.replace('"', '&quot;')
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chess Game Viewer - {event_escaped}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 24px;
            margin-bottom: 10px;
        }}
        
        .game-info {{
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin-top: 15px;
            font-size: 14px;
        }}
        
        .game-info div {{
            margin: 5px;
        }}
        
        .game-info strong {{
            margin-right: 5px;
        }}
        
        .main-content {{
            display: flex;
            flex-direction: column;
            padding: 20px;
        }}
        
        @media (min-width: 768px) {{
            .main-content {{
                flex-direction: row;
            }}
        }}
        
        .board-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }}
        
        .board-wrapper {{
            position: relative;
            margin-bottom: 20px;
        }}
        
        #chessboard {{
            display: block;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            border-radius: 5px;
        }}
        
        .controls {{
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 20px;
        }}
        
        .btn {{
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            background: #4CAF50;
            color: white;
            transition: background 0.3s;
        }}
        
        .btn:hover {{
            background: #45a049;
        }}
        
        .btn:disabled {{
            background: #cccccc;
            cursor: not-allowed;
        }}
        
        .btn.prev {{
            background: #2196F3;
        }}
        
        .btn.prev:hover {{
            background: #0b7dda;
        }}
        
        .btn.next {{
            background: #ff9800;
        }}
        
        .btn.next:hover {{
            background: #e68900;
        }}
        
        .btn.first {{
            background: #9e9e9e;
        }}
        
        .btn.last {{
            background: #9e9e9e;
        }}
        
        .move-list-container {{
            flex: 1;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 5px;
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .move-list-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }}
        
        .move-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            line-height: 2;
        }}
        
        .move {{
            padding: 5px 10px;
            margin: 2px;
            border-radius: 3px;
            cursor: pointer;
            transition: background 0.2s;
            display: inline-block;
        }}
        
        .move:hover {{
            background: #e0e0e0;
        }}
        
        .move.active {{
            background: #4CAF50;
            color: white;
            font-weight: bold;
        }}
        
        .move.divergence-move {{
            background: #ff4444 !important;
            color: white !important;
            font-weight: bold;
            border: 2px solid #cc0000;
        }}
        
        .white-move {{
            background: #fff;
        }}
        
        .black-move {{
            background: #f0f0f0;
        }}
        
        .move-number {{
            font-weight: bold;
            color: #666;
            margin-right: 5px;
        }}
        
        .opening-variant-container {{
            margin-top: 20px;
            padding: 15px;
            background: #fff9e6;
            border-left: 4px solid #ff9800;
            border-radius: 5px;
        }}
        
        .opening-variant-title {{
            font-weight: bold;
            color: #e65100;
            margin-bottom: 10px;
            font-size: 16px;
        }}
        
        .opening-variant-moves {{
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #333;
            line-height: 1.8;
        }}
        
        .position-info {{
            margin-top: 15px;
            padding: 10px;
            background: #e3f2fd;
            border-radius: 5px;
            text-align: center;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }}
        
        .move-navigation {{
            margin-top: 10px;
            padding: 10px;
            background: #fff3e0;
            border-radius: 5px;
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            justify-content: center;
            max-height: 150px;
            overflow-y: auto;
        }}
        
        .move-btn {{
            padding: 5px 10px;
            border: 1px solid #ddd;
            border-radius: 3px;
            cursor: pointer;
            background: white;
            font-size: 12px;
        }}
        
        .move-btn:hover {{
            background: #f0f0f0;
        }}
        
        .move-btn.active {{
            background: #4CAF50;
            color: white;
            border-color: #4CAF50;
        }}
        
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 5px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #888;
            border-radius: 5px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #555;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{event_escaped}</h1>
            <div class="game-info">
                <div><strong>White:</strong> {white_escaped}</div>
                <div><strong>Black:</strong> {black_escaped}</div>
                <div><strong>Result:</strong> {result}</div>
                {f'<div><strong>Date:</strong> {date}</div>' if date else ''}
                {f'<div><strong>Site:</strong> {site.replace(chr(34), "&quot;")}</div>' if site else ''}
            </div>
        </div>
        
        <div class="main-content">
            <div class="board-container">
                <div class="board-wrapper">
                    <div id="chessboard"></div>
                </div>
                
                <div class="controls">
                    <button class="btn first" onclick="goToMove(0)">⏮ First</button>
                    <button class="btn prev" onclick="previousMove()">⏪ Previous</button>
                    <button class="btn next" onclick="nextMove()">Next ⏩</button>
                    <button class="btn last" onclick="goToMove({len(positions) - 1})">Last ⏭</button>
                </div>
                
                <div class="position-info">
                    <div>Move: <span id="current-move">0</span> / <span id="total-moves">{len(positions) - 1}</span></div>
                    <div>Position: <span id="position-fen"></span></div>
                </div>
                
                <div class="move-navigation">
                    {move_buttons_html}
                </div>
            </div>
            
            <div class="move-list-container">
                <div class="move-list-title">Move List</div>
                <div class="move-list">
                    {' '.join(move_list_html)}
                </div>
                {opening_variant_html}
            </div>
        </div>
    </div>
    
    <script>
        // Store all board positions
        const boards = {boards_json};
        const positions = {positions_json};
        const moves_san = {moves_san_json};
        const moves_uci = {moves_uci_json};
        
        let currentMove = 0;
        const totalMoves = positions.length - 1;
        
        // Initialize
        function init() {{
            updateBoard(0);
            setupMoveButtons();
            setupMoveList();
        }}
        
        // Update board display
        function updateBoard(moveIndex) {{
            currentMove = moveIndex;
            document.getElementById('chessboard').innerHTML = boards[moveIndex];
            document.getElementById('current-move').textContent = currentMove;
            document.getElementById('total-moves').textContent = totalMoves;
            document.getElementById('position-fen').textContent = positions[moveIndex];
            
            // Update button states
            document.querySelector('.btn.first').disabled = currentMove === 0;
            document.querySelector('.btn.prev').disabled = currentMove === 0;
            document.querySelector('.btn.next').disabled = currentMove === totalMoves;
            document.querySelector('.btn.last').disabled = currentMove === totalMoves;
            
            // Update active move buttons
            document.querySelectorAll('.move-btn').forEach((btn, idx) => {{
                btn.classList.toggle('active', idx === currentMove);
            }});
            
            // Update active moves in move list
            document.querySelectorAll('.move').forEach((moveEl) => {{
                const moveIdx = parseInt(moveEl.dataset.index);
                if (!isNaN(moveIdx)) {{
                    moveEl.classList.toggle('active', moveIdx < currentMove);
                }}
            }});
        }}
        
        // Navigation functions
        function goToMove(moveIndex) {{
            if (moveIndex >= 0 && moveIndex <= totalMoves) {{
                updateBoard(moveIndex);
            }}
        }}
        
        function previousMove() {{
            if (currentMove > 0) {{
                updateBoard(currentMove - 1);
            }}
        }}
        
        function nextMove() {{
            if (currentMove < totalMoves) {{
                updateBoard(currentMove + 1);
            }}
        }}
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'ArrowLeft') {{
                previousMove();
            }} else if (e.key === 'ArrowRight') {{
                nextMove();
            }} else if (e.key === 'Home') {{
                goToMove(0);
            }} else if (e.key === 'End') {{
                goToMove(totalMoves);
            }}
        }});
        
        // Setup move buttons
        function setupMoveButtons() {{
            document.querySelectorAll('.move-btn').forEach((btn, idx) => {{
                btn.addEventListener('click', () => goToMove(idx));
            }});
        }}
        
        // Setup move list clicks
        function setupMoveList() {{
            document.querySelectorAll('.move').forEach((moveEl) => {{
                const moveIdx = parseInt(moveEl.dataset.index);
                if (!isNaN(moveIdx) && moveIdx < positions.length - 1) {{
                    moveEl.addEventListener('click', () => {{
                        // Go to position after this move
                        goToMove(moveIdx + 1);
                    }});
                }}
            }});
        }}
        
        // Initialize on load
        window.addEventListener('load', init);
    </script>
</body>
</html>"""
    
    return html


def create_index_html(
    games: List[str],
    opening_repertoire: Union[List[str], str, Path],
    output_file: Optional[Union[str, Path]] = None,
    open_in_browser: bool = True,
    size: int = 400
) -> str:
    """
    Create an index.html file that displays all games with their divergence points.
    
    Creates an HTML index page that lists all provided games with their divergence
    information against an opening repertoire. Each game is clickable and redirects
    to a game viewer with divergence highlighting.
    
    Args:
        games: List of PGN strings representing the games to index
        opening_repertoire: List of PGN strings or path to directory containing opening PGN files
        output_file: Optional path to save the index.html file. 
                     If None, saves to src/visualization/index.html
        open_in_browser: If True, automatically opens the HTML file in the default browser
        size: Size of chess board in pixels (default: 400)
        
    Returns:
        str: Path to the generated index.html file
        
    Raises:
        ValueError: If games list is empty
        
    Example:
        >>> games = ["[Event \"Game\"]\\n1. e4 e5 1-0", "[Event \"Game2\"]\\n1. d4 d5 1-0"]
        >>> opening_repertoire = ["1. e4 e5 2. Nf3"]
        >>> create_index_html(games, opening_repertoire)
        '/path/to/src/visualization/index.html'
    """
    if not games:
        raise ValueError("games list cannot be empty")
    
    # Load opening repertoire
    opening_trees = []
    opening_pgns = []
    
    if isinstance(opening_repertoire, (str, Path)):
        # It's a directory path
        opening_dir = Path(opening_repertoire)
        if opening_dir.is_dir():
            for pgn_file in opening_dir.glob("*.pgn"):
                with open(pgn_file, encoding="utf-8") as f:
                    pgn_str = f.read()
                    opening_pgns.append(pgn_str)
                    opening_trees.append(parse_pgn_string_to_tree(pgn_str))
        else:
            raise ValueError(f"Opening repertoire path is not a directory: {opening_repertoire}")
    else:
        # It's a list of PGN strings
        opening_pgns = opening_repertoire
        opening_trees = [parse_pgn_string_to_tree(pgn) for pgn in opening_repertoire]
    
    if not opening_trees:
        raise ValueError("Opening repertoire cannot be empty")
    
    # Analyze each game and find divergence points
    game_data_list = []
    for idx, game_pgn in enumerate(games):
        try:
            game = chess.pgn.read_game(io.StringIO(game_pgn))
            if game is None:
                continue
                
            # Get game headers
            headers = dict(game.headers)
            
            # Find divergence point
            game_tree = parse_pgn_string_to_tree(game_pgn)
            divergence_point, opening_idx = find_first_divergence_across_openings(game_tree, opening_trees)
            
            # Get matching opening PGN
            matching_opening_pgn = opening_pgns[opening_idx] if opening_idx is not None and 0 <= opening_idx < len(opening_pgns) else None
            
            game_data_list.append({
                'index': idx,
                'pgn': game_pgn,
                'game': game,
                'headers': headers,
                'divergence_point': divergence_point,
                'opening_pgn': matching_opening_pgn,
                'opening_idx': opening_idx
            })
        except Exception as e:
            # Skip games that fail to parse
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
                divergence_point=game_data['divergence_point'] if game_data['divergence_point'] else None
            )
            game_viewer_files.append(str(viewer_file.name))
        except Exception:
            game_viewer_files.append(None)
    
    # Open in browser if requested
    if open_in_browser:
        webbrowser.open(f'file://{output_file.absolute()}')
    
    return str(output_file.absolute())


def _generate_index_html_content(game_data_list: List[dict], size: int) -> str:
    """Generate HTML content for the games index page."""
    num_games = len(game_data_list)
    
    # Build game list HTML
    game_list_items = []
    for game_data in game_data_list:
        headers = game_data['headers']
        event = headers.get('Event', f"Game {game_data['index'] + 1}")
        white = headers.get('White', 'Unknown')
        black = headers.get('Black', 'Unknown')
        result = headers.get('Result', '*')
        date = headers.get('Date', '')
        
        # Format divergence info
        divergence = game_data['divergence_point']
        if divergence:
            divergence_display = ' → '.join(divergence[-3:]) if len(divergence) > 3 else ' → '.join(divergence)
            divergence_html = f'<span class="divergence-info">Diverges at: {divergence_display}</span>'
        else:
            divergence_html = '<span class="divergence-info no-divergence">✓ Follows opening repertoire</span>'
        
        viewer_file = f"game_{game_data['index']}.html"
        event_escaped = event.replace('"', '&quot;').replace("'", "&#39;")
        white_escaped = white.replace('"', '&quot;').replace("'", "&#39;")
        black_escaped = black.replace('"', '&quot;').replace("'", "&#39;")
        
        game_list_items.append(f'''
            <div class="game-item" onclick="window.open('{viewer_file}', '_blank')">
                <div class="game-header">
                    <span class="game-number">#{game_data['index'] + 1}</span>
                    <span class="game-title">{event_escaped}</span>
                    <span class="game-result">{result}</span>
                </div>
                <div class="game-players">{white_escaped} vs {black_escaped}{f" - {date}" if date else ""}</div>
                <div class="game-divergence">{divergence_html}</div>
            </div>
        ''')
    
    games_list_html = '\n'.join(game_list_items)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chess Games Index - {num_games} Games</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .games-list {{
            padding: 30px;
            max-height: calc(100vh - 200px);
            overflow-y: auto;
        }}
        
        .games-list h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 20px;
        }}
        
        .game-item {{
            background: #f9f9f9;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .game-item:hover {{
            background: #f0f0f0;
            border-color: #667eea;
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .game-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
        }}
        
        .game-number {{
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        
        .game-title {{
            flex: 1;
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }}
        
        .game-result {{
            background: #4CAF50;
            color: white;
            padding: 5px 12px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 14px;
        }}
        
        .game-players {{
            color: #666;
            margin-bottom: 10px;
            font-size: 14px;
        }}
        
        .game-divergence {{
            margin-top: 10px;
            padding: 10px;
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            border-radius: 5px;
            font-size: 13px;
        }}
        
        .divergence-info {{
            color: #e65100;
            font-weight: 600;
        }}
        
        .divergence-info.no-divergence {{
            color: #2e7d32;
        }}
        
        .info-box {{
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 20px 30px;
            border-radius: 5px;
        }}
        
        .info-box h3 {{
            margin-bottom: 10px;
            color: #1976D2;
        }}
        
        .info-box p {{
            margin-bottom: 5px;
            color: #555;
            font-size: 14px;
        }}
        
        ::-webkit-scrollbar {{
            width: 10px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #888;
            border-radius: 5px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #555;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>♟️ Chess Games Index</h1>
            <p class="subtitle">Click on any game to view it with divergence analysis</p>
        </div>
        
        <div class="info-box">
            <h3>About This Index</h3>
            <p>This page shows all games analyzed against the opening repertoire.</p>
            <p>Games that diverge from the repertoire are highlighted in orange.</p>
            <p>Click any game to open its interactive viewer with divergence highlighting.</p>
        </div>
        
        <div class="games-list">
            <h2>Games ({num_games})</h2>
            {games_list_html}
        </div>
    </div>
</body>
</html>"""
    
    return html


def _process_game(game: chess.pgn.Game, size: int) -> dict:
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
    games: List[chess.pgn.Game],
    output_file: Optional[Union[str, Path]],
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


def _generate_multi_game_html_content(games_data: List[dict], size: int) -> str:
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
    event_escaped = event.replace('"', '&quot;').replace("'", "&#39;")
    white_escaped = white.replace('"', '&quot;').replace("'", "&#39;")
    black_escaped = black.replace('"', '&quot;').replace("'", "&#39;")
    site_escaped = site.replace('"', '&quot;').replace("'", "&#39;") if site else ''
    
    # Generate move navigation buttons for first game
    first_game_positions = games_data[0]['positions']
    move_buttons_html = ''.join([
        f'<button class="move-btn" data-move="{i}">{i}</button>'
        for i in range(len(first_game_positions))
    ])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chess Games Viewer - {num_games} Games</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 24px;
            margin-bottom: 10px;
        }}
        
        .game-info {{
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin-top: 15px;
            font-size: 14px;
        }}
        
        .game-info div {{
            margin: 5px;
        }}
        
        .game-info strong {{
            margin-right: 5px;
        }}
        
        .game-navigation {{
            background: #f0f0f0;
            padding: 15px;
            border-bottom: 2px solid #ddd;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .game-nav-controls {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        
        .game-nav-btn {{
            padding: 8px 16px;
            font-size: 14px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            background: #4CAF50;
            color: white;
            transition: background 0.3s;
        }}
        
        .game-nav-btn:hover {{
            background: #45a049;
        }}
        
        .game-nav-btn:disabled {{
            background: #cccccc;
            cursor: not-allowed;
        }}
        
        .game-nav-btn.prev {{
            background: #2196F3;
        }}
        
        .game-nav-btn.prev:hover {{
            background: #0b7dda;
        }}
        
        .game-nav-btn.next {{
            background: #ff9800;
        }}
        
        .game-nav-btn.next:hover {{
            background: #e68900;
        }}
        
        .game-list-container {{
            position: relative;
            max-width: 300px;
        }}
        
        .game-list-toggle {{
            padding: 8px 16px;
            background: #9e9e9e;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .game-list-dropdown {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            max-height: 300px;
            overflow-y: auto;
            display: none;
            z-index: 1000;
            margin-top: 5px;
        }}
        
        .game-list-dropdown.show {{
            display: block;
        }}
        
        .game-item {{
            padding: 10px;
            cursor: pointer;
            border-bottom: 1px solid #eee;
            font-size: 13px;
        }}
        
        .game-item:hover {{
            background: #f0f0f0;
        }}
        
        .game-item.active {{
            background: #e3f2fd;
            font-weight: bold;
        }}
        
        .main-content {{
            display: flex;
            flex-direction: column;
            padding: 20px;
        }}
        
        @media (min-width: 768px) {{
            .main-content {{
                flex-direction: row;
            }}
        }}
        
        .board-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }}
        
        .board-wrapper {{
            position: relative;
            margin-bottom: 20px;
        }}
        
        #chessboard {{
            display: block;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            border-radius: 5px;
        }}
        
        .controls {{
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 20px;
        }}
        
        .btn {{
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            background: #4CAF50;
            color: white;
            transition: background 0.3s;
        }}
        
        .btn:hover {{
            background: #45a049;
        }}
        
        .btn:disabled {{
            background: #cccccc;
            cursor: not-allowed;
        }}
        
        .btn.prev {{
            background: #2196F3;
        }}
        
        .btn.prev:hover {{
            background: #0b7dda;
        }}
        
        .btn.next {{
            background: #ff9800;
        }}
        
        .btn.next:hover {{
            background: #e68900;
        }}
        
        .btn.first {{
            background: #9e9e9e;
        }}
        
        .btn.last {{
            background: #9e9e9e;
        }}
        
        .move-list-container {{
            flex: 1;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 5px;
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .move-list-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }}
        
        .move-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            line-height: 2;
        }}
        
        .move {{
            padding: 5px 10px;
            margin: 2px;
            border-radius: 3px;
            cursor: pointer;
            transition: background 0.2s;
            display: inline-block;
        }}
        
        .move:hover {{
            background: #e0e0e0;
        }}
        
        .move.active {{
            background: #4CAF50;
            color: white;
            font-weight: bold;
        }}
        
        .white-move {{
            background: #fff;
        }}
        
        .black-move {{
            background: #f0f0f0;
        }}
        
        .move-number {{
            font-weight: bold;
            color: #666;
            margin-right: 5px;
        }}
        
        .position-info {{
            margin-top: 15px;
            padding: 10px;
            background: #e3f2fd;
            border-radius: 5px;
            text-align: center;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }}
        
        .move-navigation {{
            margin-top: 10px;
            padding: 10px;
            background: #fff3e0;
            border-radius: 5px;
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            justify-content: center;
            max-height: 150px;
            overflow-y: auto;
        }}
        
        .move-btn {{
            padding: 5px 10px;
            border: 1px solid #ddd;
            border-radius: 3px;
            cursor: pointer;
            background: white;
            font-size: 12px;
        }}
        
        .move-btn:hover {{
            background: #f0f0f0;
        }}
        
        .move-btn.active {{
            background: #4CAF50;
            color: white;
            border-color: #4CAF50;
        }}
        
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 5px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #888;
            border-radius: 5px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #555;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Chess Games Viewer - {num_games} Games</h1>
            <div class="game-info" id="current-game-info">
                <div><strong>White:</strong> {white_escaped}</div>
                <div><strong>Black:</strong> {black_escaped}</div>
                <div><strong>Result:</strong> {result}</div>
                {f'<div><strong>Date:</strong> {date}</div>' if date else ''}
                {f'<div><strong>Site:</strong> {site_escaped}</div>' if site else ''}
            </div>
        </div>
        
        <div class="game-navigation">
            <div class="game-nav-controls">
                <button class="game-nav-btn prev" onclick="previousGame()" id="prev-game-btn">⏮ Previous Game</button>
                <span id="game-counter">Game <span id="current-game-num">1</span> / {num_games}</span>
                <button class="game-nav-btn next" onclick="nextGame()" id="next-game-btn">Next Game ⏭</button>
            </div>
            <div class="game-list-container">
                <button class="game-list-toggle" onclick="toggleGameList()">Select Game ▼</button>
                <div class="game-list-dropdown" id="game-list-dropdown">
                    {''.join(game_list_html)}
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="board-container">
                <div class="board-wrapper">
                    <div id="chessboard"></div>
                </div>
                
                <div class="controls">
                    <button class="btn first" onclick="goToMove(0)">⏮ First</button>
                    <button class="btn prev" onclick="previousMove()">⏪ Previous</button>
                    <button class="btn next" onclick="nextMove()">Next ⏩</button>
                    <button class="btn last" onclick="goToMove({len(first_game_positions) - 1})" id="last-move-btn">Last ⏭</button>
                </div>
                
                <div class="position-info">
                    <div>Move: <span id="current-move">0</span> / <span id="total-moves">0</span></div>
                    <div>Position: <span id="position-fen"></span></div>
                </div>
                
                <div class="move-navigation" id="move-navigation">
                    {move_buttons_html}
                </div>
            </div>
            
            <div class="move-list-container">
                <div class="move-list-title">Move List</div>
                <div class="move-list" id="move-list">
                    {' '.join(move_list_html)}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Store all games data
        const gamesData = {games_json};
        let currentGameIndex = 0;
        let currentMove = 0;
        let totalMoves = 0;
        
        // Initialize
        function init() {{
            switchToGame(0);
        }}
        
        // Switch to a specific game
        function switchToGame(gameIndex) {{
            if (gameIndex < 0 || gameIndex >= gamesData.length) return;
            
            currentGameIndex = gameIndex;
            currentMove = 0;
            
            const game = gamesData[currentGameIndex];
            totalMoves = game.positions.length - 1;
            
            // Update game info header
            const headers = game.headers;
            const white = headers.White || 'Unknown';
            const black = headers.Black || 'Unknown';
            const result = headers.Result || '*';
            const date = headers.Date || '';
            const site = headers.Site || '';
            
            document.getElementById('current-game-info').innerHTML = `
                <div><strong>White:</strong> ${{white}}</div>
                <div><strong>Black:</strong> ${{black}}</div>
                <div><strong>Result:</strong> ${{result}}</div>
                ${{date ? `<div><strong>Date:</strong> ${{date}}</div>` : ''}}
                ${{site ? `<div><strong>Site:</strong> ${{site}}</div>` : ''}}
            `;
            
            // Update game counter
            document.getElementById('current-game-num').textContent = currentGameIndex + 1;
            
            // Update game navigation buttons
            document.getElementById('prev-game-btn').disabled = currentGameIndex === 0;
            document.getElementById('next-game-btn').disabled = currentGameIndex === gamesData.length - 1;
            
            // Update active game in list
            document.querySelectorAll('.game-item').forEach((item, idx) => {{
                item.classList.toggle('active', idx === currentGameIndex);
            }});
            
            // Hide game list dropdown
            document.getElementById('game-list-dropdown').classList.remove('show');
            
            // Regenerate move list
            updateMoveList();
            
            // Reset to first move
            updateBoard(0);
        }}
        
        // Update move list for current game
        function updateMoveList() {{
            const game = gamesData[currentGameIndex];
            const moves_san = game.moves_san;
            const moveListHtml = [];
            let moveNumber = 1;
            
            for (let i = 0; i < moves_san.length; i += 2) {{
                const whiteMove = moves_san[i] || '';
                const blackMove = moves_san[i + 1] || '';
                moveListHtml.push(
                    `<span class="move-number">${{moveNumber}}.</span> ` +
                    `<span class="move white-move" data-index="${{i}}">${{whiteMove}}</span> ` +
                    `<span class="move black-move" data-index="${{i + 1}}">${{blackMove}}</span>`
                );
                moveNumber++;
            }}
            
            document.getElementById('move-list').innerHTML = moveListHtml.join(' ');
            setupMoveList();
            
            // Update move navigation buttons
            const positions = game.positions;
            const moveNavHtml = positions.map((_, idx) => 
                `<button class="move-btn" data-move="${{idx}}">${{idx}}</button>`
            ).join('');
            document.getElementById('move-navigation').innerHTML = moveNavHtml;
            setupMoveButtons();
            
            // Update last move button
            document.getElementById('last-move-btn').setAttribute('onclick', `goToMove(${{positions.length - 1}})`);
        }}
        
        // Update board display
        function updateBoard(moveIndex) {{
            const game = gamesData[currentGameIndex];
            if (moveIndex < 0 || moveIndex >= game.positions.length) return;
            
            currentMove = moveIndex;
            document.getElementById('chessboard').innerHTML = game.boards[moveIndex];
            document.getElementById('current-move').textContent = currentMove;
            document.getElementById('total-moves').textContent = totalMoves;
            document.getElementById('position-fen').textContent = game.positions[moveIndex];
            
            // Update button states
            document.querySelector('.btn.first').disabled = currentMove === 0;
            document.querySelector('.btn.prev').disabled = currentMove === 0;
            document.querySelector('.btn.next').disabled = currentMove === totalMoves;
            document.querySelector('.btn.last').disabled = currentMove === totalMoves;
            
            // Update active move buttons
            document.querySelectorAll('.move-btn').forEach((btn, idx) => {{
                btn.classList.toggle('active', idx === currentMove);
            }});
            
            // Update active moves in move list
            document.querySelectorAll('.move').forEach((moveEl) => {{
                const moveIdx = parseInt(moveEl.dataset.index);
                if (!isNaN(moveIdx)) {{
                    moveEl.classList.toggle('active', moveIdx < currentMove);
                }}
            }});
        }}
        
        // Game navigation functions
        function previousGame() {{
            if (currentGameIndex > 0) {{
                switchToGame(currentGameIndex - 1);
            }}
        }}
        
        function nextGame() {{
            if (currentGameIndex < gamesData.length - 1) {{
                switchToGame(currentGameIndex + 1);
            }}
        }}
        
        function toggleGameList() {{
            const dropdown = document.getElementById('game-list-dropdown');
            dropdown.classList.toggle('show');
        }}
        
        // Move navigation functions
        function goToMove(moveIndex) {{
            const game = gamesData[currentGameIndex];
            if (moveIndex >= 0 && moveIndex < game.positions.length) {{
                updateBoard(moveIndex);
            }}
        }}
        
        function previousMove() {{
            if (currentMove > 0) {{
                updateBoard(currentMove - 1);
            }}
        }}
        
        function nextMove() {{
            if (currentMove < totalMoves) {{
                updateBoard(currentMove + 1);
            }}
        }}
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'ArrowLeft' && !e.shiftKey) {{
                previousMove();
            }} else if (e.key === 'ArrowRight' && !e.shiftKey) {{
                nextMove();
            }} else if (e.key === 'ArrowLeft' && e.shiftKey) {{
                previousGame();
            }} else if (e.key === 'ArrowRight' && e.shiftKey) {{
                nextGame();
            }} else if (e.key === 'Home') {{
                goToMove(0);
            }} else if (e.key === 'End') {{
                goToMove(totalMoves);
            }}
        }});
        
        // Setup move buttons
        function setupMoveButtons() {{
            document.querySelectorAll('.move-btn').forEach((btn, idx) => {{
                btn.addEventListener('click', () => goToMove(idx));
            }});
        }}
        
        // Setup move list clicks
        function setupMoveList() {{
            document.querySelectorAll('.move').forEach((moveEl) => {{
                const moveIdx = parseInt(moveEl.dataset.index);
                if (!isNaN(moveIdx) && moveIdx < gamesData[currentGameIndex].positions.length - 1) {{
                    moveEl.addEventListener('click', () => {{
                        goToMove(moveIdx + 1);
                    }});
                }}
            }});
        }}
        
        // Close game list when clicking outside
        document.addEventListener('click', function(e) {{
            const container = document.querySelector('.game-list-container');
            if (container && !container.contains(e.target)) {{
                document.getElementById('game-list-dropdown').classList.remove('show');
            }}
        }});
        
        // Initialize on load
        window.addEventListener('load', init);
    </script>
</body>
</html>"""
    
    return html
