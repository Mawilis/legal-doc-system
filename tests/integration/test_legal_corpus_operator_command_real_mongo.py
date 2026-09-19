"""R8K-P3A real-Mongo certificate authoring artifact.

TITLE: WILSY OS Legal Corpus Operator Command Real-Mongo Certificate
VERSION: v1.1.0-R9B-P7-A2-R1-R1-LEGAL-CORPUS-OPERATOR-COMMAND-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the genuine Mongo session, transaction, atomic commit,
         rollback, immutable replay, index, hydration, and durable readback
         boundaries of the R8K operator command. This source-only P3A gate
         authors the certificate; its official host runtime is a later gate.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_corpus_operator_command_real_mongo.py
COLLABORATION / OWNERSHIP: R8K owns command lifecycle; R8H owns composition;
                           registries own immutable persistence; this artifact
                           owns only isolated real-Mongo evidence.
CERTIFICATION / UPDATE DATE: 2026-09-18
CHANGELOG: v1.1.0-R9B-P7-A2-R1-R1 repairs the deterministic six-family test
           identity so distinct admissions use distinct idempotency keys while
           exact replay retains the same key.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Deterministic TEST-only Ed25519 material is held
                            in memory; no production private key, secret file,
                            remote endpoint, or live corpus is permitted.
TENANT BOUNDARY: Platform corpus only; every database is UUID-isolated and
                 owned exclusively by this certificate invocation.
AUTHORITY BOUNDARY: TEST-only signed D1 verification and R8D derivation are
                    exercised; no production authorization is issued.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for
                              financial execution and settlement truth.
RUNTIME BOUNDARY: Static authoring does not constitute real-Mongo PASS. The
                  official host gate is the only runtime execution authority.
FAIL-CLOSED POSTURE: Non-loopback, unavailable, non-replica-set, non-primary,
                     partial, divergent, or non-atomic outcomes fail.
"""
from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlsplit
from uuid import uuid4

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.legal_operations.legal_corpus_operator_command as command
import tools.eos.legal_operations.domain.legal_corpus_operator_authorization as authorization_module
from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalDocumentStatus,
)
from tools.eos.legal_operations.domain.legal_corpus_operator_authorization import (
    AUTHORITY_MECHANISM,
    AUTHORITY_MECHANISM_VERSION,
    LegalCorpusOperatorAuthorization,
    LegalCorpusOperatorAuthorizationOperation,
    LegalCorpusOperatorAuthorizationScope,
)
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
from tools.eos.legal_operations.domain.legal_corpus_provisioning_authority import (
    LegalCorpusProvisioningAuthorityEvidence,
)
from tools.eos.legal_operations import production_legal_corpus
from tools.eos.legal_operations.production_legal_corpus import get_institutional_charter_draft
from tools.eos.legal_operations.registry.legal_corpus_provisioning_authority_registry import (
    LegalCorpusProvisioningAuthorityRegistry,
    LegalCorpusProvisioningAuthorityRegistryError,
)
from tools.eos.legal_operations.registry.legal_document_registry import (
    LegalDocumentRegistry,
)


VERSION = "v1.1.0-R9B-P7-A2-R1-R1-LEGAL-CORPUS-OPERATOR-COMMAND-REAL-MONGO-CERT"
DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
TEST_KEY_ID = "prdca-key:r8k-p3a-test"
TEST_SEED = bytes(range(32))
NOW = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _assert_loopback_uri(uri: str) -> None:
    """Reject Atlas, remote, SRV, and otherwise uncontrolled Mongo targets."""
    parsed = urlsplit(uri)
    if parsed.scheme != "mongodb" or not parsed.netloc:
        raise AssertionError("R8K_P3A_MONGO_URI_MUST_BE_LOOPBACK_MONGODB")
    authority = parsed.netloc.rsplit("@", 1)[-1]
    hosts = []
    for item in authority.split(","):
        host = item.rsplit(":", 1)[0].strip("[]") if ":" in item else item
        hosts.append(host.lower())
    if not hosts or any(host not in LOOPBACK_HOSTS for host in hosts):
        raise AssertionError("R8K_P3A_REMOTE_MONGO_FORBIDDEN")


@pytest.fixture()
def isolated_mongo_database() -> Iterator[tuple[Any, Any]]:
    """Own one disposable majority/read-write concern database per test.

    Missing or unsuitable Mongo is a certificate failure, never a skipped
    official runtime. The database name is generated only after a successful
    local replica-set hello and is dropped only by this fixture.
    """
    uri = os.environ.get("TEST_VENDOR_MONGO_URI", DEFAULT_URI)
    _assert_loopback_uri(uri)
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=3000,
        replicaSet=EXPECTED_REPLICA_SET,
        retryWrites=True,
    )
    database_name: str | None = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            raise AssertionError(
                f"R8K_P3A_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}"
            ) from error
        if hello.get("setName") != EXPECTED_REPLICA_SET or not hello.get(
            "isWritablePrimary", hello.get("ismaster", False)
        ):
            raise AssertionError("R8K_P3A_WRITABLE_CERTIFIED_REPLICA_SET_REQUIRED")
        database_name = "r8k_p3a_operator_command_" + uuid4().hex
        database = client.get_database(
            database_name,
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        yield client, database
    finally:
        if database_name is not None:
            client.drop_database(database_name)
        client.close()


def _test_trusted_key() -> tuple[Ed25519PrivateKey, LegalCorpusOperatorTrustedKey]:
    """Create deterministic in-memory TEST trust material, never production material."""
    private_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    public_key = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    public_key_text = base64.urlsafe_b64encode(public_key).rstrip(b"=").decode("ascii")
    values: dict[str, Any] = {
        "key_id": TEST_KEY_ID,
        "algorithm": ED25519_ALGORITHM,
        "public_key_base64url": public_key_text,
        "issuer_identity": "issuer:r8k-p3a-test",
        "authority_domain": AUTHORITY_DOMAIN,
        "scope": TRUST_ROOT_SCOPE,
        "permitted_operations": frozenset({AUTHORIZED_OPERATION}),
        "valid_from": NOW - timedelta(days=1),
        "valid_until": NOW + timedelta(days=2),
        "status": LegalCorpusOperatorKeyStatus.ACTIVE,
        "revision": 1,
        "trust_root_provenance": TRUST_ROOT_PROVENANCE,
    }
    values["fingerprint"] = LegalCorpusOperatorTrustedKey.fingerprint_for(**values)
    return private_key, LegalCorpusOperatorTrustedKey(**values)


def _install_test_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Ed25519PrivateKey, LegalCorpusOperatorTrustedKey]:
    """Patch only public trust resolution and deterministic clocks for TEST evidence."""
    private_key, trusted_key = _test_trusted_key()

    def resolve(key_id: str) -> LegalCorpusOperatorTrustedKey:
        if key_id != trusted_key.key_id:
            raise LegalCorpusOperatorTrustRootError("UNKNOWN_TRUSTED_KEY")
        return trusted_key

    monkeypatch.setattr(LegalCorpusOperatorTrustRoot, "resolve", staticmethod(resolve))
    monkeypatch.setattr(authorization_module, "_utc_now", lambda: NOW)
    monkeypatch.setattr(command, "_utc_now", lambda: NOW)
    return private_key, trusted_key


def _authorization(
    private_key: Ed25519PrivateKey,
    *,
    authorization_id: str = "r8k-p3a-auth-001",
    document: Any | None = None,
) -> LegalCorpusOperatorAuthorization:
    """Build one exact signed TEST authorization through canonical D1 payloads."""
    if document is None:
        document = get_institutional_charter_draft()
    values: dict[str, Any] = {
        "authorization_id": authorization_id,
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
        "replay_nonce": "r8k-p3a-replay-001",
        "idempotency_key": f"r8k-p3a-idempotency-{authorization_id}",
        "authority_mechanism": AUTHORITY_MECHANISM,
        "authority_mechanism_version": AUTHORITY_MECHANISM_VERSION,
        "signature": base64.urlsafe_b64encode(b"x" * 64).rstrip(b"=").decode("ascii"),
    }
    unsigned = LegalCorpusOperatorAuthorization(**values)
    values["signature"] = base64.urlsafe_b64encode(
        private_key.sign(unsigned.canonical_payload_bytes())
    ).rstrip(b"=").decode("ascii")
    return LegalCorpusOperatorAuthorization(**values)


def _write_authorization(tmp_path: Path, authorization: LegalCorpusOperatorAuthorization) -> Path:
    """Write one temporary TEST envelope consumed only by the command boundary."""
    path = tmp_path / "r8k-p3a-authorization.json"
    path.write_text(json.dumps(authorization.to_document()), encoding="utf-8")
    return path


def _wire_kernel(
    monkeypatch: pytest.MonkeyPatch,
    client: Any,
    database: Any,
) -> None:
    """Inject only the genuine isolated client/database at R8K's Kernel seam."""
    monkeypatch.setattr(command.kernel_db, "connect_db", lambda: (True, "isolated-test"))
    monkeypatch.setattr(command.kernel_db, "get_client", lambda: client)
    monkeypatch.setattr(command.kernel_db, "get_database", lambda: database)


def _index_map(collection: Any) -> dict[str, dict[str, Any]]:
    """Materialize actual Mongo index metadata for semantic assertions."""
    return {str(item["name"]): dict(item) for item in collection.list_indexes()}


def _assert_real_indexes(database: Any) -> None:
    """Assert actual registry index names, key order, and uniqueness."""
    document_indexes = _index_map(database[command.DOCUMENT_COLLECTION])
    authority_indexes = _index_map(database[command.AUTHORITY_COLLECTION])
    assert document_indexes["legal_document_version_unique"]["unique"] is True
    assert list(document_indexes["legal_document_version_unique"]["key"].items()) == [
        ("document_id", 1),
        ("version", 1),
    ]
    assert document_indexes["legal_agreement_version_unique"]["unique"] is True
    assert list(document_indexes["legal_agreement_version_unique"]["key"].items()) == [
        ("agreement_type", 1),
        ("version", 1),
    ]
    assert authority_indexes[
        "legal_corpus_provisioning_authority_evidence_id_unique"
    ]["unique"] is True
    assert list(
        authority_indexes["legal_corpus_provisioning_authority_evidence_id_unique"]["key"].items()
    ) == [("authority_evidence_id", 1)]
    assert authority_indexes[
        "legal_corpus_provisioning_authority_source_version_unique"
    ]["unique"] is True
    assert list(
        authority_indexes["legal_corpus_provisioning_authority_source_version_unique"]["key"].items()
    ) == [
        ("scope", 1),
        ("operation", 1),
        ("source_document_id", 1),
        ("source_version", 1),
    ]
    assert authority_indexes["legal_corpus_provisioning_authority_idempotency_unique"]["unique"] is True


def test_real_transactional_admission_same_session_and_indexes(
    isolated_mongo_database: tuple[Any, Any],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Certify genuine transaction commit, same-session R8H, pair durability, and indexes."""
    client, database = isolated_mongo_database
    private_key, _ = _install_test_authority(monkeypatch)
    authorization = _authorization(private_key)
    expected_evidence = authorization.derive_provisioning_authority_evidence()
    _wire_kernel(monkeypatch, client, database)
    observation: dict[str, Any] = {}
    production_service = command.LegalCorpusProvisioningService

    class ObservingService(production_service):
        """Delegate to R8H while observing the genuine active session identity."""

        def admit_draft(self, authority_evidence: Any, *, session: Any = None) -> Any:
            observation["session"] = session
            observation["active"] = bool(getattr(session, "in_transaction", False))
            return super().admit_draft(authority_evidence, session=session)

    monkeypatch.setattr(command, "LegalCorpusProvisioningService", ObservingService)
    result, exit_code = command.run_command(_write_authorization(tmp_path, authorization))
    assert exit_code == 0
    assert result["result"] == "DURABLE_ADMISSION_CREATED"
    assert result["durability_classification"] == "CONFIRMED_COMMIT"
    assert result["transaction_attempts"] == 1
    assert observation["active"] is True
    assert observation["session"] is not None

    documents = database[command.DOCUMENT_COLLECTION]
    authorities = database[command.AUTHORITY_COLLECTION]
    assert documents.count_documents({}) == 1
    assert authorities.count_documents({}) == 1
    document = LegalDocumentRegistry.get(
        get_institutional_charter_draft().document_id,
        get_institutional_charter_draft().version,
        documents,
    )
    evidence = LegalCorpusProvisioningAuthorityRegistry.get_by_source(
        expected_evidence.source_document_id,
        expected_evidence.source_version,
        authorities,
    )
    assert document is not None
    assert evidence is not None
    assert document.to_document() == get_institutional_charter_draft().to_document()
    assert evidence.to_document() == expected_evidence.to_document()
    assert evidence.verify_against(get_institutional_charter_draft()) is None
    _assert_real_indexes(database)


def test_real_exact_replay_has_zero_new_durable_writes(
    isolated_mongo_database: tuple[Any, Any],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Certify fresh-session exact replay without a second immutable row."""
    client, database = isolated_mongo_database
    private_key, _ = _install_test_authority(monkeypatch)
    authorization = _authorization(private_key)
    _wire_kernel(monkeypatch, client, database)
    path = _write_authorization(tmp_path, authorization)
    first, first_exit = command.run_command(path)
    assert first_exit == 0
    assert first["result"] == "DURABLE_ADMISSION_CREATED"
    documents = database[command.DOCUMENT_COLLECTION]
    authorities = database[command.AUTHORITY_COLLECTION]
    first_document = LegalDocumentRegistry.get(
        get_institutional_charter_draft().document_id,
        get_institutional_charter_draft().version,
        documents,
    )
    first_evidence = LegalCorpusProvisioningAuthorityRegistry.get_by_source(
        get_institutional_charter_draft().document_id,
        get_institutional_charter_draft().version,
        authorities,
    )
    assert first_document is not None and first_evidence is not None
    before_counts = (documents.count_documents({}), authorities.count_documents({}))
    before_semantics = (first_document.to_document(), first_evidence.to_document())
    replay, replay_exit = command.run_command(path)
    assert replay_exit == 0
    assert replay["result"] == "DURABLE_ADMISSION_ALREADY_PRESENT"
    assert replay["durability_classification"] == "EXACT_REPLAY"
    assert replay["transaction_attempts"] == 1
    assert (documents.count_documents({}), authorities.count_documents({})) == before_counts
    replay_document = LegalDocumentRegistry.get(
        get_institutional_charter_draft().document_id,
        get_institutional_charter_draft().version,
        documents,
    )
    replay_evidence = LegalCorpusProvisioningAuthorityRegistry.get_by_source(
        get_institutional_charter_draft().document_id,
        get_institutional_charter_draft().version,
        authorities,
    )
    assert replay_document is not None and replay_evidence is not None
    assert (replay_document.to_document(), replay_evidence.to_document()) == before_semantics
    assert replay_document.document_id == first_document.document_id
    assert replay_evidence.authority_evidence_id == first_evidence.authority_evidence_id


def test_real_six_family_admission_capability(
    isolated_mongo_database: tuple[Any, Any],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Certify each closed platform draft through the genuine transaction path."""
    client, database = isolated_mongo_database
    private_key, _ = _install_test_authority(monkeypatch)
    _wire_kernel(monkeypatch, client, database)
    for index, document in enumerate(production_legal_corpus.PLATFORM_LEGAL_CORPUS_DRAFTS):
        authorization = _authorization(
            private_key,
            authorization_id=f"r8k-p3a-six-family-{index}",
            document=document,
        )
        result, exit_code = command.run_command(_write_authorization(tmp_path, authorization))
        assert exit_code == 0
        assert result["result"] == "DURABLE_ADMISSION_CREATED"
        assert result["document_id"] == document.document_id
        assert result["document_version"] == document.version
    assert database[command.DOCUMENT_COLLECTION].count_documents({}) == 6
    assert database[command.AUTHORITY_COLLECTION].count_documents({}) == 6


def test_real_transaction_rollback_removes_document_staged_before_second_write(
    isolated_mongo_database: tuple[Any, Any],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Certify real abort removes the first staged write after second-write failure."""
    client, database = isolated_mongo_database
    private_key, _ = _install_test_authority(monkeypatch)
    authorization = _authorization(private_key, authorization_id="r8k-p3a-rollback-001")
    _wire_kernel(monkeypatch, client, database)

    def fail_authority_write(*_args: Any, **_kwargs: Any) -> Any:
        raise LegalCorpusProvisioningAuthorityRegistryError("R8K_P3A_TEST_SECOND_WRITE_FAILURE")

    monkeypatch.setattr(
        command.LegalCorpusProvisioningAuthorityRegistry,
        "create_or_replay",
        staticmethod(fail_authority_write),
    )
    result, exit_code = command.run_command(_write_authorization(tmp_path, authorization))
    assert exit_code == 3
    assert result["result"] == "PROVISIONING_TRANSACTION_FAILED"
    assert database[command.DOCUMENT_COLLECTION].count_documents({}) == 0
    assert database[command.AUTHORITY_COLLECTION].count_documents({}) == 0


def test_real_registry_hydration_and_durable_readback_are_exact(
    isolated_mongo_database: tuple[Any, Any],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Certify canonical hydration and BOTH_EXACT readback without simulating unknown commit."""
    client, database = isolated_mongo_database
    private_key, _ = _install_test_authority(monkeypatch)
    authorization = _authorization(private_key, authorization_id="r8k-p3a-readback-001")
    expected_evidence = authorization.derive_provisioning_authority_evidence()
    _wire_kernel(monkeypatch, client, database)
    result, exit_code = command.run_command(_write_authorization(tmp_path, authorization))
    assert exit_code == 0
    assert result["durability_classification"] == "CONFIRMED_COMMIT"
    documents = database[command.DOCUMENT_COLLECTION]
    authorities = database[command.AUTHORITY_COLLECTION]
    document = LegalDocumentRegistry.get(
        expected_evidence.source_document_id,
        expected_evidence.source_version,
        documents,
    )
    evidence = LegalCorpusProvisioningAuthorityRegistry.get_by_source(
        expected_evidence.source_document_id,
        expected_evidence.source_version,
        authorities,
    )
    assert document is not None and evidence is not None
    assert document.status is LegalDocumentStatus.DRAFT_REVIEW_REQUIRED
    assert document.to_document() == get_institutional_charter_draft().to_document()
    assert evidence.to_document() == expected_evidence.to_document()
    payload, readback_exit = command._unknown_commit_outcome(
        client=client,
        database=database,
        authorization=authorization,
        evidence=expected_evidence,
        attempt=1,
    )
    assert readback_exit == 0
    assert payload is not None
    assert payload["result"] == "DURABLE_ADMISSION_RECOGNIZED"
    assert payload["durability_classification"] == "UNKNOWN_COMMIT_RECONCILED_EXACT"


# ARTIFACT: test_legal_corpus_operator_command_real_mongo.py
# VERSION: v1.1.0-R9B-P7-A2-R1-R1-LEGAL-CORPUS-OPERATOR-COMMAND-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated real-Mongo transaction and durability evidence only
# TENANT POSTURE: UUID-isolated certification databases; no live tenant writes
# FAIL-CLOSED POSTURE: remote/unavailable Mongo and non-atomic outcomes fail
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
