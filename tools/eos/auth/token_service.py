"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG212 INSTITUTIONAL AUTHENTICATION - TOKEN SERVICE
FILE: tools/eos/auth/token_service.py
===============================================================================
Epitome:
    High-level token lifecycle management service for generating user and service
    account authentication tokens.

Biblical Worth Billions:
    "Let your communication be, Yea, yea; Nay, nay."
    — Matthew 5:37

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/auth/token_service.py
===============================================================================
"""

from typing import Any, Dict
from tools.eos.auth.jwt_provider import create_access_token


class TokenService:
    """Manages creation and validation of sovereign auth credentials."""
    @staticmethod
    def issue_token_for_identity(identity_id: str, tenant_id: str, username: str, roles: list, is_service: bool = False) -> str:
        claims = {
            "identity_id": identity_id,
            "tenant_id": tenant_id,
            "username": username,
            "roles": roles,
            "is_service_account": is_service
        }
        return create_access_token(claims)
