"""R9B-P7-A3 real-Mongo certificate for the generalized approval command.

TITLE: WILSY OS Reviewed Successor Approval Command Real-Mongo Certificate
VERSION: v1.0.0-R1D-B0F-R9B-P7-A3-REVIEWED-SUCCESSOR-APPROVAL-COMMAND-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the five reviewed-successor command artifacts through the
         actual external-signature verifier, approval operator transaction,
         durable readback, and one exact replay against isolated local Mongo.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_corpus_approval_operator_command_real_mongo.py
COLLABORATION / OWNERSHIP: The command adapter owns phase boundaries; the
                            existing approval operator, service, and registries
                            own transaction and persistence semantics. This
                            certificate owns only synthetic test evidence and
                            one run-scoped database.
CERTIFICATION / UPDATE DATE: 2026-09-20
CHANGELOG: v1.0.0 certifies exactly five reviewed 1.1.0-DRAFT successors,
           synthetic Ed25519 verification, committed creation, exact replay,
           source immutability, and bounded selector rejection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Loopback Mongo only. Synthetic private key bytes
                            exist only in memory; no production key, URI
                            credential, signature material, or secret is logged.
TENANT BOUNDARY: PLATFORM corpus only; no tenant or principal authority.
AUTHORITY BOUNDARY: Certification evidence only; no production approval,
                    review, acceptance, signature, or key admission occurs.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
RUNTIME BOUNDARY: This test is the only authorized real-Mongo execution for
                  this gate and drops only its own database.
FAIL-CLOSED POSTURE: Non-loopback, wrong-version, non-primary, unavailable,
                     tampered, split, or divergent outcomes fail.
"""
from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timedelta, timezone
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

import tools.eos.legal_operations.legal_corpus_approval_operator_command as command
from tools.eos.legal_operations.domain.legal_acceptance import canonical_document_digest
from tools.eos.legal_operations.domain.legal_corpus_approval_authorization import (
    canonical_signed_payload,
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
from tools.eos.legal_operations.production_legal_corpus import (
    PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS,
)
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
    LegalCorpusApprovalOperatorResultState,
)


DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
EXPECTED_MONGO_VERSION = "7.0.37"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
NOW = datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc)
APPROVED_AT = NOW + timedelta(hours=1)
EFFECTIVE_FROM = NOW + timedelta(days=1)
TEST_SEED = bytes(range(32))


def _assert_loopback_uri(uri: str) -> None:
    """Reject remote, SRV, credential-bearing, or uncontrolled Mongo targets."""
    parsed = urlsplit(uri)
    if parsed.scheme != "mongodb" or not parsed.netloc or "@" in parsed.netloc:
        raise AssertionError("R9B_P7_A3_LOOPBACK_MONGO_REQUIRED")
    authority = parsed.netloc.rsplit("@", 1)[-1]
    hosts = []
    for item in authority.split(","):
        host = item.rsplit(":", 1)[0].strip("[]") if ":" in item else item
        hosts.append(host.lower())
    if not hosts or any(host not in LOOPBACK_HOSTS for host in hosts):
        raise AssertionError("R9B_P7_A3_REMOTE_MONGO_FORBIDDEN")


@pytest.fixture()
def isolated_mongo_database() -> Iterator[tuple[MongoClient[Any], Any]]:
    """Yield one majority-configured run database and drop only that database."""
    uri = os.environ.get("TEST_VENDOR_MONGO_URI", DEFAULT_URI).strip()
    _assert_loopback_uri(uri)
    client = MongoClient(uri, serverSelectionTimeoutMS=3000, replicaSet=EXPECTED_REPLICA_SET, retryWrites=True)
    database_name: str | None = None
    try:
        try:
            hello = client.admin.command("hello")
            version = client.server_info().get("version")
        except PyMongoError as error:
            raise AssertionError(f"R9B_P7_A3_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}") from error
        assert version == EXPECTED_MONGO_VERSION
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster", False)) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        database_name = "r9b_p7_a3_command_" + uuid4().hex
        database = client.get_database(
            database_name,
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        yield client, database
    finally:
        if database_name is not None:
            client.drop_database(database_name)
            assert database_name not in client.list_database_names()
        client.close()


def _synthetic_trust_root() -> tuple[Ed25519PrivateKey, LegalCorpusApprovalTrustRoot]:
    """Build deterministic TEST-only approval trust material in memory."""
    private_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    public_key = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    public_text = base64.urlsafe_b64encode(public_key).rstrip(b"=").decode("ascii")
    values: dict[str, Any] = {
        "key_id": LegalCorpusApprovalTrustedKey.derive_key_id(public_text),
        "issuer_identity": APPROVAL_ISSUER_IDENTITY,
        "authority_role": APPROVAL_AUTHORITY_ROLE,
        "authority_domain": APPROVAL_AUTHORITY_DOMAIN,
        "algorithm": ED25519_ALGORITHM,
        "public_key_base64url": public_text,
        "valid_from": NOW - timedelta(days=1),
        "valid_until": NOW + timedelta(days=1),
        "status": LegalCorpusApprovalTrustStatus.ACTIVE,
        "revision": 1,
        "permitted_operations": frozenset({APPROVAL_OPERATION}),
        "scope": APPROVAL_SCOPE,
        "trust_root_provenance": APPROVAL_TRUST_ROOT_PROVENANCE,
    }
    values["trust_fingerprint"] = LegalCorpusApprovalTrustedKey.fingerprint_for(**values)
    return private_key, LegalCorpusApprovalTrustRoot(trusted_keys=(LegalCorpusApprovalTrustedKey(**values),))


def _prepare_indexes_and_sources(database: Any) -> None:
    """Create test-owned indexes and insert only the five canonical drafts."""
    documents = database[DOCUMENT_COLLECTION]
    approvals = database[APPROVAL_COLLECTION]
    LegalDocumentRegistry.ensure_indexes(documents)
    LegalCorpusApprovalRegistry.ensure_indexes(approvals)
    for source in PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS:
        documents.insert_one(source.to_document())


def test_reviewed_successors_commit_replay_and_reject_tampering(
    isolated_mongo_database: tuple[MongoClient[Any], Any],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Certify all five real commits, one exact replay, and pre-write rejection."""
    client, database = isolated_mongo_database
    private_key, trust_root = _synthetic_trust_root()
    monkeypatch.setattr(command, "PRODUCTION_APPROVAL_TRUST_ROOT", trust_root)
    monkeypatch.setattr(command, "APPROVAL_TRUSTED_KEY_ID", trust_root.all_keys()[0].key_id)
    monkeypatch.setattr(command, "_utc_now", lambda: NOW)
    operator = LegalCorpusApprovalOperator(client=client, database=database)
    monkeypatch.setattr(command, "LegalCorpusApprovalOperator", lambda: operator)
    _prepare_indexes_and_sources(database)
    source_before = {
        source.document_id: database[DOCUMENT_COLLECTION].find_one(
            {"document_id": source.document_id, "version": source.version}
        )
        for source in PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS
    }

    for source in PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS:
        artifact_directory = tmp_path / source.document_id.lower()
        unsigned, payload = command.prepare_reviewed_successor(
            document_id=source.document_id,
            output_directory=artifact_directory,
            approved_at=APPROVED_AT.isoformat(),
            effective_from=EFFECTIVE_FROM.isoformat(),
            human_authority_representation="test-governance:r9b-p7-a3",
            provenance_reference="test://r9b-p7-a3",
        )
        assert payload.read_bytes() == canonical_signed_payload(
            command._authorization_from_payload(json.loads(unsigned.read_text(encoding="utf-8")))
        )
        signature = artifact_directory / "synthetic-signature.bin"
        signature.write_bytes(private_key.sign(payload.read_bytes()))
        signed = artifact_directory / "signed.json"
        command.finalize_authorization(unsigned, signature, signed)
        result = command.execute_authorization(signed)
        assert result is LegalCorpusApprovalOperatorResultState.COMMITTED_CREATED

        authorization = command._authorization_from_payload(json.loads(signed.read_text(encoding="utf-8")))
        evidence = authorization.approval_evidence
        target = evidence.approved_document
        assert evidence.source_document == source
        assert target.document_id == source.document_id
        assert target.version == "1.1.0-APPROVED"
        assert target.content == source.content
        assert target.content_reference == source.content_reference.replace("1.1.0-draft", "1.1.0-approved")
        assert target.sha3_512 == canonical_document_digest(source.content, target.content_reference)
        assert database[DOCUMENT_COLLECTION].count_documents({"document_id": source.document_id, "version": source.version}) == 1
        assert database[DOCUMENT_COLLECTION].count_documents({"document_id": source.document_id, "version": target.version}) == 1
        assert database[APPROVAL_COLLECTION].count_documents({"authorization_id": authorization.authorization_id}) == 1
        assert database[DOCUMENT_COLLECTION].find_one({"document_id": source.document_id, "version": source.version}) == source_before[source.document_id]

    replay_source = PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS[0]
    replay_signed = tmp_path / replay_source.document_id.lower() / "signed.json"
    replay = command.execute_authorization(replay_signed)
    assert replay is LegalCorpusApprovalOperatorResultState.COMMITTED_EXACT_REPLAY
    replay_authorization = command._authorization_from_payload(json.loads(replay_signed.read_text(encoding="utf-8")))
    assert database[DOCUMENT_COLLECTION].count_documents({"document_id": replay_source.document_id, "version": "1.1.0-APPROVED"}) == 1
    assert database[APPROVAL_COLLECTION].count_documents({"authorization_id": replay_authorization.authorization_id}) == 1

    for rejected_id in ("WILSY-OS-INSTITUTIONAL-CHARTER", "WILSY-OS-USER-TERMS-LEGACY", "UNKNOWN-DOCUMENT"):
        with pytest.raises(command.LegalCorpusApprovalOperatorCommandError):
            command.prepare_reviewed_successor(
                document_id=rejected_id,
                output_directory=tmp_path / "rejected" / rejected_id.lower(),
                approved_at=APPROVED_AT.isoformat(),
                effective_from=EFFECTIVE_FROM.isoformat(),
                human_authority_representation="test-governance:r9b-p7-a3",
                provenance_reference="test://r9b-p7-a3",
            )

    tampered = tmp_path / "tampered.json"
    original_signed = replay_signed.read_text(encoding="utf-8")
    tampered.write_text(original_signed.replace("1.1.0-APPROVED", "1.1.0-TAMPERED", 1), encoding="utf-8")
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError):
        command.execute_authorization(tampered)
    assert database[APPROVAL_COLLECTION].count_documents({}) == 5
    assert database[DOCUMENT_COLLECTION].count_documents({"version": "1.1.0-APPROVED"}) == 5


# ARTIFACT: test_legal_corpus_approval_operator_command_real_mongo.py
# VERSION: v1.0.0-R1D-B0F-R9B-P7-A3-REVIEWED-SUCCESSOR-APPROVAL-COMMAND-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated real-Mongo evidence only; no production approval
# TENANT POSTURE: run-scoped PLATFORM database; no tenant/principal authority
# FAIL-CLOSED POSTURE: topology, source, target, signature, replay, and tamper checks reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
