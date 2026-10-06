"""TITLE: WILSY OS HR Document Pure Domain Certification.
VERSION: v1.0.0-P0-C12F3-HR-DOCUMENT-DOMAIN-CERT
AUTHORITY: Direct certification of immutable HR personnel-document truth.
EPITOME: Proves 20 governed document classes, exact tenant/employee/
document/version identity, sensitivity classification, certified
binary evidence consumption, UTC provenance, retention/legal-hold
state and deterministic SHA3-512 domain fingerprinting.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document.py
CERTIFICATION/UPDATE DATE: 2026-10-04.
CHANGELOG:
2026-10-04 v1.0.0-P0-C12F3-HR-DOCUMENT-DOMAIN-CERT
establishes the first sovereign HR document pure-domain certificate.
AUTHORITY BOUNDARY: Domain truth only; no IAM, registry, provider,
HTTP, deletion execution, payroll, billing or financial authority.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import hashlib
import pathlib

import pytest

from tools.eos.saas.domain.hr_document import (
    HR_DOCUMENT_SCHEMA,
    HR_DOCUMENT_CLASSES,
    HrDocument,
    HrDocumentClass,
    HrDocumentDomainError,
    HrDocumentSensitivity,
    sensitivity_for_document_class,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryWriteIntent,
)


TENANT = "tenant-hr-doc"
EMPLOYEE = "employee-42"
DOCUMENT = "hrdoc-001"
VERSION_ID = "hrdocver-001"
PRINCIPAL = "principal-hr-001"

CREATED = datetime(
    2026,
    10,
    4,
    8,
    0,
    0,
    tzinfo=timezone.utc,
)

PAYLOAD = (
    b"%PDF-1.7\n"
    b"WILSY HR APPOINTMENT LETTER\n"
    b"\x00\x01\x02"
)


def intent() -> HrDocumentBinaryWriteIntent:
    return HrDocumentBinaryWriteIntent(
        tenant_id=TENANT,
        employee_id=EMPLOYEE,
        document_id=DOCUMENT,
        document_version_id=VERSION_ID,
        ingestion_reference="ingest-001",
        media_type="application/pdf",
        original_filename="appointment-letter.pdf",
        admitted_max_content_length=2_000_000,
    )


def evidence() -> HrDocumentBinaryObjectEvidence:
    current = intent()

    return HrDocumentBinaryObjectEvidence(
        provider_name="hr-provider",
        storage_reference="opaque/hr/obj/1",
        object_version_reference="provider-version-1",
        provider_integrity_reference="provider-integrity-1",
        write_intent_fingerprint=current.fingerprint,
        content_length=len(PAYLOAD),
        content_fingerprint=hashlib.sha3_512(
            PAYLOAD
        ).hexdigest(),
    )


def document(
    *,
    document_class: HrDocumentClass = (
        HrDocumentClass.APPOINTMENT_LETTER
    ),
    retention_until: datetime | None = None,
    legal_hold: bool = False,
    supersedes_version_id: str | None = None,
) -> HrDocument:

    return HrDocument.from_binary_evidence(
        intent=intent(),
        evidence=evidence(),
        document_class=document_class,
        created_at=CREATED,
        created_by_principal_id=PRINCIPAL,
        retention_until=retention_until,
        legal_hold=legal_hold,
        supersedes_version_id=supersedes_version_id,
    )


def test_schema_is_explicit() -> None:
    assert (
        HR_DOCUMENT_SCHEMA
        == "WILSY-HR-DOCUMENT/V1"
    )


def test_exact_twenty_governed_document_classes() -> None:

    assert len(
        HR_DOCUMENT_CLASSES
    ) == 20

    assert {
        item.value
        for item in HR_DOCUMENT_CLASSES
    } == {
        "EMPLOYMENT_CONTRACT",
        "APPOINTMENT_LETTER",
        "OFFER_LETTER",
        "WARNING",
        "FINAL_WARNING",
        "DISCIPLINARY_NOTICE",
        "DISCIPLINARY_OUTCOME",
        "GRIEVANCE_RECORD",
        "PERFORMANCE_RECORD",
        "PERFORMANCE_IMPROVEMENT_PLAN",
        "POLICY_ACKNOWLEDGEMENT",
        "TRAINING_CERTIFICATE",
        "LEAVE_SUPPORTING_DOCUMENT",
        "MEDICAL_SUPPORTING_DOCUMENT",
        "IDENTITY_SUPPORTING_DOCUMENT",
        "QUALIFICATION_DOCUMENT",
        "TERMINATION_LETTER",
        "RESIGNATION_LETTER",
        "EXIT_DOCUMENT",
        "GENERAL_EMPLOYEE_ARTIFACT",
    }


@pytest.mark.parametrize(
    ("document_class", "expected"),
    (
        (
            HrDocumentClass.EMPLOYMENT_CONTRACT,
            HrDocumentSensitivity.STANDARD_EMPLOYMENT,
        ),
        (
            HrDocumentClass.APPOINTMENT_LETTER,
            HrDocumentSensitivity.STANDARD_EMPLOYMENT,
        ),
        (
            HrDocumentClass.WARNING,
            HrDocumentSensitivity.EMPLOYEE_RELATIONS_RESTRICTED,
        ),
        (
            HrDocumentClass.DISCIPLINARY_OUTCOME,
            HrDocumentSensitivity.EMPLOYEE_RELATIONS_RESTRICTED,
        ),
        (
            HrDocumentClass.PERFORMANCE_RECORD,
            HrDocumentSensitivity.PERFORMANCE_RESTRICTED,
        ),
        (
            HrDocumentClass.MEDICAL_SUPPORTING_DOCUMENT,
            HrDocumentSensitivity.HIGHLY_SENSITIVE_HEALTH,
        ),
        (
            HrDocumentClass.IDENTITY_SUPPORTING_DOCUMENT,
            HrDocumentSensitivity.HIGHLY_SENSITIVE_IDENTITY,
        ),
        (
            HrDocumentClass.TERMINATION_LETTER,
            HrDocumentSensitivity.SEPARATION_RESTRICTED,
        ),
        (
            HrDocumentClass.GENERAL_EMPLOYEE_ARTIFACT,
            HrDocumentSensitivity.GENERAL,
        ),
    ),
)
def test_sensitivity_mapping_is_exact(
    document_class: HrDocumentClass,
    expected: HrDocumentSensitivity,
) -> None:

    assert (
        sensitivity_for_document_class(
            document_class
        )
        is expected
    )


def test_factory_consumes_certified_binary_scope_and_evidence() -> None:

    value = document()

    assert value.tenant_id == TENANT
    assert value.employee_id == EMPLOYEE
    assert value.document_id == DOCUMENT
    assert value.document_version_id == VERSION_ID

    assert (
        value.document_class
        is HrDocumentClass.APPOINTMENT_LETTER
    )

    assert (
        value.sensitivity
        is HrDocumentSensitivity.STANDARD_EMPLOYMENT
    )

    assert value.original_filename == "appointment-letter.pdf"
    assert value.media_type == "application/pdf"
    assert value.byte_length == len(PAYLOAD)

    assert (
        value.content_digest_sha3_512
        == hashlib.sha3_512(
            PAYLOAD
        ).hexdigest()
    )

    assert value.storage_provider_id == "hr-provider"
    assert value.storage_object_reference == "opaque/hr/obj/1"
    assert value.object_version_reference == "provider-version-1"
    assert value.provider_integrity_reference == "provider-integrity-1"

    assert value.created_at == CREATED
    assert value.created_by_principal_id == PRINCIPAL
    assert value.legal_hold is False
    assert value.retention_until is None
    assert value.supersedes_version_id is None


def test_domain_is_frozen() -> None:

    value = document()

    with pytest.raises(
        FrozenInstanceError
    ):
        value.employee_id = "employee-forged"  # type: ignore[misc]


def test_domain_fingerprint_is_lowercase_sha3_512() -> None:

    value = document()

    assert len(value.fingerprint) == 128
    assert value.fingerprint == value.fingerprint.lower()

    int(
        value.fingerprint,
        16,
    )


def test_domain_fingerprint_is_deterministic() -> None:

    assert (
        document().fingerprint
        == document().fingerprint
    )


def test_employee_change_changes_domain_fingerprint() -> None:

    first = document()

    alternate_intent = HrDocumentBinaryWriteIntent(
        tenant_id=TENANT,
        employee_id="employee-99",
        document_id=DOCUMENT,
        document_version_id=VERSION_ID,
        ingestion_reference="ingest-001",
        media_type="application/pdf",
        original_filename="appointment-letter.pdf",
        admitted_max_content_length=2_000_000,
    )

    alternate_evidence = HrDocumentBinaryObjectEvidence(
        provider_name="hr-provider",
        storage_reference="opaque/hr/obj/2",
        object_version_reference="provider-version-2",
        provider_integrity_reference="provider-integrity-2",
        write_intent_fingerprint=alternate_intent.fingerprint,
        content_length=len(PAYLOAD),
        content_fingerprint=hashlib.sha3_512(
            PAYLOAD
        ).hexdigest(),
    )

    second = HrDocument.from_binary_evidence(
        intent=alternate_intent,
        evidence=alternate_evidence,
        document_class=HrDocumentClass.APPOINTMENT_LETTER,
        created_at=CREATED,
        created_by_principal_id=PRINCIPAL,
    )

    assert first.fingerprint != second.fingerprint


def test_document_version_change_changes_domain_fingerprint() -> None:

    first = document()

    alternate_intent = HrDocumentBinaryWriteIntent(
        tenant_id=TENANT,
        employee_id=EMPLOYEE,
        document_id=DOCUMENT,
        document_version_id="hrdocver-002",
        ingestion_reference="ingest-002",
        media_type="application/pdf",
        original_filename="appointment-letter.pdf",
        admitted_max_content_length=2_000_000,
    )

    alternate_evidence = HrDocumentBinaryObjectEvidence(
        provider_name="hr-provider",
        storage_reference="opaque/hr/obj/3",
        object_version_reference="provider-version-3",
        provider_integrity_reference="provider-integrity-3",
        write_intent_fingerprint=alternate_intent.fingerprint,
        content_length=len(PAYLOAD),
        content_fingerprint=hashlib.sha3_512(
            PAYLOAD
        ).hexdigest(),
    )

    second = HrDocument.from_binary_evidence(
        intent=alternate_intent,
        evidence=alternate_evidence,
        document_class=HrDocumentClass.APPOINTMENT_LETTER,
        created_at=CREATED,
        created_by_principal_id=PRINCIPAL,
    )

    assert first.fingerprint != second.fingerprint


def test_forged_binary_evidence_scope_rejected() -> None:

    current_intent = intent()

    forged = HrDocumentBinaryObjectEvidence(
        provider_name="hr-provider",
        storage_reference="opaque/hr/obj/forged",
        object_version_reference="provider-version-forged",
        provider_integrity_reference="provider-integrity-forged",
        write_intent_fingerprint="0" * 128,
        content_length=len(PAYLOAD),
        content_fingerprint=hashlib.sha3_512(
            PAYLOAD
        ).hexdigest(),
    )

    with pytest.raises(
        HrDocumentDomainError,
        match="P0_C12F3_BINARY_SCOPE_MISMATCH",
    ):
        HrDocument.from_binary_evidence(
            intent=current_intent,
            evidence=forged,
            document_class=HrDocumentClass.APPOINTMENT_LETTER,
            created_at=CREATED,
            created_by_principal_id=PRINCIPAL,
        )


def test_content_length_over_admitted_max_rejected() -> None:

    current_intent = HrDocumentBinaryWriteIntent(
        tenant_id=TENANT,
        employee_id=EMPLOYEE,
        document_id=DOCUMENT,
        document_version_id=VERSION_ID,
        ingestion_reference="ingest-001",
        media_type="application/pdf",
        original_filename="appointment-letter.pdf",
        admitted_max_content_length=5,
    )

    current_evidence = HrDocumentBinaryObjectEvidence(
        provider_name="hr-provider",
        storage_reference="opaque/hr/obj/1",
        object_version_reference="provider-version-1",
        provider_integrity_reference="provider-integrity-1",
        write_intent_fingerprint=current_intent.fingerprint,
        content_length=len(PAYLOAD),
        content_fingerprint=hashlib.sha3_512(
            PAYLOAD
        ).hexdigest(),
    )

    with pytest.raises(
        HrDocumentDomainError,
        match="P0_C12F3_CONTENT_LENGTH_EXCEEDED",
    ):
        HrDocument.from_binary_evidence(
            intent=current_intent,
            evidence=current_evidence,
            document_class=HrDocumentClass.APPOINTMENT_LETTER,
            created_at=CREATED,
            created_by_principal_id=PRINCIPAL,
        )


def test_naive_created_at_rejected() -> None:

    with pytest.raises(
        HrDocumentDomainError
    ):
        HrDocument.from_binary_evidence(
            intent=intent(),
            evidence=evidence(),
            document_class=HrDocumentClass.APPOINTMENT_LETTER,
            created_at=datetime(
                2026,
                10,
                4,
                8,
                0,
                0,
            ),
            created_by_principal_id=PRINCIPAL,
        )


def test_created_at_normalizes_to_utc() -> None:

    local = datetime(
        2026,
        10,
        4,
        10,
        0,
        0,
        tzinfo=timezone(
            timedelta(
                hours=2
            )
        ),
    )

    value = HrDocument.from_binary_evidence(
        intent=intent(),
        evidence=evidence(),
        document_class=HrDocumentClass.APPOINTMENT_LETTER,
        created_at=local,
        created_by_principal_id=PRINCIPAL,
    )

    assert value.created_at == CREATED
    assert value.created_at.tzinfo is timezone.utc


def test_retention_until_must_be_utc_aware() -> None:

    with pytest.raises(
        HrDocumentDomainError
    ):
        document(
            retention_until=datetime(
                2027,
                1,
                1,
            )
        )


def test_retention_until_cannot_precede_creation() -> None:

    with pytest.raises(
        HrDocumentDomainError
    ):
        document(
            retention_until=(
                CREATED
                - timedelta(
                    seconds=1
                )
            )
        )


def test_retention_blocked_before_deadline() -> None:

    value = document(
        retention_until=(
            CREATED
            + timedelta(
                days=365
            )
        )
    )

    assert value.retention_blocks_disposal(
        at=(
            CREATED
            + timedelta(
                days=30
            )
        )
    ) is True


def test_retention_not_blocking_at_deadline() -> None:

    deadline = (
        CREATED
        + timedelta(
            days=365
        )
    )

    value = document(
        retention_until=deadline
    )

    assert value.retention_blocks_disposal(
        at=deadline
    ) is False


def test_legal_hold_blocks_disposal_independently() -> None:

    value = document(
        legal_hold=True
    )

    assert value.legal_hold is True

    assert value.disposal_blocked(
        at=(
            CREATED
            + timedelta(
                days=10_000
            )
        )
    ) is True


def test_no_hold_and_no_retention_does_not_itself_block_disposal() -> None:

    value = document()

    assert value.disposal_blocked(
        at=(
            CREATED
            + timedelta(
                days=1
            )
        )
    ) is False


def test_disposal_policy_is_not_deletion_authority() -> None:

    value = document()

    assert not hasattr(
        value,
        "delete"
    )

    assert not hasattr(
        value,
        "authorize_delete"
    )

    assert not hasattr(
        value,
        "purge"
    )


def test_superseding_version_must_not_self_reference() -> None:

    with pytest.raises(
        HrDocumentDomainError
    ):
        document(
            supersedes_version_id=VERSION_ID
        )


def test_superseding_version_coordinate_is_preserved() -> None:

    value = document(
        supersedes_version_id="hrdocver-000"
    )

    assert (
        value.supersedes_version_id
        == "hrdocver-000"
    )


def test_medical_documents_are_narrowly_classified() -> None:

    value = document(
        document_class=HrDocumentClass.MEDICAL_SUPPORTING_DOCUMENT
    )

    assert (
        value.sensitivity
        is HrDocumentSensitivity.HIGHLY_SENSITIVE_HEALTH
    )


def test_identity_documents_are_narrowly_classified() -> None:

    value = document(
        document_class=HrDocumentClass.IDENTITY_SUPPORTING_DOCUMENT
    )

    assert (
        value.sensitivity
        is HrDocumentSensitivity.HIGHLY_SENSITIVE_IDENTITY
    )


def test_provider_references_are_evidence_not_authority() -> None:

    value = document()

    assert value.storage_provider_id == "hr-provider"
    assert value.storage_object_reference == "opaque/hr/obj/1"

    assert not hasattr(
        value,
        "authorize"
    )

    assert not hasattr(
        value,
        "permission"
    )


def test_production_domain_has_no_legal_iam_billing_or_http_imports() -> None:

    import tools.eos.saas.domain.hr_document as module

    source = pathlib.Path(
        module.__file__ or ""
    ).read_text(
        encoding="utf-8",
    )

    forbidden = (
        "tools.eos.legal_operations",
        "tools.eos.auth",
        "tools.eos.saas.billing",
        "tools.eos.billing",
        "fastapi",
        "starlette",
        "pymongo",
        "motor",
    )

    assert all(
        token not in source
        for token in forbidden
    )


# ARTIFACT: tests/unit/test_hr_document.py
# VERSION: v1.0.0-P0-C12F3-HR-DOCUMENT-DOMAIN-CERT
# AUTHORITY BOUNDARY: immutable HR document domain truth only
# STORAGE BOUNDARY: consumes certified binary intent/evidence; performs no provider operations
# RETENTION BOUNDARY: blocking state only; no deletion authorization
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
