"""
TITLE:
    WILSY OS System Permission Assignment Pure Domain Certificate

VERSION:
    v1.0.0-P4-R4-D5-SYSTEM-PERMISSION-ASSIGNMENT-DOMAIN-CERT

AUTHORITY:
    Wilsy OS Sovereign IAM certification only.

PURPOSE:
    Certify the pure immutable SYSTEM permission-assignment domain without
    persistence, current-principal reads, authorization composition, privileged
    activation, P5 use, break glass, or financial authority.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from inspect import getsource

import pytest

from tools.eos.auth.system_permission_assignment import (
    SystemPermissionAssignment,
    SystemPermissionAssignmentError,
    SystemPermissionAssignmentStatus,
)


NOW = datetime(
    2026,
    10,
    14,
    14,
    0,
    tzinfo=timezone.utc,
)

PERMISSION = "privileged_activation:issue"


def active(
    *,
    assignment_id: str = "assignment-opaque-a",
    principal_id: str = "principal-a",
    permission_id: str = PERMISSION,
    assigned_by_principal_id: str = "principal-grantor",
) -> SystemPermissionAssignment:
    return SystemPermissionAssignment.assign(
        assignment_id=assignment_id,
        principal_id=principal_id,
        permission_id=permission_id,
        assigned_by_principal_id=
            assigned_by_principal_id,
        assigned_at=NOW,
        assignment_evidence_reference=
            "system-permission-assignment-evidence",
    )


def test_exact_system_permission_assignment_is_immutable() -> None:
    value = active()

    assert value.assignment_id == "assignment-opaque-a"
    assert value.principal_id == "principal-a"
    assert value.permission_id == PERMISSION
    assert (
        value.status
        is SystemPermissionAssignmentStatus.ACTIVE
    )
    assert value.revision == 1
    assert value.previous_assignment_fingerprint is None
    assert value.revoked_by_principal_id is None
    assert value.revoked_at is None
    assert value.revocation_evidence_reference is None
    assert value.is_active is True
    assert len(value.assignment_fingerprint) == 128

    with pytest.raises(
        FrozenInstanceError
    ):
        value.principal_id = "principal-b"  # type: ignore[misc]


@pytest.mark.parametrize(
    "permission_id",
    (
        "legal_operations:evidence:write",
        "tenant:profile:read",
        "artifacts:read",
    ),
)
def test_non_system_permissions_are_rejected(
    permission_id: str,
) -> None:
    with pytest.raises(
        SystemPermissionAssignmentError,
        match="SYSTEM_PERMISSION_REQUIRED",
    ):
        active(
            permission_id=permission_id,
        )


@pytest.mark.parametrize(
    "permission_id",
    (
        "",
        " privileged_activation:issue",
        "privileged_activation:issue ",
        "not:a:real:permission",
    ),
)
def test_malformed_or_unknown_permission_rejects(
    permission_id: str,
) -> None:
    with pytest.raises(
        SystemPermissionAssignmentError
    ):
        active(
            permission_id=permission_id,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("assignment_id", ""),
        ("assignment_id", " assignment"),
        ("principal_id", ""),
        ("principal_id", "principal "),
        ("assigned_by_principal_id", ""),
        (
            "assigned_by_principal_id",
            " principal",
        ),
    ),
)
def test_identifier_material_rejects(
    field: str,
    value: str,
) -> None:
    kwargs = {field: value}

    with pytest.raises(
        SystemPermissionAssignmentError
    ):
        active(**kwargs)  # type: ignore[arg-type]


def test_assignment_timestamp_requires_aware_datetime() -> None:
    with pytest.raises(
        SystemPermissionAssignmentError,
        match="ASSIGNED_AT_INVALID",
    ):
        SystemPermissionAssignment.assign(
            assignment_id="assignment-a",
            principal_id="principal-a",
            permission_id=PERMISSION,
            assigned_by_principal_id="grantor-a",
            assigned_at=datetime(
                2026,
                10,
                14,
                14,
                0,
            ),
            assignment_evidence_reference="evidence",
        )


def test_assignment_evidence_reference_is_required() -> None:
    with pytest.raises(
        SystemPermissionAssignmentError,
        match="ASSIGNMENT_EVIDENCE_REFERENCE_INVALID",
    ):
        SystemPermissionAssignment.assign(
            assignment_id="assignment-a",
            principal_id="principal-a",
            permission_id=PERMISSION,
            assigned_by_principal_id="grantor-a",
            assigned_at=NOW,
            assignment_evidence_reference="",
        )


def test_revocation_is_terminal_immutable_and_chained() -> None:
    first = active()

    revoked = first.revoke(
        revoked_by_principal_id="principal-revoker",
        revoked_at=(
            NOW + timedelta(minutes=1)
        ),
        revocation_evidence_reference=
            "revocation-evidence",
    )

    assert (
        first.status
        is SystemPermissionAssignmentStatus.ACTIVE
    )
    assert first.is_active is True

    assert (
        revoked.status
        is SystemPermissionAssignmentStatus.REVOKED
    )
    assert revoked.is_active is False
    assert revoked.assignment_id == first.assignment_id
    assert revoked.principal_id == first.principal_id
    assert revoked.permission_id == first.permission_id
    assert (
        revoked.assigned_by_principal_id
        == first.assigned_by_principal_id
    )
    assert revoked.assigned_at == first.assigned_at
    assert (
        revoked.assignment_evidence_reference
        == first.assignment_evidence_reference
    )
    assert revoked.revision == 2
    assert (
        revoked.previous_assignment_fingerprint
        == first.assignment_fingerprint
    )
    assert (
        revoked.assignment_fingerprint
        != first.assignment_fingerprint
    )

    with pytest.raises(
        SystemPermissionAssignmentError,
        match="ASSIGNMENT_ALREADY_REVOKED",
    ):
        revoked.revoke(
            revoked_by_principal_id="principal-revoker",
            revoked_at=(
                NOW + timedelta(minutes=2)
            ),
            revocation_evidence_reference=
                "repeat",
        )


def test_backdated_revocation_rejects() -> None:
    with pytest.raises(
        SystemPermissionAssignmentError,
        match="REVOCATION_CHRONOLOGY_INVALID",
    ):
        active().revoke(
            revoked_by_principal_id="revoker",
            revoked_at=(
                NOW - timedelta(microseconds=1)
            ),
            revocation_evidence_reference=
                "revocation-evidence",
        )


def test_active_revision_cannot_carry_revocation_material() -> None:
    value = active()

    with pytest.raises(
        SystemPermissionAssignmentError,
        match="ACTIVE_REVOCATION_METADATA_FORBIDDEN",
    ):
        SystemPermissionAssignment(
            assignment_id=value.assignment_id,
            principal_id=value.principal_id,
            permission_id=value.permission_id,
            status=SystemPermissionAssignmentStatus.ACTIVE,
            assigned_by_principal_id=
                value.assigned_by_principal_id,
            assigned_at=value.assigned_at,
            assignment_evidence_reference=
                value.assignment_evidence_reference,
            revision=1,
            previous_assignment_fingerprint=None,
            revoked_by_principal_id="revoker",
            revoked_at=NOW,
            revocation_evidence_reference="revocation",
        )


def test_active_revision_must_be_one_and_unchained() -> None:
    value = active()

    with pytest.raises(
        SystemPermissionAssignmentError,
        match="ACTIVE_REVISION_INVALID",
    ):
        SystemPermissionAssignment(
            assignment_id=value.assignment_id,
            principal_id=value.principal_id,
            permission_id=value.permission_id,
            status=SystemPermissionAssignmentStatus.ACTIVE,
            assigned_by_principal_id=
                value.assigned_by_principal_id,
            assigned_at=value.assigned_at,
            assignment_evidence_reference=
                value.assignment_evidence_reference,
            revision=2,
            previous_assignment_fingerprint=None,
            revoked_by_principal_id=None,
            revoked_at=None,
            revocation_evidence_reference=None,
        )


def test_revoked_revision_requires_previous_fingerprint() -> None:
    value = active()

    with pytest.raises(
        SystemPermissionAssignmentError,
        match="REVOKED_PREVIOUS_FINGERPRINT_REQUIRED",
    ):
        SystemPermissionAssignment(
            assignment_id=value.assignment_id,
            principal_id=value.principal_id,
            permission_id=value.permission_id,
            status=SystemPermissionAssignmentStatus.REVOKED,
            assigned_by_principal_id=
                value.assigned_by_principal_id,
            assigned_at=value.assigned_at,
            assignment_evidence_reference=
                value.assignment_evidence_reference,
            revision=2,
            previous_assignment_fingerprint=None,
            revoked_by_principal_id="revoker",
            revoked_at=(
                NOW + timedelta(minutes=1)
            ),
            revocation_evidence_reference=
                "revocation",
        )


def test_fingerprint_covers_authority_material() -> None:
    one = active(
        assignment_id="opaque-one",
    )
    two = active(
        assignment_id="opaque-two",
    )

    assert (
        one.assignment_fingerprint
        != two.assignment_fingerprint
    )

    assert (
        one.assignment_fingerprint
        == active(
            assignment_id="opaque-one",
        ).assignment_fingerprint
    )


def test_serialization_has_no_tenant_role_or_target_privilege() -> None:
    payload = active().to_dict()

    forbidden = {
        "tenant_id",
        "role_id",
        "business_role",
        "target_class",
        "privileged_role_id",
        "activation_id",
        "session_id",
        "token",
        "password",
        "otp",
        "private_key",
        "payment_id",
        "settlement_id",
    }

    assert forbidden.isdisjoint(payload)


def test_assignment_does_not_expose_current_authorization_api() -> None:
    value = active()

    forbidden = (
        "authorize",
        "is_authorized",
        "activate",
        "issue_activation",
        "grant_role",
        "grant_tenant",
        "execute",
    )

    assert all(
        not hasattr(value, name)
        for name in forbidden
    )


def test_source_has_no_io_clock_random_or_privilege_shortcuts() -> None:
    source = getsource(
        SystemPermissionAssignment
    )

    for forbidden in (
        "MongoClient",
        "pymongo",
        "requests",
        "httpx",
        "uuid4(",
        "datetime.now(",
        "start_session(",
        "start_transaction(",
        "admin:all",
        "tenant:manage",
        "SUPER_ADMIN",
        "FOUNDER",
        "GLOBAL_ROOT",
    ):
        assert forbidden not in source


def test_assignment_is_permission_possession_evidence_only() -> None:
    payload = active().to_dict()

    assert payload["permission_id"] == (
        "privileged_activation:issue"
    )

    assert "tenant_id" not in payload
    assert "privileged_role_id" not in payload
    assert "activation_id" not in payload
    assert "authorized" not in payload
    assert "financial_authority" not in payload


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# ARTIFACT: tests/unit/test_system_permission_assignment.py
# VERSION: v1.0.0-P4-R4-D5-SYSTEM-PERMISSION-ASSIGNMENT-DOMAIN-CERT
# CERTIFIES: pure immutable SYSTEM permission-assignment semantics only
# REGISTRY AUTHORITY: NONE
# CURRENT PERMISSION AUTHORITY: NONE
# PRIVILEGED ACTIVATION AUTHORITY: NONE
# P5 PRIVILEGED USE AUTHORITY: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS TEST ARTIFACT
