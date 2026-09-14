"""Durable registry for terminal service-attempt outcome evidence.

TITLE: Wilsy OS Process-Service Attempt Outcome Registry
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist immutable P5E outcome decisions with strict hydration,
         tenant isolation, replay, and divergence rejection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/process_service_attempt_outcome_registry.py
COLLABORATION / OWNERSHIP: P5E persistence only; P1 remains lifecycle and
                            ServiceExecution authority; callers own transactions.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-REGISTRY
           establishes append-only tenant-scoped terminal-outcome evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: All reads and writes are tenant-scoped; foreign evidence is absent.
AUTHORITY BOUNDARY: Persistence/hydration only; no lifecycle or execution derivation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Corruption, unsupported schema, replay divergence,
                         duplicate races, and outages reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.process_service_attempt_outcome_authority import (
    ProcessServiceAttemptOutcomeAuthorityError,
    ProcessServiceAttemptOutcomeDecision,
    hydrate_process_service_attempt_outcome_decision,
)

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-REGISTRY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-ATTEMPT-OUTCOME-REGISTRY/V1"
COLLECTION: Final[str] = "process_service_attempt_outcome_evidence"
_ENTITY = "ProcessServiceAttemptOutcomeEvidence"
_FIELDS = frozenset({"schema", "version", "entity_type", "tenant_id", "attempt_id", "evidence_identity", "decision_payload", "decision_fingerprint"})


class ProcessServiceAttemptOutcomeRegistryError(RuntimeError):
    """Stable fail-closed terminal-outcome registry error."""

    def __init__(self, code: str) -> None:
        """Create one governed registry error."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = ProcessServiceAttemptOutcomeRegistryError(code)
    if cause is None:
        raise error
    raise error from cause


def _record(decision: ProcessServiceAttemptOutcomeDecision) -> dict[str, object]:
    return {"schema": SCHEMA, "version": VERSION, "entity_type": _ENTITY, "tenant_id": decision.tenant_id, "attempt_id": decision.attempt_id, "evidence_identity": decision.evidence_identity, "decision_payload": decision.to_dict(), "decision_fingerprint": decision.fingerprint}


def _canonical(raw: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(raw)
    value.pop("_id", None)
    return value


def _active(session: object) -> bool:
    marker = getattr(session, "in_transaction", False)
    try:
        return bool(marker() if callable(marker) else marker)
    except Exception:
        return False


def _hydrate(raw: Mapping[str, Any], tenant_id: str) -> ProcessServiceAttemptOutcomeDecision:
    value = _canonical(raw)
    if set(value) != _FIELDS:
        _fail("P5E_RECORD_SCHEMA_INVALID")
    if value["schema"] != SCHEMA or value["version"] != VERSION or value["entity_type"] != _ENTITY:
        _fail("P5E_RECORD_VERSION_UNSUPPORTED")
    if value["tenant_id"] != tenant_id:
        _fail("P5E_TENANT_MISMATCH")
    if not isinstance(value["attempt_id"], str) or not isinstance(value["evidence_identity"], str) or not isinstance(value["decision_payload"], Mapping) or not isinstance(value["decision_fingerprint"], str):
        _fail("P5E_RECORD_PAYLOAD_INVALID")
    try:
        decision = hydrate_process_service_attempt_outcome_decision(value["decision_payload"])
    except ProcessServiceAttemptOutcomeAuthorityError as error:
        _fail("P5E_RECORD_PAYLOAD_INVALID", error)
    if decision.tenant_id != tenant_id or decision.attempt_id != value["attempt_id"] or decision.evidence_identity != value["evidence_identity"]:
        _fail("P5E_RECORD_BINDING_INVALID")
    if decision.fingerprint != value["decision_fingerprint"]:
        _fail("P5E_RECORD_FINGERPRINT_INVALID")
    return decision


class ProcessServiceAttemptOutcomeRegistry:
    """Persist immutable terminal-outcome decisions with caller-owned transactions."""

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create tenant-scoped unique evidence and attempt indexes."""
        try:
            collection.create_index([("tenant_id", 1), ("evidence_identity", 1)], unique=True, name="process_service_attempt_outcome_evidence_unique")
            collection.create_index([("tenant_id", 1), ("attempt_id", 1)], unique=True, name="process_service_attempt_outcome_attempt_unique")
        except PyMongoError as error:
            _fail("P5E_PERSISTENCE_UNAVAILABLE", error)

    @staticmethod
    def persist(decision: ProcessServiceAttemptOutcomeDecision, collection: Any, *, session: object = None) -> ProcessServiceAttemptOutcomeDecision:
        """Persist one outcome or return exact replay; never owns transaction lifecycle."""
        if type(decision) is not ProcessServiceAttemptOutcomeDecision:
            _fail("P5E_DECISION_REQUIRED")
        try:
            decision.__post_init__()
        except ProcessServiceAttemptOutcomeAuthorityError as error:
            _fail("P5E_DECISION_INVALID", error)
        record = _record(decision)
        query = {"tenant_id": decision.tenant_id, "evidence_identity": decision.evidence_identity}
        try:
            existing = collection.find_one(query, session=session)
        except PyMongoError as error:
            _fail("P5E_PERSISTENCE_UNAVAILABLE", error)
        if existing is not None:
            current = _hydrate(existing, decision.tenant_id)
            if _canonical(existing) == record:
                return current
            _fail("P5E_REPLAY_CONFLICT")
        try:
            by_attempt = collection.find_one({"tenant_id": decision.tenant_id, "attempt_id": decision.attempt_id}, session=session)
        except PyMongoError as error:
            _fail("P5E_PERSISTENCE_UNAVAILABLE", error)
        if by_attempt is not None:
            _hydrate(by_attempt, decision.tenant_id)
            _fail("P5E_REPLAY_CONFLICT")
        try:
            collection.insert_one(record, session=session)
        except DuplicateKeyError as error:
            if _active(session):
                _fail("P5E_RETRY_TRANSACTION_REQUIRED", error)
            try:
                raced = collection.find_one(query, session=session)
            except PyMongoError as read_error:
                _fail("P5E_PERSISTENCE_UNAVAILABLE", read_error)
            if raced is not None:
                current = _hydrate(raced, decision.tenant_id)
                if _canonical(raced) == record:
                    return current
            _fail("P5E_REPLAY_CONFLICT", error)
        except PyMongoError as error:
            if _active(session) and error.has_error_label("TransientTransactionError") and not error.has_error_label("UnknownTransactionCommitResult"):
                _fail("P5E_RETRY_TRANSACTION_REQUIRED", error)
            _fail("P5E_PERSISTENCE_UNAVAILABLE", error)
        return _hydrate(record, decision.tenant_id)

    @staticmethod
    def get(tenant_id: str, evidence_identity: str, collection: Any, *, session: object = None) -> ProcessServiceAttemptOutcomeDecision:
        """Hydrate one exact tenant-scoped durable outcome identity."""
        if not isinstance(tenant_id, str) or not tenant_id.strip() or tenant_id.casefold() in {"default", "global", "global_root", "root", "master", "*"}:
            _fail("P5E_TENANT_INVALID")
        if not isinstance(evidence_identity, str) or len(evidence_identity) != 128 or any(char not in "0123456789abcdef" for char in evidence_identity):
            _fail("P5E_EVIDENCE_IDENTITY_INVALID")
        try:
            raw = collection.find_one({"tenant_id": tenant_id, "evidence_identity": evidence_identity}, session=session)
        except PyMongoError as error:
            _fail("P5E_PERSISTENCE_UNAVAILABLE", error)
        if raw is None:
            _fail("P5E_EVIDENCE_NOT_FOUND")
        return _hydrate(cast(Mapping[str, Any], raw), tenant_id)


__all__ = ["COLLECTION", "SCHEMA", "VERSION", "ProcessServiceAttemptOutcomeRegistry", "ProcessServiceAttemptOutcomeRegistryError"]


# ARTIFACT: process_service_attempt_outcome_registry.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-REGISTRY
# AUTHORITY BOUNDARY: immutable terminal-outcome evidence persistence only.
# TENANT POSTURE: every operation is explicitly tenant-scoped.
# FAIL-CLOSED POSTURE: corruption, divergence, races, and outages reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
