"""
Wilsy Engineering Kernel

Kernel Foundation Services

Filesystem Service

Read-only repository filesystem operations.
"""

from __future__ import annotations

from pathlib import Path


class FilesystemService:
    """
    Read-only filesystem service for the Engineering Kernel.

    This service shall never modify repository artifacts.
    """

    def read_text(
        self,
        path: Path,
    ) -> str:
        """
        Read a UTF-8 text file.
        """

        return path.read_text(encoding="utf-8")

    def exists(
        self,
        path: Path,
    ) -> bool:
        """
        Determine whether a repository object exists.
        """

        return path.exists()

    def is_file(
        self,
        path: Path,
    ) -> bool:
        """
        Determine whether a repository object is a file.
        """

        return path.is_file()

    def is_directory(
        self,
        path: Path,
    ) -> bool:
        """
        Determine whether a repository object is a directory.
        """

        return path.is_dir()

    def list_directory(
        self,
        path: Path,
    ) -> list[Path]:
        """
        List directory contents.

        Returns an empty list if the directory does not exist.
        """

        if not path.exists():
            return []

        return sorted(path.iterdir())
