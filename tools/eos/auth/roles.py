"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG212 INSTITUTIONAL AUTHENTICATION - ROLES & HIERARCHY
FILE: tools/eos/auth/roles.py
===============================================================================
Epitome:
    Defines sovereign institutional roles and permission matrices for Wilsy OS
    Platform 1.0 access control.

Biblical Worth Billions:
    "Where no counsel is, the people fall: but in the multitude of counsellors there is safety."
    — Proverbs 11:14

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/auth/roles.py
===============================================================================
"""

from typing import Dict, List

ROLE_PERMISSIONS_MAP: Dict[str, List[str]] = {
    "SOVEREIGN_ARCHITECT": [
        "kernel:read", "kernel:write", "execution:trigger", 
        "governance:evaluate", "artifacts:read", "admin:all"
    ],
    "ENTERPRISE_ADMIN": [
        "kernel:read", "execution:trigger", "governance:evaluate", 
        "artifacts:read", "tenant:manage"
    ],
    "AUDITOR": [
        "kernel:read", "artifacts:read", "governance:read", "audit:read"
    ],
    "SERVICE_WORKER": [
        "execution:trigger", "artifacts:write", "events:publish"
    ]
}


def get_permissions_for_roles(roles: List[str]) -> List[str]:
    """Aggregates all unique permissions granted across a list of roles."""
    permissions = set()
    for role in roles:
        role_perms = ROLE_PERMISSIONS_MAP.get(role, [])
        permissions.update(role_perms)
    return list(permissions)
