"""Direct certificate for the L7B Legal Operations field-service command API.

TITLE: Wilsy OS Legal Operations Command API Certificate
VERSION: v1.1.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-COMMAND-API-CERT
AUTHORITY: Transport/transaction composition only; P1/P4/P5 remain canonical.
EPITOME: Proves authenticated directory/field-service command input
         boundaries, one-orchestrator dispatch, transaction ownership, path
         binding, tenant derivation, and fail-closed exclusion of browser-
         manufactured tenant, legal, or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operations_command_router.py
COLLABORATION / OWNERSHIP: L7B certificate; domain and orchestrator contracts
                            are read-only authorities under test.
CERTIFICATION DATE: 2026-09-23
CHANGELOG: v1.1.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-COMMAND-API-CERT adds
           District/SheriffOffice/Deputy route, body-authority, exact tenant,
           L8-1 dispatch, and transaction evidence while retaining the L7B
           field-service command regression contract.
           v1.0.0 established deterministic command-boundary and transaction
           ownership evidence for allocation, attempt, outcome, and return.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: X-Tenant-ID is supplied only by the authorization dependency;
                 command bodies cannot establish tenant scope.
AUTHORITY BOUNDARY: Exactly one canonical orchestrator is invoked per command;
                    transport never constructs lifecycle truth.
FINANCIAL AUTHORITY BOUNDARY: No invoice, payment, settlement, or financial
                              execution authority; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Extra authority fields, path divergence, invalid state,
                         and failed transactions reject without partial success.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import ValidationError

import tools.eos.api.legal_operations_command_router as command_api
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import TenantAuthorizationDecision, TenantAuthorizationReason
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    Deputy,
    District,
    LegalInstruction,
    ProcessDocument,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
    SheriffOffice,
)


TENANT = "tenant-l7b"
BASE = datetime(2026, 9, 15, 8, 0, tzinfo=timezone.utc)
HEX = "a" * 128


class Session:
    def __init__(self) -> None:
        self.in_transaction = False
        self.events: list[str] = []

    def start_transaction(self) -> None:
        self.events.append("start")
        self.in_transaction = True

    def commit_transaction(self) -> None:
        self.events.append("commit")
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.events.append("abort")
        self.in_transaction = False

    def end_session(self) -> None:
        self.events.append("end")

    def __enter__(self) -> "Session":
        return self

    def __exit__(self, *_args: object) -> None:
        self.end_session()


class Client:
    def __init__(self) -> None:
        self.session = Session()

    def start_session(self) -> Session:
        return self.session


class Database:
    def get_collection(self, name: str) -> Any:
        return SimpleNamespace(name=name)


def context() -> TenantAuthorizationContext:
    identity = SovereignIdentity(
        identity_id="principal-l7b",
        tenant_id=TENANT,
        username="operator",
        email="operator@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    decision = TenantAuthorizationDecision(True, TenantAuthorizationReason.AUTHORIZED, "tenant_sheriff", "SHERIFF")
    return TenantAuthorizationContext(identity, TENANT, decision)


def attempt(state: ServiceAttemptState = ServiceAttemptState.ALLOCATED) -> ServiceAttempt:
    value = ServiceAttempt(
        tenant_id=TENANT,
        attempt_id="attempt-l7b",
        instruction_id="instruction-l7b",
        document_id="document-l7b",
        deputy_id="deputy-l7b",
        allocated_at=BASE,
        allocation_evidence_reference="allocation-evidence",
    )
    if state is ServiceAttemptState.ALLOCATED:
        return value
    attempted = value.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference="field-evidence",
        evidence_fingerprint=HEX,
        occurred_at=BASE + timedelta(minutes=1),
    )
    if state is ServiceAttemptState.ATTEMPTED:
        return attempted
    return attempted.transition_to(
        state,
        evidence_reference="terminal-evidence",
        evidence_fingerprint=HEX,
        occurred_at=BASE + timedelta(minutes=2),
    )


def test_routes_are_explicit_and_command_models_forbid_authority_fields() -> None:
    paths = {route.path for route in command_api.router.routes}  # type: ignore[reportAttributeAccessIssue]
    assert paths == {
        "/legal-operations/directory/districts",
        "/legal-operations/directory/sheriff-offices",
        "/legal-operations/directory/deputies",
        "/legal-operations/allocations",
        "/legal-operations/attempts",
        "/legal-operations/attempts/{attempt_id}/transition",
        "/legal-operations/attempts/{attempt_id}/outcome",
        "/legal-operations/executions/{execution_id}/return",
    }
    with pytest.raises(ValidationError):
        command_api.AttemptCommand(**{"attempt_authority_id": "authority", "state": "COMPLETED"})
    with pytest.raises(ValidationError):
        command_api.ReturnCommand(**{"execution_evidence_identity": HEX, "return_id": "return", "generated_at": BASE, "tenant_id": TENANT})
    with pytest.raises(ValidationError):
        command_api.DistrictProvisioningCommand.model_validate(
            {
                "district_id": "district-1",
                "name": "District",
                "jurisdiction_code": "ZA-GP",
                "evidence_reference": "source",
                "tenant_id": TENANT,
            }
        )


def test_directory_commands_use_authorized_tenant_one_l8_1_orchestrator_and_commit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Directory bodies never supply tenant authority and each command commits once."""
    client, database = Client(), Database()
    monkeypatch.setattr(command_api, "_db_handles", lambda: (client, database))
    seen: list[tuple[str, str, object]] = []

    def fake_district(**kwargs: Any) -> Any:
        seen.append(("district", kwargs["tenant_id"], kwargs["session"]))
        return SimpleNamespace(
            to_dict=lambda: {
                "disposition": "CREATED",
                "value": {"district_id": kwargs["district_id"]},
            }
        )

    def fake_office(**kwargs: Any) -> Any:
        seen.append(("office", kwargs["tenant_id"], kwargs["session"]))
        return SimpleNamespace(
            to_dict=lambda: {
                "disposition": "CREATED",
                "value": {"sheriff_office_id": kwargs["sheriff_office_id"]},
            }
        )

    def fake_deputy(**kwargs: Any) -> Any:
        seen.append(("deputy", kwargs["tenant_id"], kwargs["session"]))
        return SimpleNamespace(
            to_dict=lambda: {
                "disposition": "CREATED",
                "value": {"deputy_id": kwargs["deputy_id"]},
            }
        )

    monkeypatch.setattr(command_api, "provision_district", fake_district)
    monkeypatch.setattr(command_api, "provision_sheriff_office", fake_office)
    monkeypatch.setattr(command_api, "provision_deputy", fake_deputy)

    district = command_api.DistrictProvisioningCommand(
        district_id="district-l8-1",
        name="Central District",
        jurisdiction_code="ZA-GP-1",
        evidence_reference="district-source",
    )
    district_result = asyncio.run(
        command_api.provision_district_command(district, context())
    )
    assert district_result["value"]["district_id"] == "district-l8-1"
    assert client.session.events == ["start", "commit", "end"]

    client.session.events.clear()
    office = command_api.SheriffOfficeProvisioningCommand(
        sheriff_office_id="office-l8-1",
        district_id="district-l8-1",
        name="Central Office",
        evidence_reference="office-source",
    )
    office_result = asyncio.run(
        command_api.provision_sheriff_office_command(office, context())
    )
    assert office_result["value"]["sheriff_office_id"] == "office-l8-1"
    assert client.session.events == ["start", "commit", "end"]

    client.session.events.clear()
    deputy = command_api.DeputyProvisioningCommand(
        deputy_id="deputy-l8-1",
        sheriff_office_id="office-l8-1",
        display_name="Deputy One",
        badge_reference="badge-1",
        evidence_reference="deputy-source",
    )
    deputy_result = asyncio.run(
        command_api.provision_deputy_command(deputy, context())
    )
    assert deputy_result["value"]["deputy_id"] == "deputy-l8-1"
    assert client.session.events == ["start", "commit", "end"]

    assert seen == [
        ("district", TENANT, client.session),
        ("office", TENANT, client.session),
        ("deputy", TENANT, client.session),
    ]


def test_attempt_create_uses_one_orchestrator_and_commits(monkeypatch: pytest.MonkeyPatch) -> None:
    client, database = Client(), Database()
    seen: list[tuple[str, object]] = []
    monkeypatch.setattr(command_api, "_db_handles", lambda: (client, database))

    def fake_orchestrator(**kwargs: Any) -> ServiceAttempt:
        seen.append(("orchestrator", kwargs["session"]))
        assert kwargs["session"] is client.session
        assert kwargs["session"].in_transaction is True
        return attempt()

    monkeypatch.setattr(command_api, "orchestrate_process_service_attempt", fake_orchestrator)
    result = asyncio.run(command_api.create_process_service_attempt(command_api.AttemptCommand(attempt_authority_id="authority-l7b"), context()))
    assert result["data"]["state"] == "ALLOCATED"
    assert seen == [("orchestrator", client.session)]
    assert client.session.events == ["start", "commit", "end"]


def test_orchestrator_failure_aborts_without_success(monkeypatch: pytest.MonkeyPatch) -> None:
    client, database = Client(), Database()
    monkeypatch.setattr(command_api, "_db_handles", lambda: (client, database))

    def fail(**_kwargs: Any) -> Any:
        raise RuntimeError("domain failure")

    monkeypatch.setattr(command_api, "orchestrate_process_service_attempt", fail)
    with pytest.raises(command_api.HTTPException) as error:
        asyncio.run(command_api.create_process_service_attempt(command_api.AttemptCommand(attempt_authority_id="authority-l7b"), context()))
    assert error.value.status_code == 503
    assert client.session.events == ["start", "abort", "end"]


def test_transition_path_mismatch_aborts_before_orchestrator(monkeypatch: pytest.MonkeyPatch) -> None:
    client, database = Client(), Database()
    monkeypatch.setattr(command_api, "_db_handles", lambda: (client, database))
    monkeypatch.setattr(command_api, "_source", lambda *_args, **_kwargs: attempt())
    called = False

    def fake(**_kwargs: Any) -> Any:
        nonlocal called
        called = True
        return attempt(ServiceAttemptState.ATTEMPTED)

    monkeypatch.setattr(command_api, "transition_process_service_attempt", fake)
    command = command_api.AttemptTransitionCommand(current_evidence_identity=HEX, evidence_reference="field", evidence_fingerprint=HEX, occurred_at=BASE + timedelta(minutes=1))
    with pytest.raises(command_api.HTTPException) as error:
        asyncio.run(command_api.transition_process_service_attempt_command("different-attempt", command, context()))
    assert error.value.status_code == 404
    assert called is False
    assert client.session.events == ["start", "abort", "end"]


def test_transition_dispatches_p5d_only_after_source_path_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    client, database = Client(), Database()
    monkeypatch.setattr(command_api, "_db_handles", lambda: (client, database))
    monkeypatch.setattr(command_api, "_source", lambda *_args, **_kwargs: attempt())
    seen: list[object] = []

    def fake(**kwargs: Any) -> Any:
        seen.append(kwargs["session"])
        return attempt(ServiceAttemptState.ATTEMPTED)

    monkeypatch.setattr(command_api, "transition_process_service_attempt", fake)
    command = command_api.AttemptTransitionCommand(current_evidence_identity=HEX, evidence_reference="field", evidence_fingerprint=HEX, occurred_at=BASE + timedelta(minutes=1))
    result = asyncio.run(command_api.transition_process_service_attempt_command("attempt-l7b", command, context()))
    assert result["data"]["state"] == "ATTEMPTED"
    assert seen == [client.session]
    assert client.session.events == ["start", "commit", "end"]


def test_outcome_rejects_nonterminal_state_at_http_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False
    monkeypatch.setattr(command_api, "_transaction", lambda _callback: (_ for _ in ()).throw(AssertionError("must not transact")))
    command = command_api.OutcomeCommand(
        current_evidence_identity=HEX,
        outcome=ServiceAttemptState.ATTEMPTED,
        evidence_reference="field",
        evidence_fingerprint=HEX,
        occurred_at=BASE + timedelta(minutes=1),
        service_execution_id="execution-l7b",
        executed_at=BASE + timedelta(minutes=2),
    )
    with pytest.raises(command_api.HTTPException) as error:
        asyncio.run(command_api.record_process_service_outcome_command("attempt-l7b", command, context()))
    assert error.value.status_code == 422
    assert called is False


def test_outcome_dispatches_p5e_and_return_dispatches_p5f(monkeypatch: pytest.MonkeyPatch) -> None:
    client, database = Client(), Database()
    monkeypatch.setattr(command_api, "_db_handles", lambda: (client, database))
    monkeypatch.setattr(command_api, "_source", lambda *_args, **_kwargs: attempt(ServiceAttemptState.ATTEMPTED))
    monkeypatch.setattr(command_api, "transition_process_service_attempt_outcome", lambda **_kwargs: SimpleNamespace(to_dict=lambda: {"state": "COMPLETED"}))
    outcome = command_api.OutcomeCommand(current_evidence_identity=HEX, outcome=ServiceAttemptState.COMPLETED, evidence_reference="terminal", evidence_fingerprint=HEX, occurred_at=BASE + timedelta(minutes=2), service_execution_id="execution-l7b", executed_at=BASE + timedelta(minutes=3))
    assert asyncio.run(command_api.record_process_service_outcome_command("attempt-l7b", outcome, context()))["data"]["state"] == "COMPLETED"
    assert client.session.events == ["start", "commit", "end"]

    client.session.events.clear()
    execution = ServiceExecution.from_attempt(attempt=attempt(ServiceAttemptState.COMPLETED), service_execution_id="execution-l7b", executed_at=BASE + timedelta(minutes=3))
    monkeypatch.setattr(command_api, "_source", lambda *_args, **_kwargs: execution)
    monkeypatch.setattr(command_api, "generate_process_service_return", lambda **_kwargs: SimpleNamespace(to_dict=lambda: {"state": "GENERATED"}))
    return_command = command_api.ReturnCommand(execution_evidence_identity=HEX, return_id="return-l7b", generated_at=BASE + timedelta(minutes=4))
    assert asyncio.run(command_api.generate_return_of_service_command("execution-l7b", return_command, context()))["data"]["state"] == "GENERATED"
    assert client.session.events == ["start", "commit", "end"]


def test_return_path_mismatch_aborts_before_factory(monkeypatch: pytest.MonkeyPatch) -> None:
    client, database = Client(), Database()
    monkeypatch.setattr(command_api, "_db_handles", lambda: (client, database))
    terminal = attempt(ServiceAttemptState.COMPLETED)
    execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id="execution-l7b", executed_at=BASE + timedelta(minutes=2))
    monkeypatch.setattr(command_api, "_source", lambda *_args, **_kwargs: execution)
    called = False

    def fake(**_kwargs: Any) -> Any:
        nonlocal called
        called = True
        return object()

    monkeypatch.setattr(command_api, "generate_process_service_return", fake)
    command = command_api.ReturnCommand(execution_evidence_identity=HEX, return_id="return-l7b", generated_at=BASE + timedelta(minutes=3))
    with pytest.raises(command_api.HTTPException) as error:
        asyncio.run(command_api.generate_return_of_service_command("different-execution", command, context()))
    assert error.value.status_code == 404
    assert called is False
    assert client.session.events == ["start", "abort", "end"]


def test_allocation_dispatches_only_p4a_and_never_accepts_caller_state(monkeypatch: pytest.MonkeyPatch) -> None:
    client, database = Client(), Database()
    monkeypatch.setattr(command_api, "_db_handles", lambda: (client, database))
    instruction = LegalInstruction(TENANT, "instruction-l7b", "matter-l7b", "document-l7b", BASE, "instruction-evidence")
    document = ProcessDocument(TENANT, "document-l7b", "matter-l7b", "summons", BASE, "document-evidence")
    district = District(TENANT, "district-l7b", "District", "ZA-L7B", "district-evidence")
    office = SheriffOffice(TENANT, "office-l7b", "district-l7b", "Office", "office-evidence")
    deputy = Deputy(TENANT, "deputy-l7b", "office-l7b", "Deputy", "badge-l7b", "deputy-evidence")
    sources = {LegalInstruction: instruction, ProcessDocument: document, District: district, SheriffOffice: office, Deputy: deputy}
    monkeypatch.setattr(command_api, "_source", lambda _collection, _tenant, _identity, expected, _session: sources[expected])
    monkeypatch.setattr(command_api, "_prior_custody", lambda *_args, **_kwargs: ())
    monkeypatch.setattr(command_api, "authorize_process_service_assignment", lambda **_kwargs: object())
    monkeypatch.setattr(command_api.ProcessServiceAllocationRegistry, "get_current", lambda *_args, **_kwargs: object())
    seen: list[object] = []

    def fake(**kwargs: Any) -> Any:
        seen.append(kwargs["session"])
        return SimpleNamespace(allocated_document=document)

    monkeypatch.setattr(command_api, "orchestrate_process_service_allocation", fake)
    command = command_api.AllocationCommand(
        instruction_evidence_identity=HEX,
        document_evidence_identity=HEX,
        district_evidence_identity=HEX,
        sheriff_office_evidence_identity=HEX,
        deputy_evidence_identity=HEX,
        assignment_decision_id="assignment-l7b",
        assignment_evidence_reference="assignment-evidence",
        decided_at=BASE,
        allocation_command_id="allocation-l7b",
        idempotency_key="idem-l7b",
        allocation_custody_event_id="custody-l7b",
        allocation_evidence_reference="allocation-evidence",
        allocated_at=BASE,
    )
    result = asyncio.run(command_api.allocate_process_service(command, context()))
    assert result["data"] == document.to_dict()
    assert seen == [client.session]
    assert client.session.events == ["start", "commit", "end"]


def test_command_module_has_no_financial_or_client_ownership_surface() -> None:
    names = set(vars(command_api))
    assert not any(token in names for token in {"Invoice", "Payment", "Settlement", "MongoClient", "mongo_client", "_client"})


# ARTIFACT: test_legal_operations_command_router.py
# VERSION: v1.1.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-COMMAND-API-CERT
# AUTHORITY BOUNDARY: direct directory/field-service command composition certificate only
# TENANT POSTURE: explicit authorized context; bodies cannot establish scope
# FAIL-CLOSED POSTURE: invalid, divergent, and failed transactions reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT