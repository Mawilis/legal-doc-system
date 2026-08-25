"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Artifact Checksum Engine (FG168).
    Generates and verifies cryptographic digests for files, byte buffers, and
    text payloads across the Wilsy OS artifact ecosystem.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready cryptographic hash utility. Zero child's place.
    Proverbs 11:1 - "A false balance is abomination to the Lord: but a just weight is his delight."
    Leviticus 19:36 - "Just balances, just weights... shall ye have."

Collaboration & Maintenance:
    - [Security]: Constant-time digest comparisons via hmac.compare_digest to prevent timing attacks.
    - [Performance]: High-throughput 64KB chunked I/O stream processing for large binary payloads.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from pathlib import Path
from typing import Union

logger = logging.getLogger("WilsyOS.ArtifactChecksum")


class ArtifactChecksum:
    """
    Cryptographic digest calculation and verification utility for artifacts.
    Supports file paths, binary payloads, and text buffers with timing-attack safe validation.
    """

    # [FUNCTION EXPLANATION]: Computes cryptographic hash digest for a file on disk using buffered chunking.
    @staticmethod
    def compute_file_checksum(
        file_path: Union[Path, str], 
        algorithm: str = "sha256", 
        chunk_size: int = 65536
    ) -> str:
        """
        Computes the cryptographic checksum of a physical file on disk.

        Args:
            file_path (Union[Path, str]): Path to target file on disk.
            algorithm (str): Hashing algorithm (default "sha256").
            chunk_size (int): Buffer read size in bytes (default 64KB).

        Returns:
            str: Hexadecimal hash digest string.

        Raises:
            FileNotFoundError: If the target file path does not exist.
            ValueError: If an unsupported hashing algorithm is specified.
        """
        target = Path(file_path).resolve()
        if not target.is_file():
            raise FileNotFoundError(f"Artifact checksum failed: File not found at '{target}'")

        try:
            hasher = hashlib.new(algorithm)
        except ValueError as e:
            raise ValueError(f"Unsupported checksum algorithm '{algorithm}': {e}") from e

        with open(target, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)

        digest = hasher.hexdigest()
        logger.debug(f"Computed [{algorithm}] digest for file [{target.name}]: {digest[:12]}...")
        return digest

    # [FUNCTION EXPLANATION]: Backward-compatible alias for file checksum calculation.
    @staticmethod
    def compute_checksum(file_path: Union[Path, str], algorithm: str = "sha256") -> str:
        """
        Legacy wrapper method maintaining backward compatibility for file checksum calculation.
        """
        return ArtifactChecksum.compute_file_checksum(file_path, algorithm=algorithm)

    # [FUNCTION EXPLANATION]: Computes cryptographic digest directly for in-memory binary payloads.
    @staticmethod
    def compute_bytes_checksum(data: bytes, algorithm: str = "sha256") -> str:
        """
        Computes cryptographic checksum for an in-memory byte buffer.

        Args:
            data (bytes): Raw binary data buffer.
            algorithm (str): Hashing algorithm (default "sha256").

        Returns:
            str: Hexadecimal hash digest string.
        """
        try:
            hasher = hashlib.new(algorithm)
        except ValueError as e:
            raise ValueError(f"Unsupported checksum algorithm '{algorithm}': {e}") from e

        hasher.update(data)
        return hasher.hexdigest()

    # [FUNCTION EXPLANATION]: Computes cryptographic digest directly for text payloads.
    @staticmethod
    def compute_string_checksum(text: str, encoding: str = "utf-8", algorithm: str = "sha256") -> str:
        """
        Computes cryptographic checksum for a text string.

        Args:
            text (str): Input text string.
            encoding (str): Text encoding scheme (default "utf-8").
            algorithm (str): Hashing algorithm (default "sha256").

        Returns:
            str: Hexadecimal hash digest string.
        """
        return ArtifactChecksum.compute_bytes_checksum(text.encode(encoding), algorithm=algorithm)

    # [FUNCTION EXPLANATION]: Performs timing-attack resilient checksum verification against expected digest.
    @staticmethod
    def verify_checksum(
        file_path: Union[Path, str], 
        expected_checksum: str, 
        algorithm: str = "sha256"
    ) -> bool:
        """
        Verifies that a file's computed checksum matches an expected hash string.
        Uses constant-time comparison to protect against timing side-channel attacks.

        Args:
            file_path (Union[Path, str]): Path to target file on disk.
            expected_checksum (str): Target checksum to compare against.
            algorithm (str): Hashing algorithm used (default "sha256").

        Returns:
            bool: True if checksums match exactly, False otherwise.
        """
        actual_checksum = ArtifactChecksum.compute_file_checksum(file_path, algorithm=algorithm)
        return hmac.compare_digest(actual_checksum.lower(), expected_checksum.lower())

    # [FUNCTION EXPLANATION]: Verifies in-memory byte buffer against expected digest.
    @staticmethod
    def verify_bytes_checksum(
        data: bytes, 
        expected_checksum: str, 
        algorithm: str = "sha256"
    ) -> bool:
        """
        Verifies an in-memory byte buffer against an expected hash string.

        Args:
            data (bytes): Raw binary buffer.
            expected_checksum (str): Target checksum to compare against.
            algorithm (str): Hashing algorithm used (default "sha256").

        Returns:
            bool: True if checksums match exactly, False otherwise.
        """
        actual_checksum = ArtifactChecksum.compute_bytes_checksum(data, algorithm=algorithm)
        return hmac.compare_digest(actual_checksum.lower(), expected_checksum.lower())
