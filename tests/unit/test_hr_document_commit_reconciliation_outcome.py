"""WILSY OS HR Commit-Reconciliation Outcome Direct Certificate.

TITLE: HR Document Commit-Reconciliation Outcome Direct Certificate
VERSION: v1.0.0-P0-C12F6E1-HR-DOCUMENT-COMMIT-RECONCILIATION-OUTCOME-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Certify immutable durable evidence of a later reconciliation proof for one
frozen HR document commit uncertainty.

AUTHORITY BOUNDARY:
Pure immutable reconciliation-outcome evidence only. No persistence,
provider IO, provider deletion, orphan determination, IAM, HTTP,
retention/disposal, billing, payment, settlement or financial execution.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_commit_reconciliation_outcome.py

CERTIFICATION / UPDATE DATE: 2026-10-05
"""

from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import FrozenInstanceError
import importlib
import importlib.util

import pytest

from tools.eos.saas.domain.hr_document import (
    HrDocumentClass,
)
from tools.eos.saas.domain.hr_document_commit_uncertainty import (
    open_hr_document_commit_uncertainty,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryWriteIntent,
)

import hashlib


MODULE = (
    "tools.eos.saas.domain."
    "hr_document_commit_reconciliation_outcome"
)

EXPECTED_VERSION = (
    "v1.0.0-P0-C12F6E1-"
    "HR-DOCUMENT-COMMIT-RECONCILIATION-OUTCOME"
)

EXPECTED_SCHEMA = (
    "WILSY-HR-DOCUMENT-COMMIT-RECONCILIATION-OUTCOME/V1"
)

EXPECTED_FIELDS = {
    "outcome_id",
    "tenant_id",
    "uncertainty_id",
    "uncertainty_fingerprint",
    "document_version_id",
    "document_fingerprint",
    "outcome",
    "reconciled_at",
    "schema",
    "outcome_version",
    "fingerprint",
}

FORBIDDEN_FIELDS = {
    "orphan_proven",
    "provider_delete_authorized",
    "delete_authorized",
    "available",
    "authorized_availability",
    "mongo_commit_failed",
    "provider_object_missing",
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


def _uncertainty():
    payload = (
        b"WILSY-HR-F6E1-"
        b"RECONCILIATION-OUTCOME"
    )

    intent = HrDocumentBinaryWriteIntent(
        tenant_id="tenant-f6e1",
        employee_id="employee-f6e1",
        document_id="document-f6e1",
        document_version_id=(
            "document-version-f6e1"
        ),
        ingestion_reference=(
            "ingestion-f6e1"
        ),
        media_type="application/pdf",
        original_filename=(
            "employment-contract.pdf"
        ),
        admitted_max_content_length=4096,
    )

    evidence = HrDocumentBinaryObjectEvidence(
        provider_name="aws_s3",
        storage_reference=(
            "hr/v1/opaque-f6e1-object"
        ),
        object_version_reference=(
            "provider-version-f6e1"
        ),
        provider_integrity_reference=(
            "provider-integrity-f6e1"
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

    created = datetime(
        2026,
        10,
        5,
        12,
        0,
        0,
        123456,
        tzinfo=timezone.utc,
    )

    return open_hr_document_commit_uncertainty(
        intent=intent,
        object_evidence=evidence,
        document_class=(
            HrDocumentClass.EMPLOYMENT_CONTRACT
        ),
        created_at=created,
        created_by_principal_id=(
            "principal-f6e1"
        ),
        retention_until=None,
        legal_hold=False,
        supersedes_version_id=None,
        detected_at=created,
    )


def _document():
    return _uncertainty().to_hr_document()


def _reconciled_at():
    return datetime(
        2026,
        10,
        5,
        12,
        1,
        0,
        654321,
        tzinfo=timezone.utc,
    )


def test_domain_module_exists_before_behavior() -> None:
    assert (
        importlib.util.find_spec(
            MODULE
        )
        is not None
    ), (
        "P0_C12F6E1_EXPECTED_OUTCOME_DOMAIN_MISSING"
    )


def test_closed_outcome_vocabulary() -> None:
    module = _module()

    assert {
        item.value
        for item
        in module.HrDocumentCommitReconciliationOutcome
    } == {
        "COMMITTED_CONFIRMED",
        "COMMIT_RECOVERED",
    }


def test_exact_schema_and_no_later_authority_fields() -> None:
    module = _module()

    uncertainty = _uncertainty()
    document = uncertainty.to_hr_document()

    value = (
        module.record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=document,
            outcome=(
                module.HrDocumentCommitReconciliationOutcome
                .COMMITTED_CONFIRMED
            ),
            reconciled_at=_reconciled_at(),
        )
    )

    assert module.VERSION == EXPECTED_VERSION
    assert module.SCHEMA == EXPECTED_SCHEMA

    payload = value.to_dict()

    assert set(
        payload
    ) == EXPECTED_FIELDS

    assert not (
        set(
            payload
        )
        & FORBIDDEN_FIELDS
    )


def test_exact_uncertainty_and_document_binding() -> None:
    module = _module()

    uncertainty = _uncertainty()
    document = uncertainty.to_hr_document()

    value = (
        module.record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=document,
            outcome=(
                module.HrDocumentCommitReconciliationOutcome
                .COMMIT_RECOVERED
            ),
            reconciled_at=_reconciled_at(),
        )
    )

    assert (
        value.tenant_id
        == uncertainty.tenant_id
    )

    assert (
        value.uncertainty_id
        == uncertainty.uncertainty_id
    )

    assert (
        value.uncertainty_fingerprint
        == uncertainty.fingerprint
    )

    assert (
        value.document_version_id
        == document.document_version_id
    )

    assert (
        value.document_fingerprint
        == document.fingerprint
    )


def test_divergent_document_rejected() -> None:
    module = _module()

    uncertainty = _uncertainty()
    document = uncertainty.to_hr_document()

    wrong_uncertainty = _uncertainty()
    wrong_document = wrong_uncertainty.to_hr_document()

    # Deliberately corrupt document correlation while preserving type.
    object.__setattr__(
        wrong_document,
        "fingerprint",
        "0" * 128,
    )

    with pytest.raises(
        module.HrDocumentCommitReconciliationOutcomeError
    ):
        module.record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=wrong_document,
            outcome=(
                module.HrDocumentCommitReconciliationOutcome
                .COMMITTED_CONFIRMED
            ),
            reconciled_at=_reconciled_at(),
        )


def test_reconciliation_cannot_precede_uncertainty_detection() -> None:
    module = _module()

    uncertainty = _uncertainty()
    document = uncertainty.to_hr_document()

    with pytest.raises(
        module.HrDocumentCommitReconciliationOutcomeError
    ):
        module.record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=document,
            outcome=(
                module.HrDocumentCommitReconciliationOutcome
                .COMMITTED_CONFIRMED
            ),
            reconciled_at=(
                uncertainty.detected_at
            ),
        )


def test_exact_replay_is_deterministic() -> None:
    module = _module()

    uncertainty = _uncertainty()
    document = uncertainty.to_hr_document()

    first = (
        module.record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=document,
            outcome=(
                module.HrDocumentCommitReconciliationOutcome
                .COMMITTED_CONFIRMED
            ),
            reconciled_at=_reconciled_at(),
        )
    )

    second = (
        module.record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=document,
            outcome=(
                module.HrDocumentCommitReconciliationOutcome
                .COMMITTED_CONFIRMED
            ),
            reconciled_at=_reconciled_at(),
        )
    )

    assert first == second
    assert first.outcome_id == second.outcome_id
    assert first.fingerprint == second.fingerprint


def test_different_outcome_changes_identity() -> None:
    module = _module()

    uncertainty = _uncertainty()
    document = uncertainty.to_hr_document()

    confirmed = (
        module.record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=document,
            outcome=(
                module.HrDocumentCommitReconciliationOutcome
                .COMMITTED_CONFIRMED
            ),
            reconciled_at=_reconciled_at(),
        )
    )

    recovered = (
        module.record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=document,
            outcome=(
                module.HrDocumentCommitReconciliationOutcome
                .COMMIT_RECOVERED
            ),
            reconciled_at=_reconciled_at(),
        )
    )

    assert (
        confirmed.outcome_id
        != recovered.outcome_id
    )

    assert (
        confirmed.fingerprint
        != recovered.fingerprint
    )


def test_strict_round_trip_and_fingerprint_tamper_rejected() -> None:
    module = _module()

    uncertainty = _uncertainty()
    document = uncertainty.to_hr_document()

    value = (
        module.record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=document,
            outcome=(
                module.HrDocumentCommitReconciliationOutcome
                .COMMITTED_CONFIRMED
            ),
            reconciled_at=_reconciled_at(),
        )
    )

    payload = value.to_dict()

    assert (
        module.HrDocumentCommitReconciliationOutcomeEvidence
        .from_dict(
            payload
        )
        == value
    )

    payload[
        "fingerprint"
    ] = "0" * 128

    with pytest.raises(
        module.HrDocumentCommitReconciliationOutcomeError
    ):
        module.HrDocumentCommitReconciliationOutcomeEvidence.from_dict(
            payload
        )


def test_outcome_is_frozen() -> None:
    module = _module()

    uncertainty = _uncertainty()
    document = uncertainty.to_hr_document()

    value = (
        module.record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=document,
            outcome=(
                module.HrDocumentCommitReconciliationOutcome
                .COMMITTED_CONFIRMED
            ),
            reconciled_at=_reconciled_at(),
        )
    )

    with pytest.raises(
        (
            FrozenInstanceError,
            AttributeError,
        )
    ):
        value.tenant_id = "mutated"  # type: ignore[misc]


# ARTIFACT: tests/unit/test_hr_document_commit_reconciliation_outcome.py
# VERSION: v1.0.0-P0-C12F6E1-HR-DOCUMENT-COMMIT-RECONCILIATION-OUTCOME-CERT
# CERTIFICATE: immutable durable reconciliation-outcome evidence
# OUTCOMES: COMMITTED_CONFIRMED / COMMIT_RECOVERED only
# PROVIDER IO AUTHORITY: none
# ORPHAN PROOF AUTHORITY: none
# PROVIDER DELETE AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
