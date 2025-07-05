"""
VeriDoc Security Layer
Path validation and access control
"""

import os
from pathlib import Path
from typing import Union

class SecurityManager:
    """Manages file system security and path validation"""

    def __init__(self, base_path: Union[str, Path]):
        self.base_path = Path(base_path).resolve()

        # Ensure base path exists
        if not self.base_path.exists():
            raise ValueError(f"Base path does not exist: {self.base_path}")

        if not self.base_path.is_dir():
            raise ValueError(f"Base path is not a directory: {self.base_path}")
    
    def validate_path(self, user_path: str) -> Path:
        """
        Validate that user path is safe and within base path.

        Args:
            user_path: User-provided path (relative to base)

        Returns:
            Resolved safe path

        Raises:
            ValueError: If path is invalid or outside base path
            SecurityError: If path traversal attempt detected
        """
        # Remove leading slashes and normalize
        user_path = user_path.strip("/")

        # Check for null bytes
        if "\x00" in user_path:
            raise ValueError("Null bytes not allowed in path")

        # Construct full path
        try:
            if user_path == "" or user_path == ".":
                full_path = self.base_path
            else:
                full_path = (self.base_path / user_path).resolve()
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid path: {e}")

        # Check if resolved path is within base path
        try:
            full_path.relative_to(self.base_path)
        except ValueError:
            raise ValueError("Path outside base directory")

        # Check for symbolic links (security risk)
        if full_path.is_symlink():
            # Check if symlink target is within base path
            try:
                target = full_path.readlink()
                if target.is_absolute():
                    raise ValueError("Absolute symbolic links not allowed")

                resolved_target = (full_path.parent / target).resolve()
                resolved_target.relative_to(self.base_path)
            except (ValueError, OSError):
                raise ValueError("Symbolic link points outside base directory")

        return full_path
    
    def sanitize_input(self, user_input: str) -> str:
        """
        Sanitize user input for safe processing.

        Args:
            user_input: Raw user input

        Returns:
            Sanitized input
        """
        if not isinstance(user_input, str):
            raise ValueError("Input must be a string")

        # Remove null bytes
        sanitized = user_input.replace("\x00", "")

        # Limit length
        if len(sanitized) > 1000:
            raise ValueError("Input too long")

        return sanitized
    
    def is_safe_filename(self, filename: str) -> bool:
        """
        Check if filename is safe.

        Args:
            filename: Filename to check

        Returns:
            True if filename is safe
        """
        # Check for dangerous characters
        dangerous_chars = ["<", ">", ":", '"', "|", "?", "*", "\x00"]

        for char in dangerous_chars:
            if char in filename:
                return False

        # Check for reserved names (Windows)
        reserved_names = [
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
        ]

        if filename.upper() in reserved_names:
            return False

        return True