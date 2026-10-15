"""WILSY OS durable privileged break-glass command evidence registry.

TITLE: Privileged Break-Glass Command Evidence Registry
VERSION: v1.0.0-P7-PRIVILEGED-BREAK-GLASS-EVIDENCE-REGISTRY
AUTHORITY: Wilsy OS Sovereign IAM
EPITOME: Persist exact immutable P7 dual-control evidence with replay integrity.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/privileged_break_glass_command_evidence_registry.py
COLLABORATION / OWNERSHIP: P7 registry only; callers own transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes no-TTL immutable evidence persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Persists sealed references only; no credentials or narrative.
TENANT BOUNDARY: Every replay lookup binds exact requester and idempotency scope.
AUTHORITY BOUNDARY: Persistence only; no permission, activation, approval, or use authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes finance.
"""
from __future__ import annotations

import hmac
from typing import Any, Final, Mapping

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.privileged_break_glass_command_evidence import (
    PrivilegedBreakGlassCommandEvidence,
    PrivilegedBreakGlassCommandEvidenceError,
)

VERSION: Final[str] = "v1.0.0-P7-PRIVILEGED-BREAK-GLASS-EVIDENCE-REGISTRY"
COLLECTION: Final[str] = "privileged_break_glass_command_evidence"
EVIDENCE_ID_INDEX: Final[str] = "privileged_break_glass_evidence_id_unique"
REQUESTER_IDEMPOTENCY_INDEX: Final[str] = "privileged_break_glass_requester_idempotency_unique"
TARGET_HISTORY_INDEX: Final[str] = "privileged_break_glass_target_history"


class PrivilegedBreakGlassEvidenceRegistryError(RuntimeError):
    """Base bounded P7 persistence failure."""


class PrivilegedBreakGlassEvidenceTransactionRequiredError(PrivilegedBreakGlassEvidenceRegistryError):
    """Caller did not provide an already-active transaction."""


class PrivilegedBreakGlassEvidenceConflictError(PrivilegedBreakGlassEvidenceRegistryError):
    """Immutable replay or uniqueness semantics conflict."""


class PrivilegedBreakGlassEvidencePersistedInvalidError(PrivilegedBreakGlassEvidenceRegistryError):
    """Persisted P7 evidence is malformed or cryptographically corrupt."""


def _tx(session: object) -> object:
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        raise PrivilegedBreakGlassEvidenceTransactionRequiredError("ACTIVE_TRANSACTION_REQUIRED") from error
    if active is not True:
        raise PrivilegedBreakGlassEvidenceTransactionRequiredError("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or "*" in value:
        raise PrivilegedBreakGlassEvidenceRegistryError(name + "_INVALID")
    return value


def _hydrate(row: object) -> PrivilegedBreakGlassCommandEvidence:
    if not isinstance(row, Mapping):
        raise PrivilegedBreakGlassEvidencePersistedInvalidError("PERSISTED_RECORD_INVALID")
    try:
        return PrivilegedBreakGlassCommandEvidence.from_document(row)
    except (KeyError, TypeError, ValueError, PrivilegedBreakGlassCommandEvidenceError) as error:
        raise PrivilegedBreakGlassEvidencePersistedInvalidError("PERSISTED_RECORD_INVALID") from error


class PrivilegedBreakGlassCommandEvidenceRegistry:
    """Immutable P7 evidence persistence with exact durable replay."""

    def __init__(self, collection: Any) -> None:
        """Bind one explicit Mongo-compatible collection."""
        if collection is None:
            raise PrivilegedBreakGlassEvidenceRegistryError("COLLECTION_REQUIRED")
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create three governed indexes and no TTL/delete/update surface."""
        specs = (
            ([('evidence_id', ASCENDING)], True, EVIDENCE_ID_INDEX),
            ([('requester_principal_id', ASCENDING), ('idempotency_key', ASCENDING)], True, REQUESTER_IDEMPOTENCY_INDEX),
            ([('target_class', ASCENDING), ('tenant_id', ASCENDING), ('requester_principal_id', ASCENDING), ('privileged_role_id', ASCENDING), ('authorized_at', ASCENDING)], False, TARGET_HISTORY_INDEX),
        )
        try:
            for keys, unique, name in specs:
                self._collection.create_index(keys, unique=unique, name=name)
        except (AttributeError, PyMongoError) as error:
            raise PrivilegedBreakGlassEvidenceRegistryError("INDEX_CREATION_FAILED") from error

    def get_by_requester_idempotency(self, *, requester_principal_id: str, idempotency_key: str, session: object) -> PrivilegedBreakGlassCommandEvidence | None:
        """Read one exact replay candidate inside the caller transaction."""
        tx = _tx(session)
        query = {"requester_principal_id": _text("REQUESTER_PRINCIPAL_ID", requester_principal_id), "idempotency_key": _text("IDEMPOTENCY_KEY", idempotency_key)}
        try:
            row = self._collection.find_one(query, session=tx)
        except (AttributeError, PyMongoError) as error:
            raise PrivilegedBreakGlassEvidenceRegistryError("PERSISTENCE_UNAVAILABLE") from error
        return None if row is None else _hydrate(row)

    def create_or_replay(self, evidence: PrivilegedBreakGlassCommandEvidence, *, session: object) -> PrivilegedBreakGlassCommandEvidence:
        """Insert immutable evidence or return the exact sealed replay."""
        tx = _tx(session)
        if type(evidence) is not PrivilegedBreakGlassCommandEvidence:
            raise PrivilegedBreakGlassEvidenceRegistryError("EVIDENCE_REQUIRED")
        existing = self.get_by_requester_idempotency(requester_principal_id=evidence.requester_principal_id, idempotency_key=evidence.idempotency_key, session=tx)
        if existing is not None:
            if existing == evidence and hmac.compare_digest(existing.evidence_fingerprint, evidence.evidence_fingerprint):
                return existing
            raise PrivilegedBreakGlassEvidenceConflictError("DIVERGENT_IDEMPOTENCY_REPLAY")
        try:
            self._collection.insert_one(evidence.to_document(), session=tx)
        except DuplicateKeyError as error:
            if error.has_error_label("TransientTransactionError"):
                raise
            raise PrivilegedBreakGlassEvidenceConflictError("DUPLICATE_KEY_CONFLICT") from error
        except AttributeError as error:
            raise PrivilegedBreakGlassEvidenceRegistryError("PERSISTENCE_UNAVAILABLE") from error
        except PyMongoError as error:
            if error.has_error_label("TransientTransactionError"):
                raise
            raise PrivilegedBreakGlassEvidenceRegistryError("PERSISTENCE_UNAVAILABLE") from error
        return evidence


__all__ = ["VERSION", "COLLECTION", "EVIDENCE_ID_INDEX", "REQUESTER_IDEMPOTENCY_INDEX", "TARGET_HISTORY_INDEX", "PrivilegedBreakGlassEvidenceRegistryError", "PrivilegedBreakGlassEvidenceTransactionRequiredError", "PrivilegedBreakGlassEvidenceConflictError", "PrivilegedBreakGlassEvidencePersistedInvalidError", "PrivilegedBreakGlassCommandEvidenceRegistry"]

# ARTIFACT: privileged_break_glass_command_evidence_registry.py
# VERSION: v1.0.0-P7-PRIVILEGED-BREAK-GLASS-EVIDENCE-REGISTRY
# AUTHORITY BOUNDARY: immutable evidence persistence and exact replay only
# TENANT POSTURE: exact requester, target class, and tenant scope
# FAIL-CLOSED POSTURE: inactive transaction, corruption, divergence, collision, and outage reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
