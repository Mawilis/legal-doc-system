"""WILSY OS HR Document Commit-Reconciliation Service Real-Mongo Certificate.

TITLE: HR Document Commit-Reconciliation Service Real-Mongo Certificate
VERSION: v1.0.0-P0-C12F6E3-HR-DOCUMENT-COMMIT-RECONCILIATION-SERVICE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Certify the F6E3 reconciliation service against a real MongoDB replica set,
including atomic recovered-document/outcome persistence, abort safety,
confirmed-state handling, restart replay, fail-closed inconsistency handling
and tenant isolation.

AUTHORITY BOUNDARY:
Real-Mongo reconciliation certification only. No provider IO, provider
deletion, orphan determination, retention/disposal authority, IAM, HTTP,
payroll, billing, payment, settlement or financial execution authority.

TRANSACTION BOUNDARY:
Tests own the Mongo session, transaction, commit and abort. The production
service receives only an already-active caller-owned transaction.

ATOMICITY BOUNDARY:
For COMMIT_RECOVERED the reconstructed hr_documents row and terminal
reconciliation outcome must commit together or disappear together on abort.
The pre-existing durable uncertainty remains independently durable.

TOPOLOGY BOUNDARY:
Only the dedicated loopback wilsyVendorCertRS replica set is accepted.
Every test uses a UUID-isolated disposable database.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_hr_document_commit_reconciliation_service_real_mongo.py

CERTIFICATION / UPDATE DATE: 2026-10-05
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

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
from tools.eos.saas.hr.hr_document_commit_reconciliation_service import (
    HrDocumentCommitReconciliationServiceConflictError,
    HrDocumentCommitReconciliationServiceTransactionRequiredError,
    reconcile_hr_document_commit_uncertainty,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryWriteIntent,
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

        db_name = (
            "wilsy_hr_recon_"
            + uuid.uuid4().hex[:12]
        )

        database = client[
            db_name
        ]

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

        uncertainty_registry_module.ensure_indexes(
            uncertainty_collection
        )

        document_registry.ensure_indexes(
            document_collection
        )

        outcome_registry_module.ensure_indexes(
            outcome_collection
        )

        yield (
            client,
            database,
            uncertainty_collection,
            document_collection,
            outcome_collection,
        )

    finally:
        if database is not None:
            client.drop_database(
                database.name
            )

        client.close()


def make_uncertainty(
    tenant_id: str,
    *,
    variant: str = "base",
    document_version_id: str = "document-version-f6e3",
):
    payload = (
        "WILSY-HR-F6E3-REAL-MONGO-"
        + variant
    ).encode(
        "utf-8"
    )

    intent = HrDocumentBinaryWriteIntent(
        tenant_id=tenant_id,
        employee_id="employee-f6e3",
        document_id="document-f6e3",
        document_version_id=(
            document_version_id
        ),
        ingestion_reference=(
            "ingestion-f6e3-"
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

    evidence = HrDocumentBinaryObjectEvidence(
        provider_name="aws_s3",
        storage_reference=(
            "hr/v1/opaque-f6e3-"
            + variant
        ),
        object_version_reference=(
            "provider-version-f6e3-"
            + variant
        ),
        provider_integrity_reference=(
            "provider-integrity-f6e3-"
            + variant
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
            "principal-f6e3-real"
        ),
        retention_until=None,
        legal_hold=False,
        supersedes_version_id=None,
        detected_at=created,
    )


def reconciled_at(
    uncertainty: Any,
    *,
    minutes: int = 1,
) -> datetime:
    return (
        uncertainty.detected_at
        + timedelta(
            minutes=minutes
        )
    )


def uncertainty_owner(
    collection: Any,
):
    return (
        uncertainty_registry_module
        .HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )


def outcome_owner(
    collection: Any,
):
    return (
        outcome_registry_module
        .HrDocumentCommitReconciliationOutcomeRegistry(
            collection
        )
    )


def seed_uncertainty(
    client: MongoClient[Any],
    collection: Any,
    uncertainty: Any,
) -> None:
    owner = uncertainty_owner(
        collection
    )

    with client.start_session() as session:
        with session.start_transaction():
            assert (
                owner.create_or_replay(
                    uncertainty,
                    session=session,
                )
                == uncertainty
            )


def reconcile(
    *,
    tenant_id: str,
    uncertainty_id: str,
    at: datetime,
    uncertainty_collection: Any,
    document_collection: Any,
    outcome_collection: Any,
    session: Any,
):
    return reconcile_hr_document_commit_uncertainty(
        tenant_id=tenant_id,
        uncertainty_id=uncertainty_id,
        reconciled_at=at,
        uncertainty_registry=uncertainty_owner(
            uncertainty_collection
        ),
        outcome_registry=outcome_owner(
            outcome_collection
        ),
        document_collection=document_collection,
        session=session,
    )


def test_real_topology_and_three_collection_surface(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        Any,
        Any,
    ],
) -> None:
    client, database, _, _, _ = (
        mongo_context
    )

    hello = client.admin.command(
        "hello"
    )

    assert (
        hello.get(
            "setName"
        )
        == EXPECTED_REPLICA_SET
    )

    assert set(
        database.list_collection_names()
    ) == {
        uncertainty_registry_module.COLLECTION,
        document_registry.COLLECTION,
        outcome_registry_module.COLLECTION,
    }


def test_real_recovered_document_and_outcome_commit_atomically_and_restart_replays(
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
        uncertainty_collection,
        document_collection,
        outcome_collection,
    ) = mongo_context

    tenant = (
        "tenant-recovered-"
        + uuid.uuid4().hex
    )

    uncertainty = make_uncertainty(
        tenant
    )

    seed_uncertainty(
        client,
        uncertainty_collection,
        uncertainty,
    )

    assert uncertainty_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    assert outcome_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    with client.start_session() as session:
        with session.start_transaction():
            first = reconcile(
                tenant_id=tenant,
                uncertainty_id=(
                    uncertainty.uncertainty_id
                ),
                at=reconciled_at(
                    uncertainty
                ),
                uncertainty_collection=(
                    uncertainty_collection
                ),
                document_collection=(
                    document_collection
                ),
                outcome_collection=(
                    outcome_collection
                ),
                session=session,
            )

            assert (
                first.outcome
                is HrDocumentCommitReconciliationOutcome
                .COMMIT_RECOVERED
            )

            assert document_collection.count_documents(
                {
                    "tenant_id": tenant,
                },
                session=session,
            ) == 1

            assert outcome_collection.count_documents(
                {
                    "tenant_id": tenant,
                },
                session=session,
            ) == 1

    # Both control-plane artifacts became durable together.
    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert outcome_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    # Fresh owners model process restart.
    with client.start_session() as session:
        with session.start_transaction():
            replay = reconcile(
                tenant_id=tenant,
                uncertainty_id=(
                    uncertainty.uncertainty_id
                ),
                at=reconciled_at(
                    uncertainty,
                    minutes=10,
                ),
                uncertainty_collection=(
                    uncertainty_collection
                ),
                document_collection=(
                    document_collection
                ),
                outcome_collection=(
                    outcome_collection
                ),
                session=session,
            )

    # Historical terminal outcome is replayed byte-for-byte.
    assert replay == first
    assert (
        replay.reconciled_at
        == first.reconciled_at
    )

    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert outcome_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1


def test_real_abort_removes_recovered_document_and_outcome_but_preserves_uncertainty(
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
        uncertainty_collection,
        document_collection,
        outcome_collection,
    ) = mongo_context

    tenant = (
        "tenant-abort-"
        + uuid.uuid4().hex
    )

    uncertainty = make_uncertainty(
        tenant
    )

    seed_uncertainty(
        client,
        uncertainty_collection,
        uncertainty,
    )

    with client.start_session() as session:
        session.start_transaction()

        result = reconcile(
            tenant_id=tenant,
            uncertainty_id=(
                uncertainty.uncertainty_id
            ),
            at=reconciled_at(
                uncertainty
            ),
            uncertainty_collection=(
                uncertainty_collection
            ),
            document_collection=(
                document_collection
            ),
            outcome_collection=(
                outcome_collection
            ),
            session=session,
        )

        assert (
            result.outcome
            is HrDocumentCommitReconciliationOutcome
            .COMMIT_RECOVERED
        )

        assert document_collection.count_documents(
            {
                "tenant_id": tenant,
            },
            session=session,
        ) == 1

        assert outcome_collection.count_documents(
            {
                "tenant_id": tenant,
            },
            session=session,
        ) == 1

        session.abort_transaction()

    assert uncertainty_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    assert outcome_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0


def test_real_exact_preexisting_document_records_confirmed_without_duplicate_document(
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
        uncertainty_collection,
        document_collection,
        outcome_collection,
    ) = mongo_context

    tenant = (
        "tenant-confirmed-"
        + uuid.uuid4().hex
    )

    uncertainty = make_uncertainty(
        tenant
    )

    expected_document = (
        uncertainty.to_hr_document()
    )

    seed_uncertainty(
        client,
        uncertainty_collection,
        uncertainty,
    )

    with client.start_session() as session:
        with session.start_transaction():
            assert (
                document_registry.persist_document(
                    expected_document,
                    document_collection,
                    session=session,
                )
                == expected_document
            )

    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    with client.start_session() as session:
        with session.start_transaction():
            result = reconcile(
                tenant_id=tenant,
                uncertainty_id=(
                    uncertainty.uncertainty_id
                ),
                at=reconciled_at(
                    uncertainty
                ),
                uncertainty_collection=(
                    uncertainty_collection
                ),
                document_collection=(
                    document_collection
                ),
                outcome_collection=(
                    outcome_collection
                ),
                session=session,
            )

            assert (
                result.outcome
                is HrDocumentCommitReconciliationOutcome
                .COMMITTED_CONFIRMED
            )

    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert outcome_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1


def test_real_existing_terminal_outcome_without_document_fails_closed(
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
        uncertainty_collection,
        document_collection,
        outcome_collection,
    ) = mongo_context

    tenant = (
        "tenant-missing-doc-"
        + uuid.uuid4().hex
    )

    uncertainty = make_uncertainty(
        tenant
    )

    document = uncertainty.to_hr_document()

    seed_uncertainty(
        client,
        uncertainty_collection,
        uncertainty,
    )

    terminal = (
        record_hr_document_commit_reconciliation_outcome(
            uncertainty=uncertainty,
            document=document,
            outcome=(
                HrDocumentCommitReconciliationOutcome
                .COMMIT_RECOVERED
            ),
            reconciled_at=reconciled_at(
                uncertainty
            ),
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            assert (
                outcome_owner(
                    outcome_collection
                ).create_or_replay(
                    terminal,
                    session=session,
                )
                == terminal
            )

    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    assert outcome_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                HrDocumentCommitReconciliationServiceConflictError
            ):
                reconcile(
                    tenant_id=tenant,
                    uncertainty_id=(
                        uncertainty.uncertainty_id
                    ),
                    at=reconciled_at(
                        uncertainty,
                        minutes=10,
                    ),
                    uncertainty_collection=(
                        uncertainty_collection
                    ),
                    document_collection=(
                        document_collection
                    ),
                    outcome_collection=(
                        outcome_collection
                    ),
                    session=session,
                )

    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    assert outcome_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1


def test_real_divergent_document_occupant_fails_closed_without_outcome(
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
        uncertainty_collection,
        document_collection,
        outcome_collection,
    ) = mongo_context

    tenant = (
        "tenant-divergent-"
        + uuid.uuid4().hex
    )

    uncertainty = make_uncertainty(
        tenant,
        variant="expected",
    )

    divergent_uncertainty = make_uncertainty(
        tenant,
        variant="divergent",
        document_version_id=(
            uncertainty.document_version_id
        ),
    )

    expected_document = (
        uncertainty.to_hr_document()
    )

    divergent_document = (
        divergent_uncertainty.to_hr_document()
    )

    assert (
        divergent_document.document_version_id
        == expected_document.document_version_id
    )

    assert (
        divergent_document.fingerprint
        != expected_document.fingerprint
    )

    seed_uncertainty(
        client,
        uncertainty_collection,
        uncertainty,
    )

    with client.start_session() as session:
        with session.start_transaction():
            document_registry.persist_document(
                divergent_document,
                document_collection,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                HrDocumentCommitReconciliationServiceConflictError
            ):
                reconcile(
                    tenant_id=tenant,
                    uncertainty_id=(
                        uncertainty.uncertainty_id
                    ),
                    at=reconciled_at(
                        uncertainty
                    ),
                    uncertainty_collection=(
                        uncertainty_collection
                    ),
                    document_collection=(
                        document_collection
                    ),
                    outcome_collection=(
                        outcome_collection
                    ),
                    session=session,
                )

    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert outcome_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0


def test_real_tenant_isolation_preserves_neighbor_state(
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
        uncertainty_collection,
        document_collection,
        outcome_collection,
    ) = mongo_context

    tenant_a = (
        "tenant-recon-a-"
        + uuid.uuid4().hex
    )

    tenant_b = (
        "tenant-recon-b-"
        + uuid.uuid4().hex
    )

    uncertainty_a = make_uncertainty(
        tenant_a
    )

    uncertainty_b = make_uncertainty(
        tenant_b
    )

    seed_uncertainty(
        client,
        uncertainty_collection,
        uncertainty_a,
    )

    seed_uncertainty(
        client,
        uncertainty_collection,
        uncertainty_b,
    )

    with client.start_session() as session:
        with session.start_transaction():
            result = reconcile(
                tenant_id=tenant_a,
                uncertainty_id=(
                    uncertainty_a.uncertainty_id
                ),
                at=reconciled_at(
                    uncertainty_a
                ),
                uncertainty_collection=(
                    uncertainty_collection
                ),
                document_collection=(
                    document_collection
                ),
                outcome_collection=(
                    outcome_collection
                ),
                session=session,
            )

            assert (
                result.outcome
                is HrDocumentCommitReconciliationOutcome
                .COMMIT_RECOVERED
            )

    assert uncertainty_collection.count_documents(
        {
            "tenant_id": tenant_a,
        }
    ) == 1

    assert uncertainty_collection.count_documents(
        {
            "tenant_id": tenant_b,
        }
    ) == 1

    assert document_collection.count_documents(
        {
            "tenant_id": tenant_a,
        }
    ) == 1

    assert document_collection.count_documents(
        {
            "tenant_id": tenant_b,
        }
    ) == 0

    assert outcome_collection.count_documents(
        {
            "tenant_id": tenant_a,
        }
    ) == 1

    assert outcome_collection.count_documents(
        {
            "tenant_id": tenant_b,
        }
    ) == 0


def test_real_inactive_transaction_rejected_before_document_or_outcome_write(
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
        uncertainty_collection,
        document_collection,
        outcome_collection,
    ) = mongo_context

    tenant = (
        "tenant-inactive-"
        + uuid.uuid4().hex
    )

    uncertainty = make_uncertainty(
        tenant
    )

    seed_uncertainty(
        client,
        uncertainty_collection,
        uncertainty,
    )

    with client.start_session() as session:
        with pytest.raises(
            HrDocumentCommitReconciliationServiceTransactionRequiredError
        ):
            reconcile(
                tenant_id=tenant,
                uncertainty_id=(
                    uncertainty.uncertainty_id
                ),
                at=reconciled_at(
                    uncertainty
                ),
                uncertainty_collection=(
                    uncertainty_collection
                ),
                document_collection=(
                    document_collection
                ),
                outcome_collection=(
                    outcome_collection
                ),
                session=session,
            )

    assert uncertainty_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert document_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0

    assert outcome_collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0


# ARTIFACT: tests/integration/test_hr_document_commit_reconciliation_service_real_mongo.py
# VERSION: v1.0.0-P0-C12F6E3-HR-DOCUMENT-COMMIT-RECONCILIATION-SERVICE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo HR document commit reconciliation only
# TOPOLOGY: dedicated loopback wilsyVendorCertRS on port 27027
# DATABASE: UUID-isolated disposable database only
# UNCERTAINTY: independently durable before reconciliation
# COMMIT_RECOVERED: document + outcome commit atomically
# ABORT: document + outcome both disappear; uncertainty remains
# COMMITTED_CONFIRMED: exact pre-existing document only
# RESTART REPLAY: existing terminal outcome reused without timestamp regeneration
# DIVERGENT STATE: fail closed
# TENANT POSTURE: exact isolation
# PROVIDER IO AUTHORITY: none
# ORPHAN PROOF AUTHORITY: none
# PROVIDER DELETE AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
