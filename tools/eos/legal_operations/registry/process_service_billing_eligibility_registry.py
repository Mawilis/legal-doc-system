"""Caller-owned durable registry for P6B billing-eligibility evidence.

TITLE: Wilsy OS Process-Service Billing Eligibility Registry
VERSION: v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Strict persistence and hydration of immutable P6B eligibility records;
         no lifecycle derivation, invoice creation, or money movement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/process_service_billing_eligibility_registry.py
COLLABORATION / OWNERSHIP: P6B persistence only; P1/P2 and P6A remain source
                            authorities; caller owns collection/session/transactions.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY-REGISTRY establishes
           strict tenant-scoped replay, race, and corruption handling.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every read, source lookup, replay, and write is tenant-scoped.
AUTHORITY BOUNDARY: Persistence/composition of P6B evidence only; no invoice,
                    receivable, payment, execution, settlement, or quotation.
TRANSACTION BOUNDARY: Caller supplies session and transaction; this registry
                      never starts, commits, aborts, retries, or owns one.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement;
                              Billing owns invoice truth.
FAIL-CLOSED DECLARATION: Strict schema, source rehydration, tenant isolation,
                         conflict translation, and corruption rejection apply.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Final, NoReturn, cast

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ReturnOfService,
    ServiceAttempt,
    ServiceExecution,
    ServiceExecutionOutcome,
    LifecycleTransitionEvidence,
    ServiceAttemptState,
)
from tools.eos.legal_operations.domain.process_service_billing_eligibility_authority import (
    ProcessServiceBillingEligibility,
    ProcessServiceBillingEligibilityError,
    SCHEMA as P6B_SCHEMA,
    VERSION as P6B_VERSION,
)
from tools.eos.legal_operations.domain.process_service_tariff_authority import FeeLine, TariffAssessment
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry, _hydrate_payload
from tools.eos.legal_operations.registry.process_service_tariff_registry import ProcessServiceTariffRegistry

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY-REGISTRY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-BILLING-ELIGIBILITY-REGISTRY/V1"
COLLECTION: Final[str] = "process_service_billing_eligibility"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN = frozenset({"default", "global", "global_root", "root", "master", "*"})
_PAYLOAD_FIELDS = frozenset({"schema", "version", "entity_type", "tenant_id", "billing_eligibility_id", "tariff_assessment_id", "tariff_assessment_fingerprint", "return_id", "service_execution_id", "attempt_id", "instruction_id", "document_id", "district_id", "jurisdiction_code", "sheriff_office_id", "service_outcome", "tariff_schedule_id", "tariff_version_id", "currency", "eligible_minor_units", "eligibility_at", "source_tariff_assessment_evidence_identity", "source_tariff_assessment_fingerprint", "source_return_evidence_identity", "source_return_fingerprint", "source_execution_evidence_identity", "source_execution_fingerprint"})


class ProcessServiceBillingEligibilityRegistryError(RuntimeError):
    """Stable fail-closed persistence error retaining an optional technical cause."""

    def __init__(self, code: str, cause: BaseException | None = None) -> None:
        """Create one governed error with machine-readable ``code``."""
        self.code = code
        super().__init__(code)
        if cause is not None:
            self.__cause__ = cause


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    raise ProcessServiceBillingEligibilityRegistryError(code, cause)


def _tenant(value: object) -> str:
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None or value.casefold() in _FORBIDDEN:
        _fail("P6B_INVALID_TENANT")
    return value


def _sha3(value: object, code: str = "P6B_FINGERPRINT_INVALID") -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(code)
    return value


def _digest(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _active(session: object) -> bool:
    marker = getattr(session, "in_transaction", False)
    try:
        return bool(marker() if callable(marker) else marker)
    except Exception:
        return False


def _canonical_record(raw: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(raw)
    result.pop("_id", None)
    return result


def _parse_time(value: object) -> datetime:
    if not isinstance(value, str):
        _fail("P6B_SOURCE_PAYLOAD_INVALID")
    try:
        result = datetime.fromisoformat(value)
    except ValueError as error:
        _fail("P6B_SOURCE_PAYLOAD_INVALID", error)
    if result.tzinfo is None or result.utcoffset() is None:
        _fail("P6B_SOURCE_PAYLOAD_INVALID")
    return result


def _assessment(payload: Mapping[str, Any]) -> TariffAssessment:
    fields = {"schema", "version", "entity_type", "tenant_id", "tariff_assessment_id", "return_id", "service_execution_id", "attempt_id", "instruction_id", "document_id", "district_id", "jurisdiction_code", "sheriff_office_id", "service_outcome", "tariff_schedule_id", "tariff_version_id", "tariff_version_fingerprint", "effective_time_source", "effective_at", "fee_lines", "currency", "assessed_total_minor_units", "assessment_at", "source_return_evidence_identity", "source_return_fingerprint"}
    if set(payload) != fields or payload.get("entity_type") != "TariffAssessment" or not isinstance(payload.get("fee_lines"), list):
        _fail("P6B_SOURCE_PAYLOAD_INVALID")
    lines: list[FeeLine] = []
    for raw in cast(list[object], payload["fee_lines"]):
        if not isinstance(raw, Mapping) or set(raw) != {"fee_code", "description", "fee_type", "quantity", "unit_minor_units", "amount_minor_units", "currency", "evidence_basis"}:
            _fail("P6B_SOURCE_PAYLOAD_INVALID")
        lines.append(FeeLine(fee_code=raw["fee_code"], description=raw["description"], fee_type=raw["fee_type"], quantity=raw["quantity"], unit_minor_units=raw["unit_minor_units"], amount_minor_units=raw["amount_minor_units"], currency=raw["currency"], evidence_basis=raw["evidence_basis"]))
    try:
        return TariffAssessment(tenant_id=payload["tenant_id"], tariff_assessment_id=payload["tariff_assessment_id"], return_id=payload["return_id"], service_execution_id=payload["service_execution_id"], attempt_id=payload["attempt_id"], instruction_id=payload["instruction_id"], document_id=payload["document_id"], district_id=payload["district_id"], jurisdiction_code=payload["jurisdiction_code"], sheriff_office_id=payload["sheriff_office_id"], service_outcome=ServiceExecutionOutcome(payload["service_outcome"]), tariff_schedule_id=payload["tariff_schedule_id"], tariff_version_id=payload["tariff_version_id"], tariff_version_fingerprint=payload["tariff_version_fingerprint"], effective_time_source=payload["effective_time_source"], effective_at=_parse_time(payload["effective_at"]), fee_lines=tuple(lines), currency=payload["currency"], assessed_total_minor_units=payload["assessed_total_minor_units"], assessment_at=_parse_time(payload["assessment_at"]), source_return_evidence_identity=payload["source_return_evidence_identity"], source_return_fingerprint=payload["source_return_fingerprint"])
    except Exception as error:
        _fail("P6B_SOURCE_PAYLOAD_INVALID", error)


def _source_objects(source: Mapping[str, Any]) -> tuple[TariffAssessment, ReturnOfService, ServiceExecution, ServiceAttempt]:
    if set(source) != {"assessment", "return", "execution", "attempt"} or any(not isinstance(source[name], Mapping) for name in source):
        _fail("P6B_SOURCE_PAYLOAD_INVALID")
    assessment = _assessment(cast(Mapping[str, Any], source["assessment"]))
    attempt_raw = cast(Mapping[str, Any], source["attempt"])
    try:
        attempt_value = _hydrate_payload(attempt_raw)
    except Exception as error:
        _fail("P6B_SOURCE_PAYLOAD_INVALID", error)
    if type(attempt_value) is not ServiceAttempt:
        _fail("P6B_SOURCE_PAYLOAD_INVALID")
    attempt = cast(ServiceAttempt, attempt_value)
    execution_raw = cast(Mapping[str, Any], source["execution"])
    try:
        execution = ServiceExecution.from_attempt(attempt=attempt, service_execution_id=execution_raw["service_execution_id"], executed_at=_parse_time(execution_raw["executed_at"]))
    except Exception as error:
        _fail("P6B_SOURCE_PAYLOAD_INVALID", error)
    if execution.to_dict() != dict(execution_raw):
        _fail("P6B_SOURCE_PAYLOAD_INVALID")
    return_raw = cast(Mapping[str, Any], source["return"])
    try:
        returned = ReturnOfService.from_service_execution(instruction_id=return_raw["instruction_id"], service_execution=execution, return_id=return_raw["return_id"], generated_at=_parse_time(return_raw["generated_at"]))
    except Exception as error:
        _fail("P6B_SOURCE_PAYLOAD_INVALID", error)
    if returned.to_dict() != dict(return_raw):
        _fail("P6B_SOURCE_PAYLOAD_INVALID")
    return assessment, returned, execution, attempt


def _p2_identity(tenant: str, entity_type: str, identity: str, value: Mapping[str, Any], source: Mapping[str, Any]) -> str:
    """Recompute a P2 evidence identity from its complete canonical envelope."""
    source_fingerprint = _digest(source)
    return _digest({"tenant_id": tenant, "entity_type": entity_type, "entity_identity": identity, "p1_fingerprint": _digest(value), "source_fingerprint": source_fingerprint})


def _record(value: ProcessServiceBillingEligibility, source: Mapping[str, Any]) -> dict[str, object]:
    payload = value.to_dict()
    source_payload = dict(source)
    source_fingerprint = _digest(source_payload)
    evidence_identity = _digest({"tenant_id": value.tenant_id, "entity_type": type(value).__name__, "entity_identity": value.billing_eligibility_id, "fingerprint": value.fingerprint, "source_fingerprint": source_fingerprint})
    return {"schema": SCHEMA, "version": VERSION, "entity_type": type(value).__name__, "tenant_id": value.tenant_id, "entity_identity": value.billing_eligibility_id, "payload": payload, "fingerprint": value.fingerprint, "evidence_identity": evidence_identity, "source_payload": source_payload, "source_fingerprint": source_fingerprint}


def _hydrate(raw: Mapping[str, Any]) -> ProcessServiceBillingEligibility:
    value = _canonical_record(raw)
    required = {"schema", "version", "entity_type", "tenant_id", "entity_identity", "payload", "fingerprint", "evidence_identity", "source_payload", "source_fingerprint"}
    if set(value) != required:
        _fail("P6B_RECORD_SCHEMA_INVALID")
    if value["schema"] != SCHEMA or value["version"] != VERSION or value["entity_type"] != "ProcessServiceBillingEligibility":
        _fail("P6B_RECORD_VERSION_UNSUPPORTED")
    tenant = _tenant(value["tenant_id"])
    payload = value["payload"]
    if not isinstance(payload, Mapping) or set(payload) != _PAYLOAD_FIELDS:
        _fail("P6B_PAYLOAD_SCHEMA_INVALID")
    if payload.get("schema") != "WILSY-PROCESS-SERVICE-BILLING-ELIGIBILITY/V1" or payload.get("version") != "v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY" or payload.get("entity_type") != "ProcessServiceBillingEligibility":
        _fail("P6B_PAYLOAD_SCHEMA_INVALID")
    _sha3(value["fingerprint"], "P6B_RECORD_FINGERPRINT_INVALID")
    _sha3(value["evidence_identity"], "P6B_EVIDENCE_IDENTITY_INVALID")
    source = value["source_payload"]
    if not isinstance(source, Mapping):
        _fail("P6B_SOURCE_PAYLOAD_INVALID")
    _sha3(value["source_fingerprint"], "P6B_SOURCE_FINGERPRINT_INVALID")
    if value["source_fingerprint"] != _digest(source):
        _fail("P6B_SOURCE_FINGERPRINT_INVALID")
    assessment, returned, execution, attempt = _source_objects(source)
    expected_assessment_identity = _digest({"tenant_id": assessment.tenant_id, "entity_type": "TariffAssessment", "entity_identity": assessment.tariff_assessment_id, "fingerprint": assessment.fingerprint})
    expected_execution_identity = _p2_identity(tenant, "ServiceExecution", execution.service_execution_id, execution.to_dict(), {"attempt": attempt.to_dict()})
    expected_return_identity = _p2_identity(tenant, "ReturnOfService", returned.return_id, returned.to_dict(), {"attempt": attempt.to_dict(), "service_execution": execution.to_dict()})
    if payload["source_tariff_assessment_evidence_identity"] != expected_assessment_identity or payload["source_execution_evidence_identity"] != expected_execution_identity or payload["source_return_evidence_identity"] != expected_return_identity:
        _fail("P6B_SOURCE_IDENTITY_MISMATCH")
    try:
        decision = ProcessServiceBillingEligibility.from_sources(assessment=assessment, assessment_evidence_identity=payload["source_tariff_assessment_evidence_identity"], return_of_service=returned, return_evidence_identity=payload["source_return_evidence_identity"], service_execution=execution, execution_evidence_identity=payload["source_execution_evidence_identity"], attempt=attempt, billing_eligibility_id=payload["billing_eligibility_id"], eligibility_at=_parse_time(payload["eligibility_at"]))
    except (ProcessServiceBillingEligibilityError, KeyError) as error:
        _fail("P6B_SOURCE_BINDING_INVALID", error)
    if decision.to_dict() != dict(payload) or decision.fingerprint != value["fingerprint"] or decision.tenant_id != tenant or decision.billing_eligibility_id != value["entity_identity"]:
        _fail("P6B_FINGERPRINT_MISMATCH")
    if _digest({"tenant_id": tenant, "entity_type": "ProcessServiceBillingEligibility", "entity_identity": value["entity_identity"], "fingerprint": value["fingerprint"], "source_fingerprint": value["source_fingerprint"]}) != value["evidence_identity"]:
        _fail("P6B_EVIDENCE_IDENTITY_MISMATCH")
    return decision


class ProcessServiceBillingEligibilityRegistry:
    """Persist immutable P6B records while retaining caller transaction ownership."""

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create tenant-scoped unique evidence and identity indexes."""
        try:
            collection.create_index([("tenant_id", 1), ("evidence_identity", 1)], unique=True, name="p6b_tenant_evidence_unique")
            collection.create_index([("tenant_id", 1), ("entity_type", 1), ("entity_identity", 1)], unique=True, name="p6b_tenant_entity_unique")
        except PyMongoError as error:
            _fail("P6B_PERSISTENCE_UNAVAILABLE", error)

    @staticmethod
    def issue(*, tenant_id: str, assessment_evidence_identity: str, billing_eligibility_id: str, eligibility_at: datetime, assessment_collection: Any, lifecycle_collection: Any, collection: Any, session: Any = None) -> ProcessServiceBillingEligibility:
        """Hydrate exact P6A/P2 sources, derive P6B evidence, and persist it.

        All collection operations receive the caller's session. This method
        never begins or resolves a transaction and translates active-transaction
        write conflicts to ``P6B_RETRY_TRANSACTION_REQUIRED``.
        """
        tenant = _tenant(tenant_id)
        try:
            assessment = ProcessServiceTariffRegistry.get_assessment(tenant, assessment_evidence_identity, assessment_collection, session=session)
        except Exception as error:
            _fail("P6B_CANONICAL_ASSESSMENT_UNAVAILABLE", error)
        try:
            returned = LegalOperationsLifecycleRegistry.get(tenant, assessment.source_return_evidence_identity, lifecycle_collection, session=session)
        except Exception as error:
            _fail("P6B_CANONICAL_RETURN_UNAVAILABLE", error)
        if type(returned) is not ReturnOfService:
            _fail("P6B_CANONICAL_RETURN_REQUIRED")
        execution: ServiceExecution | None = None
        execution_identity: str | None = None
        attempt: ServiceAttempt | None = None
        try:
            execution_rows = lifecycle_collection.find({"tenant_id": tenant, "entity_type": "ServiceExecution", "entity_identity": assessment.service_execution_id}, session=session)
            for row in execution_rows:
                if not isinstance(row, Mapping) or not isinstance(row.get("evidence_identity"), str):
                    continue
                candidate = LegalOperationsLifecycleRegistry.get(tenant, row["evidence_identity"], lifecycle_collection, session=session)
                if type(candidate) is ServiceExecution and candidate.evidence_fingerprint == returned.service_evidence_fingerprint:
                    execution = candidate
                    execution_identity = row["evidence_identity"]
                    break
            attempt_rows = lifecycle_collection.find({"tenant_id": tenant, "entity_type": "ServiceAttempt", "entity_identity": assessment.attempt_id}, session=session)
            for row in attempt_rows:
                if isinstance(row, Mapping) and isinstance(row.get("evidence_identity"), str):
                    candidate = LegalOperationsLifecycleRegistry.get(tenant, row["evidence_identity"], lifecycle_collection, session=session)
                    if type(candidate) is ServiceAttempt and candidate.state is ServiceAttemptState.COMPLETED:
                        attempt = candidate
                        break
        except Exception as error:
            _fail("P6B_CANONICAL_EXECUTION_UNAVAILABLE", error)
        if execution is None or attempt is None:
            _fail("P6B_CANONICAL_EXECUTION_REQUIRED")
        if execution_identity is None:
            _fail("P6B_CANONICAL_EXECUTION_REQUIRED")
        source = {"assessment": assessment.to_dict(), "return": cast(ReturnOfService, returned).to_dict(), "execution": execution.to_dict(), "attempt": attempt.to_dict()}
        decision = ProcessServiceBillingEligibility.from_sources(assessment=assessment, assessment_evidence_identity=assessment_evidence_identity, return_of_service=cast(ReturnOfService, returned), return_evidence_identity=assessment.source_return_evidence_identity, service_execution=execution, execution_evidence_identity=execution_identity, attempt=attempt, billing_eligibility_id=billing_eligibility_id, eligibility_at=eligibility_at)
        record = _record(decision, source)
        query = {"tenant_id": tenant, "evidence_identity": record["evidence_identity"]}
        try:
            existing = collection.find_one(query, session=session)
        except PyMongoError as error:
            _fail("P6B_PERSISTENCE_UNAVAILABLE", error)
        if existing is not None:
            current = _hydrate(existing)
            if _canonical_record(existing) == record:
                return current
            _fail("P6B_REPLAY_CONFLICT")
        try:
            prior = collection.find_one({"tenant_id": tenant, "entity_type": type(decision).__name__, "entity_identity": decision.billing_eligibility_id}, session=session)
        except PyMongoError as error:
            _fail("P6B_PERSISTENCE_UNAVAILABLE", error)
        if prior is not None:
            _hydrate(prior)
            _fail("P6B_REPLAY_CONFLICT")
        try:
            collection.insert_one(record, session=session)
        except DuplicateKeyError as error:
            if _active(session):
                _fail("P6B_RETRY_TRANSACTION_REQUIRED", error)
            try:
                raced = collection.find_one(query, session=session)
            except PyMongoError as read_error:
                _fail("P6B_PERSISTENCE_UNAVAILABLE", read_error)
            if raced is not None and _canonical_record(raced) == record:
                return _hydrate(raced)
            _fail("P6B_REPLAY_CONFLICT", error)
        except PyMongoError as error:
            if _active(session) and error.has_error_label("TransientTransactionError") and not error.has_error_label("UnknownTransactionCommitResult"):
                _fail("P6B_RETRY_TRANSACTION_REQUIRED", error)
            _fail("P6B_PERSISTENCE_UNAVAILABLE", error)
        return _hydrate(record)

    @staticmethod
    def get(tenant_id: str, evidence_identity: str, collection: Any, *, session: Any = None) -> ProcessServiceBillingEligibility:
        """Hydrate one exact tenant-scoped immutable eligibility record."""
        tenant = _tenant(tenant_id)
        _sha3(evidence_identity, "P6B_EVIDENCE_IDENTITY_INVALID")
        try:
            raw = collection.find_one({"tenant_id": tenant, "evidence_identity": evidence_identity}, session=session)
        except PyMongoError as error:
            _fail("P6B_PERSISTENCE_UNAVAILABLE", error)
        if raw is None:
            _fail("P6B_NOT_FOUND")
        return _hydrate(cast(Mapping[str, Any], raw))


__all__ = ["VERSION", "SCHEMA", "COLLECTION", "ProcessServiceBillingEligibilityRegistry", "ProcessServiceBillingEligibilityRegistryError"]

# ARTIFACT: process_service_billing_eligibility_registry.py
# VERSION: v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY-REGISTRY
# AUTHORITY BOUNDARY: strict P6B evidence persistence and hydration only.
# TENANT POSTURE: all records and lookups are tenant-scoped.
# FAIL-CLOSED POSTURE: schema drift, source corruption, replay conflict, and races reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; Billing owns invoice truth.
# END OF WILSY OS SOVEREIGN ARTIFACT
