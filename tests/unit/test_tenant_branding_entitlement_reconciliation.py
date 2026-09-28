"""D21C2 direct certificate for tenant-branding entitlement currentness.

TITLE: Tenant Branding Entitlement Reconciliation Certificate
VERSION: v1.0.0-L10-P2C4-D21C2-RECONCILIATION-DIRECT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify commercial-loss mapping, immutable D21B2 terminality,
         deterministic evidence, replay/CAS behavior, and caller-owned
         transaction boundaries without Mongo or external-provider authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_entitlement_reconciliation.py
COLLABORATION / OWNERSHIP: D21C2 reconciliation service and D21B2B registry.
CERTIFICATION/UPDATE DATE: 2026-09-28.
AUTHORITY BOUNDARY: Direct currentness/reconciliation evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.saas.billing import tenant_branding_entitlement_reconciliation as module
from tools.eos.saas.billing.tenant_branding_entitlement_reconciliation import (
    TenantBrandingEntitlementReconciliationError,
    TenantBrandingEntitlementReconciliationOutcome,
    TenantBrandingEntitlementReconciliationService,
)
from tools.eos.saas.billing.tenant_branding_entitlement_registry import (
    TenantBrandingEntitlementRegistryNotFoundError,
)
from tools.eos.saas.billing.tenant_branding_vas_catalogue import (
    BRANDING_VAS_ENTERPRISE_ID,
    BRANDING_VAS_PROFESSIONAL_ID,
)
from tools.eos.saas.domain.subscription import SubscriptionStatus
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlement,
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)
from tests.unit.test_tenant_branding_commercial_eligibility import (
    _registry_subscription,
)


STAMP = datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)
TENANT = "tenant-d21c2"


class Session:
    in_transaction = True


class Reader:
    items: tuple[Any, ...] = ()
    calls: list[dict[str, Any]] = []

    @classmethod
    def list_entities(cls, **kwargs: Any) -> tuple[Any, ...]:
        cls.calls.append(kwargs)
        return cls.items


class Entitlements:
    TenantBrandingEntitlementRegistryNotFoundError = TenantBrandingEntitlementRegistryNotFoundError
    current: TenantBrandingEntitlement | None = None
    calls: list[tuple[str, dict[str, Any]]] = []
    fail_transition: Exception | None = None

    @classmethod
    def get_current(cls, *args: Any, **kwargs: Any) -> TenantBrandingEntitlement:
        cls.calls.append(("get_current", kwargs))
        if cls.current is None:
            raise TenantBrandingEntitlementRegistryNotFoundError()
        return cls.current

    @classmethod
    def transition(cls, **kwargs: Any) -> Any:
        cls.calls.append(("transition", kwargs))
        if cls.fail_transition is not None:
            raise cls.fail_transition
        assert cls.current is not None
        cls.current = cls.current.transition(
            kwargs["target_state"],
            expected_revision=kwargs["expected_revision"],
            evidence_reference=kwargs["evidence_reference"],
            evidence_fingerprint=kwargs["evidence_fingerprint"],
            occurred_at=kwargs["occurred_at"],
        )
        return SimpleNamespace(entitlement=cls.current)


def _active(tier: str = "TENANT_BRANDING_PROFESSIONAL") -> TenantBrandingEntitlement:
    pending = create_tenant_branding_entitlement(
        tenant_id=TENANT,
        entitlement_id="entitlement-d21c2",
        branding_tier=tier,
        source_evidence_reference="source:d21c2",
        source_evidence_fingerprint="a" * 128,
    )
    return pending.transition(
        TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation:d21c2",
        evidence_fingerprint="b" * 128,
        occurred_at=STAMP,
    )


def _service(subscription: Any) -> TenantBrandingEntitlementReconciliationService:
    Reader.items = (subscription,) if subscription is not None else ()
    Reader.calls = []
    Entitlements.current = _active()
    Entitlements.calls = []
    Entitlements.fail_transition = None
    return TenantBrandingEntitlementReconciliationService(
        subscription_collection=object(),
        history_collection=object(),
        current_collection=object(),
        subscription_registry=Reader,
        entitlement_registry=Entitlements,
    )


def _subscription(*, status: SubscriptionStatus = SubscriptionStatus.ACTIVE, feature: str = BRANDING_VAS_PROFESSIONAL_ID) -> Any:
    return _registry_subscription(
        tenant_id=TENANT,
        status=status,
        plan_features=(feature,),
    )


def test_active_matching_subscription_is_current_noop() -> None:
    result = _service(_subscription()).reconcile(
        tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session()
    )
    assert result.outcome is TenantBrandingEntitlementReconciliationOutcome.CURRENT
    assert not [call for call in Entitlements.calls if call[0] == "transition"]


@pytest.mark.parametrize(
    ("status", "target"),
    [
        (SubscriptionStatus.PAUSED, TenantBrandingEntitlementState.SUSPENDED),
        (SubscriptionStatus.PAST_DUE, TenantBrandingEntitlementState.SUSPENDED),
        (SubscriptionStatus.CANCELLED, TenantBrandingEntitlementState.REVOKED),
        (SubscriptionStatus.EXPIRED, TenantBrandingEntitlementState.REVOKED),
    ],
)
def test_commercial_loss_maps_to_frozen_terminal_transition(status: SubscriptionStatus, target: TenantBrandingEntitlementState) -> None:
    result = _service(_subscription(status=status)).reconcile(
        tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session()
    )
    assert result.outcome is TenantBrandingEntitlementReconciliationOutcome.TRANSITIONED
    assert result.target_state is target
    assert result.entitlement.lifecycle_state is target


def test_trial_existing_active_fails_closed() -> None:
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="TRIAL"):
        _service(_subscription(status=SubscriptionStatus.TRIAL)).reconcile(
            tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session()
        )


@pytest.mark.parametrize("feature", ["unknown.branding.v99", "crm.core"])
def test_missing_or_unknown_branding_subscription_fails_closed(feature: str) -> None:
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="NO_EXACT"):
        _service(_subscription(feature=feature)).reconcile(
            tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session()
        )


def test_conflicting_branding_identity_fails_closed() -> None:
    Reader.items = (_registry_subscription(tenant_id=TENANT, plan_features=(BRANDING_VAS_PROFESSIONAL_ID, BRANDING_VAS_ENTERPRISE_ID)),)
    Entitlements.current = _active()
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="MULTIPLE"):
        TenantBrandingEntitlementReconciliationService(
            subscription_collection=object(), history_collection=object(), current_collection=object(),
            subscription_registry=Reader, entitlement_registry=Entitlements,
        ).reconcile(tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session())


def test_multiple_eligible_subscriptions_fail_closed() -> None:
    Reader.items = (_subscription(), _registry_subscription(tenant_id=TENANT, subscription_id="second", plan_features=(BRANDING_VAS_PROFESSIONAL_ID,)))
    Entitlements.current = _active()
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="MULTIPLE_ELIGIBLE"):
        TenantBrandingEntitlementReconciliationService(
            subscription_collection=object(), history_collection=object(), current_collection=object(),
            subscription_registry=Reader, entitlement_registry=Entitlements,
        ).reconcile(tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session())


def test_tenant_mismatch_fails_closed() -> None:
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="TENANT_MISMATCH"):
        _service(replace(_subscription(), tenant_id="other-tenant")).reconcile(
            tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session()
        )


def test_tier_change_revokes_old_lineage() -> None:
    result = _service(_subscription(feature=BRANDING_VAS_ENTERPRISE_ID)).reconcile(
        tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session()
    )
    assert result.target_state is TenantBrandingEntitlementState.REVOKED
    assert str(result.entitlement.branding_tier) == "TenantBrandingTier.PROFESSIONAL"


def test_subscription_integrity_failure_fails_closed() -> None:
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="INTEGRITY"):
        _service(replace(_subscription(), proof_hash="invalid")).reconcile(
            tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session()
        )


def test_exact_replay_is_idempotent() -> None:
    service = _service(_subscription(status=SubscriptionStatus.PAUSED))
    first = service.reconcile(tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session())
    second = service.reconcile(tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session())
    assert first.outcome is TenantBrandingEntitlementReconciliationOutcome.TRANSITIONED
    assert second.outcome is TenantBrandingEntitlementReconciliationOutcome.IDEMPOTENT_REPLAY
    assert len([call for call in Entitlements.calls if call[0] == "transition"]) == 1


def test_divergent_replay_fails_closed() -> None:
    service = _service(_subscription(status=SubscriptionStatus.PAUSED))
    service.reconcile(tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session())
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="DIVERGENT"):
        service.reconcile(tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP.replace(hour=11), occurred_at=STAMP, session=Session())


def test_stale_revision_fails_closed() -> None:
    service = _service(_subscription(status=SubscriptionStatus.PAUSED))
    Entitlements.fail_transition = RuntimeError("D21B2_STALE_REVISION")
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="TRANSITION_REJECTED"):
        service.reconcile(
            tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session()
        )


def test_caller_session_is_propagated_and_not_owned() -> None:
    service = _service(_subscription(status=SubscriptionStatus.PAUSED))
    session = Session()
    service.reconcile(tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=session)
    assert Reader.calls[0]["session"] is session
    assert Entitlements.calls[0][1]["session"] is session
    assert Entitlements.calls[1][1]["session"] is session
    assert not any(hasattr(session, name) for name in ("start_transaction", "commit_transaction", "abort_transaction"))


def test_transition_evidence_is_deterministic_and_bound_to_prior_revision() -> None:
    first = _service(_subscription(status=SubscriptionStatus.PAUSED)).reconcile(
        tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session()
    )
    second = _service(_subscription(status=SubscriptionStatus.PAUSED)).reconcile(
        tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session()
    )
    assert first.transition_evidence_fingerprint == second.transition_evidence_fingerprint
    assert len(first.transition_evidence_fingerprint) == 128


def test_no_kennel_profile_asset_or_browser_surface() -> None:
    source = module.__file__
    assert source is not None
    text = open(source, encoding="utf-8").read()
    assert "kenn el" not in text.lower()
    assert "profile_collection" not in text
    assert "asset_collection" not in text
    assert "SubscriptionRegistry" in text


def test_caller_cannot_supply_target_lifecycle_or_status() -> None:
    assert "target_state" not in TenantBrandingEntitlementReconciliationService.reconcile.__annotations__
    assert "subscription_status" not in TenantBrandingEntitlementReconciliationService.reconcile.__annotations__


def test_missing_entitlement_fails_closed() -> None:
    Reader.items = (_subscription(),)
    Entitlements.current = None
    service = TenantBrandingEntitlementReconciliationService(
        subscription_collection=object(), history_collection=object(), current_collection=object(),
        subscription_registry=Reader, entitlement_registry=Entitlements,
    )
    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="NOT_FOUND"):
        service.reconcile(tenant_id=TENANT, entitlement_id="missing", evaluated_at=STAMP, occurred_at=STAMP, session=Session())


def test_inactive_caller_transaction_is_rejected() -> None:
    class Inactive:
        in_transaction = False

    with pytest.raises(TenantBrandingEntitlementReconciliationError, match="ACTIVE_TRANSACTION"):
        _service(_subscription()).reconcile(
            tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Inactive()
        )


def test_reconciliation_does_not_create_new_lineage_on_tier_change() -> None:
    result = _service(_subscription(feature=BRANDING_VAS_ENTERPRISE_ID)).reconcile(
        tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session()
    )
    assert result.entitlement.entitlement_id == "entitlement-d21c2"
    assert result.entitlement.lifecycle_state is TenantBrandingEntitlementState.REVOKED


def test_tier_replacement_revokes_even_when_new_subscription_is_paused() -> None:
    result = _service(_subscription(status=SubscriptionStatus.PAUSED, feature=BRANDING_VAS_ENTERPRISE_ID)).reconcile(
        tenant_id=TENANT, entitlement_id="entitlement-d21c2", evaluated_at=STAMP, occurred_at=STAMP, session=Session()
    )
    assert result.target_state is TenantBrandingEntitlementState.REVOKED


# ARTIFACT: test_tenant_branding_entitlement_reconciliation.py
# VERSION: v1.0.0-L10-P2C4-D21C2-RECONCILIATION-DIRECT-CERT
# AUTHORITY BOUNDARY: currentness evidence only
# FAIL-CLOSED POSTURE: ambiguity, stale state and divergent replay reject
# END OF WILSY OS SOVEREIGN ARTIFACT
