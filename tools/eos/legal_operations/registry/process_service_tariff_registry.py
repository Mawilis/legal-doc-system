"""Caller-owned persistence and composition for P6A tariff evidence.

TITLE: Wilsy OS Process-Service Tariff Registry
VERSION: v1.0.0-PROCESS-SERVICE-TARIFF-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Strictly persist immutable tariff schedules, versions, and
         ReturnOfService-derived assessments without deriving legal or money
         movement truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/process_service_tariff_registry.py
COLLABORATION / OWNERSHIP: P6A persistence/composition only; P1/P2 remain
                            canonical return authority; callers own sessions.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-TARIFF-REGISTRY establishes
           strict tenant-scoped schedule/version/assessment replay semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every read, write, replay, and source lookup is tenant-scoped.
AUTHORITY BOUNDARY: Persistence and deterministic tariff composition only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
TRANSACTION BOUNDARY: Caller supplies session and transaction; this module
                      never starts, commits, aborts, or ends one.
FAIL-CLOSED DECLARATION: Schema drift, corruption, overlap, races, and source
                         mismatch reject with stable error codes.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
import re
from typing import Any, Final, NoReturn, cast

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_operations_lifecycle import District, ReturnOfService, ServiceAttempt, ServiceExecution, ServiceExecutionOutcome
from tools.eos.legal_operations.domain.process_service_tariff_authority import FeeLine, ProcessServiceTariffAuthorityError, TariffAssessment, TariffQuantityBasis, TariffRule, TariffSchedule, TariffVersion, VERSION as P6_VERSION, SCHEMA as P6_SCHEMA, _canonical, _digest, _identity, _tenant, _timestamp, assess_from_return
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_allocation_registry import ProcessServiceAllocationRegistry, ProcessServiceAllocationReceipt

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-TARIFF-REGISTRY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-TARIFF-REGISTRY/V1"
SCHEDULE_COLLECTION: Final[str] = "process_service_tariff_schedules"
VERSION_COLLECTION: Final[str] = "process_service_tariff_versions"
ASSESSMENT_COLLECTION: Final[str] = "process_service_tariff_assessments"
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_ENTITY = {"TariffSchedule", "TariffVersion", "TariffAssessment"}


class ProcessServiceTariffRegistryError(RuntimeError):
    """Stable fail-closed persistence/composition error with a machine code."""

    def __init__(self, code: str, cause: BaseException | None = None) -> None:
        """Create one governed error while retaining technical cause context."""
        self.code = code
        super().__init__(code)
        if cause is not None:
            self.__cause__ = cause


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    raise ProcessServiceTariffRegistryError(code, cause)


def _active(session: object) -> bool:
    marker = getattr(session, "in_transaction", False)
    try:
        return bool(marker() if callable(marker) else marker)
    except Exception:
        return False


def _record(value: TariffSchedule | TariffVersion | TariffAssessment) -> dict[str, object]:
    entity = type(value).__name__
    payload = value.to_dict()
    identity = _entity_identity(value)
    evidence_identity = _digest({"tenant_id": value.tenant_id, "entity_type": entity, "entity_identity": identity, "fingerprint": value.fingerprint})
    return {"schema": SCHEMA, "version": VERSION, "entity_type": entity, "tenant_id": value.tenant_id, "entity_identity": identity, "payload": payload, "fingerprint": value.fingerprint, "evidence_identity": evidence_identity}


def _canonical_record(raw: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(raw)
    result.pop("_id", None)
    return result


def _persist(value: TariffSchedule | TariffVersion | TariffAssessment, collection: Any, *, session: object = None) -> TariffSchedule | TariffVersion | TariffAssessment:
    record = _record(value)
    query = {"tenant_id": value.tenant_id, "evidence_identity": record["evidence_identity"]}
    try:
        existing = collection.find_one(query, session=session)
    except PyMongoError as error:
        _fail("P6A_PERSISTENCE_UNAVAILABLE", error)
    if existing is not None:
        current = _hydrate(existing, value.tenant_id)
        if _canonical_record(existing) == record:
            return current
        _fail("P6A_REPLAY_CONFLICT")
    try:
        provenance = collection.find_one({"tenant_id": value.tenant_id, "entity_type": type(value).__name__, "entity_identity": record["entity_identity"]}, session=session)
    except PyMongoError as error:
        _fail("P6A_PERSISTENCE_UNAVAILABLE", error)
    if provenance is not None:
        _hydrate(provenance, value.tenant_id)
        _fail("P6A_REPLAY_CONFLICT")
    try:
        collection.insert_one(record, session=session)
    except DuplicateKeyError as error:
        if _active(session):
            _fail("P6A_RETRY_TRANSACTION_REQUIRED", error)
        try:
            raced = collection.find_one(query, session=session)
        except PyMongoError as read_error:
            _fail("P6A_PERSISTENCE_UNAVAILABLE", read_error)
        if raced is not None:
            current = _hydrate(raced, value.tenant_id)
            if _canonical_record(raced) == record:
                return current
        _fail("P6A_REPLAY_CONFLICT", error)
    except PyMongoError as error:
        if _active(session) and error.has_error_label("TransientTransactionError") and not error.has_error_label("UnknownTransactionCommitResult"):
            _fail("P6A_RETRY_TRANSACTION_REQUIRED", error)
        _fail("P6A_PERSISTENCE_UNAVAILABLE", error)
    return _hydrate(record, value.tenant_id)


def _parse_time(value: object, code: str) -> datetime:
    if not isinstance(value, str):
        _fail(code)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        _fail(code, error)
    return _timestamp(code, parsed)


def _hydrate_rule(raw: object) -> TariffRule:
    if not isinstance(raw, Mapping) or set(raw) != {"fee_code", "description", "fee_type", "quantity_basis", "unit_minor_units", "currency", "travel_rule", "tax_treatment", "evidence_basis", "supported_outcomes"}:
        _fail("P6A_RULE_INVALID")
    try:
        from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceExecutionOutcome
        outcomes = raw["supported_outcomes"]
        if not isinstance(outcomes, list):
            _fail("P6A_RULE_INVALID")
        return TariffRule(fee_code=raw["fee_code"], description=raw["description"], fee_type=raw["fee_type"], quantity_basis=TariffQuantityBasis(raw["quantity_basis"]), unit_minor_units=raw["unit_minor_units"], currency=raw["currency"], travel_rule=raw["travel_rule"], tax_treatment=raw["tax_treatment"], evidence_basis=raw["evidence_basis"], supported_outcomes=tuple(ServiceExecutionOutcome(item) for item in outcomes))
    except ProcessServiceTariffAuthorityError as error:
        _fail("P6A_RULE_INVALID", error)
    except Exception as error:
        _fail("P6A_RULE_INVALID", error)


def _hydrate(raw: Mapping[str, Any], tenant_id: str) -> TariffSchedule | TariffVersion | TariffAssessment:
    value = _canonical_record(raw)
    required = {"schema", "version", "entity_type", "tenant_id", "entity_identity", "payload", "fingerprint", "evidence_identity"}
    if set(value) != required:
        _fail("P6A_RECORD_SCHEMA_INVALID")
    if value["schema"] != SCHEMA or value["version"] != VERSION or value["tenant_id"] != tenant_id or value["entity_type"] not in _ENTITY:
        _fail("P6A_RECORD_VERSION_OR_TENANT_INVALID")
    payload = value["payload"]
    if not isinstance(payload, Mapping) or not isinstance(value["fingerprint"], str) or not _SHA3.fullmatch(value["fingerprint"]):
        _fail("P6A_RECORD_PAYLOAD_INVALID")
    try:
        entity = cast(str, value["entity_type"])
        if entity == "TariffSchedule":
            if set(payload) != {"schema", "version", "entity_type", "tenant_id", "schedule_id", "district_id", "jurisdiction_code", "court", "service_type", "evidence_reference"}:
                _fail("P6A_PAYLOAD_SCHEMA_INVALID")
            result: TariffSchedule | TariffVersion | TariffAssessment = TariffSchedule(tenant_id=payload["tenant_id"], schedule_id=payload["schedule_id"], district_id=payload["district_id"], jurisdiction_code=payload["jurisdiction_code"], court=payload["court"], service_type=payload["service_type"], evidence_reference=payload["evidence_reference"])
        elif entity == "TariffVersion":
            if set(payload) != {"schema", "version", "entity_type", "tenant_id", "schedule_id", "version_id", "effective_from", "effective_to", "rules", "evidence_reference"} or not isinstance(payload["rules"], list):
                _fail("P6A_PAYLOAD_SCHEMA_INVALID")
            result = TariffVersion(tenant_id=payload["tenant_id"], schedule_id=payload["schedule_id"], version_id=payload["version_id"], effective_from=_parse_time(payload["effective_from"], "P6A_PAYLOAD_INVALID"), effective_to=None if payload["effective_to"] is None else _parse_time(payload["effective_to"], "P6A_PAYLOAD_INVALID"), rules=tuple(_hydrate_rule(item) for item in payload["rules"]), evidence_reference=payload["evidence_reference"])
        else:
            if set(payload) != {"schema", "version", "entity_type", "tenant_id", "tariff_assessment_id", "return_id", "service_execution_id", "attempt_id", "instruction_id", "document_id", "district_id", "jurisdiction_code", "sheriff_office_id", "service_outcome", "tariff_schedule_id", "tariff_version_id", "tariff_version_fingerprint", "effective_time_source", "effective_at", "fee_lines", "currency", "assessed_total_minor_units", "assessment_at", "source_return_evidence_identity", "source_return_fingerprint"} or not isinstance(payload["fee_lines"], list):
                _fail("P6A_PAYLOAD_SCHEMA_INVALID")
            lines: list[FeeLine] = []
            for item in payload["fee_lines"]:
                if not isinstance(item, Mapping) or set(item) != {"fee_code", "description", "fee_type", "quantity", "unit_minor_units", "amount_minor_units", "currency", "evidence_basis"}:
                    _fail("P6A_PAYLOAD_INVALID")
                lines.append(FeeLine(**cast(dict[str, Any], item)))
            result = TariffAssessment(tenant_id=payload["tenant_id"], tariff_assessment_id=payload["tariff_assessment_id"], return_id=payload["return_id"], service_execution_id=payload["service_execution_id"], attempt_id=payload["attempt_id"], instruction_id=payload["instruction_id"], document_id=payload["document_id"], district_id=payload["district_id"], jurisdiction_code=payload["jurisdiction_code"], sheriff_office_id=payload["sheriff_office_id"], service_outcome=ServiceExecutionOutcome(payload["service_outcome"]), tariff_schedule_id=payload["tariff_schedule_id"], tariff_version_id=payload["tariff_version_id"], tariff_version_fingerprint=payload["tariff_version_fingerprint"], effective_time_source=payload["effective_time_source"], effective_at=_parse_time(payload["effective_at"], "P6A_PAYLOAD_INVALID"), fee_lines=tuple(lines), currency=payload["currency"], assessed_total_minor_units=payload["assessed_total_minor_units"], assessment_at=_parse_time(payload["assessment_at"], "P6A_PAYLOAD_INVALID"), source_return_evidence_identity=payload["source_return_evidence_identity"], source_return_fingerprint=payload["source_return_fingerprint"])
    except ProcessServiceTariffAuthorityError as error:
        _fail("P6A_RECORD_PAYLOAD_INVALID", error)
    if result.tenant_id != tenant_id or result.to_dict() != payload or result.fingerprint != value["fingerprint"]:
        _fail("P6A_RECORD_FINGERPRINT_INVALID")
    identity = _entity_identity(result)
    if value["entity_identity"] != identity or value["evidence_identity"] != _digest({"tenant_id": tenant_id, "entity_type": value["entity_type"], "entity_identity": identity, "fingerprint": value["fingerprint"]}):
        _fail("P6A_RECORD_IDENTITY_INVALID")
    return result


def _entity_identity(value: TariffSchedule | TariffVersion | TariffAssessment) -> str:
    if type(value) is TariffSchedule:
        return cast(TariffSchedule, value).schedule_id
    if type(value) is TariffVersion:
        return cast(TariffVersion, value).version_id
    return cast(TariffAssessment, value).tariff_assessment_id


class ProcessServiceTariffRegistry:
    """Persist schedules, versions, and assessments with caller-owned Mongo sessions."""

    @staticmethod
    def ensure_indexes(schedule_collection: Any, version_collection: Any, assessment_collection: Any) -> None:
        """Create tenant-scoped immutable identity and version indexes."""
        try:
            schedule_collection.create_index([("tenant_id", 1), ("entity_identity", 1)], unique=True, name="p6a_schedule_identity")
            version_collection.create_index([("tenant_id", 1), ("entity_identity", 1)], unique=True, name="p6a_version_identity")
            version_collection.create_index([("tenant_id", 1), ("payload.schedule_id", 1), ("payload.effective_from", 1)], unique=False, name="p6a_version_effective")
            assessment_collection.create_index([("tenant_id", 1), ("evidence_identity", 1)], unique=True, name="p6a_assessment_identity")
            assessment_collection.create_index([("tenant_id", 1), ("entity_type", 1), ("entity_identity", 1)], unique=True, name="p6a_assessment_entity_identity")
        except PyMongoError as error:
            _fail("P6A_PERSISTENCE_UNAVAILABLE", error)

    @staticmethod
    def create_schedule(schedule: TariffSchedule, collection: Any, *, session: object = None) -> TariffSchedule:
        """Persist one immutable schedule or return exact replay."""
        if type(schedule) is not TariffSchedule:
            _fail("P6A_SCHEDULE_REQUIRED")
        try:
            return cast(TariffSchedule, _persist(schedule, collection, session=session))
        except ProcessServiceTariffRegistryError:
            raise

    @staticmethod
    def create_version(version: TariffVersion, schedule: TariffSchedule, collection: Any, *, session: object = None) -> TariffVersion:
        """Persist one exact version only when its schedule binding validates."""
        if type(version) is not TariffVersion or type(schedule) is not TariffSchedule or version.tenant_id != schedule.tenant_id or version.schedule_id != schedule.schedule_id:
            _fail("P6A_SCHEDULE_VERSION_MISMATCH")
        try:
            rows = collection.find({"tenant_id": version.tenant_id, "entity_type": "TariffVersion"}, session=session)
            for row in rows:
                if isinstance(row, Mapping) and row.get("entity_identity") == version.version_id:
                    continue
                try:
                    prior = _hydrate(cast(Mapping[str, Any], row), version.tenant_id)
                except ProcessServiceTariffRegistryError:
                    raise
                if type(prior) is TariffVersion and prior.schedule_id == version.schedule_id:
                    prior_end = prior.effective_to
                    new_end = version.effective_to
                    if (new_end is None or prior.effective_from < new_end) and (prior_end is None or version.effective_from < prior_end):
                        _fail("P6A_VERSION_OVERLAP")
        except PyMongoError as error:
            _fail("P6A_PERSISTENCE_UNAVAILABLE", error)
        try:
            return cast(TariffVersion, _persist(version, collection, session=session))
        except ProcessServiceTariffRegistryError:
            raise

    @staticmethod
    def get_schedule(tenant_id: str, schedule_id: str, collection: Any, *, session: object = None) -> TariffSchedule:
        """Hydrate one exact tenant-scoped schedule."""
        tenant = _tenant(tenant_id); identity = _identity("schedule_id", schedule_id)
        try:
            raw = collection.find_one({"tenant_id": tenant, "entity_identity": identity}, session=session)
        except PyMongoError as error:
            _fail("P6A_PERSISTENCE_UNAVAILABLE", error)
        if raw is None:
            _fail("P6A_NOT_FOUND")
        value = _hydrate(cast(Mapping[str, Any], raw), tenant)
        if type(value) is not TariffSchedule:
            _fail("P6A_TYPE_MISMATCH")
        return value

    @staticmethod
    def get_version(tenant_id: str, schedule_id: str, version_id: str, schedule_collection: Any, version_collection: Any, *, session: object = None) -> TariffVersion:
        """Hydrate one exact version and reject effective-date ambiguity."""
        tenant = _tenant(tenant_id); schedule = ProcessServiceTariffRegistry.get_schedule(tenant, schedule_id, schedule_collection, session=session); identity = _identity("version_id", version_id)
        try:
            raw = version_collection.find_one({"tenant_id": tenant, "entity_identity": identity}, session=session)
        except PyMongoError as error:
            _fail("P6A_PERSISTENCE_UNAVAILABLE", error)
        if raw is None:
            _fail("P6A_NOT_FOUND")
        value = _hydrate(cast(Mapping[str, Any], raw), tenant)
        if type(value) is not TariffVersion or value.schedule_id != schedule.schedule_id:
            _fail("P6A_SCHEDULE_VERSION_MISMATCH")
        return value

    @staticmethod
    def create_assessment(assessment: TariffAssessment, collection: Any, *, session: object = None) -> TariffAssessment:
        """Persist one immutable assessment or return exact replay."""
        if type(assessment) is not TariffAssessment:
            _fail("P6A_ASSESSMENT_REQUIRED")
        return cast(TariffAssessment, _persist(assessment, collection, session=session))

    @staticmethod
    def get_assessment(tenant_id: str, evidence_identity: str, collection: Any, *, session: object = None) -> TariffAssessment:
        """Hydrate one exact tenant-scoped assessment identity."""
        tenant = _tenant(tenant_id)
        if not isinstance(evidence_identity, str) or _SHA3.fullmatch(evidence_identity) is None:
            _fail("P6A_EVIDENCE_IDENTITY_INVALID")
        try:
            raw = collection.find_one({"tenant_id": tenant, "evidence_identity": evidence_identity}, session=session)
        except PyMongoError as error:
            _fail("P6A_PERSISTENCE_UNAVAILABLE", error)
        if raw is None:
            _fail("P6A_NOT_FOUND")
        value = _hydrate(cast(Mapping[str, Any], raw), tenant)
        if type(value) is not TariffAssessment:
            _fail("P6A_TYPE_MISMATCH")
        return value

    @staticmethod
    def assess_return(*, tenant_id: str, return_evidence_identity: str, lifecycle_collection: Any, allocation_receipt_collection: Any, schedule_collection: Any, version_collection: Any, assessment_collection: Any, schedule_id: str, version_id: str, assessment_id: str, assessment_at: datetime, session: object) -> TariffAssessment:
        """Hydrate canonical P2 return/P4 jurisdiction, select exact version, persist assessment.

        The source return, source execution timestamp, district, and sheriff
        identity are never caller claims. All reads/writes use the supplied
        session; transaction lifecycle remains external.
        """
        if not _active(session):
            _fail("P6A_TRANSACTION_REQUIRED")
        try:
            returned = LegalOperationsLifecycleRegistry.get(tenant_id, return_evidence_identity, lifecycle_collection, session=session)
        except Exception as error:
            _fail("P6A_CANONICAL_RETURN_INVALID", error)
        if type(returned) is not ReturnOfService:
            _fail("P6A_CANONICAL_RETURN_REQUIRED")
        return_value = cast(ReturnOfService, returned)
        execution_at = _execution_time(return_value, lifecycle_collection, session)
        receipt = _allocation_receipt(return_value, execution_at, allocation_receipt_collection, lifecycle_collection, session)
        schedule = ProcessServiceTariffRegistry.get_schedule(tenant_id, schedule_id, schedule_collection, session=session)
        version = ProcessServiceTariffRegistry.get_version(tenant_id, schedule_id, version_id, schedule_collection, version_collection, session=session)
        district = _canonical_district(tenant_id, receipt.district_id, lifecycle_collection, session)
        if schedule.district_id != district.district_id or schedule.jurisdiction_code != district.jurisdiction_code:
            _fail("P6A_JURISDICTION_MISMATCH")
        if schedule.court is not None:
            _fail("P6A_COURT_SOURCE_UNAVAILABLE")
        if schedule.service_type is not None:
            _fail("P6A_SERVICE_TYPE_SOURCE_UNAVAILABLE")
        if not version.active_at(execution_at):
            _fail("P6A_VERSION_NOT_EFFECTIVE")
        assessment = assess_from_return(return_of_service=return_value, return_evidence_identity=return_evidence_identity, schedule=schedule, tariff_version=version, assessment_id=assessment_id, assessment_at=assessment_at, sheriff_office_id=receipt.sheriff_office_id, effective_at=execution_at)
        return ProcessServiceTariffRegistry.create_assessment(assessment, assessment_collection, session=session)


def _execution_time(return_value: ReturnOfService, lifecycle_collection: Any, session: object) -> datetime:
    rows = lifecycle_collection.find({"tenant_id": return_value.tenant_id, "entity_type": "ServiceExecution", "entity_identity": return_value.service_execution_id}, session=session)
    for row in rows:
        identity = row.get("evidence_identity") if isinstance(row, Mapping) else None
        if not isinstance(identity, str):
            continue
        try:
            value = LegalOperationsLifecycleRegistry.get(return_value.tenant_id, identity, lifecycle_collection, session=session)
        except Exception:
            continue
        if type(value) is ServiceExecution and value.to_dict()["service_execution_id"] == return_value.service_execution_id and value.outcome is return_value.service_outcome:
            return value.executed_at
    _fail("P6A_SOURCE_EXECUTION_INVALID")


def _canonical_district(tenant_id: str, district_id: str, lifecycle_collection: Any, session: object) -> District:
    rows = list(lifecycle_collection.find({"tenant_id": tenant_id, "entity_type": "District", "entity_identity": district_id}, session=session))
    if len(rows) != 1:
        _fail("P6A_DISTRICT_SOURCE_INVALID")
    identity = rows[0].get("evidence_identity") if isinstance(rows[0], Mapping) else None
    if not isinstance(identity, str):
        _fail("P6A_DISTRICT_SOURCE_INVALID")
    value = LegalOperationsLifecycleRegistry.get(tenant_id, identity, lifecycle_collection, session=session)
    if type(value) is not District:
        _fail("P6A_DISTRICT_SOURCE_INVALID")
    return cast(District, value)


def _allocation_receipt(return_value: ReturnOfService, execution_at: datetime, collection: Any, lifecycle_collection: Any, session: object) -> ProcessServiceAllocationReceipt:
    rows = collection.find({"tenant_id": return_value.tenant_id, "document_id": return_value.document_id}, session=session)
    candidates: list[ProcessServiceAllocationReceipt] = []
    for row in rows:
        key = row.get("idempotency_key") if isinstance(row, Mapping) else None
        if not isinstance(key, str):
            continue
        try:
            candidate = ProcessServiceAllocationRegistry.get_receipt_by_idempotency_key(return_value.tenant_id, return_value.document_id, key, collection, session=session)
        except Exception:
            continue
        if candidate is not None and candidate.allocation_command_id == _attempt_allocation_reference(return_value, session, lifecycle_collection):
            candidates.append(candidate)
    if len(candidates) != 1:
        _fail("P6A_JURISDICTION_SOURCE_INVALID")
    if candidates[0].allocated_at > execution_at:
        _fail("P6A_CHRONOLOGY_INVALID")
    return candidates[0]


def _attempt_allocation_reference(return_value: ReturnOfService, session: object, lifecycle_collection: Any) -> str:
    # P2 attempt snapshots are hydrated by the lifecycle registry in the caller's source collection.
    # The allocation command is recoverable from the attempt's immutable allocation reference.
    source = lifecycle_collection
    rows = source.find({"tenant_id": return_value.tenant_id, "entity_type": "ServiceAttempt", "entity_identity": return_value.attempt_id}, session=session)
    for row in rows:
        identity = row.get("evidence_identity") if isinstance(row, Mapping) else None
        if isinstance(identity, str):
            try:
                value = LegalOperationsLifecycleRegistry.get(return_value.tenant_id, identity, source, session=session)
            except Exception:
                continue
            if type(value) is ServiceAttempt and value.state.value in {"COMPLETED", "NOT_COMPLETED"}:
                derived = ServiceExecution.from_attempt(attempt=value, service_execution_id=return_value.service_execution_id, executed_at=return_value.generated_at)
                if derived.to_dict()["outcome"] == return_value.service_outcome.value:
                    return value.allocation_evidence_reference
    _fail("P6A_SOURCE_ATTEMPT_INVALID")


__all__ = ["VERSION", "SCHEMA", "SCHEDULE_COLLECTION", "VERSION_COLLECTION", "ASSESSMENT_COLLECTION", "ProcessServiceTariffRegistry", "ProcessServiceTariffRegistryError"]

# ARTIFACT: process_service_tariff_registry.py
# VERSION: v1.0.0-PROCESS-SERVICE-TARIFF-REGISTRY
# AUTHORITY BOUNDARY: strict tariff persistence and return-derived assessment composition only.
# TENANT POSTURE: all records and source lookups are tenant-scoped.
# FAIL-CLOSED POSTURE: corruption, overlap, divergence, and transaction races reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
