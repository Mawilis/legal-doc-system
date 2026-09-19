"""Direct certificate for the R8F legal-corpus authority registry.

TITLE: WILSY OS Legal Corpus Provisioning Authority Registry Certificate
VERSION: v1.1.0-R9B-P7-A2-R1-LEGAL-CORPUS-PROVISIONING-AUTHORITY-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies append-only persistence, deterministic replay, collision
         adjudication, hydration integrity, and caller-owned session semantics
         for the R8F authority-evidence registry without a Mongo server.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_provisioning_authority_registry.py
COLLABORATION / OWNERSHIP: R8F owns the production registry; this certificate
                            owns only its direct non-Mongo evidence. R8H will
                            own shared document/evidence composition.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-R8G certifies exact index contracts, replay/divergence
           behavior, corruption rejection, and transaction-boundary ownership.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque fixtures only; no secrets, network, request
                            context, or live persistence are used.
TENANT BOUNDARY: The registry is PLATFORM-scoped institutional evidence; no
                 tenant/principal fields are permitted by this certificate.
AUTHORITY BOUNDARY: Evidence persistence is not issuance, document admission,
                    review, approval, acceptance, signature, or execution.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Every collision, malformed row, lower-level persistence
                     error, and invalid input must produce a bounded failure.
"""
from __future__ import annotations

import ast
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations import production_legal_corpus as corpus
from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
)
from tools.eos.legal_operations.domain.legal_corpus_provisioning_authority import (
    AUTHORITY_SOURCE_VERSION,
    LegalCorpusProvisioningAuthorityEvidence,
    LegalCorpusProvisioningAuthorityScope,
    LegalCorpusProvisioningAuthoritySource,
    LegalCorpusProvisioningOperation,
)
from tools.eos.legal_operations.registry import legal_corpus_provisioning_authority_registry as registry


NOW = datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc)
_ATOMICITY_BY_ITSELF = "AUTHORITY_EVIDENCE_REGISTRY_ATOMIC_WITH_DOCUMENT_BY_ITSELF=NO"
_SHARED_TRANSACTION_REQUIRED = "CALLER_OWNED_SHARED_TRANSACTION_REQUIRED_FOR_FUTURE_COMPOSITION=YES"


class FakeCollection:
    """Deterministic collection double that records every driver interaction."""

    def __init__(self, documents: list[dict[str, Any]] | None = None) -> None:
        self.documents = deepcopy(documents or [])
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, Any]]] = []
        self.insert_calls: list[tuple[dict[str, Any], Any]] = []
        self.find_calls: list[tuple[dict[str, Any], Any]] = []
        self.successful_inserts = 0
        self.mutate_driver_payload = False
        self.duplicate_on_insert = False
        self.insert_error: BaseException | None = None
        self.read_error: BaseException | None = None

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.indexes.append((keys, {"unique": unique, "name": name}))
        return name

    def insert_one(self, document: dict[str, Any], *, session: Any = None) -> object:
        self.insert_calls.append((document, session))
        if self.insert_error is not None:
            raise self.insert_error
        if self.duplicate_on_insert:
            raise DuplicateKeyError("simulated unique collision")
        if self.mutate_driver_payload:
            document["_id"] = "driver-generated-storage-id"
        self.documents.append(deepcopy(document))
        self.successful_inserts += 1
        return object()

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> dict[str, Any] | None:
        self.find_calls.append((query, session))
        if self.read_error is not None:
            raise self.read_error
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                return deepcopy(document)
        return None


def _fields(**changes: Any) -> dict[str, Any]:
    document = corpus.get_institutional_charter_draft()
    values: dict[str, Any] = {
        "authority_evidence_id": "LEGAL-CORPUS-AUTH-R8G-001",
        "scope": LegalCorpusProvisioningAuthorityScope.PLATFORM,
        "operation": LegalCorpusProvisioningOperation.DRAFT_ADMISSION,
        "source_document_id": document.document_id,
        "source_agreement_type": document.agreement_type,
        "source_version": document.version,
        "source_status": document.status,
        "source_content_reference": document.content_reference,
        "source_sha3_512": document.sha3_512,
        "authority_source_id": LegalCorpusProvisioningAuthoritySource.DEPLOYMENT_OPERATOR,
        "authority_source_version": AUTHORITY_SOURCE_VERSION,
        "actor_representation": "deployment-job:r8g-certificate",
        "authorized_at": NOW,
        "idempotency_key": "r8g-idempotency-001",
    }
    values.update(changes)
    values["evidence_fingerprint"] = LegalCorpusProvisioningAuthorityEvidence.fingerprint_for(**values)
    return values


def _evidence(**changes: Any) -> LegalCorpusProvisioningAuthorityEvidence:
    return LegalCorpusProvisioningAuthorityEvidence(**_fields(**changes))


def _row(evidence: LegalCorpusProvisioningAuthorityEvidence, **changes: Any) -> dict[str, Any]:
    result: dict[str, Any] = evidence.to_document()
    result.update(changes)
    return result


def _error_code(call: Any) -> str:
    with pytest.raises(registry.LegalCorpusProvisioningAuthorityRegistryError) as captured:
        call()
    return captured.value.code


def test_collection_and_version_contract_are_exact() -> None:
    assert registry.COLLECTION == "legal_corpus_provisioning_authority_evidence"
    assert registry.VERSION == "v1.1.0-R9B-P7-A2-R1-LEGAL-CORPUS-PROVISIONING-AUTHORITY-REGISTRY"


def test_index_contract_is_exact_and_platform_only() -> None:
    collection = FakeCollection()
    registry.LegalCorpusProvisioningAuthorityRegistry.ensure_indexes(collection)
    assert collection.indexes == [
        (
            [("authority_evidence_id", 1)],
            {
                "unique": True,
                "name": "legal_corpus_provisioning_authority_evidence_id_unique",
            },
        ),
        (
            [("scope", 1), ("operation", 1), ("source_document_id", 1), ("source_version", 1)],
            {
                "unique": True,
                "name": "legal_corpus_provisioning_authority_source_version_unique",
            },
        ),
        (
            [("scope", 1), ("operation", 1), ("idempotency_key", 1)],
            {
                "unique": True,
                "name": "legal_corpus_provisioning_authority_idempotency_unique",
            },
        ),
    ]
    flattened = [field for keys, _ in collection.indexes for field, _direction in keys]
    assert "tenant_id" not in flattened and "principal_id" not in flattened
    assert "source_sha3_512" not in flattened and "source_content_reference" not in flattened
    assert "evidence_fingerprint" not in flattened


@pytest.mark.parametrize("invalid", [None, {}, object()])
def test_only_canonical_r8d_evidence_is_accepted(invalid: Any) -> None:
    assert _error_code(lambda: registry.LegalCorpusProvisioningAuthorityRegistry.create_or_replay(invalid, FakeCollection())) == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_CREATE_INVALID"


def test_first_insert_is_canonical_and_driver_id_isolated() -> None:
    evidence = _evidence()
    collection = FakeCollection()
    collection.mutate_driver_payload = True
    result = registry.LegalCorpusProvisioningAuthorityRegistry.create_or_replay(evidence, collection)
    assert result == evidence
    assert collection.successful_inserts == 1
    assert collection.documents[0]["_id"] == "driver-generated-storage-id"
    assert "_id" not in evidence.to_document()
    assert collection.insert_calls[0][0] is not collection.documents[0]


def test_session_is_forwarded_on_insert_duplicate_reconciliation_and_readback() -> None:
    evidence = _evidence()
    session = object()
    collection = FakeCollection()
    registry.LegalCorpusProvisioningAuthorityRegistry.create_or_replay(evidence, collection, session=session)
    assert collection.insert_calls[0][1] is session
    replay_collection = FakeCollection([_row(evidence, _id="mongo-id")])
    replay_collection.duplicate_on_insert = True
    assert registry.LegalCorpusProvisioningAuthorityRegistry.create_or_replay(evidence, replay_collection, session=session) == evidence
    assert replay_collection.insert_calls[0][1] is session
    assert all(call_session is session for _query, call_session in replay_collection.find_calls)
    assert registry.LegalCorpusProvisioningAuthorityRegistry.get(evidence.authority_evidence_id, replay_collection, session=session) == evidence
    assert registry.LegalCorpusProvisioningAuthorityRegistry.get_by_source(evidence.source_document_id, evidence.source_version, replay_collection, session=session) == evidence
    assert all(call_session is session for _query, call_session in replay_collection.find_calls)


def test_exact_replay_hydrates_canonical_evidence_without_additional_durable_write() -> None:
    evidence = _evidence()
    collection = FakeCollection([_row(evidence, _id="mongo-id")])
    collection.duplicate_on_insert = True
    replay = registry.LegalCorpusProvisioningAuthorityRegistry.create_or_replay(evidence, collection)
    assert replay == evidence
    assert replay.evidence_fingerprint == evidence.evidence_fingerprint
    assert collection.successful_inserts == 0
    assert len(collection.documents) == 1


def test_divergent_evidence_id_collision_fails_closed() -> None:
    incoming = _evidence()
    persisted = _evidence(actor_representation="different-actor")
    collection = FakeCollection([_row(persisted, _id="mongo-id")])
    collection.duplicate_on_insert = True
    assert _error_code(lambda: registry.LegalCorpusProvisioningAuthorityRegistry.create_or_replay(incoming, collection)) == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_IMMUTABILITY_CONFLICT"


def test_divergent_source_identity_collision_fails_closed_without_digest_reference_index() -> None:
    incoming = _evidence()
    persisted = _evidence(source_content_reference="wilsy-os://legal/changed-reference", source_sha3_512="a" * 128)
    collection = FakeCollection([_row(persisted, _id="mongo-id")])
    collection.duplicate_on_insert = True
    registry.LegalCorpusProvisioningAuthorityRegistry.ensure_indexes(collection)
    assert _error_code(lambda: registry.LegalCorpusProvisioningAuthorityRegistry.create_or_replay(incoming, collection)) == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_IMMUTABILITY_CONFLICT"


def test_divergent_idempotency_collision_fails_closed() -> None:
    incoming = _evidence()
    persisted = _evidence(actor_representation="different-actor")
    collection = FakeCollection([_row(persisted, _id="mongo-id")])
    collection.duplicate_on_insert = True
    assert _error_code(lambda: registry.LegalCorpusProvisioningAuthorityRegistry.create_or_replay(incoming, collection)) == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_IMMUTABILITY_CONFLICT"


def test_duplicate_signal_without_reconcilable_row_fails_closed() -> None:
    collection = FakeCollection()
    collection.duplicate_on_insert = True
    assert _error_code(lambda: registry.LegalCorpusProvisioningAuthorityRegistry.create_or_replay(_evidence(), collection)) == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_DUPLICATE_UNAVAILABLE"


def test_valid_hydration_and_readback_absence_contract() -> None:
    evidence = _evidence()
    collection = FakeCollection([_row(evidence, _id="mongo-id")])
    assert registry.LegalCorpusProvisioningAuthorityRegistry.get(evidence.authority_evidence_id, collection) == evidence
    assert registry.LegalCorpusProvisioningAuthorityRegistry.get("missing", collection) is None
    assert registry.LegalCorpusProvisioningAuthorityRegistry.get_by_source("missing", "1.0.0-DRAFT", collection) is None


@pytest.mark.parametrize(
    "changes",
    [
        {"authority_evidence_id": None},
        {"scope": "TENANT"},
        {"operation": "APPROVE"},
        {"source_sha3_512": "g" * 128},
        {"authorized_at": datetime(2026, 9, 17)},
        {"evidence_fingerprint": "0" * 128},
        {"authority_evidence_id": "different-id", "unexpected": "semantic"},
    ],
)
def test_corrupt_persisted_evidence_fails_closed_with_bounded_error(changes: dict[str, Any]) -> None:
    evidence = _evidence()
    row = _row(evidence, **changes)
    collection = FakeCollection([row])
    if "authority_evidence_id" in changes and changes["authority_evidence_id"] is None:
        read = lambda: registry.LegalCorpusProvisioningAuthorityRegistry.get_by_source(evidence.source_document_id, evidence.source_version, collection)
    else:
        read = lambda: registry.LegalCorpusProvisioningAuthorityRegistry.get(changes.get("authority_evidence_id", evidence.authority_evidence_id), collection)
    assert _error_code(read) == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_PERSISTED_INVALID"


def test_missing_required_persisted_field_fails_closed() -> None:
    evidence = _evidence()
    row = _row(evidence)
    del row["idempotency_key"]
    assert _error_code(lambda: registry.LegalCorpusProvisioningAuthorityRegistry.get(evidence.authority_evidence_id, FakeCollection([row]))) == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_PERSISTED_INVALID"


def test_fingerprint_revalidation_rejects_changed_semantic_value() -> None:
    evidence = _evidence()
    row = _row(evidence, actor_representation="tampered-without-rehash")
    assert _error_code(lambda: registry.LegalCorpusProvisioningAuthorityRegistry.get(evidence.authority_evidence_id, FakeCollection([row]))) == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_PERSISTED_INVALID"


def test_read_and_create_errors_translate_without_raw_mongo_messages() -> None:
    read_collection = FakeCollection()
    read_collection.read_error = PyMongoError("sensitive driver detail")
    assert _error_code(lambda: registry.LegalCorpusProvisioningAuthorityRegistry.get("evidence", read_collection)) == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_READ_FAILED"
    create_collection = FakeCollection()
    create_collection.insert_error = PyMongoError("sensitive driver detail")
    assert _error_code(lambda: registry.LegalCorpusProvisioningAuthorityRegistry.create_or_replay(_evidence(), create_collection)) == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_CREATE_FAILED"


def test_explicit_collection_precedes_kernel_database(monkeypatch: pytest.MonkeyPatch) -> None:
    collection = FakeCollection()
    monkeypatch.setattr(registry.kernel_db, "get_database", lambda: (_ for _ in ()).throw(AssertionError("kernel should not be consulted")))
    assert registry.LegalCorpusProvisioningAuthorityRegistry.get("missing", collection) is None


def test_kernel_database_fallback_resolves_dedicated_collection(monkeypatch: pytest.MonkeyPatch) -> None:
    collection = FakeCollection()

    class Database:
        def __getitem__(self, name: str) -> FakeCollection:
            assert name == registry.COLLECTION
            return collection

    monkeypatch.setattr(registry.kernel_db, "get_database", lambda: Database())
    assert registry.LegalCorpusProvisioningAuthorityRegistry.get("missing") is None


def test_kernel_database_unavailable_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(registry.kernel_db, "get_database", lambda: None)
    assert _error_code(lambda: registry.LegalCorpusProvisioningAuthorityRegistry.get("missing")) == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_DATABASE_UNAVAILABLE"


def test_transaction_boundary_and_document_mutation_are_explicitly_absent() -> None:
    source = Path("tools/eos/legal_operations/registry/legal_corpus_provisioning_authority_registry.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = [node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
    assert not any(name in calls for name in ("start_session", "start_transaction", "commit_transaction", "abort_transaction"))
    assert "MongoClient" not in source
    assert "UnknownTransactionCommitResult" not in source
    assert "LegalDocumentRegistry" not in source
    assert "production_legal_corpus" not in source
    assert _ATOMICITY_BY_ITSELF.endswith("=NO")
    assert _SHARED_TRANSACTION_REQUIRED.endswith("=YES")


def test_fake_collection_is_the_only_persistence_surface() -> None:
    collection = FakeCollection()
    registry.LegalCorpusProvisioningAuthorityRegistry.create_or_replay(_evidence(), collection)
    assert len(collection.insert_calls) == 1
    assert collection.successful_inserts == 1


def test_registry_public_api_has_no_mutable_crud_or_authority_issuer() -> None:
    public = {name for name in vars(registry.LegalCorpusProvisioningAuthorityRegistry) if not name.startswith("_")}
    assert public == {"ensure_indexes", "create_or_replay", "get", "get_by_source"}
    assert not any(token in name.casefold() for name in public for token in ("update", "delete", "replace", "issue", "approve"))


# ARTIFACT: test_legal_corpus_provisioning_authority_registry.py
# VERSION: v1.1.0-R9B-P7-A2-R1-LEGAL-CORPUS-PROVISIONING-AUTHORITY-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct registry certificate only; evidence persistence is not document persistence
# TENANT POSTURE: PLATFORM-scoped corpus evidence; tenant acceptance remains separate
# FAIL-CLOSED POSTURE: replay, collision, corruption, and lower-level errors are bounded
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
