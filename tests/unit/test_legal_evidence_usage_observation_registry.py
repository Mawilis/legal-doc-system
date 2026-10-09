"""Direct certificate for durable Legal Evidence usage-observation registry.

TITLE: Legal Evidence Usage Observation Registry Direct Certificate
VERSION: v1.0.0-L10A2Q-P3B-LEGAL-EVIDENCE-USAGE-OBSERVATION-REGISTRY-CERT
AUTHORITY: WILSY OS Core Governance
PURPOSE:
    Prove append-only tenant-scoped durability for immutable P3A Legal Evidence
    usage observations with exact replay and fail-closed corruption semantics.

EPITOME:
    OBSERVATION DERIVED
    != OBSERVATION DURABLY RECORDED
    != REMAINING CAPACITY
    != CAPACITY RESERVED
    != STORAGE ADMISSION

CERTIFICATION / UPDATE DATE: 2026-09-30

TENANT POSTURE:
    Every identity/read/replay operation is exact tenant scoped.

TRANSACTION POSTURE:
    Caller owns the Mongo session and active transaction.

AUTHORITY BOUNDARY:
    Raw usage-observation durability only. No aggregation, remaining-capacity,
    reservation, entitlement, billing, payment, settlement or execution authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_evidence_content import (
    register_legal_evidence_content,
)
from tools.eos.legal_operations.domain.legal_evidence_usage_observation import (
    LegalEvidenceUsageObservation,
    observe_legal_evidence_usage,
)
from tools.eos.legal_operations.registry.legal_evidence_usage_observation_registry import (
    LegalEvidenceUsageObservationConflictError,
    LegalEvidenceUsageObservationNotFoundError,
    LegalEvidenceUsageObservationRegistry,
    LegalEvidenceUsageObservationRegistryError,
    LegalEvidenceUsageObservationTransactionRequiredError,
)


STAMP = datetime(2026, 9, 30, 0, 30, tzinfo=timezone.utc)
FP = "a" * 128


class _Session:
    def __init__(self, *, in_transaction: bool = True) -> None:
        self.in_transaction = in_transaction


class _InsertResult:
    inserted_id = "row-1"


class _Collection:
    """Minimal deterministic collection double for direct registry semantics."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.find_calls: list[dict[str, Any]] = []
        self.insert_calls: list[dict[str, Any]] = []

    def find_one(
        self,
        query: dict[str, Any],
        *,
        session: Any,
    ) -> dict[str, Any] | None:
        self.find_calls.append(dict(query))
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None

    def insert_one(
        self,
        document: dict[str, Any],
        *,
        session: Any,
    ) -> _InsertResult:
        self.insert_calls.append(dict(document))
        self.rows.append(dict(document))
        return _InsertResult()


def _observation(
    *,
    tenant_id: str = "tenant-l10a2q-p3b",
    document_id: str = "document-l10a2q-p3b",
    content: bytes = b"canonical legal evidence usage",
) -> LegalEvidenceUsageObservation:
    canonical = register_legal_evidence_content(
        tenant_id=tenant_id,
        case_matter_id="matter-l10a2q-p3b",
        document_id=document_id,
        media_type="application/pdf",
        original_filename=f"{document_id}.pdf",
        content=content,
        source_evidence_reference=f"source:{document_id}",
        source_evidence_fingerprint=FP,
        registered_at=STAMP,
    )
    return observe_legal_evidence_usage(content=canonical)


def test_create_persists_exact_observation_and_command_evidence() -> None:
    collection = _Collection()
    registry = LegalEvidenceUsageObservationRegistry(collection)
    observation = _observation()

    persisted = registry.create_or_replay(
        observation,
        idempotency_key="idem-p3b-1",
        session=_Session(),
    )

    assert persisted == observation
    assert len(collection.insert_calls) == 1

    row = collection.insert_calls[0]
    for key, value in observation.to_dict().items():
        assert row[key] == value

    assert row["idempotency_key"] == "idem-p3b-1"
    assert isinstance(row["command_fingerprint"], str)
    assert len(row["command_fingerprint"]) == 128
    int(row["command_fingerprint"], 16)


def test_exact_idempotent_replay_returns_persisted_without_insert() -> None:
    collection = _Collection()
    registry = LegalEvidenceUsageObservationRegistry(collection)
    observation = _observation()

    first = registry.create_or_replay(
        observation,
        idempotency_key="idem-p3b-replay",
        session=_Session(),
    )
    inserts_after_first = len(collection.insert_calls)

    second = registry.create_or_replay(
        observation,
        idempotency_key="idem-p3b-replay",
        session=_Session(),
    )

    assert second == first
    assert len(collection.insert_calls) == inserts_after_first


def test_same_idempotency_with_divergent_observation_rejects() -> None:
    collection = _Collection()
    registry = LegalEvidenceUsageObservationRegistry(collection)

    registry.create_or_replay(
        _observation(document_id="document-a", content=b"content-a"),
        idempotency_key="idem-p3b-conflict",
        session=_Session(),
    )

    with pytest.raises(
        LegalEvidenceUsageObservationConflictError,
        match="L10A2Q_P3B_DIVERGENT_IDEMPOTENCY",
    ):
        registry.create_or_replay(
            _observation(document_id="document-b", content=b"content-b"),
            idempotency_key="idem-p3b-conflict",
            session=_Session(),
        )


def test_same_observation_identity_with_different_idempotency_rejects() -> None:
    collection = _Collection()
    registry = LegalEvidenceUsageObservationRegistry(collection)
    observation = _observation()

    registry.create_or_replay(
        observation,
        idempotency_key="idem-p3b-identity-a",
        session=_Session(),
    )

    with pytest.raises(
        LegalEvidenceUsageObservationConflictError,
        match="L10A2Q_P3B_DIVERGENT_OBSERVATION_IDENTITY",
    ):
        registry.create_or_replay(
            observation,
            idempotency_key="idem-p3b-identity-b",
            session=_Session(),
        )


def test_active_transaction_required_before_collection_access() -> None:
    collection = _Collection()
    registry = LegalEvidenceUsageObservationRegistry(collection)

    with pytest.raises(
        LegalEvidenceUsageObservationTransactionRequiredError,
        match="L10A2Q_P3B_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            _observation(),
            idempotency_key="idem-p3b-no-tx",
            session=_Session(in_transaction=False),
        )

    assert collection.find_calls == []
    assert collection.insert_calls == []


def test_get_is_exact_tenant_scoped() -> None:
    collection = _Collection()
    registry = LegalEvidenceUsageObservationRegistry(collection)
    observation = _observation()

    registry.create_or_replay(
        observation,
        idempotency_key="idem-p3b-get",
        session=_Session(),
    )

    own = registry.get(
        tenant_id=observation.tenant_id,
        usage_observation_id=observation.usage_observation_id,
        session=_Session(),
    )

    assert own == observation

    with pytest.raises(
        LegalEvidenceUsageObservationNotFoundError,
        match="L10A2Q_P3B_OBSERVATION_NOT_FOUND",
    ):
        registry.get(
            tenant_id="tenant-neighbor",
            usage_observation_id=observation.usage_observation_id,
            session=_Session(),
        )


def test_unknown_persisted_field_is_corruption() -> None:
    collection = _Collection()
    registry = LegalEvidenceUsageObservationRegistry(collection)
    observation = _observation()

    registry.create_or_replay(
        observation,
        idempotency_key="idem-p3b-corrupt",
        session=_Session(),
    )

    collection.rows[0]["quota"] = 1

    with pytest.raises(
        LegalEvidenceUsageObservationRegistryError,
        match="L10A2Q_P3B_CORRUPT_OBSERVATION",
    ):
        registry.get(
            tenant_id=observation.tenant_id,
            usage_observation_id=observation.usage_observation_id,
            session=_Session(),
        )


def test_durable_surface_contains_no_capacity_or_financial_authority() -> None:
    collection = _Collection()
    registry = LegalEvidenceUsageObservationRegistry(collection)
    observation = _observation()

    registry.create_or_replay(
        observation,
        idempotency_key="idem-p3b-authority",
        session=_Session(),
    )

    keys = set(collection.rows[0])

    forbidden = {
        "remaining_storage_bytes",
        "remaining_ingress_bytes",
        "quota",
        "capacity_limit",
        "reservation_id",
        "admitted",
        "price",
        "amount",
        "currency",
        "invoice",
        "payment",
        "settlement",
        "execution",
        "overage",
    }

    assert forbidden.isdisjoint(keys)


# ARTIFACT: test_legal_evidence_usage_observation_registry.py
# VERSION: v1.0.0-L10A2Q-P3B-LEGAL-EVIDENCE-USAGE-OBSERVATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: append-only raw usage-observation durability only
# TENANT POSTURE: exact tenant identity/read/replay scope
# TRANSACTION POSTURE: caller-owned active transaction required
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
