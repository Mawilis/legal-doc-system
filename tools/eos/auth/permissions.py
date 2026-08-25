"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG212 INSTITUTIONAL AUTHENTICATION - PERMISSION EVALUATOR
FILE: tools/eos/auth/permissions.py
===============================================================================
Epitome:
    Evaluates fine-grained access permissions against user identity claims.

Biblical Worth Billions:
    "Test all things; hold fast what is good."
    — 1 Thessalonians 5:21

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/auth/permissions.py
===============================================================================
"""

from typing import List
from tools.eos.auth.roles import get_permissions_for_roles


def has_permission(user_roles: List[str], required_permission: str) -> bool:
    """Checks if the given roles grant the required sovereign permission."""
    if "SOVEREIGN_ARCHITECT" in user_roles or "admin:all" in get_permissions_for_roles(user_roles):
        return True
    granted_perms = get_permissions_for_roles(user_roles)
    return required_permission in granted_perms
