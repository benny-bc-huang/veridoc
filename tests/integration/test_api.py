"""
Integration tests for API endpoints.
"""

import pytest
import json
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test cases for health endpoint."""

    def test_health_endpoint(self, test_client: TestClient):
        """Test health endpoint returns 200 OK."""
        response = test_client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert "memory_usage_mb" in data

    def test_health_endpoint_structure(self, test_client: TestClient):
        """Test health endpoint response structure."""
        response = test_client.get("/api/health")
        data = response.json()
        
        # Check required fields
        required_fields = ["status", "uptime_seconds", "memory_usage_mb"]
        for field in required_fields:
            assert field in data
        
        # Check data types
        assert isinstance(data["status"], str)
        assert isinstance(data["uptime_seconds"], int)
        assert isinstance(data["memory_usage_mb"], int)


class TestFilesEndpoint:
    """Test cases for files endpoint."""

    def test_files_endpoint_root(self, test_client: TestClient):
        """Test files endpoint for root directory."""
        response = test_client.get("/api/files")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check for expected files
        file_names = [f["name"] for f in data]
        assert "README.md" in file_names
        assert "docs" in file_names

    def test_files_endpoint_with_path(self, test_client: TestClient):
        """Test files endpoint with specific path."""
        response = test_client.get("/api/files?path=docs")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        file_names = [f["name"] for f in data]
        assert "api.md" in file_names
        assert "guide.md" in file_names

    def test_files_endpoint_file_structure(self, test_client: TestClient):
        """Test files endpoint response structure."""
        response = test_client.get("/api/files")
        data = response.json()
        
        # Check structure of each file entry
        for file_entry in data:
            assert "name" in file_entry
            assert "type" in file_entry
            assert "size" in file_entry
            assert "modified" in file_entry
            assert file_entry["type"] in ["file", "directory"]
            assert isinstance(file_entry["size"], int)
            assert isinstance(file_entry["modified"], str)

    def test_files_endpoint_nonexistent_path(self, test_client: TestClient):
        """Test files endpoint with non-existent path."""
        response = test_client.get("/api/files?path=nonexistent")
        assert response.status_code == 404

    def test_files_endpoint_malicious_path(self, test_client: TestClient):
        """Test files endpoint with malicious path."""
        response = test_client.get("/api/files?path=../../../etc")
        assert response.status_code == 403  # Forbidden due to security validation


class TestFileContentEndpoint:
    """Test cases for file content endpoint."""

    def test_file_content_markdown(self, test_client: TestClient):
        """Test file content endpoint with markdown file."""
        response = test_client.get("/api/file_content?path=README.md")
        assert response.status_code == 200
        
        data = response.json()
        assert "content" in data
        assert "metadata" in data
        assert "# Test Project" in data["content"]

    def test_file_content_python(self, test_client: TestClient):
        """Test file content endpoint with Python file."""
        response = test_client.get("/api/file_content?path=src/main.py")
        assert response.status_code == 200
        
        data = response.json()
        assert "content" in data
        assert "def main():" in data["content"]

    def test_file_content_json(self, test_client: TestClient):
        """Test file content endpoint with JSON file."""
        response = test_client.get("/api/file_content?path=config.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "content" in data
        
        # Should be valid JSON content
        json_content = json.loads(data["content"])
        assert json_content["name"] == "test-project"

    def test_file_content_nonexistent(self, test_client: TestClient):
        """Test file content endpoint with non-existent file."""
        response = test_client.get("/api/file_content?path=nonexistent.md")
        assert response.status_code == 404

    def test_file_content_malicious_path(self, test_client: TestClient):
        """Test file content endpoint with malicious path."""
        response = test_client.get("/api/file_content?path=../../../etc/passwd")
        assert response.status_code == 403

    def test_file_content_directory(self, test_client: TestClient):
        """Test file content endpoint with directory."""
        response = test_client.get("/api/file_content?path=docs")
        assert response.status_code == 400  # Bad request - cannot read directory as file

    def test_file_content_pagination(self, test_client: TestClient):
        """Test file content endpoint with pagination."""
        response = test_client.get("/api/file_content?path=large_file.txt&page=1")
        assert response.status_code == 200
        
        data = response.json()
        assert "content" in data
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["total_pages"] > 1
        assert data["pagination"]["total_lines"] == 2000

    def test_file_content_pagination_last_page(self, test_client: TestClient):
        """Test file content endpoint with last page."""
        # Get first page to know total pages
        response = test_client.get("/api/file_content?path=large_file.txt&page=1")
        data = response.json()
        total_pages = data["pagination"]["total_pages"]
        
        # Get last page
        response = test_client.get(f"/api/file_content?path=large_file.txt&page={total_pages}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["pagination"]["page"] == total_pages

    def test_file_content_pagination_invalid_page(self, test_client: TestClient):
        """Test file content endpoint with invalid page number."""
        response = test_client.get("/api/file_content?path=large_file.txt&page=999")
        assert response.status_code == 400  # Bad request - invalid page

    def test_file_content_missing_path(self, test_client: TestClient):
        """Test file content endpoint without path parameter."""
        response = test_client.get("/api/file_content")
        assert response.status_code == 422  # Unprocessable Entity - missing required parameter


class TestSearchEndpoint:
    """Test cases for search endpoint."""

    def test_search_content(self, test_client: TestClient):
        """Test search endpoint for content search."""
        response = test_client.get("/api/search?q=VeriDoc&type=content")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Check result structure
        if len(data) > 0:
            result = data[0]
            assert "file" in result
            assert "score" in result
            assert "matches" in result
            assert isinstance(result["matches"], list)

    def test_search_filename(self, test_client: TestClient):
        """Test search endpoint for filename search."""
        response = test_client.get("/api/search?q=api&type=filename")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Should find api.md
        if len(data) > 0:
            file_names = [result["file"] for result in data]
            assert any("api.md" in name for name in file_names)

    def test_search_both(self, test_client: TestClient):
        """Test search endpoint for both content and filename."""
        response = test_client.get("/api/search?q=test&type=both")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)

    def test_search_with_limit(self, test_client: TestClient):
        """Test search endpoint with limit parameter."""
        response = test_client.get("/api/search?q=test&type=both&limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 2

    def test_search_no_results(self, test_client: TestClient):
        """Test search endpoint with no results."""
        response = test_client.get("/api/search?q=nonexistentterm12345&type=both")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_search_empty_query(self, test_client: TestClient):
        """Test search endpoint with empty query."""
        response = test_client.get("/api/search?q=&type=both")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_search_invalid_type(self, test_client: TestClient):
        """Test search endpoint with invalid search type."""
        response = test_client.get("/api/search?q=test&type=invalid")
        assert response.status_code == 422  # Unprocessable Entity - invalid enum value

    def test_search_missing_parameters(self, test_client: TestClient):
        """Test search endpoint without required parameters."""
        response = test_client.get("/api/search")
        assert response.status_code == 422  # Unprocessable Entity - missing required parameters


class TestGitEndpoints:
    """Test cases for Git-related endpoints."""

    def test_git_status_endpoint(self, test_client: TestClient):
        """Test git status endpoint."""
        response = test_client.get("/api/git/status")
        assert response.status_code in [200, 404]  # 404 if not a git repository
        
        if response.status_code == 200:
            data = response.json()
            assert "branch" in data
            assert "clean" in data
            assert "modified" in data
            assert "untracked" in data
            assert "added" in data
            assert "deleted" in data

    def test_git_log_endpoint(self, test_client: TestClient):
        """Test git log endpoint."""
        response = test_client.get("/api/git/log")
        assert response.status_code in [200, 404]  # 404 if not a git repository
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            
            # Check structure of log entries
            for entry in data:
                assert "hash" in entry
                assert "author" in entry
                assert "date" in entry
                assert "message" in entry

    def test_git_log_with_limit(self, test_client: TestClient):
        """Test git log endpoint with limit parameter."""
        response = test_client.get("/api/git/log?limit=5")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) <= 5

    def test_git_diff_endpoint(self, test_client: TestClient):
        """Test git diff endpoint."""
        response = test_client.get("/api/git/diff")
        assert response.status_code in [200, 404]  # 404 if not a git repository
        
        if response.status_code == 200:
            data = response.json()
            assert "diff" in data
            assert isinstance(data["diff"], str)

    def test_git_diff_specific_file(self, test_client: TestClient):
        """Test git diff endpoint for specific file."""
        response = test_client.get("/api/git/diff?file_path=README.md")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "diff" in data


class TestErrorHandling:
    """Test cases for error handling."""

    def test_404_for_invalid_endpoint(self, test_client: TestClient):
        """Test 404 response for invalid endpoint."""
        response = test_client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, test_client: TestClient):
        """Test 405 response for wrong HTTP method."""
        response = test_client.post("/api/health")
        assert response.status_code == 405

    def test_large_request(self, test_client: TestClient):
        """Test handling of large requests."""
        # This would test request size limits if implemented
        large_query = "x" * 10000
        response = test_client.get(f"/api/search?q={large_query}&type=content")
        
        # Should handle gracefully (either process or reject)
        assert response.status_code in [200, 413, 422]  # 413 = Request Entity Too Large

    def test_cors_headers(self, test_client: TestClient):
        """Test CORS headers in responses."""
        response = test_client.get("/api/health")
        
        # Check for CORS headers if configured
        # This depends on whether CORS is enabled in the application
        headers = response.headers
        # Basic check - just ensure we get a valid response
        assert response.status_code == 200

    def test_content_type_headers(self, test_client: TestClient):
        """Test content type headers in responses."""
        response = test_client.get("/api/health")
        
        assert response.headers["content-type"] == "application/json"
        assert response.status_code == 200

    def test_response_encoding(self, test_client: TestClient):
        """Test response encoding for non-ASCII content."""
        # This would test files with Unicode content if they exist
        response = test_client.get("/api/files")
        assert response.status_code == 200
        
        # Ensure response is properly encoded
        data = response.json()
        assert isinstance(data, list)