from __future__ import annotations

from typing import Any

import pytest

from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_idempotency_registry import (
    INDEX_NAME,
    LegalEvidenceReconciliationOperationIdempotencyConflict,
    LegalEvidenceReconciliationOperationIdempotencyRegistry,
    LegalEvidenceReconciliationOperationIdempotencyError,
)


class _Collection:
    def __init__(self) -> None:
        self.indexes: list[tuple[Any, ...]] = []
        self.rows: dict[tuple[str, str], dict[str, Any]] = {}

    def create_index(self, keys, *, unique, name):
        self.indexes.append((keys, unique, name))
        return name

    def find_one(self, query, *, session):
        return self.rows.get((query["service_id"], query["idempotency_key"]))

    def insert_one(self, document, *, session):
        key = (document["service_id"], document["idempotency_key"])
        if key in self.rows:
            raise RuntimeError("duplicate operation key")
        self.rows[key] = dict(document)


class _Session:
    in_transaction = True


def test_registry_provisions_compound_unique_service_operation_index() -> None:
    collection = _Collection()
    registry = LegalEvidenceReconciliationOperationIdempotencyRegistry(collection)
    registry.ensure_indexes()
    assert collection.indexes == [
        ([("service_id", 1), ("idempotency_key", 1)], True, INDEX_NAME)
    ]


def test_registry_replays_exact_result_and_rejects_changed_request_fingerprint() -> None:
    collection = _Collection()
    registry = LegalEvidenceReconciliationOperationIdempotencyRegistry(collection)
    response = {"coverage_verification_fingerprint": "coverage-fp", "completed_observation_count": 4}
    registry.record(
        service_id="trusted-workload",
        idempotency_key="operation-1",
        request_fingerprint="request-fp",
        response=response,
        session=_Session(),
    )
    assert registry.lookup(
        service_id="trusted-workload",
        idempotency_key="operation-1",
        request_fingerprint="request-fp",
        session=_Session(),
    ) == response
    with pytest.raises(
        LegalEvidenceReconciliationOperationIdempotencyConflict,
        match="RECONCILIATION_OPERATION_IDEMPOTENCY_CONFLICT",
    ):
        registry.lookup(
            service_id="trusted-workload",
            idempotency_key="operation-1",
            request_fingerprint="different-request-fp",
            session=_Session(),
        )


def test_registry_requires_active_caller_transaction() -> None:
    registry = LegalEvidenceReconciliationOperationIdempotencyRegistry(_Collection())
    with pytest.raises(
        LegalEvidenceReconciliationOperationIdempotencyError,
        match="RECONCILIATION_OPERATION_ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.lookup(
            service_id="trusted-workload",
            idempotency_key="operation-1",
            request_fingerprint="request-fp",
            session=object(),
        )
