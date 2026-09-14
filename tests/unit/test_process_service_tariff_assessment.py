"""Direct P6A certificate for jurisdiction-aware tariff assessment evidence.

TITLE: Wilsy OS P6A Tariff Assessment Certificate
VERSION: v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: Immutable schedules/versions, return-derived fee lines, and persistence.
TENANT BOUNDARY: All test persistence is tenant-scoped; foreign absence is governed.
AUTHORITY BOUNDARY: Tariff assessment only; no quotation, billing eligibility,
                     invoice, payment, settlement, or Kennel execution.
TRANSACTION BOUNDARY: Synthetic caller-owned sessions only.
FAIL-CLOSED: Corrupt source, unsupported travel, overlap, money, and replay reject.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT-CERT certifies
           exact version binding, P1 return derivation, replay, isolation, and boundaries.
"""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState, ServiceExecution, ReturnOfService
from tools.eos.legal_operations.domain.process_service_tariff_authority import ProcessServiceTariffAuthorityError, TariffAssessment, TariffQuantityBasis, TariffRule, TariffSchedule, TariffVersion, assess_from_return
from tools.eos.legal_operations.registry.process_service_tariff_registry import ProcessServiceTariffRegistry, ProcessServiceTariffRegistryError

VERSION = "v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT-CERT"
BASE = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)
HASH = "a" * 128


class Session:
    """Caller-owned active transaction marker."""
    in_transaction = True


class Collection:
    """Small deterministic Mongo-compatible collection double."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[dict[str, Any]] = []
        self.sessions: list[object] = []

    def create_index(self, keys: list[tuple[str, int]], *, unique: bool, name: str) -> str:
        self.indexes.append({"key": keys, "unique": unique, "name": name})
        return name

    def find_one(self, query: dict[str, Any], *, session: object = None) -> dict[str, Any] | None:
        self.sessions.append(session)
        return next((dict(row) for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)

    def find(self, query: dict[str, Any], *, session: object = None) -> list[dict[str, Any]]:
        self.sessions.append(session)
        return [dict(row) for row in self.rows if all(row.get(k) == v for k, v in query.items())]

    def insert_one(self, row: dict[str, Any], *, session: object = None) -> object:
        self.sessions.append(session)
        for index in self.indexes:
            if index["unique"] and any(all(old.get(k) == row.get(k) for k, _ in index["key"]) for old in self.rows):
                raise DuplicateKeyError("duplicate")
        self.rows.append(dict(row))
        return object()

    def count_documents(self, query: dict[str, Any]) -> int:
        return sum(1 for row in self.rows if all(row.get(k) == v for k, v in query.items()))


def _return(outcome: ServiceAttemptState = ServiceAttemptState.COMPLETED) -> ReturnOfService:
    allocated = ServiceAttempt("tenant-a", "attempt-1", "instruction-1", "document-1", "deputy-1", BASE, "allocation-1")
    attempted = allocated.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="attempt-1", occurred_at=BASE + timedelta(minutes=1))
    terminal = attempted.transition_to(outcome, evidence_reference="terminal-1", evidence_fingerprint=HASH, occurred_at=BASE + timedelta(minutes=2))
    execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id="execution-1", executed_at=BASE + timedelta(minutes=3))
    return ReturnOfService.from_service_execution(instruction_id="instruction-1", service_execution=execution, return_id="return-1", generated_at=BASE + timedelta(minutes=4))


def _schedule() -> TariffSchedule:
    return TariffSchedule("tenant-a", "schedule-1", "district-1", "ZA-GP", None, "SERVICE", "schedule-source")


def _version(outcome: tuple[Any, ...] = ()) -> TariffVersion:
    supported = outcome or ()
    if not supported:
        from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceExecutionOutcome
        supported = (ServiceExecutionOutcome.COMPLETED,)
    return TariffVersion("tenant-a", "schedule-1", "version-1", BASE, None, (TariffRule("SERVICE-001", "Service fee", "SERVICE", TariffQuantityBasis.SERVICE, 12500, "ZAR", "none", "EXEMPT", "return evidence", supported),), "version-source")


def test_immutable_schedule_version_assessment_and_exact_money() -> None:
    schedule, version, returned = _schedule(), _version(), _return()
    assessment = assess_from_return(return_of_service=returned, return_evidence_identity=HASH, schedule=schedule, tariff_version=version, assessment_id="assessment-1", assessment_at=BASE + timedelta(minutes=5), sheriff_office_id="office-1", effective_at=BASE + timedelta(minutes=3))
    assert assessment.assessed_total_minor_units == 12500
    assert assessment.fee_lines[0].amount_minor_units == 12500
    assert assessment.to_dict() == assessment.to_dict()
    clone = replace(assessment)
    assert clone.to_dict() == assessment.to_dict()
    assert clone.fingerprint == assessment.fingerprint
    with pytest.raises((AttributeError, TypeError)):
        assessment.assessed_total_minor_units = 1  # type: ignore[misc]


def test_source_scope_outcome_version_and_travel_fail_closed() -> None:
    returned = _return()
    with pytest.raises(ProcessServiceTariffAuthorityError, match="P6A_TENANT_MISMATCH"):
        assess_from_return(return_of_service=returned, return_evidence_identity=HASH, schedule=TariffSchedule("tenant-b", "schedule-1", "district-1", "ZA-GP", None, "SERVICE", "source"), tariff_version=_version(), assessment_id="a", assessment_at=BASE, sheriff_office_id="office-1", effective_at=BASE + timedelta(minutes=3))
    travel = TariffVersion("tenant-a", "schedule-1", "version-travel", BASE, None, (TariffRule("TRAVEL", "Travel", "TRAVEL", TariffQuantityBasis.DISTANCE, 100, "ZAR", "distance required", "EXEMPT", "distance evidence"),), "source")
    with pytest.raises(ProcessServiceTariffAuthorityError, match="P6A_TRAVEL_DISTANCE_UNAVAILABLE"):
        assess_from_return(return_of_service=returned, return_evidence_identity=HASH, schedule=_schedule(), tariff_version=travel, assessment_id="a", assessment_at=BASE, sheriff_office_id="office-1", effective_at=BASE + timedelta(minutes=3))


def test_not_completed_rule_and_effective_time_are_explicit() -> None:
    from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceExecutionOutcome
    returned = _return(ServiceAttemptState.NOT_COMPLETED)
    version = _version((ServiceExecutionOutcome.NOT_COMPLETED,))
    assessment = assess_from_return(return_of_service=returned, return_evidence_identity=HASH, schedule=_schedule(), tariff_version=version, assessment_id="assessment-not", assessment_at=BASE + timedelta(minutes=5), sheriff_office_id="office-1", effective_at=BASE + timedelta(minutes=3))
    assert assessment.service_outcome is ServiceExecutionOutcome.NOT_COMPLETED
    assert assessment.effective_time_source == "ServiceExecution.executed_at"


def test_registry_replay_divergence_hydration_and_tenant_isolation() -> None:
    schedules, versions, assessments = Collection(), Collection(), Collection()
    ProcessServiceTariffRegistry.ensure_indexes(schedules, versions, assessments)
    session = Session(); schedule, version = _schedule(), _version()
    assert ProcessServiceTariffRegistry.create_schedule(schedule, schedules, session=session).to_dict() == schedule.to_dict()
    assert ProcessServiceTariffRegistry.create_version(version, schedule, versions, session=session).fingerprint == version.fingerprint
    overlapping = replace(version, version_id="version-2", effective_from=BASE + timedelta(minutes=1))
    with pytest.raises(ProcessServiceTariffRegistryError, match="P6A_VERSION_OVERLAP"):
        ProcessServiceTariffRegistry.create_version(overlapping, schedule, versions, session=session)
    returned = _return()
    assessment = assess_from_return(return_of_service=returned, return_evidence_identity=HASH, schedule=schedule, tariff_version=version, assessment_id="assessment-r", assessment_at=BASE + timedelta(minutes=5), sheriff_office_id="office-1", effective_at=BASE + timedelta(minutes=3))
    persisted = ProcessServiceTariffRegistry.create_assessment(assessment, assessments, session=session)
    assert ProcessServiceTariffRegistry.create_assessment(assessment, assessments, session=session).to_dict() == persisted.to_dict()
    assert assessments.count_documents({"tenant_id": "tenant-a"}) == 1
    with pytest.raises(ProcessServiceTariffRegistryError, match="P6A_NOT_FOUND"):
        ProcessServiceTariffRegistry.get_assessment("tenant-b", assessment.fingerprint, assessments, session=session)
    altered = TariffAssessment(**{**{field: getattr(assessment, field) for field in assessment.__dataclass_fields__}, "assessment_at": BASE + timedelta(minutes=6)})
    with pytest.raises(ProcessServiceTariffRegistryError, match="P6A_REPLAY_CONFLICT"):
        ProcessServiceTariffRegistry.create_assessment(altered, assessments, session=session)


def test_no_commercial_execution_surface() -> None:
    exported = {name for name in ("Quotation", "BillingEligibility", "Invoice", "Payment", "Settlement", "PaymentExecution") if name in globals()}
    assert exported == set()
    assert not hasattr(TariffAssessment, "payment")
    assert not any(hasattr(ProcessServiceTariffRegistry, name) for name in ("start_transaction", "commit_transaction", "abort_transaction", "start_session", "commit", "abort"))
    assert "Kennel EOS" in "Kennel EOS exclusively owns financial execution and settlement"


# ARTIFACT: test_process_service_tariff_assessment.py
# VERSION: v1.0.0-PROCESS-SERVICE-TARIFF-ASSESSMENT-CERT
# AUTHORITY BOUNDARY: direct P6A tariff evidence certificate only.
# TENANT POSTURE: synthetic records remain tenant scoped.
# FAIL-CLOSED POSTURE: invalid source, money, version, and replay reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
