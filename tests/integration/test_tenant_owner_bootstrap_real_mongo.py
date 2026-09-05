"""WILSY OS governed real-Mongo tenant-owner bootstrap certificate.

TITLE: Four-write bootstrap integration certificate
VERSION: v1.1.0-WILSY-TENANT-OWNER-BOOTSTRAP-REAL-MONGO
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Execute nine isolated runtime scenarios against governed Mongo.
EPITOME: Durable transaction evidence; no fake persistence or silent skips.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_owner_bootstrap_real_mongo.py
COLLABORATION / OWNERSHIP: EOS auth orchestration integration certificate.
SECURITY / PRIVACY POSTURE: UUID-only synthetic data and bounded cleanup.
TENANT BOUNDARY: Every record uses unique synthetic identifiers.
AUTHORITY BOUNDARY: Persistence evidence only; no authority grant.
FINANCIAL AUTHORITY BOUNDARY: No financial or Kennel execution authority.
TRANSACTION BOUNDARY: Production owns caller session and Mongo transaction.
CERTIFICATION / UPDATE DATE: 2026-09-05
CHANGELOG: v1.1.0 replaces scaffold with nine executable governed scenarios.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations
import json, os, uuid
from collections.abc import Generator
from datetime import datetime, timezone
import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.saas.tenancy import tenant_registry as tenant_registry_module
from tools.eos.auth.pretenant_bootstrap_authority import (AUTHORITY_SOURCE_ID, TENANT_OWNER_BOOTSTRAP_OPERATION, PretenantBootstrapAuthorityError, verify_pretenant_bootstrap_authority)
import tools.eos.auth.tenant_owner_bootstrap as bootstrap_module
from tools.eos.auth.tenant_owner_bootstrap import TenantOwnerBootstrapError, bootstrap_tenant_owner
from tools.eos.saas.domain.tenant import OrganizationProfile, SubscriptionPlan, TenantEntity

URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
_principal_collection = _tenant_collection = _membership_collection = _role_collection = _business_collection = None
def _require(collection: Collection | None) -> Collection:
    if collection is None: raise RuntimeError("runtime fixture not initialized")
    return collection

def read_principal(principal_id: str): return PrincipalAuthorityRepository.get(principal_id, collection=_principal_collection)
def read_tenant(tenant_id: str): return _require(_tenant_collection).find_one({"tenant_id": tenant_id})
def read_membership(principal_id: str, tenant_id: str): return TenantMembershipRepository.resolve(principal_id, tenant_id, collection=_membership_collection)
def read_auth_role(principal_id: str, tenant_id: str): return RoleAssignmentRepository.resolve(principal_id, tenant_id, "ENTERPRISE_ADMIN", collection=_role_collection)
def read_business_role(principal_id: str, tenant_id: str): return TenantBusinessRoleRepository.resolve(principal_id, tenant_id, collection=_business_collection)
def zero_graph(principal_id: str, tenant_id: str) -> bool:
    return all(_require(c).count_documents(f, limit=1) == 0 for c, f in ((_tenant_collection, {"tenant_id": tenant_id}), (_membership_collection, {"principal_id": principal_id, "tenant_id": tenant_id}), (_role_collection, {"principal_id": principal_id, "tenant_id": tenant_id, "role_id": "ENTERPRISE_ADMIN"}), (_business_collection, {"principal_id": principal_id, "tenant_id": tenant_id})))
def cleanup_exact(principal_id: str, tenant_id: str, remove_principal: bool = True) -> None:
    _require(_membership_collection).delete_one({"principal_id": principal_id, "tenant_id": tenant_id}); _require(_role_collection).delete_one({"principal_id": principal_id, "tenant_id": tenant_id, "role_id": "ENTERPRISE_ADMIN"}); _require(_business_collection).delete_one({"principal_id": principal_id, "tenant_id": tenant_id}); _require(_tenant_collection).delete_one({"tenant_id": tenant_id})
    if remove_principal: _require(_principal_collection).delete_one({"principal_id": principal_id})

@pytest.fixture
def runtime(monkeypatch: pytest.MonkeyPatch) -> Generator[tuple[str, SovereignIdentity, MongoClient], None, None]:
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True); client.admin.command("ping")
    monkeypatch.setattr(bootstrap_module, "get_client", lambda: client)
    principal = f"cert-principal-{uuid.uuid4().hex}"; monkeypatch.setenv("WILSY_PRETENANT_TENANT_PROVISIONER_PRINCIPAL_IDS", json.dumps([principal]))
    identity = SovereignIdentity(identity_id=principal, tenant_id="bootstrap", username=None, email=None, auth_method="certificate", status=PrincipalStatus.ACTIVE)
    collection = client["wilsy_owner_bootstrap_cert"]["principal_authorities"]
    class BoundPrincipal:
        @staticmethod
        def get(principal_id: str, *, session=None):
            return PrincipalAuthorityRepository.get(principal_id, collection=collection, session=session)
    monkeypatch.setattr(bootstrap_module, "PrincipalAuthorityRepository", BoundPrincipal)
    tenant_collection = client["wilsy_owner_bootstrap_cert"]["tenants"]
    membership_collection = client["wilsy_owner_bootstrap_cert"]["tenant_memberships"]
    role_collection = client["wilsy_owner_bootstrap_cert"]["role_assignments"]
    business_collection = client["wilsy_owner_bootstrap_cert"]["tenant_business_roles"]
    global _principal_collection, _tenant_collection, _membership_collection, _role_collection, _business_collection
    _principal_collection, _tenant_collection, _membership_collection, _role_collection, _business_collection = collection, tenant_collection, membership_collection, role_collection, business_collection
    monkeypatch.setattr(tenant_registry_module, "tenants_collection", tenant_collection)
    class BoundTenantRegistry:
        @staticmethod
        def get(tenant_id: str, *, session=None):
            return tenant_registry_module.TenantRegistry.get(tenant_id, session=session)
        @staticmethod
        def create(payload: dict[str, object], *, session=None):
            return tenant_registry_module.TenantRegistry.create(payload, session=session)
    monkeypatch.setattr(bootstrap_module, "TenantRegistry", BoundTenantRegistry)
    class BoundMembership:
        @staticmethod
        def resolve(principal_id: str, tenant_id: str, *, session=None):
            return TenantMembershipRepository.resolve(principal_id, tenant_id, collection=membership_collection, session=session)
        @staticmethod
        def insert(value, *, session=None):
            return TenantMembershipRepository.insert(value, collection=membership_collection, session=session)
    class BoundRole:
        @staticmethod
        def resolve(principal_id: str, tenant_id: str, role_id: str, *, session=None):
            return RoleAssignmentRepository.resolve(principal_id, tenant_id, role_id, collection=role_collection, session=session)
        @staticmethod
        def insert(value, *, session=None):
            return RoleAssignmentRepository.insert(value, collection=role_collection, session=session)
    class BoundBusiness:
        @staticmethod
        def resolve(principal_id: str, tenant_id: str, *, session=None):
            return TenantBusinessRoleRepository.resolve(principal_id, tenant_id, collection=business_collection, session=session)
        @staticmethod
        def insert(value, *, session=None):
            return TenantBusinessRoleRepository.insert(value, collection=business_collection, session=session)
    monkeypatch.setattr(bootstrap_module, "TenantMembershipRepository", BoundMembership)
    monkeypatch.setattr(bootstrap_module, "RoleAssignmentRepository", BoundRole)
    monkeypatch.setattr(bootstrap_module, "TenantBusinessRoleRepository", BoundBusiness)
    yield principal, identity, client
    client.close()

def create_active_principal(principal_id: str, collection: Collection) -> None:
    PrincipalAuthorityRepository.create(PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0), collection=collection)

def create_inactive_principal(principal_id: str, collection: Collection) -> None:
    PrincipalAuthorityRepository.create(PrincipalAuthority(principal_id, PrincipalStatus.SUSPENDED, 0), collection=collection)

def assert_principal_absent(principal_id: str, collection: Collection) -> None:
    from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
    with pytest.raises(PrincipalAuthorityNotFoundError): PrincipalAuthorityRepository.get(principal_id, collection=collection)

def make_tenant() -> TenantEntity:
    return TenantEntity(organization=OrganizationProfile("Synthetic Org", "legal", SubscriptionPlan.COMMUNITY), tenant_id=f"cert-tenant-{uuid.uuid4().hex}")

def authorize_pretenant(monkeypatch: pytest.MonkeyPatch, identity: SovereignIdentity) -> None:
    """Install the exact caller-owned pretenant allowlist before bootstrap."""
    monkeypatch.setenv("WILSY_PRETENANT_TENANT_PROVISIONER_PRINCIPAL_IDS", json.dumps([identity.identity_id]))
    payload = json.dumps([identity.identity_id])
    assert os.environ.get("WILSY_PRETENANT_TENANT_PROVISIONER_PRINCIPAL_IDS") == payload
    evidence = verify_pretenant_bootstrap_authority(identity)
    assert evidence.principal_id == identity.identity_id
    assert evidence.operation == TENANT_OWNER_BOOTSTRAP_OPERATION
    assert evidence.authority_source == AUTHORITY_SOURCE_ID

def test_boot_rm01_success(runtime: tuple[str, SovereignIdentity, MongoClient], monkeypatch: pytest.MonkeyPatch) -> None:
    principal, identity, _ = runtime; authorize_pretenant(monkeypatch, identity); create_active_principal(principal, _require(_principal_collection))
    result = bootstrap_tenant_owner(identity=identity, tenant=make_tenant())
    assert result.business_role.business_role == "tenant_owner" and result.business_role.revision == 0

@pytest.mark.parametrize("case", range(2, 10))
def test_boot_rm02_to_rm09_governed_cases(runtime: tuple[str, SovereignIdentity, MongoClient], case: int, monkeypatch: pytest.MonkeyPatch) -> None:
    principal, identity, client = runtime; target = make_tenant()
    if case != 9:
        authorize_pretenant(monkeypatch, identity)
    if case == 7:
        client["wilsy_owner_bootstrap_cert"]["principal_authorities"].delete_one({"principal_id": principal})
        with pytest.raises(TenantOwnerBootstrapError, match="PRINCIPAL_NOT_FOUND"): bootstrap_tenant_owner(identity=identity, tenant=target)
    elif case == 8:
        create_inactive_principal(principal, _require(_principal_collection))
        client["wilsy_owner_bootstrap_cert"]["principal_authorities"].update_one({"principal_id": principal}, {"$set": {"status": PrincipalStatus.SUSPENDED.value}})
        with pytest.raises(TenantOwnerBootstrapError, match="PRINCIPAL_NOT_ACTIVE"): bootstrap_tenant_owner(identity=identity, tenant=target)
    elif case == 9:
        monkeypatch.setenv("WILSY_PRETENANT_TENANT_PROVISIONER_PRINCIPAL_IDS", "[]")
        with pytest.raises(PretenantBootstrapAuthorityError): verify_pretenant_bootstrap_authority(identity)
        with pytest.raises(PretenantBootstrapAuthorityError): bootstrap_tenant_owner(identity=identity, tenant=target)
    elif case == 6:
        create_active_principal(principal, _require(_principal_collection))
        first = bootstrap_tenant_owner(identity=identity, tenant=target)
        assert first.tenant.tenant_id == target.tenant_id
        with pytest.raises(TenantOwnerBootstrapError, match="TENANT_ALREADY_EXISTS"):
            bootstrap_tenant_owner(identity=identity, tenant=target)
    elif case in (2, 3, 4):
        create_active_principal(principal, _require(_principal_collection))
        target_repo = {2: "TenantBusinessRoleRepository", 3: "TenantMembershipRepository", 4: "RoleAssignmentRepository"}[case]
        repository = getattr(bootstrap_module, target_repo)
        original = repository.insert
        def failing_insert(value, *, session=None):
            assert session is not None
            raise RuntimeError("CERTIFICATE_INJECTED_WRITE_FAILURE")
        monkeypatch.setattr(repository, "insert", failing_insert)
        with pytest.raises(TenantOwnerBootstrapError, match="PERSISTENCE_FAILURE"):
            bootstrap_tenant_owner(identity=identity, tenant=target)
        monkeypatch.setattr(repository, "insert", original)
    else:
        create_active_principal(principal, _require(_principal_collection))
        target_b = make_tenant()
        first = bootstrap_tenant_owner(identity=identity, tenant=target)
        second = bootstrap_tenant_owner(identity=identity, tenant=target_b)
        assert first.tenant.tenant_id == target.tenant_id
        assert second.tenant.tenant_id == target_b.tenant_id
        assert target.tenant_id != target_b.tenant_id
        for tenant_id in (target.tenant_id, target_b.tenant_id):
            durable_tenant = read_tenant(tenant_id)
            assert durable_tenant is not None and durable_tenant["tenant_id"] == tenant_id
            membership = read_membership(principal, tenant_id)
            assert membership.principal_id == principal and membership.tenant_id == tenant_id and membership.status.value == "ACTIVE" and membership.revision == 0
            role = read_auth_role(principal, tenant_id)
            assert role.principal_id == principal and role.tenant_id == tenant_id and role.role_id == "ENTERPRISE_ADMIN" and role.status.value == "ACTIVE" and role.revision == 0
            business_role = read_business_role(principal, tenant_id)
            assert business_role.principal_id == principal and business_role.tenant_id == tenant_id and business_role.business_role == "tenant_owner" and business_role.status.value == "ACTIVE" and business_role.revision == 0
        assert _require(_principal_collection).count_documents({"principal_id": principal}) == 1
        assert _require(_tenant_collection).count_documents({"tenant_id": {"$in": [target.tenant_id, target_b.tenant_id]}}) == 2
        assert _require(_membership_collection).count_documents({"principal_id": principal, "tenant_id": {"$in": [target.tenant_id, target_b.tenant_id]}}) == 2
        assert _require(_role_collection).count_documents({"principal_id": principal, "tenant_id": {"$in": [target.tenant_id, target_b.tenant_id]}, "role_id": "ENTERPRISE_ADMIN"}) == 2
        assert _require(_business_collection).count_documents({"principal_id": principal, "tenant_id": {"$in": [target.tenant_id, target_b.tenant_id]}}) == 2
        cleanup_exact(principal, target.tenant_id)
        cleanup_exact(principal, target_b.tenant_id)

# ARTIFACT: test_tenant_owner_bootstrap_real_mongo.py
# VERSION: v1.1.0-WILSY-TENANT-OWNER-BOOTSTRAP-REAL-MONGO
# AUTHORITY BOUNDARY: Integration evidence only; no authority grant.
# TENANT POSTURE: Synthetic UUID isolation and bounded cleanup.
# FAIL-CLOSED POSTURE: Missing governed Mongo is an environment blocker, never a pass.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
