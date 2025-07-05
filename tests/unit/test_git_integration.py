"""
Unit tests for Git integration functionality.
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock, call
from pathlib import Path

from veridoc.core.git_integration import GitIntegration


class TestGitIntegration:
    """Test cases for GitIntegration class."""

    def test_init(self, test_data_dir: Path):
        """Test GitIntegration initialization."""
        git_integration = GitIntegration(str(test_data_dir))
        assert git_integration.base_path == test_data_dir

    def test_is_git_repository_true(self, test_data_dir: Path):
        """Test is_git_repository when directory is a git repository."""
        # Create .git directory to simulate git repository
        git_dir = test_data_dir / ".git"
        git_dir.mkdir(exist_ok=True)
        
        git_integration = GitIntegration(str(test_data_dir))
        assert git_integration.is_git_repository is True

    def test_is_git_repository_false(self, test_data_dir: Path):
        """Test is_git_repository when directory is not a git repository."""
        # Create a completely isolated directory outside any git repo
        isolated_dir = Path("/tmp") / "isolated_test_dir"
        isolated_dir.mkdir(exist_ok=True)
        
        git_integration = GitIntegration(str(isolated_dir))
        assert git_integration.is_git_repository is False
        
        # Cleanup
        isolated_dir.rmdir()

    def test_is_git_repository_exception(self, test_data_dir: Path):
        """Test is_git_repository when directory structure is invalid."""
        # Create a new isolated directory to avoid .git from other tests
        import tempfile
        with tempfile.TemporaryDirectory() as isolated_temp_dir:
            isolated_path = Path(isolated_temp_dir)
            git_integration = GitIntegration(str(isolated_path))
            git_integration._find_git_root = lambda: None
            git_integration._is_git_repo = None  # Reset cache
            assert git_integration.is_git_repository is False

    @patch('subprocess.run')
    def test_get_git_status(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting git status."""
        # Create .git directory to simulate git repository
        git_dir = test_data_dir / ".git"
        git_dir.mkdir(exist_ok=True)
        
        # Mock git status output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="## main\n M modified.txt\n?? untracked.txt\n A  added.txt\n"
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
        # Create .git directory to simulate git repository
        git_dir = test_data_dir / ".git"
        git_dir.mkdir(exist_ok=True)
        
        # Mock git log output in the format expected by get_git_log (pipe-separated)
        mock_log_output = """abc123|Test User <test@example.com>|2024-01-01 12:00:00 +0000|Initial commit
def456|Test User <test@example.com>|2024-01-01 11:00:00 +0000|Second commit"""
        
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

    @pytest.mark.asyncio
    @patch('asyncio.create_subprocess_exec')
    async def test_get_file_history(self, mock_subprocess: MagicMock, test_data_dir: Path):
        """Test getting file history."""
        # Create .git directory to simulate git repository
        git_dir = test_data_dir / ".git"
        git_dir.mkdir(exist_ok=True)
        
        # Create the file to ensure relative path calculation works
        readme_file = test_data_dir / "README.md"
        readme_file.write_text("# Test README")
        
        # Mock git log output for specific file (format: %H|%an|%ae|%ad|%s)
        mock_log_output = """abc123|Test User|test@example.com|2024-01-01 12:00:00 +0000|Update README.md
def456|Test User|test@example.com|2024-01-01 11:00:00 +0000|Add README.md"""
        
        # Mock async subprocess with proper async mock
        from unittest.mock import AsyncMock
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (mock_log_output.encode(), b'')
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process
        
        git_integration = GitIntegration(str(test_data_dir))
        history = await git_integration.get_file_history(readme_file)
        
        assert isinstance(history, list)
        assert len(history) == 2
        assert history[0]["hash"] == "abc123"
        assert history[0]["message"] == "Update README.md"
        assert history[1]["hash"] == "def456"
        assert history[1]["message"] == "Add README.md"

    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_get_file_history_no_history(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting file history for file with no history."""
        # Mock empty git log
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )
        
        git_integration = GitIntegration(str(test_data_dir))
        history = await git_integration.get_file_history(Path("newfile.md"))
        
        assert isinstance(history, list)
        assert len(history) == 0

    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_get_file_history_not_git_repo(self, mock_run: MagicMock, test_data_dir: Path):
        """Test getting file history when not a git repository."""
        # Mock git command failure
        mock_run.return_value = MagicMock(returncode=128)
        
        git_integration = GitIntegration(str(test_data_dir))
        history = await git_integration.get_file_history(Path("README.md"))
        
        assert history == []

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