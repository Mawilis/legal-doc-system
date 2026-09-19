"""Direct certificate for the legal-corpus approval transaction operator.

TITLE: WILSY OS Legal Corpus Approval Operator Direct Certificate
VERSION: v1.0.1-R1D-B0F-R9B-P4-P3-R1-SESSION-SEQUENCING-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies caller-owned sessions, bounded whole-transaction retries,
         and fail-closed fresh readback without a Mongo server.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_approval_operator.py
COLLABORATION / OWNERSHIP: The closed approval service and registries remain
                            read-only dependencies. This certificate tests the
                            operator with deterministic lifecycle sentinels.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.0.1-R1 repairs session-local commit sequencing so fresh
           unknown-commit readback cannot consume transaction error scripts;
           all ordinary, retry, and unknown-commit classifications remain
           covered.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Existing memory-only verified-proof fixture is
                            used; no secret, network, or database is opened.
TENANT BOUNDARY: PLATFORM corpus approval only; no tenant/principal authority.
AUTHORITY BOUNDARY: Tests execution semantics only and never confer authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Every ambiguous and non-labelled failure is asserted to
                     reject without unbounded retry or inferred durability.
"""
from __future__ import annotations

import ast
import inspect
from dataclasses import FrozenInstanceError
from typing import Any, Callable, cast

import pytest

from tests.unit.test_legal_corpus_approval_service import _proof
from tools.eos.legal_operations.registry.legal_corpus_approval_registry import (
    LegalCorpusApprovalAdmissionResult,
    LegalCorpusApprovalAdmissionState,
    LegalCorpusApprovalPreflight,
    LegalCorpusApprovalPreflightState,
    LegalCorpusApprovalDurableRecord,
)
from tools.eos.legal_operations.service.legal_corpus_approval_service import (
    LegalCorpusApprovalResult,
    LegalCorpusApprovalResultState,
)
from tools.eos.legal_operations.service.legal_corpus_approval_operator import (
    LegalCorpusApprovalOperator,
    LegalCorpusApprovalOperatorError,
    LegalCorpusApprovalOperatorResultState,
    MAX_TOTAL_TRANSACTION_ATTEMPTS,
)
import tools.eos.legal_operations.service.legal_corpus_approval_operator as operator_module


class LabelError(RuntimeError):
    """Deterministic PyMongo-like labelled failure."""

    def __init__(self, *labels: str) -> None:
        self.labels = set(labels)
        super().__init__("labelled failure")

    def has_error_label(self, label: str) -> bool:
        return label in self.labels


class Session:
    """Caller-owned session sentinel with explicit lifecycle evidence."""

    def __init__(self, role: str, commit_error: BaseException | None = None) -> None:
        self.role = role
        self.in_transaction = False
        self.start_calls = 0
        self.commit_calls = 0
        self.abort_calls = 0
        self.commit_error = commit_error

    def __enter__(self) -> "Session":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        del exc_type, exc_value, traceback

    def start_transaction(self) -> None:
        self.start_calls += 1
        self.in_transaction = True

    def commit_transaction(self) -> None:
        assert self.role == "transaction"
        self.commit_calls += 1
        if self.commit_error is not None:
            raise self.commit_error
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.abort_calls += 1
        self.in_transaction = False


class Client:
    """Fresh session factory proving transaction and readback separation."""

    def __init__(self, session_specs: list[tuple[str, BaseException | None]] | None = None) -> None:
        self.session_specs = list(session_specs or [("transaction", None)])
        self.sessions: list[Session] = []

    def start_session(self) -> Session:
        role, error = self.session_specs.pop(0) if self.session_specs else ("transaction", None)
        session = Session(role, error if role == "transaction" else None)
        self.sessions.append(session)
        return session


class Database:
    """Collection map sentinel; no database calls leave the process."""

    def __getitem__(self, name: str) -> object:
        return name


def _admission(proof: Any, state: LegalCorpusApprovalAdmissionState) -> LegalCorpusApprovalAdmissionResult:
    record = LegalCorpusApprovalDurableRecord(proof.authorization, proof.approval_evidence.evidence_fingerprint)
    return LegalCorpusApprovalAdmissionResult(state, record)


def _service_result(proof: Any, state: LegalCorpusApprovalResultState) -> LegalCorpusApprovalResult:
    admission_state = (
        LegalCorpusApprovalAdmissionState.CREATED
        if state is LegalCorpusApprovalResultState.CREATED
        else LegalCorpusApprovalAdmissionState.EXACT_REPLAY
    )
    return LegalCorpusApprovalResult(state, proof.approval_evidence.approved_document, _admission(proof, admission_state))


class Service:
    """Actual-call seam recording the exact session forwarded by the operator."""

    def __init__(self, proof: Any, outcomes: list[Any]) -> None:
        self.proof = proof
        self.outcomes = list(outcomes)
        self.calls: list[Any] = []

    def admit(self, proof: Any, *, session: Any = None) -> LegalCorpusApprovalResult:
        assert proof is self.proof
        self.calls.append(session)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class DocumentRegistry:
    """Readback registry seam with queued target observations."""

    def __init__(self, targets: list[Any]) -> None:
        self.targets = list(targets)
        self.sessions: list[Any] = []

    def get(self, document_id: str, version: str, collection: Any = None, *, session: Any = None) -> Any:
        del document_id, version, collection
        self.sessions.append(session)
        target = self.targets.pop(0) if len(self.targets) > 1 else self.targets[0]
        if isinstance(target, BaseException):
            raise target
        return target


class ApprovalRegistry:
    """Readback registry seam with queued pair states."""

    def __init__(self, proof: Any, states: list[LegalCorpusApprovalPreflightState]) -> None:
        self.proof = proof
        self.states = list(states)
        self.sessions: list[Any] = []

    def preflight_verified_approval(self, proof: Any, collection: Any = None, *, session: Any = None) -> LegalCorpusApprovalPreflight:
        del collection
        assert proof is self.proof
        self.sessions.append(session)
        state = self.states.pop(0) if len(self.states) > 1 else self.states[0]
        if isinstance(state, BaseException):
            raise state
        if state is LegalCorpusApprovalPreflightState.EXACT:
            record = _admission(proof, LegalCorpusApprovalAdmissionState.EXACT_REPLAY).record
            return LegalCorpusApprovalPreflight(state, record, ("row",), (("all", "row"),), None)
        return LegalCorpusApprovalPreflight(state, None, (), (), None)


def _operator(
    proof: Any,
    outcomes: list[Any],
    *,
    session_specs: list[tuple[str, BaseException | None]] | None = None,
    targets: list[Any] | None = None,
    states: list[LegalCorpusApprovalPreflightState] | None = None,
) -> tuple[LegalCorpusApprovalOperator, Client, Service, DocumentRegistry, ApprovalRegistry]:
    client = Client(session_specs)
    service = Service(proof, outcomes)
    documents = DocumentRegistry(targets or [proof.approval_evidence.approved_document])
    approvals = ApprovalRegistry(proof, states or [LegalCorpusApprovalPreflightState.EXACT])
    instance = LegalCorpusApprovalOperator(
        client=client,
        database=Database(),
        service=cast(Any, service),
        document_registry=documents,  # type: ignore[arg-type]
        approval_registry=approvals,  # type: ignore[arg-type]
    )
    return instance, client, service, documents, approvals


def _error(call: Callable[[], Any], code: str, *, cause_required: bool = True) -> None:
    with pytest.raises(LegalCorpusApprovalOperatorError) as captured:
        call()
    assert captured.value.code == code
    if cause_required:
        assert captured.value.__cause__ is not None


def test_verified_proof_is_required_before_runtime() -> None:
    instance = LegalCorpusApprovalOperator(client=object(), database=object())
    _error(lambda: instance.execute(cast(Any, object())), "VERIFIED_PROOF_REQUIRED", cause_required=False)


@pytest.mark.parametrize(
    ("service_state", "operator_state"),
    [
        (LegalCorpusApprovalResultState.CREATED, LegalCorpusApprovalOperatorResultState.COMMITTED_CREATED),
        (LegalCorpusApprovalResultState.EXACT_REPLAY, LegalCorpusApprovalOperatorResultState.COMMITTED_EXACT_REPLAY),
    ],
)
def test_known_commit_outcomes_are_truthful_and_same_session(service_state: Any, operator_state: Any) -> None:
    proof = _proof()
    instance, client, service, _, _ = _operator(proof, [_service_result(proof, service_state)])
    result = instance.execute(proof)
    assert result.state is operator_state
    assert result.attempts == 1
    assert client.sessions[0].start_calls == 1 and client.sessions[0].commit_calls == 1
    assert client.sessions[0].abort_calls == 0 and service.calls == client.sessions


def test_service_failure_aborts_without_commit_or_retry() -> None:
    proof = _proof()
    instance, client, service, _, _ = _operator(proof, [RuntimeError("bounded")])
    _error(lambda: instance.execute(proof), "APPROVAL_SERVICE_FAILED")
    assert len(client.sessions) == 1 and client.sessions[0].abort_calls == 1
    assert client.sessions[0].commit_calls == 0 and len(service.calls) == 1


def test_non_transient_failure_has_no_retry() -> None:
    proof = _proof()
    instance, client, _, _, _ = _operator(proof, [LabelError("OtherLabel")])
    _error(lambda: instance.execute(proof), "APPROVAL_SERVICE_FAILED")
    assert len(client.sessions) == 1


def test_transient_failures_retry_whole_transaction_and_stop_at_three() -> None:
    proof = _proof()
    transient = LabelError("TransientTransactionError")
    instance, client, service, _, _ = _operator(
        proof,
        [transient, transient, _service_result(proof, LegalCorpusApprovalResultState.CREATED)],
        session_specs=[("transaction", transient), ("transaction", transient), ("transaction", None)],
    )
    result = instance.execute(proof)
    assert result.attempts == MAX_TOTAL_TRANSACTION_ATTEMPTS
    assert len(service.calls) == MAX_TOTAL_TRANSACTION_ATTEMPTS
    assert len(client.sessions) == MAX_TOTAL_TRANSACTION_ATTEMPTS
    assert all(item.abort_calls == 1 for item in client.sessions[:2])
    assert service.calls == client.sessions

    exhausted, exhausted_client, _, _, _ = _operator(
        proof,
        [transient, transient, transient],
        session_specs=[("transaction", transient), ("transaction", transient), ("transaction", transient)],
    )
    _error(lambda: exhausted.execute(proof), "TRANSIENT_RETRY_EXHAUSTED")
    assert len(exhausted_client.sessions) == MAX_TOTAL_TRANSACTION_ATTEMPTS


def test_unknown_commit_both_exact_uses_fresh_readback_and_reconciles() -> None:
    proof = _proof()
    unknown = LabelError("UnknownTransactionCommitResult")
    instance, client, service, documents, approvals = _operator(
        proof,
        [_service_result(proof, LegalCorpusApprovalResultState.CREATED)],
        session_specs=[("transaction", unknown), ("readback", None)],
        targets=[proof.approval_evidence.approved_document],
        states=[LegalCorpusApprovalPreflightState.EXACT],
    )
    result = instance.execute(proof)
    assert result.state is LegalCorpusApprovalOperatorResultState.RECONCILED_AFTER_UNKNOWN_COMMIT
    assert len(client.sessions) == 2
    assert client.sessions[0] is not client.sessions[1]
    assert documents.sessions == [client.sessions[1]] and approvals.sessions == [client.sessions[1]]
    assert service.calls == [client.sessions[0]]


@pytest.mark.parametrize(
    ("target", "state", "error_code"),
    [
        (None, LegalCorpusApprovalPreflightState.ABSENT, "UNKNOWN_COMMIT_RETRY_EXHAUSTED"),
        (None, LegalCorpusApprovalPreflightState.EXACT, "UNKNOWN_COMMIT_SPLIT_OR_PARTIAL"),
        ("divergent", LegalCorpusApprovalPreflightState.EXACT, "UNKNOWN_COMMIT_DIVERGENT"),
        ("exact", LegalCorpusApprovalPreflightState.SPLIT_IDENTITY, "UNKNOWN_COMMIT_SPLIT_OR_PARTIAL"),
    ],
)
def test_unknown_commit_states_fail_closed_or_share_retry_budget(target: Any, state: Any, error_code: str) -> None:
    proof = _proof()
    unknown = LabelError("UnknownTransactionCommitResult")
    target_value = proof.approval_evidence.approved_document if target == "exact" else target
    instance, client, _, _, _ = _operator(
        proof,
        [_service_result(proof, LegalCorpusApprovalResultState.CREATED)] * 3,
        session_specs=[
            ("transaction", unknown), ("readback", None),
            ("transaction", unknown), ("readback", None),
            ("transaction", unknown), ("readback", None),
        ],
        targets=[target_value],
        states=[state],
    )
    _error(lambda: instance.execute(proof), error_code)
    if error_code == "UNKNOWN_COMMIT_RETRY_EXHAUSTED":
        assert len(client.sessions) == MAX_TOTAL_TRANSACTION_ATTEMPTS * 2
        transaction_sessions = [item for item in client.sessions if item.role == "transaction"]
        readback_sessions = [item for item in client.sessions if item.role == "readback"]
        assert len(transaction_sessions) == 3 and len(readback_sessions) == 3
        assert all(item.commit_calls == 0 and item.commit_error is None for item in readback_sessions)
        assert [item.commit_error for item in transaction_sessions] == [unknown, unknown, unknown]
        assert all(item.role == "transaction" for item in client.sessions[::2])
        assert all(item.role == "readback" for item in client.sessions[1::2])
    else:
        assert len(client.sessions) == 2


def test_unknown_commit_readback_failure_is_fail_closed() -> None:
    proof = _proof()
    instance, client, _, _, _ = _operator(
        proof,
        [_service_result(proof, LegalCorpusApprovalResultState.CREATED)],
        session_specs=[("transaction", LabelError("UnknownTransactionCommitResult")), ("readback", None)],
        targets=[RuntimeError("readback")],
        states=[LegalCorpusApprovalPreflightState.EXACT],
    )
    _error(lambda: instance.execute(proof), "UNKNOWN_COMMIT_READBACK_FAILED")
    assert len(client.sessions) == 2


def test_operator_has_no_verification_signing_or_transaction_service_lifecycle() -> None:
    source = inspect.getsource(operator_module)
    tree = ast.parse(source)
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) for alias in node.names}
    assert not {"start_transaction", "commit_transaction", "abort_transaction"} - attributes
    assert "verify_legal_corpus_approval_authorization" not in imported
    assert "Ed25519PrivateKey" not in source and "sign(" not in source
    assert "with_transaction" not in source
    assert "while attempt <= MAX_TOTAL_TRANSACTION_ATTEMPTS" in source


def test_result_is_frozen_and_slotted() -> None:
    proof = _proof()
    instance, _, _, _, _ = _operator(proof, [_service_result(proof, LegalCorpusApprovalResultState.CREATED)])
    result = instance.execute(proof)
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        result.state = LegalCorpusApprovalOperatorResultState.COMMITTED_EXACT_REPLAY  # type: ignore[misc]
    assert hasattr(result, "__slots__") and not hasattr(result, "__dict__")


# ARTIFACT: test_legal_corpus_approval_operator.py
# VERSION: v1.0.1-R1D-B0F-R9B-P4-P3-R1-SESSION-SEQUENCING-CERT
# AUTHORITY BOUNDARY: direct evidence for caller-owned approval execution only
# TENANT POSTURE: PLATFORM corpus only; no tenant/principal authority
# FAIL-CLOSED POSTURE: retry, unknown commit, split, divergence, and readback failure are covered
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
