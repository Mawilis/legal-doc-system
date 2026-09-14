"""Direct P5C certificate for the process-service attempt orchestrator.

TITLE: Wilsy OS Process-Service Attempt Orchestrator Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Adversarially certifies the P5B-to-P1 initial-attempt handoff while
         retaining caller transaction ownership and all upstream authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_process_service_attempt_orchestrator.py
COLLABORATION / OWNERSHIP: P5C composition certificate only; P1 owns lifecycle,
                            P5B owns durable attempt-authority evidence, and
                            P2 owns durable lifecycle evidence.
CERTIFICATION DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR-CERT
           certifies exact field mapping, tenant/session boundaries, replay,
           fail-closed dependency propagation, and absence of execution or
           financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every operation uses explicit non-pseudo tenant scope; a
                 receipt from another tenant is rejected before P2 persistence.
AUTHORITY BOUNDARY: This certificate covers composition only. It proves P5B is
                    the sole durable authority source and P5C creates only the
                    initial P1 ALLOCATED snapshot.
TRANSACTION BOUNDARY: A caller-owned active transaction session is forwarded
                      unchanged; P5C never starts, commits, aborts, retries, or
                      ends sessions.
FINANCIAL AUTHORITY BOUNDARY: No billing, invoice, payment, execution, or
                              settlement authority; Kennel EOS exclusively owns
                              financial execution and settlement.
FAIL-CLOSED DECLARATION: Invalid scope, locators, receipts, lifecycle input,
                         persistence, replay, and dependency failures reject.
"""
from __future__ import annotations

from datetime import datetime, timezone
import inspect

import pytest

import tools.eos.legal_operations.orchestration.process_service_attempt_orchestrator as p5c
import tools.eos.legal_operations.registry.process_service_attempt_authority_registry as p5b
from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttemptState
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistryError,
)


VERSION = "v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR-CERT"
TENANT = "tenant-p5c"
AUTHORITY_ID = "authority-p5c"
BASE = datetime(2026, 9, 14, 9, 0, tzinfo=timezone.utc)


class SessionDouble:
    """Caller-owned transaction sentinel that records forbidden ownership calls."""

    def __init__(self) -> None:
        self.in_transaction = True
        self.start_calls = 0
        self.commit_calls = 0
        self.abort_calls = 0
        self.end_calls = 0

    def start_transaction(self, *args: object, **kwargs: object) -> None:
        self.start_calls += 1

    def commit_transaction(self, *args: object, **kwargs: object) -> None:
        self.commit_calls += 1

    def abort_transaction(self, *args: object, **kwargs: object) -> None:
        self.abort_calls += 1

    def end_session(self, *args: object, **kwargs: object) -> None:
        self.end_calls += 1


def _receipt(*, tenant: str = TENANT, authority_id: str = AUTHORITY_ID, **changes: object) -> p5b.ProcessServiceAttemptAuthorityReceipt:
    """Build a valid P5B receipt through its private proof contract for tests."""
    values: dict[str, object] = {
        "tenant_id": tenant,
        "attempt_authority_id": authority_id,
        "attempt_id": "attempt-p5c",
        "instruction_id": "instruction-p5c",
        "document_id": "document-p5c",
        "deputy_id": "deputy-p5c",
        "allocation_command_id": "allocation-command-p5c",
        "allocation_evidence_reference": "allocation-evidence-p5c",
        "allocation_receipt_evidence_identity": "a" * 128,
        "allocation_receipt_fingerprint": "b" * 128,
        "allocation_current_fingerprint": "c" * 128,
        "allocated_at": BASE,
        "authorized_at": BASE,
        "authority_decision_fingerprint": "d" * 128,
    }
    values.update(changes)
    value = object.__new__(p5b.ProcessServiceAttemptAuthorityReceipt)
    for name, item in values.items():
        object.__setattr__(value, name, item)
    object.__setattr__(value, "_construction_proof", None)
    proof = p5b._issue_receipt_proof(p5b._digest(value.to_dict()))
    object.__setattr__(value, "_construction_proof", proof)
    value.__post_init__()
    return value


def _run(
    monkeypatch: pytest.MonkeyPatch,
    receipt: object,
    *,
    tenant: str = TENANT,
    authority_id: str = AUTHORITY_ID,
    session: SessionDouble | None = None,
    p2_result: object | None = None,
) -> tuple[object, list[tuple[str, object, object, object]] | list[tuple[str, object]] , SessionDouble]:
    """Invoke P5C with spies for exact dependency/session/order assertions."""
    tx = session or SessionDouble()
    calls: list[tuple[str, object, object, object]] | list[tuple[str, object]] = []

    def authority_lookup(
        requested_tenant: str,
        locator: str,
        collection: object,
        *,
        session: object,
    ) -> object:
        calls.append(("p5b", requested_tenant, locator, session))  # type: ignore[arg-type]
        return receipt

    def lifecycle_create(value: object, collection: object, *, session: object, **kwargs: object) -> object:
        calls.append(("p2", value, session))  # type: ignore[arg-type]
        if isinstance(p2_result, BaseException):
            raise p2_result
        return value if p2_result is None else p2_result

    monkeypatch.setattr(
        p5c.ProcessServiceAttemptAuthorityRegistry,
        "get_by_attempt_authority_id",
        staticmethod(authority_lookup),
    )
    monkeypatch.setattr(
        p5c.LegalOperationsLifecycleRegistry,
        "create",
        staticmethod(lifecycle_create),
    )
    result = p5c.orchestrate_process_service_attempt(
        tenant_id=tenant,
        attempt_authority_id=authority_id,
        attempt_authority_collection=object(),
        lifecycle_collection=object(),
        session=tx,
    )
    return result, calls, tx


def test_initial_mapping_and_exact_caller_session(monkeypatch: pytest.MonkeyPatch) -> None:
    receipt = _receipt()
    result, calls, session = _run(monkeypatch, receipt)
    assert type(result) is p5c.ServiceAttempt
    assert result.state is ServiceAttemptState.ALLOCATED
    assert result.tenant_id == receipt.tenant_id
    assert result.attempt_id == receipt.attempt_id
    assert result.instruction_id == receipt.instruction_id
    assert result.document_id == receipt.document_id
    assert result.deputy_id == receipt.deputy_id
    assert result.allocated_at == receipt.allocated_at
    assert result.allocation_evidence_reference == receipt.allocation_evidence_reference
    assert result.transition_history == ()
    assert calls[0][0] == "p5b" and calls[1][0] == "p2"
    assert calls[0][3] is session  # type: ignore[index]
    assert calls[1][2] is session  # type: ignore[index]
    assert calls[0][3] is calls[1][2]  # type: ignore[index]


def test_no_transaction_ownership_or_external_client(monkeypatch: pytest.MonkeyPatch) -> None:
    result, _, session = _run(monkeypatch, _receipt())
    assert result.state is ServiceAttemptState.ALLOCATED  # type: ignore[union-attr]
    assert session.start_calls == session.commit_calls == session.abort_calls == session.end_calls == 0
    assert not any(name in vars(p5c) for name in ("MongoClient", "client", "mongo_client"))
    assert not any(hasattr(p5c.orchestrate_process_service_attempt, name) for name in ("start_transaction", "commit", "abort"))


def test_p5b_is_sole_durable_source_and_no_p4_or_p5a_reread(monkeypatch: pytest.MonkeyPatch) -> None:
    result, calls, _ = _run(monkeypatch, _receipt())
    assert result.state is ServiceAttemptState.ALLOCATED  # type: ignore[union-attr]
    assert "ProcessServiceAllocationReceipt" not in vars(p5c)
    assert "ProcessServiceAllocationCurrent" not in vars(p5c)
    assert "authorize_process_service_attempt" not in vars(p5c)
    assert [call[0] for call in calls] == ["p5b", "p2"]
    assert not hasattr(p5c, "ServiceExecution")
    assert not hasattr(p5c, "ReturnOfService")
    assert set(inspect.signature(p5c.orchestrate_process_service_attempt).parameters) == {
        "tenant_id",
        "attempt_authority_id",
        "attempt_authority_collection",
        "lifecycle_collection",
        "session",
    }


def test_tenant_mismatch_rejected_before_p2(monkeypatch: pytest.MonkeyPatch) -> None:
    def lookup(*args: object, **kwargs: object) -> object:
        return _receipt(tenant="tenant-other")

    def forbidden_p2(*args: object, **kwargs: object) -> object:
        raise AssertionError("P2 must not persist a tenant-mismatched receipt")

    monkeypatch.setattr(p5c.ProcessServiceAttemptAuthorityRegistry, "get_by_attempt_authority_id", staticmethod(lookup))
    monkeypatch.setattr(p5c.LegalOperationsLifecycleRegistry, "create", staticmethod(forbidden_p2))
    with pytest.raises(p5c.ProcessServiceAttemptOrchestratorInputError) as exc:
        p5c.orchestrate_process_service_attempt(
            tenant_id=TENANT,
            attempt_authority_id=AUTHORITY_ID,
            attempt_authority_collection=object(),
            lifecycle_collection=object(),
            session=SessionDouble(),
        )
    assert exc.value.code == "P5C_P5B_SCOPE_MISMATCH"


def test_authority_locator_mismatch_rejected_before_p2(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(p5c.ProcessServiceAttemptOrchestratorInputError) as exc:
        _run(monkeypatch, _receipt(), authority_id="different-authority")
    assert exc.value.code == "P5C_P5B_SCOPE_MISMATCH"


def test_missing_durable_authority_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    error = p5b.ProcessServiceAttemptAuthorityRegistryReceiptNotFoundError()

    def missing(*args: object, **kwargs: object) -> object:
        raise error

    monkeypatch.setattr(p5c.ProcessServiceAttemptAuthorityRegistry, "get_by_attempt_authority_id", staticmethod(missing))
    with pytest.raises(type(error)):
        p5c.orchestrate_process_service_attempt(
            tenant_id=TENANT,
            attempt_authority_id=AUTHORITY_ID,
            attempt_authority_collection=object(),
            lifecycle_collection=object(),
            session=SessionDouble(),
        )


def test_corrupt_p5b_hydration_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    error = p5b.ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError()

    def corrupt(*args: object, **kwargs: object) -> object:
        raise error

    monkeypatch.setattr(p5c.ProcessServiceAttemptAuthorityRegistry, "get_by_attempt_authority_id", staticmethod(corrupt))
    with pytest.raises(type(error)):
        p5c.orchestrate_process_service_attempt(
            tenant_id=TENANT,
            attempt_authority_id=AUTHORITY_ID,
            attempt_authority_collection=object(),
            lifecycle_collection=object(),
            session=SessionDouble(),
        )


def test_invalid_p1_construction_is_not_repaired(monkeypatch: pytest.MonkeyPatch) -> None:
    invalid = _receipt()
    object.__setattr__(invalid, "allocation_evidence_reference", "")
    monkeypatch.setattr(p5b.ProcessServiceAttemptAuthorityReceipt, "__post_init__", lambda self: None)
    with pytest.raises(p5c.ProcessServiceAttemptOrchestratorInputError) as exc:
        _run(monkeypatch, invalid)
    assert exc.value.code == "P5C_P1_ATTEMPT_INVALID"


def test_p2_failure_propagates_without_transaction_ownership(monkeypatch: pytest.MonkeyPatch) -> None:
    error = LegalOperationsLifecycleRegistryError("M2_PERSISTENCE_UNAVAILABLE")
    session = SessionDouble()
    with pytest.raises(type(error)) as exc:
        _run(monkeypatch, _receipt(), session=session, p2_result=error)
    assert str(exc.value) == "M2_PERSISTENCE_UNAVAILABLE"
    assert session.start_calls == session.commit_calls == session.abort_calls == session.end_calls == 0


def test_p2_exact_replay_is_preserved_and_no_parallel_idempotency(monkeypatch: pytest.MonkeyPatch) -> None:
    first, calls, _ = _run(monkeypatch, _receipt())
    second, _, _ = _run(monkeypatch, _receipt(), p2_result=first)
    assert second is first
    assert len(calls) == 2
    assert not hasattr(p5c, "idempotency_key")


def test_p2_divergence_is_not_relabelled_as_replay(monkeypatch: pytest.MonkeyPatch) -> None:
    error = LegalOperationsLifecycleRegistryError("M2_REPLAY_CONFLICT")
    with pytest.raises(type(error)) as exc:
        _run(monkeypatch, _receipt(), p2_result=error)
    assert str(exc.value) == "M2_REPLAY_CONFLICT"


def test_transaction_required_is_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(p5c.ProcessServiceAttemptOrchestratorTransactionRequiredError):
        p5c.orchestrate_process_service_attempt(
            tenant_id=TENANT,
            attempt_authority_id=AUTHORITY_ID,
            attempt_authority_collection=object(),
            lifecycle_collection=object(),
            session=None,
        )


def test_no_internal_retry_and_no_service_or_financial_authority(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0

    def unavailable(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        raise p5b.ProcessServiceAttemptAuthorityRegistryPersistenceUnavailableError()

    monkeypatch.setattr(p5c.ProcessServiceAttemptAuthorityRegistry, "get_by_attempt_authority_id", staticmethod(unavailable))
    with pytest.raises(p5b.ProcessServiceAttemptAuthorityRegistryPersistenceUnavailableError):
        p5c.orchestrate_process_service_attempt(
            tenant_id=TENANT,
            attempt_authority_id=AUTHORITY_ID,
            attempt_authority_collection=object(),
            lifecycle_collection=object(),
            session=SessionDouble(),
        )
    assert calls == 1
    assert not hasattr(p5c, "ServiceExecution")
    assert not hasattr(p5c, "ReturnOfService")
    assert not any(token in vars(p5c) for token in ("billing", "invoice", "payment", "settlement", "Kennel"))


# ARTIFACT: test_process_service_attempt_orchestrator.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR-CERT
# AUTHORITY BOUNDARY: direct P5C composition certificate only.
# TENANT POSTURE: explicit tenant scope; cross-tenant receipts fail closed.
# FAIL-CLOSED POSTURE: dependency, lifecycle, persistence, replay, and input failures reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
