"""Direct certificate for the legal-corpus approval authority value.

TITLE: WILSY OS Legal Corpus Approval Authority Direct Certificate
VERSION: v1.1.0-R1D-B0F-B4-R9B-P2-R1-C1-LEGAL-CORPUS-APPROVAL-AUTHORITY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Independently certifies the pure immutable approval-evidence domain
         without Mongo, signing, network, acceptance, or production approval.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_approval_authority.py
COLLABORATION / OWNERSHIP: Certifies the approval domain before any registry,
                            signer, operator command, or production promotion.
CERTIFICATION / UPDATE DATE: 2026-09-18
CHANGELOG: v1.1.0-R9B-P2-R1 repairs typed document mutation coverage, removes
           broad exception masking, and certifies adversarial source/target,
           scope, operation, fingerprint, timestamp, and control matrices.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No secrets, private keys, network, or persistence;
                            only deterministic public evidence metadata is used.
TENANT BOUNDARY: Platform approval evidence is tenant-neutral; acceptance is
                 not exercised or created by this certificate.
AUTHORITY BOUNDARY: A passing test certifies implementation semantics only; it
                    does not approve a real document or verify a human signer.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Every divergence and invalid lifecycle input must reject.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from dataclasses import FrozenInstanceError
from enum import StrEnum
from typing import Any
from pathlib import Path

import pytest

from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
    canonical_document_digest,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_authority import (
    APPROVAL_EVIDENCE_SCHEMA_VERSION,
    APPROVAL_AUTHORITY_MECHANISM,
    APPROVAL_AUTHORITY_MECHANISM_VERSION,
    APPROVAL_AUTHORITY_SOURCE,
    APPROVAL_OPERATION,
    APPROVAL_SCOPE,
    APPROVAL_SIGNING_MECHANISM,
    APPROVAL_SIGNING_MECHANISM_VERSION,
    LegalCorpusApprovalAuthorityError,
    LegalCorpusApprovalAuthorityEvidence,
    LegalCorpusApprovalAuthorityMechanism,
    LegalCorpusApprovalAuthorityScope,
    LegalCorpusApprovalAuthoritySource,
    LegalCorpusApprovalDecision,
    LegalCorpusApprovalOperation,
    LegalCorpusApprovalSigningMechanism,
)
from tools.eos.legal_operations.production_legal_corpus import INSTITUTIONAL_CHARTER_DRAFT


_UTC = timezone.utc
_SOURCE = INSTITUTIONAL_CHARTER_DRAFT
_TARGET_CONTENT_REFERENCE = "wilsy-os://legal/institutional-charter/1.0.0"
_TARGET_EFFECTIVE = datetime(2026, 10, 1, tzinfo=_UTC)
_APPROVED_AT = datetime(2026, 9, 18, 12, 0, tzinfo=_UTC)


def _target(*, status: LegalDocumentStatus = LegalDocumentStatus.APPROVED, version: str = "1.0.0", content: str | None = None, content_reference: str = _TARGET_CONTENT_REFERENCE, agreement_type: LegalAgreementType = LegalAgreementType.INSTITUTIONAL_CHARTER, document_id: str = _SOURCE.document_id, supersedes_document_id: str | None = _SOURCE.document_id, effective_from: datetime = _TARGET_EFFECTIVE) -> LegalDocumentVersion:
    prose = _SOURCE.content if content is None else content
    return LegalDocumentVersion(
        document_id=document_id,
        agreement_type=agreement_type,
        version=version,
        title=_SOURCE.title,
        jurisdiction=_SOURCE.jurisdiction,
        locale=_SOURCE.locale,
        effective_from=effective_from,
        status=status,
        content_reference=content_reference,
        content=prose,
        sha3_512=canonical_document_digest(prose, content_reference),
        created_at=_APPROVED_AT,
        supersedes_document_id=supersedes_document_id,
    )


def _document_with(document: LegalDocumentVersion, **changes: object) -> LegalDocumentVersion:
    """Clone a document with typed fields while retaining domain validation."""
    values: dict[str, Any] = {
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
        values["sha3_512"] = canonical_document_digest(values["content"], values["content_reference"])
    return LegalDocumentVersion(**values)


def _kwargs(**changes: Any) -> dict[str, Any]:
    target = _target()
    values: dict[str, Any] = {
        "approval_evidence_id": "approval-001",
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
        "approval_signing_key_id": "public-key-ref-001",
        "approval_signature_reference": "signature-evidence-ref-001",
        "source_document": _SOURCE,
        "approved_document": target,
        "approved_at": _APPROVED_AT,
        "effective_from": _TARGET_EFFECTIVE,
        "idempotency_key": "approval-idempotency-001",
        "provenance_reference": "governance-record-001",
    }
    values.update(changes)
    values["evidence_fingerprint"] = LegalCorpusApprovalAuthorityEvidence.fingerprint_for(**values)
    return values


def _evidence(**changes: Any) -> LegalCorpusApprovalAuthorityEvidence:
    return LegalCorpusApprovalAuthorityEvidence(**_kwargs(**changes))


def test_happy_path_binds_exact_reviewed_draft_and_approved_successor() -> None:
    evidence = _evidence()
    evidence.verify_against(_SOURCE, _target())
    serialized = evidence.to_document()
    assert serialized["scope"] == APPROVAL_SCOPE
    assert serialized["operation"] == APPROVAL_OPERATION
    assert serialized["source_status"] == LegalDocumentStatus.DRAFT_REVIEW_REQUIRED.value
    assert serialized["approved_status"] == LegalDocumentStatus.APPROVED.value
    assert len(evidence.evidence_fingerprint) == 128


def test_value_is_frozen_and_slotted() -> None:
    evidence = _evidence()
    assert hasattr(type(evidence), "__slots__")
    with pytest.raises(FrozenInstanceError):
        evidence.approval_decision = LegalCorpusApprovalDecision.APPROVE  # type: ignore[misc]
    with pytest.raises(AttributeError):
        evidence.unexpected = "mutation"  # type: ignore[attr-defined]


@pytest.mark.parametrize("family", [
    LegalAgreementType.INSTITUTIONAL_CHARTER,
    LegalAgreementType.USER_TERMS,
    LegalAgreementType.ACCEPTABLE_USE,
    LegalAgreementType.PRIVACY_NOTICE,
    LegalAgreementType.AI_ASSISTANCE_NOTICE,
    LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE,
])
def test_all_six_platform_families_are_eligible_when_transition_is_valid(family: LegalAgreementType) -> None:
    source = LegalDocumentVersion(
        document_id=f"DOC-{family.value}", agreement_type=family, version="0.1.0-DRAFT",
        title="Platform document", jurisdiction="ZA", locale="en-ZA",
        effective_from=datetime(2026, 9, 1, tzinfo=_UTC), status=LegalDocumentStatus.DRAFT_REVIEW_REQUIRED,
        content_reference=f"wilsy-os://legal/{family.value.lower()}/0.1.0-draft", content="same reviewed prose",
        sha3_512=canonical_document_digest("same reviewed prose", f"wilsy-os://legal/{family.value.lower()}/0.1.0-draft"),
        created_at=datetime(2026, 8, 1, tzinfo=_UTC),
    )
    target_ref = f"wilsy-os://legal/{family.value.lower()}/0.1.0"
    target = LegalDocumentVersion(
        document_id=source.document_id, agreement_type=family, version="0.1.0",
        title=source.title, jurisdiction=source.jurisdiction, locale=source.locale,
        effective_from=datetime(2026, 10, 1, tzinfo=_UTC), status=LegalDocumentStatus.APPROVED,
        content_reference=target_ref, content=source.content,
        sha3_512=canonical_document_digest(source.content, target_ref), created_at=_APPROVED_AT,
        supersedes_document_id=source.document_id,
    )
    values = _kwargs(source_document=source, approved_document=target, effective_from=target.effective_from)
    evidence = LegalCorpusApprovalAuthorityEvidence(**values)
    evidence.verify_against(source, target)


@pytest.mark.parametrize("family", [
    LegalAgreementType.MASTER_SUBSCRIPTION_AGREEMENT,
    LegalAgreementType.ORDER_FORM,
    LegalAgreementType.DATA_PROCESSING_AGREEMENT,
    LegalAgreementType.SECURITY_SLA_SCHEDULE,
    LegalAgreementType.PRODUCT_ADDENDUM,
])
def test_commercial_families_rejected(family: LegalAgreementType) -> None:
    reference = f"wilsy-os://legal/{family.value.lower()}/0.1.0-draft"
    commercial_source = LegalDocumentVersion(
        document_id="COMMERCIAL-DOCUMENT",
        agreement_type=family,
        version="0.1.0-DRAFT",
        title="Commercial document",
        jurisdiction="ZA",
        locale="en-ZA",
        effective_from=datetime(2026, 9, 1, tzinfo=_UTC),
        status=LegalDocumentStatus.DRAFT_REVIEW_REQUIRED,
        content_reference=reference,
        content="commercial reviewed prose",
        sha3_512=canonical_document_digest("commercial reviewed prose", reference),
        created_at=datetime(2026, 8, 1, tzinfo=_UTC),
    )
    with pytest.raises(LegalCorpusApprovalAuthorityError, match="APPROVAL_FAMILY_NOT_ELIGIBLE"):
        _evidence(source_document=commercial_source)


def test_fixed_authority_and_human_representation_are_not_shortcuts() -> None:
    assert APPROVAL_EVIDENCE_SCHEMA_VERSION == "v1.0.0"
    assert APPROVAL_AUTHORITY_SOURCE != "DEPLOYMENT_OPERATOR_LEGAL_CORPUS_ADMISSION"
    assert APPROVAL_AUTHORITY_MECHANISM == "HUMAN_GOVERNED_APPROVAL_RECORD"
    with pytest.raises(LegalCorpusApprovalAuthorityError) as human_error:
        _evidence(human_authority_representation="\n")
    assert human_error.value.code == "HUMAN_AUTHORITY_REPRESENTATION_INVALID"
    with pytest.raises(LegalCorpusApprovalAuthorityError) as source_error:
        _evidence(approval_authority_source="ADMIN")
    assert source_error.value.code == "APPROVAL_AUTHORITY_SOURCE_INVALID"
    with pytest.raises(LegalCorpusApprovalAuthorityError, match="SCHEMA_VERSION_INVALID"):
        _evidence(schema_version="v9.9.9")


@pytest.mark.parametrize(("changes", "code"), [
    ({"source_document": _target(status=LegalDocumentStatus.APPROVED)}, "SOURCE_NOT_REVIEWED_DRAFT"),
    ({"approved_document": _target(status=LegalDocumentStatus.DRAFT_REVIEW_REQUIRED)}, "TARGET_NOT_APPROVED"),
    ({"approved_document": _target(version="1.0.0", supersedes_document_id=None)}, "SUPERSESSION_INVALID"),
    ({"approved_document": _target(version="1.0.0", content="unreviewed prose")}, "REVIEWED_PROSE_DRIFT"),
])
def test_lifecycle_and_transition_divergence_rejects(changes: dict[str, object], code: str) -> None:
    with pytest.raises(LegalCorpusApprovalAuthorityError) as caught:
        _evidence(**changes)
    assert caught.value.code == code


@pytest.mark.parametrize(
    ("field", "mutated", "code"),
    [
        ("document_id", {"document_id": "OTHER-SOURCE"}, "SOURCE_DOCUMENT_MISMATCH"),
        ("agreement_type", {"agreement_type": LegalAgreementType.USER_TERMS}, "SOURCE_DOCUMENT_MISMATCH"),
        ("version", {"version": "9.9.9-DRAFT"}, "SOURCE_DOCUMENT_MISMATCH"),
        ("content_reference", {"content_reference": "wilsy-os://legal/institutional-charter/other-draft"}, "SOURCE_DOCUMENT_MISMATCH"),
        ("content", {"content": _SOURCE.content + "\nReviewed amendment drift."}, "SOURCE_DOCUMENT_MISMATCH"),
        ("effective_from", {"effective_from": datetime(2026, 9, 18, tzinfo=_UTC)}, "SOURCE_DOCUMENT_MISMATCH"),
        ("title", {"title": "Other title"}, "SOURCE_DOCUMENT_MISMATCH"),
        ("jurisdiction", {"jurisdiction": "US"}, "SOURCE_DOCUMENT_MISMATCH"),
        ("locale", {"locale": "en-US"}, "SOURCE_DOCUMENT_MISMATCH"),
        ("created_at", {"created_at": datetime(2026, 9, 18, tzinfo=_UTC)}, "SOURCE_DOCUMENT_MISMATCH"),
        ("supersedes_document_id", {"supersedes_document_id": "OLDER-SOURCE"}, "SOURCE_DOCUMENT_MISMATCH"),
    ],
)
def test_source_mismatch_reaches_verifier(field: str, mutated: dict[str, Any], code: str) -> None:
    source = _document_with(_SOURCE, **mutated)
    assert isinstance(source, LegalDocumentVersion)
    with pytest.raises(LegalCorpusApprovalAuthorityError) as caught:
        _evidence().verify_against(source, _target())
    assert caught.value.code == code


@pytest.mark.parametrize(
    ("field", "mutated", "code"),
    [
        ("document_id", {"document_id": "OTHER-TARGET"}, "TARGET_DOCUMENT_MISMATCH"),
        ("agreement_type", {"agreement_type": LegalAgreementType.USER_TERMS}, "TARGET_DOCUMENT_MISMATCH"),
        ("version", {"version": "2.0.0"}, "TARGET_DOCUMENT_MISMATCH"),
        ("content_reference", {"content_reference": "wilsy-os://legal/institutional-charter/2.0.0"}, "TARGET_DOCUMENT_MISMATCH"),
        ("content", {"content": _SOURCE.content + "\nTarget drift."}, "TARGET_DOCUMENT_MISMATCH"),
        ("effective_from", {"effective_from": datetime(2027, 1, 1, tzinfo=_UTC)}, "TARGET_DOCUMENT_MISMATCH"),
        ("title", {"title": "Other target title"}, "TARGET_DOCUMENT_MISMATCH"),
        ("jurisdiction", {"jurisdiction": "US"}, "TARGET_DOCUMENT_MISMATCH"),
        ("locale", {"locale": "en-US"}, "TARGET_DOCUMENT_MISMATCH"),
        ("created_at", {"created_at": datetime(2026, 10, 2, tzinfo=_UTC)}, "TARGET_DOCUMENT_MISMATCH"),
        ("supersedes_document_id", {"supersedes_document_id": "WRONG-SOURCE"}, "TARGET_DOCUMENT_MISMATCH"),
    ],
)
def test_target_mismatch_reaches_verifier(field: str, mutated: dict[str, Any], code: str) -> None:
    target = _document_with(_target(), **mutated)
    assert isinstance(target, LegalDocumentVersion)
    with pytest.raises(LegalCorpusApprovalAuthorityError) as caught:
        _evidence().verify_against(_SOURCE, target)
    assert caught.value.code == code


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (LegalDocumentStatus.APPROVED, "SOURCE_NOT_REVIEWED_DRAFT"),
        (LegalDocumentStatus.RETIRED, "SOURCE_NOT_REVIEWED_DRAFT"),
    ],
)
def test_non_draft_source_rejected_by_authority(status: LegalDocumentStatus, code: str) -> None:
    source = _document_with(_SOURCE, status=status)
    with pytest.raises(LegalCorpusApprovalAuthorityError) as caught:
        _evidence(source_document=source)
    assert caught.value.code == code


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (LegalDocumentStatus.DRAFT_REVIEW_REQUIRED, "TARGET_NOT_APPROVED"),
        (LegalDocumentStatus.RETIRED, "TARGET_NOT_APPROVED"),
    ],
)
def test_non_approved_target_rejected_by_authority(status: LegalDocumentStatus, code: str) -> None:
    target = _target(status=status)
    with pytest.raises(LegalCorpusApprovalAuthorityError) as caught:
        _evidence(approved_document=target)
    assert caught.value.code == code


def test_transition_matrix_rejects_same_version_and_wrong_supersession() -> None:
    same_version = _target(version=_SOURCE.version)
    wrong_supersession = _target(supersedes_document_id="OTHER-SOURCE")
    for target, code in ((same_version, "VERSION_SUCCESSION_INVALID"), (wrong_supersession, "SUPERSESSION_INVALID")):
        with pytest.raises(LegalCorpusApprovalAuthorityError) as caught:
            _evidence(approved_document=target)
        assert caught.value.code == code


@pytest.mark.parametrize("scope", [
    "PLATFORM", "platform", "TENANT", "ORGANISATION", "USER", "COMMERCIAL", None, object(),
])
def test_scope_matrix_is_closed(scope: object) -> None:
    with pytest.raises(LegalCorpusApprovalAuthorityError) as caught:
        _evidence(scope=scope)
    assert caught.value.code == "APPROVAL_SCOPE_INVALID"


@pytest.mark.parametrize("operation", [
    "LEGAL_CORPUS_DOCUMENT_APPROVAL", "LEGAL_CORPUS_DRAFT_ADMISSION", "USER_ACCEPTANCE",
    "ACKNOWLEDGEMENT", "ORGANISATION_BOUND", "arbitrary", None, object(),
])
def test_operation_matrix_is_closed(operation: object) -> None:
    with pytest.raises(LegalCorpusApprovalAuthorityError) as caught:
        _evidence(operation=operation)
    assert caught.value.code == "APPROVAL_OPERATION_INVALID"


def _fingerprint_with(**changes: Any) -> str:
    values = _kwargs()
    values.update(changes)
    values.pop("evidence_fingerprint")
    return LegalCorpusApprovalAuthorityEvidence.fingerprint_for(**values)


_SOURCE_ALT_REFERENCE = _document_with(_SOURCE, content_reference="wilsy-os://legal/institutional-charter/alternate-draft")
_SOURCE_ALT_CONTENT = _document_with(_SOURCE, content=_SOURCE.content + "\nUnreviewed drift.")
_SOURCE_ALT_VERSION = _document_with(_SOURCE, version="0.9.0-DRAFT")
_SOURCE_ALT_EFFECTIVE = _document_with(_SOURCE, effective_from=datetime(2026, 9, 18, tzinfo=_UTC))
_SOURCE_ALT_SUPERSESSION = _document_with(_SOURCE, supersedes_document_id="OLDER-SOURCE")
_TARGET_ALT_REFERENCE = _target(content_reference="wilsy-os://legal/institutional-charter/alternate-approved")
_TARGET_ALT_CONTENT = _target(content=_SOURCE.content + "\nUnapproved target drift.")
_TARGET_ALT_VERSION = _target(version="2.0.0")
_TARGET_ALT_EFFECTIVE = _target(effective_from=datetime(2027, 1, 1, tzinfo=_UTC))


@pytest.mark.parametrize(
    ("field", "changes", "expected"),
    [
        ("approval_evidence_id", {"approval_evidence_id": "approval-002"}, "DIFFERENT"),
        ("schema_version", {"schema_version": "v9.9.9"}, "SCHEMA_VERSION_INVALID"),
        ("scope", {"scope": "PLATFORM"}, "APPROVAL_SCOPE_INVALID"),
        ("operation", {"operation": "LEGAL_CORPUS_DOCUMENT_APPROVAL"}, "APPROVAL_OPERATION_INVALID"),
        ("approval_decision", {"approval_decision": "APPROVE"}, "APPROVAL_DECISION_INVALID"),
        ("approval_authority_source", {"approval_authority_source": "OTHER"}, "APPROVAL_AUTHORITY_SOURCE_INVALID"),
        ("approval_authority_mechanism", {"approval_authority_mechanism": "OTHER"}, "APPROVAL_AUTHORITY_MECHANISM_INVALID"),
        ("approval_authority_mechanism_version", {"approval_authority_mechanism_version": "v2.0.0"}, "AUTHORITY_MECHANISM_VERSION_INVALID"),
        ("human_authority_representation", {"human_authority_representation": "human-002"}, "DIFFERENT"),
        ("approval_signing_mechanism", {"approval_signing_mechanism": "OTHER"}, "SIGNING_MECHANISM_INVALID"),
        ("approval_signing_mechanism_version", {"approval_signing_mechanism_version": "v2.0.0"}, "SIGNING_MECHANISM_VERSION_INVALID"),
        ("approval_signing_key_id", {"approval_signing_key_id": "public-key-002"}, "DIFFERENT"),
        ("approval_signature_reference", {"approval_signature_reference": "signature-ref-002"}, "DIFFERENT"),
        ("approved_at", {"approved_at": datetime(2026, 9, 18, 13, tzinfo=_UTC)}, "DIFFERENT"),
        ("effective_from", {"approved_document": _TARGET_ALT_EFFECTIVE, "effective_from": _TARGET_ALT_EFFECTIVE.effective_from}, "DIFFERENT"),
        ("idempotency_key", {"idempotency_key": "approval-idempotency-002"}, "DIFFERENT"),
        ("provenance_reference", {"provenance_reference": "governance-record-002"}, "DIFFERENT"),
        ("source_document_id", {"source_document": _document_with(_SOURCE, document_id="OTHER-SOURCE")}, "DOCUMENT_ID_SUCCESSION_INVALID"),
        ("source_agreement_type", {"source_document": _document_with(_SOURCE, agreement_type=LegalAgreementType.USER_TERMS)}, "AGREEMENT_TYPE_SUCCESSION_INVALID"),
        ("source_version", {"source_document": _SOURCE_ALT_VERSION}, "DIFFERENT"),
        ("source_title", {"source_document": _document_with(_SOURCE, title="Other title")}, "DIFFERENT"),
        ("source_jurisdiction", {"source_document": _document_with(_SOURCE, jurisdiction="US")}, "DIFFERENT"),
        ("source_locale", {"source_document": _document_with(_SOURCE, locale="en-US")}, "DIFFERENT"),
        ("source_effective_from", {"source_document": _SOURCE_ALT_EFFECTIVE}, "DIFFERENT"),
        ("source_status", {"source_document": _document_with(_SOURCE, status=LegalDocumentStatus.APPROVED)}, "SOURCE_NOT_REVIEWED_DRAFT"),
        ("source_content_reference", {"source_document": _SOURCE_ALT_REFERENCE}, "DIFFERENT"),
        ("source_content", {"source_document": _SOURCE_ALT_CONTENT}, "REVIEWED_PROSE_DRIFT"),
        ("source_sha3_512", {"source_document": _SOURCE_ALT_REFERENCE}, "DIFFERENT"),
        ("source_created_at", {"source_document": _document_with(_SOURCE, created_at=datetime(2026, 9, 18, tzinfo=_UTC))}, "DIFFERENT"),
        ("source_supersedes_document_id", {"source_document": _SOURCE_ALT_SUPERSESSION}, "DIFFERENT"),
        ("approved_document_id", {"approved_document": _document_with(_target(), document_id="OTHER-TARGET")}, "DOCUMENT_ID_SUCCESSION_INVALID"),
        ("approved_agreement_type", {"approved_document": _document_with(_target(), agreement_type=LegalAgreementType.USER_TERMS)}, "AGREEMENT_TYPE_SUCCESSION_INVALID"),
        ("approved_version", {"approved_document": _TARGET_ALT_VERSION}, "DIFFERENT"),
        ("approved_title", {"approved_document": _document_with(_target(), title="Other target title")}, "DIFFERENT"),
        ("approved_jurisdiction", {"approved_document": _document_with(_target(), jurisdiction="US")}, "DIFFERENT"),
        ("approved_locale", {"approved_document": _document_with(_target(), locale="en-US")}, "DIFFERENT"),
        ("approved_effective_from", {"approved_document": _TARGET_ALT_EFFECTIVE, "effective_from": _TARGET_ALT_EFFECTIVE.effective_from}, "DIFFERENT"),
        ("approved_status", {"approved_document": _target(status=LegalDocumentStatus.RETIRED)}, "TARGET_NOT_APPROVED"),
        ("approved_content_reference", {"approved_document": _TARGET_ALT_REFERENCE}, "DIFFERENT"),
        ("approved_content", {"approved_document": _TARGET_ALT_CONTENT}, "REVIEWED_PROSE_DRIFT"),
        ("approved_sha3_512", {"approved_document": _TARGET_ALT_REFERENCE}, "DIFFERENT"),
        ("approved_created_at", {"approved_document": _document_with(_target(), created_at=datetime(2026, 10, 2, tzinfo=_UTC))}, "DIFFERENT"),
        ("approved_supersedes_document_id", {"approved_document": _target(supersedes_document_id="WRONG-SOURCE")}, "SUPERSESSION_INVALID"),
    ],
)
def test_fingerprint_field_matrix(field: str, changes: dict[str, Any], expected: str) -> None:
    if expected == "DIFFERENT":
        assert _fingerprint_with(**changes) != _evidence().evidence_fingerprint, field
        return
    with pytest.raises(LegalCorpusApprovalAuthorityError) as caught:
        _fingerprint_with(**changes)
    assert caught.value.code == expected, field


@pytest.mark.parametrize("changes", [
    {"approval_evidence_id": "approval-tampered"},
    {"human_authority_representation": "human-tampered"},
    {"approval_signing_key_id": "key-tampered"},
    {"approval_signature_reference": "signature-tampered"},
    {"source_document": _SOURCE_ALT_VERSION},
    {"approved_document": _TARGET_ALT_VERSION},
    {"approved_at": datetime(2026, 9, 18, 13, tzinfo=_UTC)},
    {"idempotency_key": "idempotency-tampered"},
    {"provenance_reference": "provenance-tampered"},
])
def test_reusing_old_fingerprint_after_semantic_change_rejects(changes: dict[str, Any]) -> None:
    values = _kwargs()
    original_fingerprint = values["evidence_fingerprint"]
    values.update(changes)
    values["evidence_fingerprint"] = original_fingerprint
    with pytest.raises(LegalCorpusApprovalAuthorityError) as caught:
        LegalCorpusApprovalAuthorityEvidence(**values)
    assert caught.value.code == "EVIDENCE_FINGERPRINT_MISMATCH"


def test_fingerprint_is_deterministic_complete_and_tamper_evident() -> None:
    first = _evidence()
    second = _evidence()
    assert first.evidence_fingerprint == second.evidence_fingerprint
    assert first.to_document() == second.to_document()
    assert first.to_document()["approved_at"].endswith("+00:00")
    with pytest.raises(LegalCorpusApprovalAuthorityError, match="EVIDENCE_FINGERPRINT_MISMATCH"):
        LegalCorpusApprovalAuthorityEvidence(**{**_kwargs(), "evidence_fingerprint": "0" * 128})
    changed = _kwargs(idempotency_key="approval-idempotency-002")
    assert changed["evidence_fingerprint"] != first.evidence_fingerprint


def test_aware_non_utc_normalizes_and_naive_rejects() -> None:
    offset = timezone(timedelta(hours=2))
    evidence = _evidence(approved_at=datetime(2026, 9, 18, 14, 0, tzinfo=offset))
    assert evidence.approved_at == _APPROVED_AT
    with pytest.raises(LegalCorpusApprovalAuthorityError, match="APPROVED_AT_INVALID"):
        _evidence(approved_at=datetime(2026, 9, 18, 12, 0))


def test_equivalent_utc_offsets_have_identical_fingerprints() -> None:
    utc = _evidence()
    plus_two = _evidence(
        approved_at=datetime(2026, 9, 18, 14, 0, tzinfo=timezone(timedelta(hours=2))),
        approved_document=_target(effective_from=datetime(2026, 10, 1, 2, 0, tzinfo=timezone(timedelta(hours=2)))),
        effective_from=datetime(2026, 10, 1, 2, 0, tzinfo=timezone(timedelta(hours=2))),
    )
    minus_five = _evidence(
        approved_at=datetime(2026, 9, 18, 7, 0, tzinfo=timezone(timedelta(hours=-5))),
        approved_document=_target(effective_from=datetime(2026, 9, 30, 19, 0, tzinfo=timezone(timedelta(hours=-5)))),
        effective_from=datetime(2026, 9, 30, 19, 0, tzinfo=timezone(timedelta(hours=-5))),
    )
    assert utc.evidence_fingerprint == plus_two.evidence_fingerprint == minus_five.evidence_fingerprint
    with pytest.raises(LegalCorpusApprovalAuthorityError, match="APPROVED_AT_INVALID"):
        _evidence(approved_at="2026-09-18T12:00:00Z")


@pytest.mark.parametrize("field", [
    "approval_evidence_id", "schema_version", "human_authority_representation",
    "approval_signing_key_id", "approval_signature_reference", "idempotency_key", "provenance_reference",
])
@pytest.mark.parametrize("value", ["", "   ", "\n", "\r", "\t", "\x00", "\x1f", "\x7f", "x" * 513])
def test_bounded_authority_text_rejects_controls_and_overflow(field: str, value: str) -> None:
    with pytest.raises(LegalCorpusApprovalAuthorityError):
        _evidence(**{field: value})


def test_serialization_contains_primitives_and_no_tenant_or_persistence_behavior() -> None:
    evidence = _evidence()
    document = evidence.to_document()
    repeat = evidence.to_document()
    expected_keys = {
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
    assert set(document) == expected_keys
    assert document == repeat
    original = document["approval_evidence_id"]
    document["approval_evidence_id"] = "mutated-return"
    assert evidence.approval_evidence_id == original
    assert evidence.to_document()["approval_evidence_id"] == original
    assert all(not isinstance(value, (datetime, LegalDocumentVersion, StrEnum)) for value in document.values())
    assert "tenant_id" not in document and "principal_id" not in document
    source_path = Path(__file__).parents[2] / "tools/eos/legal_operations/domain/legal_corpus_approval_authority.py"
    tree = ast.parse(source_path.read_text())
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    imported = " ".join(ast.unparse(node) for node in imports)
    for forbidden in ("pymongo", "kernel.db", "LegalDocumentRegistry", "LegalAcceptanceRegistry", "requests", "httpx"):
        assert forbidden not in imported
    function_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert not function_names.intersection({"verify_signature", "generate_private_key", "sign"})
    assert "cryptography" not in imported


# ARTIFACT: test_legal_corpus_approval_authority.py
# VERSION: v1.1.0-R1D-B0F-B4-R9B-P2-R1-C1-LEGAL-CORPUS-APPROVAL-AUTHORITY-CERT
# AUTHORITY BOUNDARY: direct unit semantics only; no production approval occurs
# TENANT POSTURE: no tenant/principal evidence is created
# FAIL-CLOSED POSTURE: invalid and divergent values must fail
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
