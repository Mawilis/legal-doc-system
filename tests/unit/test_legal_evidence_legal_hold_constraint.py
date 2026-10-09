"""Direct certificate for C4D4B Legal Evidence legal-hold constraint."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import hashlib

import pytest

from tools.eos.legal_operations.domain.legal_evidence_legal_hold_constraint import (
    LegalEvidenceLegalHoldConstraint,
    LegalEvidenceLegalHoldConstraintError,
    LegalEvidenceLegalHoldState,
    assess_legal_evidence_legal_hold,
)


AT = datetime(
    2026,
    9,
    30,
    18,
    15,
    tzinfo=timezone.utc,
)

SOURCE_FP = hashlib.sha3_512(
    b"authoritative-hold-source"
).hexdigest()


def _active() -> LegalEvidenceLegalHoldConstraint:
    return LegalEvidenceLegalHoldConstraint(
        tenant_id="tenant-c4d4b",
        provider_name="aws_s3",
        storage_reference="legal-evidence/c4d4b/object",
        object_version_reference="version-c4d4b",
        hold_reference="hold-c4d4b",
        source_evidence_reference="hold-source-c4d4b",
        source_evidence_fingerprint=SOURCE_FP,
        imposed_at=AT,
        state=LegalEvidenceLegalHoldState.ACTIVE,
    )


def _released() -> LegalEvidenceLegalHoldConstraint:
    return LegalEvidenceLegalHoldConstraint(
        tenant_id="tenant-c4d4b",
        provider_name="aws_s3",
        storage_reference="legal-evidence/c4d4b/object",
        object_version_reference="version-c4d4b",
        hold_reference="hold-c4d4b",
        source_evidence_reference="hold-source-c4d4b",
        source_evidence_fingerprint=SOURCE_FP,
        imposed_at=AT,
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=AT + timedelta(days=10),
    )


def test_active_constraint_is_immutable_and_deterministic() -> None:
    first = _active()
    second = _active()

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128

    with pytest.raises(FrozenInstanceError):
        first.hold_reference = "mutated"  # type: ignore[misc]


def test_active_hold_blocks_disposition() -> None:
    result = assess_legal_evidence_legal_hold(
        _active(),
        assessed_at=AT + timedelta(days=100),
    )

    assert result.disposition_blocked is True
    assert result.retention_satisfied is False
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False


def test_released_hold_blocks_before_release_instant() -> None:
    result = assess_legal_evidence_legal_hold(
        _released(),
        assessed_at=AT + timedelta(days=5),
    )

    assert result.disposition_blocked is True
    assert result.provider_delete_authorized is False


def test_released_hold_does_not_block_at_release_boundary() -> None:
    constraint = _released()
    assert constraint.released_at is not None

    result = assess_legal_evidence_legal_hold(
        constraint,
        assessed_at=constraint.released_at,
    )

    assert result.disposition_blocked is False
    assert result.retention_satisfied is False
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False


def test_released_hold_never_becomes_delete_authority() -> None:
    constraint = _released()
    assert constraint.released_at is not None

    result = assess_legal_evidence_legal_hold(
        constraint,
        assessed_at=constraint.released_at + timedelta(days=365),
    )

    assert result.disposition_blocked is False
    assert result.provider_delete_authorized is False
    assert result.orphan_proven is False
    assert result.retention_satisfied is False


def test_active_state_rejects_release_timestamp() -> None:
    with pytest.raises(
        LegalEvidenceLegalHoldConstraintError,
        match="ACTIVE_RELEASE_TIME_FORBIDDEN",
    ):
        replace(
            _active(),
            released_at=AT + timedelta(days=1),
            fingerprint="",
        )


def test_released_state_requires_release_timestamp() -> None:
    with pytest.raises(
        LegalEvidenceLegalHoldConstraintError,
        match="RELEASE_TIME_REQUIRED",
    ):
        replace(
            _active(),
            state=LegalEvidenceLegalHoldState.RELEASED,
            fingerprint="",
        )


def test_release_cannot_precede_imposition() -> None:
    with pytest.raises(
        LegalEvidenceLegalHoldConstraintError,
        match="RELEASE_PRECEDES_HOLD",
    ):
        LegalEvidenceLegalHoldConstraint(
            tenant_id="tenant-c4d4b",
            provider_name="aws_s3",
            storage_reference="legal-evidence/c4d4b/object",
            object_version_reference="version-c4d4b",
            hold_reference="hold-c4d4b",
            source_evidence_reference="hold-source-c4d4b",
            source_evidence_fingerprint=SOURCE_FP,
            imposed_at=AT,
            state=LegalEvidenceLegalHoldState.RELEASED,
            released_at=AT - timedelta(seconds=1),
        )


def test_pseudo_global_tenant_rejects() -> None:
    with pytest.raises(
        LegalEvidenceLegalHoldConstraintError,
        match="TENANT_REQUIRED",
    ):
        replace(
            _active(),
            tenant_id="global",
            fingerprint="",
        )


def test_source_fingerprint_corruption_rejects() -> None:
    with pytest.raises(
        LegalEvidenceLegalHoldConstraintError,
        match="SOURCE_EVIDENCE_FINGERPRINT_INVALID",
    ):
        replace(
            _active(),
            source_evidence_fingerprint="bad",
            fingerprint="",
        )


def test_fingerprint_drift_rejects_constant_time_path() -> None:
    with pytest.raises(
        LegalEvidenceLegalHoldConstraintError,
        match="FINGERPRINT_MISMATCH",
    ):
        replace(
            _active(),
            fingerprint="f" * 128,
        )


def test_later_authority_flags_reject() -> None:
    for field in (
        "retention_satisfied",
        "orphan_proven",
        "provider_delete_authorized",
    ):
        with pytest.raises(
            LegalEvidenceLegalHoldConstraintError,
            match="LATER_AUTHORITY_FORBIDDEN",
        ):
            replace(
                _active(),
                **{
                    field: True,
                    "fingerprint": "",
                },
            )


def test_public_surface_excludes_retention_delete_and_provider_commands() -> None:
    public = {
        name.lower()
        for name in dir(
            __import__(
                "tools.eos.legal_operations.domain."
                "legal_evidence_legal_hold_constraint",
                fromlist=["*"],
            )
        )
        if not name.startswith("_")
    }

    forbidden = {
        "satisfy_retention",
        "apply_retention_policy",
        "prove_orphan",
        "delete",
        "delete_object",
        "authorize_delete",
        "authorize_deletion",
        "provider_delete",
        "make_available",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(public)


# ARTIFACT: test_legal_evidence_legal_hold_constraint.py
# VERSION: v1.0.0-L10A2R-C4D4B-LEGAL-EVIDENCE-LEGAL-HOLD-CONSTRAINT-CERT
# AUTHORITY BOUNDARY: direct pure sourced legal-hold evidence only
# RETENTION POSTURE: no retention satisfaction authority
# ORPHAN POSTURE: hold state never proves orphan status
# DELETION POSTURE: released hold never authorizes provider deletion
# PROVIDER MUTATION POSTURE: none
# END OF WILSY OS SOVEREIGN ARTIFACT
