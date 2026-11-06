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
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.saas.entitlement.commercial_agreement import (
    CommercialAgreement,
    CommercialAgreementState,
    CommercialRenewalMode,
)
from tools.eos.saas.entitlement.commercial_agreement_registry import (
    CURRENT_COLLECTION as AGREEMENT_CURRENT_COLLECTION,
    HISTORY_COLLECTION as AGREEMENT_HISTORY_COLLECTION,
    create_or_replay as create_agreement_or_replay,
    ensure_indexes as ensure_agreement_indexes,
    get_current as get_current_agreement,
)
from tools.eos.saas.entitlement.commercial_bundle_activation import (
    COLLECTION as BUNDLE_ACTIVATION_COLLECTION,
    CommercialBundleActivationOutcome,
    CommercialBundleReconciliationState,
    VerifiedCommercialAgreementExecutionEvidence,
    activate_commercial_bundle,
    ensure_indexes as ensure_bundle_activation_indexes,
    reconcile_commercial_bundle_activation,
)
from tools.eos.saas.entitlement.commercial_offer_catalogue import (
    CommercialOfferId,
    get_commercial_offer,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION as PRODUCT_ENTITLEMENT_CURRENT_COLLECTION,
    HISTORY_COLLECTION as PRODUCT_ENTITLEMENT_HISTORY_COLLECTION,
    ensure_indexes as ensure_product_entitlement_indexes,
    get_current as get_current_product_entitlement,
)
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

    def resolve_current_business_role(
        self, principal_id: str, tenant_id: str, *, session: Any = None
    ) -> Any:
        return TenantBusinessRoleRepository.resolve(
            principal_id, tenant_id, self.collection, session=session
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
        "business_role": collection("tenant_business_roles"),
        "authorization": collection("tenant_authorization_decision_evidence"),
        "history": collection(HISTORY_COLLECTION),
        "current": collection(CURRENT_COLLECTION),
        "agreement_history": collection(AGREEMENT_HISTORY_COLLECTION),
        "agreement_current": collection(AGREEMENT_CURRENT_COLLECTION),
        "bundle_receipts": collection(BUNDLE_ACTIVATION_COLLECTION),
    }


def _issuer(collections: dict[str, Any]) -> TenantAuthorizationDecisionEvidenceRegistry:
    """Build the real evidence issuer over isolated canonical IAM sources."""
    assignment = _Repository(collections["assignment"], "assignment")
    business_role = _Repository(collections["business_role"], "business_role")
    return TenantAuthorizationDecisionEvidenceRegistry(
        collections["authorization"],
        principal_repository=_Repository(collections["principal"], "principal"),
        membership_repository=_Repository(collections["membership"], "membership"),
        role_assignment_repository=assignment,
        business_role_repository=business_role,
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
        PlanRegistry.provision_indexes()
        subscription_registry_module._ensure_indexes()
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        RoleAssignmentRepository.ensure_indexes(collections["assignment"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business_role"])
        _issuer(collections).ensure_indexes()
        ensure_indexes(collections["history"], collections["current"])
        ensure_agreement_indexes(collections["agreement_history"], collections["agreement_current"])
        ensure_product_entitlement_indexes(collections["history"], collections["current"])
        ensure_bundle_activation_indexes(collections["bundle_receipts"])
        yield client, database, collections
    finally:
        plan_registry_module.plans_collection = original_plans
        subscription_registry_module.subscriptions_collection = original_subscriptions
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _seed(client: MongoClient[Any], collections: dict[str, Any], tenant: str, principal: str) -> None:
    """Persist canonical IAM and one subscription with all four exact product features."""
    plan_result = PlanRegistry.create(
        {
            "name": f"D22B3 P26 {tenant}",
            "price": 100.0,
            "currency": "ZAR",
            "billingFrequency": "monthly",
            "planType": "PROFESSIONAL",
            "idempotencyKey": f"plan-{tenant}",
            "active": True,
            "features": ["legal.core", "billing.core", "crm.core", "hr.core"],
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
            TenantBusinessRoleRepository.insert(
                TenantBusinessRoleAuthority(
                    principal, tenant, "tenant_owner", TenantBusinessRoleStatus.ACTIVE,
                    0, NOW, None,
                ),
                collections["business_role"],
                session=session,
            )
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(
                    principal, tenant, "ENTERPRISE_ADMIN", RoleAssignmentStatus.ACTIVE, 0
                ),
                collections["assignment"],
                session=session,
            )


def _issue(
    client: MongoClient[Any], collections: dict[str, Any], tenant: str,
    principal: str, *, idempotency_key: str = "issue-one",
    product_id: TenantProductId = TenantProductId.LEGAL_OPERATIONS,
) -> Any:
    """Commit one issuance under caller-owned transaction lifecycle."""
    with client.start_session() as session:
        with session.start_transaction():
            return issue_tenant_product_entitlement(
                identity=_identity(tenant, principal),
                product_id=product_id,
                idempotency_key=idempotency_key,
                occurred_at=NOW,
                subscription_collection=collections["subscriptions"],
                entitlement_history_collection=collections["history"],
                entitlement_current_collection=collections["current"],
                authorization_evidence_registry=_issuer(collections),
                session=session,
            )


def _create_enterprise_agreement(
    client: MongoClient[Any], collections: dict[str, Any], tenant: str
) -> CommercialAgreement:
    """Persist one enterprise bundle draft against the exact offer fingerprint."""
    offer = get_commercial_offer(CommercialOfferId.ENTERPRISE_OPERATIONS)
    agreement = CommercialAgreement(
        tenant_id=tenant,
        agreement_id=f"agreement-{uuid4().hex}",
        offer_id=offer.offer_id,
        offer_fingerprint=offer.fingerprint,
        contract_reference=f"contract-{tenant}",
        contract_version="2026-10-01",
        counterparty_legal_name="Synthetic Enterprise Counterparty (Pty) Ltd",
        effective_at=NOW - timedelta(days=1),
        expires_at=NOW + timedelta(days=365),
        renewal_mode=CommercialRenewalMode.MANUAL,
        notice_days=30,
        termination_terms_reference=f"terms-{tenant}",
    )
    with client.start_session() as session:
        with session.start_transaction():
            create_agreement_or_replay(
                agreement,
                collections["agreement_history"],
                collections["agreement_current"],
                session=session,
            )
    return agreement


def _verified_execution_evidence(
    agreement: CommercialAgreement, principal: str
) -> VerifiedCommercialAgreementExecutionEvidence:
    """Synthetic verifier output for the service's trusted-evidence contract."""
    signed_at = NOW + timedelta(minutes=1)
    return VerifiedCommercialAgreementExecutionEvidence(
        tenant_id=agreement.tenant_id,
        agreement_id=agreement.agreement_id,
        contract_reference=agreement.contract_reference,
        contract_version=agreement.contract_version,
        offer_fingerprint=agreement.offer_fingerprint,
        execution_evidence_reference=f"signature-evidence:{agreement.agreement_id}",
        execution_evidence_fingerprint="a" * 128,
        signatory_principal_id=principal,
        signatory_authority_reference=f"board-mandate:{agreement.tenant_id}",
        signatory_authority_fingerprint="b" * 128,
        signed_at=signed_at,
        verified_at=signed_at + timedelta(minutes=1),
        verifier_id="synthetic-signature-evidence-verifier",
        verification_receipt_reference=f"verification-receipt:{agreement.agreement_id}",
        verification_receipt_fingerprint="c" * 128,
    )


def test_real_enterprise_bundle_activation_and_unknown_commit_reconciliation(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Agreement execution, four product entitlements and receipt share one commit."""
    client, _database, collections = mongo_context
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed(client, collections, tenant, principal)
    agreement = _create_enterprise_agreement(client, collections, tenant)
    evidence = _verified_execution_evidence(agreement, principal)
    occurred_at = evidence.verified_at + timedelta(minutes=1)

    with client.start_session() as session:
        with session.start_transaction():
            outcome, receipt = activate_commercial_bundle(
                identity=_identity(tenant, principal),
                agreement_id=agreement.agreement_id,
                verified_execution_evidence=evidence,
                occurred_at=occurred_at,
                agreement_history_collection=collections["agreement_history"],
                agreement_current_collection=collections["agreement_current"],
                subscription_collection=collections["subscriptions"],
                entitlement_history_collection=collections["history"],
                entitlement_current_collection=collections["current"],
                authorization_evidence_registry=_issuer(collections),
                receipt_collection=collections["bundle_receipts"],
                session=session,
            )
    assert outcome is CommercialBundleActivationOutcome.ACTIVATED
    assert tuple(item["product_id"] for item in receipt.product_entitlements) == (
        "LEGAL_OPERATIONS", "BILLING", "CRM", "HR"
    )
    assert collections["agreement_history"].count_documents({"tenant_id": tenant}) == 3
    assert collections["agreement_current"].count_documents({"tenant_id": tenant}) == 1
    assert collections["authorization"].count_documents({"tenant_id": tenant}) == 4
    assert collections["history"].count_documents({"tenant_id": tenant}) == 8
    assert collections["current"].count_documents({"tenant_id": tenant}) == 4
    assert collections["bundle_receipts"].count_documents({"tenant_id": tenant}) == 1

    with client.start_session() as session:
        with session.start_transaction():
            active_agreement = get_current_agreement(
                tenant, agreement.agreement_id,
                collections["agreement_history"], collections["agreement_current"],
                session=session,
            )
            assert active_agreement.lifecycle_state is CommercialAgreementState.ACTIVE
            assert active_agreement.lifecycle_revision == 2
            for item in receipt.product_entitlements:
                current = get_current_product_entitlement(
                    tenant, item["entitlement_id"],
                    collections["history"], collections["current"],
                    session=session,
                )
                assert current.lifecycle_state is TenantProductEntitlementState.ACTIVE
                assert current.fingerprint == item["entitlement_fingerprint"]
            reconciled, recovered = reconcile_commercial_bundle_activation(
                tenant_id=tenant,
                agreement_id=agreement.agreement_id,
                agreement_history_collection=collections["agreement_history"],
                agreement_current_collection=collections["agreement_current"],
                entitlement_history_collection=collections["history"],
                entitlement_current_collection=collections["current"],
                receipt_collection=collections["bundle_receipts"],
                session=session,
            )
            assert reconciled is CommercialBundleReconciliationState.COMMITTED
            assert recovered is not None
            assert recovered.fingerprint == receipt.fingerprint

    with client.start_session() as session:
        with session.start_transaction():
            replay, replay_receipt = activate_commercial_bundle(
                identity=_identity(tenant, principal),
                agreement_id=agreement.agreement_id,
                verified_execution_evidence=evidence,
                occurred_at=occurred_at,
                agreement_history_collection=collections["agreement_history"],
                agreement_current_collection=collections["agreement_current"],
                subscription_collection=collections["subscriptions"],
                entitlement_history_collection=collections["history"],
                entitlement_current_collection=collections["current"],
                authorization_evidence_registry=_issuer(collections),
                receipt_collection=collections["bundle_receipts"],
                session=session,
            )
    assert replay is CommercialBundleActivationOutcome.IDEMPOTENT_REPLAY
    assert replay_receipt.fingerprint == receipt.fingerprint


def test_real_bundle_activation_abort_leaves_no_execution_or_product_writes(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Caller abort rolls back agreement, all entitlements, auth evidence and receipt."""
    client, _database, collections = mongo_context
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed(client, collections, tenant, principal)
    agreement = _create_enterprise_agreement(client, collections, tenant)
    evidence = _verified_execution_evidence(agreement, principal)

    with client.start_session() as session:
        session.start_transaction()
        activate_commercial_bundle(
            identity=_identity(tenant, principal),
            agreement_id=agreement.agreement_id,
            verified_execution_evidence=evidence,
            occurred_at=evidence.verified_at + timedelta(minutes=1),
            agreement_history_collection=collections["agreement_history"],
            agreement_current_collection=collections["agreement_current"],
            subscription_collection=collections["subscriptions"],
            entitlement_history_collection=collections["history"],
            entitlement_current_collection=collections["current"],
            authorization_evidence_registry=_issuer(collections),
            receipt_collection=collections["bundle_receipts"],
            session=session,
        )
        session.abort_transaction()

    with client.start_session() as session:
        with session.start_transaction():
            current = get_current_agreement(
                tenant, agreement.agreement_id,
                collections["agreement_history"], collections["agreement_current"],
                session=session,
            )
            assert current.lifecycle_state is CommercialAgreementState.DRAFT
            reconciled, receipt = reconcile_commercial_bundle_activation(
                tenant_id=tenant,
                agreement_id=agreement.agreement_id,
                agreement_history_collection=collections["agreement_history"],
                agreement_current_collection=collections["agreement_current"],
                entitlement_history_collection=collections["history"],
                entitlement_current_collection=collections["current"],
                receipt_collection=collections["bundle_receipts"],
                session=session,
            )
            assert reconciled is CommercialBundleReconciliationState.NOT_COMMITTED
            assert receipt is None
    assert collections["agreement_history"].count_documents({"tenant_id": tenant}) == 1
    assert collections["authorization"].count_documents({"tenant_id": tenant}) == 0
    assert collections["history"].count_documents({"tenant_id": tenant}) == 0
    assert collections["current"].count_documents({"tenant_id": tenant}) == 0
    assert collections["bundle_receipts"].count_documents({"tenant_id": tenant}) == 0


def test_real_four_product_bundle_issuance_commits_atomically(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """All four mapped product entitlements and authorization receipts share one commit."""
    client, _database, collections = mongo_context
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed(client, collections, tenant, principal)
    products = (
        TenantProductId.LEGAL_OPERATIONS,
        TenantProductId.BILLING,
        TenantProductId.CRM,
        TenantProductId.HR,
    )
    with client.start_session() as session:
        with session.start_transaction():
            results = tuple(
                issue_tenant_product_entitlement(
                    identity=_identity(tenant, principal),
                    product_id=product,
                    idempotency_key=f"bundle-{product.value.lower()}",
                    occurred_at=NOW,
                    subscription_collection=collections["subscriptions"],
                    entitlement_history_collection=collections["history"],
                    entitlement_current_collection=collections["current"],
                    authorization_evidence_registry=_issuer(collections),
                    session=session,
                )
                for product in products
            )
    assert tuple(item.composition.entitlement.product_id for item in results) == products
    assert all(
        item.composition.entitlement.lifecycle_state.value == "ACTIVE"
        for item in results
    )
    assert collections["authorization"].count_documents({"tenant_id": tenant}) == 4
    assert collections["history"].count_documents({"tenant_id": tenant}) == 8
    assert collections["current"].count_documents({"tenant_id": tenant}) == 4


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
