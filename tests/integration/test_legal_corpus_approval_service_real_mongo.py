"""R9B-P4-P2 isolated real-Mongo certificate for approval promotion.

TITLE: WILSY OS Legal Corpus Approval Service Real-Mongo Certificate
VERSION: v1.1.0-R1D-B0F-R9B-P4-P2-R2-LEGAL-CORPUS-APPROVAL-SERVICE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies caller-owned Mongo transaction atomicity for the immutable
         legal-corpus approval service without claiming human approval,
         acceptance, execution, settlement, or current trust.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_corpus_approval_service_real_mongo.py
COLLABORATION / OWNERSHIP: The service composes already-verified authority;
                            this certificate owns only isolated real-Mongo
                            fixtures and caller transaction observation.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.1.0 repairs split-identity fixtures to use only independently
           verified proofs while preserving atomic CREATED/abort behavior,
           exact replay,
           complete partial/divergent/split/invalid fail-closed states,
           same-session forwarding, uncommitted visibility, and source
           immutability against the sanctioned local replica set.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic Ed25519 material is process-memory-only;
                            no credentials, private keys, or Mongo URI values
                            are emitted.
TENANT BOUNDARY: PLATFORM legal-corpus authority only; no tenant or principal
                 authority is created.
AUTHORITY BOUNDARY: A verified proof is consumed; this certificate does not
                    issue, review, approve, accept, sign, or authorize it.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Any missing, partial, divergent, split, corrupt, unsafe,
                     or transactionally ambiguous state fails closed.
"""
from __future__ import annotations

import ast
import base64
import inspect
import os
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import NAMESPACE_URL, UUID, uuid5

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

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
    APPROVAL_AUTHORITY_DOMAIN,
    APPROVAL_AUTHORITY_ROLE,
    APPROVAL_ISSUER_IDENTITY,
    APPROVAL_OPERATION,
    APPROVAL_SCOPE,
    ED25519_ALGORITHM,
    SCHEMA,
    LegalCorpusApprovalAuthorization,
    LegalCorpusApprovalAuthorizationOperation,
    LegalCorpusApprovalAuthorizationScope,
    VerifiedLegalCorpusApprovalAuthorization,
    canonical_signed_payload,
    verify_legal_corpus_approval_authorization,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_trust_root import (
    APPROVAL_TRUST_ROOT_PROVENANCE,
    LegalCorpusApprovalTrustRoot,
    LegalCorpusApprovalTrustStatus,
    LegalCorpusApprovalTrustedKey,
)
from tools.eos.legal_operations.registry.legal_corpus_approval_registry import (
    COLLECTION as APPROVAL_COLLECTION,
    LegalCorpusApprovalAdmissionState,
    LegalCorpusApprovalRegistry,
    LegalCorpusApprovalRegistryError,
    LegalCorpusApprovalPreflightState,
)
from tools.eos.legal_operations.registry.legal_document_registry import (
    COLLECTION as DOCUMENT_COLLECTION,
    LegalDocumentRegistry,
)
from tools.eos.legal_operations.service import legal_corpus_approval_service as service_module


UTC = timezone.utc
NOW = datetime(2026, 9, 19, 12, 0, 0, 123456, tzinfo=UTC)
URI_ENV = "TEST_VENDOR_MONGO_URI"
RUN_ENV = "WILSY_R9B_P4_P2_RUN_ID"
REPLICA_SET = "wilsyVendorCertRS"
RUN_ID = os.environ.get(RUN_ENV, "").strip()
if not RUN_ID or any(char not in "0123456789abcdef" for char in RUN_ID.casefold()):
    raise RuntimeError(f"{RUN_ENV} must be a non-empty hexadecimal value")
DATABASE_PREFIX = f"wilsy_r9b_p4_p2_{RUN_ID}_"
_DATABASE_SEQUENCE = 0
SOURCE = corpus.INSTITUTIONAL_CHARTER_DRAFT


def _private_key() -> Ed25519PrivateKey:
    """Return deterministic synthetic signing material held only in memory."""
    return Ed25519PrivateKey.from_private_bytes(bytes(range(32)))


def _trust_root(private_key: Ed25519PrivateKey) -> LegalCorpusApprovalTrustRoot:
    """Build the bounded synthetic trust root used solely by this certificate."""
    encoded = base64.urlsafe_b64encode(private_key.public_key().public_bytes_raw()).rstrip(b"=").decode("ascii")
    key_id = LegalCorpusApprovalTrustedKey.derive_key_id(encoded)
    values: dict[str, Any] = {
        "key_id": key_id,
        "issuer_identity": APPROVAL_ISSUER_IDENTITY,
        "authority_role": APPROVAL_AUTHORITY_ROLE,
        "authority_domain": APPROVAL_AUTHORITY_DOMAIN,
        "algorithm": ED25519_ALGORITHM,
        "public_key_base64url": encoded,
        "valid_from": datetime(2026, 9, 19, tzinfo=UTC),
        "valid_until": datetime(2026, 9, 20, tzinfo=UTC),
        "status": LegalCorpusApprovalTrustStatus.ACTIVE,
        "revision": 1,
        "permitted_operations": frozenset({APPROVAL_OPERATION}),
        "scope": APPROVAL_SCOPE,
        "trust_root_provenance": APPROVAL_TRUST_ROOT_PROVENANCE,
    }
    values["trust_fingerprint"] = LegalCorpusApprovalTrustedKey.fingerprint_for(**values)
    return LegalCorpusApprovalTrustRoot((LegalCorpusApprovalTrustedKey(**values),))


def _target(suffix: str, *, title: str | None = None) -> LegalDocumentVersion:
    """Build one deterministic APPROVED successor bound to the canonical draft."""
    reference = f"wilsy-os://legal/institutional-charter/approved-{suffix}"
    return LegalDocumentVersion(
        document_id=SOURCE.document_id,
        agreement_type=LegalAgreementType.INSTITUTIONAL_CHARTER,
        version=f"1.0.0-APPROVED-{suffix}",
        title=title or SOURCE.title,
        jurisdiction=SOURCE.jurisdiction,
        locale=SOURCE.locale,
        effective_from=datetime(2026, 10, 1, tzinfo=UTC),
        status=LegalDocumentStatus.APPROVED,
        content_reference=reference,
        content=SOURCE.content,
        sha3_512=canonical_document_digest(SOURCE.content, reference),
        created_at=datetime(2026, 9, 19, 11, 0, tzinfo=UTC),
        supersedes_document_id=SOURCE.document_id,
    )


def _uuid(suffix: str, kind: str) -> str:
    """Produce a valid deterministic UUID4-shaped identity for one fixture."""
    return str(UUID(bytes=uuid5(NAMESPACE_URL, f"r9b-p4-p2:{kind}:{suffix}").bytes, version=4))


def _proof(
    suffix: str,
    *,
    target: LegalDocumentVersion | None = None,
    evidence_id: str | None = None,
    authorization_id: str | None = None,
) -> VerifiedLegalCorpusApprovalAuthorization:
    """Create a genuinely signed, source-bound proof for the real registries."""
    private_key = _private_key()
    approved = target or _target(suffix)
    evidence_values: dict[str, Any] = {
        "approval_evidence_id": evidence_id or f"approval-evidence-{suffix}",
        "schema_version": "v1.0.0",
        "scope": LegalCorpusApprovalAuthorityScope.PLATFORM,
        "operation": LegalCorpusApprovalOperation.DOCUMENT_APPROVAL,
        "approval_decision": LegalCorpusApprovalDecision.APPROVE,
        "approval_authority_source": LegalCorpusApprovalAuthoritySource.HUMAN_GOVERNED,
        "approval_authority_mechanism": LegalCorpusApprovalAuthorityMechanism.HUMAN_APPROVAL_RECORD,
        "approval_authority_mechanism_version": APPROVAL_AUTHORITY_MECHANISM_VERSION,
        "human_authority_representation": f"synthetic-governance-{suffix}",
        "approval_signing_mechanism": LegalCorpusApprovalSigningMechanism.EXTERNAL_GOVERNED_SIGNER,
        "approval_signing_mechanism_version": APPROVAL_SIGNING_MECHANISM_VERSION,
        "approval_signing_key_id": f"synthetic-key-{suffix}",
        "approval_signature_reference": f"synthetic-signature-{suffix}",
        "source_document": SOURCE,
        "approved_document": approved,
        "approved_at": datetime(2026, 9, 19, 11, 30, tzinfo=UTC),
        "effective_from": approved.effective_from,
        "idempotency_key": f"evidence-idempotency-{suffix}",
        "provenance_reference": f"synthetic-provenance-{suffix}",
    }
    evidence_values["evidence_fingerprint"] = LegalCorpusApprovalAuthorityEvidence.fingerprint_for(**evidence_values)
    evidence = LegalCorpusApprovalAuthorityEvidence(**evidence_values)
    key = _trust_root(private_key).all_keys()[0]
    authorization_values: dict[str, Any] = {
        "schema": SCHEMA,
        "authorization_id": authorization_id or _uuid(suffix, "authorization"),
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
        "nonce": base64.urlsafe_b64encode((f"nonce-{suffix}".encode() * 8)[:32]).rstrip(b"=").decode("ascii"),
        "idempotency_key": _uuid(suffix, "authorization-idempotency"),
        "signature_base64url": base64.urlsafe_b64encode(b"s" * 64).rstrip(b"=").decode("ascii"),
    }
    unsigned = LegalCorpusApprovalAuthorization(**authorization_values)
    signature = base64.urlsafe_b64encode(private_key.sign(canonical_signed_payload(unsigned))).rstrip(b"=").decode("ascii")
    signed_values = dict(authorization_values)
    signed_values["signature_base64url"] = signature
    signed = LegalCorpusApprovalAuthorization(**signed_values)
    return verify_legal_corpus_approval_authorization(
        signed,
        _trust_root(private_key),
        now=NOW,
        source_document=SOURCE,
        approved_document=approved,
    )


def _durable_row(proof: VerifiedLegalCorpusApprovalAuthorization) -> dict[str, Any]:
    """Build the registry's public durable envelope without private imports."""
    row = dict(proof.authorization.to_document())
    row["approval_evidence_fingerprint"] = proof.approval_evidence.evidence_fingerprint
    return row


def _safe_name(label: str) -> str:
    """Return a bounded run-scoped database name."""
    del label
    global _DATABASE_SEQUENCE
    _DATABASE_SEQUENCE += 1
    name = f"{DATABASE_PREFIX}{_DATABASE_SEQUENCE}"
    assert len(name) <= 63
    assert name not in {"admin", "config", "local"}
    return name


@contextmanager
def _fresh_database(client: MongoClient[Any], label: str) -> Iterator[Any]:
    """Yield one isolated database and drop only that run-owned namespace."""
    name = _safe_name(label)
    assert name not in client.list_database_names()
    database = client.get_database(name, read_concern=ReadConcern("majority"), write_concern=WriteConcern(w="majority", j=True))
    try:
        yield database
    finally:
        assert name.startswith(DATABASE_PREFIX)
        client.drop_database(name)


@pytest.fixture(scope="module")
def mongo_runtime() -> Iterator[tuple[MongoClient[Any], dict[str, str]]]:
    """Anchor the sanctioned writable local replica set and clean leftovers."""
    uri = os.environ.get(URI_ENV, "").strip()
    if not uri:
        pytest.fail("R9B_P4_P2_ENVIRONMENT_BLOCKER:TEST_VENDOR_MONGO_URI_MISSING")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=3000, replicaSet=REPLICA_SET, retryWrites=True)
    try:
        hello = client.admin.command("hello")
        version = str(client.server_info().get("version", ""))
        assert hello.get("setName") == REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster", False)) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert version == "7.0.37"
        assert not [name for name in client.list_database_names() if name.startswith(DATABASE_PREFIX)]
        yield client, {"endpoint": "127.0.0.1:27027", "version": version, "replica_set": REPLICA_SET}
    except PyMongoError as error:
        pytest.fail(f"R9B_P4_P2_ENVIRONMENT_BLOCKER:{type(error).__name__}")
    finally:
        leftovers = [name for name in client.list_database_names() if name.startswith(DATABASE_PREFIX)]
        for name in leftovers:
            assert name.startswith(DATABASE_PREFIX)
            client.drop_database(name)
        assert not [name for name in client.list_database_names() if name.startswith(DATABASE_PREFIX)]
        client.close()


def _collections(database: Any) -> tuple[Any, Any]:
    """Create deployment indexes in the test harness, never in the service."""
    documents = database[DOCUMENT_COLLECTION]
    approvals = database[APPROVAL_COLLECTION]
    LegalDocumentRegistry.ensure_indexes(documents)
    LegalCorpusApprovalRegistry.ensure_indexes(approvals)
    return documents, approvals


def _seed_source(documents: Any) -> None:
    """Seed exactly the server-owned canonical draft before a transaction."""
    LegalDocumentRegistry.register(SOURCE, documents)


def _seed_pair(documents: Any, approvals: Any, proof: VerifiedLegalCorpusApprovalAuthorization) -> None:
    """Seed a committed exact target/evidence pair using the real registries."""
    LegalDocumentRegistry.register(proof.approval_evidence.approved_document, documents)
    result = LegalCorpusApprovalRegistry.admit_verified_approval(proof, approvals)
    assert result.state is LegalCorpusApprovalAdmissionState.CREATED


def _target_count(documents: Any, proof: VerifiedLegalCorpusApprovalAuthorization) -> int:
    return documents.count_documents({"document_id": proof.approval_evidence.approved_document_id, "version": proof.approval_evidence.approved_version})


def _evidence_count(approvals: Any, proof: VerifiedLegalCorpusApprovalAuthorization) -> int:
    return approvals.count_documents({"approval_evidence.approval_evidence_id": proof.approval_evidence.approval_evidence_id})


def _assert_source_unchanged(documents: Any) -> None:
    assert LegalDocumentRegistry.get(SOURCE.document_id, SOURCE.version, documents) == SOURCE


def test_runtime_identity_and_indexes(mongo_runtime: tuple[MongoClient[Any], dict[str, str]]) -> None:
    """Prove the sanctioned endpoint and isolated deployment indexes."""
    client, metadata = mongo_runtime
    assert metadata == {"endpoint": "127.0.0.1:27027", "version": "7.0.37", "replica_set": REPLICA_SET}
    with _fresh_database(client, "indexes") as database:
        documents, approvals = _collections(database)
        assert len(list(documents.list_indexes())) == 3
        assert len(list(approvals.list_indexes())) == 8


def test_atomic_created_commit_and_uncommitted_visibility(mongo_runtime: tuple[MongoClient[Any], dict[str, str]]) -> None:
    """CREATED stages both writes; only the caller commit makes them durable."""
    client, _ = mongo_runtime
    with _fresh_database(client, "created_commit") as database:
        documents, approvals = _collections(database)
        _seed_source(documents)
        proof = _proof("created-commit")
        service = service_module.LegalCorpusApprovalService(document_collection=documents, approval_collection=approvals)
        with client.start_session() as session:
            session.start_transaction()
            result = service.admit(proof, session=session)
            assert result.state is service_module.LegalCorpusApprovalResultState.CREATED
            assert LegalDocumentRegistry.get(proof.approval_evidence.approved_document_id, proof.approval_evidence.approved_version, documents, session=session) == proof.approval_evidence.approved_document
            assert LegalCorpusApprovalRegistry.preflight_verified_approval(proof, approvals, session=session).state is LegalCorpusApprovalPreflightState.EXACT
            assert _target_count(documents, proof) == 0
            assert _evidence_count(approvals, proof) == 0
            session.commit_transaction()
        assert _target_count(documents, proof) == 1
        assert _evidence_count(approvals, proof) == 1
        _assert_source_unchanged(documents)


def test_atomic_created_abort_rolls_back_both_sides(mongo_runtime: tuple[MongoClient[Any], dict[str, str]]) -> None:
    """Caller abort removes both staged rows and leaves the draft unchanged."""
    client, _ = mongo_runtime
    with _fresh_database(client, "created_abort") as database:
        documents, approvals = _collections(database)
        _seed_source(documents)
        proof = _proof("created-abort")
        service = service_module.LegalCorpusApprovalService(document_collection=documents, approval_collection=approvals)
        with client.start_session() as session:
            session.start_transaction()
            result = service.admit(proof, session=session)
            assert result.state is service_module.LegalCorpusApprovalResultState.CREATED
            session.abort_transaction()
        assert _target_count(documents, proof) == 0
        assert _evidence_count(approvals, proof) == 0
        _assert_source_unchanged(documents)


def test_exact_replay_real_mongo_is_zero_write(mongo_runtime: tuple[MongoClient[Any], dict[str, str]]) -> None:
    """A committed exact pair replays without either registry writing."""
    client, _ = mongo_runtime
    with _fresh_database(client, "exact_replay") as database:
        documents, approvals = _collections(database)
        _seed_source(documents)
        proof = _proof("exact-replay")
        _seed_pair(documents, approvals, proof)
        before = (_target_count(documents, proof), _evidence_count(approvals, proof))
        service = service_module.LegalCorpusApprovalService(document_collection=documents, approval_collection=approvals)
        with client.start_session() as session:
            session.start_transaction()
            result = service.admit(proof, session=session)
            assert result.state is service_module.LegalCorpusApprovalResultState.EXACT_REPLAY
            session.abort_transaction()
        assert (_target_count(documents, proof), _evidence_count(approvals, proof)) == before == (1, 1)
        _assert_source_unchanged(documents)


def test_target_only_partial_rejects_without_auto_heal(mongo_runtime: tuple[MongoClient[Any], dict[str, str]]) -> None:
    """A durable target without evidence is not an admission or replay."""
    client, _ = mongo_runtime
    with _fresh_database(client, "target_only") as database:
        documents, approvals = _collections(database)
        _seed_source(documents)
        proof = _proof("target-only")
        LegalDocumentRegistry.register(proof.approval_evidence.approved_document, documents)
        service = service_module.LegalCorpusApprovalService(document_collection=documents, approval_collection=approvals)
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(service_module.LegalCorpusApprovalServiceError, match="PARTIAL_STATE"):
                service.admit(proof, session=session)
            session.abort_transaction()
        assert _evidence_count(approvals, proof) == 0
        _assert_source_unchanged(documents)


def test_evidence_only_partial_rejects_without_auto_heal(mongo_runtime: tuple[MongoClient[Any], dict[str, str]]) -> None:
    """A durable approval record without its target is not an admission."""
    client, _ = mongo_runtime
    with _fresh_database(client, "evidence_only") as database:
        documents, approvals = _collections(database)
        _seed_source(documents)
        proof = _proof("evidence-only")
        assert LegalCorpusApprovalRegistry.admit_verified_approval(proof, approvals).state is LegalCorpusApprovalAdmissionState.CREATED
        service = service_module.LegalCorpusApprovalService(document_collection=documents, approval_collection=approvals)
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(service_module.LegalCorpusApprovalServiceError, match="PARTIAL_STATE"):
                service.admit(proof, session=session)
            session.abort_transaction()
        assert _target_count(documents, proof) == 0
        _assert_source_unchanged(documents)


def test_target_divergence_rejects_without_write(mongo_runtime: tuple[MongoClient[Any], dict[str, str]]) -> None:
    """A semantically divergent target at the exact identity fails closed."""
    client, _ = mongo_runtime
    with _fresh_database(client, "target_divergence") as database:
        documents, approvals = _collections(database)
        _seed_source(documents)
        proof = _proof("target-divergence")
        divergent = _target("target-divergence", title="Divergent persisted title")
        LegalDocumentRegistry.register(divergent, documents)
        service = service_module.LegalCorpusApprovalService(document_collection=documents, approval_collection=approvals)
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(service_module.LegalCorpusApprovalServiceError, match="TARGET_DIVERGENT"):
                service.admit(proof, session=session)
            session.abort_transaction()
        assert _evidence_count(approvals, proof) == 0
        _assert_source_unchanged(documents)


def test_evidence_divergence_rejects_without_write(mongo_runtime: tuple[MongoClient[Any], dict[str, str]]) -> None:
    """A matching evidence selector with divergent semantics fails closed."""
    client, _ = mongo_runtime
    with _fresh_database(client, "evidence_divergence") as database:
        documents, approvals = _collections(database)
        _seed_source(documents)
        proof = _proof("evidence-divergence")
        divergent = _proof("evidence-divergence-other", target=proof.approval_evidence.approved_document, evidence_id=proof.approval_evidence.approval_evidence_id)
        approvals.insert_one(_durable_row(divergent))
        service = service_module.LegalCorpusApprovalService(document_collection=documents, approval_collection=approvals)
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(service_module.LegalCorpusApprovalServiceError):
                service.admit(proof, session=session)
            session.abort_transaction()
        assert _target_count(documents, proof) == 0
        _assert_source_unchanged(documents)


def test_split_identity_rejects_without_write(mongo_runtime: tuple[MongoClient[Any], dict[str, str]]) -> None:
    """Rows split across selectors are consumed as SPLIT_IDENTITY, never replayed."""
    client, _ = mongo_runtime
    with _fresh_database(client, "split_identity") as database:
        documents, approvals = _collections(database)
        _seed_source(documents)
        incoming = _proof("split-incoming")
        row_a = _proof("split-row-a", target=incoming.approval_evidence.approved_document, evidence_id=incoming.approval_evidence.approval_evidence_id)
        row_b = _proof(
            "split-row-b",
            target=_target("split-row-b"),
            authorization_id=incoming.authorization.authorization_id,
        )
        approvals.insert_one(_durable_row(row_a))
        approvals.insert_one(_durable_row(row_b))
        preflight = LegalCorpusApprovalRegistry.preflight_verified_approval(incoming, approvals)
        assert preflight.state is LegalCorpusApprovalPreflightState.SPLIT_IDENTITY
        assert len(preflight.matched_identities) >= 2
        assert len(preflight.selector_to_row_identity) >= 2
        assert len(set(preflight.matched_identities)) >= 2
        service = service_module.LegalCorpusApprovalService(document_collection=documents, approval_collection=approvals)
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(service_module.LegalCorpusApprovalServiceError, match="SPLIT_OR_INVALID"):
                service.admit(incoming, session=session)
            session.abort_transaction()
        assert _target_count(documents, incoming) == 0
        assert _evidence_count(approvals, incoming) == 1
        _assert_source_unchanged(documents)


def test_verified_proofs_use_only_governed_verification_path() -> None:
    """AST closure rejects direct proof construction and proof replacement."""
    certificate_source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(certificate_source)
    direct_calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "VerifiedLegalCorpusApprovalAuthorization"
    ]
    verifier_calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "verify_legal_corpus_approval_authorization"
    ]
    replacement_calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and ((isinstance(node.func, ast.Name) and node.func.id == "replace")
             or (isinstance(node.func, ast.Attribute) and node.func.attr == "replace"))
    ]
    assert not direct_calls
    assert verifier_calls
    assert not replacement_calls


def test_persisted_invalid_rejects_before_target_creation(mongo_runtime: tuple[MongoClient[Any], dict[str, str]]) -> None:
    """A reachable corrupt evidence row blocks promotion and target creation."""
    client, _ = mongo_runtime
    with _fresh_database(client, "persisted_invalid") as database:
        documents, approvals = _collections(database)
        _seed_source(documents)
        proof = _proof("persisted-invalid")
        assert LegalCorpusApprovalRegistry.admit_verified_approval(proof, approvals).state is LegalCorpusApprovalAdmissionState.CREATED
        approvals.update_one({"approval_evidence.approval_evidence_id": proof.approval_evidence.approval_evidence_id}, {"$set": {"approval_evidence.source_content": "corrupt"}})
        service = service_module.LegalCorpusApprovalService(document_collection=documents, approval_collection=approvals)
        with client.start_session() as session:
            session.start_transaction()
            with pytest.raises(service_module.LegalCorpusApprovalServiceError, match="EVIDENCE_PREFLIGHT_FAILED"):
                service.admit(proof, session=session)
            session.abort_transaction()
        assert _target_count(documents, proof) == 0
        _assert_source_unchanged(documents)


def test_same_session_forwarding_real_mongo(mongo_runtime: tuple[MongoClient[Any], dict[str, str]], monkeypatch: pytest.MonkeyPatch) -> None:
    """The exact caller session reaches every real registry boundary."""
    client, _ = mongo_runtime
    with _fresh_database(client, "session_forwarding") as database:
        documents, approvals = _collections(database)
        _seed_source(documents)
        proof = _proof("session-forwarding")
        observed: list[Any] = []
        original_document_get = LegalDocumentRegistry.get
        original_document_register = LegalDocumentRegistry.register
        original_approval_preflight = LegalCorpusApprovalRegistry.preflight_verified_approval
        original_approval_admit = LegalCorpusApprovalRegistry.admit_verified_approval

        def document_get(document_id: str, version: str | None = None, collection: Any = None, *, session: Any = None) -> Any:
            observed.append(session)
            return original_document_get(document_id, version, collection, session=session)

        def document_register(document: LegalDocumentVersion, collection: Any = None, *, session: Any = None) -> Any:
            observed.append(session)
            return original_document_register(document, collection, session=session)

        def approval_preflight(proof_value: Any, collection: Any = None, *, session: Any = None) -> Any:
            observed.append(session)
            return original_approval_preflight(proof_value, collection, session=session)

        def approval_admit(proof_value: Any, collection: Any = None, *, session: Any = None) -> Any:
            observed.append(session)
            return original_approval_admit(proof_value, collection, session=session)

        monkeypatch.setattr(LegalDocumentRegistry, "get", staticmethod(document_get))
        monkeypatch.setattr(LegalDocumentRegistry, "register", staticmethod(document_register))
        monkeypatch.setattr(LegalCorpusApprovalRegistry, "preflight_verified_approval", staticmethod(approval_preflight))
        monkeypatch.setattr(LegalCorpusApprovalRegistry, "admit_verified_approval", staticmethod(approval_admit))
        with client.start_session() as session:
            session.start_transaction()
            result = service_module.LegalCorpusApprovalService(document_collection=documents, approval_collection=approvals).admit(proof, session=session)
            assert result.state is service_module.LegalCorpusApprovalResultState.CREATED
            assert observed and all(item is session for item in observed)
            session.abort_transaction()


def test_service_transaction_non_ownership_and_no_authority_expansion() -> None:
    """Static/runtime contract proves service owns no Mongo lifecycle or tenant authority."""
    source = inspect.getsource(service_module)
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert "MongoClient" not in names
    assert not {"start_transaction", "commit_transaction", "abort_transaction", "with_transaction"} & attributes
    assert "tenant_id" not in source and "principal_id" not in source
    assert not tuple(node for node in ast.walk(tree) if isinstance(node, (ast.While, ast.For, ast.AsyncFor)))


def test_service_result_contract_is_not_commit_or_unknown_commit_claim() -> None:
    """Result states remain CREATED/EXACT_REPLAY and never infer commit."""
    assert service_module.LegalCorpusApprovalResultState.CREATED.value == "CREATED"
    assert service_module.LegalCorpusApprovalResultState.EXACT_REPLAY.value == "EXACT_REPLAY"
    assert "COMMITTED" not in service_module.LegalCorpusApprovalResultState.CREATED.value


# ARTIFACT: test_legal_corpus_approval_service_real_mongo.py
# VERSION: v1.1.0-R1D-B0F-R9B-P4-P2-R2-LEGAL-CORPUS-APPROVAL-SERVICE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: caller-owned real-Mongo promotion evidence only
# TENANT POSTURE: isolated PLATFORM corpus namespaces; no tenant/principal authority
# FAIL-CLOSED POSTURE: atomicity, replay, partial, divergence, split, invalid,
#                      session, visibility, and source-immutability laws required
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
