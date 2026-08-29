# -*- coding: utf-8 -*-
"""Pure forward-canonical policy for ordinary principal lifecycle transitions.

TITLE: WILSY OS Principal Lifecycle Policy
VERSION: v1.0.0-WILSY-PRINCIPAL-LIFECYCLE-POLICY
AUTHORITY: Ordinary transition admissibility for the frozen PrincipalStatus vocabulary.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/principal_lifecycle_policy.py
CERTIFICATION/UPDATE DATE: 2026-08-29
CHANGELOG: v1.0.0 establishes explicit ACTIVE/SUSPENDED transitions and ordinary REVOKED terminality.
COMPLIANCE: Pure, deterministic, stateless policy; no persistence, I/O, or operational enforcement claim.
SECURITY/PRIVACY POSTURE: Typed fail-closed transition checks; no credentials or personal data.
TENANT BOUNDARY: This policy does not own tenant identity, membership, roles, or tenant authorization.
AUTHORITY BOUNDARY: This policy decides only whether two resolved PrincipalStatus values form an allowed ordinary transition.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial execution authority.

Epitome:
    A bounded transition predicate that makes the forward-canonical ordinary
    lifecycle contract explicit while leaving storage and enforcement upstream.

Biblical Anchor:
    "And he shall be like a tree planted by the rivers of water..." — Psalm 1:3

Collaboration & Ownership:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    AI Collaborator: Core Systems Engineering Agent
    File Path: tools/eos/auth/principal_lifecycle_policy.py
"""
from __future__ import annotations

from typing import Final

from tools.eos.auth.principal_status import PrincipalStatus


class PrincipalLifecycleTransitionError(ValueError):
    """Raised when a non-admissible ordinary PrincipalStatus transition is requested."""


_ALLOWED_TRANSITIONS: Final[frozenset[tuple[PrincipalStatus, PrincipalStatus]]] = frozenset(
    {
        (PrincipalStatus.ACTIVE, PrincipalStatus.SUSPENDED),
        (PrincipalStatus.ACTIVE, PrincipalStatus.REVOKED),
        (PrincipalStatus.SUSPENDED, PrincipalStatus.ACTIVE),
        (PrincipalStatus.SUSPENDED, PrincipalStatus.REVOKED),
    }
)


def can_transition(current: PrincipalStatus, target: PrincipalStatus) -> bool:
    """Return whether ``current`` may ordinarily transition to ``target``.

    This pure predicate owns no transition mutation, persistence, tenant,
    credential, role, authentication, kernel, or financial semantics.
    """
    if not isinstance(current, PrincipalStatus) or not isinstance(target, PrincipalStatus):
        return False
    return (current, target) in _ALLOWED_TRANSITIONS


def require_transition(current: PrincipalStatus, target: PrincipalStatus) -> None:
    """Raise a narrow domain error unless an ordinary transition is allowed."""
    if not can_transition(current, target):
        raise PrincipalLifecycleTransitionError(
            f"Ordinary principal lifecycle transition is forbidden: {current!s} -> {target!s}"
        )


__all__ = ["PrincipalLifecycleTransitionError", "can_transition", "require_transition"]

# ARTIFACT: principal_lifecycle_policy.py
# VERSION: v1.0.0-WILSY-PRINCIPAL-LIFECYCLE-POLICY
# AUTHORITY BOUNDARY: ordinary PrincipalStatus transition admissibility only
# TENANT POSTURE: no tenant ownership or authorization
# FAIL-CLOSED POSTURE: unknown or self transitions are rejected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
