"""Real-Mongo certificate for cleanup-authorization durability.

TITLE: Legal Evidence Provider Cleanup Authorization Registry Real-Mongo Certificate
VERSION: v1.0.0-L10A2R-C4D6E-A2-PROVIDER-CLEANUP-AUTHORIZATION-REGISTRY-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
PURPOSE: Certify actual MongoDB replica-set indexes, caller-owned transactions,
         durable restart replay, rollback, tenant isolation, immutable conflicts,
         corruption rejection, strict authority-field rejection and duplicate-key
         whole-transaction retry for C4D6E-A2 cleanup-authorization evidence.
EPITOME: Real Mongo proves durability without granting provider deletion authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_evidence_provider_cleanup_authorization_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Legal Operations / Legal Evidence
CERTIFICATION / UPDATE DATE: 2026-10-02
CHANGELOG:
    v1.0.0 introduces the actual replica-set durability certificate for the
    C4D6E-A2 cleanup-authorization registry v1.0.1 retry contract.
COMPLIANCE:
    Exact tenant-scoped identities, deterministic unique indexes, no TTL and
    caller-owned Mongo transactions are certified against actual MongoDB.
SECURITY / PRIVACY POSTURE:
    UUID-isolated disposable certification databases; no production tenant data.
TENANT BOUNDARY:
    Every registry identity and lookup is tenant-scoped. Cross-tenant presence
    remains opaque at the registry boundary.
AUTHORITY BOUNDARY:
    Durable cleanup-authorization evidence only. No provider deletion,
    retention/legal-hold release, IAM authorization or execution authority.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
import os
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tests.unit.test_legal_evidence_provider_cleanup_authorization as domain_cert
from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_authorization import (
    LegalEvidenceProviderCleanupAuthorization,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_cleanup_authorization_registry import (
    COLLECTION,
    INDEX_TENANT_AUTHORIZATION_ID,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    LegalEvidenceProviderCleanupAuthorizationRegistry,
    LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError,
    LegalEvidenceProviderCleanupAuthorizationRegistryRetryRequiredError,
    LegalEvidenceProviderCleanupAuthorizationRegistryTransactionError,
)


MONGO_URI = os.environ.get(
    "WILSY_C4D6E_A2_MONGO_URI",
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
    "&directConnection=true",
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"


class _Context:
    """Actual Mongo resources for one disposable certificate database."""

    def __init__(
        self,
        client: MongoClient[Any],
        database: Any,
        collection: Any,
    ) -> None:
        self.client = client
        self.database = database
        self.collection = collection
        self.registry = (
            LegalEvidenceProviderCleanupAuthorizationRegistry(
                collection
            )
        )


class _HideIdentityReads:
    """Hide winner reads while delegating insert to the real Mongo collection."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = collection
        self.find_count = 0
        self.insert_count = 0

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: Any,
    ) -> None:
        _ = query
        assert session.in_transaction is True
        self.find_count += 1
        return None

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: Any,
    ) -> Any:
        assert session.in_transaction is True
        self.insert_count += 1
        return self._collection.insert_one(
            document,
            session=session,
        )


def _start(
    session: Any,
) -> None:
    session.start_transaction(
        read_concern=ReadConcern(
            "snapshot"
        ),
        write_concern=WriteConcern(
            w="majority",
            j=True,
        ),
    )


def _orphan_proof(
    *,
    tenant_id: str,
    provider_name: str = domain_cert.PROVIDER,
    storage_reference: str = domain_cert.STORAGE,
    object_version_reference: str = domain_cert.OBJECT_VERSION,
    suffix: str,
) -> Any:
    """Build genuine orphan proof through the certified C4D6D chain."""

    scope = domain_cert.LegalEvidenceProviderDiscoveryScope(
        tenant_id=tenant_id,
        tenant_scope_fingerprint=domain_cert.SHA_A,
    )

    observation = domain_cert.LegalEvidenceCompletedObjectObservation(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        provider_integrity_reference='"etag-a2-real"',
        content_length=19,
        last_modified_at=domain_cert.AT,
        observed_at=domain_cert.AT,
        write_intent_metadata_state=(
            domain_cert.LegalEvidenceCompletedObjectIntentMetadataState.ABSENT
        ),
        write_intent_fingerprint=None,
    )

    provider = domain_cert._Provider(
        scope=scope,
        completed=(observation,),
    )

    coverage_service = (
        domain_cert.LegalEvidenceProviderCoverageVerificationService(
            provider=provider,
        )
    )

    verification = coverage_service.verify_coverage(
        scope=scope,
        provider_name=provider_name,
        observed_at=domain_cert.AT,
    )

    disownership = (
        domain_cert.LegalEvidenceProviderObjectDisownership(
            tenant_id=tenant_id,
            provider_name=provider_name,
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            disownership_reference=(
                "disownership-a2-real-" + suffix
            ),
            reason_reference=(
                "reason-a2-real-" + suffix
            ),
            source_evidence_reference=(
                "source-a2-real-" + suffix
            ),
            source_evidence_fingerprint=domain_cert.SHA_A,
            authorization_evidence_reference=(
                "authorization-evidence-a2-real-" + suffix
            ),
            authorization_evidence_fingerprint=domain_cert.SHA_B,
            decided_at=(
                domain_cert.AT
                - timedelta(minutes=5)
            ),
        )
    )

    return domain_cert.prove_legal_evidence_provider_object_orphan(
        coverage_service=coverage_service,
        verification=verification,
        observation=observation,
        disownership=disownership,
        orphan_proof_reference=(
            "orphan-proof-a2-real-" + suffix
        ),
        proved_at=(
            domain_cert.AT
            + timedelta(minutes=1)
        ),
    )


def _authorization(
    *,
    tenant_id: str,
    authorization_id: str,
    reason_reference: str,
    provider_name: str = domain_cert.PROVIDER,
    storage_reference: str = domain_cert.STORAGE,
    object_version_reference: str = domain_cert.OBJECT_VERSION,
    suffix: str,
) -> LegalEvidenceProviderCleanupAuthorization:
    """Issue genuine cleanup authorization through certified A1 factory."""

    orphan = _orphan_proof(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        suffix=suffix,
    )

    preservation = domain_cert._preservation(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
    )

    return domain_cert._authorize(
        orphan_proof=orphan,
        preservation=preservation,
        authorization_id=authorization_id,
        reason_reference=reason_reference,
    )


def _commit(
    context: _Context,
    value: LegalEvidenceProviderCleanupAuthorization,
) -> LegalEvidenceProviderCleanupAuthorization:
    with context.client.start_session() as session:
        _start(session)

        result = context.registry.create_or_replay(
            value,
            session=session,
        )

        session.commit_transaction()

    return result


@pytest.fixture()
def mongo_context() -> Iterator[_Context]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        retryWrites=True,
        tz_aware=True,
    )

    hello = client.admin.command(
        "hello"
    )

    if (
        hello.get("setName")
        != EXPECTED_REPLICA_SET
        or hello.get("isWritablePrimary")
        is not True
    ):
        client.close()
        pytest.fail(
            "C4D6E-A2 requires writable "
            "wilsyVendorCertRS replica set"
        )

    database_name = (
        "wilsy_c4d6e_a2_"
        + uuid4().hex
    )

    database = client[
        database_name
    ]

    collection = database.get_collection(
        COLLECTION,
        write_concern=WriteConcern(
            w="majority",
            j=True,
        ),
        read_concern=ReadConcern(
            "majority"
        ),
    )

    context = _Context(
        client,
        database,
        collection,
    )

    context.registry.ensure_indexes()

    try:
        yield context
    finally:
        client.drop_database(
            database_name
        )
        client.close()


def test_real_topology_indexes_unique_and_no_ttl(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    assert context.database.name.startswith(
        "wilsy_c4d6e_a2_"
    )
    assert context.database.name != "wilsy"

    hello = context.client.admin.command(
        "hello"
    )
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello["isWritablePrimary"] is True

    indexes = {
        item["name"]: item
        for item in context.collection.list_indexes()
    }

    assert set(indexes) == {
        "_id_",
        INDEX_TENANT_AUTHORIZATION_ID,
        INDEX_TENANT_FINGERPRINT,
        INDEX_TENANT_PROVIDER_OBJECT,
    }

    authorization = indexes[
        INDEX_TENANT_AUTHORIZATION_ID
    ]
    assert list(
        authorization["key"].items()
    ) == [
        ("tenant_id", 1),
        ("authorization_id", 1),
    ]
    assert authorization.get(
        "unique"
    ) is True

    fingerprint = indexes[
        INDEX_TENANT_FINGERPRINT
    ]
    assert list(
        fingerprint["key"].items()
    ) == [
        ("tenant_id", 1),
        ("fingerprint", 1),
    ]
    assert fingerprint.get(
        "unique"
    ) is True

    provider_object = indexes[
        INDEX_TENANT_PROVIDER_OBJECT
    ]
    assert list(
        provider_object["key"].items()
    ) == [
        ("tenant_id", 1),
        ("provider_name", 1),
        ("storage_reference", 1),
        ("object_version_reference", 1),
    ]
    assert provider_object.get(
        "unique"
    ) is True

    assert all(
        "expireAfterSeconds" not in item
        for item in indexes.values()
    )


def test_real_inactive_transaction_rejects_before_write(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    value = _authorization(
        tenant_id="tenant-a2-inactive-" + uuid4().hex,
        authorization_id="cleanup-a2-inactive",
        reason_reference="reason:a2:inactive",
        suffix=uuid4().hex,
    )

    with context.client.start_session() as session:
        assert session.in_transaction is False

        with pytest.raises(
            LegalEvidenceProviderCleanupAuthorizationRegistryTransactionError,
            match="ACTIVE_TRANSACTION_REQUIRED",
        ):
            context.registry.create_or_replay(
                value,
                session=session,
            )

    assert context.collection.count_documents(
        {}
    ) == 0


def test_real_commit_restart_replay_and_all_lookup_paths(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    value = _authorization(
        tenant_id="tenant-a2-replay-" + uuid4().hex,
        authorization_id="cleanup-a2-replay",
        reason_reference="reason:a2:replay",
        suffix=uuid4().hex,
    )

    assert _commit(
        context,
        value,
    ) == value

    raw = context.collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
        }
    )

    assert raw is not None
    assert raw[
        "preservation_assessed_at"
    ] == value.preservation_assessed_at.isoformat()
    assert raw[
        "authorized_at"
    ] == value.authorized_at.isoformat()
    assert isinstance(
        raw["preservation_assessed_at"],
        str,
    )
    assert isinstance(
        raw["authorized_at"],
        str,
    )

    fresh_client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        retryWrites=True,
        tz_aware=True,
    )

    try:
        fresh_collection = fresh_client[
            context.database.name
        ].get_collection(
            COLLECTION,
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
            read_concern=ReadConcern(
                "majority"
            ),
        )

        restarted = (
            LegalEvidenceProviderCleanupAuthorizationRegistry(
                fresh_collection
            )
        )

        with fresh_client.start_session() as session:
            _start(session)

            replayed = restarted.create_or_replay(
                value,
                session=session,
            )

            by_id = restarted.get_by_authorization_id(
                tenant_id=value.tenant_id,
                authorization_id=value.authorization_id,
                session=session,
            )

            by_fingerprint = restarted.get_by_fingerprint(
                tenant_id=value.tenant_id,
                fingerprint=value.fingerprint,
                session=session,
            )

            by_object = restarted.get_by_provider_object(
                tenant_id=value.tenant_id,
                provider_name=value.provider_name,
                storage_reference=value.storage_reference,
                object_version_reference=(
                    value.object_version_reference
                ),
                session=session,
            )

            cross_tenant = restarted.get_by_provider_object(
                tenant_id=value.tenant_id + "-other",
                provider_name=value.provider_name,
                storage_reference=value.storage_reference,
                object_version_reference=(
                    value.object_version_reference
                ),
                session=session,
            )

            session.commit_transaction()

        assert replayed == value
        assert by_id == value
        assert by_fingerprint == value
        assert by_object == value
        assert cross_tenant is None

    finally:
        fresh_client.close()

    assert context.collection.count_documents(
        {
            "tenant_id":
                value.tenant_id,
        }
    ) == 1


def test_real_aborted_transaction_leaves_zero_durable_row(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    value = _authorization(
        tenant_id="tenant-a2-abort-" + uuid4().hex,
        authorization_id="cleanup-a2-abort",
        reason_reference="reason:a2:abort",
        suffix=uuid4().hex,
    )

    with context.client.start_session() as session:
        _start(session)

        context.registry.create_or_replay(
            value,
            session=session,
        )

        assert context.collection.count_documents(
            {
                "tenant_id":
                    value.tenant_id,
            },
            session=session,
        ) == 1

        session.abort_transaction()

    assert context.collection.count_documents(
        {
            "tenant_id":
                value.tenant_id,
        }
    ) == 0


def test_real_same_authorization_id_divergence_rejects(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    tenant = (
        "tenant-a2-id-divergence-"
        + uuid4().hex
    )
    suffix = uuid4().hex

    first = _authorization(
        tenant_id=tenant,
        authorization_id="cleanup-a2-shared-id",
        reason_reference="reason:a2:first",
        suffix=suffix + "-first",
    )

    divergent = _authorization(
        tenant_id=tenant,
        authorization_id="cleanup-a2-shared-id",
        reason_reference="reason:a2:divergent",
        suffix=suffix + "-divergent",
    )

    assert first.fingerprint != divergent.fingerprint

    _commit(
        context,
        first,
    )

    with context.client.start_session() as session:
        _start(session)

        with pytest.raises(
            LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError,
            match="REPLAY_CONFLICT",
        ):
            context.registry.create_or_replay(
                divergent,
                session=session,
            )

        session.abort_transaction()

    assert context.collection.count_documents(
        {
            "tenant_id":
                tenant,
        }
    ) == 1


def test_real_same_provider_object_different_authorization_rejects(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    tenant = (
        "tenant-a2-object-divergence-"
        + uuid4().hex
    )

    first = _authorization(
        tenant_id=tenant,
        authorization_id="cleanup-a2-object-first",
        reason_reference="reason:a2:object:first",
        suffix=uuid4().hex,
    )

    divergent = _authorization(
        tenant_id=tenant,
        authorization_id="cleanup-a2-object-second",
        reason_reference="reason:a2:object:second",
        suffix=uuid4().hex,
    )

    assert first.fingerprint != divergent.fingerprint
    assert (
        first.storage_reference
        == divergent.storage_reference
    )
    assert (
        first.object_version_reference
        == divergent.object_version_reference
    )

    _commit(
        context,
        first,
    )

    with context.client.start_session() as session:
        _start(session)

        with pytest.raises(
            LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError,
            match="REPLAY_CONFLICT",
        ):
            context.registry.create_or_replay(
                divergent,
                session=session,
            )

        session.abort_transaction()

    assert context.collection.count_documents(
        {
            "tenant_id":
                tenant,
        }
    ) == 1


def test_real_cross_tenant_same_provider_object_isolated(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    suffix = uuid4().hex

    first = _authorization(
        tenant_id="tenant-a2-cross-a-" + suffix,
        authorization_id="cleanup-a2-cross-a",
        reason_reference="reason:a2:cross:a",
        suffix=suffix + "-a",
    )

    second = _authorization(
        tenant_id="tenant-a2-cross-b-" + suffix,
        authorization_id="cleanup-a2-cross-b",
        reason_reference="reason:a2:cross:b",
        suffix=suffix + "-b",
    )

    assert (
        first.storage_reference
        == second.storage_reference
    )
    assert (
        first.object_version_reference
        == second.object_version_reference
    )

    _commit(
        context,
        first,
    )
    _commit(
        context,
        second,
    )

    assert context.collection.count_documents(
        {
            "provider_name":
                first.provider_name,
            "storage_reference":
                first.storage_reference,
            "object_version_reference":
                first.object_version_reference,
        }
    ) == 2

    with context.client.start_session() as session:
        _start(session)

        first_read = context.registry.get_by_provider_object(
            tenant_id=first.tenant_id,
            provider_name=first.provider_name,
            storage_reference=first.storage_reference,
            object_version_reference=(
                first.object_version_reference
            ),
            session=session,
        )

        second_read = context.registry.get_by_provider_object(
            tenant_id=second.tenant_id,
            provider_name=second.provider_name,
            storage_reference=second.storage_reference,
            object_version_reference=(
                second.object_version_reference
            ),
            session=session,
        )

        session.commit_transaction()

    assert first_read == first
    assert second_read == second


def test_real_persisted_corruption_rejects_without_healing(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    value = _authorization(
        tenant_id="tenant-a2-corrupt-" + uuid4().hex,
        authorization_id="cleanup-a2-corrupt",
        reason_reference="reason:a2:corrupt",
        suffix=uuid4().hex,
    )

    _commit(
        context,
        value,
    )

    context.collection.update_one(
        {
            "tenant_id":
                value.tenant_id,
        },
        {
            "$set": {
                "reason_reference":
                    "tampered-reason",
            }
        },
    )

    corrupt_before = context.collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
        }
    )

    assert corrupt_before is not None

    with context.client.start_session() as session:
        _start(session)

        with pytest.raises(
            LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError,
            match="PERSISTED_DOCUMENT_CORRUPT",
        ):
            context.registry.get_by_fingerprint(
                tenant_id=value.tenant_id,
                fingerprint=value.fingerprint,
                session=session,
            )

        session.abort_transaction()

    corrupt_after = context.collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
        }
    )

    assert corrupt_after == corrupt_before


def test_real_unknown_authority_field_rejects_without_healing(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    value = _authorization(
        tenant_id="tenant-a2-authority-" + uuid4().hex,
        authorization_id="cleanup-a2-authority",
        reason_reference="reason:a2:authority",
        suffix=uuid4().hex,
    )

    _commit(
        context,
        value,
    )

    context.collection.update_one(
        {
            "tenant_id":
                value.tenant_id,
        },
        {
            "$set": {
                "provider_delete_authorized":
                    True,
            }
        },
    )

    corrupt_before = context.collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
        }
    )

    assert corrupt_before is not None

    with context.client.start_session() as session:
        _start(session)

        with pytest.raises(
            LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError,
            match="PERSISTED_DOCUMENT_CORRUPT",
        ):
            context.registry.get_by_fingerprint(
                tenant_id=value.tenant_id,
                fingerprint=value.fingerprint,
                session=session,
            )

        session.abort_transaction()

    corrupt_after = context.collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
        }
    )

    assert corrupt_after == corrupt_before


def test_real_duplicate_key_requires_abort_then_fresh_transaction_replays(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    value = _authorization(
        tenant_id="tenant-a2-race-" + uuid4().hex,
        authorization_id="cleanup-a2-race",
        reason_reference="reason:a2:race",
        suffix=uuid4().hex,
    )

    _commit(
        context,
        value,
    )

    hidden = _HideIdentityReads(
        context.collection
    )

    stale_registry = (
        LegalEvidenceProviderCleanupAuthorizationRegistry(
            hidden
        )
    )

    with context.client.start_session() as stale:
        _start(stale)

        with pytest.raises(
            LegalEvidenceProviderCleanupAuthorizationRegistryRetryRequiredError,
            match="WHOLE_TRANSACTION_RETRY_REQUIRED",
        ):
            stale_registry.create_or_replay(
                value,
                session=stale,
            )

        assert hidden.find_count == 3
        assert hidden.insert_count == 1
        assert stale.in_transaction is True

        stale.abort_transaction()

    with context.client.start_session() as retry:
        _start(retry)

        replayed = context.registry.create_or_replay(
            value,
            session=retry,
        )

        retry.commit_transaction()

    assert replayed == value

    assert context.collection.count_documents(
        {
            "tenant_id":
                value.tenant_id,
        }
    ) == 1


def test_real_registry_surface_grants_no_execution_or_transaction_authority(
    mongo_context: _Context,
) -> None:
    _ = mongo_context

    source = Path(
        "tools/eos/legal_operations/registry/"
        "legal_evidence_provider_cleanup_authorization_registry.py"
    ).read_text()

    assert ".start_transaction(" not in source
    assert ".commit_transaction(" not in source
    assert ".abort_transaction(" not in source

    assert ".delete_one(" not in source
    assert ".delete_many(" not in source
    assert ".update_one(" not in source
    assert ".update_many(" not in source

    assert "expireAfterSeconds" not in source
    assert "delete_object" not in source
    assert "delete_objects" not in source
    assert "provider_delete" not in source

    methods = set(
        vars(
            LegalEvidenceProviderCleanupAuthorizationRegistry
        )
    )

    assert methods.isdisjoint(
        {
            "delete",
            "delete_object",
            "delete_objects",
            "execute",
            "remove",
            "update",
            "release_hold",
            "satisfy_retention",
            "authorize_provider_delete",
        }
    )


# ARTIFACT: test_legal_evidence_provider_cleanup_authorization_registry_real_mongo.py
# VERSION: v1.0.0-L10A2R-C4D6E-A2-PROVIDER-CLEANUP-AUTHORIZATION-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: actual Mongo cleanup-authorization durability/replay only
# TENANT POSTURE: exact tenant-scoped identities and cross-tenant opacity
# TRANSACTION POSTURE: caller owns active transaction; duplicate race requires abort + fresh retry
# REPLAY POSTURE: fresh-client durable exact replay only
# CORRUPTION POSTURE: corrupt/injected durable evidence rejects without healing
# TTL POSTURE: exact unique indexes and no TTL deletion
# PROVIDER MUTATION POSTURE: no provider mutation or deletion execution authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN CERTIFICATE
