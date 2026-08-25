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


class SovereignIdentity(BaseModel):
    identity_id: str = Field(..., description="Unique sovereign identity or user UUID")
    tenant_id: str = Field(..., description="Multi-tenant namespace isolation identifier")
    username: str = Field(..., description="Principal username or service account name")
    email: Optional[str] = Field(None, description="Principal contact email")
    roles: List[str] = Field(default_factory=list, description="Assigned institutional roles (e.g., ADMIN, ARCHITECT, AUDITOR)")
    permissions: List[str] = Field(default_factory=list, description="Fine-grained capability permissions")
    is_service_account: bool = Field(False, description="Indicates whether principal is a machine/service identity")
    auth_method: str = Field(..., description="Authentication mechanism used (JWT, API_KEY, MACHINE_MTLS)")
    status: str = Field("ACTIVE", description="Identity lifecycle status")
