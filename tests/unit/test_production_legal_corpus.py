"""Direct certificate for the WILSY OS Institutional Charter draft.

TITLE: WILSY OS Production Legal Corpus Certificate
VERSION: v1.0.0-R1D-B0F-B4-R8B-PRODUCTION-CORPUS-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves the single authored Institutional Charter value is immutable,
         deterministic, substantive, and explicitly non-authoritative until
         a separate governed review and persistence workflow approves it.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_production_legal_corpus.py
COLLABORATION / OWNERSHIP: Direct certificate for the production corpus
                            draft and its legal-document domain contract.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-R8B adds direct source, digest, text-boundary, and
           anti-authority certification without database or acceptance writes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: The platform-level draft has no tenant acceptance state;
                 tenant scope begins only in the separate acceptance service.
AUTHORITY BOUNDARY: Certificate evidence only; draft text grants no approval,
                    acceptance, signature, commercial, or execution authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Any drift in identity, digest, lifecycle, or authority
                     boundary fails the certificate.
"""
from __future__ import annotations

import ast
import inspect
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any

from tools.eos.legal_operations import production_legal_corpus as corpus
from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
    canonical_document_digest,
)


EXPECTED_ID = "WILSY-OS-INSTITUTIONAL-CHARTER"
EXPECTED_VERSION = "1.0.0-DRAFT"
EXPECTED_TITLE = "WILSY OS Institutional Charter"
EXPECTED_JURISDICTION = "ZA"
EXPECTED_LOCALE = "en-ZA"


def _charter() -> LegalDocumentVersion:
    value = corpus.get_institutional_charter_draft()
    assert isinstance(value, LegalDocumentVersion)
    return value


def _source() -> str:
    return inspect.getsource(corpus)


def test_exports_exactly_one_immutable_institutional_charter_draft() -> None:
    """The production module exposes one server-owned draft and no corpus set."""
    exported_documents = [
        value for value in vars(corpus).values() if isinstance(value, LegalDocumentVersion)
    ]
    assert exported_documents == [corpus.INSTITUTIONAL_CHARTER_DRAFT]
    assert corpus.INSTITUTIONAL_CHARTER_DRAFT.agreement_type is LegalAgreementType.INSTITUTIONAL_CHARTER
    assert corpus.DOCUMENT_ID == EXPECTED_ID
    assert corpus.DOCUMENT_VERSION == EXPECTED_VERSION
    assert _charter().document_id == EXPECTED_ID


def test_charter_identity_lifecycle_and_provenance_are_exact() -> None:
    """Identity, status, jurisdiction, reference, and draft boundary are fixed."""
    value = _charter()
    assert value.version == EXPECTED_VERSION
    assert value.status is LegalDocumentStatus.DRAFT_REVIEW_REQUIRED
    assert value.jurisdiction == EXPECTED_JURISDICTION
    assert value.locale == EXPECTED_LOCALE
    assert value.title == EXPECTED_TITLE
    assert value.content_reference == corpus.CONTENT_REFERENCE
    assert value.content_reference == "wilsy-os://legal/institutional-charter/1.0.0-draft"
    assert value.content_reference.strip()
    assert value.supersedes_document_id is None
    assert isinstance(value.effective_from, datetime)
    assert value.effective_from.tzinfo is not None and value.effective_from.utcoffset() is not None
    assert isinstance(value.created_at, datetime)
    assert value.created_at.tzinfo is not None and value.created_at.utcoffset() is not None
    assert value.status is not LegalDocumentStatus.APPROVED


def test_charter_digest_and_serialization_are_deterministic() -> None:
    """The stored SHA3-512 covers exactly the canonical content/reference payload."""
    first = _charter()
    second = corpus.get_institutional_charter_draft()
    assert first is second
    assert first.sha3_512 == canonical_document_digest(first.content, first.content_reference)
    assert len(first.sha3_512) == 128
    assert first.sha3_512 == first.sha3_512.lower()
    assert all(character in "0123456789abcdef" for character in first.sha3_512)
    assert first.to_document() == second.to_document()
    assert first.to_document() is not second.to_document()


def test_charter_text_preserves_constitutional_semantic_boundaries() -> None:
    """Targeted concepts protect the authored Charter without prose snapshotting."""
    text = " ".join(corpus.CHARTER_CONTENT.casefold().split())
    required_concepts = (
        "purpose and institutional mission",
        "human accountability",
        "model output is not legal advice",
        "observed fact",
        "derived signal",
        "ai inference",
        "recommendation",
        "authorization",
        "execution",
        "settlement",
        "tenant isolation and stewardship",
        "evidence integrity and forensic posture",
        "governance and lifecycle",
        "security and privacy stewardship",
        "responsible ai assistance",
        "commercial and financial separation",
        "amendment and version succession",
        "draft status and institutional boundary",
        "kennel eos",
    )
    assert len(corpus.CHARTER_CONTENT.encode("utf-8")) > 5_000
    for concept in required_concepts:
        assert concept in text
    assert "draft_review_required" in text
    assert "has not been approved" in text


def test_source_api_has_no_persistence_or_authority_constructors() -> None:
    """Source-level imports/calls prove import and access remain side-effect free."""
    source_path = Path(corpus.__file__ or "")
    assert source_path.name == "production_legal_corpus.py"
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
    forbidden_constructors = {
        "LegalAcceptanceEvidence",
        "LegalDocumentRegistry",
        "LegalAcceptanceRegistry",
        "MongoClient",
        "Quotation",
        "Payment",
        "Settlement",
    }
    assert forbidden_constructors.isdisjoint(called_names)


def test_source_exports_no_approval_acceptance_or_commercial_authority() -> None:
    """The public API is limited to draft constants, one value, and a getter."""
    public_names = set(corpus.__all__)
    assert public_names == {
        "AUTHORING_TIMESTAMP",
        "CHARTER_CONTENT",
        "CONTENT_REFERENCE",
        "DOCUMENT_ID",
        "DOCUMENT_VERSION",
        "INSTITUTIONAL_CHARTER_DRAFT",
        "JURISDICTION",
        "LOCALE",
        "VERSION",
        "get_institutional_charter_draft",
    }
    assert not any(name in public_names for name in ("APPROVED_CHARTER", "ACCEPTANCE_EVIDENCE", "REVIEW_EVIDENCE"))
    assert not any(
        isinstance(value, LegalDocumentVersion) and value.status is LegalDocumentStatus.APPROVED
        for value in vars(corpus).values()
    )


def test_imported_module_is_not_bound_to_a_database_object() -> None:
    """The module namespace contains no Mongo/client/database object or registry."""
    namespace: Mapping[str, Any] = vars(corpus)
    assert not any(
        isinstance(value, ModuleType) and ("pymongo" in value.__name__.casefold() or "registry" in value.__name__.casefold())
        for value in namespace.values()
    )
    assert "LegalAcceptanceEvidence" not in namespace


# ARTIFACT: test_production_legal_corpus.py
# VERSION: v1.0.0-R1D-B0F-B4-R8B-PRODUCTION-CORPUS-CERT
# AUTHORITY BOUNDARY: direct certificate evidence only; no draft approval or persistence
# TENANT POSTURE: platform corpus inspection only; no tenant acceptance state
# FAIL-CLOSED POSTURE: identity, digest, lifecycle, text boundaries, and authority drift fail
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
