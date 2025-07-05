"""
Unit tests for FileHandler.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.file_handler import FileHandler


class TestFileHandler:
    """Test cases for FileHandler class."""

    def test_init(self, test_data_dir: Path):
        """Test FileHandler initialization."""
        file_handler = FileHandler(str(test_data_dir))
        assert file_handler.base_path == str(test_data_dir)
        assert file_handler.security_manager is not None

    def test_list_files_root_directory(self, file_handler: FileHandler):
        """Test listing files in root directory."""
        files = file_handler.list_files(".")
        
        # Should return a list of file entries
        assert isinstance(files, list)
        assert len(files) > 0
        
        # Check for expected files
        file_names = [f["name"] for f in files]
        assert "README.md" in file_names
        assert "docs" in file_names
        assert "src" in file_names
        
        # Check file entry structure
        for file_entry in files:
            assert "name" in file_entry
            assert "type" in file_entry
            assert "size" in file_entry
            assert "modified" in file_entry
            assert file_entry["type"] in ["file", "directory"]

    def test_list_files_subdirectory(self, file_handler: FileHandler):
        """Test listing files in subdirectory."""
        files = file_handler.list_files("docs")
        
        assert isinstance(files, list)
        assert len(files) > 0
        
        file_names = [f["name"] for f in files]
        assert "api.md" in file_names
        assert "guide.md" in file_names
        assert "subdirectory" in file_names

    def test_list_files_empty_directory(self, file_handler: FileHandler, test_data_dir: Path):
        """Test listing files in empty directory."""
        # Create empty directory
        empty_dir = test_data_dir / "empty"
        empty_dir.mkdir()
        
        files = file_handler.list_files("empty")
        assert isinstance(files, list)
        assert len(files) == 0

    def test_list_files_nonexistent_directory(self, file_handler: FileHandler):
        """Test listing files in non-existent directory."""
        with pytest.raises(FileNotFoundError):
            file_handler.list_files("nonexistent")

    def test_list_files_malicious_path(self, file_handler: FileHandler):
        """Test listing files with malicious path."""
        with pytest.raises(PermissionError):
            file_handler.list_files("../../../etc")

    def test_read_file_markdown(self, file_handler: FileHandler):
        """Test reading markdown file."""
        content = file_handler.read_file("README.md")
        
        assert isinstance(content, str)
        assert "# Test Project" in content
        assert "Features" in content
        assert "Usage" in content

    def test_read_file_python(self, file_handler: FileHandler):
        """Test reading Python file."""
        content = file_handler.read_file("src/main.py")
        
        assert isinstance(content, str)
        assert "def main():" in content
        assert 'print("Hello, VeriDoc!")' in content

    def test_read_file_json(self, file_handler: FileHandler):
        """Test reading JSON file."""
        content = file_handler.read_file("config.json")
        
        assert isinstance(content, str)
        # Should be valid JSON
        json_data = json.loads(content)
        assert json_data["name"] == "test-project"
        assert json_data["version"] == "1.0.0"

    def test_read_file_nonexistent(self, file_handler: FileHandler):
        """Test reading non-existent file."""
        with pytest.raises(FileNotFoundError):
            file_handler.read_file("nonexistent.md")

    def test_read_file_malicious_path(self, file_handler: FileHandler):
        """Test reading file with malicious path."""
        with pytest.raises(PermissionError):
            file_handler.read_file("../../../etc/passwd")

    def test_read_file_directory(self, file_handler: FileHandler):
        """Test reading directory as file."""
        with pytest.raises(IsADirectoryError):
            file_handler.read_file("docs")

    def test_read_file_large_file(self, file_handler: FileHandler):
        """Test reading large file."""
        content = file_handler.read_file("large_file.txt")
        
        assert isinstance(content, str)
        lines = content.strip().split('\n')
        assert len(lines) == 2000
        assert lines[0] == "Line 1"
        assert lines[-1] == "Line 2000"

    def test_get_file_info_file(self, file_handler: FileHandler):
        """Test getting file info for a file."""
        info = file_handler.get_file_info("README.md")
        
        assert isinstance(info, dict)
        assert info["name"] == "README.md"
        assert info["type"] == "file"
        assert info["size"] > 0
        assert "modified" in info
        assert isinstance(info["modified"], str)

    def test_get_file_info_directory(self, file_handler: FileHandler):
        """Test getting file info for a directory."""
        info = file_handler.get_file_info("docs")
        
        assert isinstance(info, dict)
        assert info["name"] == "docs"
        assert info["type"] == "directory"
        assert info["size"] >= 0
        assert "modified" in info

    def test_get_file_info_nonexistent(self, file_handler: FileHandler):
        """Test getting file info for non-existent file."""
        with pytest.raises(FileNotFoundError):
            file_handler.get_file_info("nonexistent.md")

    def test_get_file_info_malicious_path(self, file_handler: FileHandler):
        """Test getting file info with malicious path."""
        with pytest.raises(PermissionError):
            file_handler.get_file_info("../../../etc/passwd")

    def test_search_files_content(self, file_handler: FileHandler):
        """Test searching file content."""
        results = file_handler.search_files("VeriDoc", search_type="content")
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Check result structure
        for result in results:
            assert "file" in result
            assert "score" in result
            assert "matches" in result
            assert isinstance(result["matches"], list)

    def test_search_files_filenames(self, file_handler: FileHandler):
        """Test searching file names."""
        results = file_handler.search_files("api", search_type="filename")
        
        assert isinstance(results, list)
        
        # Should find api.md
        file_names = [result["file"] for result in results]
        assert any("api.md" in name for name in file_names)

    def test_search_files_both(self, file_handler: FileHandler):
        """Test searching both content and filenames."""
        results = file_handler.search_files("test", search_type="both")
        
        assert isinstance(results, list)
        # Should find results from both content and filename matching

    def test_search_files_no_results(self, file_handler: FileHandler):
        """Test searching with no results."""
        results = file_handler.search_files("nonexistentterm12345", search_type="both")
        
        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_files_empty_query(self, file_handler: FileHandler):
        """Test searching with empty query."""
        results = file_handler.search_files("", search_type="both")
        
        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_files_invalid_type(self, file_handler: FileHandler):
        """Test searching with invalid search type."""
        with pytest.raises(ValueError):
            file_handler.search_files("test", search_type="invalid")

    def test_search_files_limit(self, file_handler: FileHandler):
        """Test search results limit."""
        # Search for common term that should return many results
        results = file_handler.search_files("test", search_type="both", limit=2)
        
        assert isinstance(results, list)
        assert len(results) <= 2

    def test_is_text_file_markdown(self, file_handler: FileHandler):
        """Test is_text_file with markdown file."""
        assert file_handler.is_text_file("README.md") is True

    def test_is_text_file_python(self, file_handler: FileHandler):
        """Test is_text_file with Python file."""
        assert file_handler.is_text_file("main.py") is True

    def test_is_text_file_json(self, file_handler: FileHandler):
        """Test is_text_file with JSON file."""
        assert file_handler.is_text_file("config.json") is True

    def test_is_text_file_binary(self, file_handler: FileHandler):
        """Test is_text_file with binary file extensions."""
        binary_files = [
            "image.png",
            "document.pdf",
            "archive.zip",
            "executable.exe",
            "library.dll",
        ]
        
        for filename in binary_files:
            assert file_handler.is_text_file(filename) is False

    def test_is_text_file_no_extension(self, file_handler: FileHandler):
        """Test is_text_file with files without extension."""
        no_ext_files = [
            "README",
            "Makefile",
            "LICENSE",
            "Dockerfile",
        ]
        
        for filename in no_ext_files:
            result = file_handler.is_text_file(filename)
            # Should handle gracefully, result depends on implementation
            assert isinstance(result, bool)

    def test_get_file_extension(self, file_handler: FileHandler):
        """Test getting file extension."""
        assert file_handler.get_file_extension("README.md") == ".md"
        assert file_handler.get_file_extension("main.py") == ".py"
        assert file_handler.get_file_extension("config.json") == ".json"
        assert file_handler.get_file_extension("README") == ""
        assert file_handler.get_file_extension("file.backup.md") == ".md"

    def test_get_file_extension_edge_cases(self, file_handler: FileHandler):
        """Test getting file extension with edge cases."""
        assert file_handler.get_file_extension("") == ""
        assert file_handler.get_file_extension(".") == ""
        assert file_handler.get_file_extension("..") == ""
        assert file_handler.get_file_extension(".hidden") == ""
        assert file_handler.get_file_extension(".hidden.md") == ".md"

    @patch('os.path.getsize')
    def test_validate_file_size_mock(self, mock_getsize: MagicMock, file_handler: FileHandler):
        """Test file size validation with mocked file size."""
        # Mock file size
        mock_getsize.return_value = 1024  # 1KB
        
        # Should be valid
        assert file_handler.validate_file_size("test.md") is True
        
        # Mock large file size
        mock_getsize.return_value = 100 * 1024 * 1024  # 100MB
        
        # Should be invalid (exceeds 50MB default limit)
        assert file_handler.validate_file_size("large.md") is False

    def test_paginate_content(self, file_handler: FileHandler):
        """Test content pagination."""
        # Create content with many lines
        content = "\n".join([f"Line {i}" for i in range(2000)])
        
        # Test first page
        page1 = file_handler.paginate_content(content, page=1, lines_per_page=100)
        assert isinstance(page1, dict)
        assert "content" in page1
        assert "page" in page1
        assert "total_pages" in page1
        assert "total_lines" in page1
        assert page1["page"] == 1
        assert page1["total_pages"] == 20  # 2000 / 100
        assert page1["total_lines"] == 2000
        
        # Content should have 100 lines
        content_lines = page1["content"].strip().split('\n')
        assert len(content_lines) == 100
        assert content_lines[0] == "Line 0"
        assert content_lines[99] == "Line 99"

    def test_paginate_content_last_page(self, file_handler: FileHandler):
        """Test content pagination for last page."""
        # Create content with 150 lines
        content = "\n".join([f"Line {i}" for i in range(150)])
        
        # Test last page (should have 50 lines)
        page2 = file_handler.paginate_content(content, page=2, lines_per_page=100)
        assert page2["page"] == 2
        assert page2["total_pages"] == 2
        
        content_lines = page2["content"].strip().split('\n')
        assert len(content_lines) == 50
        assert content_lines[0] == "Line 100"
        assert content_lines[49] == "Line 149"

    def test_paginate_content_invalid_page(self, file_handler: FileHandler):
        """Test content pagination with invalid page number."""
        content = "\n".join([f"Line {i}" for i in range(100)])
        
        # Test page 0
        with pytest.raises(ValueError):
            file_handler.paginate_content(content, page=0)
        
        # Test negative page
        with pytest.raises(ValueError):
            file_handler.paginate_content(content, page=-1)
        
        # Test page beyond total pages
        with pytest.raises(ValueError):
            file_handler.paginate_content(content, page=10, lines_per_page=100)

    def test_paginate_content_small_content(self, file_handler: FileHandler):
        """Test content pagination with small content."""
        content = "Line 1\nLine 2\nLine 3"
        
        page1 = file_handler.paginate_content(content, page=1, lines_per_page=100)
        assert page1["page"] == 1
        assert page1["total_pages"] == 1
        assert page1["total_lines"] == 3
        assert page1["content"] == content

    def test_paginate_content_empty_content(self, file_handler: FileHandler):
        """Test content pagination with empty content."""
        content = ""
        
        page1 = file_handler.paginate_content(content, page=1, lines_per_page=100)
        assert page1["page"] == 1
        assert page1["total_pages"] == 1
        assert page1["total_lines"] == 0
        assert page1["content"] == ""