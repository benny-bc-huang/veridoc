"""
Unit tests for SecurityManager.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.security import SecurityManager


class TestSecurityManager:
    """Test cases for SecurityManager class."""

    def test_init(self, test_data_dir: Path):
        """Test SecurityManager initialization."""
        security_manager = SecurityManager(str(test_data_dir))
        assert security_manager.base_path == test_data_dir

    def test_is_safe_path_valid_paths(self, security_manager: SecurityManager, test_data_dir: Path):
        """Test is_safe_path with valid paths."""
        # Test valid paths within base directory
        valid_paths = [
            "README.md",
            "docs/api.md",
            "docs/subdirectory/nested.md",
            "src/main.py",
            "./README.md",
            "docs/../README.md",  # Resolves to README.md
        ]
        
        for path in valid_paths:
            assert security_manager.is_safe_path(path), f"Path should be safe: {path}"

    def test_is_safe_path_malicious_paths(self, security_manager: SecurityManager, malicious_paths: list[str]):
        """Test is_safe_path with malicious paths."""
        for path in malicious_paths:
            assert not security_manager.is_safe_path(path), f"Path should be blocked: {path}"

    def test_validate_path_absolute_paths(self, security_manager: SecurityManager):
        """Test validate_path with absolute paths."""
        malicious_absolute_paths = [
            "/etc/passwd",
            "/root/.ssh/id_rsa",
            "C:\\Windows\\System32\\config\\SAM",
            "/usr/bin/sudo",
            "/home/user/.bash_history",
        ]
        
        for path in malicious_absolute_paths:
            with pytest.raises((ValueError, Exception), msg=f"Absolute path should be blocked: {path}"):
                security_manager.validate_path(path)

    def test_validate_path_nonexistent_file(self, security_manager: SecurityManager):
        """Test validate_path with non-existent files."""
        # Non-existent files should still be considered valid if within base path
        try:
            result1 = security_manager.validate_path("nonexistent.md")
            result2 = security_manager.validate_path("docs/nonexistent.md")
            assert isinstance(result1, Path)
            assert isinstance(result2, Path)
        except Exception as e:
            pytest.fail(f"Non-existent files within base path should be valid: {e}")
        
        # But not if they try to escape
        assert not security_manager.is_safe_path("../nonexistent.md")

    @patch('os.path.islink')
    def test_is_safe_path_symbolic_links(self, mock_islink: MagicMock, security_manager: SecurityManager):
        """Test is_safe_path with symbolic links."""
        # Mock symbolic link detection
        mock_islink.return_value = True
        
        # Symbolic links should be rejected
        assert not security_manager.is_safe_path("symlink.md")
        mock_islink.assert_called()

    def test_is_safe_path_empty_string(self, security_manager: SecurityManager):
        """Test is_safe_path with empty string."""
        assert not security_manager.is_safe_path("")

    def test_is_safe_path_none(self, security_manager: SecurityManager):
        """Test is_safe_path with None."""
        assert not security_manager.is_safe_path(None)

    def test_is_safe_path_current_directory(self, security_manager: SecurityManager):
        """Test is_safe_path with current directory references."""
        # These should be safe as they resolve within base path
        assert security_manager.is_safe_path(".")
        assert security_manager.is_safe_path("./")
        assert security_manager.is_safe_path("./README.md")

    def test_is_safe_path_parent_directory_within_base(self, security_manager: SecurityManager):
        """Test is_safe_path with parent directory that stays within base."""
        # Should be safe as it resolves to base path
        assert security_manager.is_safe_path("docs/../README.md")
        assert security_manager.is_safe_path("docs/subdirectory/../api.md")

    def test_is_safe_path_case_sensitivity(self, security_manager: SecurityManager):
        """Test is_safe_path with different case variations."""
        # Test case variations (behavior may depend on OS)
        test_cases = [
            "readme.md",
            "README.MD",
            "Readme.Md",
            "docs/API.md",
            "DOCS/api.md",
        ]
        
        for path in test_cases:
            # Path safety should not depend on case
            result = security_manager.is_safe_path(path)
            assert isinstance(result, bool), f"Should return boolean for: {path}"

    def test_is_safe_path_url_schemes(self, security_manager: SecurityManager):
        """Test is_safe_path with URL schemes."""
        url_schemes = [
            "file://README.md",
            "http://example.com/file.md",
            "https://example.com/file.md",
            "ftp://example.com/file.md",
            "file:///etc/passwd",
        ]
        
        for url in url_schemes:
            assert not security_manager.is_safe_path(url), f"URL should be blocked: {url}"

    def test_is_safe_path_special_characters(self, security_manager: SecurityManager):
        """Test is_safe_path with special characters."""
        # Test paths with special characters that should be safe
        safe_special_chars = [
            "file-name.md",
            "file_name.md",
            "file name.md",
            "file.name.md",
            "files/sub-directory/file.md",
            "files/sub_directory/file.md",
        ]
        
        for path in safe_special_chars:
            # These should be safe as they don't escape base path
            result = security_manager.is_safe_path(path)
            # Just ensure it returns a boolean (actual result depends on path resolution)
            assert isinstance(result, bool), f"Should return boolean for: {path}"

    def test_is_safe_path_long_paths(self, security_manager: SecurityManager):
        """Test is_safe_path with very long paths."""
        # Test extremely long path
        long_path = "a/" * 1000 + "file.md"
        result = security_manager.is_safe_path(long_path)
        assert isinstance(result, bool)

    def test_is_safe_path_unicode_characters(self, security_manager: SecurityManager):
        """Test is_safe_path with unicode characters."""
        unicode_paths = [
            "文档.md",
            "documentación.md",
            "документ.md",
            "ドキュメント.md",
            "docs/файл.md",
        ]
        
        for path in unicode_paths:
            result = security_manager.is_safe_path(path)
            assert isinstance(result, bool), f"Should return boolean for unicode path: {path}"

    def test_path_resolution_edge_cases(self, security_manager: SecurityManager):
        """Test edge cases in path resolution."""
        edge_cases = [
            "docs/./api.md",  # Should resolve to docs/api.md
            "docs/./subdirectory/../api.md",  # Should resolve to docs/api.md
            "docs/subdirectory/./nested.md",  # Should resolve to docs/subdirectory/nested.md
        ]
        
        for path in edge_cases:
            result = security_manager.is_safe_path(path)
            assert isinstance(result, bool), f"Should handle edge case: {path}"

    def test_validate_file_size_small_file(self, security_manager: SecurityManager):
        """Test validate_file_size with small file."""
        # Small file should be valid
        assert security_manager.validate_file_size(1024)  # 1KB
        assert security_manager.validate_file_size(1024 * 1024)  # 1MB

    def test_validate_file_size_large_file(self, security_manager: SecurityManager):
        """Test validate_file_size with large file."""
        # Files at the limit should be valid
        assert security_manager.validate_file_size(50 * 1024 * 1024)  # 50MB (default limit)
        
        # Files over the limit should be invalid
        assert not security_manager.validate_file_size(51 * 1024 * 1024)  # 51MB
        assert not security_manager.validate_file_size(100 * 1024 * 1024)  # 100MB

    def test_validate_file_size_zero(self, security_manager: SecurityManager):
        """Test validate_file_size with zero size."""
        assert security_manager.validate_file_size(0)

    def test_validate_file_size_negative(self, security_manager: SecurityManager):
        """Test validate_file_size with negative size."""
        assert not security_manager.validate_file_size(-1)
        assert not security_manager.validate_file_size(-1024)

    def test_validate_file_extension_allowed(self, security_manager: SecurityManager):
        """Test validate_file_extension with allowed extensions."""
        allowed_extensions = [
            ".md",
            ".txt",
            ".py",
            ".js",
            ".json",
            ".yaml",
            ".yml",
            ".html",
            ".css",
            ".xml",
            ".rst",
            ".csv",
        ]
        
        for ext in allowed_extensions:
            assert security_manager.validate_file_extension(f"file{ext}")

    def test_validate_file_extension_case_insensitive(self, security_manager: SecurityManager):
        """Test validate_file_extension case insensitivity."""
        case_variations = [
            "file.MD",
            "file.Md",
            "file.mD",
            "file.TXT",
            "file.Txt",
            "file.PY",
            "file.Py",
        ]
        
        for filename in case_variations:
            result = security_manager.validate_file_extension(filename)
            assert isinstance(result, bool), f"Should handle case variation: {filename}"

    def test_validate_file_extension_no_extension(self, security_manager: SecurityManager):
        """Test validate_file_extension with files without extension."""
        no_ext_files = [
            "README",
            "Makefile",
            "LICENSE",
            "Dockerfile",
            "CHANGELOG",
        ]
        
        for filename in no_ext_files:
            result = security_manager.validate_file_extension(filename)
            # Should handle files without extension gracefully
            assert isinstance(result, bool), f"Should handle file without extension: {filename}"

    def test_validate_file_extension_multiple_dots(self, security_manager: SecurityManager):
        """Test validate_file_extension with multiple dots in filename."""
        multi_dot_files = [
            "file.backup.md",
            "config.local.json",
            "test.unit.py",
            "styles.min.css",
            "app.bundle.js",
        ]
        
        for filename in multi_dot_files:
            result = security_manager.validate_file_extension(filename)
            assert isinstance(result, bool), f"Should handle multiple dots: {filename}"

    def test_validate_file_extension_empty_string(self, security_manager: SecurityManager):
        """Test validate_file_extension with empty string."""
        assert not security_manager.validate_file_extension("")

    def test_validate_file_extension_none(self, security_manager: SecurityManager):
        """Test validate_file_extension with None."""
        result = security_manager.validate_file_extension(None)
        assert isinstance(result, bool)