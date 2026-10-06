"""WILSY OS HR Document Orchestration Service Real-Mongo Certificate.

TITLE: HR Document Orchestration Service Real-Mongo Certificate
VERSION: v1.0.0-P0-C12F6F-HR-DOCUMENT-ORCHESTRATION-SERVICE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Certify the F6F two-plane HR document orchestration service against a real
MongoDB replica set while keeping provider execution deterministic and local.

AUTHORITY BOUNDARY:
Real-Mongo orchestration certification only. No IAM issuance, HTTP authority,
provider deletion, orphan determination, payroll payment, billing, settlement
or financial execution authority.

PROVIDER BOUNDARY:
The certificate uses an in-memory authority-stateless provider double.
No S3 mutation occurs. The provider operation count nevertheless proves that
Mongo transaction retry and uncertainty persistence never re-execute provider
begin/write/complete.

TRANSACTION BOUNDARY:
F6F owns real Mongo session creation, start, commit, abort, bounded
whole-transaction retry and unknown primary commit classification.

UNKNOWN-COMMIT BOUNDARY:
A synthetic PyMongo-compatible UnknownTransactionCommitResult is injected only
after the underlying real primary commit has reached Mongo. F6F must refuse to
call that state COMMITTED, persist F6C/F6D uncertainty through a fresh real
transaction, and return RECONCILIATION_REQUIRED.

RECONCILIATION BOUNDARY:
The certificate may call the separately frozen F6E3 service only to prove that
the uncertainty produced by F6F is sufficient for later adjudication. F6F
itself must not import or invoke F6E3.

TOPOLOGY BOUNDARY:
Only loopback wilsyVendorCertRS is accepted. Every test uses a UUID-isolated
disposable database.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_hr_document_service_real_mongo.py

CERTIFICATION / UPDATE DATE: 2026-10-05
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.client_session import ClientSession
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.hr_document import (
    HrDocumentClass,
)
from tools.eos.saas.domain.hr_document_commit_reconciliation_outcome import (
    HrDocumentCommitReconciliationOutcome,
)
from tools.eos.saas.hr import (
    hr_document_commit_reconciliation_outcome_registry
    as outcome_registry_module,
)
from tools.eos.saas.hr import (
    hr_document_commit_uncertainty_registry
    as uncertainty_registry_module,
)
from tools.eos.saas.hr import (
    hr_document_registry
    as document_registry,
)
from tools.eos.saas.hr import (
    hr_document_service
    as service,
)
from tools.eos.saas.hr.hr_document_commit_reconciliation_service import (
    reconcile_hr_document_commit_uncertainty,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryChunkEvidence,
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryWriteIntent,
    HrDocumentBinaryWriteSession,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    (
        "mongodb://127.0.0.1:27027/"
        "?replicaSet=wilsyVendorCertRS"
    ),
)

EXPECTED_REPLICA_SET = (
    "wilsyVendorCertRS"
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
        employee: FakeEmployee,
    ) -> None:
        self.employee = employee

    def get_employee_by_id(
        self,
        employee_id: str,
        tenant_id: str,
    ):
        assert (
            employee_id
            == self.employee.employeeId
        )

        assert (
            tenant_id
            == self.employee.tenantId
        )

        return self.employee


class FakeStorage:
    def __init__(
        self,
    ) -> None:
        self.events: list[str] = []
        self.begin_calls = 0
        self.complete_calls = 0
        self.inspect_calls = 0

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
                "real-mongo-session"
            ),
            storage_reference=(
                "opaque/f6f/real-mongo"
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
                "opaque/f6f/real-mongo"
            ),
            object_version_reference=(
                "provider-version-f6f-real"
            ),
            provider_integrity_reference=(
                "provider-integrity-f6f-real"
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


class CountingMongoClient:
    def __init__(
        self,
        client: MongoClient[Any],
    ) -> None:
        self.client = client
        self.sessions = 0

    def start_session(
        self,
    ):
        self.sessions += 1
        return self.client.start_session()


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
        return (
            label
            == self.label
        )


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
    ]
]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )

    database: Any = None

    try:
        hello = client.admin.command(
            "hello"
        )

        assert (
            hello.get(
                "setName"
            )
            == EXPECTED_REPLICA_SET
        )

        assert (
            hello.get(
                "isWritablePrimary",
                hello.get(
                    "ismaster"
                ),
            )
            is True
        )

        assert (
            hello.get(
                "logicalSessionTimeoutMinutes"
            )
            is not None
        )

        database = client[
            "wilsy_hr_f6f_"
            + uuid.uuid4().hex[:12]
        ]

        document_collection = (
            database.get_collection(
                document_registry.COLLECTION,
                write_concern=WriteConcern(
                    w="majority",
                    j=True,
                ),
                read_concern=ReadConcern(
                    "majority"
                ),
            )
        )

        uncertainty_collection = (
            database.get_collection(
                uncertainty_registry_module.COLLECTION,
                write_concern=WriteConcern(
                    w="majority",
                    j=True,
                ),
                read_concern=ReadConcern(
                    "majority"
                ),
            )
        )

        outcome_collection = (
            database.get_collection(
                outcome_registry_module.COLLECTION,
                write_concern=WriteConcern(
                    w="majority",
                    j=True,
                ),
                read_concern=ReadConcern(
                    "majority"
                ),
            )
        )

        document_registry.ensure_indexes(
            document_collection
        )

        uncertainty_registry_module.ensure_indexes(
            uncertainty_collection
        )

        outcome_registry_module.ensure_indexes(
            outcome_collection
        )

        yield (
            client,
            database,
            document_collection,
            uncertainty_collection,
            outcome_collection,
        )

    finally:
        if database is not None:
            client.drop_database(
                database.name
            )

        client.close()


def make_intent(
    tenant_id: str,
    *,
    variant: str,
) -> HrDocumentBinaryWriteIntent:
    return HrDocumentBinaryWriteIntent(
        tenant_id=tenant_id,
        employee_id="employee-f6f",
        document_id=(
            "document-f6f-"
            + variant
        ),
        document_version_id=(
            "document-version-f6f-"
            + variant
        ),
        ingestion_reference=(
            "ingestion-f6f-"
            + variant
        ),
        media_type="application/pdf",
        original_filename=(
            "employment-contract-"
            + variant
            + ".pdf"
        ),
        admitted_max_content_length=4096,
    )


def chunks(
    variant: str,
) -> tuple[
    bytes,
    ...,
]:
    return (
        (
            "%PDF-1.7-WILSY-F6F-"
            + variant
            + "-A"
        ).encode(
            "utf-8"
        ),
        (
            "-WILSY-F6F-"
            + variant
            + "-B%%EOF"
        ).encode(
            "utf-8"
        ),
    )


def created_at() -> datetime:
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


def invoke(
    *,
    tenant_id: str,
    variant: str,
    storage: FakeStorage,
    mongo_client: Any,
    document_collection: Any,
    uncertainty_collection: Any,
):
    intent = make_intent(
        tenant_id,
        variant=variant,
    )

    result = service.orchestrate_hr_document_ingestion(
        intent=intent,
        chunks=chunks(
            variant
        ),
        document_class=(
            HrDocumentClass.EMPLOYMENT_CONTRACT
        ),
        created_at=created_at(),
        created_by_principal_id=(
            "principal-f6f-real"
        ),
        retention_until=None,
        legal_hold=False,
        supersedes_version_id=None,
        storage=storage,
        employee_registry=FakeEmployeeRegistry(
            FakeEmployee(
                employee_id=intent.employee_id,
                tenant_id=intent.tenant_id,
            )
        ),
        mongo_client=mongo_client,
        document_collection=(
            document_collection
        ),
        uncertainty_collection=(
            uncertainty_collection
        ),
        max_transaction_attempts=3,
    )

    return (
        intent,
        result,
    )


def test_real_topology_and_indexes(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
    ],
) -> None:
    (
        client,
        database,
        _,
        _,
        _,
    ) = mongo_context

    hello = client.admin.command(
        "hello"
    )

    assert (
        hello.get(
            "setName"
        )
        == EXPECTED_REPLICA_SET
    )

    names = set(
        database.list_collection_names()
    )

    assert {
        document_registry.COLLECTION,
        uncertainty_registry_module.COLLECTION,
        outcome_registry_module.COLLECTION,
    }.issubset(
        names
    )


def test_real_successful_metadata_commit_is_durable_without_uncertainty(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
    ],
) -> None:
    (
        client,
        _,
        document_collection,
        uncertainty_collection,
        _,
    ) = mongo_context

    tenant = (
        "tenant-f6f-commit-"
        + uuid.uuid4().hex
    )

    storage = FakeStorage()

    counting = CountingMongoClient(
        client
    )

    _, result = invoke(
        tenant_id=tenant,
        variant="commit",
        storage=storage,
        mongo_client=counting,
        document_collection=(
            document_collection
        ),
        uncertainty_collection=(
            uncertainty_collection
        ),
    )

    assert (
        result.status
        is service.HrDocumentIngestionStatus
        .COMMITTED
    )

    assert result.uncertainty is None

    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert uncertainty_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    assert counting.sessions == 1

    assert storage.events == [
        "provider.begin",
        "provider.write:0",
        "provider.write:1",
        "provider.complete",
        "provider.inspect",
    ]


def test_real_transient_metadata_retry_aborts_first_write_uses_fresh_session_and_provider_once(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        client,
        _,
        document_collection,
        uncertainty_collection,
        _,
    ) = mongo_context

    tenant = (
        "tenant-f6f-retry-"
        + uuid.uuid4().hex
    )

    storage = FakeStorage()

    counting = CountingMongoClient(
        client
    )

    original = (
        document_registry.persist_document
    )

    calls = 0

    def persist_then_retry(
        document: Any,
        collection: Any,
        *,
        session: Any,
    ):
        nonlocal calls
        calls += 1

        persisted = original(
            document,
            collection,
            session=session,
        )

        if calls == 1:
            raise (
                service.HrDocumentRegistryRetryRequiredError()
            )

        return persisted

    monkeypatch.setattr(
        service,
        "persist_document",
        persist_then_retry,
    )

    _, result = invoke(
        tenant_id=tenant,
        variant="retry",
        storage=storage,
        mongo_client=counting,
        document_collection=(
            document_collection
        ),
        uncertainty_collection=(
            uncertainty_collection
        ),
    )

    assert (
        result.status
        is service.HrDocumentIngestionStatus
        .COMMITTED
    )

    assert calls == 2
    assert counting.sessions == 2

    # First transaction wrote then was aborted; only retry winner survives.
    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert uncertainty_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    assert storage.begin_calls == 1
    assert storage.complete_calls == 1
    assert storage.inspect_calls == 1


def test_real_unknown_primary_commit_records_independent_uncertainty_without_provider_replay(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        client,
        _,
        document_collection,
        uncertainty_collection,
        _,
    ) = mongo_context

    tenant = (
        "tenant-f6f-unknown-"
        + uuid.uuid4().hex
    )

    storage = FakeStorage()

    counting = CountingMongoClient(
        client
    )

    original_commit = (
        ClientSession.commit_transaction
    )

    injected = False

    def commit_then_report_unknown(
        self: ClientSession,
    ) -> None:
        nonlocal injected

        original_commit(
            self
        )

        if not injected:
            injected = True

            raise LabeledMongoError(
                "UnknownTransactionCommitResult"
            )

    monkeypatch.setattr(
        ClientSession,
        "commit_transaction",
        commit_then_report_unknown,
    )

    _, result = invoke(
        tenant_id=tenant,
        variant="unknown",
        storage=storage,
        mongo_client=counting,
        document_collection=(
            document_collection
        ),
        uncertainty_collection=(
            uncertainty_collection
        ),
    )

    assert injected is True

    assert (
        result.status
        is service.HrDocumentIngestionStatus
        .RECONCILIATION_REQUIRED
    )

    assert result.document is not None
    assert result.uncertainty is not None

    # The underlying primary commit actually reached Mongo before the
    # uncertainty-producing unknown-result signal was injected.
    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    # F6D uncertainty is independently durable through the second session.
    assert uncertainty_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert counting.sessions == 2

    assert storage.begin_calls == 1
    assert storage.complete_calls == 1
    assert storage.inspect_calls == 1

    row = uncertainty_collection.find_one(
        {
            "tenant_id": tenant,
        }
    )

    assert isinstance(
        row,
        dict,
    )

    assert (
        row[
            "uncertainty_id"
        ]
        == result.uncertainty.uncertainty_id
    )

    assert (
        row[
            "fingerprint"
        ]
        == result.uncertainty.fingerprint
    )


def test_real_f6e3_can_adjudicate_f6f_unknown_commit_uncertainty_as_confirmed(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        client,
        _,
        document_collection,
        uncertainty_collection,
        outcome_collection,
    ) = mongo_context

    tenant = (
        "tenant-f6f-chain-"
        + uuid.uuid4().hex
    )

    storage = FakeStorage()

    counting = CountingMongoClient(
        client
    )

    original_commit = (
        ClientSession.commit_transaction
    )

    injected = False

    def commit_then_report_unknown(
        self: ClientSession,
    ) -> None:
        nonlocal injected

        original_commit(
            self
        )

        if not injected:
            injected = True

            raise LabeledMongoError(
                "UnknownTransactionCommitResult"
            )

    monkeypatch.setattr(
        ClientSession,
        "commit_transaction",
        commit_then_report_unknown,
    )

    _, ingestion = invoke(
        tenant_id=tenant,
        variant="chain",
        storage=storage,
        mongo_client=counting,
        document_collection=(
            document_collection
        ),
        uncertainty_collection=(
            uncertainty_collection
        ),
    )

    assert (
        ingestion.status
        is service.HrDocumentIngestionStatus
        .RECONCILIATION_REQUIRED
    )

    uncertainty = ingestion.uncertainty

    assert uncertainty is not None

    # Restore ordinary commit behavior before invoking F6E3.
    monkeypatch.setattr(
        ClientSession,
        "commit_transaction",
        original_commit,
    )

    uncertainty_owner = (
        uncertainty_registry_module
        .HrDocumentCommitUncertaintyRegistry(
            uncertainty_collection
        )
    )

    outcome_owner = (
        outcome_registry_module
        .HrDocumentCommitReconciliationOutcomeRegistry(
            outcome_collection
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            outcome = (
                reconcile_hr_document_commit_uncertainty(
                    tenant_id=tenant,
                    uncertainty_id=(
                        uncertainty.uncertainty_id
                    ),
                    reconciled_at=datetime(
                        2026,
                        10,
                        5,
                        14,
                        31,
                        0,
                        654321,
                        tzinfo=timezone.utc,
                    ),
                    uncertainty_registry=(
                        uncertainty_owner
                    ),
                    outcome_registry=(
                        outcome_owner
                    ),
                    document_collection=(
                        document_collection
                    ),
                    session=session,
                )
            )

            assert (
                outcome.outcome
                is HrDocumentCommitReconciliationOutcome
                .COMMITTED_CONFIRMED
            )

    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert uncertainty_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert outcome_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    # F6E3 resolution did not mutate or remove F6D uncertainty evidence.
    uncertainty_row = (
        uncertainty_collection.find_one(
            {
                "tenant_id": tenant,
            }
        )
    )

    assert isinstance(
        uncertainty_row,
        dict,
    )

    assert (
        uncertainty_row[
            "fingerprint"
        ]
        == uncertainty.fingerprint
    )


# ARTIFACT: tests/integration/test_hr_document_service_real_mongo.py
# VERSION: v1.0.0-P0-C12F6F-HR-DOCUMENT-ORCHESTRATION-SERVICE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo F6F orchestration certification only
# TOPOLOGY: dedicated loopback wilsyVendorCertRS on port 27027
# DATABASE: UUID-isolated disposable database only
# PROVIDER: authority-stateless in-memory double; no S3 mutation
# PROVIDER WRITE: exactly once regardless of Mongo retry or unknown commit
# PRIMARY COMMIT: real Mongo transaction owned by F6F
# TRANSIENT RETRY: first real write aborted; fresh-session retry commits
# UNKNOWN COMMIT: never synthetic success
# UNCERTAINTY: F6C/F6D persisted through fresh independent real transaction
# RECONCILIATION: frozen F6E3 can adjudicate later; F6F itself does not
# PROVIDER DELETE AUTHORITY: none
# ORPHAN PROOF AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
