"""WILSY OS HR Document Commit-Uncertainty Direct Certificate.

TITLE: HR Document Commit-Uncertainty Direct Certificate
VERSION: v1.0.0-P0-C12F6C-HR-DOCUMENT-COMMIT-UNCERTAINTY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS
PURPOSE: Certify immutable provider-complete / Mongo-unproven HR
document evidence and exact restart-safe HrDocument reconstruction.
ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_commit_uncertainty.py
CERTIFICATION / UPDATE DATE: 2026-10-05
AUTHORITY BOUNDARY: Pure-domain evidence only; no persistence, S3
execution, IAM, HTTP, deletion, billing, payment or settlement authority.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import importlib.util

import pytest

from tools.eos.saas.domain.hr_document import (
    HrDocument,
    HrDocumentClass,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryWriteIntent,
)


MODULE = (
    "tools.eos.saas.domain."
    "hr_document_commit_uncertainty"
)

EXPECTED_VERSION = (
    "v1.0.0-P0-C12F6C-"
    "HR-DOCUMENT-COMMIT-UNCERTAINTY"
)

EXPECTED_SCHEMA = (
    "WILSY-HR-DOCUMENT-COMMIT-UNCERTAINTY/V1"
)

EXPECTED_FIELDS = {
    "uncertainty_id",
    "tenant_id",
    "employee_id",
    "document_id",
    "document_version_id",
    "ingestion_reference",
    "media_type",
    "original_filename",
    "admitted_max_content_length",
    "document_class",
    "created_at",
    "created_by_principal_id",
    "retention_until",
    "legal_hold",
    "supersedes_version_id",
    "provider_name",
    "storage_reference",
    "object_version_reference",
    "provider_integrity_reference",
    "write_intent_fingerprint",
    "content_length",
    "content_fingerprint",
    "detected_at",
    "schema",
    "uncertainty_version",
    "fingerprint",
}

FORBIDDEN_AUTHORITY_FIELDS = {
    "available",
    "authorized_availability",
    "orphan_proven",
    "provider_delete_authorized",
    "delete_authorized",
    "iam_authorized",
    "billing_authorized",
    "payment_authorized",
    "settlement_authorized",
    "financial_execution_authorized",
}


def _module():
    return importlib.import_module(
        MODULE
    )


def _payload() -> bytes:
    return (
        b"WILSY-HR-COMMIT-UNCERTAINTY-"
        b"TEST-EVIDENCE"
    )


def _intent(
    *,
    ingestion_reference: str = "ingestion-f6c-001",
) -> HrDocumentBinaryWriteIntent:
    return HrDocumentBinaryWriteIntent(
        tenant_id="tenant-f6c",
        employee_id="employee-f6c",
        document_id="document-f6c",
        document_version_id="document-version-f6c",
        ingestion_reference=ingestion_reference,
        media_type="application/pdf",
        original_filename="employment-contract.pdf",
        admitted_max_content_length=4096,
    )


def _evidence(
    intent: HrDocumentBinaryWriteIntent,
    *,
    object_version_reference: str = "provider-version-f6c-001",
) -> HrDocumentBinaryObjectEvidence:
    payload = _payload()

    return HrDocumentBinaryObjectEvidence(
        provider_name="aws_s3",
        storage_reference=(
            "hr-documents/v1/"
            "opaque-certification-object"
        ),
        object_version_reference=(
            object_version_reference
        ),
        provider_integrity_reference=(
            "provider-integrity-f6c"
        ),
        write_intent_fingerprint=(
            intent.fingerprint
        ),
        content_length=len(
            payload
        ),
        content_fingerprint=(
            hashlib.sha3_512(
                payload
            ).hexdigest()
        ),
    )


def _times():
    created = datetime(
        2026,
        10,
        5,
        8,
        0,
        0,
        123456,
        tzinfo=timezone.utc,
    )

    detected = created + timedelta(
        seconds=2
    )

    retention = created + timedelta(
        days=365
    )

    return (
        created,
        detected,
        retention,
    )


def _open(
    *,
    intent: HrDocumentBinaryWriteIntent | None = None,
    evidence: HrDocumentBinaryObjectEvidence | None = None,
    document_class: HrDocumentClass = (
        HrDocumentClass.EMPLOYMENT_CONTRACT
    ),
    supersedes_version_id: str | None = None,
):
    module = _module()

    write_intent = (
        intent
        if intent is not None
        else _intent()
    )

    object_evidence = (
        evidence
        if evidence is not None
        else _evidence(
            write_intent
        )
    )

    created, detected, retention = _times()

    return module.open_hr_document_commit_uncertainty(
        intent=write_intent,
        object_evidence=object_evidence,
        document_class=document_class,
        created_at=created,
        created_by_principal_id="principal-f6c",
        retention_until=retention,
        legal_hold=False,
        supersedes_version_id=(
            supersedes_version_id
        ),
        detected_at=detected,
    )


def test_domain_module_exists_before_behavior() -> None:
    assert (
        importlib.util.find_spec(
            MODULE
        )
        is not None
    ), (
        "P0_C12F6C_EXPECTED_DOMAIN_MODULE_MISSING"
    )


def test_version_schema_and_exact_serialized_fields() -> None:
    module = _module()

    assert module.VERSION == EXPECTED_VERSION
    assert module.SCHEMA == EXPECTED_SCHEMA

    uncertainty = _open()

    serialized = uncertainty.to_dict()

    assert set(
        serialized
    ) == EXPECTED_FIELDS

    assert not (
        set(serialized)
        & FORBIDDEN_AUTHORITY_FIELDS
    )

    assert all(
        not isinstance(
            value,
            (
                bytes,
                bytearray,
                memoryview,
            ),
        )
        for value in serialized.values()
    )


def test_exact_replay_is_deterministic() -> None:
    first = _open()
    second = _open()

    assert first == second
    assert (
        first.uncertainty_id
        == second.uncertainty_id
    )
    assert (
        first.fingerprint
        == second.fingerprint
    )


def test_provider_version_changes_uncertainty_identity() -> None:
    intent = _intent()

    first = _open(
        intent=intent,
        evidence=_evidence(
            intent,
            object_version_reference=(
                "provider-version-f6c-001"
            ),
        ),
    )

    second = _open(
        intent=intent,
        evidence=_evidence(
            intent,
            object_version_reference=(
                "provider-version-f6c-002"
            ),
        ),
    )

    assert (
        first.uncertainty_id
        != second.uncertainty_id
    )

    assert (
        first.fingerprint
        != second.fingerprint
    )


def test_round_trip_is_strict_and_exact() -> None:
    module = _module()

    uncertainty = _open()

    hydrated = (
        module.HrDocumentCommitUncertainty
        .from_dict(
            uncertainty.to_dict()
        )
    )

    assert hydrated == uncertainty
    assert (
        hydrated.to_dict()
        == uncertainty.to_dict()
    )


def test_uncertainty_is_frozen() -> None:
    uncertainty = _open()

    with pytest.raises(
        (
            FrozenInstanceError,
            AttributeError,
        )
    ):
        uncertainty.tenant_id = "mutated"  # type: ignore[misc]


def test_divergent_object_evidence_scope_fails_closed() -> None:
    module = _module()

    first_intent = _intent(
        ingestion_reference="ingestion-f6c-001"
    )

    second_intent = _intent(
        ingestion_reference="ingestion-f6c-002"
    )

    wrong_evidence = _evidence(
        second_intent
    )

    created, detected, retention = _times()

    with pytest.raises(
        module.HrDocumentCommitUncertaintyError
    ):
        module.open_hr_document_commit_uncertainty(
            intent=first_intent,
            object_evidence=wrong_evidence,
            document_class=(
                HrDocumentClass.EMPLOYMENT_CONTRACT
            ),
            created_at=created,
            created_by_principal_id="principal-f6c",
            retention_until=retention,
            legal_hold=False,
            supersedes_version_id=None,
            detected_at=detected,
        )


def test_detection_cannot_precede_document_creation() -> None:
    module = _module()

    intent = _intent()
    evidence = _evidence(
        intent
    )

    created, _, retention = _times()

    with pytest.raises(
        module.HrDocumentCommitUncertaintyError
    ):
        module.open_hr_document_commit_uncertainty(
            intent=intent,
            object_evidence=evidence,
            document_class=(
                HrDocumentClass.EMPLOYMENT_CONTRACT
            ),
            created_at=created,
            created_by_principal_id="principal-f6c",
            retention_until=retention,
            legal_hold=False,
            supersedes_version_id=None,
            detected_at=(
                created
                - timedelta(
                    microseconds=1
                )
            ),
        )


def test_retention_before_creation_fails_closed() -> None:
    module = _module()

    intent = _intent()
    evidence = _evidence(
        intent
    )

    created, detected, _ = _times()

    with pytest.raises(
        module.HrDocumentCommitUncertaintyError
    ):
        module.open_hr_document_commit_uncertainty(
            intent=intent,
            object_evidence=evidence,
            document_class=(
                HrDocumentClass.EMPLOYMENT_CONTRACT
            ),
            created_at=created,
            created_by_principal_id="principal-f6c",
            retention_until=(
                created
                - timedelta(
                    microseconds=1
                )
            ),
            legal_hold=False,
            supersedes_version_id=None,
            detected_at=detected,
        )


def test_self_supersession_fails_closed() -> None:
    module = _module()

    with pytest.raises(
        module.HrDocumentCommitUncertaintyError
    ):
        _open(
            supersedes_version_id=(
                "document-version-f6c"
            )
        )


def test_uncertainty_reconstructs_exact_hr_document_without_caller_provider_coordinates() -> None:
    uncertainty = _open()

    document = (
        uncertainty.to_hr_document()
    )

    assert type(document) is HrDocument

    assert (
        document.tenant_id
        == uncertainty.tenant_id
    )

    assert (
        document.employee_id
        == uncertainty.employee_id
    )

    assert (
        document.document_id
        == uncertainty.document_id
    )

    assert (
        document.document_version_id
        == uncertainty.document_version_id
    )

    assert (
        document.storage_provider_id
        == uncertainty.provider_name
    )

    assert (
        document.storage_object_reference
        == uncertainty.storage_reference
    )

    assert (
        document.object_version_reference
        == uncertainty.object_version_reference
    )

    assert (
        document.provider_integrity_reference
        == uncertainty.provider_integrity_reference
    )

    assert (
        document.byte_length
        == uncertainty.content_length
    )

    assert (
        document.content_digest_sha3_512
        == uncertainty.content_fingerprint
    )


def test_serialized_fingerprint_tamper_fails_closed() -> None:
    module = _module()

    uncertainty = _open()

    payload = uncertainty.to_dict()

    payload["fingerprint"] = (
        "0" * 128
    )

    with pytest.raises(
        module.HrDocumentCommitUncertaintyError
    ):
        module.HrDocumentCommitUncertainty.from_dict(
            payload
        )

# ARTIFACT: tests/unit/test_hr_document_commit_uncertainty.py
# VERSION: v1.0.0-P0-C12F6C-HR-DOCUMENT-COMMIT-UNCERTAINTY-CERT
# CERTIFICATE: pure immutable HR commit-uncertainty domain
# RAW BYTES: forbidden
# LEGAL AUTHORITY REUSE: none
# PROVIDER DELETE AUTHORITY: none
# IAM AUTHORITY: none
# HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
