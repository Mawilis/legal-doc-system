"""B4-R9B-P3-P4 isolated real-Mongo certificate for approval evidence.

TITLE: WILSY OS Legal Corpus Approval Registry Real-Mongo Certificate
VERSION: v1.4.0-R1D-B0F-B4-R9B-P4-R5-R4-LEGAL-CORPUS-APPROVAL-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Independently certifies the append-only approval-evidence registry
         against a dedicated writable replica set without claiming approval,
         current trust, promotion, acceptance, or financial execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_corpus_approval_registry_real_mongo.py
COLLABORATION / OWNERSHIP: The governed registry owns immutable evidence
                            persistence only. This certificate owns isolated
                            fixtures and caller-owned transaction observation.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.4.0 repairs the ABSENT preflight lifecycle oracle to distinguish
           a fresh unmaterialized collection from the deployment index plan;
           the five-selector field/value comparison remains independently
           certified.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic Ed25519 material is memory-only and no
                            credentials or private keys are logged or stored.
TENANT BOUNDARY: PLATFORM-only approval evidence in UUID-isolated databases;
                 no tenant or principal authority is created.
AUTHORITY BOUNDARY: A verified proof is persisted as unverified evidence only;
                    registry reads do not re-verify current trust.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Corruption, divergent identity, ambiguous duplicate race,
                     unsafe namespace, and unsupported topology fail closed.
"""
from __future__ import annotations

import ast
import base64
import os
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping, cast
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
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
    AUTHORITY_SCOPE,
    AUTHORIZED_OPERATION,
    SCHEMA,
    LegalCorpusApprovalAuthorization,
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
    APPROVAL_EVIDENCE_FIELDS,
    AUTHORIZATION_STRUCTURAL_FIELDS,
    COLLECTION,
    LegalCorpusApprovalAdmissionState,
    LegalCorpusApprovalPreflightState,
    LegalCorpusApprovalRegistry,
    LegalCorpusApprovalRegistryError,
)


UTC = timezone.utc
NOW = datetime(2026, 9, 19, 12, 0, 0, 123456, tzinfo=UTC)
URI_ENV = "TEST_VENDOR_MONGO_URI"
REPLICA_SET = "wilsyVendorCertRS"
RUN_ID = os.environ.get("WILSY_R9B_P3_P4_RUN_ID", "").strip()
if not RUN_ID or any(ch not in "0123456789abcdef" for ch in RUN_ID.casefold()):
    raise RuntimeError("WILSY_R9B_P3_P4_RUN_ID must be a non-empty hexadecimal value")
DATABASE_PREFIX = f"wilsy_r9b_p3_p4_{RUN_ID}_"
_DATABASE_SEQUENCE = 0

TOP_LEVEL_FIELDS = frozenset(
    {
        "schema", "authorization_id", "issuer_identity", "authority_role",
        "authority_domain", "algorithm", "key_id", "trust_fingerprint",
        "operation", "scope", "approval_evidence", "approval_evidence_fingerprint",
        "issued_at", "expires_at", "nonce", "idempotency_key", "signature_base64url",
    }
)
EVIDENCE_FIELDS = frozenset(
    {
        "approval_evidence_id", "schema_version", "scope", "operation",
        "approval_decision", "approval_authority_source", "approval_authority_mechanism",
        "approval_authority_mechanism_version", "human_authority_representation",
        "approval_signing_mechanism", "approval_signing_mechanism_version",
        "approval_signing_key_id", "approval_signature_reference", "approved_at",
        "effective_from", "idempotency_key", "provenance_reference", "source_document_id",
        "source_agreement_type", "source_version", "source_title", "source_jurisdiction",
        "source_locale", "source_effective_from", "source_status", "source_content_reference",
        "source_content", "source_sha3_512", "source_created_at", "source_supersedes_document_id",
        "approved_document_id", "approved_agreement_type", "approved_version", "approved_title",
        "approved_jurisdiction", "approved_locale", "approved_effective_from", "approved_status",
        "approved_content_reference", "approved_content", "approved_sha3_512", "approved_created_at",
        "approved_supersedes_document_id", "evidence_fingerprint",
    }
)
EXPECTED_INDEXES = {
    "legal_corpus_approval_evidence_id_unique": (
        (("approval_evidence.approval_evidence_id", 1),), True
    ),
    "legal_corpus_approval_authorization_id_unique": ((('authorization_id', 1),), True),
    "legal_corpus_approval_authorization_idempotency_unique": (
        (("scope", 1), ("operation", 1), ("idempotency_key", 1)), True
    ),
    "legal_corpus_approval_evidence_idempotency_unique": (
        (("scope", 1), ("operation", 1), ("approval_evidence.idempotency_key", 1)), True
    ),
    "legal_corpus_approval_target_version_unique": (
        (("scope", 1), ("operation", 1), ("approval_evidence.approved_document_id", 1),
         ("approval_evidence.approved_version", 1)), True
    ),
    "legal_corpus_approval_evidence_fingerprint_lookup": (
        (("approval_evidence.evidence_fingerprint", 1),), False
    ),
    "legal_corpus_approval_source_lookup": (
        (("approval_evidence.source_document_id", 1), ("approval_evidence.source_version", 1)), False
    ),
}


def _private() -> Ed25519PrivateKey:
    """Return deterministic synthetic key material in process memory only."""
    return Ed25519PrivateKey.from_private_bytes(bytes(range(32)))


def _trust_root(private: Ed25519PrivateKey) -> LegalCorpusApprovalTrustRoot:
    public = private.public_key().public_bytes_raw()
    encoded = base64.urlsafe_b64encode(public).rstrip(b"=").decode("ascii")
    key_id = LegalCorpusApprovalTrustedKey.derive_key_id(encoded)
    valid_from = datetime(2026, 9, 19, tzinfo=UTC)
    valid_until = datetime(2026, 9, 20, tzinfo=UTC)
    kwargs: dict[str, Any] = {
        "key_id": key_id, "issuer_identity": APPROVAL_ISSUER_IDENTITY,
        "authority_role": APPROVAL_AUTHORITY_ROLE, "authority_domain": APPROVAL_AUTHORITY_DOMAIN,
        "algorithm": ED25519_ALGORITHM, "public_key_base64url": encoded,
        "valid_from": valid_from, "valid_until": valid_until,
        "status": LegalCorpusApprovalTrustStatus.ACTIVE, "revision": 1,
        "permitted_operations": frozenset({APPROVAL_OPERATION}), "scope": APPROVAL_SCOPE,
        "trust_root_provenance": APPROVAL_TRUST_ROOT_PROVENANCE,
    }
    fingerprint = LegalCorpusApprovalTrustedKey.fingerprint_for(**kwargs)
    return LegalCorpusApprovalTrustRoot((LegalCorpusApprovalTrustedKey(
        **kwargs, trust_fingerprint=fingerprint,
    ),))


def _target(suffix: str) -> LegalDocumentVersion:
    reference = f"wilsy-os://legal/institutional-charter/approved-{suffix}"
    source = corpus.get_institutional_charter_draft()
    return LegalDocumentVersion(
        document_id=source.document_id,
        agreement_type=LegalAgreementType.INSTITUTIONAL_CHARTER,
        version=f"1.0.0-APPROVED-{suffix}", title=source.title,
        jurisdiction=source.jurisdiction, locale=source.locale,
        effective_from=datetime(2026, 10, 1, 0, 0, 0, 654321, tzinfo=UTC),
        status=LegalDocumentStatus.APPROVED, content_reference=reference,
        content=source.content, sha3_512=canonical_document_digest(source.content, reference),
        created_at=datetime(2026, 9, 19, 11, 0, 0, 654321, tzinfo=UTC),
        supersedes_document_id=source.document_id,
    )


def _authorization_uuid(suffix: str) -> str:
    """Derive a valid deterministic UUID for one synthetic test proof."""
    return str(UUID(bytes=uuid5(NAMESPACE_URL, f"wilsy-r9b-p3-p4-authorization:{suffix}").bytes, version=4))


def _authorization_idempotency_uuid(suffix: str) -> str:
    """Derive a distinct valid UUID4 idempotency identity for one proof."""
    return str(UUID(bytes=uuid5(NAMESPACE_URL, f"wilsy-r9b-p3-p4-idempotency:{suffix}").bytes, version=4))


def _proof(
    suffix: str,
    *,
    evidence_id: str | None = None,
    authorization_id: str | None = None,
    authorization_idempotency: str | None = None,
    evidence_idempotency: str | None = None,
    target: LegalDocumentVersion | None = None,
) -> VerifiedLegalCorpusApprovalAuthorization:
    source = corpus.get_institutional_charter_draft()
    approved = target or _target(suffix)
    evidence_values: dict[str, Any] = {
        "approval_evidence_id": evidence_id or f"approval-evidence-{suffix}",
        "schema_version": "v1.0.0", "scope": LegalCorpusApprovalAuthorityScope.PLATFORM,
        "operation": LegalCorpusApprovalOperation.DOCUMENT_APPROVAL,
        "approval_decision": LegalCorpusApprovalDecision.APPROVE,
        "approval_authority_source": LegalCorpusApprovalAuthoritySource.HUMAN_GOVERNED,
        "approval_authority_mechanism": LegalCorpusApprovalAuthorityMechanism.HUMAN_APPROVAL_RECORD,
        "approval_authority_mechanism_version": APPROVAL_AUTHORITY_MECHANISM_VERSION,
        "human_authority_representation": f"synthetic-governance-record-{suffix}",
        "approval_signing_mechanism": LegalCorpusApprovalSigningMechanism.EXTERNAL_GOVERNED_SIGNER,
        "approval_signing_mechanism_version": APPROVAL_SIGNING_MECHANISM_VERSION,
        "approval_signing_key_id": f"synthetic-approval-key-{suffix}",
        "approval_signature_reference": f"synthetic-signature-{suffix}",
        "source_document": source, "approved_document": approved,
        "approved_at": datetime(2026, 9, 19, 11, 30, 0, 123456, tzinfo=UTC),
        "effective_from": approved.effective_from,
        "idempotency_key": evidence_idempotency or f"evidence-idempotency-{suffix}",
        "provenance_reference": f"synthetic-provenance-{suffix}",
    }
    evidence_values["evidence_fingerprint"] = LegalCorpusApprovalAuthorityEvidence.fingerprint_for(**evidence_values)
    evidence = LegalCorpusApprovalAuthorityEvidence(**evidence_values)
    private = _private()
    key = _trust_root(private).all_keys()[0]
    authorization_values: dict[str, Any] = {
        "schema": SCHEMA,
        "authorization_id": authorization_id or _authorization_uuid(suffix),
        "issuer_identity": APPROVAL_ISSUER_IDENTITY, "authority_role": APPROVAL_AUTHORITY_ROLE,
        "authority_domain": APPROVAL_AUTHORITY_DOMAIN, "algorithm": ED25519_ALGORITHM,
        "key_id": key.key_id, "trust_fingerprint": key.trust_fingerprint,
        "operation": LegalCorpusApprovalAuthorizationOperation.DOCUMENT_APPROVAL,
        "scope": LegalCorpusApprovalAuthorizationScope.PLATFORM,
        "approval_evidence": evidence, "issued_at": NOW,
        "expires_at": NOW + timedelta(minutes=30),
        "nonce": base64.urlsafe_b64encode((f"nonce-{suffix}".encode() * 8)[:32]).rstrip(b"=").decode("ascii"),
        "idempotency_key": authorization_idempotency or _authorization_idempotency_uuid(suffix),
        "signature_base64url": base64.urlsafe_b64encode(b"s" * 64).rstrip(b"=").decode("ascii"),
    }
    unsigned = LegalCorpusApprovalAuthorization(**authorization_values)
    signature = base64.urlsafe_b64encode(private.sign(canonical_signed_payload(unsigned))).rstrip(b"=").decode("ascii")
    signed = replace(unsigned, signature_base64url=signature)
    return verify_legal_corpus_approval_authorization(
        signed, _trust_root(private), now=NOW, source_document=source, approved_document=approved,
    )


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="microseconds")


def _document_fields(document: LegalDocumentVersion, prefix: str) -> dict[str, Any]:
    return {
        f"{prefix}_document_id": document.document_id, f"{prefix}_agreement_type": document.agreement_type.value,
        f"{prefix}_version": document.version, f"{prefix}_title": document.title,
        f"{prefix}_jurisdiction": document.jurisdiction, f"{prefix}_locale": document.locale,
        f"{prefix}_effective_from": _iso(document.effective_from), f"{prefix}_status": document.status.value,
        f"{prefix}_content_reference": document.content_reference, f"{prefix}_content": document.content,
        f"{prefix}_sha3_512": document.sha3_512, f"{prefix}_created_at": _iso(document.created_at),
        f"{prefix}_supersedes_document_id": document.supersedes_document_id,
    }


def _independent_document(proof: VerifiedLegalCorpusApprovalAuthorization) -> dict[str, Any]:
    """Independently enumerate the governed 17/44 persistence envelope."""
    authorization = proof.authorization
    evidence = proof.approval_evidence
    payload: dict[str, Any] = {
        "schema": authorization.schema, "authorization_id": authorization.authorization_id,
        "issuer_identity": authorization.issuer_identity, "authority_role": authorization.authority_role,
        "authority_domain": authorization.authority_domain, "algorithm": authorization.algorithm,
        "key_id": authorization.key_id, "trust_fingerprint": authorization.trust_fingerprint,
        "operation": authorization.operation.value, "scope": authorization.scope.value,
        "issued_at": _iso(authorization.issued_at), "expires_at": _iso(authorization.expires_at),
        "nonce": authorization.nonce, "idempotency_key": authorization.idempotency_key,
        "signature_base64url": authorization.signature_base64url,
    }
    nested: dict[str, Any] = {
        "approval_evidence_id": evidence.approval_evidence_id, "schema_version": evidence.schema_version,
        "scope": evidence.scope.value, "operation": evidence.operation.value,
        "approval_decision": evidence.approval_decision.value,
        "approval_authority_source": evidence.approval_authority_source.value,
        "approval_authority_mechanism": evidence.approval_authority_mechanism.value,
        "approval_authority_mechanism_version": evidence.approval_authority_mechanism_version,
        "human_authority_representation": evidence.human_authority_representation,
        "approval_signing_mechanism": evidence.approval_signing_mechanism.value,
        "approval_signing_mechanism_version": evidence.approval_signing_mechanism_version,
        "approval_signing_key_id": evidence.approval_signing_key_id,
        "approval_signature_reference": evidence.approval_signature_reference,
        "approved_at": _iso(evidence.approved_at), "effective_from": _iso(evidence.effective_from),
        "idempotency_key": evidence.idempotency_key, "provenance_reference": evidence.provenance_reference,
    }
    nested.update(_document_fields(evidence.source_document, "source"))
    nested.update(_document_fields(evidence.approved_document, "approved"))
    nested["evidence_fingerprint"] = evidence.evidence_fingerprint
    payload["approval_evidence"] = nested
    payload["approval_evidence_fingerprint"] = evidence.evidence_fingerprint
    assert set(payload) == TOP_LEVEL_FIELDS
    assert set(nested) == EVIDENCE_FIELDS
    return payload


def _lookup_path(document: Mapping[str, Any], path: str) -> Any:
    """Resolve one dotted Mongo selector against an in-memory fixture row."""
    value: Any = document
    for part in path.split("."):
        if not isinstance(value, Mapping):
            return None
        value = value.get(part)
    return value


class _FixtureCollection:
    """Provide read-only registry hydration without opening Mongo."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = deepcopy(rows)

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> dict[str, Any] | None:
        """Return a detached row matching every simple equality selector."""
        del session
        for row in self.rows:
            if all(_lookup_path(row, key) == expected for key, expected in query.items()):
                return deepcopy(row)
        return None


def _assert_verified_fixture(proof: VerifiedLegalCorpusApprovalAuthorization) -> dict[str, Any]:
    """Prove a signed fixture remains verifier-approved and registry-hydratable."""
    assert isinstance(proof, VerifiedLegalCorpusApprovalAuthorization)
    row = _independent_document(proof)
    fingerprint = proof.approval_evidence.evidence_fingerprint
    assert row["approval_evidence"]["evidence_fingerprint"] == fingerprint
    assert row["approval_evidence_fingerprint"] == fingerprint
    hydrated = LegalCorpusApprovalRegistry.get_by_approval_evidence_id(
        proof.approval_evidence.approval_evidence_id,
        _FixtureCollection([row]),
    )
    assert hydrated is not None
    assert hydrated.to_document() == row
    return row


def _split_fixture(prefix: str) -> tuple[
    VerifiedLegalCorpusApprovalAuthorization,
    VerifiedLegalCorpusApprovalAuthorization,
    VerifiedLegalCorpusApprovalAuthorization,
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    """Build valid incoming, evidence-selector, and authorization-selector proofs."""
    incoming = _proof(f"{prefix}incoming")
    row_a_proof = _proof(
        f"{prefix}a",
        evidence_id=incoming.approval_evidence.approval_evidence_id,
    )
    row_b_proof = _proof(
        f"{prefix}b",
        authorization_id=incoming.authorization.authorization_id,
    )
    incoming_row = _assert_verified_fixture(incoming)
    row_a = _assert_verified_fixture(row_a_proof)
    row_b = _assert_verified_fixture(row_b_proof)
    assert row_a["approval_evidence"]["approval_evidence_id"] == incoming_row["approval_evidence"]["approval_evidence_id"]
    assert row_b["authorization_id"] == incoming_row["authorization_id"]
    assert row_a["authorization_id"] != row_b["authorization_id"]
    assert row_a["approval_evidence"]["approval_evidence_id"] != row_b["approval_evidence"]["approval_evidence_id"]
    assert row_a["idempotency_key"] != row_b["idempotency_key"]
    assert row_a["approval_evidence"]["idempotency_key"] != row_b["approval_evidence"]["idempotency_key"]
    assert (
        row_a["scope"],
        row_a["operation"],
        row_a["approval_evidence"]["approved_document_id"],
        row_a["approval_evidence"]["approved_version"],
    ) != (
        row_b["scope"],
        row_b["operation"],
        row_b["approval_evidence"]["approved_document_id"],
        row_b["approval_evidence"]["approved_version"],
    )
    return incoming, row_a_proof, row_b_proof, incoming_row, row_a, row_b


def _safe_db_name(label: str) -> str:
    del label
    global _DATABASE_SEQUENCE
    _DATABASE_SEQUENCE += 1
    name = f"{DATABASE_PREFIX}{_DATABASE_SEQUENCE}"
    assert len(name) <= 63
    assert name.startswith(DATABASE_PREFIX)
    assert name not in {"admin", "config", "local"}
    return name


@contextmanager
def _fresh_database(client: MongoClient[Any], label: str) -> Iterator[Any]:
    name = _safe_db_name(label)
    assert name not in client.list_database_names()
    database = client.get_database(
        name, read_concern=ReadConcern("majority"), write_concern=WriteConcern(w="majority", j=True)
    )
    try:
        yield database
    finally:
        assert name.startswith(DATABASE_PREFIX)
        client.drop_database(name)


@pytest.fixture(scope="module")
def mongo_runtime() -> Iterator[tuple[MongoClient[Any], dict[str, Any]]]:
    """Anchor the sanctioned writable local replica set and clean namespaces."""
    uri = os.environ.get(URI_ENV, "").strip()
    if not uri:
        pytest.fail("R9B_P4_R5_ENVIRONMENT_BLOCKER:TEST_VENDOR_MONGO_URI_MISSING")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=3000, replicaSet=REPLICA_SET, retryWrites=True)
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster", False)) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert client.server_info().get("version")
        assert not [name for name in client.list_database_names() if name.startswith(DATABASE_PREFIX)]
        metadata = {
            "endpoint": "127.0.0.1:27027", "version": client.server_info()["version"],
            "replica_set": hello["setName"], "sessions": "YES", "transactions": "YES",
        }
        yield client, metadata
    except PyMongoError as error:
        pytest.fail(f"P3_P4_ENVIRONMENT_BLOCKER:{type(error).__name__}")
    finally:
        leftovers = [name for name in client.list_database_names() if name.startswith(DATABASE_PREFIX)]
        for name in leftovers:
            assert name.startswith(DATABASE_PREFIX)
            client.drop_database(name)
        assert not [name for name in client.list_database_names() if name.startswith(DATABASE_PREFIX)]
        client.close()


def _collection(database: Any) -> Any:
    return database[COLLECTION]


def _custom_indexes(collection: Any) -> dict[str, tuple[tuple[tuple[str, int], ...], bool]]:
    result: dict[str, tuple[tuple[tuple[str, int], ...], bool]] = {}
    for item in collection.list_indexes():
        if item["name"] != "_id_":
            result[item["name"]] = (tuple(item["key"].items()), bool(item.get("unique", False)))
    return result


class RecordingCollection:
    """Transparent real-collection delegate recording exact session identity."""

    def __init__(self, collection: Any) -> None:
        self.collection = collection
        self.find_queries: list[dict[str, Any]] = []
        self.find_sessions: list[Any] = []
        self.insert_sessions: list[Any] = []

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> Any:
        self.find_queries.append(deepcopy(query))
        self.find_sessions.append(session)
        return self.collection.find_one(query, session=session)

    def insert_one(self, document: dict[str, Any], *, session: Any = None) -> Any:
        self.insert_sessions.append(session)
        return self.collection.insert_one(document, session=session)


class ReadOnlyRealCollection:
    """Expose only real-Mongo reads so preflight cannot mutate by accident."""

    def __init__(self, collection: Any) -> None:
        self.collection = collection
        self.find_queries: list[dict[str, Any]] = []
        self.find_sessions: list[Any] = []

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> Any:
        self.find_queries.append(deepcopy(query))
        self.find_sessions.append(session)
        return self.collection.find_one(query, session=session)


class RaceCollection(RecordingCollection):
    """Real collection delegate that injects real durable race rows once."""

    def __init__(self, collection: Any, race_rows: list[dict[str, Any]]) -> None:
        super().__init__(collection)
        self.race_rows = race_rows
        self.race_inserted = False
        self.real_duplicate_observed = False

    def insert_one(self, document: dict[str, Any], *, session: Any = None) -> Any:
        if not self.race_inserted:
            self.race_inserted = True
            for row in self.race_rows:
                self.collection.insert_one(deepcopy(row))
        try:
            return super().insert_one(document, session=session)
        except DuplicateKeyError:
            self.real_duplicate_observed = True
            raise


def test_real_mongo_index_contract(mongo_runtime: tuple[MongoClient[Any], dict[str, Any]]) -> None:
    client, _ = mongo_runtime
    with _fresh_database(client, "indexes") as database:
        collection = _collection(database)
        assert _custom_indexes(collection) == {}
        LegalCorpusApprovalRegistry.ensure_indexes(collection)
        indexes = _custom_indexes(collection)
        assert len(list(collection.list_indexes())) == 8
        assert len(indexes) == 7
        assert indexes == EXPECTED_INDEXES


def test_admission_does_not_auto_create_custom_indexes(mongo_runtime: tuple[MongoClient[Any], dict[str, Any]]) -> None:
    client, _ = mongo_runtime
    with _fresh_database(client, "no_auto_indexes") as database:
        collection = _collection(database)
        result = LegalCorpusApprovalRegistry.admit_verified_approval(_proof("noidx"), collection)
        assert result.state is LegalCorpusApprovalAdmissionState.CREATED
        assert list(collection.list_indexes())[0]["name"] == "_id_"
        assert len(list(collection.list_indexes())) == 1


def test_real_mongo_preflight_absent_is_complete_and_non_mutating(
    mongo_runtime: tuple[MongoClient[Any], dict[str, Any]],
) -> None:
    """Certify ABSENT across all five selectors without any durable mutation."""
    client, _ = mongo_runtime
    with _fresh_database(client, "preflight_absent") as database:
        collection = _collection(database)
        proof = _proof("preflightabsent")
        before_collection_exists = COLLECTION in database.list_collection_names()
        before_indexes = list(collection.list_indexes()) if before_collection_exists else []
        before_index_definitions = tuple(
            (item["name"], tuple(item["key"].items()), bool(item.get("unique", False)))
            for item in before_indexes
        )
        before_count = collection.count_documents({})
        recording = ReadOnlyRealCollection(collection)
        result = LegalCorpusApprovalRegistry.preflight_verified_approval(proof, recording)
        after_collection_exists = COLLECTION in database.list_collection_names()
        after_indexes = list(collection.list_indexes()) if after_collection_exists else []
        after_index_definitions = tuple(
            (item["name"], tuple(item["key"].items()), bool(item.get("unique", False)))
            for item in after_indexes
        )
        assert result.state is LegalCorpusApprovalPreflightState.ABSENT
        assert result.matched_record is None
        assert result.matched_identities == ()
        assert result.selector_to_row_identity == ()
        assert result.collision_code is None
        assert len(recording.find_queries) == 5
        expected_queries = [
            [("approval_evidence.approval_evidence_id", proof.approval_evidence.approval_evidence_id)],
            [("authorization_id", proof.authorization.authorization_id)],
            [
                ("scope", proof.authorization.scope.value),
                ("operation", proof.authorization.operation.value),
                ("idempotency_key", proof.authorization.idempotency_key),
            ],
            [
                ("scope", proof.authorization.scope.value),
                ("operation", proof.authorization.operation.value),
                ("approval_evidence.idempotency_key", proof.approval_evidence.idempotency_key),
            ],
            [
                ("scope", proof.authorization.scope.value),
                ("operation", proof.authorization.operation.value),
                ("approval_evidence.approved_document_id", proof.approval_evidence.approved_document_id),
                ("approval_evidence.approved_version", proof.approval_evidence.approved_version),
            ],
        ]
        assert [list(query.items()) for query in recording.find_queries] == expected_queries
        assert before_collection_exists is False
        assert after_collection_exists is False
        assert before_count == 0 and collection.count_documents({}) == 0
        assert len(before_indexes) == 0 and len(after_indexes) == 0
        assert before_index_definitions == after_index_definitions


def test_real_mongo_preflight_exact_matches_one_physical_row_without_id(
    mongo_runtime: tuple[MongoClient[Any], dict[str, Any]],
) -> None:
    """Certify EXACT when every selector resolves the same durable row."""
    client, _ = mongo_runtime
    with _fresh_database(client, "preflight_exact") as database:
        collection = _collection(database)
        proof = _proof("preflightexact")
        row = _independent_document(proof)
        collection.insert_one(deepcopy(row))
        stored = collection.find_one({"authorization_id": proof.authorization.authorization_id})
        assert stored is not None and stored.get("_id") is not None
        result = LegalCorpusApprovalRegistry.preflight_verified_approval(proof, collection)
        assert result.state is LegalCorpusApprovalPreflightState.EXACT
        assert result.matched_record is not None
        assert result.matched_record.to_document() == row
        assert "_id" not in result.matched_record.to_document()
        assert len(result.matched_identities) == 1
        assert len(result.selector_to_row_identity) == 5
        assert {identity for _, identity in result.selector_to_row_identity} == set(result.matched_identities)
        assert result.collision_code is None
        assert collection.count_documents({}) == 1


def test_real_mongo_preflight_divergent_identity_is_source_justified(
    mongo_runtime: tuple[MongoClient[Any], dict[str, Any]],
) -> None:
    """Certify a reachable valid identity collision with divergent semantics."""
    client, _ = mongo_runtime
    with _fresh_database(client, "preflight_divergent") as database:
        collection = _collection(database)
        incoming = _proof("preflightdivergentincoming")
        divergent = _proof(
            "preflightdivergentrow",
            evidence_id=incoming.approval_evidence.approval_evidence_id,
        )
        assert divergent.approval_evidence.approved_document.version != incoming.approval_evidence.approved_document.version
        collection.insert_one(_independent_document(divergent))
        result = LegalCorpusApprovalRegistry.preflight_verified_approval(incoming, collection)
        assert result.state is LegalCorpusApprovalPreflightState.DIVERGENT
        assert result.collision_code == "LEGAL_CORPUS_APPROVAL_EVIDENCE_ID_COLLISION"
        assert result.matched_record is not None
        assert result.matched_record.to_document() == _independent_document(divergent)
        assert len(result.selector_to_row_identity) == 1
        assert result.selector_to_row_identity[0][0] == "evidence_id"
        assert collection.count_documents({}) == 1


def test_real_mongo_preflight_split_identity_reports_complete_selector_evidence(
    mongo_runtime: tuple[MongoClient[Any], dict[str, Any]],
) -> None:
    """Certify SPLIT_IDENTITY and forbid implicit repair or backfill."""
    client, _ = mongo_runtime
    with _fresh_database(client, "preflight_split") as database:
        collection = _collection(database)
        incoming, _, _, _, row_a, row_b = _split_fixture("preflightsplit")
        collection.insert_one(row_a)
        collection.insert_one(row_b)
        before_count = collection.count_documents({})
        result = LegalCorpusApprovalRegistry.preflight_verified_approval(incoming, collection)
        assert result.state is LegalCorpusApprovalPreflightState.SPLIT_IDENTITY
        assert result.matched_record is None
        assert result.collision_code is None
        assert len(result.matched_identities) == 2
        assert len(result.selector_to_row_identity) == 2
        assert {selector for selector, _ in result.selector_to_row_identity} == {"evidence_id", "authorization_id"}
        assert len({identity for _, identity in result.selector_to_row_identity}) == 2
        assert collection.count_documents({}) == before_count == 2


def test_real_mongo_preflight_persisted_invalid_is_not_absent(
    mongo_runtime: tuple[MongoClient[Any], dict[str, Any]],
) -> None:
    """Certify reachable corruption fails closed instead of becoming ABSENT."""
    client, _ = mongo_runtime
    with _fresh_database(client, "preflight_invalid") as database:
        collection = _collection(database)
        proof = _proof("preflightinvalid")
        collection.insert_one(_independent_document(proof))
        raw = collection.find_one({"approval_evidence.approval_evidence_id": proof.approval_evidence.approval_evidence_id})
        assert raw is not None
        collection.update_one({"_id": raw["_id"]}, {"$set": {"approval_evidence.source_content": "corrupted"}})
        with pytest.raises(LegalCorpusApprovalRegistryError) as captured:
            LegalCorpusApprovalRegistry.preflight_verified_approval(proof, collection)
        assert captured.value.code == "LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID"
        assert collection.count_documents({}) == 1


@pytest.mark.parametrize("bad", [None, {}, object(), False, "proof"])
def test_only_verified_proof_is_admissible(
    mongo_runtime: tuple[MongoClient[Any], dict[str, Any]], bad: object,
) -> None:
    client, _ = mongo_runtime
    with _fresh_database(client, "proof_gate") as database:
        with pytest.raises(LegalCorpusApprovalRegistryError, match="AUTHORITY_INPUT_INVALID"):
            LegalCorpusApprovalRegistry.admit_verified_approval(cast(Any, bad), _collection(database))
        assert _collection(database).count_documents({}) == 0


def test_first_insert_raw_shape_and_microseconds(mongo_runtime: tuple[MongoClient[Any], dict[str, Any]]) -> None:
    client, _ = mongo_runtime
    with _fresh_database(client, "first_insert") as database:
        collection = _collection(database)
        LegalCorpusApprovalRegistry.ensure_indexes(collection)
        proof = _proof("first")
        result = LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection)
        assert result.state is LegalCorpusApprovalAdmissionState.CREATED
        assert collection.count_documents({}) == 1
        raw = collection.find_one({"approval_evidence.approval_evidence_id": proof.approval_evidence.approval_evidence_id})
        assert raw is not None and "_id" in raw
        assert set(raw) == TOP_LEVEL_FIELDS | {"_id"}
        assert set(raw["approval_evidence"]) == EVIDENCE_FIELDS
        assert len(TOP_LEVEL_FIELDS) == 17 and len(EVIDENCE_FIELDS) == 44
        assert len(TOP_LEVEL_FIELDS) - 1 + len(EVIDENCE_FIELDS) == 60
        assert raw["approval_evidence_fingerprint"] == raw["approval_evidence"]["evidence_fingerprint"]
        assert raw["signature_base64url"] == proof.authorization.signature_base64url
        assert raw["issued_at"].endswith(".123456+00:00")
        assert raw["approval_evidence"]["approved_at"].endswith(".123456+00:00")
        assert "tenant_id" not in raw and "principal_id" not in raw
        assert "approval_evidence_fingerprint" in raw
        assert collection.count_documents({"_id": raw["_id"]}) == 1
        assert _independent_document(proof) == {key: value for key, value in raw.items() if key != "_id"}


def test_lossless_hydration_and_exact_replay(mongo_runtime: tuple[MongoClient[Any], dict[str, Any]]) -> None:
    client, _ = mongo_runtime
    with _fresh_database(client, "replay") as database:
        collection = _collection(database)
        LegalCorpusApprovalRegistry.ensure_indexes(collection)
        proof = _proof("replay")
        first = LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection)
        raw = collection.find_one({"approval_evidence.approval_evidence_id": proof.approval_evidence.approval_evidence_id})
        assert raw is not None and raw["_id"] is not None
        hydrated = LegalCorpusApprovalRegistry.get_by_approval_evidence_id(proof.approval_evidence.approval_evidence_id, collection)
        second = LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection)
        assert first.state is LegalCorpusApprovalAdmissionState.CREATED
        assert second.state is LegalCorpusApprovalAdmissionState.EXACT_REPLAY
        assert hydrated is not None and hydrated.to_document() == _independent_document(proof)
        assert collection.count_documents({}) == 1
        assert "_id" not in second.record.to_document()


@pytest.mark.parametrize("kind", ["evidence", "authorization", "authorization_idempotency", "evidence_idempotency", "target"])
def test_preflight_identity_collisions_fail_closed(
    mongo_runtime: tuple[MongoClient[Any], dict[str, Any]], kind: str,
) -> None:
    client, _ = mongo_runtime
    with _fresh_database(client, f"collision_{kind}") as database:
        collection = _collection(database)
        LegalCorpusApprovalRegistry.ensure_indexes(collection)
        first = _proof(f"{kind}a")
        if kind == "evidence":
            second = _proof("evidenceb", evidence_id=first.approval_evidence.approval_evidence_id)
        elif kind == "authorization":
            second = _proof("authorizationb", authorization_id=first.authorization.authorization_id)
        elif kind == "authorization_idempotency":
            second = _proof("authorizationidemob", authorization_idempotency=first.authorization.idempotency_key)
        elif kind == "evidence_idempotency":
            second = _proof("evidenceidemob", evidence_idempotency=first.approval_evidence.idempotency_key)
        else:
            second = _proof("targetb", target=_target("targeta"))
        LegalCorpusApprovalRegistry.admit_verified_approval(first, collection)
        with pytest.raises(LegalCorpusApprovalRegistryError):
            LegalCorpusApprovalRegistry.admit_verified_approval(second, collection)
        assert collection.count_documents({}) == 1


def test_split_identity_preflight_fails_closed(mongo_runtime: tuple[MongoClient[Any], dict[str, Any]]) -> None:
    client, _ = mongo_runtime
    with _fresh_database(client, "split_preflight") as database:
        collection = _collection(database)
        LegalCorpusApprovalRegistry.ensure_indexes(collection)
        incoming, row_a_proof, row_b_proof, _, row_a, row_b = _split_fixture("split")
        assert _assert_verified_fixture(row_a_proof) == row_a
        assert _assert_verified_fixture(row_b_proof) == row_b
        assert _assert_verified_fixture(incoming) == _independent_document(incoming)
        collection.insert_one(row_a)
        collection.insert_one(row_b)
        row_a_stored = collection.find_one(
            {"approval_evidence.approval_evidence_id": incoming.approval_evidence.approval_evidence_id}
        )
        row_b_stored = collection.find_one({"authorization_id": incoming.authorization.authorization_id})
        assert row_a_stored is not None and row_b_stored is not None
        assert row_a_stored["approval_evidence"]["approval_evidence_id"] == incoming.approval_evidence.approval_evidence_id
        assert row_b_stored["authorization_id"] == incoming.authorization.authorization_id
        assert row_a_stored["_id"] != row_b_stored["_id"]
        with pytest.raises(LegalCorpusApprovalRegistryError, match="IMMUTABILITY_CONFLICT"):
            LegalCorpusApprovalRegistry.admit_verified_approval(incoming, collection)
        assert collection.count_documents({}) == 2


@pytest.mark.parametrize("race", ["exact", "divergent", "split"])
def test_actual_server_duplicatekey_races(
    mongo_runtime: tuple[MongoClient[Any], dict[str, Any]], race: str,
) -> None:
    client, _ = mongo_runtime
    with _fresh_database(client, f"race_{race}") as database:
        collection = _collection(database)
        LegalCorpusApprovalRegistry.ensure_indexes(collection)
        incoming = _proof(f"raceincoming{race}")
        if race == "exact":
            rows = [_independent_document(incoming)]
        elif race == "divergent":
            incoming_auth = incoming.authorization.authorization_id
            rows = [_independent_document(_proof("raceauthcollision", authorization_id=incoming_auth))]
            assert rows[0]["authorization_id"] == incoming_auth
            assert rows[0]["approval_evidence"]["approval_evidence_id"] != incoming.approval_evidence.approval_evidence_id
        else:
            incoming, row_a_proof, row_b_proof, _, row_a, row_b = _split_fixture("racesplit")
            assert _assert_verified_fixture(row_a_proof) == row_a
            assert _assert_verified_fixture(row_b_proof) == row_b
            rows = [row_a, row_b]
        race_collection = RaceCollection(collection, rows)
        if race == "exact":
            result = LegalCorpusApprovalRegistry.admit_verified_approval(incoming, race_collection)
            assert result.state is LegalCorpusApprovalAdmissionState.EXACT_REPLAY
        else:
            with pytest.raises(LegalCorpusApprovalRegistryError) as captured:
                LegalCorpusApprovalRegistry.admit_verified_approval(incoming, race_collection)
            if race == "divergent":
                assert captured.value.code == "LEGAL_CORPUS_APPROVAL_AUTHORIZATION_ID_COLLISION"
            else:
                assert captured.value.code == "LEGAL_CORPUS_APPROVAL_IMMUTABILITY_CONFLICT"
        assert race_collection.real_duplicate_observed is True
        assert collection.count_documents({}) == len(rows)


@pytest.mark.parametrize("mutation", [
    "extra_top", "extra_nested", "missing_top", "missing_nested", "wrong_top_type", "wrong_nested_type",
    "unsupported_schema", "bad_enum", "bad_uuid", "bad_nonce", "bad_signature", "bad_timestamp",
    "noncanonical_timestamp", "missing_top_fp", "missing_nested_fp", "top_fp_changed", "nested_fp_changed",
    "fp_mismatch", "stale_semantic",
])
def test_corrupt_reachable_rows_fail_closed(
    mongo_runtime: tuple[MongoClient[Any], dict[str, Any]], mutation: str,
) -> None:
    client, _ = mongo_runtime
    with _fresh_database(client, f"corrupt_{mutation}") as database:
        collection = _collection(database)
        proof = _proof(f"corrupt{mutation}")
        LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection)
        raw = collection.find_one({"approval_evidence.approval_evidence_id": proof.approval_evidence.approval_evidence_id})
        assert raw is not None
        update: dict[str, Any] = {}
        unset: dict[str, Any] = {}
        if mutation == "extra_top": update["authority_extra"] = True
        elif mutation == "extra_nested": update["approval_evidence.unexpected_nested"] = True
        elif mutation == "missing_top": unset["authorization_id"] = ""
        elif mutation == "missing_nested": unset["approval_evidence.source_title"] = ""
        elif mutation == "wrong_top_type": update["issued_at"] = 123
        elif mutation == "wrong_nested_type": update["approval_evidence.source_content"] = 123
        elif mutation == "unsupported_schema": update["schema"] = "unsupported-schema"
        elif mutation == "bad_enum": update["scope"] = "TENANT"
        elif mutation == "bad_uuid": update["authorization_id"] = "not-a-uuid"
        elif mutation == "bad_nonce": update["nonce"] = "bad nonce"
        elif mutation == "bad_signature": update["signature_base64url"] = "not-base64"
        elif mutation == "bad_timestamp": update["issued_at"] = "2026-09-19T12:00:00+00:00"
        elif mutation == "noncanonical_timestamp": update["approval_evidence.approved_at"] = "2026-09-19T11:30:00.123000+00:00"
        elif mutation == "missing_top_fp": unset["approval_evidence_fingerprint"] = ""
        elif mutation == "missing_nested_fp": unset["approval_evidence.evidence_fingerprint"] = ""
        elif mutation == "top_fp_changed": update["approval_evidence_fingerprint"] = "0" * 128
        elif mutation == "nested_fp_changed": update["approval_evidence.evidence_fingerprint"] = "1" * 128
        elif mutation == "fp_mismatch":
            update["approval_evidence_fingerprint"] = "2" * 128
            update["approval_evidence.evidence_fingerprint"] = "3" * 128
        else:
            update["approval_evidence.source_content"] = "changed-content"
        changes: dict[str, Any] = {}
        if update:
            changes["$set"] = update
        if unset:
            changes["$unset"] = unset
        collection.update_one({"_id": raw["_id"]}, changes)
        reachable = collection.find_one({"approval_evidence.approval_evidence_id": proof.approval_evidence.approval_evidence_id})
        assert reachable is not None
        with pytest.raises(LegalCorpusApprovalRegistryError, match="PERSISTED_INVALID"):
            LegalCorpusApprovalRegistry.get_by_approval_evidence_id(proof.approval_evidence.approval_evidence_id, collection)


def test_session_forwarding_and_caller_transaction_ownership(
    mongo_runtime: tuple[MongoClient[Any], dict[str, Any]],
) -> None:
    client, _ = mongo_runtime
    with _fresh_database(client, "transaction") as database:
        collection = _collection(database)
        LegalCorpusApprovalRegistry.ensure_indexes(collection)
        proof = _proof("transaction")
        with client.start_session() as session:
            recording = RecordingCollection(collection)
            session.start_transaction()
            preflight = LegalCorpusApprovalRegistry.preflight_verified_approval(proof, recording, session=session)
            assert preflight.state is LegalCorpusApprovalPreflightState.ABSENT
            assert len(recording.find_sessions) == 5
            assert all(item is session for item in recording.find_sessions)
            result = LegalCorpusApprovalRegistry.admit_verified_approval(proof, recording, session=session)
            assert session.in_transaction is True
            assert result.state is LegalCorpusApprovalAdmissionState.CREATED
            assert recording.find_sessions and all(item is session for item in recording.find_sessions)
            assert recording.insert_sessions and all(item is session for item in recording.insert_sessions)
            assert recording.collection.count_documents({}, session=session) == 1
            session.abort_transaction()
            assert session.in_transaction is False
        assert collection.count_documents({}) == 0


def test_registry_is_append_only_and_does_not_verify_current_trust_on_read() -> None:
    source = Path("tools/eos/legal_operations/registry/legal_corpus_approval_registry.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert "verify_legal_corpus_approval_authorization" not in names
    assert "MongoClient" not in names
    assert not {"start_transaction", "commit_transaction", "abort_transaction", "with_transaction"} & attributes
    assert not hasattr(LegalCorpusApprovalRegistry, "update")
    assert not hasattr(LegalCorpusApprovalRegistry, "replace")
    assert not hasattr(LegalCorpusApprovalRegistry, "delete")
    assert "tenant_id" not in source and "principal_id" not in source


def test_independent_contract_constants_are_closed() -> None:
    assert AUTHORIZATION_STRUCTURAL_FIELDS == TOP_LEVEL_FIELDS
    assert APPROVAL_EVIDENCE_FIELDS == EVIDENCE_FIELDS
    assert len(TOP_LEVEL_FIELDS) == 17
    assert len(EVIDENCE_FIELDS) == 44
    assert AUTHORITY_SCOPE == "PLATFORM"
    assert AUTHORIZED_OPERATION == "LEGAL_CORPUS_DOCUMENT_APPROVAL"


# ARTIFACT: test_legal_corpus_approval_registry_real_mongo.py
# VERSION: v1.4.0-R1D-B0F-B4-R9B-P4-R5-R4-LEGAL-CORPUS-APPROVAL-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated durable PLATFORM approval-evidence registry only
# TENANT POSTURE: exact per-run UUID namespace; no tenant or principal authority
# FAIL-CLOSED POSTURE: real index, schema, replay, collision, race, corruption,
#                      session, and caller-transaction evidence is required
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
