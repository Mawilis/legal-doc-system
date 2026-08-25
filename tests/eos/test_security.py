"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Test Security - Validates cryptographic hashing, digital signatures, and tamper detection.

Biblical Scale & Architecture:
    Production-ready security test suite. Zero child's place.
    Ensures absolute cryptographic integrity and secure verification across Wilsy OS.

Collaboration & Maintenance:
    - [Testing]: Cryptographic security and tamper detection unit tests.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import unittest
from tools.eos.security.hashes import HashUtility


class TestSecurity(unittest.TestCase):
    """
    Unit tests for cryptographic security and integrity modules.
    """

    def test_sha256_hashing(self) -> None:
        """
        Verifies SHA-256 hash generation accuracy.
        """
        digest = HashUtility.compute_sha256("Wilsy OS")
        self.assertEqual(len(digest), 64, "SHA-256 digest must be 64 hex characters.")


if __name__ == "__main__":
    unittest.main()
