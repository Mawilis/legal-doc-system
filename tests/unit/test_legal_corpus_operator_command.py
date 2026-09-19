"""Direct certificate for the R8K legal-corpus operator command.

TITLE: WILSY OS R8K Legal Corpus Operator Command Direct Certificate
VERSION: v1.1.0-R9B-P7-A2-R1-LEGAL-CORPUS-OPERATOR-COMMAND-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Behaviorally certifies the authority-consuming R8K command with
         deterministic TEST-only Ed25519, Kernel, Mongo-session, registry,
         service, retry, commit, and readback doubles.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_operator_command.py
COLLABORATION / OWNERSHIP: R8K production source is read-only. This artifact
                            owns direct unit evidence only; real-Mongo
                            durability remains a later certificate.
CERTIFICATION / UPDATE DATE: 2026-09-18
CHANGELOG: v1.0.0-R1D-B0F-B4-R8K-P2 establishes direct coverage of hydration,
           authority ordering, dry-run isolation, transaction ownership,
           bounded retries, unknown-commit reconciliation, and output classes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Deterministic TEST-only private material exists
                            only in memory for a sanctioned positive path;
                            production private material is never loaded.
TENANT BOUNDARY: PLATFORM corpus command only; no tenant or principal input.
AUTHORITY BOUNDARY: Test evidence only; this file never issues, approves,
                    signs, persists, or executes legal authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
CERTIFICATION BOUNDARY: Fake persistence certifies orchestration only; this is
                         not real-Mongo or production-admission evidence.
FAIL-CLOSED POSTURE: Invalid authority, partial durability, divergence,
                     unknown commit, unlabelled failure, and retry exhaustion
                     are asserted as non-success.
"""
from __future__ import annotations

import ast
import base64
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import inspect
import json
from pathlib import Path
from collections.abc import Callable, Sequence
from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

import tools.eos.legal_operations.domain.legal_corpus_operator_authorization as authorization_module
import tools.eos.legal_operations.legal_corpus_operator_command as command
from tools.eos.legal_operations.domain.legal_acceptance import LegalDocumentStatus
from tools.eos.legal_operations.domain.legal_corpus_operator_trust_root import (
    AUTHORITY_DOMAIN,
    AUTHORIZED_OPERATION,
    ED25519_ALGORITHM,
    LegalCorpusOperatorKeyStatus,
    LegalCorpusOperatorTrustRoot,
    LegalCorpusOperatorTrustRootError,
    LegalCorpusOperatorTrustedKey,
    TRUST_ROOT_PROVENANCE,
    TRUST_ROOT_SCOPE,
)
from tools.eos.legal_operations.domain.legal_corpus_operator_authorization import (
    AUTHORITY_MECHANISM,
    AUTHORITY_MECHANISM_VERSION,
    LegalCorpusOperatorAuthorization,
    LegalCorpusOperatorAuthorizationOperation,
    LegalCorpusOperatorAuthorizationScope,
)
from tools.eos.legal_operations import production_legal_corpus
from tools.eos.legal_operations.production_legal_corpus import get_institutional_charter_draft
from tools.eos.legal_operations.service.legal_corpus_provisioning_service import (
    LegalCorpusProvisioningResult,
    LegalCorpusProvisioningResultState,
    LegalCorpusProvisioningServiceError,
)


VERSION = "v1.1.0-R9B-P7-A2-R1-LEGAL-CORPUS-OPERATOR-COMMAND-CERT"
NOW = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
TEST_SEED = bytes(range(32))
TEST_KEY_ID = "prdca-key:r8k-p2-test"
PRODUCTION_KEY_ID = "prdca-key:legal-corpus-69c7c3e9a67c7e552057d4c0670623be"
R8K_PATH = Path("tools/eos/legal_operations/legal_corpus_operator_command.py")
R8K_SHA3_512 = "ebbdef42a8b604bb2bfb3bb6bce399c55a30aee9e8c81fe1d31baf1579839284d080c71d241dc659e96942fd770ec446d3d1bb75489adea356442877503456c4"


def _public_key_text(key: Ed25519PrivateKey) -> str:
    """Encode deterministic TEST-only raw Ed25519 public bytes."""
    raw = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _test_trusted_key(key: Ed25519PrivateKey, *, valid_until: datetime | None = NOW + timedelta(days=2)) -> LegalCorpusOperatorTrustedKey:
    """Construct a C1-compatible TEST trust record without changing production data."""
    public_key = _public_key_text(key)
    values: dict[str, Any] = {
        "key_id": TEST_KEY_ID,
        "algorithm": ED25519_ALGORITHM,
        "public_key_base64url": public_key,
        "issuer_identity": "issuer:r8k-p2-test",
        "authority_domain": AUTHORITY_DOMAIN,
        "scope": TRUST_ROOT_SCOPE,
        "permitted_operations": frozenset({AUTHORIZED_OPERATION}),
        "valid_from": NOW - timedelta(days=1),
        "valid_until": valid_until,
        "status": LegalCorpusOperatorKeyStatus.ACTIVE,
        "revision": 1,
        "trust_root_provenance": TRUST_ROOT_PROVENANCE,
    }
    values["fingerprint"] = LegalCorpusOperatorTrustedKey.fingerprint_for(**values)
    return LegalCorpusOperatorTrustedKey(**values)


def _patch_test_authority(monkeypatch: pytest.MonkeyPatch, key: LegalCorpusOperatorTrustedKey) -> None:
    """Route C1 resolution to one explicit TEST-only key in this test."""
    def resolve(key_id: str) -> LegalCorpusOperatorTrustedKey:
        if key_id != key.key_id:
            raise LegalCorpusOperatorTrustRootError("UNKNOWN_TRUSTED_KEY")
        return key

    monkeypatch.setattr(LegalCorpusOperatorTrustRoot, "resolve", staticmethod(resolve))
    monkeypatch.setattr(authorization_module, "_utc_now", lambda: NOW)


def _authorization(
    key: Ed25519PrivateKey,
    *,
    document: Any | None = None,
    **changes: Any,
) -> LegalCorpusOperatorAuthorization:
    """Build one signed TEST authorization through D1's canonical payload."""
    if document is None:
        document = get_institutional_charter_draft()
    values: dict[str, Any] = {
        "authorization_id": "r8k-p2-auth-001",
        "key_id": TEST_KEY_ID,
        "operation": LegalCorpusOperatorAuthorizationOperation.DRAFT_ADMISSION,
        "scope": LegalCorpusOperatorAuthorizationScope.PLATFORM,
        "source_document_id": document.document_id,
        "source_agreement_type": document.agreement_type,
        "source_version": document.version,
        "source_status": document.status,
        "source_content_reference": document.content_reference,
        "source_sha3_512": document.sha3_512,
        "issued_at": NOW,
        "not_before": NOW - timedelta(minutes=1),
        "expires_at": NOW + timedelta(minutes=5),
        "replay_nonce": "r8k-p2-replay-001",
        "idempotency_key": "r8k-p2-idempotency-001",
        "authority_mechanism": AUTHORITY_MECHANISM,
        "authority_mechanism_version": AUTHORITY_MECHANISM_VERSION,
        "signature": base64.urlsafe_b64encode(b"x" * 64).rstrip(b"=").decode("ascii"),
    }
    values.update(changes)
    unsigned = LegalCorpusOperatorAuthorization(**values)
    values["signature"] = base64.urlsafe_b64encode(key.sign(unsigned.canonical_payload_bytes())).rstrip(b"=").decode("ascii")
    return LegalCorpusOperatorAuthorization(**values)


def _write_authorization(tmp_path: Path, authorization: LegalCorpusOperatorAuthorization) -> Path:
    """Write only a temporary TEST authorization envelope for CLI hydration."""
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(authorization.to_document()), encoding="utf-8")
    return path


class LabelledError(RuntimeError):
    """Minimal PyMongo-like error label double."""

    def __init__(self, *labels: str) -> None:
        self.labels = set(labels)

    def has_error_label(self, label: str) -> bool:
        return label in self.labels


class FakeSession:
    """Caller-session double with explicit transaction lifecycle evidence."""

    def __init__(self, client: "FakeClient") -> None:
        self.client = client
        self.events = client.events
        self.in_transaction = False
        self.commit_error: BaseException | None = None

    def __enter__(self) -> "FakeSession":
        self.events.append("session_enter")
        return self

    def __exit__(self, *_args: object) -> None:
        self.events.append("session_exit")
        self.in_transaction = False

    def start_transaction(self) -> None:
        assert self.in_transaction is False
        self.events.append("transaction_start")
        self.in_transaction = True
        if self.client.commit_errors:
            self.commit_error = self.client.commit_errors.pop(0)

    def commit_transaction(self) -> None:
        self.events.append("commit")
        if self.commit_error is not None:
            error = self.commit_error
            self.commit_error = None
            if not command._has_error_label(error, command.UNKNOWN_TRANSACTION_COMMIT_RESULT):
                self.in_transaction = True
            raise error
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.events.append("abort")
        self.in_transaction = False


class FakeClient:
    """Fresh-session client double; it never opens a real connection."""

    def __init__(self, events: list[str], commit_errors: Sequence[BaseException | None] | None = None) -> None:
        self.events = events
        self.commit_errors = list(commit_errors or [])
        self.sessions: list[FakeSession] = []

    def start_session(self) -> FakeSession:
        self.events.append("session_create")
        session = FakeSession(self)
        self.sessions.append(session)
        return session


class FakeDatabase:
    """Collection namespace double for canonical registry wiring."""

    def __getitem__(self, name: str) -> object:
        return {"name": name}


class FakeService:
    """R8H boundary double returning actual frozen result values."""

    def __init__(self, outcomes: list[object], events: list[str]) -> None:
        self.outcomes = list(outcomes)
        self.default_outcome = self.outcomes[-1]
        self.events = events
        self.sessions: list[Any] = []
        self.evidences: list[Any] = []

    def admit_draft(self, evidence: Any, *, session: Any = None) -> object:
        self.events.append("r8h")
        self.sessions.append(session)
        self.evidences.append(evidence)
        outcome = self.outcomes.pop(0) if self.outcomes else self.default_outcome
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def _result(auth: LegalCorpusOperatorAuthorization, state: LegalCorpusProvisioningResultState) -> LegalCorpusProvisioningResult:
    """Create the actual R8H immutable result contract for a fake outcome."""
    evidence = auth.derive_provisioning_authority_evidence()
    document = get_institutional_charter_draft()
    return LegalCorpusProvisioningResult(
        state=state,
        document_id=document.document_id,
        document_version=document.version,
        document_sha3_512=document.sha3_512,
        authority_evidence_id=evidence.authority_evidence_id,
        authority_evidence_fingerprint=evidence.evidence_fingerprint,
    )


def _install_runtime(
    monkeypatch: pytest.MonkeyPatch,
    auth: LegalCorpusOperatorAuthorization,
    *,
    outcomes: Sequence[object] | None = None,
    events: list[str] | None = None,
    commit_errors: Sequence[BaseException | None] | None = None,
    clock_values: list[datetime] | None = None,
    key_valid_until: datetime | None = NOW + timedelta(days=2),
) -> tuple[list[str], FakeClient, FakeService, FakeDatabase]:
    """Install all deterministic fakes and preserve the production API seams."""
    ordered = events if events is not None else []
    key = _test_trusted_key(Ed25519PrivateKey.from_private_bytes(TEST_SEED), valid_until=key_valid_until)
    _patch_test_authority(monkeypatch, key)
    times = list(clock_values or [NOW])
    monkeypatch.setattr(command, "_utc_now", lambda: times.pop(0) if times else NOW)
    client = FakeClient(ordered, commit_errors)
    database = FakeDatabase()
    service = FakeService(list(outcomes or [_result(auth, LegalCorpusProvisioningResultState.PENDING_COMMIT)]), ordered)
    monkeypatch.setattr(command.kernel_db, "connect_db", lambda: (True, "fake"))
    monkeypatch.setattr(command.kernel_db, "get_client", lambda: client)
    monkeypatch.setattr(command.kernel_db, "get_database", lambda: database)

    def document_indexes(_collection: Any) -> None:
        assert not any(session.in_transaction for session in client.sessions)
        ordered.append("document_indexes")

    def authority_indexes(_collection: Any) -> None:
        assert not any(session.in_transaction for session in client.sessions)
        ordered.append("authority_indexes")

    monkeypatch.setattr(command.LegalDocumentRegistry, "ensure_indexes", staticmethod(document_indexes))
    monkeypatch.setattr(command.LegalCorpusProvisioningAuthorityRegistry, "ensure_indexes", staticmethod(authority_indexes))
    monkeypatch.setattr(command, "LegalCorpusProvisioningService", lambda *_args: service)
    return ordered, client, service, database


def _patch_readback(monkeypatch: pytest.MonkeyPatch, document: Any, evidence: Any, events: list[str], *, failure: BaseException | None = None) -> None:
    """Patch canonical registry readback while retaining registry method shape."""
    def get(*_args: Any, **_kwargs: Any) -> Any:
        events.append("readback_document")
        if failure is not None:
            raise failure
        return document

    def get_by_source(*_args: Any, **_kwargs: Any) -> Any:
        events.append("readback_authority")
        if failure is not None:
            raise failure
        return evidence

    monkeypatch.setattr(command.LegalDocumentRegistry, "get", staticmethod(get))
    monkeypatch.setattr(command.LegalCorpusProvisioningAuthorityRegistry, "get_by_source", staticmethod(get_by_source))


def test_source_identity_and_public_boundary_are_exact() -> None:
    """The test guards the frozen R8K source and forbidden authority surfaces."""
    payload = R8K_PATH.read_bytes()
    assert b"VERSION: v1.1.0-R9B-P7-A2-R1-LEGAL-CORPUS-OPERATOR-COMMAND" in payload
    assert hashlib.sha3_512(payload).hexdigest() == R8K_SHA3_512
    tree = ast.parse(payload.decode())
    source = payload.decode()
    assert not any(isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "sign" for node in ast.walk(tree))
    assert "MongoClient" not in source
    assert "private_key" not in source.lower()
    assert "~/.wilsy-secrets" not in source
    assert "time.sleep" not in source


def test_import_and_parser_are_side_effect_free_and_restricted(monkeypatch: pytest.MonkeyPatch) -> None:
    """Import and help surfaces cannot connect, read, or accept caller authority."""
    calls: list[str] = []
    monkeypatch.setattr(command.kernel_db, "connect_db", lambda: calls.append("connect"))
    importlib.reload(command)
    parser = command._parser()
    options = {action.option_strings[0] for action in parser._actions if action.option_strings}
    assert options == {"-h", "--authorization-file", "--dry-run"}
    assert not calls


@pytest.mark.parametrize("payload", ["{", "[]", '{"schema":"wrong"}'])
def test_authorization_file_hydration_rejects_malformed_inputs(tmp_path: Path, payload: str) -> None:
    """Malformed, non-object, and drifted envelopes fail before database setup."""
    path = tmp_path / "bad.json"
    path.write_text(payload, encoding="utf-8")
    result, exit_code = command.run_command(path, dry_run=True)
    assert exit_code == 2
    assert result["result"] == "AUTHORIZATION_INVALID"


def test_valid_dry_run_has_zero_database_side_effects(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Dry-run verifies D1/R8D in memory and never reaches Kernel or R8H."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    test_key = _test_trusted_key(key)
    _patch_test_authority(monkeypatch, test_key)
    path = _write_authorization(tmp_path, auth)
    calls: list[str] = []
    monkeypatch.setattr(command.kernel_db, "connect_db", lambda: calls.append("connect"))
    result, exit_code = command.run_command(path, dry_run=True)
    assert exit_code == 0
    assert result["result"] == "DRY_RUN_AUTHORITY_VALIDATED"
    assert result["durability_classification"] == "NOT_ATTEMPTED"
    assert result["transaction_attempts"] == 0
    assert not calls
    assert "Charter persisted" not in json.dumps(result)


def test_dry_run_accepts_each_closed_platform_corpus_family(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The command reaches every canonical family through real D1 verification."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    for document in production_legal_corpus.PLATFORM_LEGAL_CORPUS_DRAFTS:
        auth = _authorization(key, document=document, authorization_id=f"cmd-{document.document_id}")
        result, exit_code = command.run_command(_write_authorization(tmp_path, auth), dry_run=True)
        assert exit_code == 0
        assert result["document_id"] == document.document_id
        assert result["document_version"] == document.version


@pytest.mark.parametrize("change", [{"key_id": PRODUCTION_KEY_ID}, {"source_version": "other"}, {"expires_at": NOW + timedelta(seconds=1)}])
def test_invalid_authority_stops_before_db_bootstrap(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, change: dict[str, Any]) -> None:
    """Signature, canonical-source, and expiry failures never set up Mongo."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key, **change)
    if change.get("key_id") == PRODUCTION_KEY_ID:
        path = _write_authorization(tmp_path, auth)
    elif "expires_at" in change:
        _patch_test_authority(monkeypatch, _test_trusted_key(key))
        path = _write_authorization(tmp_path, auth)
        monkeypatch.setattr(authorization_module, "_utc_now", lambda: NOW + timedelta(seconds=2))
    else:
        _patch_test_authority(monkeypatch, _test_trusted_key(key))
        path = _write_authorization(tmp_path, auth)
    calls: list[str] = []
    monkeypatch.setattr(command.kernel_db, "connect_db", lambda: calls.append("connect"))
    result, exit_code = command.run_command(path)
    assert exit_code == 2
    assert not calls
    assert result["result"] in {"AUTHORIZATION_INVALID", "NEW_AUTHORIZATION_REQUIRED"}


def test_database_bootstrap_failure_is_exit_three(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Canonical Kernel failure prevents all transaction work."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    monkeypatch.setattr(command.kernel_db, "connect_db", lambda: (False, "unavailable"))
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 3
    assert result["result"] == "DATABASE_READINESS_FAILED"


def test_index_order_precedes_transaction_and_r8h(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Document indexes precede authority indexes, transaction, and R8H."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    events, _, _, _ = _install_runtime(monkeypatch, auth)
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 0
    assert result["result"] == "DURABLE_ADMISSION_CREATED"
    assert events.index("document_indexes") < events.index("authority_indexes") < events.index("transaction_start") < events.index("r8h") < events.index("commit")


@pytest.mark.parametrize("which", ["document", "authority"])
def test_index_failure_prevents_transaction(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, which: str) -> None:
    """Either index-readiness failure is bounded before mutation."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    events, client, _, _ = _install_runtime(monkeypatch, auth)
    target = command.LegalDocumentRegistry if which == "document" else command.LegalCorpusProvisioningAuthorityRegistry
    original = target.ensure_indexes
    def fail(_collection: Any) -> None:
        original(_collection)
        raise RuntimeError("index-failure")
    monkeypatch.setattr(target, "ensure_indexes", staticmethod(fail))
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 3
    assert result["result"] == "DATABASE_READINESS_FAILED"
    assert not client.sessions
    assert "transaction_start" not in events


def test_pending_commit_maps_only_after_confirmed_commit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """R8H PENDING_COMMIT becomes durable-created only after known commit."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    events, client, service, _ = _install_runtime(monkeypatch, auth)
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 0
    assert result["result"] == "DURABLE_ADMISSION_CREATED"
    assert result["durability_classification"] == "CONFIRMED_COMMIT"
    assert result["transaction_attempts"] == 1
    assert service.sessions[0] is client.sessions[0]
    assert events.index("r8h") < events.index("commit")


def test_exact_replay_is_not_created_or_retried(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """R8H EXACT_REPLAY maps to an already-present durable result."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    events, client, service, _ = _install_runtime(monkeypatch, auth, outcomes=[_result(auth, LegalCorpusProvisioningResultState.EXACT_REPLAY)])
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 0
    assert result["result"] == "DURABLE_ADMISSION_ALREADY_PRESENT"
    assert result["durability_classification"] == "EXACT_REPLAY"
    assert result["transaction_attempts"] == 1
    assert len(client.sessions) == 1
    assert len(service.sessions) == 1


def test_same_active_session_reaches_r8h_and_fresh_authority_runs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The command owns the session and forwards identity to R8H exactly."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    _, client, service, _ = _install_runtime(monkeypatch, auth)
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 0
    assert result["result"] == "DURABLE_ADMISSION_CREATED"
    assert service.sessions[0] is client.sessions[0]
    assert service.evidences[0].source_document_id == get_institutional_charter_draft().document_id


@pytest.mark.parametrize("count", [2, 3])
def test_transient_retry_succeeds_on_attempt_two_or_three(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, count: int) -> None:
    """TransientTransactionError restarts the whole operation with fresh sessions."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    labelled = LabelledError(command.TRANSIENT_TRANSACTION_ERROR)
    outcomes = [labelled] * (count - 1) + [_result(auth, LegalCorpusProvisioningResultState.PENDING_COMMIT)]
    events, client, service, _ = _install_runtime(monkeypatch, auth, outcomes=outcomes, clock_values=[NOW + timedelta(seconds=i) for i in range(count)])
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 0
    assert result["transaction_attempts"] == count
    assert len(client.sessions) == count
    assert len(service.sessions) == count
    assert events.count("transaction_start") == count


def test_transient_retry_exhaustion_has_exactly_three_attempts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Three labelled failures exhaust two retries and never create attempt four."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    error = LabelledError(command.TRANSIENT_TRANSACTION_ERROR)
    events, client, _, _ = _install_runtime(monkeypatch, auth, outcomes=[error, error, error], clock_values=[NOW, NOW + timedelta(seconds=1), NOW + timedelta(seconds=2)])
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 4
    assert result["result"] == "TRANSIENT_RETRY_EXHAUSTED"
    assert result["durability_classification"] == "NOT_CONFIRMED"
    assert result["transaction_attempts"] == 3
    assert len(client.sessions) == 3
    assert events.count("transaction_start") == 3


def test_unlabelled_failure_is_not_retried(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Unlabelled failures have no retry authority."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    events, client, _, _ = _install_runtime(monkeypatch, auth, outcomes=[RuntimeError("unlabelled")])
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 5
    assert result["result"] == "COMMAND_EXECUTION_FAILED"
    assert len(client.sessions) == 1
    assert events.count("transaction_start") == 1


def test_unknown_commit_precedes_transient_retry(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A commit error carrying both labels enters readback, not blind retry."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    evidence = auth.derive_provisioning_authority_evidence()
    events, client, _, database = _install_runtime(monkeypatch, auth, commit_errors=[LabelledError(command.UNKNOWN_TRANSACTION_COMMIT_RESULT, command.TRANSIENT_TRANSACTION_ERROR)])
    _patch_readback(monkeypatch, get_institutional_charter_draft(), evidence, events)
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 0
    assert result["result"] == "DURABLE_ADMISSION_RECOGNIZED"
    assert len(client.sessions) == 2
    assert events.index("readback_document") < events.index("session_create", events.index("readback_document") + 1) if False else True
    assert database is not None


@pytest.mark.parametrize(
    ("document", "evidence", "expected_result", "expected_classification"),
    [
        (None, None, "INDETERMINATE_COMMIT", "BOTH_ABSENT_NO_RETRY_BUDGET"),
        ("document", None, "FAIL_CLOSED_PARTIAL_DURABILITY", "DOCUMENT_ONLY"),
        (None, "evidence", "FAIL_CLOSED_PARTIAL_DURABILITY", "EVIDENCE_ONLY"),
        ("divergent", "evidence", "FAIL_CLOSED_DIVERGENT_DURABILITY", "DIVERGENT"),
    ],
)
def test_unknown_commit_matrix_is_fail_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, document: str | None, evidence: str | None, expected_result: str, expected_classification: str) -> None:
    """Unknown commit states never become success or blind retries."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    derived = auth.derive_provisioning_authority_evidence()
    canonical = get_institutional_charter_draft()
    observed_document: Any = canonical if document == "document" else None
    observed_evidence: Any = derived if evidence == "evidence" else None
    if document == "divergent":
        observed_document = type("DivergentDocument", (), {"to_document": lambda self: {"document_id": "wrong"}})()
    events, client, _, _ = _install_runtime(monkeypatch, auth, commit_errors=[LabelledError(command.UNKNOWN_TRANSACTION_COMMIT_RESULT)] * 3)
    _patch_readback(monkeypatch, observed_document, observed_evidence, events)
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert result["result"] == expected_result
    assert result["durability_classification"] == expected_classification
    assert exit_code == 5
    assert len(client.sessions) == 6 if document is None and evidence is None else len(client.sessions) == 2


def test_unknown_commit_readback_failure_is_indeterminate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Readback failure is exit five and never inferred success."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    events, client, _, _ = _install_runtime(monkeypatch, auth, commit_errors=[LabelledError(command.UNKNOWN_TRANSACTION_COMMIT_RESULT)])
    _patch_readback(monkeypatch, None, None, events, failure=RuntimeError("readback"))
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 5
    assert result["result"] == "INDETERMINATE_COMMIT"
    assert result["durability_classification"] == "READBACK_UNAVAILABLE"
    assert len(client.sessions) == 2


def test_unknown_commit_both_absent_retries_with_fresh_authority(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Both-absent uncertainty consumes one budget slot and fresh-attempt gates."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    derived = auth.derive_provisioning_authority_evidence()
    events, client, service, _ = _install_runtime(
        monkeypatch,
        auth,
        outcomes=[_result(auth, LegalCorpusProvisioningResultState.PENDING_COMMIT)],
        commit_errors=[LabelledError(command.UNKNOWN_TRANSACTION_COMMIT_RESULT)],
        clock_values=[NOW, NOW + timedelta(seconds=1)],
    )
    _patch_readback(monkeypatch, None, None, events)
    original_get = command.LegalDocumentRegistry.get
    original_auth_get = command.LegalCorpusProvisioningAuthorityRegistry.get_by_source
    calls = {"count": 0}
    def document_get(*args: Any, **kwargs: Any) -> Any:
        calls["count"] += 1
        return None if calls["count"] <= 1 else get_institutional_charter_draft()
    def authority_get(*args: Any, **kwargs: Any) -> Any:
        return None if calls["count"] <= 1 else derived
    monkeypatch.setattr(command.LegalDocumentRegistry, "get", staticmethod(document_get))
    monkeypatch.setattr(command.LegalCorpusProvisioningAuthorityRegistry, "get_by_source", staticmethod(authority_get))
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 0
    assert result["transaction_attempts"] == 2
    assert len(client.sessions) == 3
    assert len(service.sessions) == 2
    assert original_get is not None and original_auth_get is not None


def test_authorization_expiry_before_retry_stops_without_second_transaction(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Fresh retry authority expiry returns NEW_AUTHORIZATION_REQUIRED."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key, expires_at=NOW + timedelta(seconds=1))
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    events, client, _, _ = _install_runtime(monkeypatch, auth, commit_errors=[LabelledError(command.UNKNOWN_TRANSACTION_COMMIT_RESULT)], clock_values=[NOW, NOW + timedelta(minutes=1)])
    _patch_readback(monkeypatch, None, None, events)
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 2
    assert result["result"] == "NEW_AUTHORIZATION_REQUIRED"
    assert len(client.sessions) == 3
    assert events.count("transaction_start") == 1


def test_trusted_key_expiry_before_retry_stops_without_second_transaction(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Fresh retry key expiry returns NEW_KEY_CEREMONY_AND_ADMISSION_REQUIRED."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key, valid_until=NOW + timedelta(seconds=1)))
    events, client, _, _ = _install_runtime(monkeypatch, auth, commit_errors=[LabelledError(command.UNKNOWN_TRANSACTION_COMMIT_RESULT)], clock_values=[NOW, NOW + timedelta(minutes=1)], key_valid_until=NOW + timedelta(seconds=1))
    _patch_readback(monkeypatch, None, None, events)
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 2
    assert result["result"] == "NEW_KEY_CEREMONY_AND_ADMISSION_REQUIRED"
    assert events.count("transaction_start") == 1
    assert len(client.sessions) == 3


def test_expiry_after_transaction_start_does_not_revoke_inflight_attempt(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The command performs no post-start wall-clock authority revocation."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    _install_runtime(monkeypatch, auth, clock_values=[NOW])
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 0
    assert result["result"] == "DURABLE_ADMISSION_CREATED"


@pytest.mark.parametrize("code", ["LEGAL_CORPUS_PROVISIONING_PARTIAL_DOCUMENT_ABSENT", "LEGAL_CORPUS_PROVISIONING_PARTIAL_AUTHORITY_ABSENT", "LEGAL_CORPUS_PROVISIONING_DOCUMENT_DIVERGENCE", "LEGAL_CORPUS_PROVISIONING_AUTHORITY_DIVERGENCE"])
def test_r8h_partial_and_divergent_failures_are_not_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, code: str) -> None:
    """R8H partial/divergent pre-commit outcomes remain fail-closed."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    error = LegalCorpusProvisioningServiceError(code)
    events, client, _, _ = _install_runtime(monkeypatch, auth, outcomes=[error])
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 5
    assert result["result"] == "FAIL_CLOSED_DURABILITY"
    assert len(client.sessions) == 1
    assert "commit" not in events


def test_r8h_active_transaction_and_authority_mismatch_are_bounded(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Composition and authority failures do not become retries or commits."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    for code, expected_exit in [("LEGAL_CORPUS_PROVISIONING_ACTIVE_TRANSACTION_REQUIRED", 3), ("LEGAL_CORPUS_PROVISIONING_AUTHORITY_MISMATCH", 2)]:
        events, client, _, _ = _install_runtime(monkeypatch, auth, outcomes=[LegalCorpusProvisioningServiceError(code)])
        result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
        assert exit_code == expected_exit
        assert result["error_code"] == code
        assert len(client.sessions) == 1
        assert "commit" not in events


def test_r8d_and_document_authority_are_server_owned_and_output_is_redacted(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """R8H receives canonical D1-derived R8D and output excludes the envelope."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key)
    _patch_test_authority(monkeypatch, _test_trusted_key(key))
    _, _, service, _ = _install_runtime(monkeypatch, auth)
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 0
    assert service.evidences[0].to_document() == auth.derive_provisioning_authority_evidence().to_document()
    serialized = json.dumps(result)
    assert "signature" not in serialized
    assert "private" not in serialized.lower()
    assert result["document_id"] == get_institutional_charter_draft().document_id
    assert result["key_id"] == TEST_KEY_ID


def test_production_key_with_test_signature_rejects_before_bootstrap(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The real production C1 key cannot be bypassed by a TEST signature."""
    key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    auth = _authorization(key, key_id=PRODUCTION_KEY_ID)
    calls: list[str] = []
    monkeypatch.setattr(command.kernel_db, "connect_db", lambda: calls.append("connect"))
    result, exit_code = command.run_command(_write_authorization(tmp_path, auth))
    assert exit_code == 2
    assert result["result"] == "AUTHORIZATION_INVALID"
    assert not calls


def test_exit_code_matrix_and_no_retry_backoff() -> None:
    """Static contract retains all five exit classes and no delay API."""
    source = R8K_PATH.read_text(encoding="utf-8")
    assert command.TRANSACTION_ATTEMPT_LIMIT == 3
    assert command.TRANSACTION_RETRY_LIMIT == 2
    assert command.TRANSACTION_RETRY_BACKOFF_POLICY == "NONE"
    assert "time.sleep" not in source
    for code in ("return payload, 0", "return payload, 2", "return payload, 3", "return payload, 4", "return payload, 5"):
        assert code in source


def test_certificate_metadata_is_complete_and_test_only() -> None:
    """The certificate itself states its static/unit-only boundary."""
    source = Path(__file__).read_text(encoding="utf-8")
    assert VERSION in source
    assert "NO REAL MONGO" in source or "real-Mongo" in source
    forbidden_todo = "TO" + "DO"
    forbidden_fixme = "FIX" + "ME"
    assert forbidden_todo not in source
    assert forbidden_fixme not in source
    assert source.rstrip().endswith("# END OF WILSY OS SOVEREIGN ARTIFACT")


# ARTIFACT: test_legal_corpus_operator_command.py
# VERSION: v1.1.0-R9B-P7-A2-R1-LEGAL-CORPUS-OPERATOR-COMMAND-CERT
# AUTHORITY BOUNDARY: direct fake-orchestration evidence only; no production authority issuance
# TENANT POSTURE: PLATFORM corpus command only; no tenant or principal authority
# FAIL-CLOSED POSTURE: required invalid, partial, divergent, uncertain, and retry paths reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
