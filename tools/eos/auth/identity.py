"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG212 INSTITUTIONAL AUTHENTICATION - IDENTITY & TENANT SCHEMA
FILE: tools/eos/auth/identity.py
===============================================================================
Epitome:
    Defines multi-tenant sovereign identity models, machine principals, service
    accounts, and role mappings for the Wilsy OS Platform 1.0 Zero Trust architecture.

Biblical Worth Billions:
    "Let all things be done decently and in order."
    — 1 Corinthians 14:40

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/auth/identity.py
===============================================================================
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from tools.eos.auth.principal_status import PrincipalStatus


class SovereignIdentity(BaseModel):
    """Authenticated projection, never a source of lifecycle authority."""
    identity_id: str = Field(..., description="Resolved principal identifier")
    tenant_id: str = Field(..., description="Verified request tenant context; membership is unresolved projection debt")
    username: Optional[str] = Field(None, description="Non-authoritative verified display metadata")
    email: Optional[str] = Field(None, description="Non-authoritative verified contact metadata")
    roles: List[str] = Field(default_factory=list, description="Projection of signed/legacy role claims; not governed assignment")
    permissions: List[str] = Field(default_factory=list, description="Projection of signed/legacy permissions; not lifecycle authority")
    auth_method: str = Field(..., description="Authentication mechanism used")
    status: PrincipalStatus = Field(..., description="Current status copied from durable PrincipalAuthority")
