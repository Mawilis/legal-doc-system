"""R9B-P4-P3-R2 isolated real-Mongo certificate for approval operator.

TITLE: WILSY OS Legal Corpus Approval Operator Real-Mongo Certificate
VERSION: v1.0.1-R1D-B0F-R9B-P4-P3-R2-LEGAL-CORPUS-APPROVAL-OPERATOR-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies actual Mongo atomic promotion, exact replay, caller-owned
         transaction retry, and fresh durable unknown-commit reconciliation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_corpus_approval_operator_real_mongo.py
COLLABORATION / OWNERSHIP: The operator, approval service, document registry,
                            and approval registry remain production authorities;
                            this certificate owns only isolated run-scoped
                            Mongo fixtures and bounded commit-boundary faults.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.0.1-R2 removes the session proxy from the real Mongo I/O path,
           returns raw ClientSession objects, and observes session identity at
           production boundaries while preserving bounded fault injection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic proof material is memory-only; Mongo
                            credentials and URI values are never printed.
TENANT BOUNDARY: PLATFORM corpus only; no tenant or principal authority.
AUTHORITY BOUNDARY: Consumes an already-verified fixture proof; no signing,
                    review, approval, acceptance, or key ceremony occurs.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Partial, divergent, split, ambiguous, and exhausted
                     outcomes are asserted to reject without inferred success.
"""
from __future__ import annotations

import os
import secrets
from contextlib import contextmanager
from typing import Any, Iterator

import pytest
from pymongo import MongoClient
from pymongo.client_session import ClientSession
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tests.unit.test_legal_corpus_approval_service import _proof
from tools.eos.legal_operations import production_legal_corpus as corpus
from tools.eos.legal_operations.registry.legal_corpus_approval_registry import (
    COLLECTION as APPROVAL_COLLECTION,
    LegalCorpusApprovalRegistry,
)
from tools.eos.legal_operations.registry.legal_document_registry import (
    COLLECTION as DOCUMENT_COLLECTION,
    LegalDocumentRegistry,
)
from tools.eos.legal_operations.service.legal_corpus_approval_operator import (
    LegalCorpusApprovalOperator,
    LegalCorpusApprovalOperatorError,
    LegalCorpusApprovalOperatorResultState,
)
from tools.eos.legal_operations.service.legal_corpus_approval_service import LegalCorpusApprovalService


DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
REPLICA_SET = "wilsyVendorCertRS"
RUN_ENV = "WILSY_R9B_P4_P3_R2_RUN_ID"
RUN_ID = os.getenv(RUN_ENV, secrets.token_hex(8)).strip()
assert RUN_ID and all(character in "0123456789abcdef" for character in RUN_ID)
DATABASE_PREFIX = f"wilsy_r9b_p4_p3_r1_{RUN_ID}_"
DATABASE_SEQUENCE = 0
SOURCE = corpus.INSTITUTIONAL_CHARTER_DRAFT


class LabelError(RuntimeError):
    """Deterministic driver-label boundary used only at commit injection."""

    def __init__(self, label: str) -> None:
        self.label = label
        super().__init__("bounded injected outcome")

    def has_error_label(self, candidate: str) -> bool:
        return candidate == self.label


class ClientSpy:
    """Delegate to MongoClient and return each raw ClientSession unchanged."""

    def __init__(self, client: MongoClient[Any]) -> None:
        self.client = client
        self.sessions: list[ClientSession] = []

    def start_session(self, *args: Any, **kwargs: Any) -> ClientSession:
        session = self.client.start_session(*args, **kwargs)
        self.sessions.append(session)
        return session


def _install_observation_and_commit_injection(
    monkeypatch: pytest.MonkeyPatch,
    client: MongoClient[Any],
    database: Any,
    proof: Any,
    actions: list[str],
) -> tuple[ClientSpy, dict[str, list[Any]]]:
    """Trace production boundaries while keeping raw PyMongo sessions intact."""
    observed: dict[str, list[Any]] = {
        "service": [], "document_get": [], "document_register": [],
        "approval_preflight": [], "approval_admission": [],
    }
    original_commit = ClientSession.commit_transaction
    action_queue = actions

    def traced_commit(session: ClientSession, *args: Any, **kwargs: Any) -> Any:
        action = action_queue.pop(0) if action_queue else "normal"
        if action in {"unknown_abort", "transient_abort"}:
            session.abort_transaction()
            label = "UnknownTransactionCommitResult" if action == "unknown_abort" else "TransientTransactionError"
            raise LabelError(label)
        result = original_commit(session, *args, **kwargs)
        if action == "unknown_exact":
            raise LabelError("UnknownTransactionCommitResult")
        if action == "unknown_partial":
            database[APPROVAL_COLLECTION].delete_many({})
            raise LabelError("UnknownTransactionCommitResult")
        if action == "unknown_divergent":
            database[DOCUMENT_COLLECTION].update_one(
                {"document_id": proof.approval_evidence.approved_document_id,
                 "version": proof.approval_evidence.approved_version},
                {"$set": {"title": "DIVERGENT_COMMIT_OBSERVATION"}},
            )
            raise LabelError("UnknownTransactionCommitResult")
        return result

    monkeypatch.setattr(ClientSession, "commit_transaction", traced_commit)
    original_admit = LegalCorpusApprovalService.admit

    def traced_admit(service: LegalCorpusApprovalService, candidate: Any, *, session: Any = None) -> Any:
        observed["service"].append(session)
        return original_admit(service, candidate, session=session)

    monkeypatch.setattr(LegalCorpusApprovalService, "admit", traced_admit)

    def trace_static(owner: Any, name: str, key: str) -> None:
        original = getattr(owner, name)

        def traced(*args: Any, **kwargs: Any) -> Any:
            observed[key].append(kwargs.get("session"))
            return original(*args, **kwargs)

        monkeypatch.setattr(owner, name, staticmethod(traced))

    trace_static(LegalDocumentRegistry, "get", "document_get")
    trace_static(LegalDocumentRegistry, "register", "document_register")
    trace_static(LegalCorpusApprovalRegistry, "preflight_verified_approval", "approval_preflight")
    trace_static(LegalCorpusApprovalRegistry, "admit_verified_approval", "approval_admission")
    return ClientSpy(client), observed


def _database_name(label: str) -> str:
    """Allocate one run-scoped Mongo database name no longer than 63 bytes."""
    del label
    global DATABASE_SEQUENCE
    DATABASE_SEQUENCE += 1
    name = f"{DATABASE_PREFIX}{DATABASE_SEQUENCE}"
    assert len(name) <= 63 and name not in {"admin", "config", "local"}
    return name


@contextmanager
def _isolated_database(client: MongoClient[Any], label: str) -> Iterator[Any]:
    """Yield and finally drop only this certificate's isolated namespace."""
    name = _database_name(label)
    assert name not in client.list_database_names()
    database = client.get_database(
        name,
        read_concern=ReadConcern("majority"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    try:
        yield database
    finally:
        client.drop_database(name)
        assert name not in client.list_database_names()


@pytest.fixture(scope="module")
def mongo_client() -> Iterator[MongoClient[Any]]:
    """Prove the sanctioned writable local topology before the official run."""
    uri = os.getenv("TEST_VENDOR_MONGO_URI", DEFAULT_URI).strip()
    assert uri.startswith("mongodb://127.0.0.1:27027/")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=3000, replicaSet=REPLICA_SET, retryWrites=True)
    hello = client.admin.command("hello")
    assert client.server_info().get("version") == "7.0.37"
    assert hello.get("setName") == REPLICA_SET
    assert hello.get("isWritablePrimary", hello.get("ismaster", False)) is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    try:
        yield client
    finally:
        client.close()


def _prepare(database: Any) -> None:
    """Create deployment-owned indexes and the canonical source draft."""
    document_collection = database[DOCUMENT_COLLECTION]
    approval_collection = database[APPROVAL_COLLECTION]
    LegalDocumentRegistry.ensure_indexes(document_collection)
    LegalCorpusApprovalRegistry.ensure_indexes(approval_collection)
    document_collection.insert_one(SOURCE.to_document())


def _operator(client: Any, database: Any, proof: Any) -> LegalCorpusApprovalOperator:
    """Construct the actual operator and closed service over this database."""
    service = LegalCorpusApprovalService(
        document_collection=database[DOCUMENT_COLLECTION],
        approval_collection=database[APPROVAL_COLLECTION],
    )
    return LegalCorpusApprovalOperator(client=client, database=database, service=service)


def test_real_create_exact_replay_and_source_immutability(
    mongo_client: MongoClient[Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Commit a real pair, replay it exactly, and preserve the source draft."""
    with _isolated_database(mongo_client, "create") as database:
        _prepare(database)
        proof = _proof()
        client_spy, observed = _install_observation_and_commit_injection(monkeypatch, mongo_client, database, proof, [])
        before = database[DOCUMENT_COLLECTION].find_one({"document_id": SOURCE.document_id, "version": SOURCE.version})
        result = _operator(client_spy, database, proof).execute(proof)
        assert result.state is LegalCorpusApprovalOperatorResultState.COMMITTED_CREATED
        assert database[DOCUMENT_COLLECTION].count_documents({"version": proof.approval_evidence.approved_document.version}) == 1
        assert database[APPROVAL_COLLECTION].count_documents({}) == 1
        replay = _operator(client_spy, database, proof).execute(proof)
        assert replay.state is LegalCorpusApprovalOperatorResultState.COMMITTED_EXACT_REPLAY
        assert database[DOCUMENT_COLLECTION].count_documents({}) == 2
        assert database[APPROVAL_COLLECTION].count_documents({}) == 1
        after = database[DOCUMENT_COLLECTION].find_one({"document_id": SOURCE.document_id, "version": SOURCE.version})
        assert after == before
        transaction_session = client_spy.sessions[0]
        assert all(item is transaction_session for item in observed["service"][:1])
        assert all(item is transaction_session for item in observed["document_get"][:2])
        assert observed["document_register"][0] is transaction_session
        assert observed["approval_preflight"][0] is transaction_session
        assert observed["approval_admission"][0] is transaction_session
        assert all(isinstance(item, ClientSession) for item in client_spy.sessions)


def test_real_service_failure_aborts_without_durability(
    mongo_client: MongoClient[Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing source fails before writes and leaves both collections empty."""
    with _isolated_database(mongo_client, "failure") as database:
        LegalDocumentRegistry.ensure_indexes(database[DOCUMENT_COLLECTION])
        LegalCorpusApprovalRegistry.ensure_indexes(database[APPROVAL_COLLECTION])
        proof = _proof()
        client_spy, observed = _install_observation_and_commit_injection(monkeypatch, mongo_client, database, proof, [])
        with pytest.raises(LegalCorpusApprovalOperatorError) as captured:
            _operator(client_spy, database, proof).execute(proof)
        assert captured.value.code == "APPROVAL_SERVICE_FAILED"
        assert database[DOCUMENT_COLLECTION].count_documents({}) == 0
        assert database[APPROVAL_COLLECTION].count_documents({}) == 0
        assert len(client_spy.sessions) == 1 and observed["service"][0] is client_spy.sessions[0]


def test_real_transient_retry_is_whole_transaction_and_bounded(
    mongo_client: MongoClient[Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Two injected transient aborts are followed by one real committed attempt."""
    with _isolated_database(mongo_client, "transient") as database:
        _prepare(database)
        proof = _proof()
        client_spy, observed = _install_observation_and_commit_injection(
            monkeypatch, mongo_client, database, proof, ["transient_abort", "transient_abort", "normal"]
        )
        result = _operator(client_spy, database, proof).execute(proof)
        assert result.state is LegalCorpusApprovalOperatorResultState.COMMITTED_CREATED
        assert result.attempts == 3
        assert len(client_spy.sessions) == 3
        assert all(item is client_spy.sessions[index] for index, item in enumerate(observed["service"]))
        assert database[DOCUMENT_COLLECTION].count_documents({}) == 2
        assert database[APPROVAL_COLLECTION].count_documents({}) == 1


def test_real_unknown_commit_exact_uses_fresh_durable_readback(
    mongo_client: MongoClient[Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """An injected ambiguous replay commit reconciles an exact real pair."""
    with _isolated_database(mongo_client, "unknown-exact") as database:
        _prepare(database)
        proof = _proof()
        actions: list[str] = []
        client_spy, observed = _install_observation_and_commit_injection(monkeypatch, mongo_client, database, proof, actions)
        _operator(client_spy, database, proof).execute(proof)
        actions.append("unknown_exact")
        result = _operator(client_spy, database, proof).execute(proof)
        assert result.state is LegalCorpusApprovalOperatorResultState.RECONCILED_AFTER_UNKNOWN_COMMIT
        assert len(client_spy.sessions) == 3
        assert client_spy.sessions[1] is not client_spy.sessions[2]
        assert observed["document_get"][-1] is client_spy.sessions[2]
        assert observed["approval_preflight"][-1] is client_spy.sessions[2]


def test_real_unknown_both_absent_retries_three_transactions(
    mongo_client: MongoClient[Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Injected unknown aborts with real BOTH_ABSENT readback exhaust the budget."""
    with _isolated_database(mongo_client, "unknown-absent") as database:
        _prepare(database)
        proof = _proof()
        client_spy, observed = _install_observation_and_commit_injection(
            monkeypatch, mongo_client, database, proof, ["unknown_abort", "unknown_abort", "unknown_abort"]
        )
        with pytest.raises(LegalCorpusApprovalOperatorError) as captured:
            _operator(client_spy, database, proof).execute(proof)
        assert captured.value.code == "UNKNOWN_COMMIT_RETRY_EXHAUSTED"
        assert len(observed["service"]) == 3
        assert len(client_spy.sessions) == 6
        assert all(isinstance(item, ClientSession) for item in client_spy.sessions)
        assert database[DOCUMENT_COLLECTION].count_documents({}) == 1
        assert database[APPROVAL_COLLECTION].count_documents({}) == 0


@pytest.mark.parametrize("action,expected", [("unknown_partial", "UNKNOWN_COMMIT_SPLIT_OR_PARTIAL"), ("unknown_divergent", "UNKNOWN_COMMIT_DIVERGENT")])
def test_real_unknown_partial_and_divergent_states_fail_closed(
    mongo_client: MongoClient[Any], monkeypatch: pytest.MonkeyPatch, action: str, expected: str
) -> None:
    """Real durable partial/divergent states never become reconciled success."""
    with _isolated_database(mongo_client, action) as database:
        _prepare(database)
        proof = _proof()
        client_spy, _ = _install_observation_and_commit_injection(monkeypatch, mongo_client, database, proof, [action])
        with pytest.raises(LegalCorpusApprovalOperatorError) as captured:
            _operator(client_spy, database, proof).execute(proof)
        assert captured.value.code == expected


# ARTIFACT: test_legal_corpus_approval_operator_real_mongo.py
# VERSION: v1.0.1-R1D-B0F-R9B-P4-P3-R2-LEGAL-CORPUS-APPROVAL-OPERATOR-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real persistence evidence for caller-owned approval execution
# TENANT POSTURE: isolated PLATFORM corpus databases; no tenant/principal authority
# FAIL-CLOSED POSTURE: atomicity, retry exhaustion, partial state, divergence, and unknown commit are covered
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
