"""TITLE: WILSY OS CRM Owner Commercial Entitlement Isolation Certificate
VERSION: v1.1.0-COMPANY-OWNER-WORK-CONTINUITY-CERT
AUTHORITY: WILSY OS source-owned unit certification; no live records.
EPITOME: Verify work service uses CRM Core truth, never Legal product truth,
         and rejects absent, ambiguous or foreign CRM entitlement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_owner_commercial_workspace_service.py
COLLABORATION / OWNERSHIP: CRM source service, canonical CRM Core resolver,
                           owner work registry and source HTTP mapping.
CERTIFICATION / UPDATE DATE: 2026-11-17
CHANGELOG: v1.1.0-COMPANY-OWNER-WORK-CONTINUITY-CERT verifies the
           exact WILSY company Founder subscription permits existing
           Headquarters owner tasks after independent source IAM, while
           foreign, cancelled, ambiguous and non-Founder evidence denies.
           No synthetic role assignment, feature widening or persisted write.
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
from datetime import datetime, timedelta, timezone

from tools.eos.saas.domain.subscription import (
    BillingFrequency, PlanTiers, SubscriptionEntity, SubscriptionStatus,
)

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


def _founder_subscription(**overrides):
    """Build the exact canonical subscription with no CRM Core feature."""
    now = datetime(2026, 11, 17, 8, 0, tzinfo=timezone.utc)
    values = {
        "tenant_id": service_module.WILSY_COMPANY_TENANT_ID,
        "plan_id": "WILSYPLAN-37B8164F",
        "plan": PlanTiers.FREE,
        "amount": 0.0,
        "currency": "ZAR",
        "billing_frequency": BillingFrequency.MONTHLY,
        "start_date": now - timedelta(days=90),
        "current_period_start": now - timedelta(days=60),
        "current_period_end": now - timedelta(days=29),
        "idempotency_key": "founder-owner-work-test",
        "subscription_id": "WILSYSUB-93455E4E",
        "plan_features": ("wilsy.vas.tenant_branding.enterprise.v1",),
        "plan_catalogue_version": 1,
        "status": SubscriptionStatus.ACTIVE,
        "billing_mode": "PLATFORM",
        "seal_nonce": "founder-owner-work-test-seal",
    }
    values.update(overrides)
    return SubscriptionEntity(**values)


def test_exact_founder_owner_tasks_admitted_without_mutating_features(monkeypatch):
    """The real term classifier admits only exact Founder subscription identity."""
    service, subscriptions = _service()
    founder = _founder_subscription()
    seen = {}

    def list_entities(tenant_id, *, collection, session):
        seen.update(tenant_id=tenant_id, collection=collection, session=session)
        return (founder,)

    monkeypatch.setattr(service_module, "resolve_crm_core_entitlement", lambda *_: None)
    monkeypatch.setattr(service_module.SubscriptionRegistry, "list_entities", list_entities)
    session = object()
    service._require_entitlement(service_module.WILSY_COMPANY_TENANT_ID, session)
    assert seen == {
        "tenant_id": service_module.WILSY_COMPANY_TENANT_ID,
        "collection": subscriptions,
        "session": session,
    }
    assert founder.plan_features == ("wilsy.vas.tenant_branding.enterprise.v1",)


@pytest.mark.parametrize("overrides", [
    {"subscription_id": "SPOOFED-SUBSCRIPTION"},
    {"plan_id": "SPOOFED-PLAN"},
    {"amount": 1.0},
    {"status": SubscriptionStatus.CANCELLED},
    {"billing_mode": "CLIENT"},
])
def test_company_owner_work_rejects_nonfounder_or_inactive_evidence(monkeypatch, overrides):
    """A company tenant string alone must never grant business work access."""
    service, _ = _service()
    monkeypatch.setattr(service_module, "resolve_crm_core_entitlement", lambda *_: None)
    monkeypatch.setattr(
        service_module.SubscriptionRegistry, "list_entities",
        lambda tenant_id, *, collection, session: (_founder_subscription(**overrides),),
    )
    with pytest.raises(
        service_module.OwnerCommercialWorkspaceError,
        match="OWNER_WORK_CRM_NOT_ENTITLED|OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE",
    ):
        service._require_entitlement(service_module.WILSY_COMPANY_TENANT_ID, object())


def test_company_owner_work_rejects_ambiguous_active_subscriptions(monkeypatch):
    """Never select a convenient Founder row from ambiguous active evidence."""
    service, _ = _service()
    monkeypatch.setattr(service_module, "resolve_crm_core_entitlement", lambda *_: None)
    monkeypatch.setattr(
        service_module.SubscriptionRegistry, "list_entities",
        lambda tenant_id, *, collection, session: (
            _founder_subscription(),
            _founder_subscription(subscription_id="SECOND-ACTIVE"),
        ),
    )
    with pytest.raises(
        service_module.OwnerCommercialWorkspaceError,
        match="OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE",
    ):
        service._require_entitlement(service_module.WILSY_COMPANY_TENANT_ID, object())


# ARTIFACT: tests/unit/test_owner_commercial_workspace_service.py
# VERSION: v1.1.0-COMPANY-OWNER-WORK-CONTINUITY-CERT
# AUTHORITY BOUNDARY: Synthetic entitlement certification only; no IAM grants.
# TENANT POSTURE: Exact tenant, foreign tenant and absence cases certified.
# FAIL-CLOSED POSTURE: Missing, pending and ambiguous truth denies.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
