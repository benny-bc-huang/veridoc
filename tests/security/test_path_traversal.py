"""
Security tests for path traversal prevention.
"""

import pytest
from fastapi.testclient import TestClient


class TestPathTraversalPrevention:
    """Test cases for path traversal attack prevention."""

    def test_basic_path_traversal_attempts(self, test_client: TestClient):
        """Test basic path traversal attempts are blocked."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM",
            "../../../../../../../../etc/passwd",
            "../",
            "..\\",
            "../../",
            "..\\..\\",
        ]
        
        for path in malicious_paths:
            # Test file listing
            response = test_client.get(f"/api/files?path={path}")
            assert response.status_code == 403, f"Path should be blocked: {path}"
            
            # Test file content
            response = test_client.get(f"/api/file_content?path={path}")
            assert response.status_code == 403, f"Path should be blocked: {path}"

    def test_url_encoded_path_traversal(self, test_client: TestClient):
        """Test URL-encoded path traversal attempts are blocked."""
        url_encoded_paths = [
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # ../../../etc/passwd
            "%2e%2e%5c%2e%2e%5c%2e%2e%5cwindows%5csystem32",  # ..\..\..\windows\system32
            "%2e%2e%2f",  # ../
            "%2e%2e%5c",  # ..\
        ]
        
        for path in url_encoded_paths:
            response = test_client.get(f"/api/files?path={path}")
            assert response.status_code == 403, f"URL-encoded path should be blocked: {path}"

    def test_double_encoded_path_traversal(self, test_client: TestClient):
        """Test double URL-encoded path traversal attempts are blocked."""
        double_encoded_paths = [
            "%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd",
            "%252e%252e%255c%252e%252e%255c%252e%252e%255cwindows",
        ]
        
        for path in double_encoded_paths:
            response = test_client.get(f"/api/files?path={path}")
            assert response.status_code in [403, 422], f"Double-encoded path should be blocked: {path}"

    def test_unicode_path_traversal(self, test_client: TestClient):
        """Test Unicode-based path traversal attempts are blocked."""
        unicode_paths = [
            "\u002e\u002e\u002f\u002e\u002e\u002f\u002e\u002e\u002fetc\u002fpasswd",  # ../../../etc/passwd
            "\uff0e\uff0e\uff0f\uff0e\uff0e\uff0f\uff0e\uff0e\uff0fetc\uff0fpasswd",  # fullwidth characters
        ]
        
        for path in unicode_paths:
            response = test_client.get(f"/api/files?path={path}")
            assert response.status_code in [403, 422], f"Unicode path should be blocked: {path}"

    def test_null_byte_injection(self, test_client: TestClient):
        """Test null byte injection attempts are blocked."""
        # Test URL-encoded null bytes (these can be sent via HTTP)
        url_encoded_null_paths = [
            "../../etc/passwd%00.txt",
            "../../../etc/passwd%00.md", 
            "safe_file.txt%00../../etc/passwd",
        ]
        
        for path in url_encoded_null_paths:
            response = test_client.get(f"/api/files?path={path}")
            assert response.status_code in [403, 422], f"Null byte path should be blocked: {path}"
            
        # Test direct SecurityManager validation for raw null bytes
        from veridoc.core.security import SecurityManager
        import tempfile
        from pathlib import Path
        
        temp_dir = Path(tempfile.mkdtemp()) 
        security_manager = SecurityManager(temp_dir)
        
        raw_null_paths = [
            "../../etc/passwd\x00.txt",
            "safe_file.txt\x00../../etc/passwd",
        ]
        
        for path in raw_null_paths:
            try:
                security_manager.validate_path(path)
                assert False, f"Raw null byte path should be blocked: {repr(path)}"
            except ValueError:
                pass  # Expected - null bytes should be blocked

    def test_file_protocol_attempts(self, test_client: TestClient):
        """Test file:// protocol attempts are blocked."""
        file_protocol_paths = [
            "file:///etc/passwd",
            "file://C:\\Windows\\System32\\config\\SAM",
            "file://localhost/etc/passwd",
            "file:///root/.ssh/id_rsa",
        ]
        
        for path in file_protocol_paths:
            response = test_client.get(f"/api/files?path={path}")
            assert response.status_code == 403, f"File protocol path should be blocked: {path}"

    def test_network_path_attempts(self, test_client: TestClient):
        """Test network path attempts are blocked."""
        network_paths = [
            "//server/share/file",
            "\\\\server\\share\\file",
            "http://example.com/malicious",
            "https://example.com/malicious",
            "ftp://example.com/malicious",
        ]
        
        for path in network_paths:
            response = test_client.get(f"/api/files?path={path}")
            assert response.status_code == 403, f"Network path should be blocked: {path}"

    def test_long_path_attempts(self, test_client: TestClient):
        """Test extremely long path attempts."""
        # Create extremely long path with traversal attempts
        long_path = "../" * 1000 + "etc/passwd"
        
        response = test_client.get(f"/api/files?path={long_path}")
        assert response.status_code in [403, 414, 422]  # 414 = URI Too Long

    def test_special_file_attempts(self, test_client: TestClient):
        """Test attempts to access special system files."""
        special_files = [
            "/proc/version",
            "/proc/self/environ",
            "/proc/self/cmdline",
            "/dev/null",
            "/dev/random",
            "C:\\boot.ini",
            "C:\\autoexec.bat",
            "/etc/shadow",
            "/etc/hosts",
            "/root/.bash_history",
        ]
        
        for path in special_files:
            response = test_client.get(f"/api/file_content?path={path}")
            assert response.status_code == 403, f"Special file should be blocked: {path}"

    def test_case_variation_attempts(self, test_client: TestClient):
        """Test case variation bypass attempts."""
        case_variations = [
            "../../../ETC/PASSWD",
            "../../../Etc/Passwd",
            "..\\..\\..\\WINDOWS\\SYSTEM32\\CONFIG\\SAM",
            "..\\..\\..\\Windows\\System32\\Config\\Sam",
        ]
        
        for path in case_variations:
            response = test_client.get(f"/api/files?path={path}")
            assert response.status_code == 403, f"Case variation should be blocked: {path}"

    def test_mixed_separator_attempts(self, test_client: TestClient):
        """Test mixed path separator attempts."""
        mixed_paths = [
            "../../../etc\\passwd",
            "..\\..\\../etc/passwd",
            "../..\\../etc\\passwd",
        ]
        
        for path in mixed_paths:
            response = test_client.get(f"/api/files?path={path}")
            assert response.status_code == 403, f"Mixed separator path should be blocked: {path}"

    def test_relative_path_normalization(self, test_client: TestClient):
        """Test that relative paths that resolve within base directory are allowed."""
        safe_relative_paths = [
            "docs/../README.md",  # Should resolve to README.md
            "docs/./api.md",  # Should resolve to docs/api.md
            "./README.md",  # Should resolve to README.md
            "docs/subdirectory/../api.md",  # Should resolve to docs/api.md
        ]
        
        for path in safe_relative_paths:
            response = test_client.get(f"/api/file_content?path={path}")
            # These should either work (200) or give file not found (404)
            # but should NOT give permission denied (403)
            assert response.status_code in [200, 404], f"Safe relative path should be allowed: {path}"

    def test_symlink_attempts(self, test_client: TestClient):
        """Test symbolic link attempts are blocked."""
        # This test would require creating symbolic links in the test environment
        # For now, we test the detection mechanism indirectly
        
        # Test paths that might be symbolic links
        potential_symlinks = [
            "/usr/bin/python",
            "/bin/sh",
            "/tmp",
        ]
        
        for path in potential_symlinks:
            response = test_client.get(f"/api/files?path={path}")
            assert response.status_code == 403, f"Potential symlink should be blocked: {path}"

    def test_search_path_traversal(self, test_client: TestClient):
        """Test path traversal in search functionality."""
        # Test that search doesn't allow traversal via the query parameter
        malicious_queries = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/passwd",
        ]
        
        for query in malicious_queries:
            response = test_client.get(f"/api/search?q={query}&type=both")
            # Search should process the query safely, not treat it as a path
            assert response.status_code == 200
            
            # Ensure search results don't contain system files
            data = response.json()
            if len(data) > 0:
                for result in data:
                    file_path = result.get("file", "")
                    assert not any(sys_path in file_path.lower() 
                                 for sys_path in ["/etc/", "/proc/", "/sys/", "\\windows\\"])

    def test_git_diff_path_traversal(self, test_client: TestClient):
        """Test path traversal in git diff file_path parameter."""
        malicious_git_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
        ]
        
        for path in malicious_git_paths:
            response = test_client.get(f"/api/git/diff?file_path={path}")
            # Should either work safely or be rejected
            assert response.status_code in [200, 403, 404]
            
            if response.status_code == 200:
                data = response.json()
                # Ensure diff doesn't contain system file content
                diff_content = data.get("diff", "")
                assert not any(sys_indicator in diff_content.lower() 
                             for sys_indicator in ["root:x:", "administrator", "system32"])

    def test_error_message_information_disclosure(self, test_client: TestClient):
        """Test that error messages don't disclose sensitive path information."""
        malicious_paths = [
            "../../../etc/passwd",
            "/root/.ssh/id_rsa",
            "C:\\Windows\\System32\\config\\SAM",
        ]
        
        for path in malicious_paths:
            response = test_client.get(f"/api/files?path={path}")
            assert response.status_code == 403
            
            # Check that error message doesn't reveal actual system paths
            error_data = response.json()
            error_message = error_data.get("detail", "").lower()
            
            # Error message should not contain sensitive path information
            assert "/etc/" not in error_message
            assert "/root/" not in error_message
            assert "c:\\" not in error_message
            assert "windows" not in error_message

    def test_timing_attack_resistance(self, test_client: TestClient):
        """Test that response times don't reveal path existence."""
        import time
        
        # Test with non-existent safe path
        start_time = time.time()
        response1 = test_client.get("/api/files?path=nonexistent_safe_file.md")
        safe_time = time.time() - start_time
        
        # Test with malicious path
        start_time = time.time()
        response2 = test_client.get("/api/files?path=../../../etc/passwd")
        malicious_time = time.time() - start_time
        
        # Both should be rejected quickly and with similar timing
        assert response1.status_code == 404  # File not found
        assert response2.status_code == 403  # Permission denied
        
        # Timing should be similar (within reasonable variance)
        time_difference = abs(safe_time - malicious_time)
        assert time_difference < 0.1, "Response times should be similar to prevent timing attacks"