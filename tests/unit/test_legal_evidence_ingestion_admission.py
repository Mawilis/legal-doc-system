"""Direct certificate for C4D5D7 Legal Evidence ingestion admission.

TITLE: Legal Evidence Ingestion Admission Direct Certificate
VERSION: v1.0.0-L10A2R-C4D5D7-LEGAL-EVIDENCE-INGESTION-ADMISSION-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
PURPOSE:
    Prove canonical ProcessDocument matter binding, server-owned ingestion
    identity, immutable transport-coordinate sealing and zero later authority.

CERTIFICATION / UPDATE DATE: 2026-10-01
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from typing import Any
from unittest.mock import patch

import pytest

from tools.eos.legal_operations.domain.legal_evidence_ingestion_admission import (
    LegalEvidenceIngestionAdmission,
    LegalEvidenceIngestionAdmissionError,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ProcessDocument,
)


NOW = datetime(
    2026,
    10,
    1,
    20,
    0,
    tzinfo=timezone.utc,
)


class _FixedUUID:
    hex = "0123456789abcdef0123456789abcdef"


def _document(
    *,
    tenant_id: str = "tenant-c4d5d7",
    document_id: str = "document-c4d5d7",
    case_matter_id: str = "matter-c4d5d7",
) -> ProcessDocument:
    return ProcessDocument(
        tenant_id=tenant_id,
        document_id=document_id,
        case_matter_id=case_matter_id,
        document_type="court-filing",
        registered_at=NOW,
        registration_evidence_reference=(
            "evidence:process-document:c4d5d7"
        ),
    )


def _issue(
    **overrides: object,
) -> LegalEvidenceIngestionAdmission:
    values: dict[str, Any] = {
        "process_document": _document(),
        "media_type": "Application/PDF",
        "original_filename": "founding-affidavit.pdf",
        "declared_content_length": 4096,
        "admitted_at": NOW,
    }
    values.update(
        overrides
    )

    with patch(
        "tools.eos.legal_operations.domain."
        "legal_evidence_ingestion_admission.uuid4",
        return_value=_FixedUUID(),
    ):
        return LegalEvidenceIngestionAdmission.issue(
            **values,
        )


def test_direct_construction_is_forbidden() -> None:
    with pytest.raises(
        LegalEvidenceIngestionAdmissionError,
        match="L10A2R_C4D5D7_FACTORY_REQUIRED",
    ):
        LegalEvidenceIngestionAdmission()


def test_issue_binds_exact_canonical_process_document_scope() -> None:
    document = _document(
        tenant_id="tenant-exact",
        document_id="document-exact",
        case_matter_id="matter-exact",
    )

    value = _issue(
        process_document=document,
    )

    assert value.tenant_id == document.tenant_id
    assert value.document_id == document.document_id
    assert value.case_matter_id == document.case_matter_id
    assert (
        value.source_process_document_fingerprint
        == document.fingerprint
    )


def test_ingestion_reference_is_server_issued() -> None:
    value = _issue()

    assert value.ingestion_reference == (
        "legal-evidence-ingestion:"
        "0123456789abcdef0123456789abcdef"
    )


def test_media_type_is_normalized_and_filename_is_preserved() -> None:
    value = _issue(
        media_type="Application/PDF",
        original_filename="Evidence Bundle.PDF",
    )

    assert value.media_type == "application/pdf"
    assert value.original_filename == "Evidence Bundle.PDF"


def test_declared_length_is_evidence_not_capacity_authority() -> None:
    value = _issue(
        declared_content_length=8192,
    )

    assert value.declared_content_length == 8192

    assert not hasattr(
        value,
        "reserved_storage_bytes",
    )
    assert not hasattr(
        value,
        "reserved_ingress_bytes",
    )
    assert not hasattr(
        value,
        "authorized_availability",
    )


@pytest.mark.parametrize(
    "field,value,code",
    [
        (
            "media_type",
            "",
            "L10A2R_C4D5D7_MEDIA_TYPE_INVALID",
        ),
        (
            "media_type",
            " application/pdf",
            "L10A2R_C4D5D7_MEDIA_TYPE_INVALID",
        ),
        (
            "original_filename",
            "",
            "L10A2R_C4D5D7_ORIGINAL_FILENAME_INVALID",
        ),
        (
            "original_filename",
            "bad\nname.pdf",
            "L10A2R_C4D5D7_ORIGINAL_FILENAME_INVALID",
        ),
        (
            "declared_content_length",
            0,
            "L10A2R_C4D5D7_DECLARED_CONTENT_LENGTH_INVALID",
        ),
        (
            "declared_content_length",
            -1,
            "L10A2R_C4D5D7_DECLARED_CONTENT_LENGTH_INVALID",
        ),
        (
            "declared_content_length",
            True,
            "L10A2R_C4D5D7_DECLARED_CONTENT_LENGTH_INVALID",
        ),
    ],
)
def test_invalid_transport_coordinates_fail_closed(
    field: str,
    value: object,
    code: str,
) -> None:
    with pytest.raises(
        LegalEvidenceIngestionAdmissionError,
        match=code,
    ):
        _issue(
            **{
                field: value,
            }
        )


def test_naive_admission_time_fails_closed() -> None:
    with pytest.raises(
        LegalEvidenceIngestionAdmissionError,
        match="L10A2R_C4D5D7_ADMITTED_AT_INVALID",
    ):
        _issue(
            admitted_at=datetime(
                2026,
                10,
                1,
                20,
                0,
            ),
        )


def test_wrong_process_document_type_fails_closed() -> None:
    with pytest.raises(
        LegalEvidenceIngestionAdmissionError,
        match="L10A2R_C4D5D7_PROCESS_DOCUMENT_REQUIRED",
    ):
        _issue(
            process_document=object(),
        )


def test_admission_is_immutable() -> None:
    value = _issue()

    with pytest.raises(
        FrozenInstanceError
    ):
        value.document_id = "mutated"  # type: ignore[misc]


def test_identical_fixed_server_identity_is_deterministic() -> None:
    left = _issue()
    right = _issue()

    assert left == right
    assert left.fingerprint == right.fingerprint


def test_different_server_identity_changes_fingerprint() -> None:
    left = _issue()

    class _OtherUUID:
        hex = "fedcba9876543210fedcba9876543210"

    with patch(
        "tools.eos.legal_operations.domain."
        "legal_evidence_ingestion_admission.uuid4",
        return_value=_OtherUUID(),
    ):
        right = LegalEvidenceIngestionAdmission.issue(
            process_document=_document(),
            media_type="Application/PDF",
            original_filename="founding-affidavit.pdf",
            declared_content_length=4096,
            admitted_at=NOW,
        )

    assert left.ingestion_reference != right.ingestion_reference
    assert left.fingerprint != right.fingerprint


def test_verify_accepts_pristine_admission() -> None:
    value = _issue()

    value.verify()


def test_verify_rejects_tampered_fingerprint() -> None:
    value = _issue()

    object.__setattr__(
        value,
        "fingerprint",
        "0" * 128,
    )

    with pytest.raises(
        LegalEvidenceIngestionAdmissionError,
        match="L10A2R_C4D5D7_ADMISSION_FINGERPRINT_INVALID",
    ):
        value.verify()


def test_no_later_authority_fields_exist() -> None:
    value = _issue()

    forbidden = {
        "provider_name",
        "storage_reference",
        "write_session_reference",
        "object_version_reference",
        "provider_integrity_reference",
        "content_reference",
        "content_fingerprint",
        "committed_at",
        "orphan_proven",
        "provider_delete_authorized",
        "abort_authorized",
        "available",
        "authorized_availability",
    }

    assert all(
        not hasattr(
            value,
            field,
        )
        for field in forbidden
    )


# ARTIFACT: test_legal_evidence_ingestion_admission.py
# VERSION: v1.0.0-L10A2R-C4D5D7-LEGAL-EVIDENCE-INGESTION-ADMISSION-CERT
# AUTHORITY BOUNDARY: direct pure-domain admission certification only
# SOURCE POSTURE: canonical ProcessDocument owns tenant/document/matter binding
# IDENTITY POSTURE: caller cannot provide the generated ingestion reference
# CAPACITY POSTURE: declared length is non-authorizing evidence only
# PROVIDER POSTURE: no provider operation certified here
# COMMIT POSTURE: no canonical commit authority
# ORPHAN POSTURE: no orphan proof
# ABORT POSTURE: no abort authority
# DELETION POSTURE: no deletion authority
# END OF WILSY OS SOVEREIGN ARTIFACT
