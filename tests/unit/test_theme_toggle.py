"""
Tests for theme toggle functionality
"""

import pytest
from pathlib import Path


class TestThemeToggle:
    """Test cases for theme toggle feature."""

    def test_css_variables_exist(self):
        """Test that CSS files contain theme variables."""
        css_path = Path(__file__).parent.parent.parent / "veridoc" / "frontend" / "css" / "main.css"
        assert css_path.exists(), f"CSS file not found at {css_path}"
        
        css_content = css_path.read_text()
        
        # Check for CSS variables
        assert ":root {" in css_content, "Root CSS variables not found"
        assert "--bg-primary" in css_content, "Primary background variable not found"
        assert "--text-primary" in css_content, "Primary text variable not found"
        
        # Check for light theme
        assert '[data-theme="light"]' in css_content, "Light theme selector not found"

    def test_theme_js_exists(self):
        """Test that theme.js file exists."""
        theme_js_path = Path(__file__).parent.parent.parent / "veridoc" / "frontend" / "js" / "utils" / "theme.js"
        assert theme_js_path.exists(), f"theme.js not found at {theme_js_path}"
        
        js_content = theme_js_path.read_text()
        
        # Check for ThemeManager class
        assert "class ThemeManager" in js_content, "ThemeManager class not found"
        assert "loadTheme()" in js_content, "loadTheme method not found"
        assert "toggleTheme()" in js_content, "toggleTheme method not found"
        assert "localStorage" in js_content, "localStorage usage not found"

    def test_html_has_theme_toggle_button(self):
        """Test that index.html contains theme toggle button."""
        html_path = Path(__file__).parent.parent.parent / "veridoc" / "frontend" / "index.html"
        assert html_path.exists(), f"HTML file not found at {html_path}"
        
        html_content = html_path.read_text()
        
        # Check for theme toggle button
        assert 'id="theme-toggle"' in html_content, "Theme toggle button not found"
        assert "theme.js" in html_content, "theme.js script include not found"
        
        # Check for Prism theme links
        assert 'id="prism-theme-dark"' in html_content, "Dark Prism theme link not found"
        assert 'id="prism-theme-light"' in html_content, "Light Prism theme link not found"

    def test_app_js_initializes_theme_manager(self):
        """Test that app.js initializes ThemeManager."""
        app_js_path = Path(__file__).parent.parent.parent / "veridoc" / "frontend" / "js" / "app.js"
        assert app_js_path.exists(), f"app.js not found at {app_js_path}"
        
        js_content = app_js_path.read_text()
        
        # Check for ThemeManager initialization
        assert "new ThemeManager()" in js_content, "ThemeManager initialization not found"
        assert "this.components.themeManager" in js_content, "ThemeManager component assignment not found"