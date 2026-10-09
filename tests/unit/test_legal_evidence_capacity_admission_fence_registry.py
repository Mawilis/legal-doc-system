"""Direct certificate for the tenant Legal Evidence capacity admission fence.

TITLE: Legal Evidence Capacity Admission Fence Registry Certificate
VERSION: v1.0.0-L10A2Q-P5C-A-LEGAL-EVIDENCE-CAPACITY-ADMISSION-FENCE-CERT
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Freeze the tenant-scoped serialization primitive required before P5C
    capacity admission may aggregate P4 remaining capacity and outstanding P5B
    reservations.

EPITOME:
    TENANT CAPACITY DECISION ATTEMPT
    -> TENANT ADMISSION FENCE CAS
    -> ONE SERIALIZED TRANSACTION SNAPSHOT
    != CAPACITY AVAILABLE
    != CAPACITY RESERVED
    != USAGE COMMITTED
    != PROVIDER WRITE
    != AUTHORIZED AVAILABILITY

CONCURRENCY:
    Exactly one durable fence row exists per tenant. First acquisition creates
    revision 1. Every later acquisition requires the exact current revision and
    advances it exactly once. Stale or competing CAS loses fail closed.

TRANSACTION:
    Every operational read/write requires one caller-owned already-active
    transaction. Index creation is administrative.

AUTHORITY BOUNDARY:
    Coordination evidence only. This registry does not own plan, entitlement,
    capacity, usage, reservation, provider, document, IAM, retention, billing,
    payment, settlement or financial execution truth.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from typing import Any
from unittest.mock import MagicMock

import pytest
from pymongo import ReturnDocument

from tools.eos.legal_operations.registry.legal_evidence_capacity_admission_fence_registry import (
    COLLECTION,
    INDEX_TENANT_FENCE,
    LegalEvidenceCapacityAdmissionFence,
    LegalEvidenceCapacityAdmissionFenceConflictError,
    LegalEvidenceCapacityAdmissionFenceNotFoundError,
    LegalEvidenceCapacityAdmissionFencePersistedRecordInvalidError,
    LegalEvidenceCapacityAdmissionFenceRegistry,
    LegalEvidenceCapacityAdmissionFenceTransactionRequiredError,
)


AT = datetime(
    2026,
    9,
    30,
    5,
    45,
    0,
    123456,
    tzinfo=timezone.utc,
)


class Session:
    """Minimal caller-owned transaction double."""

    def __init__(self, in_transaction: bool) -> None:
        self.in_transaction = in_transaction


def _fence(
    *,
    tenant_id: str = "tenant-p5ca",
    revision: int = 1,
    advanced_at: datetime = AT,
    coordination_reference: str = "reservation-p5ca-a",
) -> LegalEvidenceCapacityAdmissionFence:
    return LegalEvidenceCapacityAdmissionFence(
        tenant_id=tenant_id,
        revision=revision,
        advanced_at=advanced_at,
        coordination_reference=coordination_reference,
    )


def _row(
    fence: LegalEvidenceCapacityAdmissionFence,
) -> dict[str, object]:
    payload = fence.to_dict()
    payload["_id"] = "mongo-id"
    return payload


def test_collection_and_index_identity_are_closed_contract() -> None:
    assert (
        COLLECTION
        == "legal_evidence_capacity_admission_fences"
    )
    assert (
        INDEX_TENANT_FENCE
        == "legal_evidence_capacity_admission_fence_tenant_unique"
    )


def test_ensure_indexes_creates_exact_unique_tenant_index_without_ttl() -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityAdmissionFenceRegistry(
        collection
    )

    registry.ensure_indexes()

    collection.create_index.assert_called_once_with(
        [("tenant_id", 1)],
        unique=True,
        name=INDEX_TENANT_FENCE,
    )

    kwargs = collection.create_index.call_args.kwargs
    assert "expireAfterSeconds" not in kwargs


@pytest.mark.parametrize(
    "session",
    [
        None,
        Session(False),
    ],
)
def test_get_requires_caller_owned_active_transaction_before_database_call(
    session: Any,
) -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityAdmissionFenceRegistry(
        collection
    )

    with pytest.raises(
        LegalEvidenceCapacityAdmissionFenceTransactionRequiredError,
        match="L10A2Q_P5CA_TRANSACTION_REQUIRED",
    ):
        registry.get(
            tenant_id="tenant-p5ca",
            session=session,
        )

    collection.find_one.assert_not_called()


@pytest.mark.parametrize(
    "session",
    [
        None,
        Session(False),
    ],
)
def test_advance_requires_caller_owned_active_transaction_before_database_call(
    session: Any,
) -> None:
    collection = MagicMock()
    registry = LegalEvidenceCapacityAdmissionFenceRegistry(
        collection
    )

    with pytest.raises(
        LegalEvidenceCapacityAdmissionFenceTransactionRequiredError,
        match="L10A2Q_P5CA_TRANSACTION_REQUIRED",
    ):
        registry.advance(
            tenant_id="tenant-p5ca",
            expected_revision=None,
            coordination_reference="reservation-p5ca-a",
            advanced_at=AT,
            session=session,
        )

    collection.find_one.assert_not_called()
    collection.insert_one.assert_not_called()
    collection.find_one_and_update.assert_not_called()


def test_first_advance_creates_revision_one() -> None:
    collection = MagicMock()
    collection.find_one.return_value = None
    registry = LegalEvidenceCapacityAdmissionFenceRegistry(
        collection
    )

    result = registry.advance(
        tenant_id="tenant-p5ca",
        expected_revision=None,
        coordination_reference="reservation-p5ca-a",
        advanced_at=AT,
        session=Session(True),
    )

    assert result == _fence()
    collection.insert_one.assert_called_once()

    inserted = collection.insert_one.call_args.args[0]
    assert inserted == result.to_dict()
    assert inserted["tenant_id"] == "tenant-p5ca"
    assert inserted["revision"] == 1

    collection.find_one_and_update.assert_not_called()


def test_first_advance_requires_expected_none() -> None:
    collection = MagicMock()
    collection.find_one.return_value = None
    registry = LegalEvidenceCapacityAdmissionFenceRegistry(
        collection
    )

    with pytest.raises(
        LegalEvidenceCapacityAdmissionFenceConflictError,
        match="L10A2Q_P5CA_INITIAL_REVISION_EXPECTED_NONE",
    ):
        registry.advance(
            tenant_id="tenant-p5ca",
            expected_revision=1,
            coordination_reference="reservation-p5ca-a",
            advanced_at=AT,
            session=Session(True),
        )

    collection.insert_one.assert_not_called()
    collection.find_one_and_update.assert_not_called()


def test_existing_fence_requires_exact_expected_revision_and_cas_increment() -> None:
    current = _fence()
    successor = _fence(
        revision=2,
        advanced_at=AT + timedelta(seconds=1),
        coordination_reference="reservation-p5ca-b",
    )

    collection = MagicMock()
    collection.find_one.return_value = _row(current)
    collection.find_one_and_update.return_value = _row(
        successor
    )
    registry = LegalEvidenceCapacityAdmissionFenceRegistry(
        collection
    )

    result = registry.advance(
        tenant_id=current.tenant_id,
        expected_revision=1,
        coordination_reference="reservation-p5ca-b",
        advanced_at=AT + timedelta(seconds=1),
        session=Session(True),
    )

    assert result == successor

    collection.find_one_and_update.assert_called_once_with(
        {
            "tenant_id": current.tenant_id,
            "revision": 1,
            "fingerprint": current.fingerprint,
        },
        {
            "$set": {
                "revision": 2,
                "advanced_at": successor.to_dict()[
                    "advanced_at"
                ],
                "coordination_reference":
                    successor.coordination_reference,
                "fingerprint": successor.fingerprint,
            }
        },
        return_document=ReturnDocument.AFTER,
        session=collection.find_one_and_update.call_args.kwargs[
            "session"
        ],
    )


def test_existing_fence_rejects_missing_or_wrong_expected_revision() -> None:
    current = _fence()

    for expected in (None, 0, 2):
        collection = MagicMock()
        collection.find_one.return_value = _row(current)
        registry = (
            LegalEvidenceCapacityAdmissionFenceRegistry(
                collection
            )
        )

        with pytest.raises(
            LegalEvidenceCapacityAdmissionFenceConflictError,
            match="L10A2Q_P5CA_EXPECTED_REVISION_MISMATCH",
        ):
            registry.advance(
                tenant_id=current.tenant_id,
                expected_revision=expected,
                coordination_reference="reservation-p5ca-b",
                advanced_at=AT + timedelta(seconds=1),
                session=Session(True),
            )

        collection.find_one_and_update.assert_not_called()


def test_cas_loss_fails_closed() -> None:
    current = _fence()

    collection = MagicMock()
    collection.find_one.side_effect = [
        _row(current),
        _row(
            _fence(
                revision=2,
                advanced_at=AT + timedelta(seconds=1),
                coordination_reference="reservation-competing",
            )
        ),
    ]
    collection.find_one_and_update.return_value = None

    registry = LegalEvidenceCapacityAdmissionFenceRegistry(
        collection
    )

    with pytest.raises(
        LegalEvidenceCapacityAdmissionFenceConflictError,
        match="L10A2Q_P5CA_FENCE_CAS_CONFLICT",
    ):
        registry.advance(
            tenant_id=current.tenant_id,
            expected_revision=1,
            coordination_reference="reservation-p5ca-b",
            advanced_at=AT + timedelta(seconds=2),
            session=Session(True),
        )


def test_get_is_exact_tenant_scoped() -> None:
    own = _fence()

    collection = MagicMock()
    collection.find_one.side_effect = [
        _row(own),
        None,
    ]
    registry = LegalEvidenceCapacityAdmissionFenceRegistry(
        collection
    )
    session = Session(True)

    assert (
        registry.get(
            tenant_id=own.tenant_id,
            session=session,
        )
        == own
    )

    with pytest.raises(
        LegalEvidenceCapacityAdmissionFenceNotFoundError,
        match="L10A2Q_P5CA_FENCE_NOT_FOUND",
    ):
        registry.get(
            tenant_id="tenant-neighbor",
            session=session,
        )


def test_corrupt_persisted_fence_rejects_without_repair() -> None:
    persisted = _row(_fence())
    persisted["fingerprint"] = "0" * 128

    collection = MagicMock()
    collection.find_one.return_value = persisted
    registry = LegalEvidenceCapacityAdmissionFenceRegistry(
        collection
    )

    with pytest.raises(
        LegalEvidenceCapacityAdmissionFencePersistedRecordInvalidError,
        match="L10A2Q_P5CA_PERSISTED_RECORD_INVALID",
    ):
        registry.get(
            tenant_id="tenant-p5ca",
            session=Session(True),
        )


def test_fence_value_is_immutable_and_serialization_is_defensive() -> None:
    fence = _fence()

    with pytest.raises(
        (AttributeError, TypeError),
    ):
        fence.revision = 2  # type: ignore[misc]

    serialized = fence.to_dict()
    serialized["revision"] = 999

    assert fence.revision == 1
    assert fence.to_dict()["revision"] == 1

    proxy = MappingProxyType(fence.to_dict())
    assert proxy["fingerprint"] == fence.fingerprint


@pytest.mark.parametrize(
    "revision",
    [
        0,
        -1,
        True,
    ],
)
def test_revision_requires_positive_non_boolean_integer(
    revision: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="L10A2Q_P5CA_REVISION_INVALID",
    ):
        LegalEvidenceCapacityAdmissionFence(
            tenant_id="tenant-p5ca",
            revision=revision,  # type: ignore[arg-type]
            advanced_at=AT,
            coordination_reference="reservation-p5ca-a",
        )


def test_surface_has_coordination_authority_only() -> None:
    forbidden = {
        "reserve",
        "admit",
        "upload",
        "provider",
        "usage",
        "entitlement",
        "billing",
        "payment",
        "settlement",
        "execute",
    }

    public = {
        name.lower()
        for name in dir(
            LegalEvidenceCapacityAdmissionFenceRegistry
        )
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(public)


# ARTIFACT: test_legal_evidence_capacity_admission_fence_registry.py
# VERSION: v1.0.0-L10A2Q-P5C-A-LEGAL-EVIDENCE-CAPACITY-ADMISSION-FENCE-CERT
# AUTHORITY BOUNDARY: tenant capacity admission serialization evidence only
# TENANT POSTURE: exactly one durable coordination fence per tenant
# TRANSACTION POSTURE: caller owns one already-active transaction
# EXPIRY POSTURE: no TTL; coordination evidence is never wall-clock deleted
# RECONCILIATION POSTURE: P5D remains owner of semantic reservation reconciliation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
