"""Direct certificate for immutable legal-corpus approval promotion.

TITLE: WILSY OS Legal Corpus Approval Service Direct Certificate
VERSION: v1.0.0-R1D-B0F-R9B-P4-P1-LEGAL-CORPUS-APPROVAL-SERVICE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Independently certifies source-bound APPROVED promotion, pair-state
         arbitration, same-session forwarding, exact replay, and caller-owned
         transaction semantics with deterministic registry spies.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_approval_service.py
COLLABORATION / OWNERSHIP: The approval service owns composition only. Closed
                            verifier and registries retain their authority and
                            persistence contracts. This certificate uses no
                            Mongo server and no production authority input.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.0.0-R9B-P4-P1 certifies verified-proof admission, immutable
           draft-to-approved binding, complete pair-state failure closure,
           race readback, and caller-owned transaction boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic Ed25519 material and opaque fixture
                            values are memory-only; no secret or network path
                            is used.
TENANT BOUNDARY: PLATFORM corpus approval only; no tenant/principal authority.
AUTHORITY BOUNDARY: A passing test proves service behavior, not human
                    legitimacy, document approval, acceptance, or execution.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Missing proof/source, partial or divergent state, invalid
                     persistence, and non-exact race readback must reject.
"""
from __future__ import annotations

import ast
import base64
import inspect
import tokenize
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, cast

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.eos.legal_operations import production_legal_corpus as corpus
from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
    canonical_document_digest,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_authority import (
    APPROVAL_AUTHORITY_MECHANISM_VERSION,
    APPROVAL_SIGNING_MECHANISM_VERSION,
    LegalCorpusApprovalAuthorityEvidence,
    LegalCorpusApprovalAuthorityMechanism,
    LegalCorpusApprovalAuthorityScope,
    LegalCorpusApprovalAuthoritySource,
    LegalCorpusApprovalDecision,
    LegalCorpusApprovalOperation,
    LegalCorpusApprovalSigningMechanism,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_authorization import (
    AUTHORITY_SCOPE,
    AUTHORIZED_OPERATION,
    SCHEMA,
    LegalCorpusApprovalAuthorization,
    LegalCorpusApprovalAuthorizationError,
    LegalCorpusApprovalAuthorizationOperation,
    LegalCorpusApprovalAuthorizationScope,
    VerifiedLegalCorpusApprovalAuthorization,
    canonical_signed_payload,
    verify_legal_corpus_approval_authorization,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_trust_root import (
    APPROVAL_AUTHORITY_DOMAIN,
    APPROVAL_AUTHORITY_ROLE,
    APPROVAL_ISSUER_IDENTITY,
    APPROVAL_OPERATION,
    APPROVAL_SCOPE,
    APPROVAL_TRUST_ROOT_PROVENANCE,
    ED25519_ALGORITHM,
    LegalCorpusApprovalTrustRoot,
    LegalCorpusApprovalTrustStatus,
    LegalCorpusApprovalTrustedKey,
)
from tools.eos.legal_operations.registry.legal_corpus_approval_registry import (
    LegalCorpusApprovalAdmissionResult,
    LegalCorpusApprovalAdmissionState,
    LegalCorpusApprovalPreflight,
    LegalCorpusApprovalPreflightState,
    LegalCorpusApprovalRegistryError,
)
from tools.eos.legal_operations.registry.legal_document_registry import LegalDocumentRegistryError
from tools.eos.legal_operations.service import legal_corpus_approval_service as service_module


UTC = timezone.utc
NOW = datetime(2026, 9, 19, 12, 0, 0, 123456, tzinfo=UTC)
SOURCE = corpus.INSTITUTIONAL_CHARTER_DRAFT
TARGET_REFERENCE = "wilsy-os://legal/institutional-charter/1.0.0-approved"


class Session:
    """Minimal caller-owned transaction sentinel."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active
        self.commit_calls = 0
        self.abort_calls = 0
        self.start_calls = 0


def _target(**changes: Any) -> LegalDocumentVersion:
    values: dict[str, Any] = {
        "document_id": SOURCE.document_id,
        "agreement_type": LegalAgreementType.INSTITUTIONAL_CHARTER,
        "version": "1.0.0-APPROVED",
        "title": SOURCE.title,
        "jurisdiction": SOURCE.jurisdiction,
        "locale": SOURCE.locale,
        "effective_from": datetime(2026, 10, 1, tzinfo=UTC),
        "status": LegalDocumentStatus.APPROVED,
        "content_reference": TARGET_REFERENCE,
        "content": SOURCE.content,
        "sha3_512": canonical_document_digest(SOURCE.content, TARGET_REFERENCE),
        "created_at": datetime(2026, 9, 19, 11, 0, tzinfo=UTC),
        "supersedes_document_id": SOURCE.document_id,
    }
    values.update(changes)
    if "content" in changes or "content_reference" in changes:
        values["sha3_512"] = canonical_document_digest(values["content"], values["content_reference"])
    return LegalDocumentVersion(**values)


def _evidence(
    *,
    source_document: LegalDocumentVersion = SOURCE,
    approved_document: LegalDocumentVersion | None = None,
    **changes: Any,
) -> LegalCorpusApprovalAuthorityEvidence:
    target = approved_document or _target()
    values: dict[str, Any] = {
        "approval_evidence_id": "approval-evidence-service-001",
        "schema_version": "v1.0.0",
        "scope": LegalCorpusApprovalAuthorityScope.PLATFORM,
        "operation": LegalCorpusApprovalOperation.DOCUMENT_APPROVAL,
        "approval_decision": LegalCorpusApprovalDecision.APPROVE,
        "approval_authority_source": LegalCorpusApprovalAuthoritySource.HUMAN_GOVERNED,
        "approval_authority_mechanism": LegalCorpusApprovalAuthorityMechanism.HUMAN_APPROVAL_RECORD,
        "approval_authority_mechanism_version": APPROVAL_AUTHORITY_MECHANISM_VERSION,
        "human_authority_representation": "governance-record-service-001",
        "approval_signing_mechanism": LegalCorpusApprovalSigningMechanism.EXTERNAL_GOVERNED_SIGNER,
        "approval_signing_mechanism_version": APPROVAL_SIGNING_MECHANISM_VERSION,
        "approval_signing_key_id": "approval-key-service-001",
        "approval_signature_reference": "approval-signature-service-001",
        "source_document": source_document,
        "approved_document": target,
        "approved_at": datetime(2026, 9, 19, 11, 30, tzinfo=UTC),
        "effective_from": target.effective_from,
        "idempotency_key": "approval-idempotency-service-001",
        "provenance_reference": "provenance-service-001",
    }
    values.update(changes)
    values["evidence_fingerprint"] = LegalCorpusApprovalAuthorityEvidence.fingerprint_for(**values)
    return LegalCorpusApprovalAuthorityEvidence(**values)


def _private() -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(bytes(range(32)))


def _trust_root(private_key: Ed25519PrivateKey) -> LegalCorpusApprovalTrustRoot:
    encoded = base64.urlsafe_b64encode(private_key.public_key().public_bytes_raw()).rstrip(b"=").decode("ascii")
    key_id = LegalCorpusApprovalTrustedKey.derive_key_id(encoded)
    valid_from = datetime(2026, 9, 19, tzinfo=UTC)
    valid_until = datetime(2026, 9, 20, tzinfo=UTC)
    fingerprint = LegalCorpusApprovalTrustedKey.fingerprint_for(
        key_id=key_id,
        issuer_identity=APPROVAL_ISSUER_IDENTITY,
        authority_role=APPROVAL_AUTHORITY_ROLE,
        authority_domain=APPROVAL_AUTHORITY_DOMAIN,
        algorithm=ED25519_ALGORITHM,
        public_key_base64url=encoded,
        valid_from=valid_from,
        valid_until=valid_until,
        status=LegalCorpusApprovalTrustStatus.ACTIVE,
        revision=1,
        permitted_operations=frozenset({APPROVAL_OPERATION}),
        scope=APPROVAL_SCOPE,
        trust_root_provenance=APPROVAL_TRUST_ROOT_PROVENANCE,
    )
    return LegalCorpusApprovalTrustRoot(
        (
            LegalCorpusApprovalTrustedKey(
                key_id=key_id,
                issuer_identity=APPROVAL_ISSUER_IDENTITY,
                authority_role=APPROVAL_AUTHORITY_ROLE,
                authority_domain=APPROVAL_AUTHORITY_DOMAIN,
                algorithm=ED25519_ALGORITHM,
                public_key_base64url=encoded,
                valid_from=valid_from,
                valid_until=valid_until,
                status=LegalCorpusApprovalTrustStatus.ACTIVE,
                revision=1,
                permitted_operations=frozenset({APPROVAL_OPERATION}),
                scope=APPROVAL_SCOPE,
                trust_root_provenance=APPROVAL_TRUST_ROOT_PROVENANCE,
                trust_fingerprint=fingerprint,
            ),
        )
    )


def _proof(**changes: Any) -> VerifiedLegalCorpusApprovalAuthorization:
    private_key = _private()
    evidence = changes.pop("evidence", _evidence())
    root = _trust_root(private_key)
    key = root.all_keys()[0]
    values: dict[str, Any] = {
        "authorization_id": "123e4567-e89b-42d3-a456-426614174100",
        "issuer_identity": APPROVAL_ISSUER_IDENTITY,
        "authority_role": APPROVAL_AUTHORITY_ROLE,
        "authority_domain": APPROVAL_AUTHORITY_DOMAIN,
        "algorithm": ED25519_ALGORITHM,
        "key_id": key.key_id,
        "trust_fingerprint": key.trust_fingerprint,
        "operation": LegalCorpusApprovalAuthorizationOperation.DOCUMENT_APPROVAL,
        "scope": LegalCorpusApprovalAuthorizationScope.PLATFORM,
        "approval_evidence": evidence,
        "issued_at": NOW,
        "expires_at": NOW + timedelta(minutes=30),
        "nonce": base64.urlsafe_b64encode(b"n" * 32).rstrip(b"=").decode("ascii"),
        "idempotency_key": "223e4567-e89b-42d3-a456-426614174101",
        "signature_base64url": base64.urlsafe_b64encode(b"s" * 64).rstrip(b"=").decode("ascii"),
        "schema": SCHEMA,
    }
    values.update(changes)
    unsigned = LegalCorpusApprovalAuthorization(**cast(Any, values))
    signature = private_key.sign(canonical_signed_payload(unsigned))
    signed = replace(unsigned, signature_base64url=base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii"))
    return verify_legal_corpus_approval_authorization(
        signed,
        root,
        now=NOW,
        expected_evidence=evidence,
        source_document=evidence.source_document,
        approved_document=evidence.approved_document,
    )


class SpyDocumentRegistry:
    """Independent document persistence spy with explicit session evidence."""

    def __init__(self, source: LegalDocumentVersion = SOURCE, target: LegalDocumentVersion | None = None) -> None:
        self.documents = {(source.document_id, source.version): source}
        if target is not None:
            self.documents[(target.document_id, target.version)] = target
        self.events: list[str] = []
        self.read_sessions: list[Any] = []
        self.write_sessions: list[Any] = []
        self.register_failure: LegalDocumentRegistryError | None = None
        self.register_failure_hook: Callable[[], None] | None = None

    def get(self, document_id: str, version: str, collection: Any = None, *, session: Any = None) -> Any:
        del collection
        self.events.append("document_read")
        self.read_sessions.append(session)
        return self.documents.get((document_id, version))

    def register(self, document: LegalDocumentVersion, collection: Any = None, *, session: Any = None) -> Any:
        del collection
        self.events.append("document_write")
        self.write_sessions.append(session)
        if self.register_failure is not None:
            if self.register_failure_hook is not None:
                self.register_failure_hook()
            raise self.register_failure
        self.documents[(document.document_id, document.version)] = document
        return document


class SpyApprovalRegistry:
    """Independent approval registry spy with queued preflight states."""

    def __init__(self, proof: VerifiedLegalCorpusApprovalAuthorization, mode: str = "ABSENT") -> None:
        self.proof = proof
        self.modes = [mode]
        self.events: list[str] = []
        self.read_sessions: list[Any] = []
        self.write_sessions: list[Any] = []
        self.admit_failure: LegalCorpusApprovalRegistryError | None = None

    def _preflight(self, mode: str) -> LegalCorpusApprovalPreflight:
        if mode == "ABSENT":
            return LegalCorpusApprovalPreflight(LegalCorpusApprovalPreflightState.ABSENT, None, (), (), None)
        record = service_record(self.proof)
        if mode == "EXACT":
            return LegalCorpusApprovalPreflight(LegalCorpusApprovalPreflightState.EXACT, record, ("mongo:1",), (("all", "mongo:1"),), None)
        if mode == "DIVERGENT":
            return LegalCorpusApprovalPreflight(LegalCorpusApprovalPreflightState.DIVERGENT, record, ("mongo:1",), (("evidence_id", "mongo:1"),), "CONFLICT")
        if mode == "SPLIT":
            return LegalCorpusApprovalPreflight(LegalCorpusApprovalPreflightState.SPLIT_IDENTITY, None, ("mongo:1", "mongo:2"), (("evidence_id", "mongo:1"), ("authorization_id", "mongo:2")), None)
        raise LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID")

    def preflight_verified_approval(self, proof: Any, collection: Any = None, *, session: Any = None) -> LegalCorpusApprovalPreflight:
        del collection
        self.events.append("approval_read")
        self.read_sessions.append(session)
        mode = self.modes.pop(0) if len(self.modes) > 1 else self.modes[0]
        return self._preflight(mode)

    def admit_verified_approval(self, proof: Any, collection: Any = None, *, session: Any = None) -> LegalCorpusApprovalAdmissionResult:
        del collection
        self.events.append("approval_write")
        self.write_sessions.append(session)
        if self.admit_failure is not None:
            raise self.admit_failure
        return LegalCorpusApprovalAdmissionResult(LegalCorpusApprovalAdmissionState.CREATED, service_record(proof))


def service_record(proof: VerifiedLegalCorpusApprovalAuthorization) -> Any:
    """Build the public durable read model without private service helpers."""
    from tools.eos.legal_operations.registry.legal_corpus_approval_registry import LegalCorpusApprovalDurableRecord

    return LegalCorpusApprovalDurableRecord(proof.authorization, proof.approval_evidence.evidence_fingerprint)


def _service(
    proof: VerifiedLegalCorpusApprovalAuthorization,
    *,
    target: LegalDocumentVersion | None = None,
    evidence_mode: str = "ABSENT",
) -> tuple[service_module.LegalCorpusApprovalService, SpyDocumentRegistry, SpyApprovalRegistry, Session]:
    documents = SpyDocumentRegistry(target=target)
    approvals = SpyApprovalRegistry(proof, evidence_mode)
    session = Session()
    instance = service_module.LegalCorpusApprovalService(
        document_registry=cast(Any, documents),
        approval_registry=cast(Any, approvals),
    )
    return instance, documents, approvals, session


def _error(call: Callable[[], Any]) -> service_module.LegalCorpusApprovalServiceError:
    with pytest.raises(service_module.LegalCorpusApprovalServiceError) as captured:
        call()
    return captured.value


def test_verified_proof_is_required_and_authority_inputs_are_not_invented() -> None:
    proof = _proof()
    service, _, _, session = _service(proof)
    assert _error(lambda: service.admit(cast(Any, object()), session=session)).code == "LEGAL_CORPUS_APPROVAL_VERIFIED_PROOF_REQUIRED"
    assert "approved_document" not in inspect.signature(service.admit).parameters
    assert "authority_evidence" not in inspect.signature(service.admit).parameters


def test_missing_source_fails_closed_before_any_write() -> None:
    proof = _proof()
    service, documents, approvals, session = _service(proof)
    documents.documents.clear()
    assert _error(lambda: service.admit(proof, session=session)).code == "LEGAL_CORPUS_APPROVAL_SOURCE_MISSING"
    assert documents.write_sessions == [] and approvals.write_sessions == []


def test_source_binding_target_binding_and_source_immutability() -> None:
    proof = _proof()
    service, documents, approvals, session = _service(proof)
    before = SOURCE.to_document()
    result = service.admit(proof, session=session)
    assert result.state is service_module.LegalCorpusApprovalResultState.CREATED
    assert result.approved_document == proof.approval_evidence.approved_document
    assert documents.documents[(SOURCE.document_id, SOURCE.version)].to_document() == before
    assert approvals.write_sessions == [session]


def test_both_absent_writes_target_then_evidence_with_same_session() -> None:
    proof = _proof()
    service, documents, approvals, session = _service(proof)
    events: list[str] = []
    documents.events = events
    approvals.events = events
    result = service.admit(proof, session=session)
    assert result.state is service_module.LegalCorpusApprovalResultState.CREATED
    assert events == ["document_read", "document_read", "approval_read", "document_write", "approval_write"]
    assert documents.write_sessions == [session] and approvals.write_sessions == [session]
    assert documents.documents[(proof.approval_evidence.approved_document_id, proof.approval_evidence.approved_version)] == result.approved_document


def test_exact_replay_returns_both_durable_sides_without_writes() -> None:
    proof = _proof()
    service, documents, approvals, session = _service(proof, target=proof.approval_evidence.approved_document, evidence_mode="EXACT")
    result = service.admit(proof, session=session)
    assert result.state is service_module.LegalCorpusApprovalResultState.EXACT_REPLAY
    assert documents.write_sessions == [] and approvals.write_sessions == []


@pytest.mark.parametrize("target,evidence_mode", [( _target(), "ABSENT"), (None, "EXACT")])
def test_partial_pair_state_fails_closed(target: LegalDocumentVersion | None, evidence_mode: str) -> None:
    proof = _proof()
    service, _, _, session = _service(proof, target=target, evidence_mode=evidence_mode)
    assert _error(lambda: service.admit(proof, session=session)).code == "LEGAL_CORPUS_APPROVAL_PARTIAL_STATE"


def test_target_divergence_fails_closed() -> None:
    proof = _proof()
    divergent = _target(title="Divergent approved title")
    service, _, _, session = _service(proof, target=divergent, evidence_mode="ABSENT")
    assert _error(lambda: service.admit(proof, session=session)).code == "LEGAL_CORPUS_APPROVAL_TARGET_DIVERGENT"


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("DIVERGENT", "LEGAL_CORPUS_APPROVAL_TARGET_DIVERGENT"),
        ("SPLIT", "LEGAL_CORPUS_APPROVAL_EVIDENCE_SPLIT_OR_INVALID"),
    ],
)
def test_evidence_divergence_and_split_fail_closed(mode: str, expected: str) -> None:
    proof = _proof()
    service, _, _, session = _service(proof, evidence_mode=mode)
    assert _error(lambda: service.admit(proof, session=session)).code == expected


def test_persisted_invalid_evidence_fails_closed() -> None:
    proof = _proof()
    service, _, approvals, session = _service(proof)
    approvals.modes = ["INVALID"]
    assert _error(lambda: service.admit(proof, session=session)).code == "LEGAL_CORPUS_APPROVAL_EVIDENCE_PREFLIGHT_FAILED"


def test_race_readback_exact_replays() -> None:
    proof = _proof()
    service, documents, approvals, session = _service(proof)
    documents.register_failure = LegalDocumentRegistryError("LEGAL_DOCUMENT_DUPLICATE_UNAVAILABLE")
    documents.register_failure_hook = lambda: documents.documents.__setitem__((proof.approval_evidence.approved_document_id, proof.approval_evidence.approved_version), proof.approval_evidence.approved_document)
    approvals.modes = ["ABSENT", "EXACT"]
    result = service.admit(proof, session=session)
    assert result.state is service_module.LegalCorpusApprovalResultState.EXACT_REPLAY


@pytest.mark.parametrize("hook,mode", [
    (lambda d, p: d.documents.__setitem__((p.approval_evidence.approved_document_id, p.approval_evidence.approved_version), p.approval_evidence.approved_document), "ABSENT"),
    (lambda d, p: d.documents.__setitem__((p.approval_evidence.approved_document_id, p.approval_evidence.approved_version), _target(title="Race divergent")), "ABSENT"),
    (lambda d, p: None, "SPLIT"),
])
def test_race_readback_non_exact_fails_closed(hook: Callable[[SpyDocumentRegistry, VerifiedLegalCorpusApprovalAuthorization], None], mode: str) -> None:
    proof = _proof()
    service, documents, approvals, session = _service(proof)
    documents.register_failure = LegalDocumentRegistryError("LEGAL_DOCUMENT_DUPLICATE_UNAVAILABLE")
    documents.register_failure_hook = lambda: hook(documents, proof)
    approvals.modes = ["ABSENT", mode]
    error = _error(lambda: service.admit(proof, session=session))
    assert error.code == "LEGAL_CORPUS_APPROVAL_TARGET_WRITE_FAILED_RACE_NOT_EXACT"


def test_second_write_failure_preserves_cause_and_does_not_compensate() -> None:
    proof = _proof()
    service, documents, approvals, session = _service(proof)
    approvals.admit_failure = LegalCorpusApprovalRegistryError("LEGAL_CORPUS_APPROVAL_CREATE_FAILED")
    error = _error(lambda: service.admit(proof, session=session))
    assert error.code == "LEGAL_CORPUS_APPROVAL_EVIDENCE_WRITE_FAILED_RACE_NOT_EXACT"
    assert isinstance(error.__cause__, LegalCorpusApprovalRegistryError)
    assert documents.write_sessions == [session] and approvals.write_sessions == [session]


def test_first_write_failure_stops_evidence_write() -> None:
    proof = _proof()
    service, documents, approvals, session = _service(proof)
    documents.register_failure = LegalDocumentRegistryError("LEGAL_DOCUMENT_CREATE_FAILED")
    error = _error(lambda: service.admit(proof, session=session))
    assert error.code == "LEGAL_CORPUS_APPROVAL_TARGET_WRITE_FAILED_RACE_NOT_EXACT"
    assert approvals.write_sessions == []


def test_same_session_reaches_every_registry_call() -> None:
    proof = _proof()
    service, documents, approvals, session = _service(proof)
    service.admit(proof, session=session)
    assert all(item is session for item in documents.read_sessions + documents.write_sessions)
    assert all(item is session for item in approvals.read_sessions + approvals.write_sessions)


def test_no_service_transaction_or_retry_lifecycle() -> None:
    source = inspect.getsource(service_module)
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert "MongoClient" not in names
    assert not {"start_transaction", "commit_transaction", "abort_transaction", "with_transaction"} & attributes
    executable_loops = tuple(node for node in ast.walk(tree) if isinstance(node, (ast.While, ast.For, ast.AsyncFor)))
    assert executable_loops == ()
    module_docstring = ast.get_docstring(tree) or ""
    function_docstrings = tuple(
        ast.get_docstring(node) or ""
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )
    assert "while " in module_docstring + " ".join(function_docstrings)
    string_literals = tuple(
        node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)
    )
    assert any("while " in value for value in string_literals)
    comments = tuple(
        token.string
        for token in tokenize.generate_tokens(iter(source.splitlines(keepends=True)).__next__)
        if token.type == tokenize.COMMENT
    )
    assert all("while " not in comment for comment in comments)


def test_created_result_never_infers_commit_or_unknown_commit() -> None:
    proof = _proof()
    service, _, _, session = _service(proof)
    result = service.admit(proof, session=session)
    assert result.state is service_module.LegalCorpusApprovalResultState.CREATED
    assert "COMMITTED" not in result.state.value
    assert session.commit_calls == 0 and session.abort_calls == 0 and session.start_calls == 0


def test_admin_and_authorised_signatory_labels_cannot_create_verified_authority() -> None:
    private_key = _private()
    root = _trust_root(private_key)
    proof = _proof()
    for role in ("admin", "authorised-signatory"):
        with pytest.raises(LegalCorpusApprovalAuthorizationError):
            altered = replace(proof.authorization, authority_role=role)
            verify_legal_corpus_approval_authorization(altered, root, now=NOW)


def test_source_and_target_lifecycle_contract_is_exact() -> None:
    proof = _proof()
    assert proof.approval_evidence.source_document.status is LegalDocumentStatus.DRAFT_REVIEW_REQUIRED
    assert proof.approval_evidence.approved_document.status is LegalDocumentStatus.APPROVED
    assert proof.approval_evidence.approved_document.version != proof.approval_evidence.source_document.version
    assert proof.approval_evidence.approved_document.supersedes_document_id == proof.approval_evidence.source_document.document_id


def test_public_result_is_frozen_and_carries_durable_evidence() -> None:
    proof = _proof()
    service, _, _, session = _service(proof)
    result = service.admit(proof, session=session)
    with pytest.raises((AttributeError, TypeError)):
        result.state = service_module.LegalCorpusApprovalResultState.EXACT_REPLAY  # type: ignore[misc]
    assert result.approval_evidence == proof.approval_evidence


def test_no_indexes_or_other_authority_surfaces_are_called() -> None:
    proof = _proof()
    service, documents, approvals, session = _service(proof)
    documents.ensure_indexes = lambda: (_ for _ in ()).throw(AssertionError("index deployment forbidden"))  # type: ignore[attr-defined]
    approvals.ensure_indexes = lambda: (_ for _ in ()).throw(AssertionError("index deployment forbidden"))  # type: ignore[attr-defined]
    result = service.admit(proof, session=session)
    assert result.state is service_module.LegalCorpusApprovalResultState.CREATED


# ARTIFACT: test_legal_corpus_approval_service.py
# VERSION: v1.0.0-R1D-B0F-R9B-P4-P1-LEGAL-CORPUS-APPROVAL-SERVICE-CERT
# AUTHORITY BOUNDARY: direct non-Mongo evidence for caller-owned approval promotion
# TENANT POSTURE: PLATFORM corpus only; no tenant/principal authority
# FAIL-CLOSED POSTURE: source, pair-state, race, session, and lifecycle laws are tested
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
