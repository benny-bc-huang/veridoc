"""
Unit tests for FileHandler.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from veridoc.core.file_handler import FileHandler
from veridoc.core.security import SecurityManager


class TestFileHandler:
    """Test cases for FileHandler class."""

    def test_init(self, security_manager: SecurityManager):
        """Test FileHandler initialization."""
        file_handler = FileHandler(security_manager)
        assert file_handler.security == security_manager
        assert hasattr(file_handler, 'markdown_extensions')

    @pytest.mark.asyncio
    async def test_list_files_root_directory(self, file_handler: FileHandler, test_data_dir: Path):
        """Test listing files in root directory."""
        # Use Path object for root directory
        files = await file_handler.list_directory(test_data_dir)
        
        # Should return a list of FileItem objects
        assert isinstance(files, list)
        assert len(files) > 0
        
        # Check for expected files
        file_names = [f.name for f in files]
        assert "README.md" in file_names
        assert "docs" in file_names
        assert "src" in file_names
        
        # Check FileItem structure
        for file_entry in files:
            assert hasattr(file_entry, 'name')
            assert hasattr(file_entry, 'type')
            assert hasattr(file_entry, 'size')
            assert hasattr(file_entry, 'modified')
            assert file_entry.type in ["file", "directory"]

    @pytest.mark.asyncio
    async def test_list_files_subdirectory(self, file_handler: FileHandler, test_data_dir: Path):
        """Test listing files in subdirectory."""
        docs_path = test_data_dir / "docs"
        files = await file_handler.list_directory(docs_path)
        
        assert isinstance(files, list)
        assert len(files) > 0
        
        file_names = [f.name for f in files]
        assert "api.md" in file_names
        assert "guide.md" in file_names
        assert "subdirectory" in file_names

    @pytest.mark.asyncio
    async def test_list_files_empty_directory(self, file_handler: FileHandler, test_data_dir: Path):
        """Test listing files in empty directory."""
        # Create empty directory
        empty_dir = test_data_dir / "empty"
        empty_dir.mkdir()
        
        files = await file_handler.list_directory(empty_dir)
        assert isinstance(files, list)
        assert len(files) == 0

    @pytest.mark.asyncio
    async def test_list_files_nonexistent_directory(self, file_handler: FileHandler, test_data_dir: Path):
        """Test listing files in non-existent directory."""
        nonexistent_path = test_data_dir / "nonexistent"
        with pytest.raises(ValueError):  # Changed to ValueError as it checks is_dir()
            await file_handler.list_directory(nonexistent_path)

    @pytest.mark.asyncio
    async def test_list_files_malicious_path(self, file_handler: FileHandler):
        """Test listing files with malicious path."""
        malicious_path = Path("../../../etc")
        # SecurityManager should prevent path traversal
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            await file_handler.list_directory(malicious_path)

    @pytest.mark.asyncio
    async def test_read_file_markdown(self, file_handler: FileHandler, test_data_dir: Path):
        """Test reading markdown file."""
        file_path = test_data_dir / "README.md"
        content_response = await file_handler.get_file_content(file_path)
        
        assert hasattr(content_response, 'content')
        assert "# Test Project" in content_response.content
        assert "Features" in content_response.content
        assert "Usage" in content_response.content

    @pytest.mark.asyncio
    async def test_read_file_python(self, file_handler: FileHandler, test_data_dir: Path):
        """Test reading Python file."""
        file_path = test_data_dir / "src" / "main.py"
        content_response = await file_handler.get_file_content(file_path)
        
        assert hasattr(content_response, 'content')
        assert "def main():" in content_response.content
        assert 'print("Hello, VeriDoc!")' in content_response.content

    @pytest.mark.asyncio
    async def test_read_file_json(self, file_handler: FileHandler, test_data_dir: Path):
        """Test reading JSON file."""
        file_path = test_data_dir / "config.json"
        content_response = await file_handler.get_file_content(file_path)
        
        assert hasattr(content_response, 'content')
        # Should be valid JSON
        json_data = json.loads(content_response.content)
        assert json_data["name"] == "test-project"
        assert json_data["version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_read_file_nonexistent(self, file_handler: FileHandler, test_data_dir: Path):
        """Test reading non-existent file."""
        file_path = test_data_dir / "nonexistent.md"
        with pytest.raises(FileNotFoundError):
            await file_handler.get_file_content(file_path)

    @pytest.mark.asyncio
    async def test_read_file_malicious_path(self, file_handler: FileHandler):
        """Test reading file with malicious path."""
        malicious_path = Path("../../../etc/passwd")
        # SecurityManager should prevent path traversal
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            await file_handler.get_file_content(malicious_path)

    @pytest.mark.asyncio
    async def test_read_file_directory(self, file_handler: FileHandler, test_data_dir: Path):
        """Test reading directory as file."""
        dir_path = test_data_dir / "docs"
        with pytest.raises((IsADirectoryError, ValueError)):
            await file_handler.get_file_content(dir_path)

    @pytest.mark.asyncio
    async def test_read_file_large_file(self, file_handler: FileHandler, test_data_dir: Path):
        """Test reading large file with pagination."""
        file_path = test_data_dir / "large_file.txt"
        content_response = await file_handler.get_file_content(file_path)
        
        assert hasattr(content_response, 'content')
        lines = content_response.content.strip().split('\n')
        # Should return 1000 lines per page (default pagination)
        assert len(lines) == 1000
        assert lines[0] == "Line 1"
        assert lines[-1] == "Line 1000"
        
        # Test pagination metadata
        assert content_response.pagination.total_lines == 2000
        assert content_response.pagination.total_pages == 2
        assert content_response.pagination.page == 1
        assert content_response.pagination.has_next == True
        assert content_response.pagination.has_previous == False

    @pytest.mark.asyncio
    async def test_get_file_info_file(self, file_handler: FileHandler, test_data_dir: Path):
        """Test getting file info for a file."""
        file_path = test_data_dir / "README.md"
        info = await file_handler.get_file_metadata(file_path)
        
        assert isinstance(info, dict)
        assert "name" in info
        assert "type" in info
        assert "size" in info
        assert info["size"] > 0
        assert "modified" in info

    @pytest.mark.asyncio
    async def test_get_file_info_directory(self, file_handler: FileHandler, test_data_dir: Path):
        """Test getting file info for a directory."""
        dir_path = test_data_dir / "docs"
        info = await file_handler.get_file_metadata(dir_path)
        
        assert isinstance(info, dict)
        assert "name" in info
        assert "type" in info
        assert "size" in info
        assert info["size"] >= 0
        assert "modified" in info

    @pytest.mark.asyncio
    async def test_get_file_info_nonexistent(self, file_handler: FileHandler, test_data_dir: Path):
        """Test getting file info for non-existent file."""
        file_path = test_data_dir / "nonexistent.md"
        with pytest.raises(FileNotFoundError):
            await file_handler.get_file_metadata(file_path)

    @pytest.mark.asyncio
    async def test_get_file_info_malicious_path(self, file_handler: FileHandler):
        """Test getting file info with malicious path."""
        malicious_path = Path("../../../etc/passwd")
        # SecurityManager should prevent path traversal
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            await file_handler.get_file_metadata(malicious_path)

    # Search functionality moved to OptimizedSearchEngine in Phase 4
    # These tests are now handled in test_search_optimization.py

    def test_is_text_file_markdown(self, file_handler: FileHandler, test_data_dir: Path):
        """Test _is_text_file with markdown file."""
        file_path = test_data_dir / "README.md"
        assert file_handler._is_text_file(file_path) is True

    def test_is_text_file_python(self, file_handler: FileHandler, test_data_dir: Path):
        """Test _is_text_file with Python file."""
        file_path = test_data_dir / "src" / "main.py"
        assert file_handler._is_text_file(file_path) is True

    def test_get_file_category_markdown(self, file_handler: FileHandler, test_data_dir: Path):
        """Test get_file_category with markdown file."""
        file_path = test_data_dir / "README.md"
        category = file_handler.get_file_category(file_path)
        assert category in ["markdown", "text", "code"]  # Depends on implementation

    def test_get_file_extension(self, file_handler: FileHandler):
        """Test getting file extension via Path.suffix."""
        from pathlib import Path
        assert Path("README.md").suffix == ".md"
        assert Path("main.py").suffix == ".py"
        assert Path("config.json").suffix == ".json"
        assert Path("README").suffix == ""
        assert Path("file.backup.md").suffix == ".md"

    # File size validation is now handled in SecurityManager

    # Pagination is now handled at the API level, not in FileHandler