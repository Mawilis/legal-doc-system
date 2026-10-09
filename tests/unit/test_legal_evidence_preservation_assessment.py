"""Direct certificate for C4D4C Legal Evidence preservation composition."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import hashlib

import pytest

from tools.eos.legal_operations.domain.legal_evidence_legal_hold_constraint import (
    LegalEvidenceLegalHoldConstraint,
    LegalEvidenceLegalHoldState,
)
from tools.eos.legal_operations.domain.legal_evidence_preservation_assessment import (
    LegalEvidencePreservationAssessmentError,
    LegalEvidencePreservationState,
    assess_legal_evidence_preservation,
)
from tools.eos.legal_operations.domain.legal_evidence_retention_constraint import (
    LegalEvidenceRetentionConstraint,
)


AT = datetime(
    2026,
    9,
    30,
    18,
    30,
    tzinfo=timezone.utc,
)

RETENTION_SOURCE_FP = hashlib.sha3_512(
    b"retention-source-c4d4c"
).hexdigest()

HOLD_SOURCE_FP = hashlib.sha3_512(
    b"hold-source-c4d4c"
).hexdigest()


def _retention(
    *,
    retain_until: datetime,
) -> LegalEvidenceRetentionConstraint:
    return LegalEvidenceRetentionConstraint(
        tenant_id="tenant-c4d4c",
        provider_name="aws_s3",
        storage_reference="legal-evidence/c4d4c/object",
        object_version_reference="version-c4d4c",
        source_evidence_reference="retention-source-c4d4c",
        source_evidence_fingerprint=RETENTION_SOURCE_FP,
        imposed_at=AT,
        retain_until=retain_until,
    )


def _active_hold() -> LegalEvidenceLegalHoldConstraint:
    return LegalEvidenceLegalHoldConstraint(
        tenant_id="tenant-c4d4c",
        provider_name="aws_s3",
        storage_reference="legal-evidence/c4d4c/object",
        object_version_reference="version-c4d4c",
        hold_reference="hold-c4d4c",
        source_evidence_reference="hold-source-c4d4c",
        source_evidence_fingerprint=HOLD_SOURCE_FP,
        imposed_at=AT,
        state=LegalEvidenceLegalHoldState.ACTIVE,
    )


def _released_hold(
    *,
    released_at: datetime,
) -> LegalEvidenceLegalHoldConstraint:
    return LegalEvidenceLegalHoldConstraint(
        tenant_id="tenant-c4d4c",
        provider_name="aws_s3",
        storage_reference="legal-evidence/c4d4c/object",
        object_version_reference="version-c4d4c",
        hold_reference="hold-c4d4c",
        source_evidence_reference="hold-source-c4d4c",
        source_evidence_fingerprint=HOLD_SOURCE_FP,
        imposed_at=AT,
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=released_at,
    )


def test_retention_and_active_hold_both_require_preservation() -> None:
    result = assess_legal_evidence_preservation(
        _retention(
            retain_until=AT + timedelta(days=30),
        ),
        _active_hold(),
        assessed_at=AT + timedelta(days=5),
    )

    assert (
        result.state
        is LegalEvidencePreservationState
        .RETENTION_AND_LEGAL_HOLD_REQUIRED
    )
    assert result.preservation_required is True
    assert result.orphan_proven is False
    assert result.deletion_authorized is False
    assert result.provider_delete_authorized is False


def test_retention_only_requires_preservation() -> None:
    assessed = AT + timedelta(days=20)

    result = assess_legal_evidence_preservation(
        _retention(
            retain_until=AT + timedelta(days=30),
        ),
        _released_hold(
            released_at=AT + timedelta(days=10),
        ),
        assessed_at=assessed,
    )

    assert (
        result.state
        is LegalEvidencePreservationState.RETENTION_REQUIRED
    )
    assert result.preservation_required is True


def test_active_hold_only_requires_preservation() -> None:
    result = assess_legal_evidence_preservation(
        _retention(
            retain_until=AT + timedelta(days=10),
        ),
        _active_hold(),
        assessed_at=AT + timedelta(days=20),
    )

    assert (
        result.state
        is LegalEvidencePreservationState.LEGAL_HOLD_REQUIRED
    )
    assert result.preservation_required is True


def test_no_preservation_block_is_not_delete_authority() -> None:
    assessed = AT + timedelta(days=20)

    result = assess_legal_evidence_preservation(
        _retention(
            retain_until=AT + timedelta(days=10),
        ),
        _released_hold(
            released_at=AT + timedelta(days=15),
        ),
        assessed_at=assessed,
    )

    assert (
        result.state
        is LegalEvidencePreservationState
        .NO_PRESERVATION_BLOCK_DEMONSTRATED
    )
    assert result.preservation_required is False
    assert result.orphan_proven is False
    assert result.deletion_authorized is False
    assert result.provider_delete_authorized is False


def test_release_boundary_and_retention_boundary_compose_exactly() -> None:
    boundary = AT + timedelta(days=10)

    result = assess_legal_evidence_preservation(
        _retention(
            retain_until=boundary,
        ),
        _released_hold(
            released_at=boundary,
        ),
        assessed_at=boundary,
    )

    assert (
        result.state
        is LegalEvidencePreservationState
        .NO_PRESERVATION_BLOCK_DEMONSTRATED
    )
    assert result.preservation_required is False


def test_cross_object_identity_rejects_fail_closed() -> None:
    hold = replace(
        _active_hold(),
        storage_reference="legal-evidence/c4d4c/other-object",
        fingerprint="",
    )

    with pytest.raises(
        LegalEvidencePreservationAssessmentError,
        match="OBJECT_IDENTITY_MISMATCH",
    ):
        assess_legal_evidence_preservation(
            _retention(
                retain_until=AT + timedelta(days=30),
            ),
            hold,
            assessed_at=AT + timedelta(days=1),
        )


def test_cross_tenant_identity_rejects_fail_closed() -> None:
    hold = replace(
        _active_hold(),
        tenant_id="tenant-c4d4c-other",
        fingerprint="",
    )

    with pytest.raises(
        LegalEvidencePreservationAssessmentError,
        match="OBJECT_IDENTITY_MISMATCH",
    ):
        assess_legal_evidence_preservation(
            _retention(
                retain_until=AT + timedelta(days=30),
            ),
            hold,
            assessed_at=AT + timedelta(days=1),
        )


def test_result_is_immutable() -> None:
    result = assess_legal_evidence_preservation(
        _retention(
            retain_until=AT + timedelta(days=30),
        ),
        _active_hold(),
        assessed_at=AT + timedelta(days=1),
    )

    with pytest.raises(FrozenInstanceError):
        result.preservation_required = False  # type: ignore[misc]


def test_public_surface_excludes_orphan_delete_and_provider_commands() -> None:
    public = {
        name.lower()
        for name in dir(
            __import__(
                "tools.eos.legal_operations.domain."
                "legal_evidence_preservation_assessment",
                fromlist=["*"],
            )
        )
        if not name.startswith("_")
    }

    forbidden = {
        "prove_orphan",
        "authorize_delete",
        "authorize_deletion",
        "delete",
        "delete_object",
        "provider_delete",
        "execute_delete",
        "apply_retention_policy",
        "place_legal_hold",
        "release_legal_hold",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(public)


# ARTIFACT: test_legal_evidence_preservation_assessment.py
# VERSION: v1.0.0-L10A2R-C4D4C-LEGAL-EVIDENCE-PRESERVATION-ASSESSMENT-CERT
# AUTHORITY BOUNDARY: direct retention + hold preservation composition evidence
# ORPHAN POSTURE: no preservation block is not orphan proof
# DELETION POSTURE: no preservation block never authorizes deletion
# PROVIDER MUTATION POSTURE: none
# END OF WILSY OS SOVEREIGN ARTIFACT
