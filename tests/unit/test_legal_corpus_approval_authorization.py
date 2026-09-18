"""Direct certificate for the signed legal-corpus approval verifier.

TITLE: WILSY OS Legal Corpus Approval Authorization Direct Certificate
VERSION: v1.1.0-R1D-B0F-R9B-P2-R6-R1-C1-LEGAL-CORPUS-APPROVAL-AUTHORIZATION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Independently certifies complete R9B evidence binding and Ed25519
         verification using synthetic in-memory test keys only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_approval_authorization.py
COLLABORATION / OWNERSHIP: Certifies the domain before any production signer,
                            approval registry, service, command, or persistence.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.1.0-R6-R1 certifies guarded proof construction, issuance-time
           retirement cutoffs, complete valid-alternate evidence coverage, and
           complete signed-field perturbation coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic key material is deterministic, in-memory,
                            test-only, never printed or persisted.
TENANT BOUNDARY: PLATFORM approval only; no tenant acceptance is created.
AUTHORITY BOUNDARY: A passing certificate proves verifier behavior only; it
                    does not approve a production document or establish a human.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Every malformed, divergent, expired, revoked, and invalid
                     signature case is required to reject.
"""
from __future__ import annotations

import ast
import base64
import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
    canonical_document_digest,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_authorization import (
    AUTHORITY_SCOPE,
    AUTHORIZED_OPERATION,
    MAX_AUTHORIZATION_LIFETIME,
    SCHEMA,
    LegalCorpusApprovalAuthorization,
    LegalCorpusApprovalAuthorizationError,
    LegalCorpusApprovalAuthorizationOperation,
    LegalCorpusApprovalAuthorizationScope,
    VerifiedLegalCorpusApprovalAuthorization,
    canonical_signed_payload,
    verify_legal_corpus_approval_authorization,
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
from tools.eos.legal_operations.production_legal_corpus import INSTITUTIONAL_CHARTER_DRAFT


UTC = timezone.utc
NOW = datetime(2026, 9, 19, 12, 0, 0, 123456, tzinfo=UTC)
SOURCE = INSTITUTIONAL_CHARTER_DRAFT
TARGET = LegalDocumentVersion(
    document_id=SOURCE.document_id,
    agreement_type=LegalAgreementType.INSTITUTIONAL_CHARTER,
    version="1.0.0-APPROVED",
    title=SOURCE.title,
    jurisdiction=SOURCE.jurisdiction,
    locale=SOURCE.locale,
    effective_from=datetime(2026, 10, 1, tzinfo=UTC),
    status=LegalDocumentStatus.APPROVED,
    content_reference="wilsy-os://legal/institutional-charter/1.0.0-approved",
    content=SOURCE.content,
    sha3_512=canonical_document_digest(SOURCE.content, "wilsy-os://legal/institutional-charter/1.0.0-approved"),
    created_at=datetime(2026, 9, 19, 11, 0, tzinfo=UTC),
    supersedes_document_id=SOURCE.document_id,
)


def _evidence(*, source_document: LegalDocumentVersion = SOURCE, approved_document: LegalDocumentVersion = TARGET, **changes: object) -> LegalCorpusApprovalAuthorityEvidence:
    values = {
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
        "approved_document": approved_document,
        "approved_at": datetime(2026, 9, 19, 11, 30, tzinfo=UTC),
        "effective_from": approved_document.effective_from,
        "idempotency_key": "approval-idempotency-001",
        "provenance_reference": "governance-record-001",
    }
    values.update(changes)
    values["evidence_fingerprint"] = LegalCorpusApprovalAuthorityEvidence.fingerprint_for(**values)
    return LegalCorpusApprovalAuthorityEvidence(**values)


def _trust_root(private_key: Ed25519PrivateKey, *, status: LegalCorpusApprovalTrustStatus = LegalCorpusApprovalTrustStatus.ACTIVE, valid_until: datetime = datetime(2026, 9, 20, tzinfo=UTC)) -> LegalCorpusApprovalTrustRoot:
    public = private_key.public_key().public_bytes_raw()
    encoded = base64.urlsafe_b64encode(public).rstrip(b"=").decode("ascii")
    key_id = LegalCorpusApprovalTrustedKey.derive_key_id(encoded)
    valid_from = datetime(2026, 9, 19, 0, 0, tzinfo=UTC)
    fingerprint = LegalCorpusApprovalTrustedKey.fingerprint_for(
        key_id=key_id,
        issuer_identity=APPROVAL_ISSUER_IDENTITY,
        authority_role=APPROVAL_AUTHORITY_ROLE,
        authority_domain=APPROVAL_AUTHORITY_DOMAIN,
        algorithm=ED25519_ALGORITHM,
        public_key_base64url=encoded,
        valid_from=valid_from,
        valid_until=valid_until,
        status=status,
        revision=1,
        permitted_operations=frozenset({APPROVAL_OPERATION}),
        scope=APPROVAL_SCOPE,
        trust_root_provenance=APPROVAL_TRUST_ROOT_PROVENANCE,
    )
    key = LegalCorpusApprovalTrustedKey(
        key_id=key_id,
        issuer_identity=APPROVAL_ISSUER_IDENTITY,
        authority_role=APPROVAL_AUTHORITY_ROLE,
        authority_domain=APPROVAL_AUTHORITY_DOMAIN,
        algorithm=ED25519_ALGORITHM,
        public_key_base64url=encoded,
        valid_from=valid_from,
        valid_until=valid_until,
        status=status,
        revision=1,
        permitted_operations=frozenset({APPROVAL_OPERATION}),
        scope=APPROVAL_SCOPE,
        trust_root_provenance=APPROVAL_TRUST_ROOT_PROVENANCE,
        trust_fingerprint=fingerprint,
    )
    return LegalCorpusApprovalTrustRoot((key,))


def _envelope(private_key: Ed25519PrivateKey, *, issued_at: datetime = NOW, expires_at: datetime = NOW + timedelta(minutes=30), trust_status: LegalCorpusApprovalTrustStatus = LegalCorpusApprovalTrustStatus.ACTIVE, trust_valid_until: datetime = datetime(2026, 9, 20, tzinfo=UTC), **changes: object) -> LegalCorpusApprovalAuthorization:
    root = _trust_root(private_key, status=trust_status, valid_until=trust_valid_until)
    key = root.all_keys()[0]
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
        "approval_evidence": _evidence(),
        "issued_at": issued_at,
        "expires_at": expires_at,
        "nonce": base64.urlsafe_b64encode(b"n" * 32).rstrip(b"=").decode("ascii"),
        "idempotency_key": "223e4567-e89b-42d3-a456-426614174001",
        "signature_base64url": base64.urlsafe_b64encode(b"s" * 64).rstrip(b"=").decode("ascii"),
        "schema": SCHEMA,
    }
    values.update(changes)
    unsigned = LegalCorpusApprovalAuthorization(**cast(Any, values))
    signed = private_key.sign(canonical_signed_payload(unsigned))
    return replace(unsigned, signature_base64url=base64.urlsafe_b64encode(signed).rstrip(b"=").decode("ascii"))


def _private() -> Ed25519PrivateKey:
    # TEST-ONLY synthetic key; never a production or filesystem key.
    return Ed25519PrivateKey.from_private_bytes(bytes(range(32)))


def _independent_payload(authorization: LegalCorpusApprovalAuthorization) -> bytes:
    """Build the expected signed bytes without calling production helpers."""
    evidence = authorization.approval_evidence
    def document(document: LegalDocumentVersion, prefix: str) -> dict[str, object]:
        return {
            f"{prefix}_document_id": document.document_id,
            f"{prefix}_agreement_type": document.agreement_type.value,
            f"{prefix}_version": document.version,
            f"{prefix}_title": document.title,
            f"{prefix}_jurisdiction": document.jurisdiction,
            f"{prefix}_locale": document.locale,
            f"{prefix}_effective_from": document.effective_from.astimezone(UTC).isoformat(timespec="microseconds"),
            f"{prefix}_status": document.status.value,
            f"{prefix}_content_reference": document.content_reference,
            f"{prefix}_content": document.content,
            f"{prefix}_sha3_512": document.sha3_512,
            f"{prefix}_created_at": document.created_at.astimezone(UTC).isoformat(timespec="microseconds"),
            f"{prefix}_supersedes_document_id": document.supersedes_document_id,
        }
    approval_evidence: dict[str, object] = {
        "approval_evidence_id": evidence.approval_evidence_id,
        "schema_version": evidence.schema_version,
        "scope": evidence.scope.value,
        "operation": evidence.operation.value,
        "approval_decision": evidence.approval_decision.value,
        "approval_authority_source": evidence.approval_authority_source.value,
        "approval_authority_mechanism": evidence.approval_authority_mechanism.value,
        "approval_authority_mechanism_version": evidence.approval_authority_mechanism_version,
        "human_authority_representation": evidence.human_authority_representation,
        "approval_signing_mechanism": evidence.approval_signing_mechanism.value,
        "approval_signing_mechanism_version": evidence.approval_signing_mechanism_version,
        "approval_signing_key_id": evidence.approval_signing_key_id,
        "approval_signature_reference": evidence.approval_signature_reference,
        "approved_at": evidence.approved_at.astimezone(UTC).isoformat(timespec="microseconds"),
        "effective_from": evidence.effective_from.astimezone(UTC).isoformat(timespec="microseconds"),
        "idempotency_key": evidence.idempotency_key,
        "provenance_reference": evidence.provenance_reference,
    }
    approval_evidence.update(document(evidence.source_document, "source"))
    approval_evidence.update(document(evidence.approved_document, "approved"))
    approval_evidence["evidence_fingerprint"] = evidence.evidence_fingerprint
    payload = {
        "algorithm": authorization.algorithm,
        "approval_evidence": approval_evidence,
        "approval_evidence_fingerprint": evidence.evidence_fingerprint,
        "authority_domain": authorization.authority_domain,
        "authority_role": authorization.authority_role,
        "authorization_id": authorization.authorization_id,
        "expires_at": authorization.expires_at.astimezone(UTC).isoformat(timespec="microseconds"),
        "idempotency_key": authorization.idempotency_key,
        "issued_at": authorization.issued_at.astimezone(UTC).isoformat(timespec="microseconds"),
        "issuer_identity": authorization.issuer_identity,
        "key_id": authorization.key_id,
        "nonce": authorization.nonce,
        "operation": authorization.operation.value,
        "schema": authorization.schema,
        "scope": authorization.scope.value,
        "trust_fingerprint": authorization.trust_fingerprint,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _document_variant(document: LegalDocumentVersion, **changes: object) -> LegalDocumentVersion:
    values: dict[str, object] = {
        "document_id": document.document_id,
        "agreement_type": document.agreement_type,
        "version": document.version,
        "title": document.title,
        "jurisdiction": document.jurisdiction,
        "locale": document.locale,
        "effective_from": document.effective_from,
        "status": document.status,
        "content_reference": document.content_reference,
        "content": document.content,
        "sha3_512": document.sha3_512,
        "created_at": document.created_at,
        "supersedes_document_id": document.supersedes_document_id,
    }
    values.update(changes)
    if "content" in changes or "content_reference" in changes:
        values["sha3_512"] = canonical_document_digest(cast(str, values["content"]), cast(str, values["content_reference"]))
    return LegalDocumentVersion(**cast(Any, values))


def _valid_evidence_alternates() -> dict[str, LegalCorpusApprovalAuthorityEvidence]:
    alternate_source = _document_variant(SOURCE, document_id="WILSY-ALT-SOURCE")
    alternate_target = _document_variant(TARGET, document_id="WILSY-ALT-SOURCE", supersedes_document_id="WILSY-ALT-SOURCE")
    alternate_family_source = _document_variant(SOURCE, agreement_type=LegalAgreementType.USER_TERMS)
    alternate_family_target = _document_variant(TARGET, agreement_type=LegalAgreementType.USER_TERMS)
    alternate_prose = "The alternate governed legal prose remains intentionally synthetic for this unit certificate."
    alternate_prose_source = _document_variant(SOURCE, content=alternate_prose)
    alternate_prose_target = _document_variant(TARGET, content=alternate_prose)
    return {
        "approval_evidence_id": _evidence(approval_evidence_id="approval-evidence-002"),
        "human_authority_representation": _evidence(human_authority_representation="human-governance-record-002"),
        "approval_signing_key_id": _evidence(approval_signing_key_id="approval-key-reference-002"),
        "approval_signature_reference": _evidence(approval_signature_reference="approval-signature-reference-002"),
        "approved_at": _evidence(approved_at=datetime(2026, 9, 19, 11, 31, tzinfo=UTC)),
        "effective_from": _evidence(approved_document=_document_variant(TARGET, effective_from=datetime(2026, 10, 2, tzinfo=UTC))),
        "idempotency_key": _evidence(idempotency_key="approval-idempotency-002"),
        "provenance_reference": _evidence(provenance_reference="governance-record-002"),
        "source_document_id": _evidence(source_document=alternate_source, approved_document=alternate_target),
        "source_agreement_type": _evidence(source_document=alternate_family_source, approved_document=alternate_family_target),
        "source_version": _evidence(source_document=_document_variant(SOURCE, version="1.0.1-DRAFT"), approved_document=_document_variant(TARGET, supersedes_document_id=SOURCE.document_id)),
        "source_title": _evidence(source_document=_document_variant(SOURCE, title="Alternate Charter Title")),
        "source_jurisdiction": _evidence(source_document=_document_variant(SOURCE, jurisdiction="ZA-ALT")),
        "source_locale": _evidence(source_document=_document_variant(SOURCE, locale="en-ZA-alt")),
        "source_effective_from": _evidence(source_document=_document_variant(SOURCE, effective_from=datetime(2026, 9, 1, tzinfo=UTC))),
        "source_content_reference": _evidence(source_document=_document_variant(SOURCE, content_reference="wilsy-os://legal/alternate-source")),
        "source_content": _evidence(source_document=alternate_prose_source, approved_document=alternate_prose_target),
        "source_sha3_512": _evidence(source_document=alternate_prose_source, approved_document=alternate_prose_target),
        "source_created_at": _evidence(source_document=_document_variant(SOURCE, created_at=datetime(2026, 9, 10, tzinfo=UTC))),
        "source_supersedes_document_id": _evidence(source_document=_document_variant(SOURCE, supersedes_document_id="prior-source")),
        "approved_document_id": _evidence(source_document=alternate_source, approved_document=alternate_target),
        "approved_agreement_type": _evidence(source_document=alternate_family_source, approved_document=alternate_family_target),
        "approved_version": _evidence(approved_document=_document_variant(TARGET, version="1.0.0-APPROVED-2")),
        "approved_title": _evidence(approved_document=_document_variant(TARGET, title="Alternate Approved Title")),
        "approved_jurisdiction": _evidence(approved_document=_document_variant(TARGET, jurisdiction="ZA-ALT")),
        "approved_locale": _evidence(approved_document=_document_variant(TARGET, locale="en-ZA-alt")),
        "approved_effective_from": _evidence(approved_document=_document_variant(TARGET, effective_from=datetime(2026, 10, 2, tzinfo=UTC))),
        "approved_content_reference": _evidence(approved_document=_document_variant(TARGET, content_reference="wilsy-os://legal/alternate-approved")),
        "approved_content": _evidence(source_document=alternate_prose_source, approved_document=alternate_prose_target),
        "approved_sha3_512": _evidence(source_document=alternate_prose_source, approved_document=alternate_prose_target),
        "approved_created_at": _evidence(approved_document=_document_variant(TARGET, created_at=datetime(2026, 9, 19, 11, 1, tzinfo=UTC))),
        "evidence_fingerprint": _evidence(approval_evidence_id="approval-evidence-003"),
    }


def test_valid_signature_and_complete_evidence_are_verified() -> None:
    private = _private()
    authorization = _envelope(private)
    result = verify_legal_corpus_approval_authorization(authorization, _trust_root(private), now=NOW, source_document=SOURCE, approved_document=TARGET)
    assert isinstance(result, VerifiedLegalCorpusApprovalAuthorization)
    assert result.approval_evidence.evidence_fingerprint == _evidence().evidence_fingerprint


def test_verified_result_requires_private_verification_factory() -> None:
    private = _private()
    root = _trust_root(private)
    with pytest.raises(TypeError):
        VerifiedLegalCorpusApprovalAuthorization(object(), object(), NOW)  # type: ignore[arg-type]
    authorization = _envelope(private)
    proof = verify_legal_corpus_approval_authorization(authorization, root, now=NOW)
    assert isinstance(proof, VerifiedLegalCorpusApprovalAuthorization)
    assert proof.verified_at == NOW


def test_retired_cutoff_uses_issuance_time_not_verifier_time() -> None:
    private = _private()
    cutoff = NOW + timedelta(minutes=10)
    historical = _envelope(
        private,
        issued_at=NOW,
        expires_at=NOW + timedelta(minutes=30),
        trust_status=LegalCorpusApprovalTrustStatus.RETIRED,
        trust_valid_until=cutoff,
    )
    retired_root = _trust_root(private, status=LegalCorpusApprovalTrustStatus.RETIRED, valid_until=cutoff)
    assert verify_legal_corpus_approval_authorization(historical, retired_root, now=cutoff + timedelta(minutes=1)).authorization_id == historical.authorization_id
    at_cutoff = _envelope(
        private,
        issued_at=cutoff,
        expires_at=cutoff + timedelta(minutes=30),
        trust_status=LegalCorpusApprovalTrustStatus.RETIRED,
        trust_valid_until=cutoff,
    )
    with pytest.raises(LegalCorpusApprovalAuthorizationError, match="APPROVAL_KEY_RETIRED"):
        verify_legal_corpus_approval_authorization(at_cutoff, retired_root, now=cutoff)
    after_cutoff = _envelope(
        private,
        issued_at=cutoff + timedelta(microseconds=1),
        expires_at=cutoff + timedelta(minutes=30),
        trust_status=LegalCorpusApprovalTrustStatus.RETIRED,
        trust_valid_until=cutoff,
    )
    with pytest.raises(LegalCorpusApprovalAuthorizationError, match="APPROVAL_KEY_RETIRED"):
        verify_legal_corpus_approval_authorization(after_cutoff, retired_root, now=after_cutoff.issued_at)
    expired = _envelope(
        private,
        issued_at=NOW,
        expires_at=NOW + timedelta(minutes=5),
        trust_status=LegalCorpusApprovalTrustStatus.RETIRED,
        trust_valid_until=cutoff,
    )
    with pytest.raises(LegalCorpusApprovalAuthorizationError, match="AUTHORIZATION_EXPIRED"):
        verify_legal_corpus_approval_authorization(expired, retired_root, now=NOW + timedelta(minutes=6))
    revoked_root = _trust_root(private, status=LegalCorpusApprovalTrustStatus.REVOKED, valid_until=cutoff)
    with pytest.raises(LegalCorpusApprovalAuthorizationError, match="APPROVAL_KEY_REVOKED"):
        verify_legal_corpus_approval_authorization(historical, revoked_root, now=NOW)


def test_every_valid_alternate_evidence_field_is_rejected_when_expected_differs() -> None:
    alternates = _valid_evidence_alternates()
    assert len(alternates) == 32
    for field, alternate in alternates.items():
        private = _private()
        authorization = _envelope(private, approval_evidence=_evidence())
        with pytest.raises(LegalCorpusApprovalAuthorizationError, match="AUTHORIZATION_EVIDENCE_MISMATCH"):
            verify_legal_corpus_approval_authorization(authorization, _trust_root(private), now=NOW, expected_evidence=alternate)
        assert alternate != authorization.approval_evidence, field


def test_closed_evidence_fields_are_proven_closed_by_upstream_contract() -> None:
    all_fields = {
        "approval_evidence_id", "schema_version", "scope", "operation", "approval_decision",
        "approval_authority_source", "approval_authority_mechanism", "approval_authority_mechanism_version",
        "human_authority_representation", "approval_signing_mechanism", "approval_signing_mechanism_version",
        "approval_signing_key_id", "approval_signature_reference", "approved_at", "effective_from",
        "idempotency_key", "provenance_reference", "source_document_id", "source_agreement_type",
        "source_version", "source_title", "source_jurisdiction", "source_locale", "source_effective_from",
        "source_status", "source_content_reference", "source_content", "source_sha3_512", "source_created_at",
        "source_supersedes_document_id", "approved_document_id", "approved_agreement_type", "approved_version",
        "approved_title", "approved_jurisdiction", "approved_locale", "approved_effective_from", "approved_status",
        "approved_content_reference", "approved_content", "approved_sha3_512", "approved_created_at",
        "approved_supersedes_document_id", "evidence_fingerprint",
    }
    valid_alternate_fields = set(_valid_evidence_alternates())
    closed_fields = all_fields - valid_alternate_fields
    assert len(all_fields) == 44
    assert len(valid_alternate_fields) == 32
    assert len(closed_fields) == 12
    assert closed_fields == {
        "schema_version", "scope", "operation", "approval_decision", "approval_authority_source",
        "approval_authority_mechanism", "approval_authority_mechanism_version", "approval_signing_mechanism",
        "approval_signing_mechanism_version", "source_status", "approved_status", "approved_supersedes_document_id",
    }


def test_all_signed_top_level_fields_reject_without_resigning() -> None:
    private = _private()
    authorization = _envelope(private)
    alternate_evidence = _evidence(approval_evidence_id="approval-evidence-004")
    mutations: dict[str, object] = {
        "schema": "OTHER-SCHEMA/V1",
        "authorization_id": "323e4567-e89b-42d3-a456-426614174002",
        "issuer_identity": "OTHER_ISSUER",
        "authority_role": "OTHER_ROLE",
        "authority_domain": "OTHER_DOMAIN",
        "algorithm": "Ed448",
        "key_id": "prdca-key:legal-corpus-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "trust_fingerprint": "0" * 128,
        "operation": "OTHER_OPERATION",
        "scope": "TENANT",
        "approval_evidence": alternate_evidence,
        "issued_at": NOW + timedelta(seconds=1),
        "expires_at": NOW + timedelta(minutes=29),
        "nonce": base64.urlsafe_b64encode(b"x" * 32).rstrip(b"=").decode("ascii"),
        "idempotency_key": "423e4567-e89b-42d3-a456-426614174003",
    }
    for field, value in mutations.items():
        try:
            mutated = replace(authorization, **{field: value})
        except LegalCorpusApprovalAuthorizationError:
            continue
        with pytest.raises(LegalCorpusApprovalAuthorizationError):
            verify_legal_corpus_approval_authorization(mutated, _trust_root(private), now=NOW)


def test_certificate_independently_reconstructs_canonical_payload() -> None:
    authorization = _envelope(_private())
    expected = _independent_payload(authorization)
    assert expected == canonical_signed_payload(authorization)
    payload = json.loads(expected)
    evidence = payload["approval_evidence"]
    assert len(evidence) == 44
    assert "evidence_fingerprint" in evidence
    assert payload["approval_evidence_fingerprint"] == evidence["evidence_fingerprint"]


def test_envelope_and_verified_result_are_immutable() -> None:
    authorization = _envelope(_private())
    with pytest.raises(FrozenInstanceError):
        authorization.key_id = "changed"  # type: ignore[misc]
    result = verify_legal_corpus_approval_authorization(authorization, _trust_root(_private()), now=NOW)
    with pytest.raises(FrozenInstanceError):
        result.authorization = authorization  # type: ignore[misc]


@pytest.mark.parametrize("field", ["authorization_id", "idempotency_key"])
def test_identity_must_be_lowercase_uuid4(field: str) -> None:
    private = _private()
    with pytest.raises(LegalCorpusApprovalAuthorizationError) as error:
        cast(Any, _envelope)(private, **{field: "123e4567-e89b-12d3-a456-426614174000"})
    assert error.value.code == "AUTHORIZATION_SCHEMA_INVALID"


@pytest.mark.parametrize("nonce", [None, b"bytes", "", " " + "A" * 43, "A" * 42 + "=", "!" * 43, base64.urlsafe_b64encode(b"n" * 31).decode()])
def test_nonce_encoding_rejects_malformed_values(nonce: object) -> None:
    with pytest.raises(LegalCorpusApprovalAuthorizationError) as error:
        _envelope(_private(), nonce=nonce)
    assert error.value.code == "AUTHORIZATION_NONCE_INVALID"


@pytest.mark.parametrize("signature", [None, b"bytes", "", " " + "A" * 86, "A" * 86 + " ", "A" * 85 + "=", "!" * 86, base64.urlsafe_b64encode(b"s" * 63).decode()])
def test_signature_encoding_rejects_malformed_values(signature: object) -> None:
    with pytest.raises(LegalCorpusApprovalAuthorizationError) as error:
        _envelope(_private(), signature_base64url=signature)
    assert error.value.code == "AUTHORIZATION_SIGNATURE_ENCODING_INVALID"


def test_signature_tampering_and_wrong_evidence_fail_closed() -> None:
    private = _private()
    authorization = _envelope(private)
    tampered = replace(authorization, signature_base64url=base64.urlsafe_b64encode(b"x" * 64).rstrip(b"=").decode())
    with pytest.raises(LegalCorpusApprovalAuthorizationError, match="AUTHORIZATION_SIGNATURE_INVALID"):
        verify_legal_corpus_approval_authorization(tampered, _trust_root(private), now=NOW)
    with pytest.raises(LegalCorpusApprovalAuthorizationError, match="AUTHORIZATION_EVIDENCE_MISMATCH"):
        verify_legal_corpus_approval_authorization(authorization, _trust_root(private), now=NOW, source_document=TARGET, approved_document=TARGET)


def test_temporal_boundaries_and_maximum_lifetime() -> None:
    private = _private()
    root = _trust_root(private)
    exact = _envelope(private)
    verify_legal_corpus_approval_authorization(exact, root, now=NOW)
    verify_legal_corpus_approval_authorization(exact, root, now=exact.expires_at - timedelta(microseconds=1))
    with pytest.raises(LegalCorpusApprovalAuthorizationError, match="AUTHORIZATION_EXPIRED"):
        verify_legal_corpus_approval_authorization(exact, root, now=exact.expires_at)
    with pytest.raises(LegalCorpusApprovalAuthorizationError, match="AUTHORIZATION_NOT_YET_VALID"):
        verify_legal_corpus_approval_authorization(exact, root, now=exact.issued_at - timedelta(microseconds=1))
    with pytest.raises(LegalCorpusApprovalAuthorizationError, match="AUTHORIZATION_SCHEMA_INVALID"):
        _envelope(private, expires_at=NOW + MAX_AUTHORIZATION_LIFETIME + timedelta(microseconds=1))
    with pytest.raises(LegalCorpusApprovalAuthorizationError, match="AUTHORIZATION_SCHEMA_INVALID"):
        _envelope(private, issued_at=datetime(2026, 9, 19, 12, 0), expires_at=datetime(2026, 9, 19, 12, 1))


def test_trust_lifecycle_and_unknown_key_fail_closed() -> None:
    private = _private()
    authorization = _envelope(private)
    with pytest.raises(LegalCorpusApprovalAuthorizationError, match="APPROVAL_KEY_REVOKED"):
        verify_legal_corpus_approval_authorization(authorization, _trust_root(private, status=LegalCorpusApprovalTrustStatus.REVOKED), now=NOW)
    with pytest.raises(LegalCorpusApprovalAuthorizationError, match="UNKNOWN_APPROVAL_KEY"):
        verify_legal_corpus_approval_authorization(authorization, LegalCorpusApprovalTrustRoot(), now=NOW)
    retired = _trust_root(private, status=LegalCorpusApprovalTrustStatus.RETIRED)
    retired_authorization = _envelope(private, trust_status=LegalCorpusApprovalTrustStatus.RETIRED)
    assert verify_legal_corpus_approval_authorization(retired_authorization, retired, now=NOW).authorization_id == retired_authorization.authorization_id


def test_source_has_no_production_signer_or_persistence_surface() -> None:
    path = Path("tools/eos/legal_operations/domain/legal_corpus_approval_authorization.py")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert "Ed25519PrivateKey" not in names
    assert "MongoClient" not in names
    assert "sign" not in {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert "PRODUCTION_PRIVATE_KEY" not in source


def test_authority_constants_remain_distinct_and_platform_scoped() -> None:
    assert AUTHORIZED_OPERATION == "LEGAL_CORPUS_DOCUMENT_APPROVAL"
    assert AUTHORITY_SCOPE == "PLATFORM"
    assert APPROVAL_SCOPE == AUTHORITY_SCOPE


# ARTIFACT: test_legal_corpus_approval_authorization.py
# VERSION: v1.1.0-R1D-B0F-R9B-P2-R6-R1-C1-LEGAL-CORPUS-APPROVAL-AUTHORIZATION-CERT
# AUTHORITY BOUNDARY: direct verifier certificate only; no production authority
# TENANT POSTURE: platform-only synthetic evidence; no tenant acceptance
# FAIL-CLOSED POSTURE: malformed and divergent proof must reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
