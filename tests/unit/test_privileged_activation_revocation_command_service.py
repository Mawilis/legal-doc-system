"""
WILSY OS P6 privileged-activation supervisory revocation unit certificate.

VERSION:
    v1.0.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-UNIT

AUTHORITY:
    Test-only certificate for the frozen P6 explicit supervisory revocation
    contract. This artifact grants no runtime authority.

EPITOME:
    Define the fail-closed contract for revoking one exact current privileged
    activation only when a distinct supervising principal possesses the current
    SYSTEM permission ``privileged_activation:revoke``.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/
    test_privileged_activation_revocation_command_service.py

CERTIFICATION DATE:
    2026-10-15

CHANGELOG:
    v1.0.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-UNIT
        Initial RED certificate for P6 supervisory revocation.

SECURITY / PRIVACY POSTURE:
    Uses opaque identifiers and reason references only. Raw review narrative,
    credentials, tokens and financial data are excluded.

TENANT BOUNDARY:
    Exact activation target scope must remain PLATFORM_SYSTEM or the exact
    tenant scope already bound to the activation. Cross-scope rebinding fails
    closed.

AUTHORITY BOUNDARY:
    Test contract only. No activation issuance, permission assignment, role
    assignment, eligibility creation, assurance creation, break-glass, HTTP,
    subscription or financial authority.

FINANCIAL AUTHORITY BOUNDARY:
    NONE.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tools.eos.auth.privileged_activation_revocation_command_evidence import (
    PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
    PrivilegedActivationRevocationCommandEvidence,
    PrivilegedActivationRevocationCommandEvidenceError,
)
from tools.eos.auth.privileged_activation_revocation_command_service import (
    PrivilegedActivationRevocationCommandError,
    PrivilegedActivationRevocationCommandService,
)


NOW = datetime(2026, 10, 15, 6, 30, tzinfo=timezone.utc)

ACTOR = "principal-supervisor-p6"
TARGET = "principal-target-p6"
ACTIVATION_ID = "activation-p6"
ASSIGNMENT_ID = "system-permission-assignment-p6"
ASSIGNMENT_REVISION = 7
ASSIGNMENT_FINGERPRINT = "a" * 128
REASON_REFERENCE = "revocation-reason:p6:security-review"
IDEMPOTENCY_KEY = "p6-revoke-command-1"


def _evidence(
    *,
    actor_principal_id: str = ACTOR,
    target_principal_id: str = TARGET,
    target_activation_id: str = ACTIVATION_ID,
    target_class: str = "PLATFORM_SYSTEM_ROOT",
    target_tenant_id: str | None = None,
    reason_reference: str = REASON_REFERENCE,
    idempotency_key: str = IDEMPOTENCY_KEY,
) -> PrivilegedActivationRevocationCommandEvidence:
    """Build one canonical P6 command-evidence value."""

    return PrivilegedActivationRevocationCommandEvidence.compose(
        actor_principal_id=actor_principal_id,
        actor_permission_id=PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
        actor_permission_assignment_id=ASSIGNMENT_ID,
        actor_permission_assignment_revision=ASSIGNMENT_REVISION,
        actor_permission_assignment_fingerprint=ASSIGNMENT_FINGERPRINT,
        target_activation_id=target_activation_id,
        target_principal_id=target_principal_id,
        target_class=target_class,
        target_tenant_id=target_tenant_id,
        revocation_reason_reference=reason_reference,
        authorized_at=NOW,
        idempotency_key=idempotency_key,
    )


def test_permission_constant_is_exact_and_narrow() -> None:
    """P6 must introduce one exact revoke permission, never an alias."""

    assert (
        PRIVILEGED_ACTIVATION_REVOKE_PERMISSION
        == "privileged_activation:revoke"
    )


def test_command_evidence_is_deterministic() -> None:
    """Equivalent command semantics must produce exact evidence identity."""

    left = _evidence()
    right = _evidence()

    assert left == right
    assert left.fingerprint == right.fingerprint
    assert (
        left.revocation_command_evidence_id
        == right.revocation_command_evidence_id
    )
    assert len(left.fingerprint) == 128


def test_command_evidence_binds_current_permission_lineage() -> None:
    """Evidence must bind the exact supervisory permission assignment lineage."""

    value = _evidence()

    assert value.actor_principal_id == ACTOR
    assert (
        value.actor_permission_id
        == "privileged_activation:revoke"
    )
    assert value.actor_permission_assignment_id == ASSIGNMENT_ID
    assert (
        value.actor_permission_assignment_revision
        == ASSIGNMENT_REVISION
    )
    assert (
        value.actor_permission_assignment_fingerprint
        == ASSIGNMENT_FINGERPRINT
    )


def test_command_evidence_binds_exact_target_scope() -> None:
    """Evidence must bind one activation, target principal and target scope."""

    value = _evidence()

    assert value.target_activation_id == ACTIVATION_ID
    assert value.target_principal_id == TARGET
    assert value.target_class == "PLATFORM_SYSTEM_ROOT"
    assert value.target_tenant_id is None


def test_command_evidence_binds_reason_time_and_idempotency() -> None:
    """Durable evidence must preserve opaque reason, time and replay identity."""

    value = _evidence()

    assert value.revocation_reason_reference == REASON_REFERENCE
    assert value.authorized_at == NOW
    assert value.idempotency_key == IDEMPOTENCY_KEY


@pytest.mark.parametrize(
    "replacement",
    ("", " ", "\n"),
)
def test_raw_empty_reason_reference_fails_closed(
    replacement: str,
) -> None:
    """P6 must reject absent or whitespace-only reason references."""

    with pytest.raises(
        PrivilegedActivationRevocationCommandEvidenceError,
    ):
        _evidence(
            reason_reference=replacement,
        )


def test_actor_and_target_are_distinct() -> None:
    """Supervisory P6 revocation must not silently become self-revocation."""

    with pytest.raises(
        PrivilegedActivationRevocationCommandEvidenceError,
    ):
        _evidence(
            target_principal_id=ACTOR,
        )


def test_platform_scope_cannot_carry_tenant_id() -> None:
    """PLATFORM_SYSTEM_ROOT evidence must never be rebound to tenant scope."""

    with pytest.raises(
        PrivilegedActivationRevocationCommandEvidenceError,
    ):
        _evidence(
            target_class="PLATFORM_SYSTEM_ROOT",
            target_tenant_id="tenant-forbidden",
        )


def test_tenant_scope_requires_concrete_tenant() -> None:
    """Tenant-privileged evidence requires its exact concrete tenant."""

    with pytest.raises(
        PrivilegedActivationRevocationCommandEvidenceError,
    ):
        _evidence(
            target_class="TENANT_PRIVILEGED",
            target_tenant_id=None,
        )


def test_service_surface_is_supervisory_revocation_only() -> None:
    """P6 service must expose revocation without authority-expanding commands."""

    public = {
        name
        for name in dir(
            PrivilegedActivationRevocationCommandService
        )
        if not name.startswith("_")
    }

    assert "revoke" in public

    forbidden = {
        "issue",
        "activate",
        "assign_role",
        "assign_permission",
        "break_glass",
        "execute_payment",
        "release_payment",
        "settle_payment",
    }

    assert public.isdisjoint(forbidden)


def test_command_error_is_explicit_institutional_boundary() -> None:
    """The command plane must expose a dedicated fail-closed error type."""

    assert issubclass(
        PrivilegedActivationRevocationCommandError,
        Exception,
    )


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_privileged_activation_revocation_command_service.py
# VERSION: v1.0.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-UNIT
# AUTHORITY BOUNDARY: P6 TEST CONTRACT ONLY; NO RUNTIME AUTHORITY
# TENANT POSTURE: EXACT ACTIVATION SCOPE; CROSS-SCOPE REBINDING FORBIDDEN
# FAIL-CLOSED POSTURE: EXPLICIT ERRORS; NO ALIAS OR IMPLIED AUTHORITY
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
