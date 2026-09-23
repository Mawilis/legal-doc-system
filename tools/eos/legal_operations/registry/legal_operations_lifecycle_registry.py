"""Durable, provider-neutral Legal Operations lifecycle evidence registry.

TITLE: Wilsy OS Legal Operations Lifecycle Evidence Registry
VERSION: v1.2.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist, enumerate exact entity and document-custody history, and
         strictly hydrate immutable P1 Legal Operations evidence without
         deriving lifecycle, service, billing, or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_operations_lifecycle_registry.py
COLLABORATION / OWNERSHIP: P2 persistence owner; the P1 domain remains the
                            exclusive lifecycle/evidence authority. Callers own
                            Mongo sessions and transaction boundaries.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.2.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY adds the
           tenant/document-scoped DocumentCustodyEvent history query and its
           dedicated non-unique Mongo index so L8-3+ orchestration consumes
           hydrated P1 custody evidence without depending on P2 record schema.
           2026-09-23 v1.1.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY added exact
           tenant/type/entity immutable-history retrieval, propagates the
           caller session through the indexed history query, hydrates every
           returned snapshot, and deliberately leaves current-state selection
           to the separate deterministic L8-0 projection authority.
           2026-09-14 v1.0.1-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY translated
           labeled transient transaction write conflicts into the governed
           whole-transaction retry signal while preserving caller ownership.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Stores canonical opaque evidence only; no network,
                             provider, credential, secret, or PII expansion.
TENANT BOUNDARY: Every record and lookup is explicitly tenant-scoped; foreign
                 records are indistinguishable from absence.
AUTHORITY BOUNDARY: Persistence and strict hydration only; no lifecycle
                    derivation, transition authorization, or state fabrication.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; this registry has no invoice,
                              payment, or settlement authority.
TRANSACTION BOUNDARY: Caller supplies and owns every Mongo session/transaction;
                      this registry never starts, commits, aborts, or retries.
FAIL-CLOSED DECLARATION: Unknown types, schema drift, corruption, divergence,
                         persistence failure, and transaction races reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Final, NoReturn, TypeAlias, cast

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
    Deputy,
    District,
    DocumentCustodyEvent,
    DocumentCustodyEventType,
    LegalInstruction,
    LegalInstructionState,
    LifecycleTransitionEvidence,
    ProcessDocument,
    ProcessDocumentState,
    ReturnOfService,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
    ServiceExecutionOutcome,
    SheriffOffice,
)


VERSION: Final[str] = "v1.2.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY"
COLLECTION: Final[str] = "legal_operations_lifecycle_evidence"
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_ENTITY_TYPES = frozenset(
    {
        "LegalInstruction",
        "CaseMatter",
        "ProcessDocument",
        "District",
        "SheriffOffice",
        "Deputy",
        "DocumentCustodyEvent",
        "ServiceAttempt",
        "ServiceExecution",
        "ReturnOfService",
    }
)
_RECORD_FIELDS = frozenset(
    {
        "tenant_id",
        "entity_type",
        "entity_identity",
        "p1_schema",
        "p1_version",
        "p1_payload",
        "p1_fingerprint",
        "evidence_identity",
        "source_payload",
        "source_fingerprint",
    }
)
_ENTITY_ID_FIELDS: Final[dict[str, str]] = {
    "LegalInstruction": "instruction_id",
    "CaseMatter": "case_matter_id",
    "ProcessDocument": "document_id",
    "District": "district_id",
    "SheriffOffice": "sheriff_office_id",
    "Deputy": "deputy_id",
    "DocumentCustodyEvent": "custody_event_id",
    "ServiceAttempt": "attempt_id",
    "ServiceExecution": "service_execution_id",
    "ReturnOfService": "return_id",
}
P1Value: TypeAlias = (
    LegalInstruction
    | CaseMatter
    | ProcessDocument
    | District
    | SheriffOffice
    | Deputy
    | DocumentCustodyEvent
    | ServiceAttempt
    | ServiceExecution
    | ReturnOfService
)


class LegalOperationsLifecycleRegistryError(RuntimeError):
    """Governed persistence, hydration, replay, and tenant-scope failure."""


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable registry error, retaining the technical cause only."""
    error = LegalOperationsLifecycleRegistryError(code)
    if cause is None:
        raise error
    raise error from cause


def _tenant(value: object) -> str:
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail("M2_INVALID_TENANT")
    text = cast(str, value)
    if text.casefold() in {"default", "global", "global_root", "root", "master", "*"}:
        _fail("M2_INVALID_TENANT")
    return text


def _sha3(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_512(encoded.encode("utf-8")).hexdigest()


def _is_transient_transaction_write_conflict(error: PyMongoError) -> bool:
    """Recognize retryable transaction conflicts without resolving commit uncertainty."""
    return error.has_error_label("TransientTransactionError") and not error.has_error_label(
        "UnknownTransactionCommitResult"
    )


def _require_sha3(value: object, code: str) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(code)
    return cast(str, value)


def _required_text(value: object, code: str) -> str:
    """Require one non-empty textual authority field during hydration."""
    if not isinstance(value, str) or not value:
        _fail(code)
    return value


def _parse_timestamp(value: object, code: str) -> datetime:
    if not isinstance(value, str):
        _fail(code)
    text = cast(str, value)
    try:
        result = datetime.fromisoformat(text)
    except ValueError as error:
        _fail(code, error)
    if result.tzinfo is None or result.utcoffset() is None:
        _fail(code)
    return result


def _parse_history(value: object, enum_type: Any) -> tuple[LifecycleTransitionEvidence, ...]:
    if not isinstance(value, list):
        _fail("M2_HISTORY_INVALID")
    result: list[LifecycleTransitionEvidence] = []
    for raw_value in cast(list[object], value):
        raw = cast(Mapping[str, Any], raw_value)
        if not isinstance(raw, Mapping) or set(raw) != {
            "prior_state", "resulting_state", "occurred_at", "evidence_reference", "evidence_fingerprint"
        }:
            _fail("M2_HISTORY_INVALID")
        prior = raw["prior_state"]
        resulting = raw["resulting_state"]
        if not isinstance(prior, str) or not isinstance(resulting, str):
            _fail("M2_HISTORY_INVALID")
        if not isinstance(raw["evidence_reference"], str):
            _fail("M2_HISTORY_INVALID")
        if raw["evidence_fingerprint"] is not None and not isinstance(raw["evidence_fingerprint"], str):
            _fail("M2_HISTORY_INVALID")
        result.append(
            LifecycleTransitionEvidence(
                prior_state=_enum(enum_type, prior, "M2_HISTORY_INVALID"),
                resulting_state=_enum(enum_type, resulting, "M2_HISTORY_INVALID"),
                occurred_at=_parse_timestamp(raw["occurred_at"], "M2_HISTORY_INVALID"),
                evidence_reference=raw["evidence_reference"],
                evidence_fingerprint=raw["evidence_fingerprint"],
            )
        )
    return tuple(result)


def _enum(enum_type: Any, value: object, code: str) -> Any:
    if not isinstance(value, str):
        _fail(code)
    try:
        return enum_type(value)
    except ValueError as error:
        _fail(code, error)


def _payload_fields(entity_type: str) -> frozenset[str]:
    return {
        "LegalInstruction": frozenset({"schema", "version", "entity_type", "tenant_id", "instruction_id", "case_matter_id", "document_id", "registered_at", "evidence_reference", "state", "transition_history"}),
        "CaseMatter": frozenset({"schema", "version", "entity_type", "tenant_id", "case_matter_id", "matter_reference", "opened_at", "evidence_reference", "state", "transition_history"}),
        "ProcessDocument": frozenset({"schema", "version", "entity_type", "tenant_id", "document_id", "case_matter_id", "document_type", "registered_at", "registration_evidence_reference", "state", "transition_history"}),
        "District": frozenset({"schema", "version", "entity_type", "tenant_id", "district_id", "name", "jurisdiction_code", "evidence_reference"}),
        "SheriffOffice": frozenset({"schema", "version", "entity_type", "tenant_id", "sheriff_office_id", "district_id", "name", "evidence_reference"}),
        "Deputy": frozenset({"schema", "version", "entity_type", "tenant_id", "deputy_id", "sheriff_office_id", "display_name", "badge_reference", "evidence_reference"}),
        "DocumentCustodyEvent": frozenset({"schema", "version", "entity_type", "tenant_id", "custody_event_id", "document_id", "event_type", "occurred_at", "sequence_number", "evidence_reference", "from_holder_reference", "to_holder_reference"}),
        "ServiceAttempt": frozenset({"schema", "version", "entity_type", "tenant_id", "attempt_id", "instruction_id", "document_id", "deputy_id", "allocated_at", "allocation_evidence_reference", "state", "transition_history"}),
        "ServiceExecution": frozenset({"schema", "version", "entity_type", "tenant_id", "service_execution_id", "attempt_id", "instruction_id", "document_id", "outcome", "executed_at", "evidence_reference", "evidence_fingerprint"}),
        "ReturnOfService": frozenset({"schema", "version", "entity_type", "tenant_id", "return_id", "instruction_id", "document_id", "attempt_id", "service_execution_id", "service_outcome", "service_evidence_reference", "service_evidence_fingerprint", "generated_at", "state"}),
    }[entity_type]


def _hydrate_payload(payload: object) -> P1Value:
    if not isinstance(payload, Mapping):
        _fail("M2_P1_PAYLOAD_INVALID")
    payload = cast(Mapping[str, Any], payload)
    entity_type = payload.get("entity_type")
    if not isinstance(entity_type, str) or entity_type not in _ENTITY_TYPES:
        _fail("M2_ENTITY_TYPE_UNSUPPORTED")
    if set(payload) != _payload_fields(entity_type):
        _fail("M2_P1_PAYLOAD_SCHEMA_INVALID")
    if payload.get("schema") != "WILSY-LEGAL-OPERATIONS-LIFECYCLE/V1" or payload.get("version") != "v1.0.0-LEGAL-OPERATIONS-LIFECYCLE":
        _fail("M2_P1_VERSION_UNSUPPORTED")
    try:
        common_tenant: Any = payload["tenant_id"]
        if entity_type == "LegalInstruction":
            return LegalInstruction(tenant_id=common_tenant, instruction_id=payload["instruction_id"], case_matter_id=payload["case_matter_id"], document_id=payload["document_id"], registered_at=_parse_timestamp(payload["registered_at"], "M2_P1_PAYLOAD_INVALID"), evidence_reference=payload["evidence_reference"], state=_enum(LegalInstructionState, payload["state"], "M2_P1_PAYLOAD_INVALID"), transition_history=_parse_history(payload["transition_history"], LegalInstructionState))
        if entity_type == "CaseMatter":
            return CaseMatter(tenant_id=common_tenant, case_matter_id=payload["case_matter_id"], matter_reference=payload["matter_reference"], opened_at=_parse_timestamp(payload["opened_at"], "M2_P1_PAYLOAD_INVALID"), evidence_reference=payload["evidence_reference"], state=_enum(CaseMatterState, payload["state"], "M2_P1_PAYLOAD_INVALID"), transition_history=_parse_history(payload["transition_history"], CaseMatterState))
        if entity_type == "ProcessDocument":
            return ProcessDocument(tenant_id=common_tenant, document_id=payload["document_id"], case_matter_id=payload["case_matter_id"], document_type=payload["document_type"], registered_at=_parse_timestamp(payload["registered_at"], "M2_P1_PAYLOAD_INVALID"), registration_evidence_reference=payload["registration_evidence_reference"], state=_enum(ProcessDocumentState, payload["state"], "M2_P1_PAYLOAD_INVALID"), transition_history=_parse_history(payload["transition_history"], ProcessDocumentState))
        if entity_type == "District":
            return District(tenant_id=common_tenant, district_id=payload["district_id"], name=payload["name"], jurisdiction_code=payload["jurisdiction_code"], evidence_reference=payload["evidence_reference"])
        if entity_type == "SheriffOffice":
            return SheriffOffice(tenant_id=common_tenant, sheriff_office_id=payload["sheriff_office_id"], district_id=payload["district_id"], name=payload["name"], evidence_reference=payload["evidence_reference"])
        if entity_type == "Deputy":
            return Deputy(tenant_id=common_tenant, deputy_id=payload["deputy_id"], sheriff_office_id=payload["sheriff_office_id"], display_name=payload["display_name"], badge_reference=payload["badge_reference"], evidence_reference=payload["evidence_reference"])
        if entity_type == "DocumentCustodyEvent":
            return DocumentCustodyEvent(tenant_id=common_tenant, custody_event_id=payload["custody_event_id"], document_id=payload["document_id"], event_type=_enum(DocumentCustodyEventType, payload["event_type"], "M2_P1_PAYLOAD_INVALID"), occurred_at=_parse_timestamp(payload["occurred_at"], "M2_P1_PAYLOAD_INVALID"), sequence_number=payload["sequence_number"], evidence_reference=payload["evidence_reference"], from_holder_reference=payload["from_holder_reference"], to_holder_reference=payload["to_holder_reference"])
        if entity_type == "ServiceAttempt":
            return ServiceAttempt(tenant_id=common_tenant, attempt_id=payload["attempt_id"], instruction_id=payload["instruction_id"], document_id=payload["document_id"], deputy_id=payload["deputy_id"], allocated_at=_parse_timestamp(payload["allocated_at"], "M2_P1_PAYLOAD_INVALID"), allocation_evidence_reference=payload["allocation_evidence_reference"], state=_enum(ServiceAttemptState, payload["state"], "M2_P1_PAYLOAD_INVALID"), transition_history=_parse_history(payload["transition_history"], ServiceAttemptState))
    except LegalOperationsLifecycleRegistryError:
        raise
    except Exception as error:
        _fail("M2_P1_PAYLOAD_INVALID", error)
    if entity_type == "ServiceExecution":
        _fail("M2_FACTORY_SOURCE_REQUIRED")
    _fail("M2_FACTORY_SOURCE_REQUIRED")


def _source_canonical(
    value: P1Value,
    source_attempt: ServiceAttempt | None,
    source_execution: ServiceExecution | None,
) -> tuple[dict[str, object] | None, str | None]:
    """Build a verifiable source envelope for factory-only P1 values."""
    if not isinstance(value, (ServiceExecution, ReturnOfService)):
        if source_attempt is not None or source_execution is not None:
            _fail("M2_FACTORY_SOURCE_INVALID")
        return None, None
    if not isinstance(source_attempt, ServiceAttempt):
        _fail("M2_FACTORY_SOURCE_REQUIRED")
    if isinstance(value, ServiceExecution):
        if source_execution is not None:
            _fail("M2_FACTORY_SOURCE_INVALID")
        try:
            derived = ServiceExecution.from_attempt(
                attempt=source_attempt,
                service_execution_id=value.service_execution_id,
                executed_at=value.executed_at,
            )
        except Exception as error:
            _fail("M2_FACTORY_SOURCE_INVALID", error)
        if derived.to_dict() != value.to_dict() or derived.fingerprint != value.fingerprint:
            _fail("M2_FACTORY_SOURCE_INVALID")
        envelope: dict[str, object] = {"attempt": source_attempt.to_dict()}
    else:
        if not isinstance(source_execution, ServiceExecution):
            _fail("M2_FACTORY_SOURCE_REQUIRED")
        try:
            derived_execution = ServiceExecution.from_attempt(
                attempt=source_attempt,
                service_execution_id=source_execution.service_execution_id,
                executed_at=source_execution.executed_at,
            )
            if (
                derived_execution.to_dict() != source_execution.to_dict()
                or derived_execution.fingerprint != source_execution.fingerprint
            ):
                _fail("M2_FACTORY_SOURCE_INVALID")
            derived_return = ReturnOfService.from_service_execution(
                instruction_id=value.instruction_id,
                service_execution=derived_execution,
                return_id=value.return_id,
                generated_at=value.generated_at,
            )
        except Exception as error:
            _fail("M2_FACTORY_SOURCE_INVALID", error)
        if derived_return.to_dict() != value.to_dict() or derived_return.fingerprint != value.fingerprint:
            _fail("M2_FACTORY_SOURCE_INVALID")
        envelope = {"attempt": source_attempt.to_dict(), "service_execution": source_execution.to_dict()}
    return envelope, _sha3(envelope)


def _entity_identity(value: P1Value) -> str:
    entity_type = type(value).__name__
    identity = getattr(value, _ENTITY_ID_FIELDS[entity_type])
    if not isinstance(identity, str) or not identity:
        _fail("M2_ENTITY_ID_INVALID")
    return identity


def _record_for(
    value: P1Value,
    source_attempt: ServiceAttempt | None = None,
    source_execution: ServiceExecution | None = None,
) -> dict[str, object]:
    payload = value.to_dict()
    entity_type = type(value).__name__
    identity = _entity_identity(value)
    source_payload, source_fingerprint = _source_canonical(value, source_attempt, source_execution)
    record = {
        "tenant_id": value.tenant_id,
        "entity_type": entity_type,
        "entity_identity": identity,
        "p1_schema": payload["schema"],
        "p1_version": payload["version"],
        "p1_payload": payload,
        "p1_fingerprint": value.fingerprint,
        "evidence_identity": _sha3(
            {
                "tenant_id": value.tenant_id,
                "entity_type": entity_type,
                "entity_identity": identity,
                "p1_fingerprint": value.fingerprint,
                "source_fingerprint": source_fingerprint,
            }
        ),
        "source_payload": source_payload,
        "source_fingerprint": source_fingerprint,
    }
    return record


def _hydrate_record(document: Mapping[str, Any]) -> P1Value:
    payload: dict[str, Any] = dict(document)
    payload.pop("_id", None)
    if set(payload) != _RECORD_FIELDS:
        _fail("M2_RECORD_SCHEMA_INVALID")
    tenant = _tenant(payload["tenant_id"])
    if payload["entity_type"] not in _ENTITY_TYPES:
        _fail("M2_ENTITY_TYPE_UNSUPPORTED")
    if not isinstance(payload["p1_payload"], Mapping):
        _fail("M2_P1_PAYLOAD_INVALID")
    _require_sha3(payload["p1_fingerprint"], "M2_P1_FINGERPRINT_INVALID")
    _require_sha3(payload["evidence_identity"], "M2_EVIDENCE_IDENTITY_INVALID")
    if payload["p1_schema"] != "WILSY-LEGAL-OPERATIONS-LIFECYCLE/V1" or payload["p1_version"] != "v1.0.0-LEGAL-OPERATIONS-LIFECYCLE":
        _fail("M2_P1_VERSION_UNSUPPORTED")
    value: P1Value
    entity_type = payload["entity_type"]
    if entity_type in {"ServiceExecution", "ReturnOfService"}:
        try:
            source = payload["source_payload"]
            if not isinstance(source, Mapping):
                _fail("M2_FACTORY_SOURCE_REQUIRED")
            if entity_type == "ServiceExecution":
                if set(source) != {"attempt"} or not isinstance(source["attempt"], Mapping):
                    _fail("M2_FACTORY_SOURCE_INVALID")
                source_attempt = _hydrate_payload(source["attempt"])
                if not isinstance(source_attempt, ServiceAttempt):
                    _fail("M2_FACTORY_SOURCE_INVALID")
                p1_payload = cast(Mapping[str, Any], payload["p1_payload"])
                value = ServiceExecution.from_attempt(attempt=source_attempt, service_execution_id=_required_text(p1_payload.get("service_execution_id"), "M2_P1_PAYLOAD_INVALID"), executed_at=_parse_timestamp(p1_payload.get("executed_at"), "M2_P1_PAYLOAD_INVALID"))
                if value.to_dict() != p1_payload:
                    _fail("M2_FACTORY_SOURCE_INVALID")
            else:
                if set(source) != {"attempt", "service_execution"} or not isinstance(source["attempt"], Mapping) or not isinstance(source["service_execution"], Mapping):
                    _fail("M2_FACTORY_SOURCE_INVALID")
                source_attempt = _hydrate_payload(source["attempt"])
                if not isinstance(source_attempt, ServiceAttempt):
                    _fail("M2_FACTORY_SOURCE_INVALID")
                source_execution_payload = cast(Mapping[str, Any], source["service_execution"])
                source_execution = ServiceExecution.from_attempt(attempt=source_attempt, service_execution_id=_required_text(source_execution_payload.get("service_execution_id"), "M2_P1_PAYLOAD_INVALID"), executed_at=_parse_timestamp(source_execution_payload.get("executed_at"), "M2_P1_PAYLOAD_INVALID"))
                if source_execution.to_dict() != source_execution_payload:
                    _fail("M2_FACTORY_SOURCE_INVALID")
                p1_payload = cast(Mapping[str, Any], payload["p1_payload"])
                value = ReturnOfService.from_service_execution(instruction_id=_required_text(p1_payload.get("instruction_id"), "M2_P1_PAYLOAD_INVALID"), service_execution=source_execution, return_id=_required_text(p1_payload.get("return_id"), "M2_P1_PAYLOAD_INVALID"), generated_at=_parse_timestamp(p1_payload.get("generated_at"), "M2_P1_PAYLOAD_INVALID"))
        except LegalOperationsLifecycleRegistryError:
            raise
        except Exception as error:
            _fail("M2_FACTORY_SOURCE_INVALID", error)
    else:
        value = _hydrate_payload(payload["p1_payload"])
    if value.tenant_id != tenant or type(value).__name__ != entity_type:
        _fail("M2_TENANT_OR_TYPE_MISMATCH")
    if _entity_identity(value) != payload["entity_identity"]:
        _fail("M2_ENTITY_ID_MISMATCH")
    if value.to_dict() != payload["p1_payload"] or value.fingerprint != payload["p1_fingerprint"]:
        _fail("M2_P1_FINGERPRINT_MISMATCH")
    if _sha3(
        {
            "tenant_id": tenant,
            "entity_type": entity_type,
            "entity_identity": payload["entity_identity"],
            "p1_fingerprint": payload["p1_fingerprint"],
            "source_fingerprint": payload["source_fingerprint"],
        }
    ) != payload["evidence_identity"]:
        _fail("M2_EVIDENCE_IDENTITY_MISMATCH")
    if payload["source_payload"] is not None:
        if entity_type not in {"ServiceExecution", "ReturnOfService"}:
            _fail("M2_FACTORY_SOURCE_INVALID")
        _require_sha3(payload["source_fingerprint"], "M2_FACTORY_SOURCE_INVALID")
        if not isinstance(payload["source_payload"], Mapping) or payload["source_fingerprint"] != _sha3(payload["source_payload"]):
            _fail("M2_FACTORY_SOURCE_INVALID")
    elif payload["source_fingerprint"] is not None:
        _fail("M2_FACTORY_SOURCE_INVALID")
    return value


def _canonical_record(document: Mapping[str, Any]) -> dict[str, Any]:
    """Return one persisted record without Mongo's transport-only ``_id``."""
    result = dict(document)
    result.pop("_id", None)
    return result


class LegalOperationsLifecycleRegistry:
    """Persist, enumerate, and strictly hydrate immutable P1 lifecycle evidence.

    The registry owns no lifecycle transition, current-state selection,
    authorization, transaction, billing, invoice, payment, execution, or
    settlement authority. Every public persistence/read method preserves exact
    tenant scope and propagates caller-owned sessions without starting,
    committing, aborting, or retrying a transaction.
    """

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create tenant-scoped immutable identity indexes only."""
        try:
            collection.create_index(
                [("tenant_id", 1), ("entity_type", 1), ("entity_identity", 1)],
                unique=False,
                name="legal_operations_tenant_entity_history",
            )
            collection.create_index(
                [
                    ("tenant_id", 1),
                    ("entity_type", 1),
                    ("p1_payload.document_id", 1),
                ],
                unique=False,
                name="legal_operations_tenant_document_custody_history",
            )
            collection.create_index([("tenant_id", 1), ("evidence_identity", 1)], unique=True, name="legal_operations_tenant_evidence_unique")
        except PyMongoError as error:
            _fail("M2_PERSISTENCE_UNAVAILABLE", error)

    @staticmethod
    def create(
        value: P1Value,
        collection: Any,
        *,
        session: Any = None,
        source_attempt: ServiceAttempt | None = None,
        source_execution: ServiceExecution | None = None,
    ) -> P1Value:
        """Persist one P1 value or return exact replay; caller owns transactions.

        Factory-only service values require their exact source attempt. Return
        values additionally require the exact source service execution so the
        P1 factory gate is replayed with its original execution timestamp.
        """
        if not isinstance(value, (LegalInstruction, CaseMatter, ProcessDocument, District, SheriffOffice, Deputy, DocumentCustodyEvent, ServiceAttempt, ServiceExecution, ReturnOfService)):
            _fail("M2_P1_VALUE_REQUIRED")
        record = _record_for(value, source_attempt, source_execution)
        query = {"tenant_id": record["tenant_id"], "evidence_identity": record["evidence_identity"]}
        try:
            existing = collection.find_one(query, session=session)
        except PyMongoError as error:
            if session is not None and getattr(session, "in_transaction", False) and _is_transient_transaction_write_conflict(error):
                _fail("M2_RETRY_TRANSACTION_REQUIRED", error)
            _fail("M2_PERSISTENCE_UNAVAILABLE", error)
        if existing is not None:
            current = _hydrate_record(existing)
            if _canonical_record(existing) == record:
                return current
            _fail("M2_REPLAY_CONFLICT")
        provenance_query = {
            "tenant_id": record["tenant_id"],
            "entity_type": record["entity_type"],
            "entity_identity": record["entity_identity"],
            "p1_fingerprint": record["p1_fingerprint"],
        }
        try:
            provenance = collection.find_one(provenance_query, session=session)
        except PyMongoError as error:
            _fail("M2_PERSISTENCE_UNAVAILABLE", error)
        if provenance is not None:
            _hydrate_record(provenance)
            _fail("M2_REPLAY_CONFLICT")
        try:
            collection.insert_one(record, session=session)
        except DuplicateKeyError as error:
            if session is not None and getattr(session, "in_transaction", False):
                _fail("M2_RETRY_TRANSACTION_REQUIRED", error)
            try:
                raced = collection.find_one(query, session=session)
            except PyMongoError as read_error:
                _fail("M2_PERSISTENCE_UNAVAILABLE", read_error)
            if raced is not None:
                current = _hydrate_record(raced)
                if _canonical_record(raced) == record:
                    return current
            _fail("M2_REPLAY_CONFLICT", error)
        except PyMongoError as error:
            if session is not None and getattr(session, "in_transaction", False) and _is_transient_transaction_write_conflict(error):
                _fail("M2_RETRY_TRANSACTION_REQUIRED", error)
            _fail("M2_PERSISTENCE_UNAVAILABLE", error)
        try:
            persisted = collection.find_one(query, session=session)
        except PyMongoError as error:
            _fail("M2_PERSISTENCE_UNAVAILABLE", error)
        if persisted is None:
            _fail("M2_PERSISTENCE_UNAVAILABLE")
        return _hydrate_record(persisted)

    @staticmethod
    def get_entity_history(
        tenant_id: str,
        entity_type: str,
        entity_identity: str,
        collection: Any,
        *,
        session: Any = None,
    ) -> tuple[P1Value, ...]:
        """Read complete immutable history for one exact tenant/type/entity scope.

        This method performs no current-state selection and no mutation. It
        propagates the caller-owned session into one indexed history query,
        strictly hydrates every returned record, rejects any scope divergence
        or corruption, and returns an empty tuple when no record exists for
        the exact tenant/type/entity predicate. Consumers that need "current"
        truth must compose the separate deterministic current-projection
        authority over this complete history. The method has no billing,
        invoice, payment, financial-execution, or settlement authority.
        """
        tenant = _tenant(tenant_id)
        if not isinstance(entity_type, str) or entity_type not in _ENTITY_TYPES:
            _fail("M2_ENTITY_TYPE_UNSUPPORTED")
        if not isinstance(entity_identity, str) or _IDENTITY.fullmatch(entity_identity) is None:
            _fail("M2_ENTITY_ID_INVALID")
        query = {
            "tenant_id": tenant,
            "entity_type": entity_type,
            "entity_identity": entity_identity,
        }
        try:
            documents = list(collection.find(query, session=session))
        except PyMongoError as error:
            _fail("M2_PERSISTENCE_UNAVAILABLE", error)

        history: list[P1Value] = []
        for document in documents:
            if not isinstance(document, Mapping):
                _fail("M2_RECORD_SCHEMA_INVALID")
            value = _hydrate_record(cast(Mapping[str, Any], document))
            if value.tenant_id != tenant:
                _fail("M2_TENANT_MISMATCH")
            if type(value).__name__ != entity_type or _entity_identity(value) != entity_identity:
                _fail("M2_ENTITY_HISTORY_SCOPE_MISMATCH")
            history.append(value)
        return tuple(history)

    @staticmethod
    def get_document_custody_history(
        tenant_id: str,
        document_id: str,
        collection: Any,
        *,
        session: Any = None,
    ) -> tuple[DocumentCustodyEvent, ...]:
        """Read complete custody history for one exact tenant/document scope.

        P2 owns the durable record shape and indexed query. Every matching row
        is strictly hydrated back into a canonical P1 DocumentCustodyEvent,
        tenant/document scope is rechecked after hydration, and the caller-owned
        session is forwarded unchanged. This method deliberately does not sort,
        validate sequence/chronology, choose a current holder, infer receipt,
        allocation, service, billing, payment, execution, or settlement truth.
        Consumers must compose P1 custody-chain validation over the returned
        immutable facts. Exact foreign-tenant evidence is represented as absence.
        """
        tenant = _tenant(tenant_id)
        if not isinstance(document_id, str) or _IDENTITY.fullmatch(document_id) is None:
            _fail("M2_ENTITY_ID_INVALID")
        query = {
            "tenant_id": tenant,
            "entity_type": "DocumentCustodyEvent",
            "p1_payload.document_id": document_id,
        }
        try:
            documents = list(collection.find(query, session=session))
        except PyMongoError as error:
            _fail("M2_PERSISTENCE_UNAVAILABLE", error)

        history: list[DocumentCustodyEvent] = []
        for document in documents:
            if not isinstance(document, Mapping):
                _fail("M2_RECORD_SCHEMA_INVALID")
            value = _hydrate_record(cast(Mapping[str, Any], document))
            if type(value) is not DocumentCustodyEvent:
                _fail("M2_ENTITY_HISTORY_SCOPE_MISMATCH")
            event = cast(DocumentCustodyEvent, value)
            if event.tenant_id != tenant or event.document_id != document_id:
                _fail("M2_ENTITY_HISTORY_SCOPE_MISMATCH")
            history.append(event)
        return tuple(history)

    @staticmethod
    def get(tenant_id: str, evidence_identity: str, collection: Any, *, session: Any = None) -> P1Value:
        """Read one immutable snapshot by exact tenant-scoped evidence identity."""
        tenant = _tenant(tenant_id)
        _require_sha3(evidence_identity, "M2_EVIDENCE_IDENTITY_INVALID")
        try:
            document = collection.find_one({"tenant_id": tenant, "evidence_identity": evidence_identity}, session=session)
        except PyMongoError as error:
            _fail("M2_PERSISTENCE_UNAVAILABLE", error)
        if document is None:
            _fail("M2_EVIDENCE_NOT_FOUND")
        value = _hydrate_record(document)
        if value.tenant_id != tenant:
            _fail("M2_TENANT_MISMATCH")
        return value


__all__ = [
    "COLLECTION",
    "VERSION",
    "LegalOperationsLifecycleRegistry",
    "LegalOperationsLifecycleRegistryError",
]


# ARTIFACT: legal_operations_lifecycle_registry.py
# VERSION: v1.2.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY
# AUTHORITY BOUNDARY: durable P1 evidence persistence, exact entity/custody history enumeration, and strict hydration only.
# TENANT POSTURE: every record and lookup is explicitly tenant-scoped.
# FAIL-CLOSED POSTURE: corruption, divergence, unsupported types, and outages reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT