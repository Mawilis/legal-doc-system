"""Durable, tenant-scoped Process Service allocation receipt registry.

TITLE: Wilsy OS Process Service Allocation Registry (P4B)
VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist immutable P4A allocation receipts and advance an explicit
         tenant/document current-allocation pointer with strict replay and
         compare-and-set semantics. This module never derives allocation,
         custody, service, or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/process_service_allocation_registry.py
COLLABORATION / OWNERSHIP: P4B persistence owner; P1 owns lifecycle evidence,
                            P2 owns immutable P1 evidence, P3 owns assignment
                            authorization, and a later P4A caller owns
                            allocation orchestration. Callers own Mongo
                            sessions and transaction boundaries.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ALLOCATION-REGISTRY establishes
           immutable receipt persistence, explicit currentness, strict replay,
           and fail-closed receipt/pointer correlation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Stores opaque tenant, identity, custody, and
                             evidence references only; no network, provider,
                             secret, credential, or PII expansion.
TENANT BOUNDARY: Every receipt, pointer, lookup, replay query, and CAS
                 predicate is explicitly tenant-scoped; foreign records are
                 indistinguishable from absence.
AUTHORITY BOUNDARY: Immutable allocation-receipt persistence and explicit
                    current-pointer CAS only. No P1/P2/P3 derivation, history
                    selection, allocation orchestration, custody derivation,
                    service creation, or source fabrication.
FINANCIAL AUTHORITY BOUNDARY: Legal allocation evidence is not invoicing,
                              payment, execution, or settlement; Kennel EOS
                              exclusively owns financial execution and
                              settlement.
TRANSACTION BOUNDARY: The caller must provide an already-active session and
                      transaction. This registry never starts, commits,
                      aborts, retries, or stores a Mongo client.
FAIL-CLOSED DECLARATION: Schema drift, malformed evidence, duplicate current
                         pointers, replay divergence, CAS races, outages, and
                         transaction ambiguity reject through stable P4 errors.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError


VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-ALLOCATION-REGISTRY"
RECEIPT_SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-ALLOCATION-RECEIPT/V1"
CURRENT_SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-ALLOCATION-CURRENT/V1"
RECEIPT_COLLECTION: Final[str] = "process_service_allocation_receipts"
CURRENT_COLLECTION: Final[str] = "process_service_allocation_current"
FACT_COLLECTION: Final[str] = RECEIPT_COLLECTION
POINTER_COLLECTION: Final[str] = CURRENT_COLLECTION
ALLOCATION_RECEIPT_COLLECTION: Final[str] = RECEIPT_COLLECTION
ALLOCATION_CURRENT_COLLECTION: Final[str] = CURRENT_COLLECTION

RECEIPT_COMMAND_INDEX_NAME: Final[str] = "process_service_allocation_tenant_command_unique"
RECEIPT_IDEMPOTENCY_INDEX_NAME: Final[str] = "process_service_allocation_tenant_document_idempotency_unique"
RECEIPT_EVENT_INDEX_NAME: Final[str] = "process_service_allocation_tenant_event_unique"
CURRENT_STREAM_INDEX_NAME: Final[str] = "process_service_allocation_current_tenant_document_unique"

_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceAllocationRegistryError(RuntimeError):
    """Base fail-closed P4B persistence error.

    Errors carry stable ``P4_`` codes and represent no allocation, custody,
    service, payment, settlement, or transaction-side effect.
    """

    default_code = "P4_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class ProcessServiceAllocationRegistryInputError(ProcessServiceAllocationRegistryError):
    """Caller input or explicit dependency failed closed."""

    default_code = "P4_INPUT_INVALID"


class ProcessServiceAllocationRegistryTransactionRequiredError(ProcessServiceAllocationRegistryError):
    """An already-active caller-owned Mongo transaction is required."""

    default_code = "P4_ACTIVE_TRANSACTION_REQUIRED"


class ProcessServiceAllocationRegistryPersistedRecordInvalidError(ProcessServiceAllocationRegistryError):
    """A persisted receipt or current pointer failed strict hydration."""

    default_code = "P4_PERSISTED_RECORD_INVALID"


class ProcessServiceAllocationRegistryReceiptNotFoundError(ProcessServiceAllocationRegistryError):
    """A required tenant/document receipt was absent in the caller snapshot."""

    default_code = "P4_RECEIPT_NOT_FOUND"


class ProcessServiceAllocationRegistryCurrentPointerMissingError(ProcessServiceAllocationRegistryError):
    """The explicit current pointer was absent; historical latest is never inferred."""

    default_code = "P4_CURRENT_POINTER_MISSING"


class ProcessServiceAllocationRegistryMultipleCurrentPointerError(ProcessServiceAllocationRegistryPersistedRecordInvalidError):
    """More than one current pointer exists for one tenant/document stream."""

    default_code = "P4_MULTIPLE_CURRENT_POINTERS"


class ProcessServiceAllocationRegistryIdempotencyConflictError(ProcessServiceAllocationRegistryError):
    """An idempotency key was reused for divergent immutable evidence."""

    default_code = "P4_IDEMPOTENCY_CONFLICT"


class ProcessServiceAllocationRegistryAllocationCommandConflictError(ProcessServiceAllocationRegistryError):
    """An allocation-command identity is already bound to different evidence."""

    default_code = "P4_ALLOCATION_COMMAND_IDENTITY_CONFLICT"


class ProcessServiceAllocationRegistryCurrentPointerConflictError(ProcessServiceAllocationRegistryError):
    """The supplied expected current pointer does not match durable currentness."""

    default_code = "P4_CURRENT_POINTER_CAS_CONFLICT"


class ProcessServiceAllocationRegistryPersistenceUnavailableError(ProcessServiceAllocationRegistryError):
    """Mongo persistence or cursor access was unavailable."""

    default_code = "P4_PERSISTENCE_UNAVAILABLE"


class ProcessServiceAllocationRegistryRetryRequiredError(ProcessServiceAllocationRegistryError):
    """A transaction-scoped race requires whole-transaction caller restart."""

    default_code = "P4_WHOLE_TRANSACTION_RETRY_REQUIRED"


class ProcessServiceAllocationRegistryReceiptPointerCorrelationError(ProcessServiceAllocationRegistryPersistedRecordInvalidError):
    """Receipt and explicit current pointer do not correlate exactly."""

    default_code = "P4_RECEIPT_POINTER_CORRELATION_INVALID"


class ProcessServiceAllocationRegistryCustodyEventConflictError(ProcessServiceAllocationRegistryError):
    """An allocation custody-event identity is already bound divergently."""

    default_code = "P4_ALLOCATION_CUSTODY_EVENT_IDENTITY_CONFLICT"


class ProcessServiceAllocationPersistenceOutcome(StrEnum):
    """Durable operation result; neither value implies allocation execution."""

    CREATED = "CREATED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


def _raise(
    error_type: type[ProcessServiceAllocationRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object, *, maximum: int | None = None) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _raise(ProcessServiceAllocationRegistryInputError, f"P4_{name.upper()}_INVALID")
    if maximum is not None and len(value) > maximum:
        _raise(ProcessServiceAllocationRegistryInputError, f"P4_{name.upper()}_INVALID")
    return value


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _raise(ProcessServiceAllocationRegistryInputError, f"P4_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _raise(ProcessServiceAllocationRegistryInputError, "P4_TENANT_INVALID")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _raise(ProcessServiceAllocationRegistryInputError, f"P4_{name.upper()}_INVALID")
    return cast(str, value)


def _utc(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        _raise(ProcessServiceAllocationRegistryInputError, f"P4_{name.upper()}_INVALID")
    return value


def _positive_int(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        _raise(ProcessServiceAllocationRegistryInputError, f"P4_{name.upper()}_INVALID")
    return value


def _sha3(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _parse_utc(name: str, value: object) -> datetime:
    if not isinstance(value, str):
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, f"P4_{name.upper()}_INVALID")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, f"P4_{name.upper()}_INVALID", error)
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, f"P4_{name.upper()}_INVALID")
    return parsed


def _canonical(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_canonical(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in value.items()}
    return value


RECEIPT_SEMANTIC_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id",
    "allocation_command_id",
    "idempotency_key",
    "instruction_id",
    "case_matter_id",
    "document_id",
    "district_id",
    "sheriff_office_id",
    "deputy_id",
    "assignment_decision_id",
    "assignment_decision_fingerprint",
    "source_instruction_fingerprint",
    "source_document_fingerprint",
    "source_district_fingerprint",
    "source_sheriff_office_fingerprint",
    "source_deputy_fingerprint",
    "prior_custody_chain_fingerprint",
    "prior_custody_head_event_id",
    "prior_custody_head_fingerprint",
    "prior_custody_head_sequence_number",
    "from_holder_reference",
    "to_holder_reference",
    "allocation_custody_event_id",
    "allocation_evidence_reference",
    "allocated_at",
    "allocated_document_fingerprint",
    "allocation_custody_event_fingerprint",
    "result_custody_chain_fingerprint",
)


@dataclass(frozen=True, slots=True)
class ProcessServiceAllocationReceipt:
    """Immutable P4A allocation receipt awaiting durable persistence.

    All source/P3/custody bindings are caller-provided evidence and are
    validated for exact shape. ``command_fingerprint`` and ``fingerprint`` are
    derived properties, never caller assertions. The value records allocation
    evidence only; it does not mutate custody, create a service attempt, or
    confer invoice, payment, execution, or settlement authority.
    """

    tenant_id: str
    allocation_command_id: str
    idempotency_key: str
    instruction_id: str
    case_matter_id: str
    document_id: str
    district_id: str
    sheriff_office_id: str
    deputy_id: str
    assignment_decision_id: str
    assignment_decision_fingerprint: str
    source_instruction_fingerprint: str
    source_document_fingerprint: str
    source_district_fingerprint: str
    source_sheriff_office_fingerprint: str
    source_deputy_fingerprint: str
    prior_custody_chain_fingerprint: str
    prior_custody_head_event_id: str
    prior_custody_head_fingerprint: str
    prior_custody_head_sequence_number: int
    from_holder_reference: str
    to_holder_reference: str
    allocation_custody_event_id: str
    allocation_evidence_reference: str
    allocated_at: datetime
    allocated_document_fingerprint: str
    allocation_custody_event_fingerprint: str
    result_custody_chain_fingerprint: str

    def __post_init__(self) -> None:
        """Validate every immutable receipt field fail closed."""
        _tenant(self.tenant_id)
        _identity("allocation_command_id", self.allocation_command_id)
        _text("idempotency_key", self.idempotency_key, maximum=256)
        for name in (
            "instruction_id", "case_matter_id", "document_id", "district_id",
            "sheriff_office_id", "deputy_id", "assignment_decision_id",
            "prior_custody_head_event_id", "allocation_custody_event_id",
        ):
            _identity(name, getattr(self, name))
        for name in (
            "assignment_decision_fingerprint", "source_instruction_fingerprint",
            "source_document_fingerprint", "source_district_fingerprint",
            "source_sheriff_office_fingerprint", "source_deputy_fingerprint",
            "prior_custody_chain_fingerprint", "prior_custody_head_fingerprint",
            "allocated_document_fingerprint", "allocation_custody_event_fingerprint",
            "result_custody_chain_fingerprint",
        ):
            _fingerprint(name, getattr(self, name))
        _positive_int("prior_custody_head_sequence_number", self.prior_custody_head_sequence_number)
        _text("from_holder_reference", self.from_holder_reference)
        _text("to_holder_reference", self.to_holder_reference)
        _text("allocation_evidence_reference", self.allocation_evidence_reference)
        _utc("allocated_at", self.allocated_at)

    def _command_payload(self) -> dict[str, object]:
        """Return the pre-allocation command semantics, excluding results."""
        payload = self.to_dict(include_fingerprint=False, include_command_fingerprint=False)
        payload.pop("allocated_document_fingerprint")
        payload.pop("allocation_custody_event_fingerprint")
        payload.pop("result_custody_chain_fingerprint")
        return payload

    @property
    def command_fingerprint(self) -> str:
        """Return SHA3-512 over command/pre-allocation semantics only."""
        return _sha3(self._command_payload())

    def to_dict(
        self,
        *,
        include_fingerprint: bool = True,
        include_command_fingerprint: bool = True,
    ) -> dict[str, object]:
        """Serialize the complete immutable receipt deterministically."""
        payload: dict[str, object] = {
            "schema": RECEIPT_SCHEMA,
            "version": VERSION,
            "entity_type": "ProcessServiceAllocationReceipt",
        }
        payload.update({name: _canonical(getattr(self, name)) for name in RECEIPT_SEMANTIC_FIELDS})
        if include_command_fingerprint:
            payload["command_fingerprint"] = self.command_fingerprint
        if include_fingerprint:
            payload["fingerprint"] = _sha3(payload)
        return payload

    @property
    def fingerprint(self) -> str:
        """Return SHA3-512 over the complete receipt including command digest."""
        return cast(str, self.to_dict()["fingerprint"])

    @property
    def evidence_identity(self) -> str:
        """Return the deterministic registry identity for this receipt."""
        return _receipt_evidence_identity(self)


CURRENT_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id",
    "document_id",
    "process_document_fingerprint",
    "custody_chain_fingerprint",
    "custody_head_event_id",
    "custody_head_fingerprint",
    "custody_head_sequence_number",
    "current_holder_reference",
    "authority_evidence_reference",
    "authority_evidence_fingerprint",
)


@dataclass(frozen=True, slots=True)
class ProcessServiceAllocationCurrent:
    """Immutable explicit current pointer for one tenant/document stream.

    This compact pointer is currentness evidence, not a P1 document snapshot.
    Normal allocation advancement derives the next pointer internally from a
    validated receipt; callers cannot submit an independently asserted next
    pointer to the persistence operation.
    """

    tenant_id: str
    document_id: str
    process_document_fingerprint: str
    custody_chain_fingerprint: str
    custody_head_event_id: str
    custody_head_fingerprint: str
    custody_head_sequence_number: int
    current_holder_reference: str
    authority_evidence_reference: str
    authority_evidence_fingerprint: str

    def __post_init__(self) -> None:
        """Validate the complete tenant/document currentness pointer."""
        _tenant(self.tenant_id)
        _identity("document_id", self.document_id)
        for name in (
            "process_document_fingerprint", "custody_chain_fingerprint",
            "custody_head_fingerprint", "authority_evidence_fingerprint",
        ):
            _fingerprint(name, getattr(self, name))
        _identity("custody_head_event_id", self.custody_head_event_id)
        _positive_int("custody_head_sequence_number", self.custody_head_sequence_number)
        _text("current_holder_reference", self.current_holder_reference)
        _identity("authority_evidence_reference", self.authority_evidence_reference)

    def to_dict(self) -> dict[str, object]:
        """Serialize the strict current pointer, including schema identity."""
        payload: dict[str, object] = {
            "schema": CURRENT_SCHEMA,
            "version": VERSION,
            "entity_type": "ProcessServiceAllocationCurrent",
        }
        payload.update({name: _canonical(getattr(self, name)) for name in CURRENT_FIELDS})
        return payload


@dataclass(frozen=True, slots=True)
class ProcessServiceAllocationPersistenceResult:
    """Immutable outcome containing the exact durable receipt and current head."""

    outcome: ProcessServiceAllocationPersistenceOutcome
    receipt: ProcessServiceAllocationReceipt
    current: ProcessServiceAllocationCurrent

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, ProcessServiceAllocationPersistenceOutcome):
            _raise(ProcessServiceAllocationRegistryInputError, "P4_OUTCOME_INVALID")
        if type(self.receipt) is not ProcessServiceAllocationReceipt or type(self.current) is not ProcessServiceAllocationCurrent:
            _raise(ProcessServiceAllocationRegistryInputError, "P4_RESULT_VALUE_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize the result without adding transport or financial fields."""
        return {
            "outcome": self.outcome.value,
            "receipt": self.receipt.to_dict(),
            "current": self.current.to_dict(),
        }


def _receipt_evidence_identity(receipt: ProcessServiceAllocationReceipt) -> str:
    return _sha3(
        {
            "schema": RECEIPT_SCHEMA,
            "version": VERSION,
            "tenant_id": receipt.tenant_id,
            "document_id": receipt.document_id,
            "allocation_command_id": receipt.allocation_command_id,
            "receipt_fingerprint": receipt.fingerprint,
        }
    )


def _record_for(receipt: ProcessServiceAllocationReceipt) -> dict[str, object]:
    """Build one immutable receipt record; all digests are derived here."""
    return {
        "schema": RECEIPT_SCHEMA,
        "version": VERSION,
        "entity_type": "ProcessServiceAllocationReceiptRecord",
        "tenant_id": receipt.tenant_id,
        "document_id": receipt.document_id,
        "allocation_command_id": receipt.allocation_command_id,
        "allocation_custody_event_id": receipt.allocation_custody_event_id,
        "idempotency_key": receipt.idempotency_key,
        "evidence_identity": receipt.evidence_identity,
        "receipt_payload": receipt.to_dict(),
        "command_fingerprint": receipt.command_fingerprint,
        "receipt_fingerprint": receipt.fingerprint,
    }


_RECORD_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema", "version", "entity_type", "tenant_id", "document_id",
        "allocation_command_id", "idempotency_key", "evidence_identity",
        "allocation_custody_event_id",
        "receipt_payload", "command_fingerprint", "receipt_fingerprint",
    }
)
_RECEIPT_PAYLOAD_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema", "version", "entity_type", *RECEIPT_SEMANTIC_FIELDS,
        "command_fingerprint", "fingerprint",
    }
)
_CURRENT_FIELDS_SET: Final[frozenset[str]] = frozenset(
    {"schema", "version", "entity_type", *CURRENT_FIELDS}
)


def _receipt_from_payload(payload: object) -> ProcessServiceAllocationReceipt:
    """Strictly reconstruct one P4B receipt without trusting persisted digests."""
    if not isinstance(payload, Mapping) or set(payload) != _RECEIPT_PAYLOAD_FIELDS:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_RECEIPT_PAYLOAD_SCHEMA_INVALID")
    if payload.get("schema") != RECEIPT_SCHEMA or payload.get("version") != VERSION or payload.get("entity_type") != "ProcessServiceAllocationReceipt":
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_RECEIPT_VERSION_UNSUPPORTED")
    values: dict[str, Any] = {}
    for name in RECEIPT_SEMANTIC_FIELDS:
        value = payload[name]
        if name == "allocated_at":
            value = _parse_utc(name, value)
        values[name] = value
    try:
        receipt = ProcessServiceAllocationReceipt(**values)
    except ProcessServiceAllocationRegistryPersistedRecordInvalidError:
        raise
    except ProcessServiceAllocationRegistryInputError as error:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_RECEIPT_PAYLOAD_INVALID", error)
    except (TypeError, ValueError) as error:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_RECEIPT_PAYLOAD_INVALID", error)
    if payload.get("command_fingerprint") != receipt.command_fingerprint:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_COMMAND_FINGERPRINT_MISMATCH")
    if payload.get("fingerprint") != receipt.fingerprint:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_RECEIPT_FINGERPRINT_MISMATCH")
    return receipt


def _hydrate_receipt(document: Mapping[str, Any]) -> ProcessServiceAllocationReceipt:
    """Hydrate and cryptographically verify one persisted receipt record."""
    if not isinstance(document, Mapping):
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_RECEIPT_RECORD_INVALID")
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _RECORD_FIELDS:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_RECEIPT_RECORD_SCHEMA_INVALID")
    if raw.get("schema") != RECEIPT_SCHEMA or raw.get("version") != VERSION or raw.get("entity_type") != "ProcessServiceAllocationReceiptRecord":
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_RECEIPT_VERSION_UNSUPPORTED")
    try:
        tenant = _tenant(raw.get("tenant_id"))
        payload = raw.get("receipt_payload")
        receipt = _receipt_from_payload(payload)
        if (
            receipt.tenant_id != tenant
            or receipt.document_id != raw.get("document_id")
            or receipt.allocation_command_id != raw.get("allocation_command_id")
            or receipt.idempotency_key != raw.get("idempotency_key")
            or receipt.allocation_custody_event_id != raw.get("allocation_custody_event_id")
        ):
            _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_RECEIPT_METADATA_MISMATCH")
        _fingerprint("command_fingerprint", raw.get("command_fingerprint"))
        _fingerprint("receipt_fingerprint", raw.get("receipt_fingerprint"))
        _fingerprint("evidence_identity", raw.get("evidence_identity"))
    except ProcessServiceAllocationRegistryPersistedRecordInvalidError:
        raise
    except ProcessServiceAllocationRegistryInputError as error:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_RECEIPT_RECORD_INVALID", error)
    if raw["command_fingerprint"] != receipt.command_fingerprint:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_COMMAND_FINGERPRINT_MISMATCH")
    if raw["receipt_fingerprint"] != receipt.fingerprint:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_RECEIPT_FINGERPRINT_MISMATCH")
    if raw["evidence_identity"] != receipt.evidence_identity:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_EVIDENCE_IDENTITY_MISMATCH")
    return receipt


def _hydrate_current(document: Mapping[str, Any]) -> ProcessServiceAllocationCurrent:
    """Hydrate one explicit pointer with an exact persisted field allowlist."""
    if not isinstance(document, Mapping):
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_CURRENT_RECORD_INVALID")
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _CURRENT_FIELDS_SET:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_CURRENT_RECORD_SCHEMA_INVALID")
    if raw.get("schema") != CURRENT_SCHEMA or raw.get("version") != VERSION or raw.get("entity_type") != "ProcessServiceAllocationCurrent":
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_CURRENT_VERSION_UNSUPPORTED")
    values: dict[str, Any] = {name: raw[name] for name in CURRENT_FIELDS}
    try:
        for name in (
            "process_document_fingerprint", "custody_chain_fingerprint",
            "custody_head_fingerprint", "authority_evidence_fingerprint",
        ):
            _fingerprint(name, values[name])
        pointer = ProcessServiceAllocationCurrent(**values)
    except ProcessServiceAllocationRegistryPersistedRecordInvalidError:
        raise
    except ProcessServiceAllocationRegistryInputError as error:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_CURRENT_RECORD_INVALID", error)
    except (TypeError, ValueError) as error:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_CURRENT_RECORD_INVALID", error)
    if pointer.to_dict() != raw:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_CURRENT_RECORD_MISMATCH")
    return pointer


def _active_transaction(session: Any) -> Any:
    """Require an active caller transaction, supporting bool or callable markers."""
    if session is None:
        _raise(ProcessServiceAllocationRegistryTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(ProcessServiceAllocationRegistryTransactionRequiredError)
    return session


def _collection(value: Any, label: str) -> Any:
    if value is None:
        _raise(ProcessServiceAllocationRegistryInputError, f"P4_{label}_COLLECTION_REQUIRED")
    return value


def _rows(collection: Any, query: Mapping[str, object], session: Any) -> list[Mapping[str, Any]]:
    """Exhaust a bounded query and preserve the caller session on every read."""
    target = _collection(collection, "COLLECTION")
    if hasattr(target, "find"):
        cursor = target.find(dict(query), session=session)
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(2)
        return [cast(Mapping[str, Any], row) for row in cursor]
    if hasattr(target, "find_one"):
        row = target.find_one(dict(query), session=session)
        return [] if row is None else [cast(Mapping[str, Any], row)]
    _raise(ProcessServiceAllocationRegistryInputError, "P4_COLLECTION_INTERFACE_INVALID")


def _read_rows(collection: Any, query: Mapping[str, object], session: Any) -> list[Mapping[str, Any]]:
    try:
        return _rows(collection, query, session)
    except PyMongoError as error:
        _raise(ProcessServiceAllocationRegistryPersistenceUnavailableError, cause=error)


def _receipt_query(receipt: ProcessServiceAllocationReceipt) -> dict[str, object]:
    return {
        "tenant_id": receipt.tenant_id,
        "document_id": receipt.document_id,
        "idempotency_key": receipt.idempotency_key,
    }


def _command_query(receipt: ProcessServiceAllocationReceipt) -> dict[str, object]:
    return {
        "tenant_id": receipt.tenant_id,
        "allocation_command_id": receipt.allocation_command_id,
    }


def _event_query(receipt: ProcessServiceAllocationReceipt) -> dict[str, object]:
    return {
        "tenant_id": receipt.tenant_id,
        "allocation_custody_event_id": receipt.allocation_custody_event_id,
    }


def _current_query(tenant_id: str, document_id: str) -> dict[str, object]:
    return {"tenant_id": _tenant(tenant_id), "document_id": _identity("document_id", document_id)}


def _pointer_cas_query(pointer: ProcessServiceAllocationCurrent) -> dict[str, object]:
    return pointer.to_dict()


def _next_current(receipt: ProcessServiceAllocationReceipt) -> ProcessServiceAllocationCurrent:
    """Derive the only permitted next pointer from one validated receipt."""
    return ProcessServiceAllocationCurrent(
        tenant_id=receipt.tenant_id,
        document_id=receipt.document_id,
        process_document_fingerprint=receipt.allocated_document_fingerprint,
        custody_chain_fingerprint=receipt.result_custody_chain_fingerprint,
        custody_head_event_id=receipt.allocation_custody_event_id,
        custody_head_fingerprint=receipt.allocation_custody_event_fingerprint,
        custody_head_sequence_number=receipt.prior_custody_head_sequence_number + 1,
        current_holder_reference=receipt.to_holder_reference,
        authority_evidence_reference=receipt.allocation_command_id,
        authority_evidence_fingerprint=receipt.fingerprint,
    )


def _correlates(receipt: ProcessServiceAllocationReceipt, prior: ProcessServiceAllocationCurrent) -> bool:
    return (
        receipt.tenant_id == prior.tenant_id
        and receipt.document_id == prior.document_id
        and receipt.source_document_fingerprint == prior.process_document_fingerprint
        and receipt.prior_custody_chain_fingerprint == prior.custody_chain_fingerprint
        and receipt.prior_custody_head_event_id == prior.custody_head_event_id
        and receipt.prior_custody_head_fingerprint == prior.custody_head_fingerprint
        and receipt.prior_custody_head_sequence_number == prior.custody_head_sequence_number
        and receipt.from_holder_reference == prior.current_holder_reference
    )


def ensure_indexes(receipt_collection: Any, current_collection: Any) -> None:
    """Create the four tenant-scoped uniqueness primitives without DB ownership."""
    receipts = _collection(receipt_collection, "RECEIPT")
    current = _collection(current_collection, "CURRENT")
    if not hasattr(receipts, "create_index") or not hasattr(current, "create_index"):
        _raise(ProcessServiceAllocationRegistryInputError, "P4_COLLECTION_INTERFACE_INVALID")
    try:
        receipts.create_index(
            [("tenant_id", ASCENDING), ("allocation_command_id", ASCENDING)],
            unique=True,
            name=RECEIPT_COMMAND_INDEX_NAME,
        )
        receipts.create_index(
            [("tenant_id", ASCENDING), ("document_id", ASCENDING), ("idempotency_key", ASCENDING)],
            unique=True,
            name=RECEIPT_IDEMPOTENCY_INDEX_NAME,
        )
        receipts.create_index(
            [("tenant_id", ASCENDING), ("allocation_custody_event_id", ASCENDING)],
            unique=True,
            name=RECEIPT_EVENT_INDEX_NAME,
        )
        current.create_index(
            [("tenant_id", ASCENDING), ("document_id", ASCENDING)],
            unique=True,
            name=CURRENT_STREAM_INDEX_NAME,
        )
    except PyMongoError as error:
        _raise(ProcessServiceAllocationRegistryPersistenceUnavailableError, cause=error)


def get_current(
    tenant_id: str,
    document_id: str,
    current_collection: Any,
    *,
    session: Any,
) -> ProcessServiceAllocationCurrent:
    """Read exactly one explicit current pointer under the caller snapshot."""
    tx = _active_transaction(session)
    query = _current_query(tenant_id, document_id)
    rows = _read_rows(current_collection, query, tx)
    if not rows:
        _raise(ProcessServiceAllocationRegistryCurrentPointerMissingError)
    if len(rows) > 1:
        _raise(ProcessServiceAllocationRegistryMultipleCurrentPointerError)
    pointer = _hydrate_current(rows[0])
    if pointer.tenant_id != query["tenant_id"] or pointer.document_id != query["document_id"]:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_CURRENT_TENANT_OR_DOCUMENT_MISMATCH")
    return pointer


def get_receipt_by_idempotency_key(
    tenant_id: str,
    document_id: str,
    idempotency_key: str,
    receipt_collection: Any,
    *,
    session: Any,
) -> ProcessServiceAllocationReceipt | None:
    """Read one exact tenant/document/idempotency receipt; absence returns ``None``."""
    tx = _active_transaction(session)
    tenant = _tenant(tenant_id)
    document = _identity("document_id", document_id)
    key = _text("idempotency_key", idempotency_key, maximum=256)
    rows = _read_rows(
        receipt_collection,
        {"tenant_id": tenant, "document_id": document, "idempotency_key": key},
        tx,
    )
    if len(rows) > 1:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_DUPLICATE_IDEMPOTENCY")
    return None if not rows else _hydrate_receipt(rows[0])


def _get_current_rows(
    tenant_id: str,
    document_id: str,
    current_collection: Any,
    session: Any,
) -> ProcessServiceAllocationCurrent:
    return get_current(tenant_id, document_id, current_collection, session=session)


def persist_receipt_and_advance_current(
    receipt: ProcessServiceAllocationReceipt,
    expected_prior_current: ProcessServiceAllocationCurrent,
    receipt_collection: Any,
    current_collection: Any,
    *,
    session: Any,
) -> ProcessServiceAllocationPersistenceResult:
    """Persist one receipt and CAS-advance explicit currentness atomically.

    The caller owns the active Mongo transaction. Replay is checked first;
    divergent idempotency, command identity, pointer correlation, persistence
    outages, and races fail closed. No pointer seeding, history selection,
    transaction retry, allocation orchestration, or financial behavior occurs.
    """
    tx = _active_transaction(session)
    if type(receipt) is not ProcessServiceAllocationReceipt:
        _raise(ProcessServiceAllocationRegistryInputError, "P4_RECEIPT_REQUIRED")
    if type(expected_prior_current) is not ProcessServiceAllocationCurrent:
        _raise(ProcessServiceAllocationRegistryInputError, "P4_EXPECTED_PRIOR_CURRENT_REQUIRED")
    receipts = _collection(receipt_collection, "RECEIPT")
    current_collection = _collection(current_collection, "CURRENT")
    if not hasattr(receipts, "insert_one") or not hasattr(current_collection, "update_one"):
        _raise(ProcessServiceAllocationRegistryInputError, "P4_COLLECTION_INTERFACE_INVALID")

    replay_rows = _read_rows(receipts, _receipt_query(receipt), tx)
    if len(replay_rows) > 1:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_DUPLICATE_IDEMPOTENCY")
    if replay_rows:
        existing = _hydrate_receipt(replay_rows[0])
        if existing.to_dict() != receipt.to_dict():
            _raise(ProcessServiceAllocationRegistryIdempotencyConflictError)
        durable_current = _get_current_rows(receipt.tenant_id, receipt.document_id, current_collection, tx)
        expected_next = _next_current(existing)
        if durable_current.to_dict() != expected_next.to_dict():
            _raise(ProcessServiceAllocationRegistryReceiptPointerCorrelationError)
        return ProcessServiceAllocationPersistenceResult(
            ProcessServiceAllocationPersistenceOutcome.IDEMPOTENT_REPLAY,
            existing,
            durable_current,
        )

    command_rows = _read_rows(receipts, _command_query(receipt), tx)
    if len(command_rows) > 1:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_DUPLICATE_ALLOCATION_COMMAND")
    if command_rows:
        _hydrate_receipt(command_rows[0])
        _raise(ProcessServiceAllocationRegistryAllocationCommandConflictError)

    event_rows = _read_rows(receipts, _event_query(receipt), tx)
    if len(event_rows) > 1:
        _raise(ProcessServiceAllocationRegistryPersistedRecordInvalidError, "P4_DUPLICATE_ALLOCATION_CUSTODY_EVENT")
    if event_rows:
        _hydrate_receipt(event_rows[0])
        _raise(ProcessServiceAllocationRegistryCustodyEventConflictError)

    durable_prior = _get_current_rows(receipt.tenant_id, receipt.document_id, current_collection, tx)
    if durable_prior.to_dict() != expected_prior_current.to_dict():
        _raise(ProcessServiceAllocationRegistryCurrentPointerConflictError)
    if not _correlates(receipt, expected_prior_current):
        _raise(ProcessServiceAllocationRegistryReceiptPointerCorrelationError)

    record = _record_for(receipt)
    try:
        receipts.insert_one(record, session=tx)
    except DuplicateKeyError as error:
        _raise(ProcessServiceAllocationRegistryRetryRequiredError, cause=error)
    except PyMongoError as error:
        _raise(ProcessServiceAllocationRegistryPersistenceUnavailableError, cause=error)

    next_current = _next_current(receipt)
    try:
        result = current_collection.update_one(
            _pointer_cas_query(expected_prior_current),
            {"$set": next_current.to_dict()},
            session=tx,
        )
    except DuplicateKeyError as error:
        _raise(ProcessServiceAllocationRegistryRetryRequiredError, cause=error)
    except PyMongoError as error:
        _raise(ProcessServiceAllocationRegistryPersistenceUnavailableError, cause=error)
    if getattr(result, "matched_count", 0) != 1:
        _raise(ProcessServiceAllocationRegistryRetryRequiredError)

    persisted_rows = _read_rows(receipts, _receipt_query(receipt), tx)
    if len(persisted_rows) != 1:
        _raise(ProcessServiceAllocationRegistryPersistenceUnavailableError)
    persisted_receipt = _hydrate_receipt(persisted_rows[0])
    persisted_current = _get_current_rows(receipt.tenant_id, receipt.document_id, current_collection, tx)
    if persisted_receipt.to_dict() != receipt.to_dict() or persisted_current.to_dict() != next_current.to_dict():
        _raise(ProcessServiceAllocationRegistryReceiptPointerCorrelationError)
    return ProcessServiceAllocationPersistenceResult(
        ProcessServiceAllocationPersistenceOutcome.CREATED,
        persisted_receipt,
        persisted_current,
    )


class ProcessServiceAllocationRegistry:
    """Static P4B facade; it owns no Mongo client or transaction lifecycle."""

    ensure_indexes = staticmethod(ensure_indexes)
    get_current = staticmethod(get_current)
    get_receipt_by_idempotency_key = staticmethod(get_receipt_by_idempotency_key)
    persist_receipt_and_advance_current = staticmethod(persist_receipt_and_advance_current)
    persist_and_advance_current = staticmethod(persist_receipt_and_advance_current)


__all__ = [
    "ALLOCATION_CURRENT_COLLECTION",
    "ALLOCATION_RECEIPT_COLLECTION",
    "CURRENT_COLLECTION",
    "CURRENT_SCHEMA",
    "CURRENT_STREAM_INDEX_NAME",
    "FACT_COLLECTION",
    "ProcessServiceAllocationCurrent",
    "ProcessServiceAllocationPersistenceOutcome",
    "ProcessServiceAllocationPersistenceResult",
    "ProcessServiceAllocationReceipt",
    "ProcessServiceAllocationRegistry",
    "ProcessServiceAllocationRegistryAllocationCommandConflictError",
    "ProcessServiceAllocationRegistryCurrentPointerConflictError",
    "ProcessServiceAllocationRegistryCurrentPointerMissingError",
    "ProcessServiceAllocationRegistryCustodyEventConflictError",
    "ProcessServiceAllocationRegistryError",
    "ProcessServiceAllocationRegistryIdempotencyConflictError",
    "ProcessServiceAllocationRegistryInputError",
    "ProcessServiceAllocationRegistryMultipleCurrentPointerError",
    "ProcessServiceAllocationRegistryPersistedRecordInvalidError",
    "ProcessServiceAllocationRegistryPersistenceUnavailableError",
    "ProcessServiceAllocationRegistryReceiptNotFoundError",
    "ProcessServiceAllocationRegistryReceiptPointerCorrelationError",
    "ProcessServiceAllocationRegistryRetryRequiredError",
    "ProcessServiceAllocationRegistryTransactionRequiredError",
    "POINTER_COLLECTION",
    "RECEIPT_COLLECTION",
    "RECEIPT_COMMAND_INDEX_NAME",
    "RECEIPT_EVENT_INDEX_NAME",
    "RECEIPT_IDEMPOTENCY_INDEX_NAME",
    "RECEIPT_SCHEMA",
    "VERSION",
    "ensure_indexes",
    "get_current",
    "get_receipt_by_idempotency_key",
    "persist_receipt_and_advance_current",
]


# ARTIFACT: process_service_allocation_registry.py
# VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-REGISTRY
# AUTHORITY BOUNDARY: immutable allocation receipt persistence and explicit current-pointer CAS only.
# TENANT POSTURE: tenant/document scope is mandatory on every read, replay, write, and pointer predicate.
# FAIL-CLOSED POSTURE: strict schemas, digests, races, corruption, and persistence failures reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns financial execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
