"""HTTP projection certificate for the authenticated EOS tenant module manifest."""
import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from tools.eos.api import auth_router
from tools.eos.auth.tenant_module_manifest import TenantModuleId
from tools.eos.crm.domain.crm_core_entitlement import (
    CRM_CORE_FEATURE_ID,
    CrmCoreEntitlement,
    CrmCoreEntitlementState,
)
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
    create_tenant_product_entitlement,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)
from tools.eos.saas.entitlement import tenant_product_entitlement_registry as registry
from tools.eos.crm.service import crm_core_entitlement_resolver as crm_resolver


TENANT = "TENANT-MODULE-HTTP"
NOW = datetime(2026, 11, 6, 9, 0, tzinfo=timezone.utc)
SOURCE = "a" * 128
ACTIVATION = "b" * 128


class FakeSession:
    def __init__(self):
        self.in_transaction = False
        self.aborted = 0
        self.ended = 0

    def start_transaction(self):
        self.in_transaction = True

    def abort_transaction(self):
        self.in_transaction = False
        self.aborted += 1

    def end_session(self):
        self.ended += 1


class FakeClient:
    def __init__(self):
        self.sessions = []

    def start_session(self):
        session = FakeSession()
        self.sessions.append(session)
        return session


class FakeDatabase:
    def __getitem__(self, name):
        return SimpleNamespace(name=name)


def _active_legal(tenant_id=TENANT):
    pending = create_tenant_product_entitlement(
        tenant_id=tenant_id,
        entitlement_id=derive_tenant_product_entitlement_id(
            tenant_id, TenantProductId.LEGAL_OPERATIONS
        ),
        product_id=TenantProductId.LEGAL_OPERATIONS,
        source_evidence_reference="agreement:approved",
        source_evidence_fingerprint=SOURCE,
    )
    return pending.transition(
        TenantProductEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="subscription:active",
        evidence_fingerprint=ACTIVATION,
        occurred_at=NOW,
    )


def _active_crm(tenant_id=TENANT):
    pending = CrmCoreEntitlement(
        tenant_id=tenant_id,
        entitlement_id=f"crm.core:{tenant_id}:subscription-1",
        feature_id=CRM_CORE_FEATURE_ID,
        subscription_id="subscription-1",
        plan_id="plan-1",
        plan_catalogue_version=1,
        subscription_proof_hash="A" * 128,
        lifecycle_state=CrmCoreEntitlementState.PENDING_SOURCE,
    )
    return pending.transition(
        CrmCoreEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="subscription:active",
        evidence_fingerprint=ACTIVATION,
        occurred_at=NOW,
    )


def _bind_runtime(monkeypatch):
    from tools.eos.kernel import db as kernel_db

    client = FakeClient()
    monkeypatch.setattr(kernel_db, "get_client", lambda: client)
    monkeypatch.setattr(kernel_db, "get_database", lambda: FakeDatabase())
    monkeypatch.setattr(crm_resolver, "resolve_crm_core_entitlement", lambda *_a, **_k: None)
    return client


def test_module_manifest_http_projection_reads_canonical_legal_evidence(monkeypatch):
    client = _bind_runtime(monkeypatch)
    legal = _active_legal()
    missing = registry.TenantProductEntitlementRegistryNotFoundError()

    def get_current(tenant_id, entitlement_id, *_args, session=None, **_kwargs):
        assert tenant_id == TENANT
        assert session is client.sessions[-1]
        if entitlement_id == legal.entitlement_id:
            return legal
        raise missing

    monkeypatch.setattr(registry, "get_current", get_current)
    result = auth_router._workspace_module_manifest_projection(TENANT)

    assert [item["moduleId"] for item in result] == [TenantModuleId.LEGAL_OS.value]
    assert result[0]["entitlementRevision"] == 1
    assert client.sessions[0].aborted == 1
    assert client.sessions[0].ended == 1


def test_module_manifest_http_projection_uses_crm_core_resolver(monkeypatch):
    client = _bind_runtime(monkeypatch)
    crm = _active_crm()
    missing = registry.TenantProductEntitlementRegistryNotFoundError()

    def get_current(*_args, **_kwargs):
        raise missing

    def resolve_crm(tenant_id, collection, session):
        assert tenant_id == TENANT
        assert collection.name == "subscriptions"
        assert session is client.sessions[-1]
        return crm

    monkeypatch.setattr(registry, "get_current", get_current)
    monkeypatch.setattr(crm_resolver, "resolve_crm_core_entitlement", resolve_crm)
    result = auth_router._workspace_module_manifest_projection(TENANT)

    assert [item["moduleId"] for item in result] == [TenantModuleId.CRM.value]
    assert client.sessions[0].aborted == 1
    assert client.sessions[0].ended == 1


def test_module_manifest_http_projection_retries_whole_read_transaction(monkeypatch):
    client = _bind_runtime(monkeypatch)
    missing = registry.TenantProductEntitlementRegistryNotFoundError()
    calls = {"count": 0}

    def get_current(*_args, **_kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise registry.TenantProductEntitlementRegistryRetryRequiredError()
        raise missing

    monkeypatch.setattr(registry, "get_current", get_current)
    result = auth_router._workspace_module_manifest_projection(TENANT)

    assert result == ()
    assert len(client.sessions) == 2
    assert all(session.aborted == 1 and session.ended == 1 for session in client.sessions)


def test_module_manifest_http_projection_rejects_foreign_tenant_evidence(monkeypatch):
    client = _bind_runtime(monkeypatch)
    foreign = _active_legal("TENANT-FOREIGN")
    missing = registry.TenantProductEntitlementRegistryNotFoundError()

    calls = {"count": 0}

    def get_current(_tenant_id, _entitlement_id, *_args, **_kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return foreign
        raise missing

    monkeypatch.setattr(registry, "get_current", get_current)
    with pytest.raises(auth_router.WorkspaceModuleManifestProjectionError):
        auth_router._workspace_module_manifest_projection(TENANT)

    assert client.sessions[0].ended == 1


def test_module_manifest_endpoint_revalidates_workspace_before_returning_modules(monkeypatch):
    monkeypatch.setattr(
        auth_router,
        "build_workspace_bootstrap_projection",
        lambda **_kwargs: SimpleNamespace(tenant_id=TENANT),
    )
    monkeypatch.setattr(
        auth_router,
        "_workspace_module_manifest_projection",
        lambda tenant_id: (
            {
                "moduleId": TenantModuleId.LEGAL_OS.value,
                "productId": TenantProductId.LEGAL_OPERATIONS.value,
                "label": "Legal OS",
            },
        ),
    )
    identity = SimpleNamespace(identity_id="principal-1")
    response = asyncio.run(auth_router.workspace_module_manifest(identity))

    assert response["status"] == "READY"
    assert response["workspace"]["tenantId"] == TENANT
    assert response["workspace"]["modules"][0]["moduleId"] == "LEGAL_OS"
    assert "businessRole" not in response["workspace"]
    assert "permissions" not in response["workspace"]
