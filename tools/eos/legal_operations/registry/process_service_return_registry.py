"""Durable registry for immutable return-generation authority.

TITLE: Wilsy OS Process-Service Return Registry
VERSION: v1.0.0-PROCESS-SERVICE-RETURN-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist strict, tenant-scoped return authority receipts without
         deriving or mutating legal lifecycle or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/process_service_return_registry.py
COLLABORATION / OWNERSHIP: P5F persistence only; P1 owns ReturnOfService,
                            P2 owns snapshots; caller owns transactions.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-RETURN-REGISTRY establishes
           append-only return authority persistence and strict hydration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: All operations are tenant-scoped and foreign records are absent.
AUTHORITY BOUNDARY: Return authority persistence/hydration only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Corruption, divergence, races, and outages reject.
"""
from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Any, Final, NoReturn, cast

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.process_service_return_authority import ProcessServiceReturnAuthorityError, ProcessServiceReturnDecision, hydrate_process_service_return_decision

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-RETURN-REGISTRY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-RETURN-REGISTRY/V1"
COLLECTION: Final[str] = "process_service_return_evidence"
_ENTITY = "ProcessServiceReturnEvidence"
_FIELDS = frozenset({"schema", "version", "entity_type", "tenant_id", "service_execution_id", "return_id", "evidence_identity", "decision_payload", "decision_fingerprint"})
_TENANT_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceReturnRegistryError(RuntimeError):
    """Stable fail-closed return registry error."""

    def __init__(self, code: str) -> None:
        """Create one governed registry error."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = ProcessServiceReturnRegistryError(code)
    if cause is None:
        raise error
    raise error from cause


def _record(decision: ProcessServiceReturnDecision) -> dict[str, object]:
    return {"schema": SCHEMA, "version": VERSION, "entity_type": _ENTITY, "tenant_id": decision.tenant_id, "service_execution_id": decision.service_execution_id, "return_id": decision.return_id, "evidence_identity": decision.evidence_identity, "decision_payload": decision.to_dict(), "decision_fingerprint": decision.fingerprint}


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


def _hydrate(raw: Mapping[str, Any], tenant_id: str) -> ProcessServiceReturnDecision:
    value = _canonical(raw)
    if set(value) != _FIELDS:
        _fail("P5F_RECORD_SCHEMA_INVALID")
    if value["schema"] != SCHEMA or value["version"] != VERSION or value["entity_type"] != _ENTITY:
        _fail("P5F_RECORD_VERSION_UNSUPPORTED")
    if value["tenant_id"] != tenant_id:
        _fail("P5F_TENANT_MISMATCH")
    if not isinstance(value["service_execution_id"], str) or not isinstance(value["return_id"], str) or not isinstance(value["evidence_identity"], str) or not isinstance(value["decision_payload"], Mapping) or not isinstance(value["decision_fingerprint"], str):
        _fail("P5F_RECORD_PAYLOAD_INVALID")
    try:
        decision = hydrate_process_service_return_decision(value["decision_payload"])
    except ProcessServiceReturnAuthorityError as error:
        _fail("P5F_RECORD_PAYLOAD_INVALID", error)
    if decision.tenant_id != tenant_id or decision.service_execution_id != value["service_execution_id"] or decision.return_id != value["return_id"] or decision.evidence_identity != value["evidence_identity"]:
        _fail("P5F_RECORD_BINDING_INVALID")
    if decision.fingerprint != value["decision_fingerprint"]:
        _fail("P5F_RECORD_FINGERPRINT_INVALID")
    return decision


class ProcessServiceReturnRegistry:
    """Persist immutable return decisions with caller-owned Mongo boundaries."""

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create tenant-scoped unique return and evidence identities."""
        try:
            collection.create_index([("tenant_id", 1), ("evidence_identity", 1)], unique=True, name="process_service_return_evidence_unique")
            collection.create_index([("tenant_id", 1), ("return_id", 1)], unique=True, name="process_service_return_id_unique")
        except PyMongoError as error:
            _fail("P5F_PERSISTENCE_UNAVAILABLE", error)

    @staticmethod
    def persist(decision: ProcessServiceReturnDecision, collection: Any, *, session: object = None) -> ProcessServiceReturnDecision:
        """Persist one return decision or return exact replay; never owns a transaction."""
        if type(decision) is not ProcessServiceReturnDecision:
            _fail("P5F_DECISION_REQUIRED")
        try:
            decision.__post_init__()
        except ProcessServiceReturnAuthorityError as error:
            _fail("P5F_DECISION_INVALID", error)
        record = _record(decision)
        query = {"tenant_id": decision.tenant_id, "evidence_identity": decision.evidence_identity}
        try:
            existing = collection.find_one(query, session=session)
        except PyMongoError as error:
            _fail("P5F_PERSISTENCE_UNAVAILABLE", error)
        if existing is not None:
            current = _hydrate(existing, decision.tenant_id)
            if _canonical(existing) == record:
                return current
            _fail("P5F_REPLAY_CONFLICT")
        try:
            by_return = collection.find_one({"tenant_id": decision.tenant_id, "return_id": decision.return_id}, session=session)
        except PyMongoError as error:
            _fail("P5F_PERSISTENCE_UNAVAILABLE", error)
        if by_return is not None:
            _hydrate(by_return, decision.tenant_id)
            _fail("P5F_REPLAY_CONFLICT")
        try:
            collection.insert_one(record, session=session)
        except DuplicateKeyError as error:
            if _active(session):
                _fail("P5F_RETRY_TRANSACTION_REQUIRED", error)
            try:
                raced = collection.find_one(query, session=session)
            except PyMongoError as read_error:
                _fail("P5F_PERSISTENCE_UNAVAILABLE", read_error)
            if raced is not None:
                current = _hydrate(raced, decision.tenant_id)
                if _canonical(raced) == record:
                    return current
            _fail("P5F_REPLAY_CONFLICT", error)
        except PyMongoError as error:
            if _active(session) and error.has_error_label("TransientTransactionError") and not error.has_error_label("UnknownTransactionCommitResult"):
                _fail("P5F_RETRY_TRANSACTION_REQUIRED", error)
            _fail("P5F_PERSISTENCE_UNAVAILABLE", error)
        return _hydrate(record, decision.tenant_id)

    @staticmethod
    def get(tenant_id: str, evidence_identity: str, collection: Any, *, session: object = None) -> ProcessServiceReturnDecision:
        """Hydrate one exact tenant-scoped return authority identity."""
        if not isinstance(tenant_id, str) or tenant_id != tenant_id.strip() or _TENANT_IDENTITY.fullmatch(tenant_id) is None or tenant_id.casefold() in _FORBIDDEN_TENANTS:
            _fail("P5F_TENANT_INVALID")
        if not isinstance(evidence_identity, str) or len(evidence_identity) != 128 or any(char not in "0123456789abcdef" for char in evidence_identity):
            _fail("P5F_EVIDENCE_IDENTITY_INVALID")
        try:
            raw = collection.find_one({"tenant_id": tenant_id, "evidence_identity": evidence_identity}, session=session)
        except PyMongoError as error:
            _fail("P5F_PERSISTENCE_UNAVAILABLE", error)
        if raw is None:
            _fail("P5F_EVIDENCE_NOT_FOUND")
        return _hydrate(cast(Mapping[str, Any], raw), tenant_id)


__all__ = ["COLLECTION", "SCHEMA", "VERSION", "ProcessServiceReturnRegistry", "ProcessServiceReturnRegistryError"]


# ARTIFACT: process_service_return_registry.py
# VERSION: v1.0.0-PROCESS-SERVICE-RETURN-REGISTRY
# AUTHORITY BOUNDARY: immutable return authority persistence and hydration only.
# TENANT POSTURE: every operation is explicitly tenant-scoped.
# FAIL-CLOSED POSTURE: corruption, divergence, races, and outages reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
