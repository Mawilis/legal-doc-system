"""Direct certificate for immutable Legal evidence-content identity.

TITLE: WILSY OS Legal Evidence Content Direct Certificate
VERSION: v1.0.0-L10A1-LEGAL-EVIDENCE-CONTENT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify exact tenant/matter/document binding, safe content admission,
         SHA3-512 byte identity, deterministic references, immutable metadata,
         corruption rejection and explicit authority exclusions for L10A1.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_evidence_content.py
COLLABORATION / OWNERSHIP: Certifies only
                            tools/eos/legal_operations/domain/legal_evidence_content.py.
                            Storage, persistence, HTTP admission, ProcessDocument
                            lifecycle, custody, Court Online, AI and finance are
                            outside this certificate.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: 2026-09-29 v1.0.0-L10A1-LEGAL-EVIDENCE-CONTENT-CERT establishes
           positive construction/round-trip evidence plus malformed identity,
           unsafe filename/media, byte-limit, schema, fingerprint and authority
           boundary certificates.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic bytes and opaque identities only; no live
                             tenant evidence or personal information.
TENANT BOUNDARY: Cross/pseudo-tenant identities are not accepted by the
                 certified domain contract.
AUTHORITY BOUNDARY: Content identity certificate only; creates no lifecycle,
                    Court filing, service, IAM, AI or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Any expected rejection that begins passing is a
                         certificate failure rather than inferred authority.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib

import pytest

from tools.eos.legal_operations.domain.legal_evidence_content import (
    LEGAL_EVIDENCE_CONTENT_FIELDS,
    MAX_CONTENT_BYTES,
    SAFE_MEDIA_TYPES,
    SCHEMA,
    VERSION,
    LegalEvidenceContent,
    LegalEvidenceContentError,
    content_fingerprint,
    register_legal_evidence_content,
)


TENANT = "WILSYTENANT-4CD2FZ4O"
MATTER = "matter-l10a1"
DOCUMENT = "document-l10a1"
CONTENT = b"%PDF-1.7\nsynthetic legal evidence\n"
SOURCE_FINGERPRINT = hashlib.sha3_512(b"source-evidence").hexdigest()
REGISTERED_AT = datetime(2026, 9, 29, 16, 30, tzinfo=timezone.utc)


def evidence(**overrides: object) -> LegalEvidenceContent:
    """Return one valid immutable synthetic Legal evidence-content value."""
    values: dict[str, object] = {
        "tenant_id": TENANT,
        "case_matter_id": MATTER,
        "document_id": DOCUMENT,
        "media_type": "application/pdf",
        "original_filename": "founding-affidavit.pdf",
        "content": CONTENT,
        "source_evidence_reference": "partner-upload:l10a1",
        "source_evidence_fingerprint": SOURCE_FINGERPRINT,
        "registered_at": REGISTERED_AT,
    }
    values.update(overrides)
    return register_legal_evidence_content(**values)  # type: ignore[arg-type]


def test_contract_identity_and_public_shape() -> None:
    """Certify stable L10A1 schema/version/exported metadata shape."""
    value = evidence()

    assert VERSION == "v1.0.0-L10A1-LEGAL-EVIDENCE-CONTENT"
    assert SCHEMA == "WILSY-LEGAL-EVIDENCE-CONTENT/V1"
    assert value.schema == SCHEMA
    assert value.evidence_content_version == VERSION
    assert set(value.to_dict()) == set(LEGAL_EVIDENCE_CONTENT_FIELDS)


def test_exact_tenant_matter_and_document_binding() -> None:
    """Certify exact operational identity binding without inferred scope."""
    value = evidence()

    assert value.tenant_id == TENANT
    assert value.case_matter_id == MATTER
    assert value.document_id == DOCUMENT


def test_content_bytes_receive_exact_sha3_512_identity() -> None:
    """Certify the exact supplied bytes determine the content digest."""
    value = evidence()

    expected = hashlib.sha3_512(CONTENT).hexdigest()

    assert value.content_fingerprint == expected
    assert content_fingerprint(CONTENT) == expected
    assert len(value.content_fingerprint) == 128
    assert value.content_fingerprint == value.content_fingerprint.lower()


def test_reference_is_deterministic_and_server_derived() -> None:
    """Certify stable reference derivation from validated identity plus digest."""
    first = evidence()
    second = evidence()

    assert first.content_reference == second.content_reference
    assert first.content_reference == (
        f"legal-evidence:{TENANT}:{MATTER}:{DOCUMENT}:"
        f"{first.content_fingerprint[:32]}"
    )


def test_metadata_round_trip_is_exact() -> None:
    """Certify exact immutable metadata dehydration and hydration."""
    original = evidence()
    hydrated = LegalEvidenceContent.from_dict(original.to_dict())

    assert hydrated == original
    assert hydrated.to_dict() == original.to_dict()


@pytest.mark.parametrize(
    ("tenant", "expected_code"),
    [
        ("default", "L10A1_TENANT_REQUIRED"),
        ("global", "L10A1_TENANT_REQUIRED"),
        ("global_root", "L10A1_TENANT_REQUIRED"),
        ("root", "L10A1_TENANT_REQUIRED"),
        ("master", "L10A1_TENANT_REQUIRED"),
        ("*", "L10A1_INVALID_TENANT_ID"),
    ],
)
def test_pseudo_tenants_reject(
    tenant: str,
    expected_code: str,
) -> None:
    """Certify pseudo/global tenant fallbacks cannot own Legal evidence."""
    with pytest.raises(
        LegalEvidenceContentError,
        match=f"^{expected_code}$",
    ):
        evidence(tenant_id=tenant)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tenant_id", ""),
        ("tenant_id", " bad"),
        ("case_matter_id", ""),
        ("case_matter_id", "matter with spaces"),
        ("document_id", ""),
        ("document_id", "document/escape"),
    ],
)
def test_invalid_operational_identities_reject(
    field: str,
    value: str,
) -> None:
    """Certify malformed tenant/matter/document identity fails closed."""
    with pytest.raises(LegalEvidenceContentError):
        evidence(**{field: value})


@pytest.mark.parametrize(
    "media_type",
    [
        "text/html",
        "text/css",
        "application/javascript",
        "application/x-msdownload",
        "application/octet-stream",
        "application/vnd.ms-word.document.macroEnabled.12",
        "image/svg+xml",
    ],
)
def test_unsafe_or_unapproved_media_types_reject(media_type: str) -> None:
    """Certify executable/active/unapproved media cannot enter L10A1."""
    assert media_type not in SAFE_MEDIA_TYPES

    with pytest.raises(
        LegalEvidenceContentError,
        match="^L10A1_MEDIA_TYPE_UNSUPPORTED$",
    ):
        evidence(media_type=media_type)


@pytest.mark.parametrize(
    "media_type",
    sorted(SAFE_MEDIA_TYPES),
)
def test_declared_safe_media_types_are_admitted(media_type: str) -> None:
    """Certify each closed L10A1 media type remains deliberately admissible."""
    value = evidence(media_type=media_type)

    assert value.media_type == media_type


@pytest.mark.parametrize(
    "filename",
    [
        "../affidavit.pdf",
        "..\\affidavit.pdf",
        "/tmp/affidavit.pdf",
        "folder/affidavit.pdf",
        "folder\\affidavit.pdf",
        ".secret.pdf",
        ".",
        "..",
        "bad\x00name.pdf",
    ],
)
def test_path_or_hidden_filename_semantics_reject(filename: str) -> None:
    """Certify original filename is display metadata and never a storage path."""
    with pytest.raises(
        LegalEvidenceContentError,
        match="^L10A1_INVALID_ORIGINAL_FILENAME$",
    ):
        evidence(original_filename=filename)


def test_empty_content_rejects() -> None:
    """Certify empty uploads cannot produce evidence identity."""
    with pytest.raises(
        LegalEvidenceContentError,
        match="^L10A1_CONTENT_LENGTH_INVALID$",
    ):
        evidence(content=b"")


def test_oversize_content_rejects() -> None:
    """Certify the internal Legal ingestion safety ceiling is enforced."""
    with pytest.raises(
        LegalEvidenceContentError,
        match="^L10A1_CONTENT_LENGTH_INVALID$",
    ):
        evidence(content=b"x" * (MAX_CONTENT_BYTES + 1))


def test_non_bytes_content_rejects() -> None:
    """Certify the pure content domain never hashes caller text implicitly."""
    with pytest.raises(
        LegalEvidenceContentError,
        match="^L10A1_CONTENT_BYTES_REQUIRED$",
    ):
        evidence(content="not-bytes")


def test_divergent_bytes_produce_divergent_content_identity() -> None:
    """Certify byte changes are cryptographically observable."""
    first = evidence()
    second = evidence(content=CONTENT + b"changed")

    assert first.content_fingerprint != second.content_fingerprint
    assert first.content_reference != second.content_reference
    assert first.fingerprint != second.fingerprint


def test_metadata_corruption_rejects_on_hydration() -> None:
    """Certify persisted metadata drift cannot hydrate as valid evidence."""
    value = evidence()
    payload = value.to_dict()
    payload["content_length"] = value.content_length + 1

    with pytest.raises(
        LegalEvidenceContentError,
        match="^L10A1_FINGERPRINT_MISMATCH$",
    ):
        LegalEvidenceContent.from_dict(payload)


def test_content_reference_forgery_rejects() -> None:
    """Certify callers cannot supply an unrelated evidence content locator."""
    value = evidence()

    with pytest.raises(
        LegalEvidenceContentError,
        match="^L10A1_CONTENT_REFERENCE_INVALID$",
    ):
        replace(
            value,
            content_reference="legal-evidence:foreign:forged",
            fingerprint="",
        )


def test_content_fingerprint_format_corruption_rejects() -> None:
    """Certify content identity remains lowercase SHA3-512 only."""
    value = evidence()

    with pytest.raises(
        LegalEvidenceContentError,
        match="^L10A1_INVALID_CONTENT_FINGERPRINT$",
    ):
        replace(
            value,
            content_fingerprint="A" * 128,
            fingerprint="",
        )


def test_source_fingerprint_format_corruption_rejects() -> None:
    """Certify provenance fingerprint cannot silently degrade."""
    with pytest.raises(
        LegalEvidenceContentError,
        match="^L10A1_INVALID_SOURCE_EVIDENCE_FINGERPRINT$",
    ):
        evidence(source_evidence_fingerprint="f" * 127)


def test_schema_drift_rejects() -> None:
    """Certify persisted extra/missing fields fail closed."""
    payload = evidence().to_dict()
    payload["unexpected"] = "forged"

    with pytest.raises(
        LegalEvidenceContentError,
        match="^L10A1_SCHEMA_INVALID$",
    ):
        LegalEvidenceContent.from_dict(payload)


def test_raw_bytes_and_sensitive_authority_are_not_serialized() -> None:
    """Certify metadata creates no raw-content or downstream authority fields."""
    payload = evidence().to_dict()

    forbidden = {
        "content",
        "content_bytes",
        "raw_bytes",
        "filesystem_path",
        "path",
        "url",
        "court_online_credentials",
        "court_online_token",
        "filed_at",
        "accepted_at",
        "judicial_order",
        "attorney_of_record",
        "service_completed",
        "invoice",
        "payment",
        "executed",
        "settled",
    }

    assert forbidden.isdisjoint(payload)


def test_contract_does_not_claim_storage_or_downstream_execution_methods() -> None:
    """Certify L10A1 stays a pure content-identity domain."""
    forbidden_methods = {
        "save",
        "store",
        "upload",
        "submit_to_court",
        "file_at_court",
        "mark_filed",
        "authorize_service",
        "authorize_payment",
        "execute_payment",
        "settle",
    }

    public = {
        name
        for name in dir(LegalEvidenceContent)
        if not name.startswith("_")
    }

    assert forbidden_methods.isdisjoint(public)


# ARTIFACT: test_legal_evidence_content.py
# VERSION: v1.0.0-L10A1-LEGAL-EVIDENCE-CONTENT-CERT
# AUTHORITY BOUNDARY: direct immutable Legal evidence-content domain certificate only
# TENANT POSTURE: synthetic exact-tenant evidence with pseudo/cross-scope rejection
# FAIL-CLOSED POSTURE: malformed identity/media/name/bytes/schema/fingerprint and authority inflation reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
