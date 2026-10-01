"""Real-Mongo certificate for provider-object orphan-proof durability.

TITLE: Legal Evidence Provider Object Orphan Proof Registry Real-Mongo Certificate
VERSION: v1.0.0-L10A2R-C4D6D-B2-ORPHAN-PROOF-REGISTRY-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Certify actual MongoDB replica-set durability for immutable B1
         provider-object orphan proofs without granting later disposition authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_evidence_provider_object_orphan_proof_registry_real_mongo.py
COLLABORATION / OWNERSHIP:
    C4D6D-B1 owns positive orphan-proof truth.
    C4D6D-B2 owns only durable exact persistence/replay of that truth.
    This certificate owns disposable real-Mongo runtime evidence only.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.0-L10A2R-C4D6D-B2 certifies real replica-set topology, exact unique
    indexes, zero TTL, caller-owned active transactions, commit durability,
    fresh-client replay, rollback, exact replay, divergent provider-object
    rejection, reference collision rejection, tenant opacity, corruption
    rejection without healing, and real duplicate-key whole-transaction retry.
COMPLIANCE:
    Synthetic UUID-isolated runtime evidence only.
SECURITY / PRIVACY POSTURE:
    No production database and no real customer evidence is touched.
TENANT BOUNDARY:
    Every registry identity and read remains exact tenant scoped.
AUTHORITY BOUNDARY:
    Durable orphan-proof persistence/replay only. No inference from absence,
    retention satisfaction, legal-hold release, abort authority, deletion
    authorization or provider mutation.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.
TRANSACTION BOUNDARY:
    Tests own every session and transaction. Registry starts, commits, aborts
    and retries none.
TOPOLOGY BOUNDARY:
    Requires local/CI Mongo replica set wilsyVendorCertRS.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_provider_object_disownership import (
    LegalEvidenceProviderObjectDisownership,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_object_orphan_proof import (
    LegalEvidenceProviderObjectOrphanProof,
    prove_legal_evidence_provider_object_orphan,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_object_orphan_proof_registry import (
    COLLECTION,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    INDEX_TENANT_REFERENCE,
    LegalEvidenceProviderObjectOrphanProofConflictError,
    LegalEvidenceProviderObjectOrphanProofNotFoundError,
    LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
    LegalEvidenceProviderObjectOrphanProofRegistry,
    LegalEvidenceProviderObjectOrphanProofTransactionRequiredError,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceProviderDiscoveryScope,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_enumeration_port import (
    LegalEvidenceProviderEnumerationKind,
    LegalEvidenceProviderEnumerationPage,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_verification_service import (
    LegalEvidenceProviderCoverageVerificationService,
)


VERSION = (
    "v1.0.0-L10A2R-C4D6D-B2-"
    "ORPHAN-PROOF-REGISTRY-REAL-MONGO-CERT"
)

MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

AT = datetime(
    2026,
    10,
    1,
    12,
    0,
    tzinfo=timezone.utc,
)

SHA_A = "a" * 128
SHA_B = "b" * 128


class _MongoContext:
    """One UUID-isolated real-Mongo B2 certification context."""

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
            LegalEvidenceProviderObjectOrphanProofRegistry(
                collection
            )
        )


class _Provider:
    """Deterministic provider-enumeration source used only to issue valid B1 facts."""

    def __init__(
        self,
        *,
        scope: LegalEvidenceProviderDiscoveryScope,
        observation: LegalEvidenceCompletedObjectObservation,
    ) -> None:
        self.scope = scope
        self.observation = observation

    def list_incomplete_write_session_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        assert scope == self.scope
        assert observed_at == AT
        assert page_reference is None

        return LegalEvidenceProviderEnumerationPage(
            tenant_id=scope.tenant_id,
            tenant_scope_fingerprint=scope.tenant_scope_fingerprint,
            provider_name=self.observation.provider_name,
            enumeration_kind=(
                LegalEvidenceProviderEnumerationKind
                .INCOMPLETE_WRITE_SESSIONS
            ),
            observed_at=AT,
            observations=(),
            next_page_reference=None,
        )

    def list_completed_object_version_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        assert scope == self.scope
        assert observed_at == AT
        assert page_reference is None

        return LegalEvidenceProviderEnumerationPage(
            tenant_id=scope.tenant_id,
            tenant_scope_fingerprint=scope.tenant_scope_fingerprint,
            provider_name=self.observation.provider_name,
            enumeration_kind=(
                LegalEvidenceProviderEnumerationKind
                .COMPLETED_OBJECT_VERSIONS
            ),
            observed_at=AT,
            observations=(
                self.observation,
            ),
            next_page_reference=None,
        )


class _HideIdentityReads:
    """Force one real duplicate-key insert after hiding the replay pre-read scan."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = collection
        self._remaining_hidden_reads = 3

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: Any,
    ) -> Any:
        if self._remaining_hidden_reads > 0:
            self._remaining_hidden_reads -= 1
            return None

        return self._collection.find_one(
            query,
            session=session,
        )

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: Any,
    ) -> Any:
        return self._collection.insert_one(
            document,
            session=session,
        )


def _scope(
    *,
    tenant_id: str,
) -> LegalEvidenceProviderDiscoveryScope:
    return LegalEvidenceProviderDiscoveryScope(
        tenant_id=tenant_id,
        tenant_scope_fingerprint=SHA_A,
    )


def _observation(
    *,
    tenant_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
) -> LegalEvidenceCompletedObjectObservation:
    return LegalEvidenceCompletedObjectObservation(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        provider_integrity_reference='"etag-b2-real"',
        content_length=41,
        last_modified_at=AT,
        observed_at=AT,
        write_intent_metadata_state=(
            LegalEvidenceCompletedObjectIntentMetadataState.ABSENT
        ),
        write_intent_fingerprint=None,
    )


def _value(
    *,
    tenant_id: str = "tenant-b2-real",
    provider_name: str = "aws_s3",
    storage_reference: str = "legal-evidence/b2-real/object",
    object_version_reference: str = "version-b2-real",
    orphan_proof_reference: str = "orphan-proof-b2-real",
    proved_at: datetime = AT + timedelta(minutes=1),
) -> LegalEvidenceProviderObjectOrphanProof:
    scope = _scope(
        tenant_id=tenant_id,
    )

    observation = _observation(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
    )

    service = LegalEvidenceProviderCoverageVerificationService(
        provider=_Provider(
            scope=scope,
            observation=observation,
        )
    )

    verification = service.verify_coverage(
        scope=scope,
        provider_name=provider_name,
        observed_at=AT,
    )

    disownership = LegalEvidenceProviderObjectDisownership(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        disownership_reference=(
            "disownership:"
            + tenant_id
            + ":"
            + object_version_reference
        ),
        reason_reference="reason:b2-real",
        source_evidence_reference="source:b2-real",
        source_evidence_fingerprint=SHA_A,
        authorization_evidence_reference="authorization:b2-real",
        authorization_evidence_fingerprint=SHA_B,
        decided_at=AT - timedelta(minutes=5),
    )

    return prove_legal_evidence_provider_object_orphan(
        coverage_service=service,
        verification=verification,
        observation=observation,
        disownership=disownership,
        orphan_proof_reference=orphan_proof_reference,
        proved_at=proved_at,
    )


def _start(
    session: Any,
) -> None:
    session.start_transaction(
        read_concern=ReadConcern(
            "snapshot"
        ),
        write_concern=WriteConcern(
            "majority",
            j=True,
        ),
    )


def _commit(
    context: _MongoContext,
    value: LegalEvidenceProviderObjectOrphanProof,
) -> LegalEvidenceProviderObjectOrphanProof:
    with context.client.start_session() as session:
        _start(
            session
        )

        result = context.registry.create_or_replay(
            value,
            session=session,
        )

        session.commit_transaction()

    return result


@pytest.fixture()
def mongo_context() -> Iterator[_MongoContext]:
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
            "C4D6D-B2 requires writable "
            "wilsyVendorCertRS replica set"
        )

    database_name = (
        "wilsy_c4d6d_b2_"
        + uuid4().hex
    )

    database = client[
        database_name
    ]

    collection = database.get_collection(
        COLLECTION,
        write_concern=WriteConcern(
            "majority",
            j=True,
        ),
        read_concern=ReadConcern(
            "majority"
        ),
    )

    context = _MongoContext(
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


def test_real_topology_database_and_indexes(
    mongo_context: _MongoContext,
) -> None:
    context = mongo_context

    assert context.database.name.startswith(
        "wilsy_c4d6d_b2_"
    )

    assert (
        context.database.name
        != "wilsy"
    )

    hello = context.client.admin.command(
        "hello"
    )

    assert (
        hello["setName"]
        == EXPECTED_REPLICA_SET
    )

    assert (
        hello["isWritablePrimary"]
        is True
    )

    entries = {
        item["name"]: item
        for item
        in context.collection.list_indexes()
        if item["name"] != "_id_"
    }

    assert set(
        entries
    ) == {
        INDEX_TENANT_REFERENCE,
        INDEX_TENANT_FINGERPRINT,
        INDEX_TENANT_PROVIDER_OBJECT,
    }

    assert dict(
        entries[
            INDEX_TENANT_REFERENCE
        ]["key"]
    ) == {
        "tenant_id": 1,
        "orphan_proof_reference": 1,
    }

    assert (
        entries[
            INDEX_TENANT_REFERENCE
        ].get(
            "unique"
        )
        is True
    )

    assert dict(
        entries[
            INDEX_TENANT_FINGERPRINT
        ]["key"]
    ) == {
        "tenant_id": 1,
        "fingerprint": 1,
    }

    assert (
        entries[
            INDEX_TENANT_FINGERPRINT
        ].get(
            "unique"
        )
        is True
    )

    assert dict(
        entries[
            INDEX_TENANT_PROVIDER_OBJECT
        ]["key"]
    ) == {
        "tenant_id": 1,
        "provider_name": 1,
        "storage_reference": 1,
        "object_version_reference": 1,
    }

    assert (
        entries[
            INDEX_TENANT_PROVIDER_OBJECT
        ].get(
            "unique"
        )
        is True
    )

    assert all(
        "expireAfterSeconds"
        not in item
        for item in entries.values()
    )


def test_real_inactive_transaction_rejects_before_write(
    mongo_context: _MongoContext,
) -> None:
    context = mongo_context
    value = _value()

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofTransactionRequiredError,
        match="L10A2R_C4D6D_B2_ACTIVE_TRANSACTION_REQUIRED",
    ):
        context.registry.create_or_replay(
            value,
            session=None,
        )

    with context.client.start_session() as inactive:
        with pytest.raises(
            LegalEvidenceProviderObjectOrphanProofTransactionRequiredError,
            match="L10A2R_C4D6D_B2_ACTIVE_TRANSACTION_REQUIRED",
        ):
            context.registry.create_or_replay(
                value,
                session=inactive,
            )

    assert (
        context.collection.count_documents(
            {}
        )
        == 0
    )


def test_real_commit_restart_replay_and_tenant_opacity(
    mongo_context: _MongoContext,
) -> None:
    context = mongo_context
    value = _value()

    assert (
        _commit(
            context,
            value,
        )
        == value
    )

    fresh_client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        retryWrites=True,
        tz_aware=True,
    )

    try:
        collection = fresh_client[
            context.database.name
        ].get_collection(
            COLLECTION,
            write_concern=WriteConcern(
                "majority",
                j=True,
            ),
            read_concern=ReadConcern(
                "majority"
            ),
        )

        restarted = (
            LegalEvidenceProviderObjectOrphanProofRegistry(
                collection
            )
        )

        with fresh_client.start_session() as session:
            _start(
                session
            )

            replayed = restarted.create_or_replay(
                value,
                session=session,
            )

            assert replayed == value

            assert (
                restarted.get_by_reference(
                    tenant_id=value.tenant_id,
                    orphan_proof_reference=(
                        value.orphan_proof_reference
                    ),
                    session=session,
                )
                == value
            )

            with pytest.raises(
                LegalEvidenceProviderObjectOrphanProofNotFoundError,
                match="L10A2R_C4D6D_B2_NOT_FOUND",
            ):
                restarted.get_by_reference(
                    tenant_id="tenant-other",
                    orphan_proof_reference=(
                        value.orphan_proof_reference
                    ),
                    session=session,
                )

            session.commit_transaction()

    finally:
        fresh_client.close()

    assert (
        context.collection.count_documents(
            {
                "tenant_id":
                    value.tenant_id,
            }
        )
        == 1
    )


def test_real_aborted_transaction_rolls_back(
    mongo_context: _MongoContext,
) -> None:
    context = mongo_context
    value = _value(
        orphan_proof_reference=(
            "orphan-proof-b2-abort"
        )
    )

    with context.client.start_session() as session:
        _start(
            session
        )

        context.registry.create_or_replay(
            value,
            session=session,
        )

        assert (
            context.collection.count_documents(
                {
                    "tenant_id":
                        value.tenant_id,
                },
                session=session,
            )
            == 1
        )

        session.abort_transaction()

    assert (
        context.collection.count_documents(
            {
                "tenant_id":
                    value.tenant_id,
            }
        )
        == 0
    )


def test_real_exact_replay_is_one_row(
    mongo_context: _MongoContext,
) -> None:
    context = mongo_context
    value = _value(
        orphan_proof_reference=(
            "orphan-proof-b2-replay"
        )
    )

    assert _commit(
        context,
        value,
    ) == value

    assert _commit(
        context,
        value,
    ) == value

    assert (
        context.collection.count_documents(
            {
                "tenant_id":
                    value.tenant_id,
            }
        )
        == 1
    )


def test_real_provider_object_divergence_rejects_without_second_row(
    mongo_context: _MongoContext,
) -> None:
    context = mongo_context
    value = _value(
        orphan_proof_reference=(
            "orphan-proof-b2-base"
        )
    )

    _commit(
        context,
        value,
    )

    divergent = _value(
        orphan_proof_reference=(
            "orphan-proof-b2-divergent"
        ),
        proved_at=(
            AT
            + timedelta(
                minutes=2
            )
        ),
    )

    with context.client.start_session() as session:
        _start(
            session
        )

        with pytest.raises(
            LegalEvidenceProviderObjectOrphanProofConflictError,
            match="L10A2R_C4D6D_B2_IMMUTABLE_DIVERGENCE",
        ):
            context.registry.create_or_replay(
                divergent,
                session=session,
            )

        session.abort_transaction()

    assert (
        context.collection.count_documents(
            {
                "tenant_id":
                    value.tenant_id,
            }
        )
        == 1
    )


def test_real_reference_collision_other_provider_object_rejects(
    mongo_context: _MongoContext,
) -> None:
    context = mongo_context
    value = _value(
        orphan_proof_reference=(
            "orphan-proof-b2-reference"
        )
    )

    _commit(
        context,
        value,
    )

    divergent = _value(
        storage_reference=(
            "legal-evidence/b2-real/other"
        ),
        object_version_reference=(
            "version-b2-real-other"
        ),
        orphan_proof_reference=(
            value.orphan_proof_reference
        ),
    )

    with context.client.start_session() as session:
        _start(
            session
        )

        with pytest.raises(
            LegalEvidenceProviderObjectOrphanProofConflictError,
            match="L10A2R_C4D6D_B2_IMMUTABLE_DIVERGENCE",
        ):
            context.registry.create_or_replay(
                divergent,
                session=session,
            )

        session.abort_transaction()

    assert (
        context.collection.count_documents(
            {}
        )
        == 1
    )


def test_real_cross_tenant_same_provider_object_isolated(
    mongo_context: _MongoContext,
) -> None:
    context = mongo_context

    tenant_a = _value(
        tenant_id="tenant-b2-real-a",
        orphan_proof_reference=(
            "orphan-proof-b2-a"
        ),
    )

    tenant_b = _value(
        tenant_id="tenant-b2-real-b",
        orphan_proof_reference=(
            "orphan-proof-b2-b"
        ),
    )

    _commit(
        context,
        tenant_a,
    )

    _commit(
        context,
        tenant_b,
    )

    assert (
        context.collection.count_documents(
            {}
        )
        == 2
    )

    with context.client.start_session() as session:
        _start(
            session
        )

        assert (
            context.registry.get_by_provider_object(
                tenant_id=tenant_a.tenant_id,
                provider_name=tenant_a.provider_name,
                storage_reference=tenant_a.storage_reference,
                object_version_reference=(
                    tenant_a.object_version_reference
                ),
                session=session,
            )
            == tenant_a
        )

        assert (
            context.registry.get_by_provider_object(
                tenant_id=tenant_b.tenant_id,
                provider_name=tenant_b.provider_name,
                storage_reference=tenant_b.storage_reference,
                object_version_reference=(
                    tenant_b.object_version_reference
                ),
                session=session,
            )
            == tenant_b
        )

        session.commit_transaction()


def test_real_corruption_rejects_without_healing(
    mongo_context: _MongoContext,
) -> None:
    context = mongo_context
    value = _value(
        orphan_proof_reference=(
            "orphan-proof-b2-corrupt"
        )
    )

    _commit(
        context,
        value,
    )

    changed = context.collection.update_one(
        {
            "tenant_id":
                value.tenant_id,
            "orphan_proof_reference":
                value.orphan_proof_reference,
        },
        {
            "$set": {
                "coverage_verification_fingerprint":
                    "f" * 128,
            }
        },
    )

    assert (
        changed.modified_count
        == 1
    )

    corrupt_before = context.collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
            "orphan_proof_reference":
                value.orphan_proof_reference,
        }
    )

    assert corrupt_before is not None

    with context.client.start_session() as session:
        _start(
            session
        )

        with pytest.raises(
            LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
            match="L10A2R_C4D6D_B2_PERSISTED_RECORD_INVALID",
        ):
            context.registry.get_by_reference(
                tenant_id=value.tenant_id,
                orphan_proof_reference=(
                    value.orphan_proof_reference
                ),
                session=session,
            )

        session.abort_transaction()

    corrupt_after = context.collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
            "orphan_proof_reference":
                value.orphan_proof_reference,
        }
    )

    assert (
        corrupt_after
        == corrupt_before
    )


def test_real_duplicate_key_requires_abort_then_fresh_transaction_replays(
    mongo_context: _MongoContext,
) -> None:
    context = mongo_context

    value = _value(
        orphan_proof_reference=(
            "orphan-proof-b2-duplicate"
        )
    )

    _commit(
        context,
        value,
    )

    stale_registry = (
        LegalEvidenceProviderObjectOrphanProofRegistry(
            _HideIdentityReads(
                context.collection
            )
        )
    )

    with context.client.start_session() as stale:
        _start(
            stale
        )

        with pytest.raises(
            LegalEvidenceProviderObjectOrphanProofConflictError,
            match="L10A2R_C4D6D_B2_WHOLE_TRANSACTION_RETRY_REQUIRED",
        ):
            stale_registry.create_or_replay(
                value,
                session=stale,
            )

        stale.abort_transaction()

    with context.client.start_session() as retry:
        _start(
            retry
        )

        replayed = context.registry.create_or_replay(
            value,
            session=retry,
        )

        retry.commit_transaction()

    assert replayed == value

    assert (
        context.collection.count_documents(
            {
                "tenant_id":
                    value.tenant_id,
            }
        )
        == 1
    )


def test_real_registry_surface_grants_no_later_authority(
    mongo_context: _MongoContext,
) -> None:
    del mongo_context

    forbidden = {
        "authorize_abort",
        "authorize_delete",
        "authorize_deletion",
        "delete",
        "delete_one",
        "delete_many",
        "delete_object",
        "delete_objects",
        "provider_delete",
        "release_legal_hold",
        "retention_satisfied",
        "update",
        "update_one",
        "update_many",
    }

    assert forbidden.isdisjoint(
        dir(
            LegalEvidenceProviderObjectOrphanProofRegistry
        )
    )


# ARTIFACT: test_legal_evidence_provider_object_orphan_proof_registry_real_mongo.py
# VERSION: v1.0.0-L10A2R-C4D6D-B2-ORPHAN-PROOF-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: actual Mongo durability/replay of already-proved B1 evidence only
# TENANT POSTURE: exact tenant-scoped identity/read opacity
# TRANSACTION POSTURE: caller owns active transaction; duplicate race requires retry
# REPLAY POSTURE: fresh-client durable exact replay only
# CORRUPTION POSTURE: corrupt durable evidence rejects without healing
# TTL POSTURE: exact indexes and no TTL deletion
# ORPHAN POSTURE: persistence does not infer or create orphan proof
# RETENTION / HOLD POSTURE: no retention satisfaction or legal-hold release authority
# DELETION POSTURE: no abort/delete authorization/update/delete/provider mutation authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
