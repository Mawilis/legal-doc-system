"""Direct certificate for the six-document WILSY OS platform draft corpus.

TITLE: WILSY OS Required Platform Legal Corpus Certificate
VERSION: v1.1.2-R1D-B0F-R9B-P7-A1-R2-PRODUCTION-CORPUS-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the immutable Charter source plus five substantive,
         review-required platform legal-document drafts without provisioning,
         approval, acceptance, signing, or commercial execution authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_production_legal_corpus.py
COLLABORATION / OWNERSHIP: Direct certificate for production_legal_corpus and
                            its immutable legal-document domain contract.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.1.2 adds bounded presentation-level lexical normalization for
           semantic boundary assertions while preserving the repaired
           non-approval expectation and no-persistence boundary.
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


def test_public_api_is_exact_and_repeatable() -> None:
    """The explicit API exposes only immutable corpus values and pure getters."""
    assert set(corpus.__all__) == {
        "AUTHORING_TIMESTAMP", "DRAFT_AUTHORING_TIMESTAMP", "CHARTER_CONTENT",
        "CONTENT_REFERENCE", "DOCUMENT_ID", "DOCUMENT_VERSION",
        "INSTITUTIONAL_CHARTER_DRAFT", "USER_TERMS_CONTENT", "USER_TERMS_DRAFT",
        "ACCEPTABLE_USE_CONTENT", "ACCEPTABLE_USE_DRAFT", "PRIVACY_NOTICE_CONTENT",
        "PRIVACY_NOTICE_DRAFT", "AI_ASSISTANCE_NOTICE_CONTENT", "AI_ASSISTANCE_NOTICE_DRAFT",
        "ADMIN_RESPONSIBILITY_NOTICE_CONTENT", "ADMIN_RESPONSIBILITY_NOTICE_DRAFT",
        "JURISDICTION", "LOCALE", "PLATFORM_LEGAL_CORPUS_DRAFTS", "VERSION",
        "get_acceptable_use_draft", "get_admin_responsibility_notice_draft",
        "get_ai_assistance_notice_draft", "get_institutional_charter_draft",
        "get_privacy_notice_draft", "get_user_terms_draft",
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
# VERSION: v1.1.2-R1D-B0F-R9B-P7-A1-R2-PRODUCTION-CORPUS-CERT
# AUTHORITY BOUNDARY: direct draft-corpus evidence only; no approval or persistence
# TENANT POSTURE: platform corpus inspection only; no tenant acceptance state
# FAIL-CLOSED POSTURE: identity, digest, lifecycle, text, and authority drift fail
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
