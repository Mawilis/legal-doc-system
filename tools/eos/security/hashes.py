"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Hashes - Provides high-performance cryptographic hashing utilities (SHA-256, SHA-512).

Biblical Scale & Architecture:
    Production-ready cryptographic utility module. Zero child's place.
    Offers bulletproof hashing functions for secure checksum generation and data verification.

Collaboration & Maintenance:
    - [Architecture]: Cryptographic hashing algorithms and digest wrappers.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import hashlib


class HashUtility:
    """
    High-performance cryptographic hashing utility.
    """

    @staticmethod
    def compute_sha256(data: str | bytes) -> str:
        """
        Computes the SHA-256 cryptographic digest of input data.

        Args:
            data (str | bytes): Input data.

        Returns:
            str: Hexadecimal SHA-256 digest string.
        """
        if isinstance(data, str):
            data_bytes = data.encode("utf-8")
        else:
            data_bytes = data

        return hashlib.sha256(data_bytes).hexdigest()

    @staticmethod
    def compute_sha512(data: str | bytes) -> str:
        """
        Computes the SHA-512 cryptographic digest of input data.

        Args:
            data (str | bytes): Input data.

        Returns:
            str: Hexadecimal SHA-512 digest string.
        """
        if isinstance(data, str):
            data_bytes = data.encode("utf-8")
        else:
            data_bytes = data

        return hashlib.sha512(data_bytes).hexdigest()
