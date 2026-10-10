"""Real-Mongo certificate for the Legal product availability projection.

TITLE: Legal Product Availability Projection Real-Mongo Certificate
VERSION: v1.0.0-D22B5-R7-LEGAL-PRODUCT-AVAILABILITY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify the pure Legal product availability projection against real
         D22B2 durable current entitlement truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_product_availability_projection_real_mongo.py
COLLABORATION / OWNERSHIP: D22A owns product/workspace description; D22B1 owns
                            lifecycle semantics; D22B2 owns durable currentness;
                            D22B3 owns deterministic lineage identity; R6 owns
                            the read projection. This file owns test evidence only.
CERTIFICATION / UPDATE DATE: 2026-10-10
CHANGELOG: v1.0.0-D22B5-R7-LEGAL-PRODUCT-AVAILABILITY-REAL-MONGO-CERT
           establishes physical absence, lifecycle, isolation, pointer,
           corruption, active-transaction, and zero-write evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenant evidence in the
                             sanctioned disposable local replica set only.
TENANT POSTURE: UUID-isolated exact-tenant real-Mongo evidence; no shared or
                canonical database is accessed.
AUTHORITY BOUNDARY: Read projection certification only; no IAM, admission,
                    HTTP, workspace, subscription, or commercial mutation.
TRANSACTION BOUNDARY: Every authoritative projection read occurs in an active
                      caller-owned transaction; production owns no lifecycle.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Wrong runtime may skip only before fixture yield;
                         every post-yield lifecycle, isolation, corruption,
                         pointer, or read-only failure fails certification.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlement,
    TenantProductEntitlementState,
    create_tenant_product_entitlement,
)
from tools.eos.saas.entitlement import legal_product_availability_projection as projection
from tools.eos.saas.entitlement import tenant_product_entitlement_registry as registry
from tools.eos.saas.entitlement.product_catalogue import (
    TenantProductId,
    get_tenant_product,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)


VERSION = "v1.0.0-D22B5-R7-LEGAL-PRODUCT-AVAILABILITY-REAL-MONGO-CERT"
SANCTIONED_MONGO_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 10, 10, 10, 0, tzinfo=timezone.utc)
EVIDENCE_FINGERPRINT = "a" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any, Any]]:
    """Yield one UUID-isolated database on only the sanctioned replica set."""
    configured_uri = os.getenv("TEST_VENDOR_MONGO_URI")
    if configured_uri != SANCTIONED_MONGO_URI:
        pytest.skip("exact sanctioned TEST_VENDOR_MONGO_URI is required")

    client: MongoClient[Any] = MongoClient(
        SANCTIONED_MONGO_URI,
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
                f"sanctioned Mongo unavailable before fixture yield: "
                f"{type(error).__name__}: {error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("sanctioned replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("sanctioned replica set lacks logical sessions")

        database = client[f"wilsy_d22b5_r7_projection_{uuid.uuid4().hex}"]
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


def _identity(tenant_id: str) -> str:
    """Derive the production Legal Operations entitlement lineage identity."""
    return derive_tenant_product_entitlement_id(
        tenant_id,
        TenantProductId.LEGAL_OPERATIONS,
    )


def _pending(tenant_id: str) -> TenantProductEntitlement:
    """Build one canonical pending Legal entitlement through D22B1."""
    return create_tenant_product_entitlement(
        tenant_id=tenant_id,
        entitlement_id=_identity(tenant_id),
        product_id=TenantProductId.LEGAL_OPERATIONS,
        source_evidence_reference=f"d22b5-r7-source:{tenant_id}",
        source_evidence_fingerprint=EVIDENCE_FINGERPRINT,
    )


def _create(
    client: MongoClient[Any],
    tenant_id: str,
    history: Any,
    current: Any,
) -> TenantProductEntitlement:
    """Commit one canonical pending lineage in a caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            result = registry.create_or_replay(
                _pending(tenant_id),
                history,
                current,
                session=session,
            )
    return result.entitlement


def _transition(
    client: MongoClient[Any],
    tenant_id: str,
    target: TenantProductEntitlementState,
    expected_revision: int,
    history: Any,
    current: Any,
) -> TenantProductEntitlement:
    """Commit one legal production-registry lifecycle transition."""
    occurred_at = NOW + timedelta(minutes=expected_revision)
    with client.start_session() as session:
        with session.start_transaction():
            result = registry.transition(
                tenant_id=tenant_id,
                entitlement_id=_identity(tenant_id),
                target_state=target,
                expected_revision=expected_revision,
                evidence_reference=f"d22b5-r7-{target.value.lower()}:{tenant_id}",
                evidence_fingerprint=EVIDENCE_FINGERPRINT,
                occurred_at=occurred_at,
                history_collection=history,
                current_collection=current,
                session=session,
            )
    return result.entitlement


def _resolve(
    client: MongoClient[Any],
    tenant_id: str,
    history: Any,
    current: Any,
) -> projection.LegalProductAvailabilityProjection:
    """Resolve inside the certificate-owned active transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            assert session.in_transaction is True
            return projection.resolve_legal_product_availability(
                tenant_id,
                history,
                current,
                session=session,
            )


def _rows(collection: Any, tenant_id: str) -> list[dict[str, Any]]:
    """Snapshot exact physical tenant rows in deterministic revision order."""
    rows = deepcopy(list(collection.find({"tenant_id": tenant_id})))
    return sorted(rows, key=lambda item: int(item.get("lifecycle_revision", -1)))


def test_real_absence_projects_canonical_unavailable_without_writes(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """Real absence is lawful, canonical, deterministic, and read-only."""
    client, _, history, current = mongo_context
    tenant = f"tenant-absence-{uuid.uuid4().hex}"
    result = _resolve(client, tenant, history, current)
    assert result.available is False
    assert result.lifecycle_state is None
    assert result.product_id is TenantProductId.LEGAL_OPERATIONS
    assert result.workspace_key == get_tenant_product(
        TenantProductId.LEGAL_OPERATIONS
    ).workspace_key
    assert result.entitlement_id == _identity(tenant)
    assert history.count_documents({"tenant_id": tenant}) == 0
    assert current.count_documents({"tenant_id": tenant}) == 0


def test_real_pending_projects_unavailable(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """A canonically persisted PENDING_SOURCE lineage is unavailable."""
    client, _, history, current = mongo_context
    tenant = f"tenant-pending-{uuid.uuid4().hex}"
    persisted = _create(client, tenant, history, current)
    result = _resolve(client, tenant, history, current)
    assert persisted.entitlement_id == _identity(tenant)
    assert result.lifecycle_state is TenantProductEntitlementState.PENDING_SOURCE
    assert result.available is False


def test_real_active_projects_available_and_performs_zero_writes(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """ACTIVE current truth projects available without durable mutation."""
    client, _, history, current = mongo_context
    tenant = f"tenant-active-{uuid.uuid4().hex}"
    _create(client, tenant, history, current)
    active = _transition(
        client, tenant, TenantProductEntitlementState.ACTIVE, 0, history, current
    )
    history_before = _rows(history, tenant)
    current_before = _rows(current, tenant)
    result = _resolve(client, tenant, history, current)
    assert active.entitlement_id == _identity(tenant)
    assert result.lifecycle_state is TenantProductEntitlementState.ACTIVE
    assert result.available is True
    assert _rows(history, tenant) == history_before
    assert _rows(current, tenant) == current_before


@pytest.mark.parametrize(
    "target",
    [
        TenantProductEntitlementState.SUSPENDED,
        TenantProductEntitlementState.REVOKED,
    ],
)
def test_real_terminal_non_active_states_project_unavailable(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
    target: TenantProductEntitlementState,
) -> None:
    """Legal ACTIVE-to-terminal transitions preserve exact unavailable state."""
    client, _, history, current = mongo_context
    tenant = f"tenant-{target.value.lower()}-{uuid.uuid4().hex}"
    _create(client, tenant, history, current)
    _transition(client, tenant, TenantProductEntitlementState.ACTIVE, 0, history, current)
    terminal = _transition(client, tenant, target, 1, history, current)
    result = _resolve(client, tenant, history, current)
    assert terminal.lifecycle_state is target
    assert result.lifecycle_state is target
    assert result.available is False


def test_real_tenant_isolation_never_falls_back_to_foreign_legal_truth(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """Tenant B absence cannot consume tenant A's durable ACTIVE entitlement."""
    client, _, history, current = mongo_context
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"
    _create(client, tenant_a, history, current)
    _transition(
        client, tenant_a, TenantProductEntitlementState.ACTIVE, 0, history, current
    )
    result = _resolve(client, tenant_b, history, current)
    assert result.available is False
    assert result.lifecycle_state is None
    assert result.entitlement_id == _identity(tenant_b)
    assert result.entitlement_id != _identity(tenant_a)


def test_real_current_pointer_outranks_unpointed_later_history(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """An unpointed later history revision cannot replace explicit currentness."""
    client, _, history, current = mongo_context
    tenant = f"tenant-pointer-{uuid.uuid4().hex}"
    _create(client, tenant, history, current)
    active = _transition(
        client, tenant, TenantProductEntitlementState.ACTIVE, 0, history, current
    )
    suspended = active.transition(
        TenantProductEntitlementState.SUSPENDED,
        expected_revision=1,
        evidence_reference=f"d22b5-r7-unpointed:{tenant}",
        evidence_fingerprint=EVIDENCE_FINGERPRINT,
        occurred_at=NOW + timedelta(minutes=2),
    )
    with client.start_session() as session:
        with session.start_transaction():
            history.insert_one(registry._history_record(suspended), session=session)
    result = _resolve(client, tenant, history, current)
    assert history.count_documents({"tenant_id": tenant}) == 3
    assert result.lifecycle_state is TenantProductEntitlementState.ACTIVE
    assert result.available is True


def test_real_current_history_corruption_fails_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """Physical pointer/history corruption is fatal, never lawful absence."""
    client, _, history, current = mongo_context
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    _create(client, tenant, history, current)
    mutation = current.update_one(
        {"tenant_id": tenant, "entitlement_id": _identity(tenant)},
        {"$set": {"lifecycle_revision": 99}},
    )
    assert mutation.modified_count == 1
    with pytest.raises(projection.LegalProductAvailabilityProjectionError) as raised:
        _resolve(client, tenant, history, current)
    assert raised.value.code == "D22B5_REGISTRY_AUTHORITY_FAILURE"
    assert isinstance(
        raised.value.__cause__,
        registry.TenantProductEntitlementRegistryPersistedRecordInvalidError,
    )


def test_real_inactive_caller_session_fails_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    """A real session without an active transaction cannot establish truth."""
    client, _, history, current = mongo_context
    tenant = f"tenant-inactive-{uuid.uuid4().hex}"
    with client.start_session() as session:
        assert session.in_transaction is False
        with pytest.raises(projection.LegalProductAvailabilityProjectionError) as raised:
            projection.resolve_legal_product_availability(
                tenant,
                history,
                current,
                session=session,
            )
    assert raised.value.code == "D22B5_REGISTRY_AUTHORITY_FAILURE"
    assert isinstance(
        raised.value.__cause__,
        registry.TenantProductEntitlementRegistryTransactionRequiredError,
    )


# ARTIFACT: test_legal_product_availability_projection_real_mongo.py
# VERSION: v1.0.0-D22B5-R7-LEGAL-PRODUCT-AVAILABILITY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo read-projection certification only; no IAM, HTTP, admission, or commercial authority
# TENANT POSTURE: UUID-isolated exact-tenant evidence with explicit cross-tenant absence proof
# FAIL-CLOSED POSTURE: wrong runtime skips only pre-yield; pointer drift, corruption, and missing active transaction fail
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
