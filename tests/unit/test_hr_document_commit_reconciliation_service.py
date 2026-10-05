"""WILSY OS HR Document Commit-Reconciliation Service Direct Certificate.

TITLE: HR Document Commit-Reconciliation Service Direct Certificate
VERSION: v1.0.0-P0-C12F6E3-HR-DOCUMENT-COMMIT-RECONCILIATION-SERVICE-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Certify bounded reconciliation of durable HR document commit uncertainty
against immutable HR document metadata and durable terminal outcome evidence.

AUTHORITY BOUNDARY:
Reconciliation orchestration only. No provider IO, provider deletion, orphan
determination, retention/disposal authority, IAM, HTTP, payroll, billing,
payment, settlement or financial execution authority.

TRANSACTION BOUNDARY:
Caller owns one already-active transaction. The service never starts,
commits, aborts or retries transactions.

CONSISTENCY BOUNDARY:
COMMIT_RECOVERED may be returned only when the exact reconstructed HrDocument
and its durable outcome are written through the same caller-owned transaction.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_commit_reconciliation_service.py

CERTIFICATION / UPDATE DATE: 2026-10-05
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import importlib.util
from typing import Any

import pytest

from tools.eos.saas.domain.hr_document import (
    HrDocumentClass,
)
from tools.eos.saas.domain.hr_document_commit_reconciliation_outcome import (
    HrDocumentCommitReconciliationOutcome,
    record_hr_document_commit_reconciliation_outcome,
)
from tools.eos.saas.domain.hr_document_commit_uncertainty import (
    open_hr_document_commit_uncertainty,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryWriteIntent,
)


MODULE = (
    "tools.eos.saas.hr."
    "hr_document_commit_reconciliation_service"
)


class ActiveSession:
    in_transaction = True


def _uncertainty(
    *,
    tenant_id: str = "tenant-f6e3",
):
    payload = (
        b"WILSY-HR-F6E3-"
        b"RECONCILIATION-SERVICE"
    )

    intent = HrDocumentBinaryWriteIntent(
        tenant_id=tenant_id,
        employee_id="employee-f6e3",
        document_id="document-f6e3",
        document_version_id=(
            "document-version-f6e3"
        ),
        ingestion_reference=(
            "ingestion-f6e3"
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
            "hr/v1/opaque-f6e3-object"
        ),
        object_version_reference=(
            "provider-version-f6e3"
        ),
        provider_integrity_reference=(
            "provider-integrity-f6e3"
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
        14,
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
            "principal-f6e3"
        ),
        retention_until=None,
        legal_hold=False,
        supersedes_version_id=None,
        detected_at=created,
    )


def _reconciled_at():
    return datetime(
        2026,
        10,
        5,
        14,
        1,
        0,
        654321,
        tzinfo=timezone.utc,
    )


class FakeUncertaintyRegistry:
    def __init__(
        self,
        value: Any,
    ) -> None:
        self.value = value
        self.calls: list[
            tuple[
                str,
                str,
                Any,
            ]
        ] = []

    def get(
        self,
        *,
        tenant_id: str,
        uncertainty_id: str,
        session: Any,
    ):
        self.calls.append(
            (
                tenant_id,
                uncertainty_id,
                session,
            )
        )

        return self.value


class FakeOutcomeRegistry:
    def __init__(
        self,
        existing: Any = None,
    ) -> None:
        self.existing = existing
        self.get_calls: list[
            tuple[
                str,
                str,
                Any,
            ]
        ] = []
        self.create_calls: list[
            tuple[
                Any,
                Any,
            ]
        ] = []

    def get_by_uncertainty(
        self,
        *,
        tenant_id: str,
        uncertainty_id: str,
        session: Any,
    ):
        self.get_calls.append(
            (
                tenant_id,
                uncertainty_id,
                session,
            )
        )

        if self.existing is None:
            raise RuntimeError(
                "OUTCOME_NOT_FOUND"
            )

        return self.existing

    def create_or_replay(
        self,
        value: Any,
        *,
        session: Any,
    ):
        self.create_calls.append(
            (
                value,
                session,
            )
        )

        return value


def _module():
    return importlib.import_module(
        MODULE
    )


def test_service_module_exists_before_behavior() -> None:
    assert (
        importlib.util.find_spec(
            MODULE
        )
        is not None
    ), (
        "P0_C12F6E3_EXPECTED_RECONCILIATION_SERVICE_MODULE_MISSING"
    )


def test_existing_outcome_and_exact_document_replays_existing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()

    uncertainty = _uncertainty()
    document = uncertainty.to_hr_document()

    existing = (
        record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=document,
            outcome=(
                HrDocumentCommitReconciliationOutcome
                .COMMIT_RECOVERED
            ),
            reconciled_at=_reconciled_at(),
        )
    )

    session = ActiveSession()

    uncertainty_registry = (
        FakeUncertaintyRegistry(
            uncertainty
        )
    )

    outcome_registry = (
        FakeOutcomeRegistry(
            existing
        )
    )

    document_reads: list[
        tuple[
            str,
            str,
            Any,
        ]
    ] = []

    def get_document(
        tenant_id: str,
        document_version_id: str,
        collection: Any,
        *,
        session: Any,
    ):
        del collection

        document_reads.append(
            (
                tenant_id,
                document_version_id,
                session,
            )
        )

        return document

    monkeypatch.setattr(
        module,
        "get_document_version",
        get_document,
    )

    result = module.reconcile_hr_document_commit_uncertainty(
        tenant_id=uncertainty.tenant_id,
        uncertainty_id=uncertainty.uncertainty_id,
        reconciled_at=(
            _reconciled_at()
            + timedelta(
                hours=1
            )
        ),
        uncertainty_registry=uncertainty_registry,
        outcome_registry=outcome_registry,
        document_collection=object(),
        session=session,
    )

    assert result == existing

    assert (
        outcome_registry.create_calls
        == []
    )

    assert document_reads == [
        (
            uncertainty.tenant_id,
            uncertainty.document_version_id,
            session,
        )
    ]


def test_no_outcome_exact_document_records_confirmed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()

    uncertainty = _uncertainty()
    document = uncertainty.to_hr_document()

    session = ActiveSession()

    outcome_registry = FakeOutcomeRegistry()

    def missing_outcome(
        *,
        tenant_id: str,
        uncertainty_id: str,
        session: Any,
    ):
        del tenant_id
        del uncertainty_id
        del session

        raise (
            module.HrDocumentCommitReconciliationOutcomeRegistryNotFoundError()
        )

    outcome_registry.get_by_uncertainty = missing_outcome  # type: ignore[method-assign]

    monkeypatch.setattr(
        module,
        "get_document_version",
        lambda tenant_id, document_version_id, collection, *, session: document,
    )

    result = module.reconcile_hr_document_commit_uncertainty(
        tenant_id=uncertainty.tenant_id,
        uncertainty_id=uncertainty.uncertainty_id,
        reconciled_at=_reconciled_at(),
        uncertainty_registry=FakeUncertaintyRegistry(
            uncertainty
        ),
        outcome_registry=outcome_registry,
        document_collection=object(),
        session=session,
    )

    assert (
        result.outcome
        is HrDocumentCommitReconciliationOutcome
        .COMMITTED_CONFIRMED
    )

    assert len(
        outcome_registry.create_calls
    ) == 1

    assert (
        outcome_registry.create_calls[0][1]
        is session
    )


def test_no_outcome_absent_document_recovers_document_and_outcome_same_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()

    uncertainty = _uncertainty()

    session = ActiveSession()

    outcome_registry = FakeOutcomeRegistry()

    def missing_outcome(
        *,
        tenant_id: str,
        uncertainty_id: str,
        session: Any,
    ):
        del tenant_id
        del uncertainty_id
        del session

        raise (
            module.HrDocumentCommitReconciliationOutcomeRegistryNotFoundError()
        )

    outcome_registry.get_by_uncertainty = missing_outcome  # type: ignore[method-assign]

    def missing_document(
        tenant_id: str,
        document_version_id: str,
        collection: Any,
        *,
        session: Any,
    ):
        del tenant_id
        del document_version_id
        del collection
        del session

        raise (
            module.HrDocumentRegistryNotFoundError()
        )

    monkeypatch.setattr(
        module,
        "get_document_version",
        missing_document,
    )

    persisted: list[
        tuple[
            Any,
            Any,
        ]
    ] = []

    def persist(
        value: Any,
        collection: Any,
        *,
        session: Any,
    ):
        del collection

        persisted.append(
            (
                value,
                session,
            )
        )

        return value

    monkeypatch.setattr(
        module,
        "persist_document",
        persist,
    )

    result = module.reconcile_hr_document_commit_uncertainty(
        tenant_id=uncertainty.tenant_id,
        uncertainty_id=uncertainty.uncertainty_id,
        reconciled_at=_reconciled_at(),
        uncertainty_registry=FakeUncertaintyRegistry(
            uncertainty
        ),
        outcome_registry=outcome_registry,
        document_collection=object(),
        session=session,
    )

    assert (
        result.outcome
        is HrDocumentCommitReconciliationOutcome
        .COMMIT_RECOVERED
    )

    assert len(
        persisted
    ) == 1

    assert (
        persisted[0][0]
        == uncertainty.to_hr_document()
    )

    assert (
        persisted[0][1]
        is session
    )

    assert len(
        outcome_registry.create_calls
    ) == 1

    assert (
        outcome_registry.create_calls[0][1]
        is session
    )


def test_divergent_existing_document_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()

    uncertainty = _uncertainty()
    expected = uncertainty.to_hr_document()

    object.__setattr__(
        expected,
        "fingerprint",
        "0" * 128,
    )

    outcome_registry = FakeOutcomeRegistry()

    def missing_outcome(
        *,
        tenant_id: str,
        uncertainty_id: str,
        session: Any,
    ):
        del tenant_id
        del uncertainty_id
        del session

        raise (
            module.HrDocumentCommitReconciliationOutcomeRegistryNotFoundError()
        )

    outcome_registry.get_by_uncertainty = missing_outcome  # type: ignore[method-assign]

    monkeypatch.setattr(
        module,
        "get_document_version",
        lambda tenant_id, document_version_id, collection, *, session: expected,
    )

    with pytest.raises(
        module.HrDocumentCommitReconciliationServiceConflictError
    ):
        module.reconcile_hr_document_commit_uncertainty(
            tenant_id=uncertainty.tenant_id,
            uncertainty_id=uncertainty.uncertainty_id,
            reconciled_at=_reconciled_at(),
            uncertainty_registry=FakeUncertaintyRegistry(
                uncertainty
            ),
            outcome_registry=outcome_registry,
            document_collection=object(),
            session=ActiveSession(),
        )

    assert (
        outcome_registry.create_calls
        == []
    )


def test_existing_outcome_missing_document_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()

    uncertainty = _uncertainty()
    document = uncertainty.to_hr_document()

    existing = (
        record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=document,
            outcome=(
                HrDocumentCommitReconciliationOutcome
                .COMMIT_RECOVERED
            ),
            reconciled_at=_reconciled_at(),
        )
    )

    outcome_registry = (
        FakeOutcomeRegistry(
            existing
        )
    )

    def missing_document(
        tenant_id: str,
        document_version_id: str,
        collection: Any,
        *,
        session: Any,
    ):
        del tenant_id
        del document_version_id
        del collection
        del session

        raise (
            module.HrDocumentRegistryNotFoundError()
        )

    monkeypatch.setattr(
        module,
        "get_document_version",
        missing_document,
    )

    with pytest.raises(
        module.HrDocumentCommitReconciliationServiceConflictError
    ):
        module.reconcile_hr_document_commit_uncertainty(
            tenant_id=uncertainty.tenant_id,
            uncertainty_id=uncertainty.uncertainty_id,
            reconciled_at=(
                _reconciled_at()
                + timedelta(
                    hours=1
                )
            ),
            uncertainty_registry=FakeUncertaintyRegistry(
                uncertainty
            ),
            outcome_registry=outcome_registry,
            document_collection=object(),
            session=ActiveSession(),
        )


def test_existing_outcome_fingerprint_binding_mismatch_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()

    uncertainty = _uncertainty()
    document = uncertainty.to_hr_document()

    existing = (
        record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=document,
            outcome=(
                HrDocumentCommitReconciliationOutcome
                .COMMITTED_CONFIRMED
            ),
            reconciled_at=_reconciled_at(),
        )
    )

    object.__setattr__(
        existing,
        "uncertainty_fingerprint",
        "0" * 128,
    )

    monkeypatch.setattr(
        module,
        "get_document_version",
        lambda tenant_id, document_version_id, collection, *, session: document,
    )

    with pytest.raises(
        module.HrDocumentCommitReconciliationServiceConflictError
    ):
        module.reconcile_hr_document_commit_uncertainty(
            tenant_id=uncertainty.tenant_id,
            uncertainty_id=uncertainty.uncertainty_id,
            reconciled_at=(
                _reconciled_at()
                + timedelta(
                    hours=1
                )
            ),
            uncertainty_registry=FakeUncertaintyRegistry(
                uncertainty
            ),
            outcome_registry=FakeOutcomeRegistry(
                existing
            ),
            document_collection=object(),
            session=ActiveSession(),
        )


def test_service_requires_active_transaction_before_registry_read() -> None:
    module = _module()

    uncertainty_registry = (
        FakeUncertaintyRegistry(
            _uncertainty()
        )
    )

    class Inactive:
        in_transaction = False

    with pytest.raises(
        module.HrDocumentCommitReconciliationServiceTransactionRequiredError
    ):
        module.reconcile_hr_document_commit_uncertainty(
            tenant_id="tenant-f6e3",
            uncertainty_id="uncertainty-f6e3",
            reconciled_at=_reconciled_at(),
            uncertainty_registry=uncertainty_registry,
            outcome_registry=FakeOutcomeRegistry(),
            document_collection=object(),
            session=Inactive(),
        )

    assert (
        uncertainty_registry.calls
        == []
    )


def test_service_does_not_expose_transaction_lifecycle_or_provider_methods() -> None:
    module = _module()

    forbidden = {
        "start_transaction",
        "commit_transaction",
        "abort_transaction",
        "retry_transaction",
        "delete_provider",
        "write_provider",
        "reconcile_provider",
    }

    assert forbidden.isdisjoint(
        {
            name
            for name in dir(
                module
            )
            if not name.startswith(
                "_"
            )
        }
    )


# ARTIFACT: tests/unit/test_hr_document_commit_reconciliation_service.py
# VERSION: v1.0.0-P0-C12F6E3-HR-DOCUMENT-COMMIT-RECONCILIATION-SERVICE-CERT
# CERTIFICATE: bounded HR document commit reconciliation
# EXISTING DURABLE OUTCOME: replay only after exact document correlation
# COMMITTED_CONFIRMED: exact pre-existing document only
# COMMIT_RECOVERED: exact document + outcome same caller-owned transaction
# UNKNOWN TRANSACTION OUTCOME: no synthetic resolution
# PROVIDER IO AUTHORITY: none
# ORPHAN PROOF AUTHORITY: none
# PROVIDER DELETE AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
