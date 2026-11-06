"""Authenticated real-Mongo HTTP certificate for commercial agreements.

The test exercises FastAPI routing, durable IAM repositories, tenant scope,
the agreement router's transaction boundary and real replica-set persistence.
Only synthetic tenants and contract metadata are used.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.commercial_agreement_router as agreement_api
import tools.eos.api.tenant_authorization_http as authorization_http
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth import authentication, tenant_access
import tools.eos.kernel.db as kernel_db_module
import tools.eos.auth.principal_authority_repository as principal_repository_module
import tools.eos.auth.tenant_membership_repository as membership_repository_module
import tools.eos.auth.role_assignment_repository as role_repository_module
import tools.eos.auth.tenant_business_role_repository as business_role_repository_module
import tools.eos.saas.entitlement.tenant_product_entitlement_registry as entitlement_registry_module
import tools.eos.saas.billing.plan_registry as plan_registry_module
import tools.eos.saas.billing.subscription_registry as subscription_registry_module
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.saas.entitlement.commercial_bundle_activation import VerifiedCommercialAgreementExecutionEvidence
from tools.eos.saas.entitlement.commercial_agreement_registry import (
    CURRENT_COLLECTION,
    HISTORY_COLLECTION,
)

URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc)


class _PrincipalReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        return PrincipalAuthorityRepository.get(principal_id, self.collection, session=session)


class _MembershipReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, tenant_id: str, *, session: Any = None) -> Any:
        return TenantMembershipRepository.resolve(principal_id, tenant_id, self.collection, session=session)


class _RoleReader:
    """Mirror the production split-store role reader against isolated collections."""
    def __init__(self, role_collection: Any, business_collection: Any) -> None:
        self.role_collection = role_collection
        self.business_collection = business_collection

    def resolve_current_business_role(
        self, principal_id: str, tenant_id: str, *, session: Any = None
    ) -> Any:
        return TenantBusinessRoleRepository.resolve(
            principal_id, tenant_id, self.business_collection, session=session
        )

    def resolve_all_business_roles(
        self, principal_id: str, tenant_id: str, *, session: Any = None
    ) -> tuple[Any, ...]:
        return TenantBusinessRoleRepository.resolve_all(
            principal_id, tenant_id, self.business_collection, session=session
        )

    def resolve(
        self, principal_id: str, tenant_id: str, role_id: str, *, session: Any = None
    ) -> Any:
        if role_id in TENANT_ROLES:
            return TenantBusinessRoleRepository.resolve_business_role(
                principal_id, tenant_id, role_id, self.business_collection, session=session
            )
        return RoleAssignmentRepository.resolve(
            principal_id, tenant_id, role_id, self.role_collection, session=session
        )

@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    client: MongoClient[Any] = MongoClient(
        URI, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000,
        retryWrites=True, tz_aware=True,
    )
    database = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"host Mongo unavailable before fixture yield: {type(error).__name__}")
        if hello.get("setName") != REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("replica set does not support logical sessions")
        database = client.get_database(
            f"ca_http_{uuid4().hex}",
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        collections = {
            "principal": database.get_collection("principal_authorities"),
            "membership": database.get_collection("tenant_memberships"),
            "roles": database.get_collection("role_assignments"),
            "business": database.get_collection("tenant_business_roles"),
        }
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        RoleAssignmentRepository.ensure_indexes(collections["roles"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business"])
        yield {"client": client, "database": database, "collections": collections}
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _seed_actor(
    context: dict[str, Any], *, tenant: str, principal: str,
    business_role: str, grant_role: str,
) -> None:
    c = context["collections"]
    with context["client"].start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0),
                c["principal"], session=session,
            )
            TenantMembershipRepository.insert(
                TenantMembershipAuthority(principal, tenant, TenantMembershipStatus.ACTIVE, 0),
                c["membership"], session=session,
            )
            TenantBusinessRoleRepository.insert(
                TenantBusinessRoleAuthority(
                    principal, tenant, business_role, TenantBusinessRoleStatus.ACTIVE,
                    0, NOW, None,
                ),
                c["business"], session=session,
            )
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(principal, tenant, grant_role, RoleAssignmentStatus.ACTIVE, 0),
                c["roles"], session=session,
            )


def _identity(principal: str, tenant: str) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=principal, tenant_id=tenant, username="commercial-operator",
        email="commercial-operator@example.test", auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _client(context: dict[str, Any], monkeypatch: pytest.MonkeyPatch, *, tenant: str, principal: str) -> TestClient:
    c = context["collections"]
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.dependency_overrides[authorization_http.get_current_identity] = lambda: _identity(principal, tenant)
    app.dependency_overrides[authentication.get_principal_authority_repository] = lambda: _PrincipalReader(c["principal"])
    app.dependency_overrides[tenant_access.get_tenant_membership_repository] = lambda: _MembershipReader(c["membership"])
    app.dependency_overrides[authorization_http.get_role_assignment_repository] = lambda: _RoleReader(c["roles"], c["business"])
    app.include_router(agreement_api.router, prefix="/api")
    monkeypatch.setattr(agreement_api, "get_client", lambda: context["client"])
    monkeypatch.setattr(agreement_api, "get_database", lambda: context["database"])
    return TestClient(app)


def _draft_payload(agreement_id: str = "agreement-http-1") -> dict[str, object]:
    return {
        "agreement_id": agreement_id,
        "offer_id": "LEGAL_OPERATIONS_STANDALONE",
        "contract_reference": f"contract-{agreement_id}",
        "contract_version": "2026-11-01",
        "counterparty_legal_name": "Synthetic Counterparty (Pty) Ltd",
        "effective_at": NOW.isoformat(),
        "expires_at": (NOW + timedelta(days=365)).isoformat(),
        "renewal_mode": "MANUAL",
        "notice_days": 30,
        "termination_terms_reference": "terms-http-1",
    }


def test_authenticated_owner_can_create_read_and_list_durable_agreement_history(
    mongo_context: dict[str, Any], monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_actor(mongo_context, tenant=tenant, principal=principal, business_role="tenant_owner", grant_role="ENTERPRISE_ADMIN")
    headers = {"X-Tenant-ID": tenant}
    with _client(mongo_context, monkeypatch, tenant=tenant, principal=principal) as http:
        created = http.post("/api/commercial/agreements", headers=headers, json=_draft_payload())
        assert created.status_code == 201, created.text
        body = created.json()
        assert body["outcome"] == "CREATED"
        assert body["agreement"]["tenant_id"] == tenant
        assert body["agreement"]["lifecycle_state"] == "DRAFT"
        current = http.get("/api/commercial/agreements/agreement-http-1", headers=headers)
        history = http.get("/api/commercial/agreements/agreement-http-1/history", headers=headers)
    assert current.status_code == 200, current.text
    assert history.status_code == 200, history.text
    assert current.json()["agreement"] == body["agreement"]
    assert history.json()["tenant_id"] == tenant
    assert len(history.json()["revisions"]) == 1
    assert mongo_context["database"][HISTORY_COLLECTION].count_documents({"tenant_id": tenant}) == 1
    assert mongo_context["database"][CURRENT_COLLECTION].count_documents({"tenant_id": tenant}) == 1


def test_authenticated_owner_replay_is_idempotent_and_conflict_is_rejected(
    mongo_context: dict[str, Any], monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_actor(mongo_context, tenant=tenant, principal=principal, business_role="tenant_owner", grant_role="ENTERPRISE_ADMIN")
    headers = {"X-Tenant-ID": tenant}
    with _client(mongo_context, monkeypatch, tenant=tenant, principal=principal) as http:
        first = http.post("/api/commercial/agreements", headers=headers, json=_draft_payload())
        replay = http.post("/api/commercial/agreements", headers=headers, json=_draft_payload())
        conflict_payload = _draft_payload()
        conflict_payload["counterparty_legal_name"] = "Different Counterparty (Pty) Ltd"
        conflict = http.post("/api/commercial/agreements", headers=headers, json=conflict_payload)
    assert first.status_code == 201
    assert replay.status_code == 201
    assert replay.json()["outcome"] == "IDEMPOTENT_REPLAY"
    assert conflict.status_code == 409


def test_foreign_tenant_scope_and_legal_partner_cannot_read_owner_commercial_agreements(
    mongo_context: dict[str, Any], monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    foreign_tenant = f"tenant-{uuid4().hex}"
    _seed_actor(mongo_context, tenant=tenant, principal=principal, business_role="tenant_owner", grant_role="ENTERPRISE_ADMIN")
    headers = {"X-Tenant-ID": tenant}
    with _client(mongo_context, monkeypatch, tenant=tenant, principal=principal) as owner:
        created = owner.post("/api/commercial/agreements", headers=headers, json=_draft_payload())
        assert created.status_code == 201
    foreign_scope = {"X-Tenant-ID": foreign_tenant}
    with _client(mongo_context, monkeypatch, tenant=tenant, principal=principal) as owner:
        denied_scope = owner.get("/api/commercial/agreements/agreement-http-1", headers=foreign_scope)
    assert denied_scope.status_code == 403

    partner, partner_principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_actor(mongo_context, tenant=partner, principal=partner_principal, business_role="tenant_legal_partner", grant_role="LEGAL_PARTNER")
    with _client(mongo_context, monkeypatch, tenant=partner, principal=partner_principal) as legal_partner:
        denied_role = legal_partner.get(
            "/api/commercial/agreements/agreement-http-1",
            headers={"X-Tenant-ID": partner},
        )
    assert denied_role.status_code == 403



class _TrustedExecutionVerifier:
    """Test-only verifier double; cryptographic behavior is covered by unit tests."""

    def __init__(self, principal_id: str) -> None:
        self.principal_id = principal_id
        self.signed_at = datetime.now(timezone.utc) - timedelta(seconds=30)

    def verify(self, *, agreement: Any, evidence_reference: str) -> VerifiedCommercialAgreementExecutionEvidence:
        assert evidence_reference == "evidence:trusted-test-provider:001"
        signed_at = self.signed_at
        return VerifiedCommercialAgreementExecutionEvidence(
            tenant_id=agreement.tenant_id,
            agreement_id=agreement.agreement_id,
            contract_reference=agreement.contract_reference,
            contract_version=agreement.contract_version,
            offer_fingerprint=agreement.offer_fingerprint,
            execution_evidence_reference=evidence_reference,
            execution_evidence_fingerprint="a" * 128,
            signatory_principal_id=self.principal_id,
            signatory_authority_reference="board-mandate:test",
            signatory_authority_fingerprint="b" * 128,
            signed_at=signed_at,
            verified_at=signed_at + timedelta(seconds=1),
            verifier_id="test-only-trusted-verifier",
            verification_receipt_reference="verification-receipt:test",
            verification_receipt_fingerprint="c" * 128,
        )


def test_authenticated_signatory_can_execute_only_verified_server_evidence(
    mongo_context: dict[str, Any], monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_actor(
        mongo_context, tenant=tenant, principal=principal,
        business_role="tenant_owner", grant_role="ENTERPRISE_ADMIN",
    )
    monkeypatch.setattr(
        agreement_api, "_execution_verifier",
        lambda _request: _TrustedExecutionVerifier(principal),
    )
    headers = {"X-Tenant-ID": tenant}
    with _client(mongo_context, monkeypatch, tenant=tenant, principal=principal) as http:
        created = http.post(
            "/api/commercial/agreements", headers=headers,
            json=_draft_payload("agreement-execute-http"),
        )
        assert created.status_code == 201, created.text
        executed = http.post(
            "/api/commercial/agreements/agreement-execute-http/execute",
            headers=headers,
            json={"execution_evidence_reference": "evidence:trusted-test-provider:001"},
        )
        assert executed.status_code == 200, executed.text
        assert executed.json()["outcome"] == "EXECUTED"
        assert executed.json()["agreement"]["lifecycle_state"] == "EXECUTED"
        replay = http.post(
            "/api/commercial/agreements/agreement-execute-http/execute",
            headers=headers,
            json={"execution_evidence_reference": "evidence:trusted-test-provider:001"},
        )
    assert replay.status_code == 200, replay.text
    assert replay.json()["outcome"] == "IDEMPOTENT_REPLAY"
    assert mongo_context["database"]["commercial_agreement_execution_verification_receipts"].count_documents(
        {"tenant_id": tenant, "agreement_id": "agreement-execute-http"}
    ) == 1


def test_execution_route_fails_closed_without_trusted_verifier_and_rejects_browser_proof(
    mongo_context: dict[str, Any], monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_actor(
        mongo_context, tenant=tenant, principal=principal,
        business_role="tenant_owner", grant_role="ENTERPRISE_ADMIN",
    )
    headers = {"X-Tenant-ID": tenant}
    with _client(mongo_context, monkeypatch, tenant=tenant, principal=principal) as http:
        created = http.post(
            "/api/commercial/agreements", headers=headers,
            json=_draft_payload("agreement-no-verifier"),
        )
        assert created.status_code == 201, created.text
        unavailable = http.post(
            "/api/commercial/agreements/agreement-no-verifier/execute",
            headers=headers,
            json={"execution_evidence_reference": "evidence:trusted-test-provider:001"},
        )
        browser_proof = http.post(
            "/api/commercial/agreements/agreement-no-verifier/execute",
            headers=headers,
            json={
                "execution_evidence_reference": "evidence:trusted-test-provider:001",
                "signature": "browser-supplied-signature",
                "certificate_pem": "browser-supplied-certificate",
            },
        )
    assert unavailable.status_code == 503
    assert browser_proof.status_code == 422


def test_legal_partner_cannot_execute_tenant_commercial_agreement(
    mongo_context: dict[str, Any], monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_actor(
        mongo_context, tenant=tenant, principal=principal,
        business_role="tenant_legal_partner", grant_role="LEGAL_PARTNER",
    )
    with _client(mongo_context, monkeypatch, tenant=tenant, principal=principal) as http:
        denied = http.post(
            "/api/commercial/agreements/agreement-any/execute",
            headers={"X-Tenant-ID": tenant},
            json={"execution_evidence_reference": "evidence:trusted-test-provider:001"},
        )
    assert denied.status_code == 403



def test_authenticated_execution_activation_and_entitlement_readback_real_mongo(
    mongo_context: dict[str, Any], monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    database = mongo_context["database"]
    now = datetime.now(timezone.utc)
    plans = database.get_collection("plans")
    subscriptions = database.get_collection(
        "subscriptions",
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    monkeypatch.setattr(plan_registry_module, "plans_collection", plans)
    monkeypatch.setattr(subscription_registry_module, "subscriptions_collection", subscriptions)
    monkeypatch.setattr(kernel_db_module, "get_database", lambda: database)
    for module in (
        principal_repository_module,
        membership_repository_module,
        role_repository_module,
        business_role_repository_module,
        entitlement_registry_module,
        subscription_registry_module,
    ):
        monkeypatch.setattr(
            module, "get_database", lambda database=database: database, raising=False
        )
    PlanRegistry.provision_indexes()
    subscription_registry_module._ensure_indexes(subscriptions)

    plan = PlanRegistry.create({
        "name": f"Execution activation certificate {tenant}",
        "price": 100.0,
        "currency": "ZAR",
        "billingFrequency": "monthly",
        "planType": "PROFESSIONAL",
        "idempotencyKey": f"plan-{tenant}",
        "active": True,
        "features": ["legal.core", "billing.core", "crm.core", "hr.core"],
        "metadata": {"certificate": True},
        "tags": ["commercial-bundle-activation"],
        "user": "COMMERCIAL-BUNDLE-CERT",
    })
    assert plan["success"] is True
    subscription = SubscriptionRegistry.create(
        {
            "tenantId": tenant,
            "planId": plan["plan"].plan_id,
            "startDate": (now - timedelta(days=1)).isoformat(),
            "idempotencyKey": f"subscription-{tenant}",
            "billingMode": "PLATFORM",
            "onboardingRef": f"ONBOARD-{tenant}",
            "metadata": {"certificate": True},
        },
        tenant_id_header=tenant,
    )
    assert subscription["success"] is True

    _seed_actor(
        mongo_context, tenant=tenant, principal=principal,
        business_role="tenant_owner", grant_role="ENTERPRISE_ADMIN",
    )
    trusted_verifier = _TrustedExecutionVerifier(principal)
    monkeypatch.setattr(
        agreement_api, "_execution_verifier",
        lambda _request: trusted_verifier,
    )
    payload = _draft_payload("agreement-full-journey")
    payload["offer_id"] = "ENTERPRISE_OPERATIONS_BUNDLE"
    payload["effective_at"] = (now - timedelta(days=1)).isoformat()
    payload["expires_at"] = (now + timedelta(days=365)).isoformat()
    headers = {"X-Tenant-ID": tenant}
    with _client(mongo_context, monkeypatch, tenant=tenant, principal=principal) as http:
        created = http.post("/api/commercial/agreements", headers=headers, json=payload)
        assert created.status_code == 201, created.text
        executed = http.post(
            "/api/commercial/agreements/agreement-full-journey/execute",
            headers=headers,
            json={"execution_evidence_reference": "evidence:trusted-test-provider:001"},
        )
        assert executed.status_code == 200, executed.text
        assert executed.json()["agreement"]["lifecycle_state"] == "EXECUTED"
        activated = http.post(
            "/api/commercial/agreements/agreement-full-journey/activate",
            headers=headers,
            json={"execution_evidence_reference": "evidence:trusted-test-provider:001"},
        )
        assert activated.status_code == 200, activated.text
        assert activated.json()["outcome"] == "ACTIVATED"
        readback = http.get(
            "/api/commercial/agreements/agreement-full-journey/entitlements",
            headers=headers,
        )
    assert readback.status_code == 200, readback.text
    products = readback.json()["product_entitlements"]
    assert {item["product_id"] for item in products} == {
        "LEGAL_OPERATIONS", "BILLING", "CRM", "HR"
    }
    assert all(item["lifecycle_state"] == "ACTIVE" for item in products)
    assert database["commercial_bundle_activation_receipts"].count_documents(
        {"tenant_id": tenant, "agreement_id": "agreement-full-journey"}
    ) == 1
    assert database["commercial_agreement_execution_verification_receipts"].count_documents(
        {"tenant_id": tenant, "agreement_id": "agreement-full-journey"}
    ) == 1
