"""WILSY OS HR Document Orchestration Service Direct Certificate.

TITLE: HR Document Orchestration Service Direct Certificate
VERSION: v1.0.0-P0-C12F6F-HR-DOCUMENT-ORCHESTRATION-SERVICE-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Freeze the two-plane orchestration contract that accepts bounded HR document
bytes, verifies employee scope, executes the certified provider write exactly
once, and then owns Mongo metadata transaction lifecycle and durable
commit-uncertainty escalation.

TRANSACTION OWNER:
F6F owns Mongo session creation, primary transaction start/commit/abort,
bounded whole-transaction retry, unknown-commit classification, and the
separate uncertainty-persistence transaction.

PROVIDER BOUNDARY:
The storage adapter owns provider execution. Mongo retry never repeats provider
begin/write/complete. F6F never fabricates provider evidence or deletion truth.

RECONCILIATION BOUNDARY:
Provider completion plus unproven Mongo metadata commit produces durable F6C/F6D
uncertainty. F6F does not resolve that uncertainty; F6E3 remains the certified
reconciliation owner.

AUTHORITY BOUNDARY:
No IAM issuance, HTTP authority, provider deletion, orphan proof, payroll
payment, billing, settlement, or financial execution authority.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_service.py

CERTIFICATION / UPDATE DATE: 2026-10-05
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib
import importlib.util
from typing import Any

import pytest

from tools.eos.saas.domain.hr_document import (
    HrDocumentClass,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryChunkEvidence,
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryWriteIntent,
    HrDocumentBinaryWriteSession,
)


MODULE = (
    "tools.eos.saas.hr."
    "hr_document_service"
)


class FakeEmployee:
    def __init__(
        self,
        *,
        employee_id: str,
        tenant_id: str,
    ) -> None:
        self.employeeId = employee_id
        self.tenantId = tenant_id


class FakeEmployeeRegistry:
    def __init__(
        self,
        employee: Any,
    ) -> None:
        self.employee = employee
        self.calls: list[
            tuple[
                str,
                str,
            ]
        ] = []

    def get_employee_by_id(
        self,
        employee_id: str,
        tenant_id: str,
    ):
        self.calls.append(
            (
                employee_id,
                tenant_id,
            )
        )

        return self.employee


class FakeStorage:
    def __init__(
        self,
        *,
        fail_write: bool = False,
    ) -> None:
        self.fail_write = fail_write
        self.events: list[str] = []
        self.begin_calls = 0
        self.complete_calls = 0
        self.inspect_calls = 0
        self.abort_calls = 0

    def begin(
        self,
        intent: HrDocumentBinaryWriteIntent,
    ) -> HrDocumentBinaryWriteSession:
        self.events.append(
            "provider.begin"
        )

        self.begin_calls += 1

        return HrDocumentBinaryWriteSession(
            provider_name="fake_s3",
            write_session_reference=(
                "session-f6f"
            ),
            storage_reference=(
                "opaque/f6f/object"
            ),
            write_intent_fingerprint=(
                intent.fingerprint
            ),
        )

    def write_chunk(
        self,
        intent: HrDocumentBinaryWriteIntent,
        session: HrDocumentBinaryWriteSession,
        *,
        sequence: int,
        chunk: bytes,
    ) -> HrDocumentBinaryChunkEvidence:
        del intent
        del session

        self.events.append(
            f"provider.write:{sequence}"
        )

        if self.fail_write:
            raise RuntimeError(
                "PROVIDER_WRITE_FAILED"
            )

        return HrDocumentBinaryChunkEvidence(
            sequence=sequence,
            chunk_length=len(
                chunk
            ),
            provider_part_reference=(
                f"part-{sequence}"
            ),
        )

    def complete(
        self,
        intent: HrDocumentBinaryWriteIntent,
        session: HrDocumentBinaryWriteSession,
        chunks: tuple[
            HrDocumentBinaryChunkEvidence,
            ...,
        ],
        *,
        observed_length: int,
        observed_fingerprint: str,
    ) -> HrDocumentBinaryObjectEvidence:
        del session
        del chunks

        self.events.append(
            "provider.complete"
        )

        self.complete_calls += 1

        return HrDocumentBinaryObjectEvidence(
            provider_name="fake_s3",
            storage_reference=(
                "opaque/f6f/object"
            ),
            object_version_reference=(
                "provider-version-f6f"
            ),
            provider_integrity_reference=(
                "integrity-f6f"
            ),
            write_intent_fingerprint=(
                intent.fingerprint
            ),
            content_length=(
                observed_length
            ),
            content_fingerprint=(
                observed_fingerprint
            ),
        )

    def inspect(
        self,
        intent: HrDocumentBinaryWriteIntent,
        evidence: HrDocumentBinaryObjectEvidence,
    ) -> HrDocumentBinaryObjectEvidence:
        del intent

        self.events.append(
            "provider.inspect"
        )

        self.inspect_calls += 1

        return evidence

    def abort(
        self,
        intent: HrDocumentBinaryWriteIntent,
        session: HrDocumentBinaryWriteSession,
    ) -> None:
        del intent
        del session

        self.events.append(
            "provider.abort"
        )

        self.abort_calls += 1


class FakeSession:
    def __init__(
        self,
        owner: "FakeMongoClient",
        ordinal: int,
    ) -> None:
        self.owner = owner
        self.ordinal = ordinal
        self.in_transaction = False

    def __enter__(
        self,
    ) -> "FakeSession":
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc: Any,
        tb: Any,
    ) -> None:
        del exc_type
        del exc
        del tb

    def start_transaction(
        self,
    ) -> None:
        self.owner.events.append(
            f"mongo.start:{self.ordinal}"
        )

        self.in_transaction = True

    def commit_transaction(
        self,
    ) -> None:
        self.owner.events.append(
            f"mongo.commit:{self.ordinal}"
        )

        outcome = self.owner.commit_outcomes.pop(
            0
        )

        if isinstance(
            outcome,
            BaseException,
        ):
            raise outcome

        self.in_transaction = False

    def abort_transaction(
        self,
    ) -> None:
        self.owner.events.append(
            f"mongo.abort:{self.ordinal}"
        )

        self.in_transaction = False


class FakeMongoClient:
    def __init__(
        self,
        commit_outcomes: list[
            object
        ],
    ) -> None:
        self.commit_outcomes = list(
            commit_outcomes
        )

        self.events: list[str] = []
        self.sessions = 0

    def start_session(
        self,
    ) -> FakeSession:
        self.sessions += 1

        self.events.append(
            f"mongo.session:{self.sessions}"
        )

        return FakeSession(
            self,
            self.sessions,
        )


class LabeledMongoError(
    RuntimeError
):
    def __init__(
        self,
        label: str,
    ) -> None:
        super().__init__(
            label
        )

        self.label = label

    def has_error_label(
        self,
        label: str,
    ) -> bool:
        return label == self.label


def _module():
    return importlib.import_module(
        MODULE
    )


def _intent() -> HrDocumentBinaryWriteIntent:
    return HrDocumentBinaryWriteIntent(
        tenant_id="tenant-f6f",
        employee_id="employee-f6f",
        document_id="document-f6f",
        document_version_id=(
            "document-version-f6f"
        ),
        ingestion_reference=(
            "ingestion-f6f"
        ),
        media_type="application/pdf",
        original_filename=(
            "employment-contract.pdf"
        ),
        admitted_max_content_length=4096,
    )


def _chunks() -> tuple[
    bytes,
    ...,
]:
    return (
        b"%PDF-WILSY-F6F-A",
        b"-WILSY-F6F-B%%EOF",
    )


def _created_at() -> datetime:
    return datetime(
        2026,
        10,
        5,
        14,
        30,
        0,
        123456,
        tzinfo=timezone.utc,
    )


def _employee_registry():
    intent = _intent()

    return FakeEmployeeRegistry(
        FakeEmployee(
            employee_id=intent.employee_id,
            tenant_id=intent.tenant_id,
        )
    )


def _invoke(
    module: Any,
    *,
    storage: FakeStorage | None = None,
    employee_registry: Any = None,
    mongo_client: Any = None,
):
    intent = _intent()

    return module.orchestrate_hr_document_ingestion(
        intent=intent,
        chunks=_chunks(),
        document_class=(
            HrDocumentClass.EMPLOYMENT_CONTRACT
        ),
        created_at=_created_at(),
        created_by_principal_id=(
            "principal-f6f"
        ),
        retention_until=None,
        legal_hold=False,
        supersedes_version_id=None,
        storage=(
            storage
            or FakeStorage()
        ),
        employee_registry=(
            employee_registry
            or _employee_registry()
        ),
        mongo_client=(
            mongo_client
            or FakeMongoClient(
                [
                    None,
                ]
            )
        ),
        document_collection=object(),
        uncertainty_collection=object(),
        max_transaction_attempts=3,
    )


def test_service_module_exists_before_behavior() -> None:
    assert (
        importlib.util.find_spec(
            MODULE
        )
        is not None
    ), (
        "P0_C12F6F_EXPECTED_HR_DOCUMENT_SERVICE_MODULE_MISSING"
    )


def test_employee_exact_binding_is_checked_before_provider_begin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()

    events: list[str] = []

    class EmployeeRegistry(
        FakeEmployeeRegistry
    ):
        def get_employee_by_id(
            self,
            employee_id: str,
            tenant_id: str,
        ):
            events.append(
                "employee.lookup"
            )

            return super().get_employee_by_id(
                employee_id,
                tenant_id,
            )

    storage = FakeStorage()

    original_begin = storage.begin

    def begin(
        intent: HrDocumentBinaryWriteIntent,
    ):
        events.append(
            "provider.begin"
        )

        return original_begin(
            intent
        )

    storage.begin = begin  # type: ignore[method-assign]

    monkeypatch.setattr(
        module,
        "persist_document",
        lambda value, collection, *, session: value,
    )

    result = _invoke(
        module,
        storage=storage,
        employee_registry=EmployeeRegistry(
            FakeEmployee(
                employee_id="employee-f6f",
                tenant_id="tenant-f6f",
            )
        ),
    )

    assert result.document is not None

    assert events[:2] == [
        "employee.lookup",
        "provider.begin",
    ]


def test_missing_or_cross_tenant_employee_rejects_before_provider_io() -> None:
    module = _module()

    for employee in (
        None,
        FakeEmployee(
            employee_id="employee-f6f",
            tenant_id="tenant-neighbor",
        ),
    ):
        storage = FakeStorage()

        with pytest.raises(
            module.HrDocumentServiceScopeError
        ):
            _invoke(
                module,
                storage=storage,
                employee_registry=FakeEmployeeRegistry(
                    employee
                ),
            )

        assert (
            storage.begin_calls
            == 0
        )


def test_provider_stream_is_completed_and_inspected_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()

    storage = FakeStorage()

    monkeypatch.setattr(
        module,
        "persist_document",
        lambda value, collection, *, session: value,
    )

    result = _invoke(
        module,
        storage=storage,
    )

    assert result.document is not None

    assert storage.events == [
        "provider.begin",
        "provider.write:0",
        "provider.write:1",
        "provider.complete",
        "provider.inspect",
    ]

    assert storage.begin_calls == 1
    assert storage.complete_calls == 1
    assert storage.inspect_calls == 1


def test_successful_metadata_commit_returns_committed_and_no_uncertainty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()

    persisted: list[
        tuple[
            Any,
            Any,
        ]
    ] = []

    monkeypatch.setattr(
        module,
        "persist_document",
        lambda value, collection, *, session: (
            persisted.append(
                (
                    value,
                    session,
                )
            )
            or value
        ),
    )

    client = FakeMongoClient(
        [
            None,
        ]
    )

    result = _invoke(
        module,
        mongo_client=client,
    )

    assert (
        result.status
        is module.HrDocumentIngestionStatus.COMMITTED
    )

    assert result.document is not None
    assert result.uncertainty is None
    assert len(persisted) == 1

    assert client.events == [
        "mongo.session:1",
        "mongo.start:1",
        "mongo.commit:1",
    ]


def test_transient_primary_transaction_retry_does_not_repeat_provider_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()

    storage = FakeStorage()

    attempts = 0

    def persist(
        value: Any,
        collection: Any,
        *,
        session: Any,
    ):
        del collection
        del session

        nonlocal attempts
        attempts += 1

        if attempts == 1:
            raise module.HrDocumentRegistryRetryRequiredError()

        return value

    monkeypatch.setattr(
        module,
        "persist_document",
        persist,
    )

    client = FakeMongoClient(
        [
            None,
        ]
    )

    result = _invoke(
        module,
        storage=storage,
        mongo_client=client,
    )

    assert (
        result.status
        is module.HrDocumentIngestionStatus.COMMITTED
    )

    assert attempts == 2

    assert storage.begin_calls == 1
    assert storage.complete_calls == 1
    assert storage.inspect_calls == 1

    assert client.sessions == 2


def test_unknown_primary_commit_never_repeats_provider_and_records_uncertainty_in_fresh_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()

    storage = FakeStorage()

    persisted_uncertainties: list[
        tuple[
            Any,
            Any,
        ]
    ] = []

    class UncertaintyRegistry:
        def __init__(
            self,
            collection: Any,
        ) -> None:
            del collection

        def create_or_replay(
            self,
            value: Any,
            *,
            session: Any,
        ):
            persisted_uncertainties.append(
                (
                    value,
                    session,
                )
            )

            return value

    monkeypatch.setattr(
        module,
        "persist_document",
        lambda value, collection, *, session: value,
    )

    monkeypatch.setattr(
        module,
        "HrDocumentCommitUncertaintyRegistry",
        UncertaintyRegistry,
    )

    client = FakeMongoClient(
        [
            LabeledMongoError(
                "UnknownTransactionCommitResult"
            ),
            None,
        ]
    )

    result = _invoke(
        module,
        storage=storage,
        mongo_client=client,
    )

    assert (
        result.status
        is module.HrDocumentIngestionStatus.RECONCILIATION_REQUIRED
    )

    assert result.document is not None
    assert result.uncertainty is not None

    assert len(
        persisted_uncertainties
    ) == 1

    assert (
        persisted_uncertainties[0][1].ordinal
        == 2
    )

    assert storage.begin_calls == 1
    assert storage.complete_calls == 1
    assert storage.inspect_calls == 1

    assert client.sessions == 2


def test_provider_failure_before_completion_aborts_and_never_starts_mongo() -> None:
    module = _module()

    storage = FakeStorage(
        fail_write=True
    )

    client = FakeMongoClient(
        []
    )

    with pytest.raises(
        module.HrDocumentServiceProviderError
    ):
        _invoke(
            module,
            storage=storage,
            mongo_client=client,
        )

    assert storage.begin_calls == 1
    assert storage.complete_calls == 0
    assert storage.abort_calls == 1
    assert client.sessions == 0


def test_service_exposes_explicit_non_success_reconciliation_state() -> None:
    module = _module()

    assert {
        item.value
        for item in module.HrDocumentIngestionStatus
    } == {
        "COMMITTED",
        "RECONCILIATION_REQUIRED",
    }

    assert (
        module.HrDocumentIngestionStatus.RECONCILIATION_REQUIRED
        is not module.HrDocumentIngestionStatus.COMMITTED
    )


def test_service_does_not_import_reconciliation_resolution_or_provider_delete_authority() -> None:
    module = _module()

    forbidden = {
        "reconcile_hr_document_commit_uncertainty",
        "delete_object",
        "delete_provider",
        "provider_delete",
        "settle",
        "execute_payment",
    }

    public_names = {
        name
        for name in dir(
            module
        )
        if not name.startswith(
            "_"
        )
    }

    assert forbidden.isdisjoint(
        public_names
    )


# ARTIFACT: tests/unit/test_hr_document_service.py
# VERSION: v1.0.0-P0-C12F6F-HR-DOCUMENT-ORCHESTRATION-SERVICE-CERT
# TRANSACTION OWNER: F6F
# PROVIDER WRITE: exactly once before Mongo metadata transaction
# PRIMARY MONGO TX: F6F start/commit/abort/bounded whole-transaction retry
# UNKNOWN COMMIT: no provider replay; persist F6C/F6D uncertainty in fresh transaction
# COMMITTED: exact HrDocument metadata commit proven
# RECONCILIATION_REQUIRED: explicit non-success state only
# F6E3: remains exclusive reconciliation owner
# PROVIDER DELETE AUTHORITY: none
# ORPHAN PROOF AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
