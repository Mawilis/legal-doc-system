from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import derive_tenant_product_entitlement_id
from tools.eos.saas.domain.tenant_product_entitlement import TenantProductEntitlementState
from tools.eos.workspaces.persistence.tenant_module_work_registry import TenantModuleWorkRegistry
from tools.eos.workspaces.service import tenant_module_workspace_service as service_module

NOW = datetime(2026, 11, 6, 10, tzinfo=timezone.utc)
TENANT = "WILSYTENANT-4CD2FZ4O"


class Cursor(list):
    def sort(self, *_args, **_kwargs):
        return self

    def limit(self, _value):
        return self


class Collection:
    def __init__(self):
        self.rows = []

    def find_one(self, query, session=None):
        assert session is not None
        return next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)

    def insert_one(self, document, session=None):
        assert session is not None
        self.rows.append(dict(document))

    def find(self, query, session=None):
        assert session is not None
        return Cursor(row for row in self.rows if all(row.get(k) == v for k, v in query.items()))

    def update_one(self, query, update, session=None):
        assert session is not None
        row = next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)
        if row is None:
            return SimpleNamespace(matched_count=0)
        row.update(update["$set"])
        return SimpleNamespace(matched_count=1)


def active_entitlement(tenant_id, product_id):
    return SimpleNamespace(
        tenant_id=tenant_id,
        entitlement_id=derive_tenant_product_entitlement_id(tenant_id, product_id),
        product_id=product_id,
        lifecycle_state=TenantProductEntitlementState.ACTIVE,
        lifecycle_revision=2,
        fingerprint="c" * 128,
    )


def build_service(product_id, collection, monkeypatch, entitlements):
    monkeypatch.setattr(
        service_module,
        "get_current",
        lambda tenant, entitlement_id, *_args, **_kwargs: entitlements[entitlement_id],
    )
    return service_module.TenantModuleWorkspaceService(
        TenantModuleWorkRegistry(collection),
        product_id,
        object(),
        object(),
    )


def test_operations_and_intelligence_use_separate_entitlement_and_queue_authorities(monkeypatch):
    operations = active_entitlement(TENANT, TenantProductId.OPERATIONS)
    intelligence = active_entitlement(TENANT, TenantProductId.INTELLIGENCE)
    entitlements = {
        operations.entitlement_id: operations,
        intelligence.entitlement_id: intelligence,
    }
    ops_collection, intel_collection = Collection(), Collection()
    ops = build_service(TenantProductId.OPERATIONS, ops_collection, monkeypatch, entitlements)
    intel = build_service(TenantProductId.INTELLIGENCE, intel_collection, monkeypatch, entitlements)

    created = ops.create(
        tenant_id=TENANT, principal_id="principal-owner", title="Prepare operations runbook",
        description="", kind=service_module.ModuleWorkKind.TASK,
        priority=service_module.ModuleWorkPriority.HIGH, due_at=None,
        source_type=None, source_id=None, idempotency_key="ops-1", now=NOW, session=object(),
    )
    assert created.work_item_id.startswith("tmw_")
    assert ops.daily_queue(tenant_id=TENANT, now=NOW, session=object())[0]["title"] == "Prepare operations runbook"
    assert intel.daily_queue(tenant_id=TENANT, now=NOW, session=object()) == ()

    completed = ops.complete(
        tenant_id=TENANT, work_item_id=created.work_item_id,
        completion_note="Runbook prepared", now=NOW, session=object(),
    )
    assert completed.status.value == "COMPLETED"
    assert ops.daily_queue(tenant_id=TENANT, now=NOW, session=object()) == ()


def test_product_entitlement_mismatch_fails_closed(monkeypatch):
    intelligence = active_entitlement(TENANT, TenantProductId.INTELLIGENCE)
    service = build_service(
        TenantProductId.OPERATIONS, Collection(), monkeypatch,
        {intelligence.entitlement_id: intelligence},
    )
    with pytest.raises(service_module.TenantModuleWorkspaceError, match="MODULE_WORK_PRODUCT_NOT_ENTITLED"):
        service.daily_queue(tenant_id=TENANT, now=NOW, session=object())


def test_only_operations_and_intelligence_are_supported_products():
    with pytest.raises(service_module.TenantModuleWorkspaceError, match="MODULE_WORK_PRODUCT_UNSUPPORTED"):
        service_module.TenantModuleWorkspaceService(
            TenantModuleWorkRegistry(Collection()), TenantProductId.CRM, object(), object(),
        )
