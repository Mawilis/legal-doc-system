"""Durable registry for evidence-backed ALLOCATED -> ATTEMPTED transitions.

TITLE: Wilsy OS Process-Service Attempt Transition Registry
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist immutable P5D field-attempt evidence while keeping P1 lifecycle
         and P2 snapshot persistence authoritative.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/process_service_attempt_transition_registry.py
COLLABORATION / OWNERSHIP: Caller supplies collection, session, and transaction;
                            this registry owns no Mongo client or transaction.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-REGISTRY
           establishes strict tenant-scoped immutable transition evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every read and write is tenant-scoped; foreign evidence is absent.
AUTHORITY BOUNDARY: Persistence and hydration only; no lifecycle derivation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Schema drift, malformed evidence, replay divergence,
                         duplicate races, and persistence outages reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.process_service_attempt_transition_authority import (
    ProcessServiceAttemptTransitionDecision,
    ProcessServiceAttemptTransitionAuthorityError,
    hydrate_process_service_attempt_transition_decision,
)

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-REGISTRY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-ATTEMPT-TRANSITION-REGISTRY/V1"
COLLECTION: Final[str] = "process_service_attempt_transition_evidence"
_ENTITY = "ProcessServiceAttemptTransitionEvidence"
_FIELDS = frozenset({"schema", "version", "entity_type", "tenant_id", "attempt_id", "evidence_identity", "decision_payload", "decision_fingerprint"})


class ProcessServiceAttemptTransitionRegistryError(RuntimeError):
    """Stable fail-closed P5D persistence, hydration, and replay error."""

    def __init__(self, code: str) -> None:
        """Create one governed error with a stable code."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one registry error, retaining technical causes only as context."""
    error = ProcessServiceAttemptTransitionRegistryError(code)
    if cause is None:
        raise error
    raise error from cause


def _record(decision: ProcessServiceAttemptTransitionDecision) -> dict[str, object]:
    """Build the complete immutable durable envelope."""
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "entity_type": _ENTITY,
        "tenant_id": decision.tenant_id,
        "attempt_id": decision.attempt_id,
        "evidence_identity": decision.evidence_identity,
        "decision_payload": decision.to_dict(),
        "decision_fingerprint": decision.fingerprint,
    }


def _canonical(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Return a record without Mongo transport metadata."""
    value = dict(raw)
    value.pop("_id", None)
    return value


def _hydrate(raw: Mapping[str, Any], tenant_id: str) -> ProcessServiceAttemptTransitionDecision:
    """Strictly hydrate and verify one tenant-scoped durable record."""
    value = _canonical(raw)
    if set(value) != _FIELDS:
        _fail("P5D_RECORD_SCHEMA_INVALID")
    if value["schema"] != SCHEMA or value["version"] != VERSION or value["entity_type"] != _ENTITY:
        _fail("P5D_RECORD_VERSION_UNSUPPORTED")
    if value["tenant_id"] != tenant_id:
        _fail("P5D_TENANT_MISMATCH")
    if not isinstance(value["attempt_id"], str) or not isinstance(value["evidence_identity"], str):
        _fail("P5D_RECORD_IDENTITY_INVALID")
    if not isinstance(value["decision_payload"], Mapping) or not isinstance(value["decision_fingerprint"], str):
        _fail("P5D_RECORD_PAYLOAD_INVALID")
    try:
        decision = hydrate_process_service_attempt_transition_decision(value["decision_payload"])
    except ProcessServiceAttemptTransitionAuthorityError as error:
        _fail("P5D_RECORD_PAYLOAD_INVALID", error)
    if decision.tenant_id != tenant_id or decision.attempt_id != value["attempt_id"] or decision.evidence_identity != value["evidence_identity"]:
        _fail("P5D_RECORD_BINDING_INVALID")
    if decision.fingerprint != value["decision_fingerprint"]:
        _fail("P5D_RECORD_FINGERPRINT_INVALID")
    return decision


def _active(session: object) -> bool:
    marker = getattr(session, "in_transaction", False)
    try:
        return bool(marker() if callable(marker) else marker)
    except Exception:
        return False


class ProcessServiceAttemptTransitionRegistry:
    """Persist immutable P5D evidence under caller-owned Mongo boundaries."""

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create deterministic tenant-scoped uniqueness indexes."""
        try:
            collection.create_index([("tenant_id", 1), ("evidence_identity", 1)], unique=True, name="process_service_attempt_transition_evidence_unique")
            collection.create_index([("tenant_id", 1), ("attempt_id", 1)], unique=True, name="process_service_attempt_transition_attempt_unique")
        except PyMongoError as error:
            _fail("P5D_PERSISTENCE_UNAVAILABLE", error)

    @staticmethod
    def persist(decision: ProcessServiceAttemptTransitionDecision, collection: Any, *, session: object = None) -> ProcessServiceAttemptTransitionDecision:
        """Persist one decision or return exact replay; never owns transactions."""
        if type(decision) is not ProcessServiceAttemptTransitionDecision:
            _fail("P5D_DECISION_REQUIRED")
        try:
            decision.__post_init__()
        except ProcessServiceAttemptTransitionAuthorityError as error:
            _fail("P5D_DECISION_INVALID", error)
        record = _record(decision)
        query = {"tenant_id": decision.tenant_id, "evidence_identity": decision.evidence_identity}
        try:
            existing = collection.find_one(query, session=session)
        except PyMongoError as error:
            _fail("P5D_PERSISTENCE_UNAVAILABLE", error)
        if existing is not None:
            current = _hydrate(existing, decision.tenant_id)
            if _canonical(existing) == record:
                return current
            _fail("P5D_REPLAY_CONFLICT")
        try:
            by_attempt = collection.find_one({"tenant_id": decision.tenant_id, "attempt_id": decision.attempt_id}, session=session)
        except PyMongoError as error:
            _fail("P5D_PERSISTENCE_UNAVAILABLE", error)
        if by_attempt is not None:
            _hydrate(by_attempt, decision.tenant_id)
            _fail("P5D_REPLAY_CONFLICT")
        try:
            collection.insert_one(record, session=session)
        except DuplicateKeyError as error:
            if _active(session):
                _fail("P5D_RETRY_TRANSACTION_REQUIRED", error)
            try:
                raced = collection.find_one(query, session=session)
            except PyMongoError as read_error:
                _fail("P5D_PERSISTENCE_UNAVAILABLE", read_error)
            if raced is not None:
                current = _hydrate(raced, decision.tenant_id)
                if _canonical(raced) == record:
                    return current
            _fail("P5D_REPLAY_CONFLICT", error)
        except PyMongoError as error:
            if _active(session) and error.has_error_label("TransientTransactionError") and not error.has_error_label("UnknownTransactionCommitResult"):
                _fail("P5D_RETRY_TRANSACTION_REQUIRED", error)
            _fail("P5D_PERSISTENCE_UNAVAILABLE", error)
        return _hydrate(record, decision.tenant_id)

    @staticmethod
    def get(tenant_id: str, evidence_identity: str, collection: Any, *, session: object = None) -> ProcessServiceAttemptTransitionDecision:
        """Hydrate one exact tenant-scoped evidence identity."""
        if not isinstance(tenant_id, str) or not tenant_id.strip() or tenant_id.casefold() in {"default", "global", "global_root", "root", "master", "*"}:
            _fail("P5D_TENANT_INVALID")
        if not isinstance(evidence_identity, str) or len(evidence_identity) != 128 or any(char not in "0123456789abcdef" for char in evidence_identity):
            _fail("P5D_EVIDENCE_IDENTITY_INVALID")
        try:
            raw = collection.find_one({"tenant_id": tenant_id, "evidence_identity": evidence_identity}, session=session)
        except PyMongoError as error:
            _fail("P5D_PERSISTENCE_UNAVAILABLE", error)
        if raw is None:
            _fail("P5D_EVIDENCE_NOT_FOUND")
        return _hydrate(cast(Mapping[str, Any], raw), tenant_id)


__all__ = ["COLLECTION", "SCHEMA", "VERSION", "ProcessServiceAttemptTransitionRegistry", "ProcessServiceAttemptTransitionRegistryError"]


# ARTIFACT: process_service_attempt_transition_registry.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-REGISTRY
# AUTHORITY BOUNDARY: immutable P5D evidence persistence and hydration only.
# TENANT POSTURE: every operation is tenant-scoped and fail-closed.
# FAIL-CLOSED POSTURE: corruption, divergence, races, and outages reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
