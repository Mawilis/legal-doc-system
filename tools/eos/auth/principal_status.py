# -*- coding: utf-8 -*-
"""Canonical closed status vocabulary for principal lifecycle authority.

TITLE: WILSY OS Principal Status Domain Contract
VERSION: v1.0.1-WILSY-PRINCIPAL-STATUS
AUTHORITY: principal status identity and deterministic serialization only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/principal_status.py
CERTIFICATION/UPDATE DATE: 2026-08-29
CHANGELOG: v1.0.1 structurally certifies governance boundaries without changing runtime semantics; v1.0.0 established the three-value vocabulary.
COMPLIANCE: Closed, immutable, deterministic status vocabulary only; no operational revocation or authentication enforcement claim.
SECURITY/PRIVACY POSTURE: Unknown values fail closed; no credentials, personal-data persistence, tenant lookup, or authentication authority.
TENANT BOUNDARY: PrincipalStatus does not own, derive, validate, or mutate tenant identity, tenant membership, or cross-tenant authorization.
AUTHORITY BOUNDARY: PrincipalStatus owns only the closed principal lifecycle status vocabulary; it does not own transitions, authentication, authorization, persistence, role assignment, credential validity, or revocation enforcement.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial execution authority.

Epitome:
    A small immutable vocabulary separating principal lifecycle state from
    credentials, authentication, authorization, tenant membership, and
    financial authority.

Biblical Anchor:
    "And he shall be like a tree planted by the rivers of water..." — Psalm 1:3

Collaboration & Ownership:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    AI Collaborator: Core Systems Engineering Agent
    File Path: tools/eos/auth/principal_status.py
"""
from __future__ import annotations

from enum import StrEnum

VERSION = "v1.0.0-WILSY-PRINCIPAL-STATUS"


class PrincipalStatus(StrEnum):
    """Closed principal-global lifecycle status vocabulary.

    This type owns state identity and serialization only. Lifecycle transitions
    and their authorization belong to a separate principal lifecycle authority.
    """

    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"


__all__ = ["PrincipalStatus", "VERSION"]

# ARTIFACT: principal_status.py
# VERSION: v1.0.1-WILSY-PRINCIPAL-STATUS
# END OF WILSY OS SOVEREIGN ARTIFACT
