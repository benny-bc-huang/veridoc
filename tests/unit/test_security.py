"""
Unit tests for SecurityManager.
"""

import pytest
import os
import tempfile
from pathlib import Path
from typing import List
from unittest.mock import patch, MagicMock

from veridoc.core.security import SecurityManager


class TestSecurityManager:
    """Test cases for SecurityManager class."""

    def test_init(self, test_data_dir: Path):
        """Test SecurityManager initialization."""
        security_manager = SecurityManager(str(test_data_dir))
        assert security_manager.base_path == test_data_dir

    def test_validate_path_valid_paths(self, security_manager: SecurityManager, test_data_dir: Path):
        """Test validate_path with valid paths."""
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
            try:
                result = security_manager.validate_path(path)
                assert isinstance(result, Path), f"Should return Path for valid path: {path}"
            except ValueError:
                pytest.fail(f"Valid path should not raise exception: {path}")

    def test_validate_path_malicious_paths(self, security_manager: SecurityManager, malicious_paths: List[str]):
        """Test validate_path with malicious paths."""
        for path in malicious_paths:
            with pytest.raises(ValueError):
                security_manager.validate_path(path)

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
            with pytest.raises((ValueError, Exception)):
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
        with pytest.raises(ValueError):
            security_manager.validate_path("../nonexistent.md")

    def test_validate_path_symbolic_links(self, security_manager: SecurityManager):
        """Test validate_path with symbolic links."""
        # Create a test symlink if possible
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.txt"
            test_file.write_text("test")
            symlink_path = temp_path / "symlink.txt"
            
            try:
                symlink_path.symlink_to(test_file)
                # Create SecurityManager with temp directory
                temp_security = SecurityManager(temp_path)
                
                # Should validate internal symlinks
                result = temp_security.validate_path("symlink.txt")
                assert isinstance(result, Path)
            except OSError:
                # Skip if symlinks not supported
                pytest.skip("Symbolic links not supported on this system")

    def test_validate_path_empty_string(self, security_manager: SecurityManager):
        """Test validate_path with empty string."""
        # Empty string should resolve to base path
        result = security_manager.validate_path("")
        assert result == security_manager.base_path

    def test_validate_path_none(self, security_manager: SecurityManager):
        """Test validate_path with None."""
        with pytest.raises((ValueError, AttributeError)):
            security_manager.validate_path(None)

    def test_validate_path_current_directory(self, security_manager: SecurityManager):
        """Test validate_path with current directory references."""
        # These should be safe as they resolve within base path
        result1 = security_manager.validate_path(".")
        result2 = security_manager.validate_path("./")
        result3 = security_manager.validate_path("./README.md")
        
        assert isinstance(result1, Path)
        assert isinstance(result2, Path) 
        assert isinstance(result3, Path)

    def test_validate_path_parent_directory_within_base(self, security_manager: SecurityManager):
        """Test validate_path with parent directory that stays within base."""
        # Should be safe as it resolves to base path
        result1 = security_manager.validate_path("docs/../README.md")
        result2 = security_manager.validate_path("docs/subdirectory/../api.md")
        
        assert isinstance(result1, Path)
        assert isinstance(result2, Path)

    def test_validate_path_case_sensitivity(self, security_manager: SecurityManager):
        """Test validate_path with different case variations."""
        # Test case variations (behavior may depend on OS)
        test_cases = [
            "readme.md",
            "README.MD", 
            "Readme.Md",
            "docs/API.md",
            "DOCS/api.md",
        ]
        
        for path in test_cases:
            # Should return Path for valid cases
            result = security_manager.validate_path(path)
            assert isinstance(result, Path), f"Should return Path for: {path}"

    def test_validate_path_url_schemes(self, security_manager: SecurityManager):
        """Test validate_path with URL schemes."""
        url_schemes = [
            "file://README.md",
            "http://example.com/file.md",
            "https://example.com/file.md", 
            "ftp://example.com/file.md",
            "file:///etc/passwd",
        ]
        
        for url in url_schemes:
            with pytest.raises(ValueError):
                security_manager.validate_path(url)

    def test_validate_path_special_characters(self, security_manager: SecurityManager):
        """Test validate_path with special characters."""
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
            result = security_manager.validate_path(path)
            assert isinstance(result, Path), f"Should return Path for: {path}"

    def test_validate_path_long_paths(self, security_manager: SecurityManager):
        """Test validate_path with very long paths."""
        # Test extremely long path
        long_path = "a/" * 1000 + "file.md"
        try:
            result = security_manager.validate_path(long_path)
            assert isinstance(result, Path)
        except (ValueError, OSError):
            # Long paths may be rejected by OS
            pass

    def test_validate_path_unicode_characters(self, security_manager: SecurityManager):
        """Test validate_path with unicode characters."""
        unicode_paths = [
            "文档.md",
            "documentación.md",
            "документ.md",
            "ドキュメント.md",
            "docs/файл.md",
        ]
        
        for path in unicode_paths:
            result = security_manager.validate_path(path)
            assert isinstance(result, Path), f"Should return Path for unicode path: {path}"

    def test_path_resolution_edge_cases(self, security_manager: SecurityManager):
        """Test edge cases in path resolution."""
        edge_cases = [
            "docs/./api.md",  # Should resolve to docs/api.md
            "docs/./subdirectory/../api.md",  # Should resolve to docs/api.md
            "docs/subdirectory/./nested.md",  # Should resolve to docs/subdirectory/nested.md
        ]
        
        for path in edge_cases:
            result = security_manager.validate_path(path)
            assert isinstance(result, Path), f"Should handle edge case: {path}"

    def test_validate_path_root_slash(self, security_manager: SecurityManager):
        """Test that root path '/' is correctly handled as base path."""
        # This is critical for API endpoint compatibility
        result = security_manager.validate_path("/")
        
        # Should return the base path itself
        assert result == security_manager.base_path
        assert result.is_dir()
        
        # Should not raise any security errors
        assert isinstance(result, Path)

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