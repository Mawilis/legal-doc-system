"""Direct certificate for the historical and reviewed-successor platform corpus.

TITLE: WILSY OS Required Platform Legal Corpus Certificate
VERSION: v1.4.1-R9B-P7-A3-R2-R1-REVIEWED-SUCCESSOR-RUNTIME-CATALOG-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the immutable Charter source plus five substantive,
         review-required platform legal-document drafts without provisioning,
         approval, acceptance, signing, or commercial execution authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_production_legal_corpus.py
COLLABORATION / OWNERSHIP: Direct certificate for production_legal_corpus and
                            its immutable legal-document domain contract.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.4.1 repairs the resolver ambiguity/non-draft certificate
           fixture to construct domain-valid LegalDocumentVersion values
           without serialized enum primitive rehydration; production runtime
           semantics are unchanged.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Platform drafts only; tenant acceptance remains separate.
AUTHORITY BOUNDARY: Draft evidence only; no review, approval, signature,
                    acceptance, organisation binding, or execution authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Identity, digest, lifecycle, substantive text, API, and
                     authority drift fail the certificate.
"""
from __future__ import annotations

import ast
from dataclasses import replace
import inspect
import unicodedata
from collections.abc import Mapping
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from tools.eos.legal_operations import production_legal_corpus as corpus
from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
    canonical_document_digest,
)


CHARTER_ID = "WILSY-OS-INSTITUTIONAL-CHARTER"
CHARTER_DIGEST = "c67cab37c2c8bbb38ecdb44f2295c46e39b6f01d25cb618a8c9a6a7dc5194f69608cbeacc5f7c00166cde0ae6d620b8d5b22555f46cfd9faa06b5c8a53bfaf6a"
EXPECTED = (
    (LegalAgreementType.INSTITUTIONAL_CHARTER, CHARTER_ID, "WILSY OS Institutional Charter", "wilsy-os://legal/institutional-charter/1.0.0-draft", "CHARTER_CONTENT"),
    (LegalAgreementType.USER_TERMS, "WILSY-OS-USER-TERMS", "WILSY OS User Terms", "wilsy-os://legal/user-terms/1.0.0-draft", "USER_TERMS_CONTENT"),
    (LegalAgreementType.ACCEPTABLE_USE, "WILSY-OS-ACCEPTABLE-USE", "WILSY OS Acceptable Use Policy", "wilsy-os://legal/acceptable-use/1.0.0-draft", "ACCEPTABLE_USE_CONTENT"),
    (LegalAgreementType.PRIVACY_NOTICE, "WILSY-OS-PRIVACY-NOTICE", "WILSY OS Privacy Notice", "wilsy-os://legal/privacy-notice/1.0.0-draft", "PRIVACY_NOTICE_CONTENT"),
    (LegalAgreementType.AI_ASSISTANCE_NOTICE, "WILSY-OS-AI-ASSISTANCE-NOTICE", "WILSY OS AI Assistance Notice", "wilsy-os://legal/ai-assistance-notice/1.0.0-draft", "AI_ASSISTANCE_NOTICE_CONTENT"),
    (LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE, "WILSY-OS-ADMIN-RESPONSIBILITY-NOTICE", "WILSY OS Administrator Responsibility Notice", "wilsy-os://legal/admin-responsibility-notice/1.0.0-draft", "ADMIN_RESPONSIBILITY_NOTICE_CONTENT"),
)
NEW_FAMILIES = tuple(item[0] for item in EXPECTED[1:])
PLACEHOLDER_PATTERNS = ("[COMPANY NAME]", "[TBD]", "[ADDRESS]", "[EMAIL]", "TODO", "FIXME")
SUCCESSOR_EXPECTED = (
    (LegalAgreementType.USER_TERMS, "WILSY-OS-USER-TERMS", "wilsy-os://legal/user-terms/1.1.0-draft", "USER_TERMS_REVIEWED_SUCCESSOR_CONTENT"),
    (LegalAgreementType.ACCEPTABLE_USE, "WILSY-OS-ACCEPTABLE-USE", "wilsy-os://legal/acceptable-use/1.1.0-draft", "ACCEPTABLE_USE_REVIEWED_SUCCESSOR_CONTENT"),
    (LegalAgreementType.PRIVACY_NOTICE, "WILSY-OS-PRIVACY-NOTICE", "wilsy-os://legal/privacy-notice/1.1.0-draft", "PRIVACY_NOTICE_REVIEWED_SUCCESSOR_CONTENT"),
    (LegalAgreementType.AI_ASSISTANCE_NOTICE, "WILSY-OS-AI-ASSISTANCE-NOTICE", "wilsy-os://legal/ai-assistance-notice/1.1.0-draft", "AI_ASSISTANCE_NOTICE_REVIEWED_SUCCESSOR_CONTENT"),
    (LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE, "WILSY-OS-ADMIN-RESPONSIBILITY-NOTICE", "wilsy-os://legal/admin-responsibility-notice/1.1.0-draft", "ADMIN_RESPONSIBILITY_NOTICE_REVIEWED_SUCCESSOR_CONTENT"),
)
SUCCESSOR_FORBIDDEN_PHRASES = (
    "DRAFT_REVIEW_REQUIRED",
    "not approved",
    "has not been approved",
    "have not been approved",
    "this draft",
    "this policy is a draft",
    "this notice is a draft",
    "awaiting approval",
    "future approved",
    "later approved",
)


def _normalize_semantic_text(value: str) -> str:
    """Normalize typography only for bounded semantic phrase assertions.

    This certificate preserves every legal token and does not perform fuzzy
    matching, stemming, synonym expansion, or arbitrary punctuation removal.
    Unicode compatibility normalization, case folding, dash-to-space
    conversion, and whitespace collapse make presentation-level variants such
    as ``least-privilege`` and ``least privilege`` compare as one concept.
    """
    normalized = unicodedata.normalize("NFKC", value).casefold()
    normalized = normalized.translate(
        str.maketrans({character: " " for character in "‐‑‒–—―-"})
    )
    return " ".join(normalized.split())


def test_exactly_six_platform_drafts_and_one_family_each() -> None:
    """The public immutable collection contains exactly the required families."""
    drafts = corpus.PLATFORM_LEGAL_CORPUS_DRAFTS
    assert isinstance(drafts, tuple)
    assert len(drafts) == 6
    assert all(isinstance(value, LegalDocumentVersion) for value in drafts)
    assert tuple(value.agreement_type for value in drafts) == tuple(item[0] for item in EXPECTED)
    assert len({value.agreement_type for value in drafts}) == 6
    assert len({value.document_id for value in drafts}) == 6
    assert len({value.content_reference for value in drafts}) == 6


def test_exact_identity_lifecycle_and_digests() -> None:
    """Every source identity is fixed, draft-only, ZA/en-ZA, and hash-bound."""
    for value, expected in zip(corpus.PLATFORM_LEGAL_CORPUS_DRAFTS, EXPECTED, strict=True):
        family, document_id, title, reference, content_name = expected
        assert value.agreement_type is family
        assert value.document_id == document_id
        assert value.title == title
        assert value.version == "1.0.0-DRAFT"
        assert value.status is LegalDocumentStatus.DRAFT_REVIEW_REQUIRED
        assert value.jurisdiction == "ZA"
        assert value.locale == "en-ZA"
        assert value.content_reference == reference
        assert value.supersedes_document_id is None
        assert value.sha3_512 == canonical_document_digest(value.content, reference)
        assert len(value.sha3_512) == 128 and value.sha3_512 == value.sha3_512.lower()
        assert getattr(corpus, content_name) == value.content
        assert len(value.content.encode("utf-8")) > 1_000
        assert value.effective_from.tzinfo is not None and value.effective_from.utcoffset() is not None
        assert value.created_at.tzinfo is not None and value.created_at.utcoffset() is not None


def test_charter_source_identity_and_content_digest_are_unchanged() -> None:
    """The approved Charter predecessor remains the exact historical draft source."""
    charter = corpus.INSTITUTIONAL_CHARTER_DRAFT
    assert charter.document_id == CHARTER_ID
    assert charter.version == "1.0.0-DRAFT"
    assert charter.status is LegalDocumentStatus.DRAFT_REVIEW_REQUIRED
    assert charter.content_reference == "wilsy-os://legal/institutional-charter/1.0.0-draft"
    assert charter.sha3_512 == CHARTER_DIGEST
    assert charter.sha3_512 == canonical_document_digest(charter.content, charter.content_reference)
    assert corpus.get_institutional_charter_draft() is charter
    assert charter.agreement_type is LegalAgreementType.INSTITUTIONAL_CHARTER


def test_new_drafts_share_one_explicit_authorship_timestamp_only() -> None:
    """The five new drafts have one aware authorship instant distinct from Charter history."""
    new_drafts = corpus.PLATFORM_LEGAL_CORPUS_DRAFTS[1:]
    assert all(value.created_at == corpus.DRAFT_AUTHORING_TIMESTAMP for value in new_drafts)
    assert all(value.effective_from == corpus.DRAFT_AUTHORING_TIMESTAMP for value in new_drafts)
    assert corpus.DRAFT_AUTHORING_TIMESTAMP != corpus.AUTHORING_TIMESTAMP
    assert corpus.DRAFT_AUTHORING_TIMESTAMP.tzinfo is not None


def test_each_family_has_substantive_targeted_boundaries() -> None:
    """Targeted concepts certify that each text is substantive without snapshots."""
    required = {
        LegalAgreementType.USER_TERMS: ("authenticated", "tenant", "organisation-binding", "ai", "financial", "DRAFT_REVIEW_REQUIRED"),
        LegalAgreementType.ACCEPTABLE_USE: ("lawful", "malware", "tenant isolation", "impersonate", "vulnerability", "DRAFT_REVIEW_REQUIRED"),
        LegalAgreementType.PRIVACY_NOTICE: ("POPIA", "personal", "purposes", "retention", "cross-border", "DRAFT_REVIEW_REQUIRED"),
        LegalAgreementType.AI_ASSISTANCE_NOTICE: ("AI INFERENCE", "legal advice", "human review", "provider", "tenant", "DRAFT_REVIEW_REQUIRED"),
        LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE: ("least privilege", "SUPER_ADMIN", "tenant isolation", "evidence", "Kennel EOS", "DRAFT_REVIEW_REQUIRED"),
    }
    for value in corpus.PLATFORM_LEGAL_CORPUS_DRAFTS[1:]:
        text = _normalize_semantic_text(value.content)
        assert all(_normalize_semantic_text(token) in text for token in required[value.agreement_type])
        assert _normalize_semantic_text("not been approved") in text
        assert not any(_normalize_semantic_text(pattern) in text for pattern in PLACEHOLDER_PATTERNS)


def test_corpus_and_documents_are_immutable() -> None:
    """Tuple and frozen legal-document values cannot be changed by callers."""
    with pytest.raises(TypeError):
        corpus.PLATFORM_LEGAL_CORPUS_DRAFTS[0] = corpus.USER_TERMS_DRAFT  # type: ignore[index]
    with pytest.raises((AttributeError, TypeError)):
        corpus.USER_TERMS_DRAFT.version = "2.0.0"  # type: ignore[misc]
    assert corpus.get_user_terms_draft() is corpus.USER_TERMS_DRAFT
    assert corpus.get_acceptable_use_draft() is corpus.ACCEPTABLE_USE_DRAFT
    assert corpus.get_privacy_notice_draft() is corpus.PRIVACY_NOTICE_DRAFT
    assert corpus.get_ai_assistance_notice_draft() is corpus.AI_ASSISTANCE_NOTICE_DRAFT
    assert corpus.get_admin_responsibility_notice_draft() is corpus.ADMIN_RESPONSIBILITY_NOTICE_DRAFT
    assert corpus.get_institutional_charter_draft() is corpus.INSTITUTIONAL_CHARTER_DRAFT


def test_no_approved_commercial_or_authority_value_is_authored() -> None:
    """The source contains no approved object, commercial family, or authority value."""
    assert all(value.status is not LegalDocumentStatus.APPROVED for value in corpus.PLATFORM_LEGAL_CORPUS_DRAFTS)
    assert all(value.agreement_type in (LegalAgreementType.INSTITUTIONAL_CHARTER, *NEW_FAMILIES) for value in corpus.PLATFORM_LEGAL_CORPUS_DRAFTS)
    source = inspect.getsource(corpus).casefold()
    assert "master_subscription_agreement" not in source
    assert "order_form" not in source
    assert "data_processing_agreement" not in source
    assert "security_sla_schedule" not in source


def test_historical_five_drafts_remain_exactly_preserved() -> None:
    """The provisioned 1.0.0-DRAFT values cannot drift during succession authoring."""
    expected_digests = (
        "61714295aba8625bb32a8482de7436e58699133c1ca1b476742e3fae0ad3ac1657f51b64d2603a0c152de6e91c8b5839cb634b9a0169b007fec1aaa50c848b0a",
        "a76498f4b45468e72a4e17216d0f33cf50cf933ea41aef74e3c8e3dd84ac86c2333bc4287d5bce7ce7eec3a00775f6bfe7b02edb363206ddef7a55257b509e96",
        "eba0ec831b8cb38e0faf0dae6076188c63802aff011493b46b4854fc8be33721f336d909c8dea230aad4242105219424a4bb409437f2a4e4c9f0947ed1a911c1",
        "e11b4839099bdc1f83ac83dabeaa6f20e0373802468fbbac1e8381ca1b322708e0f08b0e7ce85eb5295ff05572f75c5038159b5d72aa643bcd2ef242283d56cc",
        "df2ff9a63ed47da56caf318667a69c965a8dcbc68dcd8454c78804568a044d467df358217dfcee989aeb0d42e141a43274ec5f4427f4badde71e841bbc0571e2",
    )
    historical = corpus.PLATFORM_LEGAL_CORPUS_DRAFTS[1:]
    assert len(historical) == 5
    assert tuple(value.version for value in historical) == ("1.0.0-DRAFT",) * 5
    assert tuple(value.sha3_512 for value in historical) == expected_digests


def test_reviewed_successor_tuple_and_identity_are_exact() -> None:
    """The five successor values are immutable source succession only."""
    successors = corpus.PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS
    historical = corpus.PLATFORM_LEGAL_CORPUS_DRAFTS[1:]
    assert isinstance(successors, tuple)
    assert len(successors) == 5
    assert tuple(value.agreement_type for value in successors) == tuple(item[0] for item in SUCCESSOR_EXPECTED)
    assert len({value.document_id for value in successors}) == 5
    assert len({(value.document_id, value.version) for value in successors}) == 5
    for old, successor, expected in zip(historical, successors, SUCCESSOR_EXPECTED, strict=True):
        family, document_id, reference, content_name = expected
        assert successor.agreement_type is family
        assert successor.document_id == document_id == old.document_id
        assert successor.version == "1.1.0-DRAFT"
        assert successor.status is LegalDocumentStatus.DRAFT_REVIEW_REQUIRED
        assert successor.jurisdiction == "ZA"
        assert successor.locale == "en-ZA"
        assert successor.content_reference == reference
        assert successor.supersedes_document_id == old.document_id
        assert successor.content_reference != old.content_reference
        assert successor.content != old.content
        assert successor.sha3_512 != old.sha3_512
        assert successor.sha3_512 == canonical_document_digest(successor.content, reference)
        assert getattr(corpus, content_name) == successor.content
        assert successor.created_at == corpus.REVIEWED_SUCCESSOR_AUTHORING_TIMESTAMP
        assert successor.effective_from == corpus.REVIEWED_SUCCESSOR_AUTHORING_TIMESTAMP
        assert successor.created_at > old.created_at


def test_reviewed_successors_are_lifecycle_neutral_and_approval_preservable() -> None:
    """Successor prose does not describe its current metadata lifecycle."""
    for successor in corpus.PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS:
        normalized = _normalize_semantic_text(successor.content)
        assert all(_normalize_semantic_text(phrase) not in normalized for phrase in SUCCESSOR_FORBIDDEN_PHRASES)
        assert "approved" not in normalized
        assert "organisation-binding authority" in normalized or "organisation binding" in normalized
        assert len(successor.content.encode("utf-8")) > 1_000


def test_reviewed_successors_are_immutable_and_getters_are_repeatable() -> None:
    """Successor values and their exported getters remain frozen and pure."""
    with pytest.raises(TypeError):
        corpus.PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS[0] = corpus.USER_TERMS_DRAFT  # type: ignore[index]
    for successor, getter in zip(
        corpus.PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS,
        (
            corpus.get_user_terms_reviewed_successor_draft,
            corpus.get_acceptable_use_reviewed_successor_draft,
            corpus.get_privacy_notice_reviewed_successor_draft,
            corpus.get_ai_assistance_notice_reviewed_successor_draft,
            corpus.get_admin_responsibility_notice_reviewed_successor_draft,
        ),
        strict=True,
    ):
        assert getter() is successor
        with pytest.raises((AttributeError, TypeError)):
            successor.version = "2.0.0"  # type: ignore[misc]


def test_canonical_runtime_catalog_and_exact_resolver_cover_all_eleven_values() -> None:
    """The source-owned resolver separates historical and successor versions."""
    catalog = corpus.PLATFORM_LEGAL_CORPUS_CANONICAL_DRAFTS
    assert isinstance(catalog, tuple)
    assert len(catalog) == 11
    assert len({(value.document_id, value.version) for value in catalog}) == 11
    for value in catalog:
        assert corpus.resolve_platform_legal_corpus_draft(value.document_id, value.version) is value
    for historical, successor in zip(corpus.PLATFORM_LEGAL_CORPUS_DRAFTS[1:], corpus.PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS, strict=True):
        assert corpus.resolve_platform_legal_corpus_draft(historical.document_id, "1.0.0-DRAFT") is historical
        assert corpus.resolve_platform_legal_corpus_draft(successor.document_id, "1.1.0-DRAFT") is successor
    with pytest.raises(corpus.LegalCorpusCanonicalDraftResolutionError, match="CANONICAL_DOCUMENT_UNKNOWN"):
        corpus.resolve_platform_legal_corpus_draft("WILSY-OS-USER-TERMS", "9.9.9-DRAFT")


def test_canonical_runtime_resolver_rejects_ambiguity_and_non_draft_without_io(monkeypatch: pytest.MonkeyPatch) -> None:
    """Forced source ambiguity and lifecycle drift fail closed without authority or I/O."""
    original = corpus.PLATFORM_LEGAL_CORPUS_CANONICAL_DRAFTS
    duplicate = original + (original[0],)
    monkeypatch.setattr(corpus, "PLATFORM_LEGAL_CORPUS_CANONICAL_DRAFTS", duplicate)
    with pytest.raises(corpus.LegalCorpusCanonicalDraftResolutionError, match="CANONICAL_DOCUMENT_DUPLICATE"):
        corpus.resolve_platform_legal_corpus_draft(original[0].document_id, original[0].version)
    non_draft = replace(original[0], status=LegalDocumentStatus.APPROVED)
    monkeypatch.setattr(corpus, "PLATFORM_LEGAL_CORPUS_CANONICAL_DRAFTS", (non_draft, *original[1:]))
    with pytest.raises(corpus.LegalCorpusCanonicalDraftResolutionError, match="NON_DRAFT_CANONICAL_SOURCE"):
        corpus.resolve_platform_legal_corpus_draft(original[0].document_id, original[0].version)


def test_public_api_is_exact_and_repeatable() -> None:
    """The explicit API exposes only immutable corpus values and pure getters."""
    assert set(corpus.__all__) == {
        "AUTHORING_TIMESTAMP", "DRAFT_AUTHORING_TIMESTAMP", "REVIEWED_SUCCESSOR_AUTHORING_TIMESTAMP", "CHARTER_CONTENT",
        "CONTENT_REFERENCE", "DOCUMENT_ID", "DOCUMENT_VERSION",
        "INSTITUTIONAL_CHARTER_DRAFT", "USER_TERMS_CONTENT", "USER_TERMS_DRAFT",
        "ACCEPTABLE_USE_CONTENT", "ACCEPTABLE_USE_DRAFT", "PRIVACY_NOTICE_CONTENT",
        "PRIVACY_NOTICE_DRAFT", "AI_ASSISTANCE_NOTICE_CONTENT", "AI_ASSISTANCE_NOTICE_DRAFT",
        "ADMIN_RESPONSIBILITY_NOTICE_CONTENT", "ADMIN_RESPONSIBILITY_NOTICE_DRAFT",
        "USER_TERMS_REVIEWED_SUCCESSOR_CONTENT", "USER_TERMS_REVIEWED_SUCCESSOR_DRAFT",
        "ACCEPTABLE_USE_REVIEWED_SUCCESSOR_CONTENT", "ACCEPTABLE_USE_REVIEWED_SUCCESSOR_DRAFT",
        "PRIVACY_NOTICE_REVIEWED_SUCCESSOR_CONTENT", "PRIVACY_NOTICE_REVIEWED_SUCCESSOR_DRAFT",
        "AI_ASSISTANCE_NOTICE_REVIEWED_SUCCESSOR_CONTENT", "AI_ASSISTANCE_NOTICE_REVIEWED_SUCCESSOR_DRAFT",
        "ADMIN_RESPONSIBILITY_NOTICE_REVIEWED_SUCCESSOR_CONTENT", "ADMIN_RESPONSIBILITY_NOTICE_REVIEWED_SUCCESSOR_DRAFT",
        "JURISDICTION", "LOCALE", "PLATFORM_LEGAL_CORPUS_DRAFTS", "PLATFORM_LEGAL_CORPUS_CANONICAL_DRAFTS", "PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS", "LegalCorpusCanonicalDraftResolutionError", "resolve_platform_legal_corpus_draft", "VERSION",
        "get_acceptable_use_draft", "get_admin_responsibility_notice_draft",
        "get_ai_assistance_notice_draft", "get_institutional_charter_draft",
        "get_privacy_notice_draft", "get_user_terms_draft",
        "get_acceptable_use_reviewed_successor_draft",
        "get_admin_responsibility_notice_reviewed_successor_draft",
        "get_ai_assistance_notice_reviewed_successor_draft",
        "get_privacy_notice_reviewed_successor_draft",
        "get_user_terms_reviewed_successor_draft",
    }
    assert corpus.get_institutional_charter_draft().to_document() == corpus.get_institutional_charter_draft().to_document()
    assert corpus.get_user_terms_draft().to_document() == corpus.get_user_terms_draft().to_document()


def test_source_has_no_persistence_acceptance_or_approval_surface() -> None:
    """AST and namespace inspection prove authoring remains side-effect free."""
    source_path = Path(corpus.__file__ or "")
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported_modules: list[str] = []
    called_names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.append(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called_names.append(node.func.attr)
    assert not any("pymongo" in module or "registry" in module for module in imported_modules)
    assert "LegalDocumentVersion" in called_names
    assert "canonical_document_digest" in called_names
    forbidden_calls = {
        "LegalAcceptanceEvidence", "LegalDocumentRegistry", "LegalAcceptanceRegistry",
        "MongoClient", "LegalCorpusApprovalAuthorityEvidence", "LegalCorpusApprovalAuthorization",
        "Quotation", "Payment", "Settlement",
    }
    assert forbidden_calls.isdisjoint(called_names)
    namespace: Mapping[str, Any] = vars(corpus)
    assert not any(
        isinstance(value, ModuleType)
        and ("pymongo" in value.__name__.casefold() or "registry" in value.__name__.casefold())
        for value in namespace.values()
    )
    assert "LegalAcceptanceEvidence" not in namespace
    assert "LegalCorpusApprovalAuthorityEvidence" not in namespace


def test_source_does_not_use_mutable_corpus_collection() -> None:
    """The canonical six-document collection is structurally a tuple, not list/dict."""
    tree = ast.parse(Path(corpus.__file__ or "").read_text(encoding="utf-8"))
    collection_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "PLATFORM_LEGAL_CORPUS_DRAFTS"]
    assert len(collection_nodes) == 1
    assert isinstance(collection_nodes[0].value, ast.Tuple)


# ARTIFACT: test_production_legal_corpus.py
# VERSION: v1.4.1-R9B-P7-A3-R2-R1-REVIEWED-SUCCESSOR-RUNTIME-CATALOG-CERT
# AUTHORITY BOUNDARY: historical and successor draft-corpus evidence only
# TENANT POSTURE: platform corpus inspection only; no tenant acceptance state
# FAIL-CLOSED POSTURE: identity, digest, lifecycle, text, and authority drift fail
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
