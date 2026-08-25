"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Policy Loader - Institutional Policy Ingestion & Parsing (FG165).
    Loads policy rulebooks from files or registries for Wilsy OS engines.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.
===============================================================================
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Union

logger = logging.getLogger("WilsyOS.PolicyLoader")


class PolicyLoader:
    """Institutional policy loading and parsing utility."""

    @staticmethod
    def load_policy(policy_source: Union[str, Path]) -> Dict[str, Any]:
        """
        Loads policy rules from a file path or returns default governance rules.
        """
        source_str = str(policy_source)
        if source_str == "default_governance":
            return {
                "policy_id": "default_governance",
                "rules": {
                    "max_file_size_bytes": 1024 * 1024,
                    "max_complexity": 15,
                    "required_markers": ["Epitome:", "Collaboration & Maintenance"]
                }
            }
        
        path = Path(policy_source)
        if path.is_file():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Loaded policy from file: {path}")
                return data
        
        raise FileNotFoundError(f"Policy source not found: {policy_source}")
