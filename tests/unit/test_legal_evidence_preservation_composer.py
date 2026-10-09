"""Direct certificate for the C4D4C Legal Evidence preservation composer.

VERSION: v1.0.0-L10A2R-C4D4C-PRESERVATION-COMPOSER-CERT
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_evidence_legal_hold_constraint import (
    LegalEvidenceLegalHoldConstraint,
    LegalEvidenceLegalHoldState,
)
from tools.eos.legal_operations.domain.legal_evidence_legal_hold_currentness import (
    LegalEvidenceLegalHoldCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_evidence_preservation_assessment import (
    LegalEvidencePreservationState,
)
from tools.eos.legal_operations.domain.legal_evidence_retention_constraint import (
    LegalEvidenceRetentionConstraint,
)
from tools.eos.legal_operations.orchestration.legal_evidence_preservation_composer import (
    LegalEvidencePreservationComposer,
    LegalEvidencePreservationComposerError,
)


BASE = datetime(
    2026,
    10,
    1,
    12,
    0,
    tzinfo=timezone.utc,
)


class _Session:
    def __init__(
        self,
        active: bool,
    ) -> None:
        self.in_transaction = active


class _RetentionRegistry:
    def __init__(
        self,
        value: LegalEvidenceRetentionConstraint,
    ) -> None:
        self.value = value
        self.calls: list[
            dict[str, Any]
        ] = []

    def get_by_provider_object(
        self,
        **kwargs: Any,
    ) -> LegalEvidenceRetentionConstraint:
        self.calls.append(
            kwargs
        )
        return self.value


class _HoldRegistry:
    def __init__(
        self,
        values: tuple[
            LegalEvidenceLegalHoldConstraint,
            ...,
        ],
    ) -> None:
        self.values = values
        self.calls: list[
            dict[str, Any]
        ] = []

    def list_provider_object_history(
        self,
        **kwargs: Any,
    ) -> tuple[
        LegalEvidenceLegalHoldConstraint,
        ...,
    ]:
        self.calls.append(
            kwargs
        )
        return self.values


def _retention(
    *,
    retain_until: datetime,
) -> LegalEvidenceRetentionConstraint:
    return LegalEvidenceRetentionConstraint(
        tenant_id="tenant-composer",
        provider_name="s3",
        storage_reference="bucket-composer",
        object_version_reference="object-v1",
        source_evidence_reference="source-retention",
        source_evidence_fingerprint="a" * 128,
        imposed_at=BASE - timedelta(days=10),
        retain_until=retain_until,
    )


def _hold(
    *,
    state: LegalEvidenceLegalHoldState,
    released_at: datetime | None = None,
) -> LegalEvidenceLegalHoldConstraint:
    return LegalEvidenceLegalHoldConstraint(
        tenant_id="tenant-composer",
        provider_name="s3",
        storage_reference="bucket-composer",
        object_version_reference="object-v1",
        hold_reference="hold-a",
        source_evidence_reference="source-hold",
        source_evidence_fingerprint="b" * 128,
        imposed_at=BASE - timedelta(days=5),
        state=state,
        released_at=released_at,
    )


def _compose(
    *,
    retention: LegalEvidenceRetentionConstraint,
    history: tuple[
        LegalEvidenceLegalHoldConstraint,
        ...,
    ],
    assessed_at: datetime = BASE,
):
    retention_registry = (
        _RetentionRegistry(
            retention
        )
    )
    hold_registry = (
        _HoldRegistry(
            history
        )
    )
    session = _Session(
        True
    )

    composer = (
        LegalEvidencePreservationComposer(
            retention_registry,
            hold_registry,
        )
    )

    result = composer.compose_preservation(
        tenant_id="tenant-composer",
        provider_name="s3",
        storage_reference="bucket-composer",
        object_version_reference="object-v1",
        assessed_at=assessed_at,
        session=session,
    )

    return (
        result,
        retention_registry,
        hold_registry,
        session,
    )


def test_active_retention_without_hold_requires_retention() -> None:
    result, _, _, _ = _compose(
        retention=_retention(
            retain_until=BASE + timedelta(days=5),
        ),
        history=(),
    )

    assert result.state is (
        LegalEvidencePreservationState.RETENTION_REQUIRED
    )
    assert result.preservation_required is True
    assert result.legal_hold_currentness.state is (
        LegalEvidenceLegalHoldCurrentnessState.NO_HOLD_EVIDENCE
    )


def test_elapsed_retention_without_hold_has_no_demonstrated_block() -> None:
    result, _, _, _ = _compose(
        retention=_retention(
            retain_until=BASE,
        ),
        history=(),
    )

    assert result.state is (
        LegalEvidencePreservationState.NO_PRESERVATION_BLOCK_DEMONSTRATED
    )
    assert result.preservation_required is False


def test_active_hold_with_elapsed_retention_requires_hold() -> None:
    result, _, _, _ = _compose(
        retention=_retention(
            retain_until=BASE,
        ),
        history=(
            _hold(
                state=LegalEvidenceLegalHoldState.ACTIVE,
            ),
        ),
    )

    assert result.state is (
        LegalEvidencePreservationState.LEGAL_HOLD_REQUIRED
    )
    assert result.preservation_required is True


def test_active_retention_and_active_hold_require_both() -> None:
    result, _, _, _ = _compose(
        retention=_retention(
            retain_until=BASE + timedelta(days=5),
        ),
        history=(
            _hold(
                state=LegalEvidenceLegalHoldState.ACTIVE,
            ),
        ),
    )

    assert result.state is (
        LegalEvidencePreservationState.RETENTION_AND_LEGAL_HOLD_REQUIRED
    )


def test_released_hold_at_boundary_no_longer_blocks() -> None:
    active = _hold(
        state=LegalEvidenceLegalHoldState.ACTIVE,
    )
    released = _hold(
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE,
    )

    result, _, _, _ = _compose(
        retention=_retention(
            retain_until=BASE,
        ),
        history=(
            active,
            released,
        ),
    )

    assert result.state is (
        LegalEvidencePreservationState.NO_PRESERVATION_BLOCK_DEMONSTRATED
    )


def test_ambiguous_hold_currentness_remains_preservation_blocking() -> None:
    active = _hold(
        state=LegalEvidenceLegalHoldState.ACTIVE,
    )

    release_one = _hold(
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(days=1),
    )

    release_two = _hold(
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(days=2),
    )

    result, _, _, _ = _compose(
        retention=_retention(
            retain_until=BASE,
        ),
        history=(
            active,
            release_one,
            release_two,
        ),
        assessed_at=BASE + timedelta(days=3),
    )

    assert result.legal_hold_currentness.state is (
        LegalEvidenceLegalHoldCurrentnessState.AMBIGUOUS_BLOCKED
    )
    assert result.state is (
        LegalEvidencePreservationState.LEGAL_HOLD_REQUIRED
    )
    assert result.preservation_required is True


def test_inactive_transaction_rejects_before_registry_reads() -> None:
    retention_registry = _RetentionRegistry(
        _retention(
            retain_until=BASE,
        )
    )
    hold_registry = _HoldRegistry(
        ()
    )
    session = _Session(
        False
    )

    composer = LegalEvidencePreservationComposer(
        retention_registry,
        hold_registry,
    )

    with pytest.raises(
        LegalEvidencePreservationComposerError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        composer.compose_preservation(
            tenant_id="tenant-composer",
            provider_name="s3",
            storage_reference="bucket-composer",
            object_version_reference="object-v1",
            assessed_at=BASE,
            session=session,
        )

    assert retention_registry.calls == []
    assert hold_registry.calls == []


def test_same_session_and_exact_scope_propagate_to_both_reads() -> None:
    result, retention_registry, hold_registry, session = _compose(
        retention=_retention(
            retain_until=BASE,
        ),
        history=(),
    )

    assert result.assessed_at == BASE

    assert len(
        retention_registry.calls
    ) == 1

    assert len(
        hold_registry.calls
    ) == 1

    for call in (
        retention_registry.calls[0],
        hold_registry.calls[0],
    ):
        assert call == {
            "tenant_id": "tenant-composer",
            "provider_name": "s3",
            "storage_reference": "bucket-composer",
            "object_version_reference": "object-v1",
            "session": session,
        }


def test_naive_assessment_time_rejects_before_reads() -> None:
    retention_registry = _RetentionRegistry(
        _retention(
            retain_until=BASE,
        )
    )
    hold_registry = _HoldRegistry(
        ()
    )

    composer = LegalEvidencePreservationComposer(
        retention_registry,
        hold_registry,
    )

    with pytest.raises(
        LegalEvidencePreservationComposerError,
        match="ASSESSED_AT_INVALID",
    ):
        composer.compose_preservation(
            tenant_id="tenant-composer",
            provider_name="s3",
            storage_reference="bucket-composer",
            object_version_reference="object-v1",
            assessed_at=datetime(
                2026,
                10,
                1,
                12,
                0,
            ),
            session=_Session(
                True
            ),
        )

    assert retention_registry.calls == []
    assert hold_registry.calls == []


def test_composition_never_creates_later_authority() -> None:
    result, _, _, _ = _compose(
        retention=_retention(
            retain_until=BASE,
        ),
        history=(),
    )

    assert result.orphan_proven is False
    assert result.deletion_authorized is False
    assert result.provider_delete_authorized is False


# ARTIFACT: test_legal_evidence_preservation_composer.py
# VERSION: v1.0.0-L10A2R-C4D4C-PRESERVATION-COMPOSER-CERT
# AUTHORITY BOUNDARY: direct certificate for read-only preservation composition
# END OF WILSY OS SOVEREIGN ARTIFACT
