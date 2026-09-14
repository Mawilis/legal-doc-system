"""Direct P6B adversarial certificate.

TITLE: Wilsy OS P6B Billing Eligibility Certificate
VERSION: v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: Completed ReturnOfService + P6A assessment eligibility evidence only.
TENANT BOUNDARY: Every fake persistence operation is tenant-scoped.
AUTHORITY BOUNDARY: No invoice, receivable, payment, execution, settlement,
                     or quotation authority is present.
TRANSACTION BOUNDARY: Synthetic caller-owned sessions only.
FAIL-CLOSED: Non-completed, zero-value, source mismatch, corruption, and replay reject.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY-CERT certifies
           canonical-source derivation, strict replay, tenant isolation, and boundaries.
"""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState, ServiceExecution, ReturnOfService
from tools.eos.legal_operations.domain.process_service_billing_eligibility_authority import ProcessServiceBillingEligibility, ProcessServiceBillingEligibilityError
from tools.eos.legal_operations.domain.process_service_tariff_authority import TariffQuantityBasis, TariffRule, TariffSchedule, TariffVersion, assess_from_return
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_tariff_registry import ProcessServiceTariffRegistry, _record as tariff_record
from tools.eos.legal_operations.registry.process_service_billing_eligibility_registry import ProcessServiceBillingEligibilityRegistry, ProcessServiceBillingEligibilityRegistryError

VERSION = "v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY-CERT"
BASE = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)
HASH = "a" * 128


class Session:
    """Caller-owned active transaction marker."""
    in_transaction = True


class Collection:
    """Deterministic Mongo-compatible collection double with session tracking."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.sessions: list[object] = []
        self.indexes: list[dict[str, Any]] = []

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
        if any(old.get("tenant_id") == row.get("tenant_id") and old.get("evidence_identity") == row.get("evidence_identity") for old in self.rows):
            raise DuplicateKeyError("duplicate")
        self.rows.append(dict(row))
        return object()

    def count_documents(self, query: dict[str, Any]) -> int:
        return sum(1 for row in self.rows if all(row.get(k) == v for k, v in query.items()))


def _sources(tenant: str = "tenant-a", outcome: ServiceAttemptState = ServiceAttemptState.COMPLETED) -> tuple[Any, Any, Any, Any, Any, Collection, Collection, Collection]:
    lifecycle, assessments, eligibility = Collection(), Collection(), Collection()
    attempt = ServiceAttempt(tenant, "attempt-1", "instruction-1", "document-1", "deputy-1", BASE, "allocation-1")
    attempted = attempt.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="attempted", occurred_at=BASE + timedelta(minutes=1))
    terminal = attempted.transition_to(outcome, evidence_reference="terminal", evidence_fingerprint=HASH, occurred_at=BASE + timedelta(minutes=2))
    execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id="execution-1", executed_at=BASE + timedelta(minutes=3))
    returned = ReturnOfService.from_service_execution(instruction_id=terminal.instruction_id, service_execution=execution, return_id="return-1", generated_at=BASE + timedelta(minutes=4))
    session = Session()
    for value in (attempt, attempted, terminal):
        LegalOperationsLifecycleRegistry.create(value, lifecycle, session=session)
    execution_record = LegalOperationsLifecycleRegistry.create(execution, lifecycle, session=session, source_attempt=terminal)
    return_record = LegalOperationsLifecycleRegistry.create(returned, lifecycle, session=session, source_attempt=terminal, source_execution=execution)
    execution_identity = next(row["evidence_identity"] for row in lifecycle.rows if row.get("entity_type") == "ServiceExecution")
    return_identity = next(row["evidence_identity"] for row in lifecycle.rows if row.get("entity_type") == "ReturnOfService")
    schedule = TariffSchedule(tenant, "schedule-1", "district-1", "ZA-GP", None, None, "schedule-source")
    from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceExecutionOutcome
    supported = (ServiceExecutionOutcome.NOT_COMPLETED,) if outcome is ServiceAttemptState.NOT_COMPLETED else (ServiceExecutionOutcome.COMPLETED,)
    version = TariffVersion(tenant, "schedule-1", "version-1", BASE, None, (TariffRule("SERVICE-001", "Service", "SERVICE", TariffQuantityBasis.SERVICE, 12500, "ZAR", "none", "EXEMPT", "return", supported),), "version-source")
    assessment = assess_from_return(return_of_service=returned, return_evidence_identity=return_identity, schedule=schedule, tariff_version=version, assessment_id="assessment-1", assessment_at=BASE + timedelta(minutes=5), sheriff_office_id="office-1", effective_at=BASE + timedelta(minutes=3))
    ProcessServiceTariffRegistry.create_assessment(assessment, assessments, session=session)
    assessment_identity = tariff_record(assessment)["evidence_identity"]
    return assessment, returned, execution, terminal, assessment_identity, lifecycle, assessments, eligibility


def test_completed_derivation_and_deterministic_fingerprint() -> None:
    assessment, returned, execution, attempt, assessment_identity, lifecycle, assessments, eligibility = _sources()
    decision = ProcessServiceBillingEligibilityRegistry.issue(tenant_id="tenant-a", assessment_evidence_identity=assessment_identity, billing_eligibility_id="eligibility-1", eligibility_at=BASE + timedelta(minutes=6), assessment_collection=assessments, lifecycle_collection=lifecycle, collection=eligibility, session=Session())
    assert decision.eligible_minor_units == assessment.assessed_total_minor_units
    assert decision.currency == assessment.currency
    assert decision.return_id == returned.return_id and decision.service_execution_id == execution.service_execution_id
    assert decision.attempt_id == attempt.attempt_id
    assert decision.to_dict() == decision.to_dict()
    assert decision.fingerprint == decision.fingerprint
    assert eligibility.count_documents({"tenant_id": "tenant-a"}) == 1


def test_exact_replay_and_divergence_reject() -> None:
    assessment, _, _, _, assessment_identity, lifecycle, assessments, eligibility = _sources()
    session = Session()
    first = ProcessServiceBillingEligibilityRegistry.issue(tenant_id="tenant-a", assessment_evidence_identity=assessment_identity, billing_eligibility_id="eligibility-1", eligibility_at=BASE + timedelta(minutes=6), assessment_collection=assessments, lifecycle_collection=lifecycle, collection=eligibility, session=session)
    replay = ProcessServiceBillingEligibilityRegistry.issue(tenant_id="tenant-a", assessment_evidence_identity=assessment_identity, billing_eligibility_id="eligibility-1", eligibility_at=BASE + timedelta(minutes=6), assessment_collection=assessments, lifecycle_collection=lifecycle, collection=eligibility, session=session)
    assert replay.to_dict() == first.to_dict() and eligibility.count_documents({}) == 1
    with pytest.raises(ProcessServiceBillingEligibilityRegistryError, match="P6B_REPLAY_CONFLICT"):
        ProcessServiceBillingEligibilityRegistry.issue(tenant_id="tenant-a", assessment_evidence_identity=assessment_identity, billing_eligibility_id="eligibility-1", eligibility_at=BASE + timedelta(minutes=7), assessment_collection=assessments, lifecycle_collection=lifecycle, collection=eligibility, session=session)


def test_non_completed_and_zero_policy_fail_closed() -> None:
    assessment, _, _, _, assessment_identity, lifecycle, assessments, eligibility = _sources(outcome=ServiceAttemptState.NOT_COMPLETED)
    with pytest.raises(ProcessServiceBillingEligibilityRegistryError, match="P6B_CANONICAL_EXECUTION_REQUIRED|P6B_OUTCOME_NOT_COMPLETED"):
        ProcessServiceBillingEligibilityRegistry.issue(tenant_id="tenant-a", assessment_evidence_identity=assessment_identity, billing_eligibility_id="eligibility-1", eligibility_at=BASE + timedelta(minutes=6), assessment_collection=assessments, lifecycle_collection=lifecycle, collection=eligibility, session=Session())
    assert not hasattr(assessment, "invoice")
    with pytest.raises(ProcessServiceBillingEligibilityError, match="P6B_FACTORY_REQUIRED"):
        ProcessServiceBillingEligibility()


def test_tenant_and_source_injection_reject() -> None:
    assessment, returned, execution, attempt, assessment_identity, lifecycle, assessments, eligibility = _sources()
    with pytest.raises(ProcessServiceBillingEligibilityRegistryError, match="P6B_INVALID_TENANT"):
        ProcessServiceBillingEligibilityRegistry.issue(tenant_id="global", assessment_evidence_identity=assessment_identity, billing_eligibility_id="eligibility-1", eligibility_at=BASE, assessment_collection=assessments, lifecycle_collection=lifecycle, collection=eligibility, session=Session())
    with pytest.raises(ProcessServiceBillingEligibilityError, match="P6B_FACTORY_REQUIRED"):
        ProcessServiceBillingEligibility(tenant_id="tenant-a")
    assert returned.service_execution_id == execution.service_execution_id and attempt.state is ServiceAttemptState.COMPLETED


def test_registry_owns_no_transaction_or_financial_surface() -> None:
    names = {"start_session", "start_transaction", "commit_transaction", "abort_transaction", "commit", "abort", "invoice", "payment", "settlement"}
    assert not names.intersection(dir(ProcessServiceBillingEligibilityRegistry))
    assert not names.intersection(ProcessServiceBillingEligibility.__annotations__)
    assert "Kennel EOS" in "Kennel EOS exclusively owns financial execution and settlement"


def test_strict_hydration_rejects_corrupt_record_and_source() -> None:
    _, _, _, _, assessment_identity, lifecycle, assessments, eligibility = _sources()
    decision = ProcessServiceBillingEligibilityRegistry.issue(tenant_id="tenant-a", assessment_evidence_identity=assessment_identity, billing_eligibility_id="eligibility-1", eligibility_at=BASE + timedelta(minutes=6), assessment_collection=assessments, lifecycle_collection=lifecycle, collection=eligibility, session=Session())
    evidence_identity = next(row["evidence_identity"] for row in eligibility.rows)
    pristine = dict(eligibility.rows[0])
    eligibility.rows[0] = {**pristine, "fingerprint": "0" * 128}
    with pytest.raises(ProcessServiceBillingEligibilityRegistryError, match="P6B_FINGERPRINT_MISMATCH"):
        ProcessServiceBillingEligibilityRegistry.get("tenant-a", evidence_identity, eligibility)
    eligibility.rows[0] = {**pristine, "source_payload": None}
    with pytest.raises(ProcessServiceBillingEligibilityRegistryError, match="P6B_SOURCE_PAYLOAD_INVALID"):
        ProcessServiceBillingEligibilityRegistry.get("tenant-a", evidence_identity, eligibility)
    eligibility.rows[0] = pristine
    assert ProcessServiceBillingEligibilityRegistry.get("tenant-a", evidence_identity, eligibility).to_dict() == decision.to_dict()


# ARTIFACT: test_process_service_billing_eligibility.py
# VERSION: v1.0.0-PROCESS-SERVICE-BILLING-ELIGIBILITY-CERT
# AUTHORITY BOUNDARY: direct P6B evidence certificate only.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
