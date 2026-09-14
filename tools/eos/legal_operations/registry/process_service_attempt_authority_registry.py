"""Durable tenant-scoped registry for process-service attempt authority.

TITLE: Wilsy OS Process-Service Attempt Authority Registry
VERSION: v1.1.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist immutable P5A attempt-authorization receipts with strict
         replay, hydration, tenant isolation, and caller-owned transactions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/process_service_attempt_authority_registry.py
COLLABORATION / OWNERSHIP: P5B owns durable P5A receipt persistence only;
                            P5A remains attempt-authorization evidence owner;
                            callers own Mongo sessions and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.1.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY
           extends the immutable P5B receipt and durable payload with the
           exact validated P5A allocation-evidence reference, preserving
           append-only replay, hydration, and transaction boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Stores opaque tenant, identity, and evidence
                             references only; no provider, credential,
                             location, or personal-data expansion.
TENANT BOUNDARY: Every query and persisted record is explicitly tenant-scoped;
                 foreign records are indistinguishable from absence.
AUTHORITY BOUNDARY: Append-only P5A receipt persistence and strict hydration
                    only. No ServiceAttempt, ServiceExecution, ReturnOfService,
                    custody, P1/P2/P4, IAM, transport, or currentness authority.
FINANCIAL AUTHORITY BOUNDARY: Attempt authorization is not billing, invoicing,
                              payment, execution, or settlement; Kennel EOS
                              exclusively owns financial execution and settlement.
TRANSACTION BOUNDARY: The caller must supply an already-active Mongo session
                      and transaction. This registry never starts, commits,
                      aborts, retries, or stores a Mongo client.
FAIL-CLOSED DECLARATION: Schema drift, malformed P5A evidence, replay or
                         identity divergence, duplicate rows, Mongo outages,
                         and transaction races reject through stable P5B errors.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, Callable, Final, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.process_service_attempt_authority import (
    SCHEMA as P5A_SCHEMA,
    VERSION as P5A_VERSION,
    ProcessServiceAttemptAuthorityDecision,
)


VERSION: Final[str] = "v1.1.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY"
RECEIPT_SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-ATTEMPT-AUTHORITY-RECEIPT/V1"
RECEIPT_COLLECTION: Final[str] = "process_service_attempt_authority_receipts"
AUTHORITY_INDEX_NAME: Final[str] = "process_service_attempt_tenant_authority_unique"
ATTEMPT_INDEX_NAME: Final[str] = "process_service_attempt_tenant_attempt_unique"
EVIDENCE_INDEX_NAME: Final[str] = "process_service_attempt_tenant_evidence_unique"
_RECORD_SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY/V1"
_RECORD_ENTITY: Final[str] = "ProcessServiceAttemptAuthorityReceiptRecord"
_RECEIPT_ENTITY: Final[str] = "ProcessServiceAttemptAuthorityReceipt"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})
_RECEIPT_SEMANTIC_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id",
    "attempt_authority_id",
    "attempt_id",
    "instruction_id",
    "document_id",
    "deputy_id",
    "allocation_command_id",
    "allocation_evidence_reference",
    "allocation_receipt_evidence_identity",
    "allocation_receipt_fingerprint",
    "allocation_current_fingerprint",
    "allocated_at",
    "authorized_at",
    "authority_decision_fingerprint",
)
_RECEIPT_PAYLOAD_FIELDS: Final[frozenset[str]] = frozenset(
    {"schema", "version", "entity_type", *_RECEIPT_SEMANTIC_FIELDS}
)
_RECORD_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "entity_type",
        "tenant_id",
        "attempt_authority_id",
        "attempt_id",
        "evidence_identity",
        "receipt_payload",
        "receipt_fingerprint",
        "authority_decision_fingerprint",
    }
)


class ProcessServiceAttemptAuthorityRegistryError(RuntimeError):
    """Base governed P5B persistence, replay, and hydration failure."""

    default_code = "P5B_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        """Create one deterministic error carrying its stable code."""
        self.code = code or self.default_code
        super().__init__(self.code)


class ProcessServiceAttemptAuthorityRegistryInputError(ProcessServiceAttemptAuthorityRegistryError):
    """Explicit caller input or dependency failed closed."""

    default_code = "P5B_INPUT_INVALID"


class ProcessServiceAttemptAuthorityRegistryTransactionRequiredError(ProcessServiceAttemptAuthorityRegistryError):
    """An already-active caller-owned transaction is required."""

    default_code = "P5B_ACTIVE_TRANSACTION_REQUIRED"


class ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError(ProcessServiceAttemptAuthorityRegistryError):
    """A durable record failed strict schema, source, or digest validation."""

    default_code = "P5B_PERSISTED_RECORD_INVALID"


class ProcessServiceAttemptAuthorityRegistryReceiptNotFoundError(ProcessServiceAttemptAuthorityRegistryError):
    """No receipt exists for the explicit tenant-scoped locator."""

    default_code = "P5B_ATTEMPT_AUTHORITY_NOT_FOUND"


class ProcessServiceAttemptAuthorityRegistryAuthorityIdentityConflictError(ProcessServiceAttemptAuthorityRegistryError):
    """An authority identity is already bound to divergent immutable evidence."""

    default_code = "P5B_ATTEMPT_AUTHORITY_IDENTITY_CONFLICT"


class ProcessServiceAttemptAuthorityRegistryAttemptIdentityConflictError(ProcessServiceAttemptAuthorityRegistryError):
    """An attempt identity is already bound to another authority receipt."""

    default_code = "P5B_ATTEMPT_IDENTITY_CONFLICT"


class ProcessServiceAttemptAuthorityRegistryPersistenceUnavailableError(ProcessServiceAttemptAuthorityRegistryError):
    """Mongo read, cursor, index, or insert access was unavailable."""

    default_code = "P5B_PERSISTENCE_UNAVAILABLE"


class ProcessServiceAttemptAuthorityRegistryRetryRequiredError(ProcessServiceAttemptAuthorityRegistryError):
    """A duplicate-key race requires the caller to restart the whole transaction."""

    default_code = "P5B_WHOLE_TRANSACTION_RETRY_REQUIRED"


def _raise(
    error_type: type[ProcessServiceAttemptAuthorityRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one structured P5B error, retaining technical cause only."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _digest(payload: object) -> str:
    """Hash deterministic canonical JSON with lowercase SHA3-512."""
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _identity(name: str, value: object, error_type: type[ProcessServiceAttemptAuthorityRegistryError]) -> str:
    """Validate one canonical opaque identity."""
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _raise(error_type, f"P5B_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object, error_type: type[ProcessServiceAttemptAuthorityRegistryError]) -> str:
    """Validate one explicit non-default tenant."""
    tenant = _identity("tenant_id", value, error_type)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _raise(error_type, "P5B_TENANT_INVALID")
    return tenant


def _fingerprint(name: str, value: object, error_type: type[ProcessServiceAttemptAuthorityRegistryError]) -> str:
    """Validate one lowercase 128-character SHA3-512 digest."""
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _raise(error_type, f"P5B_{name.upper()}_INVALID")
    return cast(str, value)


def _text(name: str, value: object, error_type: type[ProcessServiceAttemptAuthorityRegistryError]) -> str:
    """Validate one non-empty canonical text field."""
    if not isinstance(value, str) or not value or value != value.strip():
        _raise(error_type, f"P5B_{name.upper()}_INVALID")
    return value


def _utc(name: str, value: object, error_type: type[ProcessServiceAttemptAuthorityRegistryError]) -> datetime:
    """Require an aware UTC datetime."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        _raise(error_type, f"P5B_{name.upper()}_INVALID")
    return value


def _parse_utc(name: str, value: object) -> datetime:
    """Parse one persisted aware UTC timestamp."""
    if not isinstance(value, str):
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, f"P5B_{name.upper()}_INVALID")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, f"P5B_{name.upper()}_INVALID", error)
    return _utc(name, parsed, ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError)


def _canonical(value: object) -> object:
    """Convert supported receipt values to deterministic JSON primitives."""
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _receipt_payload(
    *,
    tenant_id: str,
    attempt_authority_id: str,
    attempt_id: str,
    instruction_id: str,
    document_id: str,
    deputy_id: str,
    allocation_command_id: str,
    allocation_evidence_reference: str,
    allocation_receipt_evidence_identity: str,
    allocation_receipt_fingerprint: str,
    allocation_current_fingerprint: str,
    allocated_at: datetime,
    authorized_at: datetime,
    authority_decision_fingerprint: str,
) -> dict[str, object]:
    """Build the complete immutable receipt payload."""
    return {
        "schema": RECEIPT_SCHEMA,
        "version": VERSION,
        "entity_type": _RECEIPT_ENTITY,
        "tenant_id": tenant_id,
        "attempt_authority_id": attempt_authority_id,
        "attempt_id": attempt_id,
        "instruction_id": instruction_id,
        "document_id": document_id,
        "deputy_id": deputy_id,
        "allocation_command_id": allocation_command_id,
        "allocation_evidence_reference": allocation_evidence_reference,
        "allocation_receipt_evidence_identity": allocation_receipt_evidence_identity,
        "allocation_receipt_fingerprint": allocation_receipt_fingerprint,
        "allocation_current_fingerprint": allocation_current_fingerprint,
        "allocated_at": _canonical(allocated_at),
        "authorized_at": _canonical(authorized_at),
        "authority_decision_fingerprint": authority_decision_fingerprint,
    }


def _p5a_payload_from_receipt(receipt: "ProcessServiceAttemptAuthorityReceipt") -> dict[str, object]:
    """Rebuild the public P5A payload for independent digest verification."""
    return {
        "schema": P5A_SCHEMA,
        "version": P5A_VERSION,
        "entity_type": "ProcessServiceAttemptAuthorityDecision",
        "tenant_id": receipt.tenant_id,
        "attempt_authority_id": receipt.attempt_authority_id,
        "attempt_id": receipt.attempt_id,
        "instruction_id": receipt.instruction_id,
        "document_id": receipt.document_id,
        "deputy_id": receipt.deputy_id,
        "allocation_command_id": receipt.allocation_command_id,
        "allocation_evidence_reference": receipt.allocation_evidence_reference,
        "allocation_receipt_evidence_identity": receipt.allocation_receipt_evidence_identity,
        "allocation_receipt_fingerprint": receipt.allocation_receipt_fingerprint,
        "allocation_current_fingerprint": receipt.allocation_current_fingerprint,
        "allocated_at": receipt.allocated_at.isoformat(),
        "authorized_at": receipt.authorized_at.isoformat(),
    }


def _make_receipt_proof_contract() -> tuple[Callable[[str], object], Callable[[object], bool], Callable[[object], str | None]]:
    """Create a private proof contract for registry-derived receipts."""

    @dataclass(frozen=True, slots=True)
    class _ReceiptProof:
        payload_digest: str

    def issue(payload_digest: str) -> object:
        return _ReceiptProof(payload_digest)

    def validate(value: object) -> bool:
        return isinstance(value, _ReceiptProof)

    def digest(value: object) -> str | None:
        if not isinstance(value, _ReceiptProof):
            return None
        return value.payload_digest

    return issue, validate, digest


_issue_receipt_proof, _is_receipt_proof, _receipt_proof_digest = _make_receipt_proof_contract()


@dataclass(frozen=True, slots=True)
class ProcessServiceAttemptAuthorityReceipt:
    """Immutable tenant-scoped P5B receipt derived from one P5A decision.

    The private proof prevents ordinary caller construction from manufacturing
    durable authority. Registry persistence derives every field from a
    validated ``ProcessServiceAttemptAuthorityDecision``. The receipt records
    evidence only; it does not create a ServiceAttempt, service, custody,
    invoice, payment, execution, or settlement fact.
    """

    tenant_id: str
    attempt_authority_id: str
    attempt_id: str
    instruction_id: str
    document_id: str
    deputy_id: str
    allocation_command_id: str
    allocation_evidence_reference: str
    allocation_receipt_evidence_identity: str
    allocation_receipt_fingerprint: str
    allocation_current_fingerprint: str
    allocated_at: datetime
    authorized_at: datetime
    authority_decision_fingerprint: str
    _construction_proof: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Validate immutable receipt shape and its private payload proof."""
        if not _is_receipt_proof(self._construction_proof):
            _raise(ProcessServiceAttemptAuthorityRegistryInputError, "P5B_RECEIPT_FACTORY_REQUIRED")
        _tenant(self.tenant_id, ProcessServiceAttemptAuthorityRegistryInputError)
        for name in (
            "attempt_authority_id", "attempt_id", "instruction_id", "document_id",
            "deputy_id", "allocation_command_id",
        ):
            _identity(name, getattr(self, name), ProcessServiceAttemptAuthorityRegistryInputError)
        _text(
            "allocation_evidence_reference",
            self.allocation_evidence_reference,
            ProcessServiceAttemptAuthorityRegistryInputError,
        )
        for name in (
            "allocation_receipt_evidence_identity", "allocation_receipt_fingerprint",
            "allocation_current_fingerprint", "authority_decision_fingerprint",
        ):
            _fingerprint(name, getattr(self, name), ProcessServiceAttemptAuthorityRegistryInputError)
        _utc("allocated_at", self.allocated_at, ProcessServiceAttemptAuthorityRegistryInputError)
        _utc("authorized_at", self.authorized_at, ProcessServiceAttemptAuthorityRegistryInputError)
        if self.authorized_at < self.allocated_at:
            _raise(ProcessServiceAttemptAuthorityRegistryInputError, "P5B_RECEIPT_CHRONOLOGY_INVALID")
        if _receipt_proof_digest(self._construction_proof) != _digest(self.to_dict()):
            _raise(ProcessServiceAttemptAuthorityRegistryInputError, "P5B_RECEIPT_SOURCE_BINDING_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize complete immutable receipt evidence deterministically."""
        return _receipt_payload(
            tenant_id=self.tenant_id,
            attempt_authority_id=self.attempt_authority_id,
            attempt_id=self.attempt_id,
            instruction_id=self.instruction_id,
            document_id=self.document_id,
            deputy_id=self.deputy_id,
            allocation_command_id=self.allocation_command_id,
            allocation_evidence_reference=self.allocation_evidence_reference,
            allocation_receipt_evidence_identity=self.allocation_receipt_evidence_identity,
            allocation_receipt_fingerprint=self.allocation_receipt_fingerprint,
            allocation_current_fingerprint=self.allocation_current_fingerprint,
            allocated_at=self.allocated_at,
            authorized_at=self.authorized_at,
            authority_decision_fingerprint=self.authority_decision_fingerprint,
        )

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over the complete receipt payload."""
        return _digest(self.to_dict())

    @property
    def evidence_identity(self) -> str:
        """Return deterministic tenant-scoped immutable registry identity."""
        return _digest(
            {
                "schema": RECEIPT_SCHEMA,
                "version": VERSION,
                "tenant_id": self.tenant_id,
                "attempt_authority_id": self.attempt_authority_id,
                "attempt_id": self.attempt_id,
                "receipt_fingerprint": self.fingerprint,
            }
        )


class ProcessServiceAttemptAuthorityPersistenceOutcome(StrEnum):
    """Durable outcome; neither value implies service or financial execution."""

    CREATED = "CREATED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


@dataclass(frozen=True, slots=True)
class ProcessServiceAttemptAuthorityPersistenceResult:
    """Immutable operation result containing exact receipt evidence."""

    outcome: ProcessServiceAttemptAuthorityPersistenceOutcome
    receipt: ProcessServiceAttemptAuthorityReceipt

    def __post_init__(self) -> None:
        """Reject malformed result values before they leave the registry."""
        if not isinstance(self.outcome, ProcessServiceAttemptAuthorityPersistenceOutcome):
            _raise(ProcessServiceAttemptAuthorityRegistryInputError, "P5B_OUTCOME_INVALID")
        if type(self.receipt) is not ProcessServiceAttemptAuthorityReceipt:
            _raise(ProcessServiceAttemptAuthorityRegistryInputError, "P5B_RECEIPT_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact durable outcome without transport metadata."""
        return {"outcome": self.outcome.value, "receipt": self.receipt.to_dict()}


def _receipt_from_decision(decision: ProcessServiceAttemptAuthorityDecision) -> ProcessServiceAttemptAuthorityReceipt:
    """Derive one receipt exclusively from an exact validated P5A decision."""
    payload = decision.to_dict()
    receipt_payload = _receipt_payload(
        tenant_id=cast(str, payload["tenant_id"]),
        attempt_authority_id=cast(str, payload["attempt_authority_id"]),
        attempt_id=cast(str, payload["attempt_id"]),
        instruction_id=cast(str, payload["instruction_id"]),
        document_id=cast(str, payload["document_id"]),
        deputy_id=cast(str, payload["deputy_id"]),
        allocation_command_id=cast(str, payload["allocation_command_id"]),
        allocation_evidence_reference=cast(str, payload["allocation_evidence_reference"]),
        allocation_receipt_evidence_identity=cast(str, payload["allocation_receipt_evidence_identity"]),
        allocation_receipt_fingerprint=cast(str, payload["allocation_receipt_fingerprint"]),
        allocation_current_fingerprint=cast(str, payload["allocation_current_fingerprint"]),
        allocated_at=decision.allocated_at,
        authorized_at=decision.authorized_at,
        authority_decision_fingerprint=decision.fingerprint,
    )
    return ProcessServiceAttemptAuthorityReceipt(
        tenant_id=cast(str, payload["tenant_id"]),
        attempt_authority_id=cast(str, payload["attempt_authority_id"]),
        attempt_id=cast(str, payload["attempt_id"]),
        instruction_id=cast(str, payload["instruction_id"]),
        document_id=cast(str, payload["document_id"]),
        deputy_id=cast(str, payload["deputy_id"]),
        allocation_command_id=cast(str, payload["allocation_command_id"]),
        allocation_evidence_reference=cast(str, payload["allocation_evidence_reference"]),
        allocation_receipt_evidence_identity=cast(str, payload["allocation_receipt_evidence_identity"]),
        allocation_receipt_fingerprint=cast(str, payload["allocation_receipt_fingerprint"]),
        allocation_current_fingerprint=cast(str, payload["allocation_current_fingerprint"]),
        allocated_at=decision.allocated_at,
        authorized_at=decision.authorized_at,
        authority_decision_fingerprint=decision.fingerprint,
        _construction_proof=_issue_receipt_proof(_digest(receipt_payload)),
    )


def _record_for(receipt: ProcessServiceAttemptAuthorityReceipt) -> dict[str, object]:
    """Build one immutable persisted record with derived registry metadata."""
    return {
        "schema": _RECORD_SCHEMA,
        "version": VERSION,
        "entity_type": _RECORD_ENTITY,
        "tenant_id": receipt.tenant_id,
        "attempt_authority_id": receipt.attempt_authority_id,
        "attempt_id": receipt.attempt_id,
        "evidence_identity": receipt.evidence_identity,
        "receipt_payload": receipt.to_dict(),
        "receipt_fingerprint": receipt.fingerprint,
        "authority_decision_fingerprint": receipt.authority_decision_fingerprint,
    }


def _canonical_record(document: Mapping[str, Any]) -> dict[str, Any]:
    """Remove Mongo transport-only ``_id`` for exact canonical comparison."""
    result = dict(document)
    result.pop("_id", None)
    return result


def _hydrate_record(document: Mapping[str, Any]) -> ProcessServiceAttemptAuthorityReceipt:
    """Strictly hydrate and independently verify one persisted receipt."""
    if not isinstance(document, Mapping):
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_RECORD_INVALID")
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _RECORD_FIELDS:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_RECORD_SCHEMA_INVALID")
    if raw.get("schema") != _RECORD_SCHEMA or raw.get("version") != VERSION or raw.get("entity_type") != _RECORD_ENTITY:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_RECORD_VERSION_UNSUPPORTED")
    tenant = _tenant(raw.get("tenant_id"), ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError)
    authority_id = _identity("attempt_authority_id", raw.get("attempt_authority_id"), ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError)
    attempt_id = _identity("attempt_id", raw.get("attempt_id"), ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError)
    record_receipt_fingerprint = _fingerprint("receipt_fingerprint", raw.get("receipt_fingerprint"), ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError)
    record_decision_fingerprint = _fingerprint("authority_decision_fingerprint", raw.get("authority_decision_fingerprint"), ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError)
    evidence_identity = _fingerprint("evidence_identity", raw.get("evidence_identity"), ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError)
    payload = raw.get("receipt_payload")
    if not isinstance(payload, Mapping) or set(payload) != _RECEIPT_PAYLOAD_FIELDS:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_RECEIPT_PAYLOAD_SCHEMA_INVALID")
    payload = dict(payload)
    if payload.get("schema") != RECEIPT_SCHEMA or payload.get("version") != VERSION or payload.get("entity_type") != _RECEIPT_ENTITY:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_RECEIPT_VERSION_UNSUPPORTED")
    allocated_at = _parse_utc("allocated_at", payload.get("allocated_at"))
    authorized_at = _parse_utc("authorized_at", payload.get("authorized_at"))
    values: dict[str, Any] = {
        name: payload.get(name)
        for name in _RECEIPT_SEMANTIC_FIELDS
        if name not in {"allocated_at", "authorized_at"}
    }
    values["allocated_at"] = allocated_at
    values["authorized_at"] = authorized_at
    for name in (
        "tenant_id", "attempt_authority_id", "attempt_id", "instruction_id", "document_id",
        "deputy_id", "allocation_command_id",
    ):
        _identity(name, values[name], ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError)
    _text(
        "allocation_evidence_reference",
        values["allocation_evidence_reference"],
        ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError,
    )
    for name in (
        "allocation_receipt_evidence_identity", "allocation_receipt_fingerprint",
        "allocation_current_fingerprint", "authority_decision_fingerprint",
    ):
        _fingerprint(name, values[name], ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError)
    _tenant(values["tenant_id"], ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError)
    if values["authorized_at"] < values["allocated_at"]:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_RECEIPT_CHRONOLOGY_INVALID")
    canonical_payload = _receipt_payload(**values)
    if payload != canonical_payload:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_RECEIPT_PAYLOAD_INVALID")
    try:
        receipt = ProcessServiceAttemptAuthorityReceipt(
            **values,
            _construction_proof=_issue_receipt_proof(_digest(canonical_payload)),
        )
    except ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError:
        raise
    except ProcessServiceAttemptAuthorityRegistryError as error:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_RECEIPT_PAYLOAD_INVALID", error)
    except Exception as error:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_RECEIPT_PAYLOAD_INVALID", error)
    if receipt.tenant_id != tenant or receipt.attempt_authority_id != authority_id or receipt.attempt_id != attempt_id:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_RECORD_METADATA_MISMATCH")
    if receipt.authority_decision_fingerprint != record_decision_fingerprint:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_DECISION_FINGERPRINT_MISMATCH")
    if _digest(_p5a_payload_from_receipt(receipt)) != receipt.authority_decision_fingerprint:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_DECISION_FINGERPRINT_MISMATCH")
    if receipt.fingerprint != record_receipt_fingerprint:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_RECEIPT_FINGERPRINT_MISMATCH")
    if receipt.evidence_identity != evidence_identity:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_EVIDENCE_IDENTITY_MISMATCH")
    return receipt


def _require_collection(collection: Any) -> None:
    """Require an injected Mongo-compatible collection without owning it."""
    if collection is None or not hasattr(collection, "find_one") or not hasattr(collection, "insert_one"):
        _raise(ProcessServiceAttemptAuthorityRegistryInputError, "P5B_COLLECTION_REQUIRED")


def _require_transaction(session: Any) -> None:
    """Require an already-active caller transaction and never manage it."""
    if session is None:
        _raise(ProcessServiceAttemptAuthorityRegistryTransactionRequiredError)
    state = getattr(session, "in_transaction", False)
    if callable(state):
        state = state()
    if not bool(state):
        _raise(ProcessServiceAttemptAuthorityRegistryTransactionRequiredError)


def _find_rows(collection: Any, query: Mapping[str, object], session: Any) -> list[Mapping[str, Any]]:
    """Exhaust one tenant-scoped query and translate Mongo access failures."""
    try:
        if hasattr(collection, "find"):
            cursor = collection.find(dict(query), session=session)
            return [cast(Mapping[str, Any], row) for row in cursor]
        row = collection.find_one(dict(query), session=session)
        return [] if row is None else [cast(Mapping[str, Any], row)]
    except PyMongoError as error:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistenceUnavailableError, cause=error)


def _is_transient_transaction_write_conflict(error: PyMongoError) -> bool:
    """Recognize only a labeled transactional write conflict at insert time.

    ``TransientTransactionError`` is the driver's positive semantic signal for
    a transaction/write conflict. ``UnknownTransactionCommitResult`` is
    deliberately excluded because it describes commit uncertainty, not a
    rejected insert. This helper is used only by the insert boundary below;
    lookup and index outages retain persistence-unavailable semantics.
    """
    return error.has_error_label("TransientTransactionError") and not error.has_error_label(
        "UnknownTransactionCommitResult"
    )


def _one_or_not_found(rows: list[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Require zero or one structurally valid durable row."""
    if len(rows) > 1:
        _raise(ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError, "P5B_DUPLICATE_DURABLE_ROWS")
    if not rows:
        _raise(ProcessServiceAttemptAuthorityRegistryReceiptNotFoundError)
    return rows[0]


def _persisted_exactly(record: Mapping[str, object], candidate: Mapping[str, Any]) -> bool:
    """Compare durable canonical bytes while ignoring Mongo's ``_id`` only."""
    return _canonical_record(candidate) == dict(record)


class ProcessServiceAttemptAuthorityRegistry:
    """Caller-transaction-owned append-only P5B receipt registry.

    The registry accepts only exact P5A decisions, persists one immutable
    receipt collection, and strictly hydrates every returned row. It stores no
    Mongo client and never starts, commits, aborts, retries, or owns a caller's
    session. Persistence is evidence only and cannot create service, custody,
    billing, payment, execution, or settlement truth.
    """

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create the three tenant-scoped unique P5B identity indexes."""
        _require_collection(collection)
        try:
            collection.create_index(
                [("tenant_id", ASCENDING), ("attempt_authority_id", ASCENDING)],
                unique=True,
                name=AUTHORITY_INDEX_NAME,
            )
            collection.create_index(
                [("tenant_id", ASCENDING), ("attempt_id", ASCENDING)],
                unique=True,
                name=ATTEMPT_INDEX_NAME,
            )
            collection.create_index(
                [("tenant_id", ASCENDING), ("evidence_identity", ASCENDING)],
                unique=True,
                name=EVIDENCE_INDEX_NAME,
            )
        except PyMongoError as error:
            _raise(ProcessServiceAttemptAuthorityRegistryPersistenceUnavailableError, cause=error)

    @staticmethod
    def get_by_attempt_authority_id(
        tenant_id: str,
        attempt_authority_id: str,
        collection: Any,
        *,
        session: Any,
    ) -> ProcessServiceAttemptAuthorityReceipt:
        """Hydrate one exact tenant/authority receipt under the caller snapshot."""
        _require_collection(collection)
        _require_transaction(session)
        tenant = _tenant(tenant_id, ProcessServiceAttemptAuthorityRegistryInputError)
        authority_id = _identity("attempt_authority_id", attempt_authority_id, ProcessServiceAttemptAuthorityRegistryInputError)
        rows = _find_rows(collection, {"tenant_id": tenant, "attempt_authority_id": authority_id}, session)
        return _hydrate_record(_one_or_not_found(rows))

    @staticmethod
    def get_by_attempt_id(
        tenant_id: str,
        attempt_id: str,
        collection: Any,
        *,
        session: Any,
    ) -> ProcessServiceAttemptAuthorityReceipt:
        """Hydrate one exact tenant/attempt receipt under the caller snapshot."""
        _require_collection(collection)
        _require_transaction(session)
        tenant = _tenant(tenant_id, ProcessServiceAttemptAuthorityRegistryInputError)
        attempt = _identity("attempt_id", attempt_id, ProcessServiceAttemptAuthorityRegistryInputError)
        rows = _find_rows(collection, {"tenant_id": tenant, "attempt_id": attempt}, session)
        return _hydrate_record(_one_or_not_found(rows))

    @staticmethod
    def persist(
        decision: ProcessServiceAttemptAuthorityDecision,
        collection: Any,
        *,
        session: Any,
    ) -> ProcessServiceAttemptAuthorityPersistenceResult:
        """Persist one exact P5A decision or return an exact immutable replay.

        The caller owns the active transaction. Same authority identity and
        canonical bytes replay exactly; divergent authority or attempt identity
        fails closed. A duplicate-key race in the active transaction requires a
        whole-transaction retry and is never healed locally.
        """
        _require_collection(collection)
        _require_transaction(session)
        if type(decision) is not ProcessServiceAttemptAuthorityDecision:
            _raise(ProcessServiceAttemptAuthorityRegistryInputError, "P5B_DECISION_REQUIRED")
        try:
            decision.__post_init__()
        except ProcessServiceAttemptAuthorityRegistryError:
            raise
        except Exception as error:
            _raise(ProcessServiceAttemptAuthorityRegistryInputError, "P5B_DECISION_INVALID", error)
        try:
            receipt = _receipt_from_decision(decision)
        except ProcessServiceAttemptAuthorityRegistryError:
            raise
        except Exception as error:
            _raise(ProcessServiceAttemptAuthorityRegistryInputError, "P5B_DECISION_INVALID", error)
        record = _record_for(receipt)
        authority_query = {"tenant_id": receipt.tenant_id, "attempt_authority_id": receipt.attempt_authority_id}
        authority_rows = _find_rows(collection, authority_query, session)
        if authority_rows:
            existing = _one_or_not_found(authority_rows)
            existing_receipt = _hydrate_record(existing)
            if _persisted_exactly(record, existing):
                return ProcessServiceAttemptAuthorityPersistenceResult(
                    outcome=ProcessServiceAttemptAuthorityPersistenceOutcome.IDEMPOTENT_REPLAY,
                    receipt=existing_receipt,
                )
            _raise(ProcessServiceAttemptAuthorityRegistryAuthorityIdentityConflictError)
        attempt_query = {"tenant_id": receipt.tenant_id, "attempt_id": receipt.attempt_id}
        attempt_rows = _find_rows(collection, attempt_query, session)
        if attempt_rows:
            _hydrate_record(_one_or_not_found(attempt_rows))
            _raise(ProcessServiceAttemptAuthorityRegistryAttemptIdentityConflictError)
        try:
            collection.insert_one(dict(record), session=session)
        except DuplicateKeyError as error:
            _raise(ProcessServiceAttemptAuthorityRegistryRetryRequiredError, cause=error)
        except PyMongoError as error:
            if _is_transient_transaction_write_conflict(error):
                _raise(ProcessServiceAttemptAuthorityRegistryRetryRequiredError, cause=error)
            _raise(ProcessServiceAttemptAuthorityRegistryPersistenceUnavailableError, cause=error)
        persisted_rows = _find_rows(collection, authority_query, session)
        persisted = _one_or_not_found(persisted_rows)
        persisted_receipt = _hydrate_record(persisted)
        if not _persisted_exactly(record, persisted):
            _raise(ProcessServiceAttemptAuthorityRegistryAuthorityIdentityConflictError)
        return ProcessServiceAttemptAuthorityPersistenceResult(
            outcome=ProcessServiceAttemptAuthorityPersistenceOutcome.CREATED,
            receipt=persisted_receipt,
        )


def ensure_indexes(collection: Any) -> None:
    """Delegate index creation to the canonical P5B registry."""
    ProcessServiceAttemptAuthorityRegistry.ensure_indexes(collection)


def get_by_attempt_authority_id(
    tenant_id: str,
    attempt_authority_id: str,
    collection: Any,
    *,
    session: Any,
) -> ProcessServiceAttemptAuthorityReceipt:
    """Delegate exact tenant/authority hydration to the canonical registry."""
    return ProcessServiceAttemptAuthorityRegistry.get_by_attempt_authority_id(
        tenant_id, attempt_authority_id, collection, session=session
    )


def get_by_attempt_id(
    tenant_id: str,
    attempt_id: str,
    collection: Any,
    *,
    session: Any,
) -> ProcessServiceAttemptAuthorityReceipt:
    """Delegate exact tenant/attempt hydration to the canonical registry."""
    return ProcessServiceAttemptAuthorityRegistry.get_by_attempt_id(
        tenant_id, attempt_id, collection, session=session
    )


def persist(
    decision: ProcessServiceAttemptAuthorityDecision,
    collection: Any,
    *,
    session: Any,
) -> ProcessServiceAttemptAuthorityPersistenceResult:
    """Delegate caller-owned transactional persistence to the canonical registry."""
    return ProcessServiceAttemptAuthorityRegistry.persist(decision, collection, session=session)


__all__ = [
    "VERSION",
    "RECEIPT_SCHEMA",
    "RECEIPT_COLLECTION",
    "AUTHORITY_INDEX_NAME",
    "ATTEMPT_INDEX_NAME",
    "EVIDENCE_INDEX_NAME",
    "ProcessServiceAttemptAuthorityRegistryError",
    "ProcessServiceAttemptAuthorityRegistryInputError",
    "ProcessServiceAttemptAuthorityRegistryTransactionRequiredError",
    "ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError",
    "ProcessServiceAttemptAuthorityRegistryReceiptNotFoundError",
    "ProcessServiceAttemptAuthorityRegistryAuthorityIdentityConflictError",
    "ProcessServiceAttemptAuthorityRegistryAttemptIdentityConflictError",
    "ProcessServiceAttemptAuthorityRegistryPersistenceUnavailableError",
    "ProcessServiceAttemptAuthorityRegistryRetryRequiredError",
    "ProcessServiceAttemptAuthorityPersistenceOutcome",
    "ProcessServiceAttemptAuthorityReceipt",
    "ProcessServiceAttemptAuthorityPersistenceResult",
    "ProcessServiceAttemptAuthorityRegistry",
    "ensure_indexes",
    "get_by_attempt_authority_id",
    "get_by_attempt_id",
    "persist",
]


# ARTIFACT: process_service_attempt_authority_registry.py
# VERSION: v1.1.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY
# AUTHORITY BOUNDARY: append-only P5A receipt persistence and strict hydration
# TENANT POSTURE: every lookup and record is explicitly tenant-scoped
# FAIL-CLOSED POSTURE: corruption, divergence, outages, and races reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
