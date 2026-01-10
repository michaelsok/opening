"""
Tests for index.html generation with chess game redirect functionality.
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
    """Tests for create_index_html function."""
    
    def test_create_index_html_default_location(self):
        """Test creating index.html in default location (src/visualization)."""
        with patch('webbrowser.open'):
            output_file = create_index_html(open_in_browser=False)
        
        assert os.path.exists(output_file)
        assert output_file.endswith('index.html')
        assert 'visualization' in str(output_file)
        
        # Check HTML content
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            assert '<html' in html_content.lower()
            assert 'chess' in html_content.lower()
            assert 'redirect' in html_content.lower() or 'game' in html_content.lower()
            assert 'pgn' in html_content.lower()
        
        # Cleanup
        os.unlink(output_file)
    
    def test_create_index_html_custom_location(self):
        """Test creating index.html in custom location."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'index.html')
            
            with patch('webbrowser.open'):
                result_file = create_index_html(
                    output_file=output_path,
                    open_in_browser=False
                )
            
            assert result_file == output_path
            assert os.path.exists(output_path)
            
            # Check HTML content
            with open(output_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                assert '<html' in html_content.lower()
                assert 'chess' in html_content.lower()
    
    def test_index_html_contains_form(self):
        """Test that index.html contains a form for input."""
        with patch('webbrowser.open'):
            output_file = create_index_html(open_in_browser=False)
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
                assert '<form' in html_content.lower()
                assert 'input' in html_content.lower()
                assert 'textarea' in html_content.lower() or 'input' in html_content.lower()
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_index_html_handles_url_parameters(self):
        """Test that index.html can handle URL parameters for PGN input."""
        with patch('webbrowser.open'):
            output_file = create_index_html(open_in_browser=False)
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
                # Should have JavaScript to handle URL parameters
                assert 'urlparams' in html_content.lower() or 'urlsearchparams' in html_content.lower() or 'location.search' in html_content.lower()
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_index_html_has_redirect_logic(self):
        """Test that index.html has logic to redirect to game viewer."""
        with patch('webbrowser.open'):
            output_file = create_index_html(open_in_browser=False)
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
                # Should have JavaScript to create/redirect to game viewer
                assert 'display_game' in html_content.lower() or 'redirect' in html_content.lower() or 'window.location' in html_content.lower()
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
