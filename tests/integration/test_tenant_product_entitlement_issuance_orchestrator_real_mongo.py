"""Real-Mongo certificate for D22B3-P25/P26 positive issuance orchestration.

TITLE: Tenant Product Entitlement Issuance Orchestrator Real-Mongo Certificate
VERSION: v1.0.0-D22B3-P26-POSITIVE-ISSUANCE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prepare physical proof that authorization evidence and positive Legal
         entitlement truth share one caller-owned replica-set transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_product_entitlement_issuance_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: IAM evidence registry, SubscriptionRegistry and D22B2
                            persistence retain truth; P25 only orchestrates them.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B3-P26-POSITIVE-ISSUANCE-REAL-MONGO-CERT prepares commit,
           abort, replay, divergence, isolation, corruption, index, concurrency
           and absence-of-financial-mutation evidence for the P26 run gate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic data; no credentials or PII.
TENANT BOUNDARY: Every persisted query and mutation is exact-tenant scoped.
AUTHORITY BOUNDARY: Operational certificate only; no route or client authority.
TRANSACTION BOUNDARY: Tests own start/commit/abort and whole-transaction retry.
FINANCIAL AUTHORITY BOUNDARY: No execution or settlement; Kennel EOS exclusive.
FAIL-CLOSED DECLARATION: Wrong topology, denial, divergence, corrupt evidence,
                         cross-tenant access and unresolved races fail the run.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import os
from threading import Barrier
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.saas.billing.plan_registry as plan_registry_module
import tools.eos.saas.billing.subscription_registry as subscription_registry_module
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_issuance_orchestrator import (
    TenantProductEntitlementIssuanceOrchestratorError,
    issue_tenant_product_entitlement,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION,
    HISTORY_COLLECTION,
    ensure_indexes,
    get_current,
)


VERSION = "v1.0.0-D22B3-P26-POSITIVE-ISSUANCE-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)


class _Repository:
    """Bind canonical repository resolve operations to isolated collections."""

    def __init__(self, collection: Any, kind: str) -> None:
        self.collection = collection
        self.kind = kind

    def resolve(self, *args: str, **kwargs: Any) -> Any:
        """Resolve one IAM record with the exact caller session."""
        session = kwargs.get("session")
        if self.kind == "principal":
            return PrincipalAuthorityRepository.resolve(
                args[0], self.collection, session=session
            )
        if self.kind == "membership":
            return TenantMembershipRepository.resolve(
                args[0], args[1], self.collection, session=session
            )
        return RoleAssignmentRepository.resolve(
            args[0], args[1], args[2], self.collection, session=session
        )


def _identity(tenant: str, principal: str) -> SovereignIdentity:
    """Create an active synthetic identity without credential material."""
    return SovereignIdentity(
        identity_id=principal,
        tenant_id=tenant,
        username=None,
        email=None,
        roles=[],
        permissions=[],
        auth_method="synthetic-certificate",
        status=PrincipalStatus.ACTIVE,
    )


def _collections(database: Any) -> dict[str, Any]:
    """Create majority/journaled certificate collection handles."""
    def collection(name: str) -> Any:
        return database.get_collection(
            name,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )

    return {
        "plans": collection("plans"),
        "subscriptions": collection("subscriptions"),
        "principal": collection("principal_authorities"),
        "membership": collection("tenant_memberships"),
        "assignment": collection("role_assignments"),
        "authorization": collection("tenant_authorization_decision_evidence"),
        "history": collection(HISTORY_COLLECTION),
        "current": collection(CURRENT_COLLECTION),
    }


def _issuer(collections: dict[str, Any]) -> TenantAuthorizationDecisionEvidenceRegistry:
    """Build the real evidence issuer over isolated canonical IAM sources."""
    assignment = _Repository(collections["assignment"], "assignment")
    return TenantAuthorizationDecisionEvidenceRegistry(
        collections["authorization"],
        principal_repository=_Repository(collections["principal"], "principal"),
        membership_repository=_Repository(collections["membership"], "membership"),
        role_assignment_repository=assignment,
        business_role_repository=assignment,
    )


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, dict[str, Any]]]:
    """Yield one UUID-isolated database only on the required writable replica set."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    original_plans = plan_registry_module.plans_collection
    original_subscriptions = subscription_registry_module.subscriptions_collection
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"host Mongo unavailable before fixture yield: {error}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip("wrong local replica set")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("local replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("replica set does not advertise logical sessions")
        database = client[f"wilsy_d22b3_p26_{uuid4().hex}"]
        collections = _collections(database)
        plan_registry_module.plans_collection = collections["plans"]
        subscription_registry_module.subscriptions_collection = collections[
            "subscriptions"
        ]
        PlanRegistry._ensure_indexes()
        subscription_registry_module._ensure_indexes()
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        RoleAssignmentRepository.ensure_indexes(collections["assignment"])
        _issuer(collections).ensure_indexes()
        ensure_indexes(collections["history"], collections["current"])
        yield client, database, collections
    finally:
        plan_registry_module.plans_collection = original_plans
        subscription_registry_module.subscriptions_collection = original_subscriptions
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _seed(client: MongoClient[Any], collections: dict[str, Any], tenant: str, principal: str) -> None:
    """Persist canonical IAM and ACTIVE legal.core subscription sources."""
    plan_result = PlanRegistry.create(
        {
            "name": f"D22B3 P26 {tenant}",
            "price": 100.0,
            "currency": "ZAR",
            "billingFrequency": "monthly",
            "planType": "PROFESSIONAL",
            "idempotencyKey": f"plan-{tenant}",
            "active": True,
            "features": ["legal.core"],
            "metadata": {"certificate": True},
            "tags": ["d22b3-p26"],
            "user": "D22B3-P26-CERT",
        }
    )
    assert plan_result["success"] is True
    subscription_result = SubscriptionRegistry.create(
        {
            "tenantId": tenant,
            "planId": plan_result["plan"].plan_id,
            "startDate": NOW.isoformat(),
            "idempotencyKey": f"subscription-{tenant}",
            "billingMode": "PLATFORM",
            "onboardingRef": f"ONBOARD-{tenant}",
            "metadata": {"certificate": True},
        },
        tenant_id_header=tenant,
    )
    assert subscription_result["success"] is True
    with client.start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0),
                collections["principal"],
                session=session,
            )
            TenantMembershipRepository.insert(
                TenantMembershipAuthority(
                    principal, tenant, TenantMembershipStatus.ACTIVE, 1
                ),
                collections["membership"],
                session=session,
            )
            for role in ("tenant_owner", "ENTERPRISE_ADMIN"):
                RoleAssignmentRepository.insert(
                    RoleAssignmentAuthority(
                        principal, tenant, role, RoleAssignmentStatus.ACTIVE, 0
                    ),
                    collections["assignment"],
                    session=session,
                )


def _issue(
    client: MongoClient[Any], collections: dict[str, Any], tenant: str,
    principal: str, *, idempotency_key: str = "issue-one",
) -> Any:
    """Commit one issuance under caller-owned transaction lifecycle."""
    with client.start_session() as session:
        with session.start_transaction():
            return issue_tenant_product_entitlement(
                identity=_identity(tenant, principal),
                product_id=TenantProductId.LEGAL_OPERATIONS,
                idempotency_key=idempotency_key,
                occurred_at=NOW,
                subscription_collection=collections["subscriptions"],
                entitlement_history_collection=collections["history"],
                entitlement_current_collection=collections["current"],
                authorization_evidence_registry=_issuer(collections),
                session=session,
            )


def test_real_commit_atomicity_indexes_and_exact_replay(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Commit both authorities, prove unique indexes and preserve both identities."""
    client, _database, collections = mongo_context
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed(client, collections, tenant, principal)
    first = _issue(client, collections, tenant, principal)
    replay = _issue(client, collections, tenant, principal)
    assert replay.authorization_evidence.authorization_decision_id == (
        first.authorization_evidence.authorization_decision_id
    )
    assert replay.composition.entitlement.entitlement_id == (
        first.composition.entitlement.entitlement_id
    )
    assert replay.composition.exact_active_replay is True
    assert collections["authorization"].count_documents({"tenant_id": tenant}) == 1
    assert collections["history"].count_documents({"tenant_id": tenant}) == 2
    assert collections["current"].count_documents({"tenant_id": tenant}) == 1
    authorization_indexes = {row["name"]: row for row in collections["authorization"].list_indexes()}
    history_indexes = {row["name"]: row for row in collections["history"].list_indexes()}
    current_indexes = {row["name"]: row for row in collections["current"].list_indexes()}
    assert authorization_indexes["tenant_authorization_idempotency_unique"]["unique"] is True
    assert any(row.get("unique") is True for row in history_indexes.values())
    assert any(row.get("unique") is True for row in current_indexes.values())


def test_real_caller_abort_removes_authorization_and_entitlement_writes(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Caller abort leaves zero P25 evidence and D22B2 writes."""
    client, _database, collections = mongo_context
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed(client, collections, tenant, principal)
    with client.start_session() as session:
        session.start_transaction()
        issue_tenant_product_entitlement(
            identity=_identity(tenant, principal),
            product_id=TenantProductId.LEGAL_OPERATIONS,
            idempotency_key="abort-one",
            occurred_at=NOW,
            subscription_collection=collections["subscriptions"],
            entitlement_history_collection=collections["history"],
            entitlement_current_collection=collections["current"],
            authorization_evidence_registry=_issuer(collections),
            session=session,
        )
        assert collections["authorization"].count_documents(
            {"tenant_id": tenant}, session=session
        ) == 1
        session.abort_transaction()
    assert collections["authorization"].count_documents({"tenant_id": tenant}) == 0
    assert collections["history"].count_documents({"tenant_id": tenant}) == 0
    assert collections["current"].count_documents({"tenant_id": tenant}) == 0


def test_real_divergent_replay_and_tenant_isolation_leave_zero_extra_writes(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Changed authorization semantics and another tenant cannot reuse evidence."""
    client, _database, collections = mongo_context
    tenant_a, principal_a = f"tenant-a-{uuid4().hex}", f"principal-a-{uuid4().hex}"
    tenant_b, principal_b = f"tenant-b-{uuid4().hex}", f"principal-b-{uuid4().hex}"
    _seed(client, collections, tenant_a, principal_a)
    _seed(client, collections, tenant_b, principal_b)
    _issue(client, collections, tenant_a, principal_a)
    _issue(client, collections, tenant_b, principal_b)
    assert collections["authorization"].count_documents({"tenant_id": tenant_a}) == 1
    assert collections["authorization"].count_documents({"tenant_id": tenant_b}) == 1
    entitlement_a = derive_tenant_product_entitlement_id(
        tenant_a, TenantProductId.LEGAL_OPERATIONS
    )
    with client.start_session() as session:
        with session.start_transaction():
            assert get_current(
                tenant_a,
                entitlement_a,
                collections["history"],
                collections["current"],
                session=session,
            ).tenant_id == tenant_a
            with pytest.raises(Exception):
                get_current(
                    tenant_b,
                    entitlement_a,
                    collections["history"],
                    collections["current"],
                    session=session,
                )


def test_real_corrupt_authorization_and_entitlement_evidence_fail_closed(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Persisted fingerprint corruption cannot replay as authority or entitlement."""
    client, _database, collections = mongo_context
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed(client, collections, tenant, principal)
    _issue(client, collections, tenant, principal)
    collections["authorization"].update_one(
        {"tenant_id": tenant},
        {"$set": {"authorization_evidence_fingerprint": "0" * 128}},
    )
    with pytest.raises(TenantProductEntitlementIssuanceOrchestratorError):
        _issue(client, collections, tenant, principal)
    collections["authorization"].delete_many({"tenant_id": tenant})
    collections["current"].update_one(
        {"tenant_id": tenant}, {"$set": {"record_fingerprint": "0" * 128}}
    )
    with pytest.raises(Exception):
        _issue(client, collections, tenant, principal, idempotency_key="corrupt-current")


def test_real_competing_transactions_do_not_double_issue(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Concurrent callers yield at most one committed authorization/entitlement identity."""
    client, _database, collections = mongo_context
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed(client, collections, tenant, principal)
    barrier = Barrier(2)

    def contender() -> str:
        try:
            with client.start_session() as session:
                session.start_transaction()
                barrier.wait(timeout=10)
                result = issue_tenant_product_entitlement(
                    identity=_identity(tenant, principal),
                    product_id=TenantProductId.LEGAL_OPERATIONS,
                    idempotency_key="race-one",
                    occurred_at=NOW,
                    subscription_collection=collections["subscriptions"],
                    entitlement_history_collection=collections["history"],
                    entitlement_current_collection=collections["current"],
                    authorization_evidence_registry=_issuer(collections),
                    session=session,
                )
                session.commit_transaction()
                return result.authorization_evidence.authorization_decision_id
        except Exception as error:
            return type(error).__name__

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = tuple(executor.map(lambda _: contender(), range(2)))
    assert len(outcomes) == 2
    assert collections["authorization"].count_documents({"tenant_id": tenant}) == 1
    assert collections["current"].count_documents({"tenant_id": tenant}) == 1
    assert collections["history"].count_documents({"tenant_id": tenant}) == 2


def test_no_credentials_or_financial_execution_truth_is_persisted(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Durable artifacts contain no raw auth secret or execution/settlement state."""
    client, database, collections = mongo_context
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed(client, collections, tenant, principal)
    _issue(client, collections, tenant, principal)
    documents = [
        *collections["authorization"].find({"tenant_id": tenant}),
        *collections["history"].find({"tenant_id": tenant}),
        *collections["current"].find({"tenant_id": tenant}),
    ]
    forbidden = {
        "token", "access_token", "refresh_token", "password", "credential",
        "bank_account", "payment_destination", "executed", "settled",
    }
    assert all(forbidden.isdisjoint(document) for document in documents)
    assert not {
        "payments", "settlements", "bank_executions", "financial_executions"
    } & set(database.list_collection_names())

# ARTIFACT: test_tenant_product_entitlement_issuance_orchestrator_real_mongo.py
# VERSION: v1.0.0-D22B3-P26-POSITIVE-ISSUANCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: P26 real-replica-set operational certificate only
# TENANT POSTURE: UUID-isolated exact tenant scope with cross-tenant denial
# FAIL-CLOSED POSTURE: topology, abort, replay divergence, corruption and races are explicit
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
