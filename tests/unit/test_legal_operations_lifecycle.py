"""Direct adversarial certificate for the Legal Operations lifecycle contract.

TITLE: Wilsy OS Legal Operations Lifecycle Direct Certificate
VERSION: v1.0.0-LEGAL-OPERATIONS-LIFECYCLE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove immutable tenant-scoped lifecycle history, custody evidence,
         executable service/return factory gates, and financial separation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operations_lifecycle.py
COLLABORATION / OWNERSHIP: Direct certificate for
                            legal_operations_lifecycle.py; no production
                            semantics are defined here.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: 2026-09-13 v1.0.0-LEGAL-OPERATIONS-LIFECYCLE-CERT certifies
           canonical construction, complete transition histories, custody
           chronology, service/return factory boundaries, deterministic
           SHA3-512 evidence, and non-financial authority separation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers only; no network, database,
                             provider, secret, or customer data access.
TENANT BOUNDARY: Every certificate fixture uses explicit non-global tenants.
AUTHORITY BOUNDARY: Tests certify the production lifecycle contract only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive financial
                              execution and settlement authority.
FAIL-CLOSED DECLARATION: Any unexpected lifecycle, history, fingerprint,
                         custody, or factory behavior fails the certificate.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest
import tools.eos.legal_operations.domain.legal_operations_lifecycle as lifecycle

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
    DocumentCustodyEvent,
    DocumentCustodyEventType,
    LegalInstruction,
    LegalInstructionState,
    LegalOperationsLifecycleError,
    LifecycleTransitionEvidence,
    ProcessDocument,
    ProcessDocumentState,
    ReturnOfService,
    ReturnOfServiceState,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
    ServiceExecutionOutcome,
    validate_custody_event_chain,
)


NOW = datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)
TERMINAL_FINGERPRINT = "a" * 128


def instruction(**overrides: object) -> LegalInstruction:
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "instruction_id": "instruction-1",
        "case_matter_id": "matter-1",
        "document_id": "document-1",
        "registered_at": NOW,
        "evidence_reference": "instruction-registration",
    }
    values.update(overrides)
    return cast(Any, LegalInstruction)(**values)


def matter(**overrides: object) -> CaseMatter:
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "case_matter_id": "matter-1",
        "matter_reference": "matter-reference",
        "opened_at": NOW,
        "evidence_reference": "matter-opening",
    }
    values.update(overrides)
    return cast(Any, CaseMatter)(**values)


def document(**overrides: object) -> ProcessDocument:
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "document_id": "document-1",
        "case_matter_id": "matter-1",
        "document_type": "summons",
        "registered_at": NOW,
        "registration_evidence_reference": "document-registration",
    }
    values.update(overrides)
    return cast(Any, ProcessDocument)(**values)


def attempt(**overrides: object) -> ServiceAttempt:
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "attempt_id": "attempt-1",
        "instruction_id": "instruction-1",
        "document_id": "document-1",
        "deputy_id": "deputy-1",
        "allocated_at": NOW,
        "allocation_evidence_reference": "allocation-evidence",
    }
    values.update(overrides)
    return cast(Any, ServiceAttempt)(**values)


def event(
    prior: object,
    resulting: object,
    occurred_at: datetime,
    reference: str,
    fingerprint: str | None = None,
) -> LifecycleTransitionEvidence:
    return LifecycleTransitionEvidence(
        prior_state=prior,  # type: ignore[arg-type]
        resulting_state=resulting,  # type: ignore[arg-type]
        occurred_at=occurred_at,
        evidence_reference=reference,
        evidence_fingerprint=fingerprint,
    )


def test_canonical_initial_construction_and_identity_boundaries() -> None:
    values = (instruction(), matter(), document(), attempt())
    assert [value.state.value for value in values] == ["REGISTERED", "OPEN", "REGISTERED", "ALLOCATED"]
    for value in values:
        assert value.tenant_id == "tenant-a"
        assert is_dataclass(value)

    for factory, field_name in (
        (instruction, "registered_at"),
        (matter, "opened_at"),
        (document, "registered_at"),
        (attempt, "allocated_at"),
    ):
        with pytest.raises(LegalOperationsLifecycleError):
            factory(**{field_name: datetime(2026, 9, 13, 12, 0)})


@pytest.mark.parametrize("tenant_id", ["default", "global", "global_root", "root", "master", "*"])
def test_pseudo_global_tenants_reject(tenant_id: str) -> None:
    with pytest.raises(LegalOperationsLifecycleError):
        instruction(tenant_id=tenant_id)
    with pytest.raises(LegalOperationsLifecycleError):
        matter(tenant_id=tenant_id)
    with pytest.raises(LegalOperationsLifecycleError):
        document(tenant_id=tenant_id)
    with pytest.raises(LegalOperationsLifecycleError):
        attempt(tenant_id=tenant_id)


def test_immutable_and_deterministic_evidence() -> None:
    value = instruction()
    with pytest.raises(FrozenInstanceError):
        value.tenant_id = "tenant-b"  # type: ignore[misc]
    assert value.to_dict() == instruction().to_dict()
    assert value.fingerprint == instruction().fingerprint
    changed = instruction(evidence_reference="different-registration")
    assert changed.fingerprint != value.fingerprint
    assert isinstance(value.fingerprint, str) and len(value.fingerprint) == 128
    assert value.fingerprint == value.fingerprint.lower()


def test_legal_instruction_complete_chain_and_cancellation_paths() -> None:
    accepted = instruction().transition_to(LegalInstructionState.ACCEPTED, evidence_reference="accepted", occurred_at=NOW)
    closed = accepted.transition_to(
        LegalInstructionState.CLOSED,
        evidence_reference="closed",
        occurred_at=NOW + timedelta(minutes=1),
    )
    assert [record.resulting_state for record in closed.transition_history] == [
        LegalInstructionState.ACCEPTED,
        LegalInstructionState.CLOSED,
    ]
    assert instruction().transition_to(
        LegalInstructionState.CANCELLED, evidence_reference="cancelled", occurred_at=NOW
    ).state is LegalInstructionState.CANCELLED
    assert accepted.transition_to(
        LegalInstructionState.CANCELLED, evidence_reference="cancelled-after-accept", occurred_at=NOW + timedelta(minutes=1)
    ).state is LegalInstructionState.CANCELLED


@pytest.mark.parametrize(
    "history",
    [
        (event(LegalInstructionState.REGISTERED, LegalInstructionState.CLOSED, NOW, "skip"),),
        (
            event(LegalInstructionState.REGISTERED, LegalInstructionState.ACCEPTED, NOW, "accept"),
            event(LegalInstructionState.REGISTERED, LegalInstructionState.CLOSED, NOW + timedelta(minutes=1), "gap"),
        ),
        (
            event(LegalInstructionState.REGISTERED, LegalInstructionState.ACCEPTED, NOW, "accept"),
            event(LegalInstructionState.ACCEPTED, LegalInstructionState.CLOSED, NOW - timedelta(minutes=1), "reverse-time"),
        ),
    ],
)
def test_legal_instruction_history_rejects_skips_reversals_and_chronology(
    history: tuple[LifecycleTransitionEvidence, ...],
) -> None:
    with pytest.raises(LegalOperationsLifecycleError):
        instruction(state=LegalInstructionState.CLOSED, transition_history=history)
    with pytest.raises(LegalOperationsLifecycleError):
        instruction(state=LegalInstructionState.ACCEPTED, transition_history=history)


def test_case_matter_open_closed_and_invalid_history() -> None:
    closed = matter().transition_to(CaseMatterState.CLOSED, evidence_reference="matter-close", occurred_at=NOW)
    assert closed.state is CaseMatterState.CLOSED
    assert len(closed.transition_history) == 1
    invalid = (event(CaseMatterState.CLOSED, CaseMatterState.OPEN, NOW, "reopen"),)
    with pytest.raises(LegalOperationsLifecycleError):
        matter(state=CaseMatterState.OPEN, transition_history=invalid)


def test_process_document_complete_chain() -> None:
    value = document()
    value = value.transition_to(ProcessDocumentState.RECEIVED, evidence_reference="received", occurred_at=NOW)
    value = value.transition_to(
        ProcessDocumentState.ALLOCATED_TO_DEPUTY,
        evidence_reference="allocated",
        occurred_at=NOW + timedelta(minutes=1),
    )
    value = value.transition_to(
        ProcessDocumentState.RETURNED_TO_CLIENT,
        evidence_reference="returned",
        occurred_at=NOW + timedelta(minutes=2),
    )
    assert [record.resulting_state for record in value.transition_history] == [
        ProcessDocumentState.RECEIVED,
        ProcessDocumentState.ALLOCATED_TO_DEPUTY,
        ProcessDocumentState.RETURNED_TO_CLIENT,
    ]


@pytest.mark.parametrize(
    "state,history",
    [
        (
            ProcessDocumentState.RETURNED_TO_CLIENT,
            (event(ProcessDocumentState.REGISTERED, ProcessDocumentState.RETURNED_TO_CLIENT, NOW, "skip"),),
        ),
        (
            ProcessDocumentState.RETURNED_TO_CLIENT,
            (
                event(ProcessDocumentState.REGISTERED, ProcessDocumentState.RECEIVED, NOW, "received"),
                event(ProcessDocumentState.RECEIVED, ProcessDocumentState.REGISTERED, NOW + timedelta(minutes=1), "reverse"),
            ),
        ),
        (
            ProcessDocumentState.ALLOCATED_TO_DEPUTY,
            (
                event(ProcessDocumentState.REGISTERED, ProcessDocumentState.RECEIVED, NOW, "received"),
                event(ProcessDocumentState.RECEIVED, ProcessDocumentState.ALLOCATED_TO_DEPUTY, NOW - timedelta(minutes=1), "time"),
            ),
        ),
    ],
)
def test_process_document_history_rejects_skip_reversal_and_chronology(
    state: ProcessDocumentState,
    history: tuple[LifecycleTransitionEvidence, ...],
) -> None:
    with pytest.raises(LegalOperationsLifecycleError):
        document(state=state, transition_history=history)
    with pytest.raises(LegalOperationsLifecycleError):
        document(state=ProcessDocumentState.RECEIVED, transition_history=history)


def test_service_attempt_completed_and_not_completed_chains() -> None:
    completed = attempt().transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="attempted", occurred_at=NOW)
    completed = completed.transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference="completed-source",
        evidence_fingerprint=TERMINAL_FINGERPRINT,
        occurred_at=NOW + timedelta(minutes=1),
    )
    assert completed.state is ServiceAttemptState.COMPLETED
    assert completed.transition_history[-1].evidence_fingerprint == TERMINAL_FINGERPRINT

    not_completed = attempt(attempt_id="attempt-2").transition_to(
        ServiceAttemptState.ATTEMPTED, evidence_reference="attempted-2", occurred_at=NOW
    )
    not_completed = not_completed.transition_to(
        ServiceAttemptState.NOT_COMPLETED,
        evidence_reference="not-completed-source",
        evidence_fingerprint=TERMINAL_FINGERPRINT,
        occurred_at=NOW + timedelta(minutes=1),
    )
    assert not_completed.state is ServiceAttemptState.NOT_COMPLETED


def test_service_attempt_terminal_fingerprint_and_fabricated_history_reject() -> None:
    with pytest.raises(LegalOperationsLifecycleError):
        attempt().transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="attempted", occurred_at=NOW).transition_to(
            ServiceAttemptState.COMPLETED, evidence_reference="completed", occurred_at=NOW + timedelta(minutes=1)
        )
    fabricated = (event(ServiceAttemptState.ALLOCATED, ServiceAttemptState.COMPLETED, NOW, "fabricated", TERMINAL_FINGERPRINT),)
    with pytest.raises(LegalOperationsLifecycleError):
        attempt(state=ServiceAttemptState.COMPLETED, transition_history=fabricated)


def test_service_execution_is_factory_derived_and_chronology_bound() -> None:
    terminal = attempt().transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="attempted", occurred_at=NOW).transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference="service-source",
        evidence_fingerprint=TERMINAL_FINGERPRINT,
        occurred_at=NOW + timedelta(minutes=1),
    )
    with pytest.raises(LegalOperationsLifecycleError):
        ServiceExecution(
            tenant_id="tenant-b",
            service_execution_id="forged",
            attempt_id="other-attempt",
            instruction_id="other-instruction",
            document_id="other-document",
            outcome=ServiceExecutionOutcome.COMPLETED,
            executed_at=NOW,
            evidence_reference="forged-source",
            evidence_fingerprint=TERMINAL_FINGERPRINT,
        )
    with pytest.raises(LegalOperationsLifecycleError):
        ServiceExecution.from_attempt(attempt=attempt(), service_execution_id="execution-1", executed_at=NOW)
    execution = ServiceExecution.from_attempt(
        attempt=terminal,
        service_execution_id="execution-1",
        executed_at=NOW + timedelta(minutes=2),
    )
    assert execution.tenant_id == terminal.tenant_id
    assert execution.instruction_id == terminal.instruction_id
    assert execution.document_id == terminal.document_id
    assert execution.attempt_id == terminal.attempt_id
    assert execution.outcome is ServiceExecutionOutcome.COMPLETED
    assert execution.evidence_reference == terminal.transition_history[-1].evidence_reference
    assert execution.evidence_fingerprint == TERMINAL_FINGERPRINT
    with pytest.raises(LegalOperationsLifecycleError):
        ServiceExecution.from_attempt(attempt=terminal, service_execution_id="execution-2", executed_at=NOW)


def test_service_execution_rejects_fabricated_skipped_attempt_history() -> None:
    with pytest.raises(LegalOperationsLifecycleError):
        skipped = attempt(
            state=ServiceAttemptState.COMPLETED,
            transition_history=(
                event(ServiceAttemptState.ALLOCATED, ServiceAttemptState.COMPLETED, NOW, "skipped", TERMINAL_FINGERPRINT),
            ),
        )
        ServiceExecution.from_attempt(attempt=skipped, service_execution_id="execution-1", executed_at=NOW)


def test_return_of_service_is_factory_derived_and_separate_from_service() -> None:
    terminal = attempt().transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="attempted", occurred_at=NOW).transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference="service-source",
        evidence_fingerprint=TERMINAL_FINGERPRINT,
        occurred_at=NOW + timedelta(minutes=1),
    )
    execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id="execution-1", executed_at=NOW + timedelta(minutes=1))
    with pytest.raises(LegalOperationsLifecycleError):
        ReturnOfService(
            tenant_id="tenant-b",
            return_id="forged-return",
            instruction_id="other-instruction",
            document_id="other-document",
            attempt_id="other-attempt",
            service_execution_id="other-execution",
            service_outcome=ServiceExecutionOutcome.COMPLETED,
            service_evidence_reference="forged",
            service_evidence_fingerprint=TERMINAL_FINGERPRINT,
            generated_at=NOW,
        )
    returned = ReturnOfService.from_service_execution(
        instruction_id="instruction-1",
        service_execution=execution,
        return_id="return-1",
        generated_at=NOW + timedelta(minutes=2),
    )
    assert returned.state is ReturnOfServiceState.GENERATED
    assert returned.tenant_id == execution.tenant_id
    assert returned.document_id == execution.document_id
    assert returned.attempt_id == execution.attempt_id
    assert returned.service_execution_id == execution.service_execution_id
    assert returned.service_outcome is execution.outcome
    assert returned.service_evidence_reference == execution.evidence_reference
    assert returned.service_evidence_fingerprint == execution.evidence_fingerprint
    with pytest.raises(LegalOperationsLifecycleError):
        ReturnOfService.from_service_execution(
            instruction_id="wrong-instruction",
            service_execution=execution,
            return_id="return-2",
            generated_at=NOW + timedelta(minutes=2),
        )
    with pytest.raises(LegalOperationsLifecycleError):
        ReturnOfService.from_service_execution(
            instruction_id="instruction-1",
            service_execution=execution,
            return_id="return-3",
            generated_at=NOW,
        )


def test_custody_chain_registration_continuity_containment_and_chronology() -> None:
    registered = DocumentCustodyEvent("tenant-a", "custody-1", "document-1", DocumentCustodyEventType.REGISTERED, NOW, 1, "registered")
    received = DocumentCustodyEvent("tenant-a", "custody-2", "document-1", DocumentCustodyEventType.RECEIVED_IN_OFFICE, NOW, 2, "received", to_holder_reference="office-1")
    allocated = DocumentCustodyEvent("tenant-a", "custody-3", "document-1", DocumentCustodyEventType.ALLOCATED_TO_DEPUTY, NOW + timedelta(minutes=1), 3, "allocated", to_holder_reference="deputy-1")
    assert validate_custody_event_chain((registered, received, allocated)) == (registered, received, allocated)
    with pytest.raises(LegalOperationsLifecycleError):
        validate_custody_event_chain((received, allocated))
    with pytest.raises(LegalOperationsLifecycleError):
        validate_custody_event_chain((registered, allocated))
    duplicate = DocumentCustodyEvent("tenant-a", "custody-2", "document-1", DocumentCustodyEventType.RECEIVED_IN_OFFICE, NOW, 2, "duplicate", to_holder_reference="office-1")
    with pytest.raises(LegalOperationsLifecycleError):
        validate_custody_event_chain((registered, received, duplicate))
    wrong_scope = DocumentCustodyEvent("tenant-b", "custody-4", "document-1", DocumentCustodyEventType.RETURNED_TO_CLIENT, NOW + timedelta(minutes=2), 3, "wrong-tenant", to_holder_reference="client-1")
    with pytest.raises(LegalOperationsLifecycleError):
        validate_custody_event_chain((registered, received, wrong_scope))
    wrong_document = DocumentCustodyEvent("tenant-a", "custody-5", "document-2", DocumentCustodyEventType.RETURNED_TO_CLIENT, NOW + timedelta(minutes=2), 3, "wrong-document", to_holder_reference="client-1")
    with pytest.raises(LegalOperationsLifecycleError):
        validate_custody_event_chain((registered, received, wrong_document))
    out_of_order = DocumentCustodyEvent("tenant-a", "custody-6", "document-1", DocumentCustodyEventType.RETURNED_TO_CLIENT, NOW - timedelta(minutes=1), 3, "out-of-order", to_holder_reference="client-1")
    with pytest.raises(LegalOperationsLifecycleError):
        validate_custody_event_chain((registered, received, out_of_order))


def test_authority_separations_and_no_financial_surface() -> None:
    assert ServiceAttemptState.ATTEMPTED is not ServiceAttemptState.COMPLETED
    assert ServiceExecutionOutcome.COMPLETED is not ReturnOfServiceState.GENERATED
    for value in (instruction(), matter(), document(), attempt()):
        names = {field.name.casefold() for field in fields(value)}
        assert names.isdisjoint({"invoice", "invoice_id", "payment", "payment_id", "settlement", "settlement_id"})
    assert "Kennel EOS exclusively" in (lifecycle.__doc__ or "")


# ARTIFACT: test_legal_operations_lifecycle.py
# VERSION: v1.0.0-LEGAL-OPERATIONS-LIFECYCLE-CERT
# AUTHORITY BOUNDARY: direct certificate only; no production authority.
# TENANT POSTURE: synthetic explicit tenants; no cross-tenant disclosure.
# FAIL-CLOSED POSTURE: adversarial assertions reject malformed or skipped facts.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
