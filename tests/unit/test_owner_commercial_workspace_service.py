from types import SimpleNamespace

from tools.eos.crm.persistence.owner_commercial_work_registry import OwnerCommercialWorkRegistry
from tools.eos.crm.service import owner_commercial_workspace_service as service_module


def test_owner_workspace_service_retains_all_legal_entitlement_dependencies(monkeypatch):
    registry = OwnerCommercialWorkRegistry(object())
    subscriptions = object()
    entitlement_history = object()
    entitlement_current = object()
    service = service_module.OwnerCommercialWorkspaceService(
        registry,
        subscriptions,
        entitlement_history,
        entitlement_current,
    )
    observed = {}

    def resolve(tenant_id, subscription_collection, history_collection, current_collection, *, session):
        observed.update({
            "tenant_id": tenant_id,
            "subscriptions": subscription_collection,
            "history": history_collection,
            "current": current_collection,
            "session": session,
        })
        return SimpleNamespace(
            tenant_id=tenant_id,
            product_available=True,
            subscription_status=object(),
        )

    monkeypatch.setattr(service_module, "resolve_legal_commercial_context", resolve)
    session = object()
    service._require_entitlement("WILSYTENANT-CERT", session)

    assert observed == {
        "tenant_id": "WILSYTENANT-CERT",
        "subscriptions": subscriptions,
        "history": entitlement_history,
        "current": entitlement_current,
        "session": session,
    }
