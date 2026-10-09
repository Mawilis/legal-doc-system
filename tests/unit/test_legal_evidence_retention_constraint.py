"""Direct certificate for C4D4A Legal Evidence retention constraint."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import hashlib

import pytest

from tools.eos.legal_operations.domain.legal_evidence_retention_constraint import (
    LegalEvidenceRetentionConstraint,
    LegalEvidenceRetentionConstraintError,
    LegalEvidenceRetentionState,
    assess_legal_evidence_retention,
)


AT = datetime(
    2026,
    9,
    30,
    17,
    30,
    tzinfo=timezone.utc,
)

SOURCE_FP = hashlib.sha3_512(
    b"authoritative-retention-source"
).hexdigest()


def _constraint(
    *,
    imposed_at: datetime = AT,
    retain_until: datetime = AT + timedelta(days=30),
) -> LegalEvidenceRetentionConstraint:
    return LegalEvidenceRetentionConstraint(
        tenant_id="tenant-c4d4a",
        provider_name="aws_s3",
        storage_reference="legal-evidence/c4d4a/object",
        object_version_reference="version-c4d4a",
        source_evidence_reference="retention-source-c4d4a",
        source_evidence_fingerprint=SOURCE_FP,
        imposed_at=imposed_at,
        retain_until=retain_until,
    )


def test_constraint_is_exact_immutable_and_deterministic() -> None:
    first = _constraint()
    second = _constraint()

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128

    with pytest.raises(FrozenInstanceError):
        first.tenant_id = "tenant-mutated"  # type: ignore[misc]


def test_active_before_retain_until() -> None:
    constraint = _constraint()

    result = assess_legal_evidence_retention(
        constraint,
        assessed_at=AT + timedelta(days=29),
    )

    assert result.state is LegalEvidenceRetentionState.ACTIVE
    assert result.retention_elapsed is False
    assert result.legal_hold_cleared is False
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False


def test_elapsed_at_exact_boundary() -> None:
    constraint = _constraint()

    result = assess_legal_evidence_retention(
        constraint,
        assessed_at=constraint.retain_until,
    )

    assert result.state is LegalEvidenceRetentionState.ELAPSED
    assert result.retention_elapsed is True
    assert result.legal_hold_cleared is False
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False


def test_elapsed_after_boundary_is_still_not_delete_authority() -> None:
    constraint = _constraint()

    result = assess_legal_evidence_retention(
        constraint,
        assessed_at=constraint.retain_until + timedelta(days=365),
    )

    assert result.retention_elapsed is True
    assert result.provider_delete_authorized is False
    assert result.orphan_proven is False
    assert result.legal_hold_cleared is False


def test_interval_inversion_rejects() -> None:
    with pytest.raises(
        LegalEvidenceRetentionConstraintError,
        match="RETENTION_INTERVAL_INVALID",
    ):
        _constraint(
            retain_until=AT - timedelta(seconds=1),
        )


def test_assessment_before_constraint_rejects() -> None:
    constraint = _constraint()

    with pytest.raises(
        LegalEvidenceRetentionConstraintError,
        match="ASSESSMENT_PRECEDES_CONSTRAINT",
    ):
        assess_legal_evidence_retention(
            constraint,
            assessed_at=AT - timedelta(seconds=1),
        )


def test_naive_time_rejects() -> None:
    naive = datetime(
        2026,
        9,
        30,
        17,
        30,
    )

    with pytest.raises(
        LegalEvidenceRetentionConstraintError,
        match="IMPOSED_AT_INVALID",
    ):
        _constraint(
            imposed_at=naive,
        )


def test_pseudo_global_tenant_rejects() -> None:
    with pytest.raises(
        LegalEvidenceRetentionConstraintError,
        match="TENANT_REQUIRED",
    ):
        replace(
            _constraint(),
            tenant_id="global",
            fingerprint="",
        )


def test_source_fingerprint_corruption_rejects() -> None:
    with pytest.raises(
        LegalEvidenceRetentionConstraintError,
        match="SOURCE_EVIDENCE_FINGERPRINT_INVALID",
    ):
        replace(
            _constraint(),
            source_evidence_fingerprint="not-a-fingerprint",
            fingerprint="",
        )


def test_fingerprint_drift_rejects_constant_time_path() -> None:
    with pytest.raises(
        LegalEvidenceRetentionConstraintError,
        match="FINGERPRINT_MISMATCH",
    ):
        replace(
            _constraint(),
            fingerprint="f" * 128,
        )


def test_later_authority_flags_reject() -> None:
    for field in (
        "legal_hold_cleared",
        "orphan_proven",
        "provider_delete_authorized",
    ):
        with pytest.raises(
            LegalEvidenceRetentionConstraintError,
            match="LATER_AUTHORITY_FORBIDDEN",
        ):
            replace(
                _constraint(),
                **{
                    field: True,
                    "fingerprint": "",
                },
            )


def test_public_surface_excludes_policy_selection_hold_and_delete_commands() -> None:
    public = {
        name.lower()
        for name in dir(
            __import__(
                "tools.eos.legal_operations.domain."
                "legal_evidence_retention_constraint",
                fromlist=["*"],
            )
        )
        if not name.startswith("_")
    }

    forbidden = {
        "select_retention_policy",
        "calculate_statutory_period",
        "apply_retention_policy",
        "place_legal_hold",
        "release_legal_hold",
        "clear_legal_hold",
        "prove_orphan",
        "delete",
        "delete_object",
        "authorize_delete",
        "authorize_deletion",
        "make_available",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(public)


# ARTIFACT: test_legal_evidence_retention_constraint.py
# VERSION: v1.0.0-L10A2R-C4D4A-LEGAL-EVIDENCE-RETENTION-CONSTRAINT-CERT
# AUTHORITY BOUNDARY: direct pure retention-constraint evidence only
# POLICY POSTURE: no statutory/commercial policy selection
# LEGAL HOLD POSTURE: no hold authority
# ORPHAN POSTURE: elapsed retention is not orphan proof
# DELETION POSTURE: elapsed retention never authorizes deletion
# PROVIDER MUTATION POSTURE: none
# END OF WILSY OS SOVEREIGN ARTIFACT
