"""
Unit tests for Git integration functionality.
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock, call
from pathlib import Path

from core.git_integration import GitIntegration


class TestGitIntegration:
    """Test cases for GitIntegration class."""

    def test_init(self, test_data_dir: Path):
        """Test GitIntegration initialization."""
        git_integration = GitIntegration(str(test_data_dir))
        assert git_integration.base_path == str(test_data_dir)

    @patch('subprocess.run')
    def test_is_git_repository_true(self, mock_run: MagicMock, test_data_dir: Path):
        """Test is_git_repository when directory is a git repository."""
        # Mock successful git command
        mock_run.return_value = MagicMock(returncode=0)
        
        git_integration = GitIntegration(str(test_data_dir))
        assert git_integration.is_git_repository() is True
        
        # Verify git command was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert 'git' in call_args
        assert 'rev-parse' in call_args

    @patch('subprocess.run')
    def test_is_git_repository_false(self, mock_run: MagicMock, test_data_dir: Path):
        """Test is_git_repository when directory is not a git repository."""
        # Mock failed git command
        mock_run.return_value = MagicMock(returncode=128)
        
        git_integration = GitIntegration(str(test_data_dir))
        assert git_integration.is_git_repository() is False

    @patch('subprocess.run')
    def test_is_git_repository_exception(self, mock_run: MagicMock, test_data_dir: Path):
        """Test is_git_repository when git command raises exception."""
        # Mock exception
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        
        git_integration = GitIntegration(str(test_data_dir))
        assert git_integration.is_git_repository() is False

    @patch('subprocess.run')
    def test_get_git_status(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting git status."""
        # Mock git status output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=" M modified.txt\n?? untracked.txt\n A  added.txt\n"
        )
        
        git_integration = GitIntegration(str(test_data_dir))
        status = git_integration.get_git_status()
        
        assert isinstance(status, dict)
        assert "modified" in status
        assert "untracked" in status
        assert "added" in status
        assert "deleted" in status
        assert "branch" in status
        assert "clean" in status
        
        # Check parsed files
        assert len(status["modified"]) == 1
        assert "modified.txt" in status["modified"]
        assert len(status["untracked"]) == 1
        assert "untracked.txt" in status["untracked"]
        assert len(status["added"]) == 1
        assert "added.txt" in status["added"]

    @patch('subprocess.run')
    def test_get_git_status_clean(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting git status for clean repository."""
        # Mock clean git status
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )
        
        git_integration = GitIntegration(str(test_data_dir))
        status = git_integration.get_git_status()
        
        assert status["clean"] is True
        assert len(status["modified"]) == 0
        assert len(status["untracked"]) == 0
        assert len(status["added"]) == 0
        assert len(status["deleted"]) == 0

    @patch('subprocess.run')
    def test_get_git_status_not_git_repo(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting git status when not a git repository."""
        # Mock git command failure
        mock_run.return_value = MagicMock(returncode=128)
        
        git_integration = GitIntegration(str(test_data_dir))
        status = git_integration.get_git_status()
        
        assert status is None

    @patch('subprocess.run')
    def test_get_git_log(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting git log."""
        # Mock git log output
        mock_log_output = """commit abc123
Author: Test User <test@example.com>
Date: Mon Jan 1 12:00:00 2024 +0000

    Initial commit

commit def456
Author: Test User <test@example.com>
Date: Mon Jan 1 11:00:00 2024 +0000

    Second commit
"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mock_log_output
        )
        
        git_integration = GitIntegration(str(test_data_dir))
        log = git_integration.get_git_log(limit=10)
        
        assert isinstance(log, list)
        assert len(log) == 2
        
        # Check first commit
        assert log[0]["hash"] == "abc123"
        assert log[0]["author"] == "Test User <test@example.com>"
        assert log[0]["message"] == "Initial commit"
        assert "date" in log[0]
        
        # Check second commit
        assert log[1]["hash"] == "def456"
        assert log[1]["message"] == "Second commit"

    @patch('subprocess.run')
    def test_get_git_log_empty(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting git log for repository with no commits."""
        # Mock empty git log
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )
        
        git_integration = GitIntegration(str(test_data_dir))
        log = git_integration.get_git_log()
        
        assert isinstance(log, list)
        assert len(log) == 0

    @patch('subprocess.run')
    def test_get_git_log_not_git_repo(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting git log when not a git repository."""
        # Mock git command failure
        mock_run.return_value = MagicMock(returncode=128)
        
        git_integration = GitIntegration(str(test_data_dir))
        log = git_integration.get_git_log()
        
        assert log is None

    @patch('subprocess.run')
    def test_get_git_diff(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting git diff."""
        # Mock git diff output
        mock_diff_output = """diff --git a/file.txt b/file.txt
index 1234567..abcdefg 100644
--- a/file.txt
+++ b/file.txt
@@ -1,3 +1,3 @@
 line 1
-line 2
+line 2 modified
 line 3
"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mock_diff_output
        )
        
        git_integration = GitIntegration(str(test_data_dir))
        diff = git_integration.get_git_diff()
        
        assert isinstance(diff, str)
        assert "diff --git" in diff
        assert "line 2 modified" in diff

    @patch('subprocess.run')
    def test_get_git_diff_specific_file(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting git diff for specific file."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="diff for specific file"
        )
        
        git_integration = GitIntegration(str(test_data_dir))
        diff = git_integration.get_git_diff(file_path="README.md")
        
        assert isinstance(diff, str)
        assert diff == "diff for specific file"
        
        # Verify git command included file path
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "README.md" in call_args

    @patch('subprocess.run')
    def test_get_git_diff_no_changes(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting git diff when no changes exist."""
        # Mock empty diff
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )
        
        git_integration = GitIntegration(str(test_data_dir))
        diff = git_integration.get_git_diff()
        
        assert diff == ""

    @patch('subprocess.run')
    def test_get_git_diff_not_git_repo(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting git diff when not a git repository."""
        # Mock git command failure
        mock_run.return_value = MagicMock(returncode=128)
        
        git_integration = GitIntegration(str(test_data_dir))
        diff = git_integration.get_git_diff()
        
        assert diff is None

    @patch('subprocess.run')
    def test_get_current_branch(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting current branch."""
        # Mock git branch output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="main\n"
        )
        
        git_integration = GitIntegration(str(test_data_dir))
        branch = git_integration.get_current_branch()
        
        assert branch == "main"

    @patch('subprocess.run')
    def test_get_current_branch_detached_head(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting current branch in detached HEAD state."""
        # Mock detached HEAD
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="* (HEAD detached at abc123)\n"
        )
        
        git_integration = GitIntegration(str(test_data_dir))
        branch = git_integration.get_current_branch()
        
        assert "detached" in branch.lower()

    @patch('subprocess.run')
    def test_get_current_branch_not_git_repo(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting current branch when not a git repository."""
        # Mock git command failure
        mock_run.return_value = MagicMock(returncode=128)
        
        git_integration = GitIntegration(str(test_data_dir))
        branch = git_integration.get_current_branch()
        
        assert branch is None

    @patch('subprocess.run')
    def test_get_file_history(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting file history."""
        # Mock git log output for specific file
        mock_log_output = """commit abc123
Author: Test User <test@example.com>
Date: Mon Jan 1 12:00:00 2024 +0000

    Update README.md

commit def456
Author: Test User <test@example.com>
Date: Mon Jan 1 11:00:00 2024 +0000

    Add README.md
"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mock_log_output
        )
        
        git_integration = GitIntegration(str(test_data_dir))
        history = git_integration.get_file_history("README.md")
        
        assert isinstance(history, list)
        assert len(history) == 2
        assert history[0]["hash"] == "abc123"
        assert history[0]["message"] == "Update README.md"
        assert history[1]["hash"] == "def456"
        assert history[1]["message"] == "Add README.md"

    @patch('subprocess.run')
    def test_get_file_history_no_history(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting file history for file with no history."""
        # Mock empty git log
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )
        
        git_integration = GitIntegration(str(test_data_dir))
        history = git_integration.get_file_history("newfile.md")
        
        assert isinstance(history, list)
        assert len(history) == 0

    @patch('subprocess.run')
    def test_get_file_history_not_git_repo(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting file history when not a git repository."""
        # Mock git command failure
        mock_run.return_value = MagicMock(returncode=128)
        
        git_integration = GitIntegration(str(test_data_dir))
        history = git_integration.get_file_history("README.md")
        
        assert history is None

    @patch('subprocess.run')
    def test_command_execution_timeout(self, mock_run: MagicMock, test_data_dir: Path):
        """Test git command execution with timeout."""
        # Mock timeout exception
        mock_run.side_effect = subprocess.TimeoutExpired('git', 10)
        
        git_integration = GitIntegration(str(test_data_dir))
        result = git_integration.get_git_status()
        
        # Should handle timeout gracefully
        assert result is None

    @patch('subprocess.run')
    def test_command_execution_permission_error(self, mock_run: MagicMock, test_data_dir: Path):
        """Test git command execution with permission error."""
        # Mock permission error
        mock_run.side_effect = PermissionError("Permission denied")
        
        git_integration = GitIntegration(str(test_data_dir))
        result = git_integration.get_git_status()
        
        # Should handle permission error gracefully
        assert result is None

    @patch('subprocess.run')
    def test_parse_git_log_malformed(self, mock_run: MagicMock, test_data_dir: Path):
        """Test parsing malformed git log output."""
        # Mock malformed git log output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="malformed output without proper format"
        )
        
        git_integration = GitIntegration(str(test_data_dir))
        log = git_integration.get_git_log()
        
        # Should handle malformed output gracefully
        assert isinstance(log, list)
        # May be empty or contain partial data depending on implementation