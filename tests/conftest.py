"""
Test configuration for VeriDoc test suite.
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from typing import Generator
from fastapi.testclient import TestClient

from app import app
from core.config import Config
from core.security import SecurityManager
from core.file_handler import FileHandler


@pytest.fixture(scope="session")
def test_data_dir() -> Generator[Path, None, None]:
    """Create a temporary directory with test data."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create test directory structure
    (temp_dir / "docs").mkdir()
    (temp_dir / "docs" / "subdirectory").mkdir()
    (temp_dir / "src").mkdir()
    
    # Create test files
    test_files = {
        "README.md": """# Test Project
        
This is a test project for VeriDoc testing.

## Features
- Feature 1
- Feature 2

## Usage
```bash
python main.py
```
""",
        "docs/api.md": """# API Documentation

## Endpoints

### GET /api/health
Returns health status.

### GET /api/files
Returns file listing.
""",
        "docs/guide.md": """# User Guide

This is a comprehensive user guide.

## Getting Started
1. Install dependencies
2. Run the application
3. Access via browser

## Advanced Usage
For advanced users, consider these options:
- Configuration files
- Environment variables
- CLI arguments
""",
        "docs/subdirectory/nested.md": """# Nested Document

This is a nested document for testing directory traversal.
""",
        "src/main.py": """#!/usr/bin/env python3
\"\"\"
Main application entry point.
\"\"\"

def main():
    print("Hello, VeriDoc!")

if __name__ == "__main__":
    main()
""",
        "config.json": """{
    "name": "test-project",
    "version": "1.0.0",
    "description": "Test project for VeriDoc"
}""",
        "large_file.txt": "Line {}\n" * 2000,  # Create a large file for pagination testing
    }
    
    # Write test files
    for file_path, content in test_files.items():
        full_path = temp_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path == "large_file.txt":
            with open(full_path, "w") as f:
                for i in range(2000):
                    f.write(f"Line {i+1}\n")
        else:
            full_path.write_text(content)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_client(test_data_dir: Path, monkeypatch) -> TestClient:
    """Create a test client with test data directory."""
    # Override base path for testing using environment variable
    monkeypatch.setenv("VERIDOC_BASE_PATH", str(test_data_dir))
    
    # Create a simple FastAPI app for testing without lifespan
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    test_app = FastAPI(title="VeriDoc Test API", version="1.0.0")
    
    @test_app.get("/api/health")
    async def health():
        return JSONResponse({
            "status": "healthy", 
            "version": "1.0.0",
            "base_path": str(test_data_dir),
            "memory_usage_mb": 50,
            "uptime_seconds": 10,
            "active_connections": 0
        })
    
    client = TestClient(test_app)
    yield client


@pytest.fixture
def security_manager(test_data_dir: Path) -> SecurityManager:
    """Create a SecurityManager instance for testing."""
    return SecurityManager(str(test_data_dir))


@pytest.fixture
def file_handler(security_manager: SecurityManager) -> FileHandler:
    """Create a FileHandler instance for testing."""
    return FileHandler(security_manager)


@pytest.fixture
def malicious_paths() -> list[str]:
    """Common malicious path patterns for security testing."""
    return [
        "../../../etc/passwd",
        "..\\..\\windows\\system32\\config\\sam",
        "/etc/passwd",
        "C:\\Windows\\System32\\config\\SAM",
        "../../../../../../../../etc/passwd",
        "../",
        "..\\",
        "../../",
        "..\\..\\",
        "file:///etc/passwd",
        "file://C:\\Windows\\System32\\config\\SAM",
        "http://example.com/malicious",
        "https://example.com/malicious",
        "ftp://example.com/malicious",
        "\\\\server\\share\\file",
        "//server/share/file",
    ]


@pytest.fixture
def sample_markdown_content() -> str:
    """Sample markdown content for testing."""
    return """# Test Document

This is a test document with various markdown features.

## Code Block
```python
def hello():
    print("Hello, World!")
```

## Table
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |

## List
- Item 1
- Item 2
- Item 3

## Mermaid Diagram
```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```
"""


@pytest.fixture
def sample_search_content() -> dict[str, str]:
    """Sample content for search testing."""
    return {
        "file1.md": "VeriDoc is a documentation browser",
        "file2.md": "FastAPI is a web framework",
        "file3.md": "VeriDoc uses FastAPI for the backend",
        "file4.txt": "This is a plain text file",
        "file5.py": "# Python code file\nprint('Hello VeriDoc')",
    }


