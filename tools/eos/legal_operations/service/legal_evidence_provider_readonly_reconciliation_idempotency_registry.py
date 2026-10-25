"""Durable, transaction-bound idempotent result replay for reconciliation."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING
from pymongo.errors import PyMongoError

COLLECTION = "legal_evidence_provider_reconciliation_operations"
INDEX_NAME = "legal_evidence_reconciliation_operation_idempotency_unique"


class LegalEvidenceReconciliationOperationIdempotencyError(RuntimeError):
    """Base fail-closed operation-result registry error."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class LegalEvidenceReconciliationOperationIdempotencyConflict(
    LegalEvidenceReconciliationOperationIdempotencyError
):
    """The same caller-scoped key was reused for different operation material."""


def _active_session(session: object) -> object:
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise LegalEvidenceReconciliationOperationIdempotencyError(
            "RECONCILIATION_OPERATION_ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


class LegalEvidenceReconciliationOperationIdempotencyRegistry:
    """Store one response per authenticated service/key inside the business txn.

    The ledger stores only the bounded read-only reconciliation summary. It
    never stores provider object content or grants authority. Unique-key races
    fail the caller transaction; a retry then reads the committed exact result.
    """

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        if collection is None or not callable(getattr(collection, "find_one", None)):
            raise LegalEvidenceReconciliationOperationIdempotencyError(
                "RECONCILIATION_OPERATION_COLLECTION_REQUIRED"
            )
        self._collection = collection

    def ensure_indexes(self) -> None:
        try:
            self._collection.create_index(
                [("service_id", ASCENDING), ("idempotency_key", ASCENDING)],
                unique=True,
                name=INDEX_NAME,
            )
        except PyMongoError as error:
            raise LegalEvidenceReconciliationOperationIdempotencyError(
                "RECONCILIATION_OPERATION_INDEX_SETUP_FAILED"
            ) from error

    def lookup(
        self,
        *,
        service_id: str,
        idempotency_key: str,
        request_fingerprint: str,
        session: object,
    ) -> dict[str, Any] | None:
        tx = _active_session(session)
        try:
            row = self._collection.find_one(
                {"service_id": service_id, "idempotency_key": idempotency_key},
                session=tx,
            )
        except PyMongoError as error:
            raise LegalEvidenceReconciliationOperationIdempotencyError(
                "RECONCILIATION_OPERATION_LOOKUP_FAILED"
            ) from error
        if row is None:
            return None
        if row.get("request_fingerprint") != request_fingerprint:
            raise LegalEvidenceReconciliationOperationIdempotencyConflict(
                "RECONCILIATION_OPERATION_IDEMPOTENCY_CONFLICT"
            )
        response = row.get("response")
        if not isinstance(response, Mapping) or not isinstance(response.get("coverage_verification_fingerprint"), str):
            raise LegalEvidenceReconciliationOperationIdempotencyError(
                "RECONCILIATION_OPERATION_RESULT_INVALID"
            )
        return dict(response)

    def record(
        self,
        *,
        service_id: str,
        idempotency_key: str,
        request_fingerprint: str,
        response: Mapping[str, Any],
        session: object,
    ) -> None:
        tx = _active_session(session)
        document = {
            "service_id": service_id,
            "idempotency_key": idempotency_key,
            "request_fingerprint": request_fingerprint,
            "response": dict(response),
            "created_at": datetime.now(timezone.utc),
        }
        try:
            self._collection.insert_one(document, session=tx)
        except PyMongoError as error:
            # A unique-key race is not resolved inside the failed transaction.
            # The caller aborts; the next retry resolves the committed record.
            raise LegalEvidenceReconciliationOperationIdempotencyError(
                "RECONCILIATION_OPERATION_RESULT_PERSISTENCE_FAILED"
            ) from error


__all__ = [
    "COLLECTION",
    "INDEX_NAME",
    "LegalEvidenceReconciliationOperationIdempotencyError",
    "LegalEvidenceReconciliationOperationIdempotencyConflict",
    "LegalEvidenceReconciliationOperationIdempotencyRegistry",
]
