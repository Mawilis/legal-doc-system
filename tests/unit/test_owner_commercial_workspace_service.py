"""TITLE: WILSY OS CRM Owner Commercial Entitlement Isolation Certificate
VERSION: v1.0.0-INDEPENDENT-CRM-CORE-ADMISSION
AUTHORITY: WILSY OS source-owned unit certification; no live records.
EPITOME: Verify work service uses CRM Core truth, never Legal product truth,
         and rejects absent, ambiguous or foreign CRM entitlement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_owner_commercial_workspace_service.py
COLLABORATION / OWNERSHIP: CRM source service, canonical CRM Core resolver,
                           owner work registry and source HTTP mapping.
CERTIFICATION / UPDATE DATE: 2026-11-17
CHANGELOG: v1.0.0-INDEPENDENT-CRM-CORE-ADMISSION replaces the old Legal
           entitlement fixture with explicit positive and negative CRM
           resolver evidence and exact caller-owned session assertions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic tenant and source mocks only.
TENANT BOUNDARY: Foreign or absent CRM evidence never authorizes work.
AUTHORITY BOUNDARY: Tests grant neither CRM permission nor subscription;
                    the real subscription and IAM registries remain authoritative.
TRANSACTION / IDEMPOTENCY BOUNDARY: Supplied session is unchanged; no writes.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS alone executes financial acts.
FAIL-CLOSED POSTURE: Missing, malformed, ambiguous or foreign evidence rejects.
"""
from types import SimpleNamespace

import pytest

from tools.eos.crm.domain.crm_core_entitlement import CrmCoreEntitlementState
from tools.eos.crm.persistence.owner_commercial_work_registry import OwnerCommercialWorkRegistry
from tools.eos.crm.service import owner_commercial_workspace_service as service_module
from tools.eos.crm.service.crm_core_entitlement_resolver import CrmCoreEntitlementResolverError


def _service():
    """Construct an isolated source with distinct synthetic dependency handles."""
    registry = OwnerCommercialWorkRegistry(object())
    subscriptions = object()
    history = object()
    current = object()
    service = service_module.OwnerCommercialWorkspaceService(
        registry, subscriptions, history, current,
    )
    return service, subscriptions


def test_owner_work_requires_exact_active_crm_core_without_legal_dependency(monkeypatch):
    """Forward exact tenant, collection, and session only to CRM authority."""
    service, subscriptions = _service()
    observed = {}

    def resolve(tenant_id, subscription_collection, session):
        observed.update(tenant=tenant_id, subscriptions=subscription_collection, session=session)
        return SimpleNamespace(
            tenant_id=tenant_id,
            lifecycle_state=CrmCoreEntitlementState.ACTIVE,
        )

    monkeypatch.setattr(service_module, "resolve_crm_core_entitlement", resolve)
    session = object()
    service._require_entitlement("WILSYTENANT-CERT", session)
    assert observed == {
        "tenant": "WILSYTENANT-CERT",
        "subscriptions": subscriptions,
        "session": session,
    }
    assert not hasattr(service_module, "resolve_legal_commercial_context")


def test_missing_crm_core_remains_denied(monkeypatch):
    """Founder subscription classification cannot invent CRM Core availability."""
    service, _ = _service()
    monkeypatch.setattr(
        service_module, "resolve_crm_core_entitlement",
        lambda tenant_id, subscription_collection, session: None,
    )
    with pytest.raises(
        service_module.OwnerCommercialWorkspaceError,
        match="OWNER_WORK_CRM_NOT_ENTITLED",
    ):
        service._require_entitlement("WILSYTENANT-CERT", object())


@pytest.mark.parametrize("invalid", [
    SimpleNamespace(tenant_id="OTHER-TENANT", lifecycle_state=CrmCoreEntitlementState.ACTIVE),
    SimpleNamespace(tenant_id="WILSYTENANT-CERT", lifecycle_state=CrmCoreEntitlementState.PENDING_SOURCE),
])
def test_foreign_or_inactive_crm_core_rejects(monkeypatch, invalid):
    """Cross-tenant or pending evidence never promotes a source work queue."""
    service, _ = _service()
    monkeypatch.setattr(
        service_module, "resolve_crm_core_entitlement",
        lambda tenant_id, subscription_collection, session: invalid,
    )
    with pytest.raises(
        service_module.OwnerCommercialWorkspaceError,
        match="OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE",
    ):
        service._require_entitlement("WILSYTENANT-CERT", object())


def test_ambiguous_crm_subscription_evidence_fails_closed(monkeypatch):
    """Resolver uncertainty cannot become a positive CRM entitlement."""
    service, _ = _service()

    def ambiguous(tenant_id, subscription_collection, session):
        raise CrmCoreEntitlementResolverError("CRM_CORE_ENTITLEMENT_SUBSCRIPTION_AMBIGUOUS")

    monkeypatch.setattr(service_module, "resolve_crm_core_entitlement", ambiguous)
    with pytest.raises(
        service_module.OwnerCommercialWorkspaceError,
        match="OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE",
    ):
        service._require_entitlement("WILSYTENANT-CERT", object())


# ARTIFACT: tests/unit/test_owner_commercial_workspace_service.py
# VERSION: v1.0.0-INDEPENDENT-CRM-CORE-ADMISSION
# AUTHORITY BOUNDARY: Synthetic entitlement certification only; no IAM grants.
# TENANT POSTURE: Exact tenant, foreign tenant and absence cases certified.
# FAIL-CLOSED POSTURE: Missing, pending and ambiguous truth denies.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
