# -*- coding: utf-8 -*-
"""Immutable forward-canonical snapshot of principal lifecycle authority.

TITLE: WILSY OS Principal Authority Snapshot
VERSION: v1.0.0-WILSY-PRINCIPAL-AUTHORITY
AUTHORITY: Immutable principal identifier, PrincipalStatus, and lifecycle revision snapshot.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/principal_authority.py
CERTIFICATION/UPDATE DATE: 2026-08-29
CHANGELOG: v1.0.0 establishes the minimal immutable authority snapshot without persistence or resolution.
COMPLIANCE: Strict typed value object; no default authority, generated IDs, I/O, or mutation.
SECURITY/PRIVACY POSTURE: Rejects malformed identifiers, unknown status values, and invalid revisions.
TENANT BOUNDARY: No tenant identity, membership, role, or authorization is represented.
AUTHORITY BOUNDARY: Owns only principal_id, current PrincipalStatus, and lifecycle revision; it does not decide transitions or persist state.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial execution authority.

Epitome:
    A hashable immutable snapshot that carries only the minimum proven identity
    and lifecycle authority needed by a future resolver or repository.

Biblical Anchor:
    "And he shall be like a tree planted by the rivers of water..." — Psalm 1:3

Collaboration & Ownership:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    AI Collaborator: Core Systems Engineering Agent
    File Path: tools/eos/auth/principal_authority.py
"""
from __future__ import annotations

from dataclasses import dataclass

from tools.eos.auth.principal_status import PrincipalStatus


@dataclass(frozen=True, slots=True)
class PrincipalAuthority:
    """Immutable principal lifecycle authority snapshot.

    The record owns no transition permission, persistence, authentication,
    authorization, tenant, role, credential, kind, kernel, or financial data.
    """

    principal_id: str
    status: PrincipalStatus
    revision: int

    def __post_init__(self) -> None:
        """Reject malformed values without normalizing or inventing authority."""
        if not isinstance(self.principal_id, str) or not self.principal_id:
            raise ValueError("principal_id must be a non-empty string")
        if self.principal_id != self.principal_id.strip():
            raise ValueError("principal_id must not contain leading or trailing whitespace")
        if not isinstance(self.status, PrincipalStatus):
            raise TypeError("status must be a PrincipalStatus")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int):
            raise TypeError("revision must be a non-negative integer")
        if self.revision < 0:
            raise ValueError("revision must be a non-negative integer")


__all__ = ["PrincipalAuthority"]

# ARTIFACT: principal_authority.py
# VERSION: v1.0.0-WILSY-PRINCIPAL-AUTHORITY
# AUTHORITY BOUNDARY: immutable principal_id/status/revision snapshot only
# TENANT POSTURE: no tenant ownership or membership
# FAIL-CLOSED POSTURE: malformed identity, status, and revision are rejected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
