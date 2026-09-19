"""Direct certificate for the signed legal-corpus approval registry.

TITLE: WILSY OS Legal Corpus Approval Registry Direct Certificate
VERSION: v1.5.0-R1D-B0F-R9B-P4-R2-LEGAL-CORPUS-APPROVAL-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Independently certifies the lossless normalized approval envelope,
         closed hydration, exact replay, collision law, and caller-owned
         transaction boundary without a Mongo server.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_approval_registry.py
COLLABORATION / OWNERSHIP: Certifies the P3-P1 registry only. The future
                            approval service owns document coordination,
                            transactions, retries, and commit truth.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.5.0-R1D-B0F-R9B-P4-R2-LEGAL-CORPUS-APPROVAL-REGISTRY-CERT
           independently certifies the non-mutating complete five-selector
           preflight, immutable identity evidence, and shared admission
           reconciliation core.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic Ed25519 material is memory-only test
                            material; no key is written, printed, or admitted.
TENANT BOUNDARY: PLATFORM approval only; no tenant/principal authority.
AUTHORITY BOUNDARY: Passing tests certify persistence behavior, not approval,
                    human identity, current trust, acceptance, or execution.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Invalid proof, corruption, divergence, split identity,
                     duplicate ambiguity, and lower-level errors reject.
"""
from __future__ import annotations

import ast
import base64
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, cast

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pymongo.errors import DuplicateKeyError, PyMongoError

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
from tools.eos.legal_operations.registry import legal_corpus_approval_registry as registry


UTC = timezone.utc
NOW = datetime(2026, 9, 19, 12, 0, 0, 123456, tzinfo=UTC)
SOURCE = corpus.get_institutional_charter_draft()

_EXPECTED_TOP_LEVEL_FIELDS = {
    "schema", "authorization_id", "issuer_identity", "authority_role",
    "authority_domain", "algorithm", "key_id", "trust_fingerprint",
    "operation", "scope", "approval_evidence", "approval_evidence_fingerprint",
    "issued_at", "expires_at", "nonce", "idempotency_key", "signature_base64url",
}
_EXPECTED_EVIDENCE_FIELDS = {
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


def _target(version: str = "1.0.0-APPROVED", effective_from: datetime = datetime(2026, 10, 1, tzinfo=UTC)) -> LegalDocumentVersion:
    reference = f"wilsy-os://legal/institutional-charter/{version.casefold()}"
    return LegalDocumentVersion(
        document_id=SOURCE.document_id,
        agreement_type=LegalAgreementType.INSTITUTIONAL_CHARTER,
        version=version,
        title=SOURCE.title,
        jurisdiction=SOURCE.jurisdiction,
        locale=SOURCE.locale,
        effective_from=effective_from,
        status=LegalDocumentStatus.APPROVED,
        content_reference=reference,
        content=SOURCE.content,
        sha3_512=canonical_document_digest(SOURCE.content, reference),
        created_at=datetime(2026, 9, 19, 11, 0, 0, 654321, tzinfo=UTC),
        supersedes_document_id=SOURCE.document_id,
    )


def _evidence(*, source_document: LegalDocumentVersion = SOURCE, approved_document: LegalDocumentVersion | None = None, **changes: object) -> LegalCorpusApprovalAuthorityEvidence:
    approved = approved_document or _target()
    values: dict[str, object] = {
        "approval_evidence_id": "approval-evidence-001",
        "schema_version": "v1.0.0",
        "scope": LegalCorpusApprovalAuthorityScope.PLATFORM,
        "operation": LegalCorpusApprovalOperation.DOCUMENT_APPROVAL,
        "approval_decision": LegalCorpusApprovalDecision.APPROVE,
        "approval_authority_source": LegalCorpusApprovalAuthoritySource.HUMAN_GOVERNED,
        "approval_authority_mechanism": LegalCorpusApprovalAuthorityMechanism.HUMAN_APPROVAL_RECORD,
        "approval_authority_mechanism_version": APPROVAL_AUTHORITY_MECHANISM_VERSION,
        "human_authority_representation": "human-governance-record-001",
        "approval_signing_mechanism": LegalCorpusApprovalSigningMechanism.EXTERNAL_GOVERNED_SIGNER,
        "approval_signing_mechanism_version": APPROVAL_SIGNING_MECHANISM_VERSION,
        "approval_signing_key_id": "approval-key-reference-001",
        "approval_signature_reference": "approval-signature-reference-001",
        "source_document": source_document,
        "approved_document": approved,
        "approved_at": datetime(2026, 9, 19, 11, 30, 0, 123456, tzinfo=UTC),
        "effective_from": approved.effective_from,
        "idempotency_key": "approval-idempotency-001",
        "provenance_reference": "governance-record-001",
    }
    values.update(changes)
    values["evidence_fingerprint"] = LegalCorpusApprovalAuthorityEvidence.fingerprint_for(**cast(Any, values))
    return LegalCorpusApprovalAuthorityEvidence(**cast(Any, values))


def _private() -> Ed25519PrivateKey:
    """Return deterministic memory-only test material."""
    return Ed25519PrivateKey.from_private_bytes(bytes(range(32)))


def _trust_root(private: Ed25519PrivateKey) -> LegalCorpusApprovalTrustRoot:
    public = private.public_key().public_bytes_raw()
    encoded = base64.urlsafe_b64encode(public).rstrip(b"=").decode("ascii")
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
    return LegalCorpusApprovalTrustRoot((LegalCorpusApprovalTrustedKey(
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
    ),))


def _proof(*, evidence_changes: dict[str, object] | None = None, authorization_changes: dict[str, object] | None = None, approved_document: LegalDocumentVersion | None = None) -> VerifiedLegalCorpusApprovalAuthorization:
    private = _private()
    evidence = _evidence(approved_document=approved_document, **cast(Any, evidence_changes or {}))
    key = _trust_root(private).all_keys()[0]
    values: dict[str, object] = {
        "authorization_id": "123e4567-e89b-42d3-a456-426614174000",
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
        "idempotency_key": "223e4567-e89b-42d3-a456-426614174001",
        "signature_base64url": base64.urlsafe_b64encode(b"s" * 64).rstrip(b"=").decode("ascii"),
        "schema": SCHEMA,
    }
    values.update(authorization_changes or {})
    unsigned = LegalCorpusApprovalAuthorization(**cast(Any, values))
    signature = base64.urlsafe_b64encode(private.sign(canonical_signed_payload(unsigned))).rstrip(b"=").decode("ascii")
    signed = replace(unsigned, signature_base64url=signature)
    return verify_legal_corpus_approval_authorization(
        signed,
        _trust_root(private),
        now=NOW,
        source_document=SOURCE,
        approved_document=approved_document or _target(),
    )


def _get_path(row: dict[str, Any], path: str) -> Any:
    value: Any = row
    for component in path.split("."):
        if not isinstance(value, dict) or component not in value:
            return None
        value = value[component]
    return value


class FakeCollection:
    """Strict fake collection recording indexes, filters, sessions, and writes."""

    def __init__(self, documents: list[dict[str, Any]] | None = None) -> None:
        self.documents = deepcopy(documents or [])
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, Any]]] = []
        self.find_calls: list[tuple[dict[str, Any], Any]] = []
        self.insert_calls: list[tuple[dict[str, Any], Any]] = []
        self.pre_insert_snapshots: list[dict[str, Any]] = []
        self.successful_inserts = 0
        self.duplicate_on_insert = False
        self.duplicate_seed: list[dict[str, Any]] = []
        self.mutate_driver_payload = False
        self.insert_error: BaseException | None = None
        self.read_error: BaseException | None = None
        self.duplicate_observer: Callable[[Any], None] | None = None

    def create_index(self, keys: list[tuple[str, int]], *, unique: bool, name: str) -> str:
        self.indexes.append((keys, {"unique": unique, "name": name}))
        return name

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> dict[str, Any] | None:
        self.find_calls.append((query, session))
        if self.read_error is not None:
            raise self.read_error
        for document in self.documents:
            if all(_get_path(document, key) == value for key, value in query.items()):
                return deepcopy(document)
        return None

    def insert_one(self, document: dict[str, Any], *, session: Any = None) -> object:
        self.insert_calls.append((document, session))
        self.pre_insert_snapshots.append(deepcopy(document))
        if self.insert_error is not None:
            raise self.insert_error
        if self.duplicate_on_insert:
            self.documents.extend(deepcopy(self.duplicate_seed))
            if self.duplicate_observer is not None:
                self.duplicate_observer(self)
            raise DuplicateKeyError("simulated unique collision")
        if self.mutate_driver_payload:
            document["_id"] = "driver-generated-storage-id"
        self.documents.append(deepcopy(document))
        self.successful_inserts += 1
        return object()


def _stored(proof: VerifiedLegalCorpusApprovalAuthorization) -> dict[str, Any]:
    payload = deepcopy(proof.authorization.to_document())
    payload["approval_evidence_fingerprint"] = proof.approval_evidence.evidence_fingerprint
    return payload


def _error(call: Callable[[], Any]) -> str:
    with pytest.raises(registry.LegalCorpusApprovalRegistryError) as captured:
        call()
    return captured.value.code


def test_contract_is_closed_and_lossless() -> None:
    assert registry.VERSION == "v1.1.0-R1D-B0F-B4-R9B-P4-R2-LEGAL-CORPUS-APPROVAL-REGISTRY"
    assert registry.COLLECTION == "legal_corpus_approval_evidence"
    assert registry.AUTHORIZATION_STRUCTURAL_FIELDS == _EXPECTED_TOP_LEVEL_FIELDS
    assert registry.APPROVAL_EVIDENCE_FIELDS == _EXPECTED_EVIDENCE_FIELDS
    assert len(_EXPECTED_TOP_LEVEL_FIELDS) == 17
    assert len(_EXPECTED_EVIDENCE_FIELDS) == 44
    assert len(_EXPECTED_TOP_LEVEL_FIELDS) + len(_EXPECTED_EVIDENCE_FIELDS) - 1 == 60


def test_index_plan_is_exact() -> None:
    collection = FakeCollection()
    registry.LegalCorpusApprovalRegistry.ensure_indexes(collection)
    assert collection.indexes == [
        ([('approval_evidence.approval_evidence_id', 1)], {'unique': True, 'name': 'legal_corpus_approval_evidence_id_unique'}),
        ([('authorization_id', 1)], {'unique': True, 'name': 'legal_corpus_approval_authorization_id_unique'}),
        ([('scope', 1), ('operation', 1), ('idempotency_key', 1)], {'unique': True, 'name': 'legal_corpus_approval_authorization_idempotency_unique'}),
        ([('scope', 1), ('operation', 1), ('approval_evidence.idempotency_key', 1)], {'unique': True, 'name': 'legal_corpus_approval_evidence_idempotency_unique'}),
        ([('scope', 1), ('operation', 1), ('approval_evidence.approved_document_id', 1), ('approval_evidence.approved_version', 1)], {'unique': True, 'name': 'legal_corpus_approval_target_version_unique'}),
        ([('approval_evidence.evidence_fingerprint', 1)], {'unique': False, 'name': 'legal_corpus_approval_evidence_fingerprint_lookup'}),
        ([('approval_evidence.source_document_id', 1), ('approval_evidence.source_version', 1)], {'unique': False, 'name': 'legal_corpus_approval_source_lookup'}),
    ]


@pytest.mark.parametrize("bad", [None, {}, object(), False, "proof"])
def test_only_verified_proof_is_admissible(bad: object) -> None:
    assert _error(lambda: registry.LegalCorpusApprovalRegistry.admit_verified_approval(cast(Any, bad))) == "LEGAL_CORPUS_APPROVAL_AUTHORITY_INPUT_INVALID"


def test_insert_preserves_full_shape_and_detaches_driver_metadata() -> None:
    proof = _proof()
    collection = FakeCollection()
    collection.mutate_driver_payload = True
    result = registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection, session="s")
    assert result.state is registry.LegalCorpusApprovalAdmissionState.CREATED
    assert result.record.to_document() == _stored(proof)
    stored = collection.documents[0]
    assert set(stored) == _EXPECTED_TOP_LEVEL_FIELDS | {"_id"}
    assert set(stored["approval_evidence"]) == _EXPECTED_EVIDENCE_FIELDS
    assert stored["approval_evidence_fingerprint"] == stored["approval_evidence"]["evidence_fingerprint"]
    assert stored["signature_base64url"] == proof.authorization.signature_base64url
    assert stored["issued_at"].endswith(".123456+00:00")
    assert "tenant_id" not in stored and "principal_id" not in stored
    assert "_id" not in result.record.to_document()
    stored["approval_evidence"]["source_content"] = "tampered-driver-copy"
    assert result.record.authorization.approval_evidence.source_document.content != "tampered-driver-copy"


def test_exact_replay_is_non_authoritative_and_writes_once() -> None:
    proof = _proof()
    collection = FakeCollection([_stored(proof)])
    first = registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection)
    second = registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection)
    assert first.state is registry.LegalCorpusApprovalAdmissionState.EXACT_REPLAY
    assert second.state is registry.LegalCorpusApprovalAdmissionState.EXACT_REPLAY
    assert collection.successful_inserts == 0
    assert not isinstance(second.record, VerifiedLegalCorpusApprovalAuthorization)
    assert second.record.to_document() == _stored(proof)


def test_preflight_absent_reads_all_five_and_never_writes() -> None:
    proof = _proof()
    collection = FakeCollection()
    result = registry.LegalCorpusApprovalRegistry.preflight_verified_approval(
        proof, collection, session="preflight-session"
    )
    assert result.state is registry.LegalCorpusApprovalPreflightState.ABSENT
    assert result.matched_record is None
    assert result.matched_identities == ()
    assert result.selector_to_row_identity == ()
    assert result.collision_code is None
    assert len(collection.find_calls) == 5
    assert collection.insert_calls == []
    assert collection.indexes == []
    assert all(call_session == "preflight-session" for _, call_session in collection.find_calls)


def test_preflight_exact_returns_complete_immutable_identity_evidence() -> None:
    proof = _proof()
    collection = FakeCollection([dict(_stored(proof), _id="approval-row-001")])
    result = registry.LegalCorpusApprovalRegistry.preflight_verified_approval(proof, collection)
    assert result.state is registry.LegalCorpusApprovalPreflightState.EXACT
    assert result.matched_record is not None
    assert result.matched_record.to_document() == _stored(proof)
    assert result.matched_identities == ("mongo:approval-row-001",)
    assert tuple(selector for selector, _ in result.selector_to_row_identity) == (
        "evidence_id", "authorization_id", "authorization_idempotency",
        "evidence_idempotency", "target_version",
    )
    assert all(identity == "mongo:approval-row-001" for _, identity in result.selector_to_row_identity)
    assert result.collision_code is None
    with pytest.raises(FrozenInstanceError):
        result.state = registry.LegalCorpusApprovalPreflightState.ABSENT  # type: ignore[misc]
    with pytest.raises(AttributeError):
        result.matched_identities.append("x")  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "alternate_proof",
    [
        lambda: _proof(authorization_changes={"authorization_id": "223e4567-e89b-42d3-a456-426614174010"}),
        lambda: _proof(authorization_changes={"idempotency_key": "323e4567-e89b-42d3-a456-426614174002"}),
        lambda: _proof(evidence_changes={"idempotency_key": "evidence-idempotency-divergent"}),
        lambda: _proof(approved_document=_target(version="1.0.0-OTHER")),
    ],
)
def test_preflight_partial_identity_is_divergent_and_fail_closed(
    alternate_proof: Callable[[], VerifiedLegalCorpusApprovalAuthorization],
) -> None:
    proof = _proof()
    collection = FakeCollection([_stored(alternate_proof())])
    result = registry.LegalCorpusApprovalRegistry.preflight_verified_approval(proof, collection)
    assert result.state is registry.LegalCorpusApprovalPreflightState.DIVERGENT
    assert result.matched_record is not None
    assert result.collision_code in {
        "LEGAL_CORPUS_APPROVAL_AUTHORIZATION_ID_COLLISION",
        "LEGAL_CORPUS_APPROVAL_IDEMPOTENCY_CONFLICT",
        "LEGAL_CORPUS_APPROVAL_IMMUTABILITY_CONFLICT",
        "LEGAL_CORPUS_APPROVAL_EVIDENCE_ID_COLLISION",
    }
    assert collection.insert_calls == []


def test_preflight_split_identity_reports_selector_rows_without_repair() -> None:
    proof = _proof()
    row_a = _stored(_proof(authorization_changes={"authorization_id": "223e4567-e89b-42d3-a456-426614174010"}))
    row_b = _stored(_proof(evidence_changes={"approval_evidence_id": "approval-evidence-002"}))
    row_a["_id"] = "preflight-row-a"
    row_b["_id"] = "preflight-row-b"
    collection = FakeCollection([row_a, row_b])
    result = registry.LegalCorpusApprovalRegistry.preflight_verified_approval(proof, collection)
    assert result.state is registry.LegalCorpusApprovalPreflightState.SPLIT_IDENTITY
    assert result.matched_record is None
    assert result.matched_identities == ("mongo:preflight-row-a", "mongo:preflight-row-b")
    assert {identity for _, identity in result.selector_to_row_identity} == {
        "mongo:preflight-row-a", "mongo:preflight-row-b",
    }
    assert result.collision_code is None
    assert collection.insert_calls == []


def test_preflight_rejects_proof_only_input_and_corrupt_or_unreadable_rows() -> None:
    assert _error(lambda: registry.LegalCorpusApprovalRegistry.preflight_verified_approval(cast(Any, {}))) == "LEGAL_CORPUS_APPROVAL_AUTHORITY_INPUT_INVALID"
    proof = _proof()
    corrupt = _stored(proof)
    corrupt["approval_evidence"].pop("evidence_fingerprint")
    assert _error(lambda: registry.LegalCorpusApprovalRegistry.preflight_verified_approval(proof, FakeCollection([corrupt]))) == "LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID"
    lower = PyMongoError("preflight-read")
    collection = FakeCollection()
    collection.read_error = lower
    with pytest.raises(registry.LegalCorpusApprovalRegistryError) as captured:
        registry.LegalCorpusApprovalRegistry.preflight_verified_approval(proof, collection)
    assert captured.value.code == "LEGAL_CORPUS_APPROVAL_READ_FAILED"
    assert captured.value.__cause__ is lower
    assert collection.insert_calls == []


def test_preflight_without_driver_id_uses_stable_semantic_identity() -> None:
    proof = _proof()
    result = registry.LegalCorpusApprovalRegistry.preflight_verified_approval(proof, FakeCollection([_stored(proof)]))
    assert result.state is registry.LegalCorpusApprovalPreflightState.EXACT
    assert result.matched_identities[0].startswith("semantic:")
    assert len(result.matched_identities[0].split(":", 1)[1]) == 128


def test_admission_and_public_preflight_share_reconciliation_core(monkeypatch: pytest.MonkeyPatch) -> None:
    proof = _proof()
    collection = FakeCollection([_stored(proof)])
    calls: list[str] = []
    original = registry._preflight_core

    def observe(source: Any, authorization: Any, session: Any) -> Any:
        calls.append("shared-core")
        return original(source, authorization, session)

    monkeypatch.setattr(registry, "_preflight_core", observe)
    registry.LegalCorpusApprovalRegistry.preflight_verified_approval(proof, collection)
    registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection)
    assert calls == ["shared-core", "shared-core"]
    assert collection.insert_calls == []


@pytest.mark.parametrize("selector", [
    "evidence_id", "authorization_id", "authorization_idempotency", "evidence_idempotency", "target_version",
])
def test_each_unique_identity_divergence_fails_closed(selector: str) -> None:
    proof = _proof()
    row = _stored(proof)
    if selector == "evidence_id":
        row["approval_evidence"]["approval_evidence_id"] = "different-evidence"
    elif selector == "authorization_id":
        row["authorization_id"] = "different-authorization"
    elif selector == "authorization_idempotency":
        row["idempotency_key"] = "different-authorization-idempotency"
    elif selector == "evidence_idempotency":
        row["approval_evidence"]["idempotency_key"] = "different-evidence-idempotency"
    else:
        row["approval_evidence"]["approved_version"] = "1.0.0-OTHER"
    code = _error(lambda: registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, FakeCollection([row])))
    assert code in {
        "LEGAL_CORPUS_APPROVAL_EVIDENCE_ID_COLLISION",
        "LEGAL_CORPUS_APPROVAL_AUTHORIZATION_ID_COLLISION",
        "LEGAL_CORPUS_APPROVAL_IDEMPOTENCY_CONFLICT",
        "LEGAL_CORPUS_APPROVAL_IMMUTABILITY_CONFLICT",
        "LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID",
    }


def test_split_identity_rows_fail_closed_before_insert() -> None:
    proof = _proof()
    row_a = _stored(_proof(authorization_changes={"authorization_id": "223e4567-e89b-42d3-a456-426614174010"}))
    row_b = _stored(_proof(evidence_changes={"approval_evidence_id": "approval-evidence-002"}))
    row_a["_id"] = "row-a"
    row_b["_id"] = "row-b"
    collection = FakeCollection([row_a, row_b])
    assert collection.find_one({"approval_evidence.approval_evidence_id": proof.approval_evidence.approval_evidence_id}) == row_a
    assert collection.find_one({"authorization_id": proof.authorization.authorization_id}) == row_b
    collection.find_calls.clear()
    assert _error(lambda: registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection)) == "LEGAL_CORPUS_APPROVAL_IMMUTABILITY_CONFLICT"
    assert collection.insert_calls == []


def test_duplicate_race_exact_reconciles_with_causal_duplicate() -> None:
    proof = _proof()
    collection = FakeCollection()
    collection.duplicate_on_insert = True
    collection.duplicate_seed = [_stored(proof)]
    result = registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection)
    assert result.state is registry.LegalCorpusApprovalAdmissionState.EXACT_REPLAY
    assert collection.successful_inserts == 0


def test_duplicate_race_unavailable_preserves_cause() -> None:
    proof = _proof()
    collection = FakeCollection()
    collection.duplicate_on_insert = True
    collection.duplicate_seed = []
    with pytest.raises(registry.LegalCorpusApprovalRegistryError) as captured:
        registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection)
    assert captured.value.code == "LEGAL_CORPUS_APPROVAL_DUPLICATE_UNAVAILABLE"
    assert captured.value.__cause__ is not None
    assert isinstance(captured.value.__cause__, DuplicateKeyError)


def test_duplicate_race_divergent_readback_fails_closed() -> None:
    proof = _proof()
    divergent = _stored(_proof(evidence_changes={"approval_evidence_id": "approval-evidence-divergent"}))
    collection = FakeCollection()
    collection.duplicate_on_insert = True
    collection.duplicate_seed = [divergent]
    session = object()
    with pytest.raises(registry.LegalCorpusApprovalRegistryError) as captured:
        registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection, session=session)
    assert captured.value.code == "LEGAL_CORPUS_APPROVAL_AUTHORIZATION_ID_COLLISION"
    assert len(collection.insert_calls) == 1
    assert all(call_session is session for _, call_session in collection.find_calls)


def test_duplicate_race_split_identity_readback_fails_closed() -> None:
    proof = _proof()
    row_a = _stored(_proof(authorization_changes={"authorization_id": "223e4567-e89b-42d3-a456-426614174010"}))
    row_b = _stored(_proof(evidence_changes={"approval_evidence_id": "approval-evidence-002"}))
    row_a["_id"] = "race-row-a"
    row_b["_id"] = "race-row-b"
    collection = FakeCollection()
    collection.duplicate_on_insert = True
    collection.duplicate_seed = [row_a, row_b]
    session = object()
    observed: dict[str, Any] = {}

    def observe(fake: Any) -> None:
        observed["evidence"] = fake.find_one(
            {"approval_evidence.approval_evidence_id": proof.approval_evidence.approval_evidence_id},
            session=session,
        )
        observed["authorization"] = fake.find_one(
            {"authorization_id": proof.authorization.authorization_id},
            session=session,
        )

    collection.duplicate_observer = observe
    with pytest.raises(registry.LegalCorpusApprovalRegistryError) as captured:
        registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection, session=session)
    assert captured.value.code == "LEGAL_CORPUS_APPROVAL_IMMUTABILITY_CONFLICT"
    assert observed["evidence"]["_id"] == "race-row-a"
    assert observed["authorization"]["_id"] == "race-row-b"
    assert collection.insert_calls and len(collection.insert_calls) == 1
    assert all(call_session is session for _, call_session in collection.find_calls)


def test_all_reads_and_write_forward_same_session() -> None:
    proof = _proof()
    collection = FakeCollection()
    session = object()
    registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection, session=session)
    assert collection.find_calls and all(value is session for _, value in collection.find_calls)
    assert len(collection.insert_calls) == 1 and collection.insert_calls[0][1] is session


@pytest.mark.parametrize("mutation", [
    lambda row: row.pop("authorization_id"),
    lambda row: row["approval_evidence"].pop("evidence_fingerprint"),
    lambda row: row.pop("approval_evidence_fingerprint"),
    lambda row: row.__setitem__("extra", True),
    lambda row: row.__setitem__("issued_at", "2026-09-19T12:00:00+00:00"),
    lambda row: row.__setitem__("signature_base64url", "not-base64"),
])
def test_corrupt_rows_are_rejected(mutation: Callable[[dict[str, Any]], object]) -> None:
    proof = _proof()
    row = _stored(proof)
    mutation(row)
    assert _error(lambda: registry.LegalCorpusApprovalRegistry.get_by_approval_evidence_id(proof.approval_evidence.approval_evidence_id, FakeCollection([row]))) == "LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID"


def test_top_level_fingerprint_is_not_repaired() -> None:
    proof = _proof()
    row = _stored(proof)
    row["approval_evidence_fingerprint"] = "0" * 128
    assert _error(lambda: registry.LegalCorpusApprovalRegistry.get_by_approval_evidence_id(proof.approval_evidence.approval_evidence_id, FakeCollection([row]))) == "LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID"


@pytest.mark.parametrize("mutation", [
    lambda row: row["approval_evidence"].__setitem__("evidence_fingerprint", "0" * 128),
    lambda row: row["approval_evidence"].__setitem__("source_content", "changed-content"),
    lambda row: row.__setitem__("approval_evidence_fingerprint", "1" * 128),
    lambda row: row["approval_evidence"].__setitem__("evidence_fingerprint", "2" * 128),
])
def test_fingerprint_mismatch_matrix_is_rejected(mutation: Callable[[dict[str, Any]], object]) -> None:
    proof = _proof()
    row = _stored(proof)
    mutation(row)
    assert _error(lambda: registry.LegalCorpusApprovalRegistry.get_by_approval_evidence_id(proof.approval_evidence.approval_evidence_id, FakeCollection([row]))) == "LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID"


@pytest.mark.parametrize("mutation", [
    lambda row: row["approval_evidence"].__setitem__("unexpected_nested", True),
    lambda row: row["approval_evidence"].pop("source_title"),
    lambda row: row.__setitem__("schema", "unsupported-schema"),
    lambda row: row["approval_evidence"].__setitem__("schema_version", "unsupported-version"),
    lambda row: row.__setitem__("scope", "TENANT"),
    lambda row: row.__setitem__("authorization_id", "not-a-uuid"),
    lambda row: row.__setitem__("nonce", "bad nonce"),
    lambda row: row["approval_evidence"].__setitem__("source_content", 123),
    lambda row: row.__setitem__("issued_at", "2026-09-19T12:00:00.123456Z"),
    lambda row: row["approval_evidence"].__setitem__("approved_at", "2026-09-19T11:30:00.123000+00:00"),
])
def test_closed_schema_corruption_matrix_is_rejected(mutation: Callable[[dict[str, Any]], object]) -> None:
    proof = _proof()
    row = _stored(proof)
    mutation(row)
    collection = FakeCollection([row])
    assert collection.find_one({"approval_evidence.approval_evidence_id": proof.approval_evidence.approval_evidence_id}) == row
    assert _error(lambda: registry.LegalCorpusApprovalRegistry.get_by_approval_evidence_id(proof.approval_evidence.approval_evidence_id, collection)) == "LEGAL_CORPUS_APPROVAL_PERSISTED_INVALID"


def test_read_invalid_id_is_bounded() -> None:
    assert _error(lambda: registry.LegalCorpusApprovalRegistry.get_by_approval_evidence_id(" ", FakeCollection())) == "LEGAL_CORPUS_APPROVAL_AUTHORITY_INPUT_INVALID"


def test_read_failures_are_bounded_and_causal() -> None:
    proof = _proof()
    lower = PyMongoError("read")
    collection = FakeCollection()
    collection.read_error = lower
    with pytest.raises(registry.LegalCorpusApprovalRegistryError) as captured:
        registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection)
    assert captured.value.code == "LEGAL_CORPUS_APPROVAL_READ_FAILED"
    assert captured.value.__cause__ is lower
    assert collection.insert_calls == []


def test_insert_failures_are_bounded_and_do_not_compensate() -> None:
    proof = _proof()
    lower = PyMongoError("insert")
    collection = FakeCollection()
    collection.insert_error = lower
    with pytest.raises(registry.LegalCorpusApprovalRegistryError) as captured:
        registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection)
    assert captured.value.code == "LEGAL_CORPUS_APPROVAL_CREATE_FAILED"
    assert captured.value.__cause__ is lower
    assert collection.successful_inserts == 0


def test_source_has_no_trust_verifier_or_transaction_orchestration() -> None:
    tree = ast.parse(Path(registry.__file__).read_text(encoding="utf-8"))
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert "verify_legal_corpus_approval_authorization" not in names
    assert "MongoClient" not in names
    forbidden = {"start_transaction", "commit_transaction", "abort_transaction", "with_transaction"}
    assert not any(isinstance(node, ast.Attribute) and node.attr in forbidden for node in ast.walk(tree))


def test_source_has_no_orchestration_or_mutating_api() -> None:
    source = Path(registry.__file__).read_text(encoding="utf-8")
    certificate_source = Path(__file__).read_text(encoding="utf-8")
    assert "LegalDocumentRegistry" not in source
    assert "LegalCorpusProvisioningService" not in source
    assert "record_fingerprint" not in source
    forbidden_audit_marker_a = "TO" + "DO"
    forbidden_audit_marker_b = "FIX" + "ME"
    assert forbidden_audit_marker_a not in source and forbidden_audit_marker_b not in source
    multi_code_pattern = "captured.value.code " + "in {"
    assert multi_code_pattern not in certificate_source
    assert not hasattr(registry.LegalCorpusApprovalRegistry, "update")
    assert not hasattr(registry.LegalCorpusApprovalRegistry, "delete")
    assert not hasattr(registry.LegalCorpusApprovalRegistry, "replace")


def test_kernel_resolution_is_explicit_and_missing_database_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(registry.kernel_db, "get_database", lambda: None)
    assert _error(lambda: registry.LegalCorpusApprovalRegistry.ensure_indexes()) == "LEGAL_CORPUS_APPROVAL_DATABASE_UNAVAILABLE"


def test_record_and_authorization_are_immutable() -> None:
    proof = _proof()
    record = registry.LegalCorpusApprovalDurableRecord(proof.authorization, proof.approval_evidence.evidence_fingerprint)
    with pytest.raises(FrozenInstanceError):
        record.approval_evidence_fingerprint = "x"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        proof.authorization.authorization_id = "x"  # type: ignore[misc]


def test_five_identity_reads_precede_first_write() -> None:
    proof = _proof()
    collection = FakeCollection()
    registry.LegalCorpusApprovalRegistry.admit_verified_approval(proof, collection)
    assert len(collection.find_calls) == 5
    assert collection.insert_calls and len(collection.find_calls) == 5
