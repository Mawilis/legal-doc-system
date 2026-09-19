"""Direct certificate for the R8D legal-corpus authority evidence value.

TITLE: WILSY OS Legal Corpus Provisioning Authority Certificate
VERSION: v1.0.0-R1D-B0F-B4-R8E-LEGAL-CORPUS-PROVISIONING-AUTHORITY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the exact R8D immutable PLATFORM draft-admission evidence
         contract, its canonical fingerprint, and its fail-closed source
         verification without persistence or operational authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_provisioning_authority.py
COLLABORATION / OWNERSHIP: Direct certificate for the R8D domain artifact;
                            future registry and provisioning-service gates
                            remain separate owners.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-R8E certifies constrained authority shape, semantic
           fingerprint coverage, draft-only verification, and zero side effects.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tests use opaque fixtures only and never require
                            secrets, network, or request context.
TENANT BOUNDARY: PLATFORM corpus evidence is intentionally tenant-neutral;
                 tenant/principal acceptance evidence is separate.
AUTHORITY BOUNDARY: Certificate evidence only; possession or construction of
                    this value is not legal review, approval, acceptance,
                    signature, commercial execution, or payment authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Any identity, status, source, timestamp, fingerprint, or
                     serialization drift fails the certificate.
"""
from __future__ import annotations

import ast
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from tools.eos.legal_operations import production_legal_corpus as corpus
from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
)
from tools.eos.legal_operations.domain.legal_corpus_provisioning_authority import (
    AUTHORITY_SOURCE_ID,
    AUTHORITY_SOURCE_VERSION,
    AUTHORITY_SCOPE,
    AUTHORIZED_OPERATION,
    LegalCorpusProvisioningAuthorityError,
    LegalCorpusProvisioningAuthorityEvidence,
    LegalCorpusProvisioningAuthorityScope,
    LegalCorpusProvisioningAuthoritySource,
    LegalCorpusProvisioningOperation,
)


NOW = datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc)


def _fields(**changes: Any) -> dict[str, Any]:
    document = corpus.get_institutional_charter_draft()
    values: dict[str, Any] = {
        "authority_evidence_id": "LEGAL-CORPUS-AUTH-R8E-001",
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
        "actor_representation": "deployment-job:r8e-certificate",
        "authorized_at": NOW,
        "idempotency_key": "r8e-idempotency-001",
    }
    values.update(changes)
    values["evidence_fingerprint"] = LegalCorpusProvisioningAuthorityEvidence.fingerprint_for(**values)
    return values


def _evidence(**changes: Any) -> LegalCorpusProvisioningAuthorityEvidence:
    return LegalCorpusProvisioningAuthorityEvidence(**_fields(**changes))


def _expect_code(values: dict[str, Any], code: str) -> None:
    with pytest.raises(LegalCorpusProvisioningAuthorityError, match=code) as captured:
        LegalCorpusProvisioningAuthorityEvidence(**values)
    assert captured.value.code == code


def test_authority_shape_is_platform_draft_admission_only() -> None:
    value = _evidence()
    assert AUTHORITY_SCOPE == "PLATFORM"
    assert AUTHORIZED_OPERATION == "LEGAL_CORPUS_DRAFT_ADMISSION"
    assert value.scope is LegalCorpusProvisioningAuthorityScope.PLATFORM
    assert value.operation is LegalCorpusProvisioningOperation.DRAFT_ADMISSION
    assert value.authority_source_id.value == AUTHORITY_SOURCE_ID
    assert value.authority_source_version == AUTHORITY_SOURCE_VERSION
    assert "APPROVE" not in {item.value for item in LegalCorpusProvisioningOperation}
    assert "REVIEW" not in {item.value for item in LegalCorpusProvisioningOperation}
    assert "ACCEPT" not in {item.value for item in LegalCorpusProvisioningOperation}
    assert "SIGN" not in {item.value for item in LegalCorpusProvisioningOperation}
    assert "PAYMENT" not in {item.value for item in LegalCorpusProvisioningOperation}


def test_immutable_value_rejects_mutation_and_has_no_promotion_method() -> None:
    value = _evidence()
    with pytest.raises((AttributeError, TypeError)):
        value.scope = LegalCorpusProvisioningAuthorityScope.PLATFORM  # type: ignore[misc]
    method_names = set(vars(type(value)))
    assert not any(token in name.casefold() for name in method_names for token in ("mutat", "promot", "approv", "accept", "sign"))


def test_every_authority_field_participates_in_fingerprint() -> None:
    original = _evidence()
    valid_changes = (
        ("authority_evidence_id", "LEGAL-CORPUS-AUTH-R8E-002"),
        ("source_document_id", "OTHER-DOCUMENT"),
        ("source_agreement_type", LegalAgreementType.USER_TERMS),
        ("source_version", "1.0.1-DRAFT"),
        ("source_content_reference", "wilsy-os://legal/other"),
        ("source_sha3_512", "a" * 128),
        ("actor_representation", "deployment-job:r8e-other"),
        ("authorized_at", NOW + timedelta(seconds=1)),
        ("idempotency_key", "r8e-idempotency-002"),
    )
    original_fields = _fields()
    original_fields.pop("evidence_fingerprint")
    for field, changed in valid_changes:
        changed_fields = {**original_fields, field: changed}
        assert LegalCorpusProvisioningAuthorityEvidence.fingerprint_for(**changed_fields) != original.evidence_fingerprint
    for field, changed, code in (
        ("scope", "TENANT", "AUTHORITY_SCOPE_INVALID"),
        ("operation", "APPROVE", "AUTHORIZED_OPERATION_INVALID"),
        ("source_status", LegalDocumentStatus.APPROVED, "NON_DRAFT_SOURCE_STATUS"),
        ("authority_source_id", "CALLER_INVENTED_AUTHORITY", "AUTHORITY_SOURCE_INVALID"),
        ("authority_source_version", "v9.0.0", "AUTHORITY_SOURCE_VERSION_INVALID"),
    ):
        changed_fields = {**original_fields, field: changed}
        with pytest.raises(LegalCorpusProvisioningAuthorityError, match=code):
            LegalCorpusProvisioningAuthorityEvidence.fingerprint_for(**changed_fields)


def test_fingerprint_is_sha3_canonical_and_self_exclusion_is_fail_closed() -> None:
    value = _evidence()
    fields = _fields()
    fingerprint = fields.pop("evidence_fingerprint")
    assert fingerprint == value.evidence_fingerprint
    assert len(fingerprint) == 128
    assert fingerprint == fingerprint.lower()
    assert all(character in "0123456789abcdef" for character in fingerprint)
    assert LegalCorpusProvisioningAuthorityEvidence.fingerprint_for(**fields) == fingerprint
    _expect_code({**_fields(), "evidence_fingerprint": "0" * 128}, "EVIDENCE_FINGERPRINT_MISMATCH")


def test_timezone_normalization_and_serialization_are_deterministic() -> None:
    utc = _evidence(authorized_at=NOW)
    plus_two = _evidence(authorized_at=datetime(2026, 9, 17, 14, 0, tzinfo=timezone(timedelta(hours=2))))
    assert plus_two.authorized_at == utc.authorized_at
    assert plus_two.evidence_fingerprint == utc.evidence_fingerprint
    first = utc.to_document()
    second = utc.to_document()
    assert first == second
    assert first["authorized_at"] == "2026-09-17T12:00:00+00:00"
    assert set(first) == {
        "authority_evidence_id", "scope", "operation", "source_document_id",
        "source_agreement_type", "source_version", "source_status",
        "source_content_reference", "source_sha3_512", "authority_source_id",
        "authority_source_version", "actor_representation", "authorized_at",
        "idempotency_key", "evidence_fingerprint",
    }
    assert all(isinstance(item, str) for item in first.values())


def test_canonical_charter_verification_and_all_source_mismatches_fail_closed() -> None:
    document = corpus.get_institutional_charter_draft()
    value = _evidence()
    value.verify_against(document)
    for field, changed in (
        ("source_document_id", "OTHER-DOCUMENT"),
        ("source_agreement_type", LegalAgreementType.USER_TERMS),
        ("source_version", "1.0.1-DRAFT"),
        ("source_content_reference", "wilsy-os://legal/other"),
        ("source_sha3_512", "b" * 128),
    ):
        with pytest.raises(LegalCorpusProvisioningAuthorityError, match="SOURCE_DOCUMENT_MISMATCH"):
            _evidence(**{field: changed}).verify_against(document)
    for status in (LegalDocumentStatus.APPROVED, LegalDocumentStatus.RETIRED):
        with pytest.raises(LegalCorpusProvisioningAuthorityError, match="NON_DRAFT_SOURCE_STATUS"):
            value.verify_against(replace(document, status=status))


@pytest.mark.parametrize(
    ("changes", "code"),
    [
        ({"authority_evidence_id": ""}, "AUTHORITY_EVIDENCE_ID_INVALID"),
        ({"source_document_id": ""}, "SOURCE_DOCUMENT_ID_INVALID"),
        ({"source_version": ""}, "SOURCE_VERSION_INVALID"),
        ({"source_content_reference": ""}, "SOURCE_REFERENCE_INVALID"),
        ({"actor_representation": ""}, "ACTOR_REPRESENTATION_INVALID"),
        ({"idempotency_key": ""}, "IDEMPOTENCY_KEY_REQUIRED"),
        ({"source_sha3_512": "a" * 127}, "SOURCE_SHA3_512_INVALID"),
        ({"source_sha3_512": "A" * 128}, "SOURCE_SHA3_512_INVALID"),
        ({"source_sha3_512": "g" * 128}, "SOURCE_SHA3_512_INVALID"),
        ({"authorized_at": datetime(2026, 9, 17)}, "AUTHORIZED_AT_INVALID"),
        ({"source_status": "APPROVED"}, "SOURCE_STATUS_INVALID"),
    ],
)
def test_invalid_inputs_have_structured_failures(changes: dict[str, Any], code: str) -> None:
    values = _fields()
    values.update(changes)
    values["evidence_fingerprint"] = "0" * 128
    _expect_code(values, code)


def test_domain_has_no_persistence_imports_or_caller_authority_path() -> None:
    path = Path("tools/eos/legal_operations/domain/legal_corpus_provisioning_authority.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imports.extend(alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names)
    assert not any(token in module.casefold() for module in imports for token in ("pymongo", "kernel", "registry", "http"))
    source = path.read_text(encoding="utf-8")
    assert "LegalDocumentRegistry" not in source
    assert "LegalAcceptanceRegistry" not in source
    assert "MongoClient" not in source
    assert "not an issuing authority" in source
    assert set(_fields()) >= {"authority_evidence_id", "evidence_fingerprint"}


# ARTIFACT: test_legal_corpus_provisioning_authority.py
# VERSION: v1.0.0-R1D-B0F-B4-R8E-LEGAL-CORPUS-PROVISIONING-AUTHORITY-CERT
# AUTHORITY BOUNDARY: direct certificate evidence only; no provisioning authority
# TENANT POSTURE: PLATFORM corpus evidence; no tenant acceptance state
# FAIL-CLOSED POSTURE: authority, source, digest, and lifecycle drift fails
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
