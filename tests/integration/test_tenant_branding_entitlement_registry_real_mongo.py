"""Real-Mongo certificate for the D21B2B branding entitlement registry.

TITLE: Tenant Branding Entitlement Registry Real-Mongo Certificate
VERSION: v1.0.0-D21B2B-TENANT-BRANDING-ENTITLEMENT-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Physically certify immutable entitlement revision history, explicit
         exact-entitlement currentness, caller-owned transactions, lifecycle CAS,
         corruption rejection and competing-transition retry semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_branding_entitlement_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Host-backed D21B2B certificate only. D21B2 owns
                            lifecycle semantics; D21B2B owns durable history and
                            exact currentness; caller owns Mongo transactions.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B2B-TENANT-BRANDING-ENTITLEMENT-REGISTRY-REAL-MONGO-CERT
           establishes physical evidence for exact indexes, create/replay,
           transaction rollback, ACTIVE/SUSPENDED transitions, replay/stale
           protection, corruption rejection, compact current pointers, tenant
           isolation and a genuine competing transition race.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and disposable local
                             database only; no credentials, brand assets, browser
                             state or external services.
TENANT BOUNDARY: Every registry operation and physical uniqueness primitive is
                 exact-tenant/exact-entitlement scoped; foreign scope is absence.
AUTHORITY BOUNDARY: Durable D21B2 lifecycle/currentness evidence only; no profile,
                    asset, browser, IAM, workspace or legal-command authority.
FINANCIAL AUTHORITY BOUNDARY: No financial execution/settlement truth; Kennel
                               EOS remains exclusive.
TRANSACTION BOUNDARY: Certificate owns test transactions; registry must only
                      require/propagate supplied active sessions.
FAIL-CLOSED DECLARATION: Wrong/unavailable replica set may skip only pre-yield.
                         Once yielded, index, transaction, hydration, replay,
                         CAS, corruption or concurrency failures fail.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import os
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.billing import tenant_branding_entitlement_registry as registry
from tools.eos.saas.billing.tenant_branding_vas_policy import TenantBrandingTier
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlement,
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)


VERSION = "v1.0.0-D21B2B-TENANT-BRANDING-ENTITLEMENT-REGISTRY-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 25, 16, 0, tzinfo=timezone.utc)
FP = "a" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any, Any]]:
    """Yield one UUID-isolated writable replica-set database."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(
                f"host Mongo unavailable during hello: {type(error).__name__}: {error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("replica set has no logical-session capability")

        database = client[f"wilsy_d21b2b_branding_{uuid.uuid4().hex}"]
        history = database.get_collection(
            registry.HISTORY_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        current = database.get_collection(
            registry.CURRENT_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        registry.ensure_indexes(history, current)
        yield client, database, history, current
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _pending(
    tenant_id: str,
    entitlement_id: str = "branding-entitlement-1",
) -> TenantBrandingEntitlement:
    """Build one exact pending D21B2 entitlement."""
    return create_tenant_branding_entitlement(
        tenant_id=tenant_id,
        entitlement_id=entitlement_id,
        branding_tier=TenantBrandingTier.PROFESSIONAL,
        source_evidence_reference="composition-1",
        source_evidence_fingerprint=FP,
    )


def _commit_create(
    client: MongoClient[Any],
    entitlement: TenantBrandingEntitlement,
    history: Any,
    current: Any,
) -> registry.TenantBrandingEntitlementPersistenceResult:
    """Persist initial entitlement in one caller-owned committed transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return registry.create_or_replay(
                entitlement,
                history,
                current,
                session=session,
            )


def _commit_transition(
    client: MongoClient[Any],
    *,
    tenant_id: str,
    entitlement_id: str,
    target_state: TenantBrandingEntitlementState,
    expected_revision: int,
    evidence_reference: str,
    history: Any,
    current: Any,
) -> registry.TenantBrandingEntitlementPersistenceResult:
    """Commit one exact registry-derived lifecycle transition."""
    with client.start_session() as session:
        with session.start_transaction():
            return registry.transition(
                tenant_id=tenant_id,
                entitlement_id=entitlement_id,
                target_state=target_state,
                expected_revision=expected_revision,
                evidence_reference=evidence_reference,
                evidence_fingerprint=FP,
                occurred_at=NOW,
                history_collection=history,
                current_collection=current,
                session=session,
            )


def _raw_without_id(collection: Any, query: dict[str, object]) -> dict[str, Any]:
    """Return one physical row without Mongo transport-only _id."""
    row = collection.find_one(query)
    assert isinstance(row, dict)
    payload = dict(row)
    payload.pop("_id", None)
    return payload


def test_real_indexes_are_exact_unique_and_have_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """Physically prove three exact uniqueness primitives and no TTL."""
    _, _, history, current = mongo_context
    history_indexes = {
        item["name"]: item
        for item in history.list_indexes()
        if item["name"] != "_id_"
    }
    current_indexes = {
        item["name"]: item
        for item in current.list_indexes()
        if item["name"] != "_id_"
    }
    assert set(history_indexes) == {
        registry.HISTORY_REVISION_INDEX_NAME,
        registry.HISTORY_FINGERPRINT_INDEX_NAME,
    }
    assert dict(
        history_indexes[registry.HISTORY_REVISION_INDEX_NAME]["key"]
    ) == {
        "tenant_id": 1,
        "entitlement_id": 1,
        "lifecycle_revision": 1,
    }
    assert dict(
        history_indexes[registry.HISTORY_FINGERPRINT_INDEX_NAME]["key"]
    ) == {
        "tenant_id": 1,
        "entitlement_fingerprint": 1,
    }
    assert set(current_indexes) == {registry.CURRENT_IDENTITY_INDEX_NAME}
    assert dict(
        current_indexes[registry.CURRENT_IDENTITY_INDEX_NAME]["key"]
    ) == {
        "tenant_id": 1,
        "entitlement_id": 1,
    }
    all_indexes = [*history_indexes.values(), *current_indexes.values()]
    assert all(item.get("unique") is True for item in all_indexes)
    assert all("expireAfterSeconds" not in item for item in all_indexes)


def test_real_create_replay_and_cross_tenant_absence(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """Certify committed create, exact replay and foreign-tenant silence."""
    client, _, history, current = mongo_context
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"
    value = _pending(tenant_a)
    first = _commit_create(client, value, history, current)
    replay = _commit_create(client, value, history, current)
    assert first.outcome is registry.TenantBrandingEntitlementPersistenceOutcome.CREATED
    assert replay.outcome is registry.TenantBrandingEntitlementPersistenceOutcome.IDEMPOTENT_REPLAY
    assert history.count_documents({"tenant_id": tenant_a}) == 1
    assert current.count_documents({"tenant_id": tenant_a}) == 1

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.TenantBrandingEntitlementRegistryNotFoundError):
                registry.get_current(
                    tenant_b,
                    value.entitlement_id,
                    history,
                    current,
                    session=session,
                )


def test_real_active_transaction_required_and_abort_rolls_back_atomically(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """Registry owns no transaction lifecycle and caller abort removes both rows."""
    client, _, history, current = mongo_context
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    value = _pending(tenant)

    with pytest.raises(
        registry.TenantBrandingEntitlementRegistryTransactionRequiredError
    ):
        registry.create_or_replay(value, history, current, session=None)

    with client.start_session() as inactive:
        assert inactive.in_transaction is False
        with pytest.raises(
            registry.TenantBrandingEntitlementRegistryTransactionRequiredError
        ):
            registry.create_or_replay(value, history, current, session=inactive)

    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(value, history, current, session=session)
        assert history.count_documents({"tenant_id": tenant}, session=session) == 1
        assert current.count_documents({"tenant_id": tenant}, session=session) == 1
        session.abort_transaction()

    assert history.count_documents({"tenant_id": tenant}) == 0
    assert current.count_documents({"tenant_id": tenant}) == 0


def test_real_transition_cas_and_exact_replay_preserve_explicit_currentness(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """Certify ACTIVE transition, exact replay and SUSPENDED CAS advancement."""
    client, _, history, current = mongo_context
    tenant = f"tenant-transition-{uuid.uuid4().hex}"
    value = _pending(tenant)
    _commit_create(client, value, history, current)

    activated = _commit_transition(
        client,
        tenant_id=tenant,
        entitlement_id=value.entitlement_id,
        target_state=TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-1",
        history=history,
        current=current,
    )
    assert activated.entitlement.lifecycle_state is TenantBrandingEntitlementState.ACTIVE
    assert activated.entitlement.lifecycle_revision == 1

    replay = _commit_transition(
        client,
        tenant_id=tenant,
        entitlement_id=value.entitlement_id,
        target_state=TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-1",
        history=history,
        current=current,
    )
    assert replay.outcome is registry.TenantBrandingEntitlementPersistenceOutcome.IDEMPOTENT_REPLAY

    suspended = _commit_transition(
        client,
        tenant_id=tenant,
        entitlement_id=value.entitlement_id,
        target_state=TenantBrandingEntitlementState.SUSPENDED,
        expected_revision=1,
        evidence_reference="suspension-1",
        history=history,
        current=current,
    )
    assert suspended.entitlement.lifecycle_state is TenantBrandingEntitlementState.SUSPENDED
    assert suspended.entitlement.lifecycle_revision == 2
    assert history.count_documents({"tenant_id": tenant}) == 3
    assert current.count_documents({"tenant_id": tenant}) == 1

    raw = _raw_without_id(current, {"tenant_id": tenant})
    assert raw["lifecycle_revision"] == 2
    assert raw["lifecycle_state"] == TenantBrandingEntitlementState.SUSPENDED.value


def test_real_stale_initial_and_changed_transition_replay_fail_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """Historical creation/replay cannot obscure or rewrite current lifecycle."""
    client, _, history, current = mongo_context
    tenant = f"tenant-stale-{uuid.uuid4().hex}"
    value = _pending(tenant)
    _commit_create(client, value, history, current)
    _commit_transition(
        client,
        tenant_id=tenant,
        entitlement_id=value.entitlement_id,
        target_state=TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-1",
        history=history,
        current=current,
    )

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(
            registry.TenantBrandingEntitlementRegistryConflictError
        ) as raised:
            registry.create_or_replay(
                value,
                history,
                current,
                session=session,
            )
        assert raised.value.code == "D21B2B_STALE_INITIAL_REPLAY"
        session.abort_transaction()

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(
            registry.TenantBrandingEntitlementRegistryConflictError
        ) as raised:
            registry.transition(
                tenant_id=tenant,
                entitlement_id=value.entitlement_id,
                target_state=TenantBrandingEntitlementState.ACTIVE,
                expected_revision=0,
                evidence_reference="different-activation",
                evidence_fingerprint=FP,
                occurred_at=NOW,
                history_collection=history,
                current_collection=current,
                session=session,
            )
        assert raised.value.code == "D21B2B_TRANSITION_REPLAY_CONFLICT"
        session.abort_transaction()

    assert _raw_without_id(current, {"tenant_id": tenant})["lifecycle_revision"] == 1


def test_real_corrupt_history_or_pointer_rejects_current_hydration(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """Physical history and pointer corruption never becomes current authority."""
    client, _, history, current = mongo_context
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    value = _pending(tenant)
    _commit_create(client, value, history, current)

    original_history = deepcopy(history.find_one({"tenant_id": tenant}))
    original_current = deepcopy(current.find_one({"tenant_id": tenant}))
    assert isinstance(original_history, dict)
    assert isinstance(original_current, dict)

    history.update_one(
        {"tenant_id": tenant},
        {"$set": {"entitlement_payload.fingerprint": "f" * 128}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.TenantBrandingEntitlementRegistryPersistedRecordInvalidError
            ):
                registry.get_current(
                    tenant,
                    value.entitlement_id,
                    history,
                    current,
                    session=session,
                )
    history.replace_one({"_id": original_history["_id"]}, original_history)

    current.update_one(
        {"tenant_id": tenant},
        {"$set": {"entitlement_fingerprint": "e" * 128}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.TenantBrandingEntitlementRegistryPersistedRecordInvalidError
            ):
                registry.get_current(
                    tenant,
                    value.entitlement_id,
                    history,
                    current,
                    session=session,
                )
    current.replace_one({"_id": original_current["_id"]}, original_current)


def test_real_current_pointer_is_unique_and_contains_no_unrelated_authority(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """Physically prove one compact pointer per exact tenant/entitlement."""
    client, _, history, current = mongo_context
    tenant = f"tenant-pointer-{uuid.uuid4().hex}"
    value = _pending(tenant)
    _commit_create(client, value, history, current)

    raw = _raw_without_id(current, {"tenant_id": tenant})
    forbidden = {
        "logo",
        "logo_url",
        "logo_asset_reference",
        "primary_color",
        "secondary_color",
        "accent_color",
        "email_identity",
        "favicon",
        "custom_domain",
        "profile_id",
        "principal_id",
        "role",
        "permission",
        "price",
        "amount",
        "currency",
        "bank",
        "invoice",
        "payment",
        "execution",
        "settlement",
    }
    assert forbidden.isdisjoint(raw)

    duplicate = deepcopy(raw)
    duplicate["lifecycle_revision"] = 99
    duplicate["entitlement_fingerprint"] = "d" * 128
    duplicate["fingerprint"] = "c" * 128
    with pytest.raises(DuplicateKeyError):
        current.insert_one(duplicate)
    assert current.count_documents({"tenant_id": tenant}) == 1


def test_real_competing_active_transitions_have_one_commit_and_one_retry(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """A genuine ACTIVE race cannot commit both SUSPENDED and REVOKED currentness."""
    client, _, history, current = mongo_context
    tenant = f"tenant-race-{uuid.uuid4().hex}"
    value = _pending(tenant)
    _commit_create(client, value, history, current)
    _commit_transition(
        client,
        tenant_id=tenant,
        entitlement_id=value.entitlement_id,
        target_state=TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-1",
        history=history,
        current=current,
    )

    barrier = Barrier(2)

    def contender(
        command: tuple[TenantBrandingEntitlementState, str],
    ) -> str:
        target_state, evidence_reference = command
        with client.start_session() as session:
            session.start_transaction()
            barrier.wait()
            try:
                registry.transition(
                    tenant_id=tenant,
                    entitlement_id=value.entitlement_id,
                    target_state=target_state,
                    expected_revision=1,
                    evidence_reference=evidence_reference,
                    evidence_fingerprint=FP,
                    occurred_at=NOW,
                    history_collection=history,
                    current_collection=current,
                    session=session,
                )
                session.commit_transaction()
                return "COMMITTED"
            except registry.TenantBrandingEntitlementRegistryRetryRequiredError:
                if session.in_transaction:
                    session.abort_transaction()
                return "RETRY_REQUIRED"
            except Exception as error:
                if session.in_transaction:
                    session.abort_transaction()
                return type(error).__name__

    commands = (
        (TenantBrandingEntitlementState.SUSPENDED, "suspension-race"),
        (TenantBrandingEntitlementState.REVOKED, "revocation-race"),
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(contender, commands))

    assert outcomes.count("COMMITTED") == 1
    assert outcomes.count("RETRY_REQUIRED") == 1
    assert history.count_documents(
        {"tenant_id": tenant, "lifecycle_revision": 2}
    ) == 1
    assert current.count_documents({"tenant_id": tenant}) == 1
    raw = _raw_without_id(current, {"tenant_id": tenant})
    assert raw["lifecycle_revision"] == 2
    assert raw["lifecycle_state"] in {
        TenantBrandingEntitlementState.SUSPENDED.value,
        TenantBrandingEntitlementState.REVOKED.value,
    }


# ARTIFACT: test_tenant_branding_entitlement_registry_real_mongo.py
# VERSION: v1.0.0-D21B2B-TENANT-BRANDING-ENTITLEMENT-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical D21B2B history/currentness evidence only; no profile, asset, browser, IAM or financial authority
# TENANT POSTURE: UUID-isolated database and exact tenant/entitlement indexes, reads, writes and CAS
# FAIL-CLOSED POSTURE: post-yield transaction, replay, CAS, corruption and concurrency failures fail certification
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
