"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG212 INSTITUTIONAL AUTHENTICATION - AUTHORIZATION DEPENDENCIES
FILE: tools/eos/auth/authorization.py
===============================================================================
Epitome:
    Role and permission enforcement factories for securing FastAPI endpoints
    against unauthorized institutional access.

Biblical Worth Billions:
    "Better is a little with righteousness than great revenues without right."
    — Proverbs 16:8

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/auth/authorization.py
===============================================================================
"""

from typing import List
from fastapi import Depends
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.authentication import get_current_identity
from tools.eos.auth.permissions import has_permission
from tools.eos.api.exceptions import ForbiddenOperationException


class RequirePermission:
    """Dependency callable that verifies if the current identity possesses a required permission."""
    def __init__(self, permission: str):
        self.permission = permission

    async def __call__(self, identity: SovereignIdentity = Depends(get_current_identity)) -> SovereignIdentity:
        if not has_permission(identity.roles, self.permission):
            raise ForbiddenOperationException(f"Identity '{identity.username}' lacks required permission: '{self.permission}'.")
        return identity


class RequireRole:
    """Dependency callable that verifies if the current identity holds one of the required roles."""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, identity: SovereignIdentity = Depends(get_current_identity)) -> SovereignIdentity:
        if "SOVEREIGN_ARCHITECT" in identity.roles:
            return identity
        if not any(role in identity.roles for role in self.allowed_roles):
            raise ForbiddenOperationException(f"Identity '{identity.username}' lacks required role access.")
        return identity
