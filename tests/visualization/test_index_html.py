"""
Tests for index.html generation with games and divergence points.
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.visualization.chess_display import (
    create_index_html,
)


class TestCreateIndexHtml:
    """Tests for create_index_html function with games and opening repertoire."""
    
    def test_create_index_html_with_games(self):
        """Test creating index.html with games and opening repertoire."""
        games = [
            """[Event "Test Game 1"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 1-0""",
            """[Event "Test Game 2"]
[White "Player3"]
[Black "Player4"]
[Result "1/2-1/2"]

1. d4 d5 2. c4 e6 1/2-1/2"""
        ]
        opening_repertoire = ["1. e4 e5 2. Nf3 Nc6 3. Bb5"]
        
        with patch('webbrowser.open'):
            output_file = create_index_html(
                games=games,
                opening_repertoire=opening_repertoire,
                open_in_browser=False
            )
        
        assert os.path.exists(output_file)
        assert output_file.endswith('index.html')
        
        # Check HTML content
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            assert '<html' in html_content.lower()
            assert 'chess' in html_content.lower()
            assert 'Player1' in html_content or 'Player1' in html_content
            assert 'divergence' in html_content.lower()
        
        # Cleanup
        os.unlink(output_file)
    
    def test_create_index_html_with_opening_directory(self):
        """Test creating index.html with games and opening directory."""
        games = [
            """[Event "Test"]
[White "White"]
[Black "Black"]
[Result "1-0"]

1. e4 e5 1-0"""
        ]
        
        # Create temporary opening directory with a PGN file
        with tempfile.TemporaryDirectory() as tmpdir:
            opening_dir = Path(tmpdir) / "openings"
            opening_dir.mkdir()
            
            opening_file = opening_dir / "opening.pgn"
            with open(opening_file, 'w') as f:
                f.write("1. e4 e5 2. Nf3")
            
            with patch('webbrowser.open'):
                output_file = create_index_html(
                    games=games,
                    opening_repertoire=str(opening_dir),
                    open_in_browser=False
                )
            
            assert os.path.exists(output_file)
            
            # Cleanup
            os.unlink(output_file)
    
    def test_index_html_lists_all_games(self):
        """Test that index.html lists all provided games."""
        games = [
            """[Event "Game 1"]
1. e4 e5 1-0""",
            """[Event "Game 2"]
1. d4 d5 1/2-1/2""",
            """[Event "Game 3"]
1. c4 e5 0-1"""
        ]
        opening_repertoire = ["1. e4"]
        
        with patch('webbrowser.open'):
            output_file = create_index_html(
                games=games,
                opening_repertoire=opening_repertoire,
                open_in_browser=False
            )
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
                assert 'Game 1' in html_content
                assert 'Game 2' in html_content
                assert 'Game 3' in html_content
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_index_html_shows_divergence_points(self):
        """Test that index.html shows divergence points for games."""
        games = [
            """[Event "Divergence Test"]
1. e4 e5 2. Nf3 Nc6 3. Bc4 1-0"""
        ]
        opening_repertoire = ["1. e4 e5 2. Nf3 Nc6 3. Bb5"]
        
        with patch('webbrowser.open'):
            output_file = create_index_html(
                games=games,
                opening_repertoire=opening_repertoire,
                open_in_browser=False
            )
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
                # Should show divergence information
                assert '3. Bc4' in html_content or 'Bc4' in html_content
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_index_html_games_are_clickable(self):
        """Test that games in index.html are clickable/redirectable."""
        games = [
            """[Event "Clickable Game"]
1. e4 e5 1-0"""
        ]
        opening_repertoire = ["1. e4"]
        
        with patch('webbrowser.open'):
            output_file = create_index_html(
                games=games,
                opening_repertoire=opening_repertoire,
                open_in_browser=False
            )
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
                # Should have links or onclick handlers for games
                assert 'onclick' in html_content.lower() or 'href' in html_content.lower() or 'window.location' in html_content.lower()
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_index_html_empty_games_list(self):
        """Test creating index.html with empty games list raises error."""
        with pytest.raises(ValueError, match="games.*empty"):
            create_index_html(
                games=[],
                opening_repertoire=["1. e4"],
                open_in_browser=False
            )
    
    def test_index_html_default_location(self):
        """Test creating index.html in default location."""
        games = [
            """[Event "Test"]
1. e4 e5 1-0"""
        ]
        opening_repertoire = ["1. e4"]
        
        with patch('webbrowser.open'):
            output_file = create_index_html(
                games=games,
                opening_repertoire=opening_repertoire,
                open_in_browser=False
            )
        
        assert 'visualization' in str(output_file)
        
        # Cleanup
        os.unlink(output_file)
    
    def test_index_html_custom_location(self):
        """Test creating index.html in custom location."""
        games = [
            """[Event "Test"]
1. e4 e5 1-0"""
        ]
        opening_repertoire = ["1. e4"]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'index.html')
            
            with patch('webbrowser.open'):
                result_file = create_index_html(
                    games=games,
                    opening_repertoire=opening_repertoire,
                    output_file=output_path,
                    open_in_browser=False
                )
            
        assert result_file == output_path
        assert os.path.exists(output_path)


def test_variant_modal_and_dual_boards_present(tmp_path):
    """Test the modal for variant choice and dual SVG boards presence after divergence."""
    games = [
        """[Event "Modal Test"]\n[White "Alpha"]\n[Black "Beta"]\n[Result "1-0"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bc4 1-0"""
    ]
    opening_repertoire = ["1. e4 e5 2. Nf3 Nc6 3. Bb5"]
    index_path = tmp_path / "index.html"
    from unittest.mock import patch
    from src.visualization.chess_display import create_index_html
    with patch('webbrowser.open'):
        viewer_path = create_index_html(
            games=games,
            opening_repertoire=opening_repertoire,
            output_file=index_path,
            open_in_browser=False,
        )
    # Load the generated HTML
    with open(viewer_path, encoding="utf-8") as f:
        html = f.read()

    # Modal present
    assert 'id="variant-modal"' in html
    assert "Choose Variant to Follow" in html

    # There should be a divergence-point marker div (for popup to trigger)
    assert 'id="divergence-point-marker"' in html

    # There should be at least two SVG boards in the post-divergence view (main + opening)
    assert html.count("<svg") >= 2  # Not perfect, but rough coverage
