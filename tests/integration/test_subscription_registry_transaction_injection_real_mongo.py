"""Real-Mongo certificate for bounded SubscriptionRegistry transaction injection.

TITLE: SubscriptionRegistry Transaction Injection Real-Mongo Certificate
VERSION: v1.0.0-D22B3-P34-SUBSCRIPTION-TRANSACTION-INJECTION-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove create, replay, resume, reactivate and optimistic CAS participate
         in caller-owned transactions against an isolated writable replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_subscription_registry_transaction_injection_real_mongo.py
COLLABORATION / OWNERSHIP: SubscriptionRegistry owns commercial lifecycle truth;
                            this certificate alone owns test transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B3-P34-SUBSCRIPTION-TRANSACTION-INJECTION-REAL-MONGO-CERT
           establishes physical abort, commit, replay and stale-CAS evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic data; no credentials or PII.
TENANT BOUNDARY: Every operation uses one explicit synthetic tenant scope.
AUTHORITY BOUNDARY: Subscription persistence certification only.
TRANSACTION BOUNDARY: Tests start, commit and abort; registry only propagates.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
FAIL-CLOSED DECLARATION: Wrong topology, lost session, stale revision or durable
                         state mismatch fails certification.
"""
from __future__ import annotations

import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.saas.billing.plan_registry as plan_registry_module
import tools.eos.saas.billing.subscription_registry as registry
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_registry import (
    SubscriptionRegistry,
    SubscriptionRegistryError,
)
from tools.eos.saas.domain.subscription import SubscriptionStatus


VERSION = "v1.0.0-D22B3-P34-SUBSCRIPTION-TRANSACTION-INJECTION-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[MongoClient[Any], Collection[dict[str, Any]], Collection[dict[str, Any]]]
]:
    """Yield majority/journaled collections from one disposable replica-set DB."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    original_plans = plan_registry_module.plans_collection
    original_subscriptions = registry.subscriptions_collection
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        database = client[f"wilsy_d22b3_p34_{uuid4().hex}"]
        plans = database.get_collection(
            "plans",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        subscriptions = database.get_collection(
            "subscriptions",
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        plan_registry_module.plans_collection = plans
        registry.subscriptions_collection = subscriptions
        PlanRegistry._ensure_indexes()
        registry._ensure_indexes(subscriptions)
        yield client, plans, subscriptions
    finally:
        plan_registry_module.plans_collection = original_plans
        registry.subscriptions_collection = original_subscriptions
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _plan(key: str) -> str:
    """Persist one canonical Legal Operations commercial plan."""
    result = PlanRegistry.create(
        {
            "name": f"P34 Plan {key}",
            "price": 100.0,
            "currency": "ZAR",
            "billingFrequency": "monthly",
            "planType": "PROFESSIONAL",
            "idempotencyKey": f"plan-{key}",
            "active": True,
            "features": ["legal.core"],
            "metadata": {"certificate": True},
            "tags": ["d22b3-p34"],
            "user": "D22B3-P34-CERT",
        }
    )
    assert result["success"] is True
    return result["plan"].plan_id


def _payload(
    tenant: str, plan_id: str, key: str, *, status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
) -> dict[str, Any]:
    """Return one canonical synthetic subscription command."""
    return {
        "tenantId": tenant,
        "planId": plan_id,
        "startDate": "2026-10-09T12:00:00+00:00",
        "idempotencyKey": key,
        "billingMode": "PLATFORM",
        "status": status.value,
        "metadata": {"certificate": True},
    }


def _committed_create(
    client: MongoClient[Any], collection: Collection[dict[str, Any]], payload: dict[str, Any],
) -> dict[str, Any]:
    """Create and commit through an explicitly caller-owned transaction."""
    tenant = str(payload["tenantId"])
    with client.start_session() as session:
        session.start_transaction()
        result = SubscriptionRegistry.create(
            payload, tenant, collection=collection, session=session
        )
        session.commit_transaction()
    assert result["success"] is True
    return result


def test_create_abort_and_registry_does_not_end_caller_transaction(
    mongo_context: tuple[MongoClient[Any], Collection[dict[str, Any]], Collection[dict[str, Any]]],
) -> None:
    """Create is visible in-session, registry leaves transaction active, abort removes it."""
    client, _plans, subscriptions = mongo_context
    tenant, key = f"tenant-{uuid4().hex}", f"create-abort-{uuid4().hex}"
    payload = _payload(tenant, _plan(uuid4().hex), key)
    with client.start_session() as session:
        session.start_transaction()
        result = SubscriptionRegistry.create(
            payload, tenant, collection=subscriptions, session=session
        )
        assert result["success"] is True
        assert session.in_transaction is True
        assert subscriptions.count_documents(
            {"tenant_id": tenant}, session=session
        ) == 1
        session.abort_transaction()
    assert subscriptions.count_documents({"tenant_id": tenant}) == 0


def test_create_commit_persists_and_registry_does_not_commit_early(
    mongo_context: tuple[MongoClient[Any], Collection[dict[str, Any]], Collection[dict[str, Any]]],
) -> None:
    """Only caller commit makes injected create durable."""
    client, _plans, subscriptions = mongo_context
    tenant, key = f"tenant-{uuid4().hex}", f"create-commit-{uuid4().hex}"
    payload = _payload(tenant, _plan(uuid4().hex), key)
    with client.start_session() as session:
        session.start_transaction()
        result = SubscriptionRegistry.create(
            payload, tenant, collection=subscriptions, session=session
        )
        assert result["success"] is True and session.in_transaction is True
        session.commit_transaction()
    assert subscriptions.count_documents({"tenant_id": tenant}) == 1


def test_create_exact_replay_inside_new_caller_transaction(
    mongo_context: tuple[MongoClient[Any], Collection[dict[str, Any]], Collection[dict[str, Any]]],
) -> None:
    """Exact command replay returns one identity and creates no duplicate row."""
    client, _plans, subscriptions = mongo_context
    tenant, key = f"tenant-{uuid4().hex}", f"replay-{uuid4().hex}"
    payload = _payload(tenant, _plan(uuid4().hex), key)
    first = _committed_create(client, subscriptions, payload)
    with client.start_session() as session:
        session.start_transaction()
        replay = SubscriptionRegistry.create(
            payload, tenant, collection=subscriptions, session=session
        )
        assert session.in_transaction is True
        session.commit_transaction()
    assert replay["success"] is True and replay["replayed"] is True
    assert replay["subscription"].subscription_id == first["subscription"].subscription_id
    assert subscriptions.count_documents({"tenant_id": tenant}) == 1


@pytest.mark.parametrize("commit", [False, True], ids=["abort", "commit"])
def test_resume_obeys_caller_transaction_outcome(
    mongo_context: tuple[MongoClient[Any], Collection[dict[str, Any]], Collection[dict[str, Any]]],
    commit: bool,
) -> None:
    """PAUSED to ACTIVE is visible in-session and durable only after caller commit."""
    client, _plans, subscriptions = mongo_context
    tenant = f"tenant-{uuid4().hex}"
    created = _committed_create(
        client,
        subscriptions,
        _payload(tenant, _plan(uuid4().hex), f"resume-{uuid4().hex}", status=SubscriptionStatus.PAUSED),
    )
    subscription_id = created["subscription"].subscription_id
    with client.start_session() as session:
        session.start_transaction()
        result = SubscriptionRegistry.resume(
            subscription_id, tenant, collection=subscriptions, session=session
        )
        assert result["success"] is True
        assert result["subscription"].status is SubscriptionStatus.ACTIVE
        assert session.in_transaction is True
        if commit:
            session.commit_transaction()
        else:
            session.abort_transaction()
    durable = registry._find_document(
        subscription_id, tenant, collection=subscriptions
    )
    assert durable is not None
    expected = SubscriptionStatus.ACTIVE if commit else SubscriptionStatus.PAUSED
    assert registry._hydrate(durable).status is expected


@pytest.mark.parametrize("commit", [False, True], ids=["abort", "commit"])
def test_reactivate_obeys_caller_transaction_outcome(
    mongo_context: tuple[MongoClient[Any], Collection[dict[str, Any]], Collection[dict[str, Any]]],
    commit: bool,
) -> None:
    """CANCELLED to ACTIVE is durable only after caller-owned commit."""
    client, _plans, subscriptions = mongo_context
    tenant = f"tenant-{uuid4().hex}"
    created = _committed_create(
        client,
        subscriptions,
        _payload(tenant, _plan(uuid4().hex), f"reactivate-{uuid4().hex}", status=SubscriptionStatus.CANCELLED),
    )
    subscription_id = created["subscription"].subscription_id
    with client.start_session() as session:
        session.start_transaction()
        result = SubscriptionRegistry.reactivate(
            subscription_id, tenant, collection=subscriptions, session=session
        )
        assert result["success"] is True
        assert result["subscription"].status is SubscriptionStatus.ACTIVE
        assert session.in_transaction is True
        if commit:
            session.commit_transaction()
        else:
            session.abort_transaction()
    durable = registry._find_document(
        subscription_id, tenant, collection=subscriptions
    )
    assert durable is not None
    expected = SubscriptionStatus.ACTIVE if commit else SubscriptionStatus.CANCELLED
    assert registry._hydrate(durable).status is expected


def test_stale_optimistic_cas_remains_fail_closed_with_injected_dependencies(
    mongo_context: tuple[MongoClient[Any], Collection[dict[str, Any]], Collection[dict[str, Any]]],
) -> None:
    """A stale prior revision cannot replace newer durable subscription truth."""
    client, _plans, subscriptions = mongo_context
    tenant = f"tenant-{uuid4().hex}"
    created = _committed_create(
        client,
        subscriptions,
        _payload(tenant, _plan(uuid4().hex), f"cas-{uuid4().hex}"),
    )
    subscription_id = created["subscription"].subscription_id
    stale = registry._find_document(
        subscription_id, tenant, collection=subscriptions
    )
    assert stale is not None and stale["_registry_revision"] == 1
    subscriptions.update_one(
        {"tenant_id": tenant, "subscription_id": subscription_id},
        {"$set": {"_registry_revision": 2}},
    )
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(
            SubscriptionRegistryError,
            match="SUBSCRIPTION_REGISTRY_CONCURRENT_MODIFICATION",
        ):
            registry._replace_document(
                stale,
                registry._hydrate(stale),
                collection=subscriptions,
                session=session,
            )
        assert session.in_transaction is True
        session.abort_transaction()
    durable = subscriptions.find_one(
        {"tenant_id": tenant, "subscription_id": subscription_id}
    )
    assert durable is not None and durable["_registry_revision"] == 2


def test_real_certificate_contains_no_registry_transaction_ownership(
    mongo_context: tuple[MongoClient[Any], Collection[dict[str, Any]], Collection[dict[str, Any]]],
) -> None:
    """The registry source contains none of the prohibited lifecycle calls."""
    _client, _plans, _subscriptions = mongo_context
    source = open(registry.__file__, encoding="utf-8").read()
    for token in (
        "start_session(", "start_transaction(", "commit_transaction(",
        "abort_transaction(", "with_transaction(",
    ):
        assert token not in source

# ARTIFACT: test_subscription_registry_transaction_injection_real_mongo.py
# VERSION: v1.0.0-D22B3-P34-SUBSCRIPTION-TRANSACTION-INJECTION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated real-Mongo transaction participation certificate
# TENANT POSTURE: exact synthetic tenant scope on every operation
# FAIL-CLOSED POSTURE: abort, stale CAS and topology violations fail certification
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
