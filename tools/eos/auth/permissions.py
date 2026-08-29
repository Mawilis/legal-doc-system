"""TITLE: WILSY OS Permission Policy Evaluator.
VERSION: v1.0.0-WILSY-PERMISSION-POLICY
AUTHORITY: Pure deterministic Python evaluation of exact explicit permission grants from governed role definitions only.
EPITOME: Evaluates exact permission membership across governed role definitions without establishing current role possession or final authorization.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/permissions.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-29.
CHANGELOG: v1.0.0-WILSY-PERMISSION-POLICY removes legacy SOVEREIGN_ARCHITECT and admin:all bypass semantics and establishes exact explicit permission policy evaluation only.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Pure policy evaluator; no credentials, principal profiles, tenant records, persistence, secrets, or runtime IO.
TENANT BOUNDARY: Tenant-agnostic policy evaluation only; current tenant-scoped role possession remains governed by RoleAssignmentAuthority.
AUTHORITY BOUNDARY: Owns exact permission-policy evaluation over role definitions only; does not own role possession, principal status, membership, authentication, authorization decisions, or financial execution.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""
from __future__ import annotations
from typing import List
from tools.eos.auth.roles import get_permissions_for_roles

VERSION = "v1.0.0-WILSY-PERMISSION-POLICY"

def has_permission(user_roles: List[str], required_permission: str) -> bool:
    """Evaluate one exact permission for candidate defined roles; never authorize possession."""
    if not isinstance(user_roles, list) or not isinstance(required_permission, str) or not required_permission:
        return False
    return required_permission in get_permissions_for_roles(user_roles)

__all__ = ["VERSION", "has_permission"]

# ARTIFACT: permissions.py
# VERSION: v1.0.0-WILSY-PERMISSION-POLICY
# AUTHORITY BOUNDARY: exact deterministic permission-policy evaluation over governed role definitions only
# TENANT POSTURE: tenant-agnostic policy only; current tenant-scoped possession requires governed RoleAssignmentAuthority
# FAIL-CLOSED POSTURE: unknown, malformed, implicit, wildcard, and non-explicit permissions never grant authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
