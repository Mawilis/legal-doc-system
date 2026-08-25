"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Cache Keys - Institutional Deterministic Key Generator (FG164).
    Standardizes cryptographic and structured cache key generation for repository scans,
    AI inferences, quality reports, and engine artifacts across Wilsy OS.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional key structures. Orderly identification and retrieval.
    Proverbs 21:5 - "The plans of the diligent lead surely to abundance..."

Collaboration & Maintenance:
    - [Architecture]: Deterministic hashing and namespace-based cache key generation.
    - [Compliance]: Collision-resistant key formatting for cross-engine caching.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("WilsyOS.CacheKeys")


class CacheKeys:
    """
    Institutional cache key builder providing deterministic, namespaced,
    and hashed keys for cross-engine caching.
    """

    @staticmethod
    # [FUNCTION EXPLANATION]: Generates a deterministic hash from arbitrary input parameters or file contents.
    def compute_hash(data: Any) -> str:
        """
        Computes a secure SHA-256 hash for complex data structures or strings.

        Args:
            data (Any): Input data (dict, string, list) to hash.

        Returns:
            str: Hexadecimal SHA-256 digest string.
        """
        if isinstance(data, (dict, list)):
            serialized = json.dumps(data, sort_keys=True, default=str)
        else:
            serialized = str(data)
        
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    # [FUNCTION EXPLANATION]: Builds a namespaced cache key for repository scan operations.
    def repository_scan_key(cls, repo_path: str, scan_options: Optional[Dict[str, Any]] = None) -> str:
        """Generates a unique cache key for a repository scan."""
        options_hash = cls.compute_hash(scan_options or {})
        return f"eos:cache:repo:scan:{cls.compute_hash(repo_path)}:{options_hash}"

    @classmethod
    # [FUNCTION EXPLANATION]: Builds a namespaced cache key for AI model inferences.
    def ai_inference_key(cls, model_name: str, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generates a unique cache key for AI generation or analysis results."""
        param_hash = cls.compute_hash(parameters or {})
        prompt_hash = cls.compute_hash(prompt)
        return f"eos:cache:ai:{model_name}:{prompt_hash}:{param_hash}"

    @classmethod
    # [FUNCTION EXPLANATION]: Builds a namespaced cache key for engine quality and lint audits.
    def quality_audit_key(cls, target_id: str, ruleset_version: str) -> str:
        """Generates a unique cache key for quality audits and lint compliance checks."""
        return f"eos:cache:quality:{target_id}:{ruleset_version}"

    @classmethod
    # [FUNCTION EXPLANATION]: Builds a general-purpose namespaced cache key.
    def custom_key(cls, namespace: str, identifier: str, qualifiers: Optional[Dict[str, Any]] = None) -> str:
        """Generates a custom namespaced cache key with optional qualifiers."""
        qual_hash = cls.compute_hash(qualifiers or {})
        return f"eos:cache:{namespace}:{identifier}:{qual_hash}"
