"""Real-Mongo certificate for subscription/Legal entitlement composition.

TITLE: Subscription Active Entitlement Composition Service Real-Mongo Certificate
VERSION: v1.0.2-D22B3-P43-REAL-MONGO-SERVICE-CERTIFICATE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies that the P42 service composes canonical subscription
         mutation, authorization evidence and Legal Operations entitlement
         truth inside one service-owned real Mongo transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_subscription_active_entitlement_composition_service_real_mongo.py
COLLABORATION / OWNERSHIP: P42 owns transaction lifecycle; SubscriptionRegistry,
                            IAM evidence and D22B2 entitlement registries retain
                            their distinct canonical truth boundaries.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.2-D22B3-P43-REAL-MONGO-SERVICE-CERTIFICATE corrects the positive
           current-pointer/domain coordinate to canonical lifecycle_revision.
           v1.0.1-D22B3-P43-REAL-MONGO-SERVICE-CERTIFICATE repairs current-pointer
           revision correlation and permits only the typed bounded-retry loser
           while requiring one successful contender and one durable lineage.
           v1.0.0-D22B3-P43-REAL-MONGO-SERVICE-CERTIFICATE establishes isolated
           replica-set proofs for commit, replay, abort, non-Legal success,
           resume, reactivate, isolation, competition and corruption rejection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic records only; no credentials,
                             personal data or external network dependency.
TENANT BOUNDARY: Every command, authority fixture and durable assertion is
                 exact-tenant and exact-principal scoped.
AUTHORITY BOUNDARY: Operational test evidence only; product remains internally
                    fixed to LEGAL_OPERATIONS and no IAM grant is fabricated.
TRANSACTION BOUNDARY: The real P42 service alone starts, commits, aborts and
                      retries; registries, issuer and composer remain participants.
FINANCIAL AUTHORITY BOUNDARY: No payment, execution or settlement truth;
                              Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Wrong topology, unavailable authority, partial writes,
                         cross-tenant access, duplicate lineage and corrupt
                         durable evidence fail the certificate.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import inspect
import os
from pathlib import Path
from threading import Barrier
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.kernel.db as kernel_db
import tools.eos.saas.billing.plan_registry as plan_registry_module
import tools.eos.saas.billing.subscription_active_entitlement_composition_service as service_module
import tools.eos.saas.billing.subscription_registry as subscription_registry_module
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    COLLECTION as PRINCIPAL_COLLECTION,
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    COLLECTION as ROLE_ASSIGNMENT_COLLECTION,
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as AUTHORIZATION_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    COLLECTION as MEMBERSHIP_COLLECTION,
    TenantMembershipRepository,
)
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_active_entitlement_composition_service import (
    SubscriptionActiveEntitlementCompositionIssuanceError,
    SubscriptionActiveEntitlementCompositionLifecycleError,
    SubscriptionActiveEntitlementCompositionRetryExhaustedError,
    SubscriptionActiveEntitlementCompositionService,
)
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.domain.subscription import SubscriptionStatus
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION,
    HISTORY_COLLECTION,
    ensure_indexes as ensure_entitlement_indexes,
    get_current as get_current_entitlement,
)


VERSION = "v1.0.2-D22B3-P43-REAL-MONGO-SERVICE-CERTIFICATE"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)


def _majority(database: Any, name: str) -> Any:
    """Return one canonical collection with majority/journal durability."""
    return database.get_collection(
        name,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )


def _collections(database: Any) -> dict[str, Any]:
    """Bind every canonical participant to its production collection name."""
    names = {
        "plans": "plans",
        "subscriptions": service_module.SUBSCRIPTION_COLLECTION,
        "principal": PRINCIPAL_COLLECTION,
        "membership": MEMBERSHIP_COLLECTION,
        "assignment": ROLE_ASSIGNMENT_COLLECTION,
        "authorization": AUTHORIZATION_COLLECTION,
        "history": HISTORY_COLLECTION,
        "current": CURRENT_COLLECTION,
    }
    return {key: _majority(database, name) for key, name in names.items()}


@pytest.fixture
def mongo_context(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[MongoClient[Any], Any, dict[str, Any]]]:
    """Yield a UUID database on the sanctioned writable replica set only."""
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
            pytest.fail(f"sanctioned Mongo unavailable: {type(error).__name__}")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        database = client[f"wilsy_d22b3_p43_{uuid4().hex}"]
        collections = _collections(database)

        monkeypatch.setattr(plan_registry_module, "plans_collection", collections["plans"])
        monkeypatch.setattr(
            subscription_registry_module,
            "subscriptions_collection",
            collections["subscriptions"],
        )
        monkeypatch.setattr(kernel_db, "get_client", lambda: client)
        monkeypatch.setattr(kernel_db, "get_database", lambda: database)
        monkeypatch.setattr(service_module, "get_client", lambda: client)
        monkeypatch.setattr(service_module, "get_database", lambda: database)

        PlanRegistry._ensure_indexes()
        subscription_registry_module._ensure_indexes()
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        RoleAssignmentRepository.ensure_indexes(collections["assignment"])
        service_module._authorization_registry(database).ensure_indexes()
        ensure_entitlement_indexes(collections["history"], collections["current"])
        yield client, database, collections
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _identity(tenant_id: str, principal_id: str) -> SovereignIdentity:
    """Create a synthetic active identity containing no credential material."""
    return SovereignIdentity(
        identity_id=principal_id,
        tenant_id=tenant_id,
        username=None,
        email=None,
        roles=[],
        permissions=[],
        auth_method="p43-real-mongo-certificate",
        status=PrincipalStatus.ACTIVE,
    )


def _seed_authority(
    collections: dict[str, Any], tenant_id: str, principal_id: str
) -> None:
    """Persist the exact canonical authority prerequisite used by P25."""
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0),
        collections["principal"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal_id, tenant_id, TenantMembershipStatus.ACTIVE, 1
        ),
        collections["membership"],
    )
    for role_id in ("tenant_owner", "ENTERPRISE_ADMIN"):
        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                principal_id,
                tenant_id,
                role_id,
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            collections["assignment"],
        )


def _plan(tenant_id: str, features: tuple[str, ...]) -> Any:
    """Create canonical immutable catalogue truth for one certificate tenant."""
    result = PlanRegistry.create(
        {
            "name": f"P43 {tenant_id}",
            "price": 100.0,
            "currency": "ZAR",
            "billingFrequency": "monthly",
            "planType": "PROFESSIONAL",
            "idempotencyKey": f"plan-{tenant_id}",
            "active": True,
            "features": list(features),
            "metadata": {"certificate": "D22B3-P43"},
            "tags": ["d22b3-p43"],
            "user": "D22B3-P43-CERT",
        }
    )
    assert result["success"] is True
    return result["plan"]


def _command(tenant_id: str, plan_id: str, key: str) -> dict[str, Any]:
    """Build a selection-only commercial command with no product authority."""
    command = {
        "tenantId": tenant_id,
        "planId": plan_id,
        "startDate": NOW.isoformat(),
        "idempotencyKey": key,
        "billingMode": "PLATFORM",
        "onboardingRef": f"ONBOARD-{tenant_id}",
        "metadata": {"certificate": "D22B3-P43"},
    }
    assert "product" not in command and "product_id" not in command
    return command


def _coordinates(collections: dict[str, Any], tenant_id: str) -> tuple[int, int, int, int]:
    """Return exact durable lineage counts for one tenant."""
    return (
        collections["subscriptions"].count_documents({"tenant_id": tenant_id}),
        collections["authorization"].count_documents({"tenant_id": tenant_id}),
        collections["history"].count_documents({"tenant_id": tenant_id}),
        collections["current"].count_documents({"tenant_id": tenant_id}),
    )


def _assert_positive(
    result: Any,
    collections: dict[str, Any],
    tenant_id: str,
    principal_id: str,
) -> None:
    """Assert exact cross-authority correlation without inferring extra grants."""
    assert result.subscription.status is SubscriptionStatus.ACTIVE
    assert result.legal_entitlement_applicable is True
    assert result.entitlement_issuance_result is not None
    issuance = result.entitlement_issuance_result
    evidence = issuance.authorization_evidence
    entitlement = issuance.composition.entitlement
    assert evidence.tenant_id == tenant_id
    assert evidence.principal_id == principal_id
    assert entitlement.tenant_id == tenant_id
    assert entitlement.product_id is TenantProductId.LEGAL_OPERATIONS
    assert _coordinates(collections, tenant_id) == (1, 1, 2, 1)
    current = collections["current"].find_one({"tenant_id": tenant_id})
    assert current is not None
    assert current["entitlement_id"] == entitlement.entitlement_id
    assert current["lifecycle_revision"] == entitlement.lifecycle_revision


def test_runtime_indexes_positive_create_and_exact_replay(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Prove canonical bindings, one real commit and lineage-stable replay."""
    _client, database, collections = mongo_context
    tenant_id, principal_id = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_authority(collections, tenant_id, principal_id)
    plan = _plan(tenant_id, ("legal.core",))
    command = _command(tenant_id, plan.plan_id, f"create-{tenant_id}")

    first = SubscriptionActiveEntitlementCompositionService.create(
        command, _identity(tenant_id, principal_id)
    )
    _assert_positive(first, collections, tenant_id, principal_id)
    assert first.entitlement_issuance_result is not None
    first_issuance = first.entitlement_issuance_result
    first_ids = (
        first.subscription.subscription_id,
        first_issuance.authorization_evidence.authorization_decision_id,
        first_issuance.composition.entitlement.entitlement_id,
    )
    replay = SubscriptionActiveEntitlementCompositionService.create(
        command, _identity(tenant_id, principal_id)
    )
    assert replay.entitlement_issuance_result is not None
    replay_issuance = replay.entitlement_issuance_result
    replay_ids = (
        replay.subscription.subscription_id,
        replay_issuance.authorization_evidence.authorization_decision_id,
        replay_issuance.composition.entitlement.entitlement_id,
    )
    assert replay_ids == first_ids
    _assert_positive(replay, collections, tenant_id, principal_id)
    assert set(database.list_collection_names()).issuperset(
        {
            "subscriptions",
            "tenant_authorization_decision_evidence",
            "tenant_product_entitlement_history",
            "tenant_product_entitlement_current",
        }
    )
    assert any(row.get("unique") for row in collections["subscriptions"].list_indexes())
    assert any(row.get("unique") for row in collections["authorization"].list_indexes())
    assert any(row.get("unique") for row in collections["history"].list_indexes())
    assert any(row.get("unique") for row in collections["current"].list_indexes())


def test_downstream_failure_after_commercial_write_aborts_everything(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Force failure after the transactional commercial insert and prove zero write."""
    _client, _database, collections = mongo_context
    tenant_id, principal_id = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_authority(collections, tenant_id, principal_id)
    plan = _plan(tenant_id, ("legal.core",))
    observed = {"commercial_visible_in_transaction": False}

    def fail_after_commercial(**kwargs: Any) -> Any:
        session = kwargs["session"]
        observed["commercial_visible_in_transaction"] = (
            collections["subscriptions"].count_documents(
                {"tenant_id": tenant_id}, session=session
            )
            == 1
        )
        raise service_module.TenantProductEntitlementIssuanceOrchestratorError(
            "P43_FORCED_POST_COMMERCIAL_FAILURE"
        )

    monkeypatch.setattr(service_module, "issue_tenant_product_entitlement", fail_after_commercial)
    with pytest.raises(SubscriptionActiveEntitlementCompositionIssuanceError):
        SubscriptionActiveEntitlementCompositionService.create(
            _command(tenant_id, plan.plan_id, f"abort-{tenant_id}"),
            _identity(tenant_id, principal_id),
        )
    assert observed["commercial_visible_in_transaction"] is True
    assert _coordinates(collections, tenant_id) == (0, 0, 0, 0)


def test_non_legal_plan_commits_only_commercial_truth(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """An ACTIVE plan lacking exact legal.core emits no P42 issuance truth."""
    _client, _database, collections = mongo_context
    tenant_id, principal_id = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_authority(collections, tenant_id, principal_id)
    plan = _plan(tenant_id, ("crm.core",))
    result = SubscriptionActiveEntitlementCompositionService.create(
        _command(tenant_id, plan.plan_id, f"non-legal-{tenant_id}"),
        _identity(tenant_id, principal_id),
    )
    assert result.subscription.status is SubscriptionStatus.ACTIVE
    assert result.legal_entitlement_applicable is False
    assert result.entitlement_issuance_result is None
    assert _coordinates(collections, tenant_id) == (1, 0, 0, 0)


@pytest.mark.parametrize("operation", ("resume", "reactivate"))
def test_resume_and_reactivate_commit_commercial_and_entitlement_atomically(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
    operation: str,
) -> None:
    """Canonical PAUSED/CANCELLED truth becomes ACTIVE with correlated issuance."""
    _client, _database, collections = mongo_context
    tenant_id = f"tenant-{operation}-{uuid4().hex}"
    principal_id = f"principal-{operation}-{uuid4().hex}"
    _seed_authority(collections, tenant_id, principal_id)
    plan = _plan(tenant_id, ("legal.core",))
    created = SubscriptionRegistry.create(
        _command(tenant_id, plan.plan_id, f"setup-{operation}-{tenant_id}"),
        tenant_id_header=tenant_id,
    )
    assert created["success"] is True
    subscription_id = created["subscription"].subscription_id
    if operation == "resume":
        prepared = SubscriptionRegistry.pause(
            subscription_id,
            tenant_id_header=tenant_id,
            pause_reason="P43 canonical setup",
        )
        assert prepared["subscription"].status is SubscriptionStatus.PAUSED
        result = SubscriptionActiveEntitlementCompositionService.resume(
            subscription_id,
            {"certificate": "D22B3-P43"},
            _identity(tenant_id, principal_id),
        )
    else:
        prepared = SubscriptionRegistry.cancel(
            subscription_id,
            tenant_id_header=tenant_id,
            cancel_reason="P43 canonical setup",
            cancel_at_period_end=False,
        )
        assert prepared["subscription"].status is SubscriptionStatus.CANCELLED
        result = SubscriptionActiveEntitlementCompositionService.reactivate(
            subscription_id,
            {"certificate": "D22B3-P43"},
            _identity(tenant_id, principal_id),
        )
    _assert_positive(result, collections, tenant_id, principal_id)
    assert result.subscription.audit_trail[-1].action.value == operation


def test_tenant_isolation_rejects_foreign_lifecycle_access(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """A second tenant cannot read, resume, correlate or mutate the first tenant."""
    _client, _database, collections = mongo_context
    tenant_a, tenant_b = f"tenant-a-{uuid4().hex}", f"tenant-b-{uuid4().hex}"
    principal_a, principal_b = f"principal-a-{uuid4().hex}", f"principal-b-{uuid4().hex}"
    for tenant_id, principal_id in ((tenant_a, principal_a), (tenant_b, principal_b)):
        _seed_authority(collections, tenant_id, principal_id)
    plan_a = _plan(tenant_a, ("legal.core",))
    result_a = SubscriptionActiveEntitlementCompositionService.create(
        _command(tenant_a, plan_a.plan_id, f"create-{tenant_a}"),
        _identity(tenant_a, principal_a),
    )
    before_a = _coordinates(collections, tenant_a)
    with pytest.raises(SubscriptionActiveEntitlementCompositionLifecycleError):
        SubscriptionActiveEntitlementCompositionService.resume(
            result_a.subscription.subscription_id,
            {"certificate": "foreign-attempt"},
            _identity(tenant_b, principal_b),
        )
    assert _coordinates(collections, tenant_a) == before_a
    assert _coordinates(collections, tenant_b) == (0, 0, 0, 0)


def test_competing_exact_create_has_one_lineage_and_valid_current_pointer(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Competing exact commercial commands converge without double lineage."""
    client, _database, collections = mongo_context
    tenant_id, principal_id = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_authority(collections, tenant_id, principal_id)
    plan = _plan(tenant_id, ("legal.core",))
    command = _command(tenant_id, plan.plan_id, f"race-{tenant_id}")
    barrier = Barrier(2)

    def contender() -> tuple[str, Any]:
        barrier.wait(timeout=10)
        try:
            return (
                "SUCCESS",
                SubscriptionActiveEntitlementCompositionService.create(
                    command, _identity(tenant_id, principal_id)
                ),
            )
        except SubscriptionActiveEntitlementCompositionRetryExhaustedError as error:
            return ("RETRY_EXHAUSTED", error)

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = tuple(executor.map(lambda _index: contender(), range(2)))
    assert len(outcomes) == 2
    assert all(tag in {"SUCCESS", "RETRY_EXHAUSTED"} for tag, _value in outcomes)
    successes = tuple(value for tag, value in outcomes if tag == "SUCCESS")
    assert len(successes) >= 1
    _assert_positive(successes[0], collections, tenant_id, principal_id)
    winning_issuance = successes[0].entitlement_issuance_result
    assert winning_issuance is not None
    winning_entitlement = winning_issuance.composition.entitlement
    with client.start_session() as session:
        with session.start_transaction():
            durable_entitlement = get_current_entitlement(
                tenant_id,
                winning_entitlement.entitlement_id,
                collections["history"],
                collections["current"],
                session=session,
            )
    assert durable_entitlement.to_dict() == winning_entitlement.to_dict()

    if len(successes) == 2:
        correlated_ids = []
        for result in successes:
            assert result.entitlement_issuance_result is not None
            issuance = result.entitlement_issuance_result
            correlated_ids.append(
                (
                    result.subscription.subscription_id,
                    issuance.authorization_evidence.authorization_decision_id,
                    issuance.composition.entitlement.entitlement_id,
                )
            )
        assert correlated_ids[0] == correlated_ids[1]


def test_corrupt_authorization_evidence_replay_fails_closed(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Corrupt durable authority evidence is rejected, not replaced or laundered."""
    _client, _database, collections = mongo_context
    tenant_id, principal_id = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_authority(collections, tenant_id, principal_id)
    plan = _plan(tenant_id, ("legal.core",))
    command = _command(tenant_id, plan.plan_id, f"corrupt-{tenant_id}")
    SubscriptionActiveEntitlementCompositionService.create(
        command, _identity(tenant_id, principal_id)
    )
    before = _coordinates(collections, tenant_id)
    update = collections["authorization"].update_one(
        {"tenant_id": tenant_id},
        {"$set": {"authorization_evidence_fingerprint": "0" * 128}},
    )
    assert update.modified_count == 1
    with pytest.raises(SubscriptionActiveEntitlementCompositionIssuanceError):
        SubscriptionActiveEntitlementCompositionService.create(
            command, _identity(tenant_id, principal_id)
        )
    assert _coordinates(collections, tenant_id) == before
    assert collections["authorization"].find_one({"tenant_id": tenant_id})[
        "authorization_evidence_fingerprint"
    ] == "0" * 128


def test_transaction_ownership_and_authority_exclusions_are_exact() -> None:
    """Prove P42 owns lifecycle and creates no excluded authority surface."""
    service_source = Path(service_module.__file__).read_text(encoding="utf-8")
    assert "session.start_transaction()" in service_source
    assert "session.commit_transaction()" in service_source
    assert "_abort_if_active(session)" in service_source
    assert "TenantProductId.LEGAL_OPERATIONS" in service_source
    for excluded in ("TenantProductId.CRM", "TenantProductId.BILLING", "TenantProductId.HR"):
        assert excluded not in service_source
    participant_sources = (
        inspect.getsource(SubscriptionRegistry.resume),
        inspect.getsource(service_module.issue_tenant_product_entitlement),
    )
    for source in participant_sources:
        for token in ("start_transaction(", "commit_transaction(", "abort_transaction("):
            assert token not in source
    lowered = service_source.lower()
    assert "no payment execution" in lowered
    assert "settlement authority" in lowered


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_subscription_active_entitlement_composition_service_real_mongo.py
# VERSION: v1.0.2-D22B3-P43-REAL-MONGO-SERVICE-CERTIFICATE
# AUTHORITY BOUNDARY: operational real-Mongo evidence only; no route or product authority
# TENANT POSTURE: UUID-isolated exact-tenant and exact-principal certification
# FAIL-CLOSED POSTURE: topology, partial write, isolation, race and corruption failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
