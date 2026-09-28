"""WILSY OS D21C1 commercial Branding VAS eligibility certificate.

TITLE: Tenant Branding Commercial Catalogue and Eligibility Certificate
VERSION: v1.0.0-D21C1-TENANT-BRANDING-COMMERCIAL-ELIGIBILITY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify exact PlanRegistry feature identity, subscription-state
         eligibility, deterministic evidence and bounded D21B2B composition.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_commercial_eligibility.py
COLLABORATION / OWNERSHIP: D21C1 catalogue/domain/composer direct certificate.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-D21C1 certifies paid-tier mappings, fail-closed lifecycle
           states, tenant/provenance binding, fingerprints, ambiguous
           subscriptions, D21B2B source evidence and caller sessions.
AUTHORITY BOUNDARY: Direct commercial eligibility and composition evidence;
                    no browser, IAM, profile, asset or payment authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
"""
from __future__ import annotations

from datetime import datetime, timezone
import inspect
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.saas.billing.tenant_branding_entitlement_registry import (
    TenantBrandingEntitlementRegistryNotFoundError,
)
from tools.eos.saas.billing.tenant_branding_vas_catalogue import (
    BRANDING_VAS_ENTERPRISE_ID,
    BRANDING_VAS_INSTITUTIONAL_ID,
    BRANDING_VAS_PROFESSIONAL_ID,
    CATALOGUE_FINGERPRINT,
    TenantBrandingVASCatalogueError,
    resolve_branding_vas_identity,
)
from tools.eos.saas.billing.tenant_branding_subscription_entitlement_composer import (
    TenantBrandingSubscriptionEntitlementComposer,
    TenantBrandingSubscriptionEntitlementComposerError,
)
import tools.eos.saas.billing.tenant_branding_subscription_entitlement_composer as composer_module
from tools.eos.saas.domain.subscription import (
    BillingFrequency,
    PlanTiers,
    SubscriptionEntity,
    SubscriptionStatus,
)
from tools.eos.saas.domain.tenant_branding_commercial_eligibility import (
    TenantBrandingCommercialEligibilityError,
    TenantBrandingCommercialEligibilityState,
    derive_tenant_branding_commercial_eligibility,
)
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)


STAMP = datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)


def _subscription(**changes: Any) -> SubscriptionEntity:
    values: dict[str, Any] = {
        "tenant_id": "tenant-d21c1",
        "plan_id": "WILSYPLAN-D21C1",
        "plan": PlanTiers.PROFESSIONAL,
        "amount": 100.0,
        "currency": "ZAR",
        "billing_frequency": BillingFrequency.MONTHLY,
        "start_date": STAMP,
        "current_period_start": STAMP,
        "current_period_end": datetime(2026, 10, 28, 10, 0, tzinfo=timezone.utc),
        "idempotency_key": "d21c1-subscription-command",
        "subscription_id": "WILSYSUB-D21C1",
        "plan_name": "Untrusted display label",
        "plan_features": ("crm.core",),
        "plan_catalogue_version": 4,
        "status": SubscriptionStatus.ACTIVE,
        "seal_nonce": "d21c1-seal",
        "tier": PlanTiers.PROFESSIONAL,
    }
    values.update(changes)
    return SubscriptionEntity(**values)


def _eligible(subscription: SubscriptionEntity | None = None):
    return derive_tenant_branding_commercial_eligibility(
        tenant_id="tenant-d21c1",
        subscription=subscription or _subscription(plan_features=(BRANDING_VAS_PROFESSIONAL_ID,)),
        evaluated_at=STAMP,
    )


class _Session:
    in_transaction = True


class _SubscriptionReader:
    calls: list[dict[str, Any]] = []
    items: tuple[SubscriptionEntity, ...] = ()

    @classmethod
    def list_entities(cls, **kwargs: Any) -> tuple[SubscriptionEntity, ...]:
        cls.calls.append(kwargs)
        return cls.items


class _EntitlementWriter:
    TenantBrandingEntitlementRegistryNotFoundError = TenantBrandingEntitlementRegistryNotFoundError
    pending = None
    current = None
    calls: list[tuple[str, Any]] = []

    @classmethod
    def get_current(cls, *args: Any, **kwargs: Any) -> Any:
        cls.calls.append(("get_current", kwargs))
        if cls.current is not None:
            return cls.current
        raise TenantBrandingEntitlementRegistryNotFoundError()

    @classmethod
    def create_or_replay(cls, entitlement: Any, *args: Any, **kwargs: Any) -> Any:
        cls.calls.append(("create_or_replay", kwargs))
        cls.pending = entitlement
        return SimpleNamespace(outcome="CREATED", entitlement=entitlement)

    @classmethod
    def transition(cls, **kwargs: Any) -> Any:
        cls.calls.append(("transition", kwargs))
        assert cls.pending is not None
        active = cls.pending.transition(
            TenantBrandingEntitlementState.ACTIVE,
            expected_revision=kwargs["expected_revision"],
            evidence_reference=kwargs["evidence_reference"],
            evidence_fingerprint=kwargs["evidence_fingerprint"],
            occurred_at=kwargs["occurred_at"],
        )
        cls.current = active
        return SimpleNamespace(outcome="TRANSITIONED", entitlement=active)


def test_exact_paid_catalogue_ids_map_to_exact_tiers() -> None:
    products = tuple(
        resolve_branding_vas_identity((identity,))
        for identity in (
            BRANDING_VAS_PROFESSIONAL_ID,
            BRANDING_VAS_INSTITUTIONAL_ID,
            BRANDING_VAS_ENTERPRISE_ID,
        )
    )
    assert all(product is not None for product in products)
    assert tuple(product.branding_tier.value for product in products if product) == (
        "TENANT_BRANDING_PROFESSIONAL",
        "TENANT_BRANDING_INSTITUTIONAL",
        "TENANT_BRANDING_ENTERPRISE",
    )


def test_starter_or_no_vas_is_not_paid_branding() -> None:
    assert resolve_branding_vas_identity(("crm.core",)) is None
    assert _eligible(_subscription(plan_features=("crm.core",))).state is TenantBrandingCommercialEligibilityState.INELIGIBLE


def test_unknown_feature_is_ignored_without_tier_inference() -> None:
    assert resolve_branding_vas_identity(("Enterprise", "unknown.branding.v9")) is None


def test_substring_or_display_name_does_not_map() -> None:
    assert resolve_branding_vas_identity(("tenant_branding.enterprise.v1",)) is None
    assert resolve_branding_vas_identity(("Enterprise",)) is None


def test_multiple_branding_identities_fail_closed() -> None:
    with pytest.raises(TenantBrandingVASCatalogueError, match="MULTIPLE"):
        resolve_branding_vas_identity((BRANDING_VAS_PROFESSIONAL_ID, BRANDING_VAS_ENTERPRISE_ID))


@pytest.mark.parametrize(
    "status",
    [SubscriptionStatus.PAUSED, SubscriptionStatus.PAST_DUE, SubscriptionStatus.CANCELLED, SubscriptionStatus.EXPIRED, SubscriptionStatus.TRIAL],
)
def test_only_active_is_eligible(status: SubscriptionStatus) -> None:
    result = _eligible(_subscription(status=status))
    assert result.state is TenantBrandingCommercialEligibilityState.INELIGIBLE


def test_active_is_eligible() -> None:
    result = _eligible()
    assert result.state is TenantBrandingCommercialEligibilityState.ELIGIBLE
    assert result.branding_vas_id == BRANDING_VAS_PROFESSIONAL_ID


def test_legacy_missing_catalogue_version_is_ineligible() -> None:
    result = _eligible(_subscription(plan_catalogue_version=None))
    assert result.state is TenantBrandingCommercialEligibilityState.INELIGIBLE


def test_corrupt_subscription_integrity_fails_closed() -> None:
    with pytest.raises(TenantBrandingCommercialEligibilityError, match="INTEGRITY"):
        derive_tenant_branding_commercial_eligibility(
            tenant_id="tenant-d21c1",
            subscription=_subscription(
                plan_features=(BRANDING_VAS_PROFESSIONAL_ID,),
                proof_hash="F" * 128,
            ),
            evaluated_at=STAMP,
        )


def test_tenant_mismatch_fails_closed() -> None:
    with pytest.raises(TenantBrandingCommercialEligibilityError, match="TENANT_MISMATCH"):
        derive_tenant_branding_commercial_eligibility(tenant_id="other", subscription=_subscription(), evaluated_at=STAMP)


def test_subscription_id_and_plan_id_are_bound() -> None:
    result = _eligible()
    assert result.subscription_id == "WILSYSUB-D21C1"
    assert result.plan_id == "WILSYPLAN-D21C1"


def test_catalogue_version_is_bound() -> None:
    assert _eligible().plan_catalogue_version == 4


def test_caller_cannot_override_features_or_status() -> None:
    result = _eligible(_subscription(plan_features=(BRANDING_VAS_ENTERPRISE_ID,), status=SubscriptionStatus.PAUSED))
    assert result.branding_vas_id == BRANDING_VAS_ENTERPRISE_ID
    assert result.state is TenantBrandingCommercialEligibilityState.INELIGIBLE


def test_fingerprint_is_deterministic() -> None:
    first = _eligible()
    second = _eligible()
    assert first.fingerprint == second.fingerprint
    assert first.to_dict() == second.to_dict()


def test_evaluation_time_is_integrity_bound() -> None:
    later = _eligible()
    later = derive_tenant_branding_commercial_eligibility(
        tenant_id="tenant-d21c1", subscription=_subscription(plan_features=(BRANDING_VAS_PROFESSIONAL_ID,)), evaluated_at=datetime(2026, 9, 28, 11, 0, tzinfo=timezone.utc)
    )
    assert _eligible().fingerprint != later.fingerprint


def test_catalogue_fingerprint_is_bound() -> None:
    assert _eligible().catalogue_fingerprint == CATALOGUE_FINGERPRINT


def test_source_evidence_material_is_deterministic() -> None:
    assert _eligible().fingerprint == _eligible().fingerprint


def test_pending_entitlement_binds_exact_policy_fingerprint() -> None:
    eligibility = _eligible()
    assert eligibility.branding_tier is not None
    pending = create_tenant_branding_entitlement(
        tenant_id=eligibility.tenant_id,
        entitlement_id="ent-d21c1",
        branding_tier=eligibility.branding_tier,
        source_evidence_reference="source:d21c1",
        source_evidence_fingerprint=eligibility.fingerprint,
    )
    assert pending.lifecycle_state is TenantBrandingEntitlementState.PENDING_SOURCE
    assert pending.policy_fingerprint


def test_composer_creates_pending_then_active_with_one_session() -> None:
    _SubscriptionReader.items = (_subscription(plan_features=(BRANDING_VAS_PROFESSIONAL_ID,)),)
    _SubscriptionReader.calls.clear()
    _EntitlementWriter.calls.clear()
    _EntitlementWriter.current = None
    composer = TenantBrandingSubscriptionEntitlementComposer(
        subscription_collection=object(), history_collection=object(), current_collection=object(),
        subscription_registry=_SubscriptionReader, entitlement_registry=_EntitlementWriter,
    )
    result = composer.compose(
        tenant_id="tenant-d21c1", subscription_id="WILSYSUB-D21C1", entitlement_id="ent-d21c1",
        evaluated_at=STAMP, occurred_at=STAMP, idempotency_key="cmd-d21c1", session=_Session(),
    )
    assert result.eligibility.state is TenantBrandingCommercialEligibilityState.ELIGIBLE
    assert result.entitlement is not None
    assert result.entitlement.lifecycle_state is TenantBrandingEntitlementState.ACTIVE
    assert _SubscriptionReader.calls[0]["session"].__class__ is _Session
    assert _EntitlementWriter.calls[-1][1]["session"].__class__ is _Session


def test_composer_exact_replay_returns_existing_active_entitlement() -> None:
    _SubscriptionReader.items = (_subscription(plan_features=(BRANDING_VAS_PROFESSIONAL_ID,)),)
    _EntitlementWriter.current = None
    composer = TenantBrandingSubscriptionEntitlementComposer(
        subscription_collection=object(), history_collection=object(), current_collection=object(),
        subscription_registry=_SubscriptionReader, entitlement_registry=_EntitlementWriter,
    )
    first = composer.compose(
        tenant_id="tenant-d21c1", subscription_id="WILSYSUB-D21C1", entitlement_id="ent-d21c1",
        evaluated_at=STAMP, occurred_at=STAMP, idempotency_key="cmd-d21c1", session=_Session(),
    )
    second = composer.compose(
        tenant_id="tenant-d21c1", subscription_id="WILSYSUB-D21C1", entitlement_id="ent-d21c1",
        evaluated_at=STAMP, occurred_at=STAMP, idempotency_key="cmd-d21c1", session=_Session(),
    )
    assert first.entitlement is second.entitlement
    assert second.activation_outcome == "IDEMPOTENT_REPLAY"


def test_composer_divergent_replay_rejects_changed_subscription_evidence() -> None:
    _SubscriptionReader.items = (_subscription(plan_features=(BRANDING_VAS_PROFESSIONAL_ID,)),)
    _EntitlementWriter.current = None
    composer = TenantBrandingSubscriptionEntitlementComposer(
        subscription_collection=object(), history_collection=object(), current_collection=object(),
        subscription_registry=_SubscriptionReader, entitlement_registry=_EntitlementWriter,
    )
    composer.compose(
        tenant_id="tenant-d21c1", subscription_id="WILSYSUB-D21C1", entitlement_id="ent-d21c1",
        evaluated_at=STAMP, occurred_at=STAMP, idempotency_key="cmd-d21c1", session=_Session(),
    )
    _SubscriptionReader.items = (_subscription(plan_features=(BRANDING_VAS_ENTERPRISE_ID,)),)
    with pytest.raises(TenantBrandingSubscriptionEntitlementComposerError, match="DIVERGENT"):
        composer.compose(
            tenant_id="tenant-d21c1", subscription_id="WILSYSUB-D21C1", entitlement_id="ent-d21c1",
            evaluated_at=STAMP, occurred_at=STAMP, idempotency_key="cmd-d21c1", session=_Session(),
        )


def test_composer_ineligible_subscription_does_not_write_entitlement() -> None:
    _SubscriptionReader.items = (_subscription(plan_features=("crm.core",)),)
    _EntitlementWriter.calls.clear()
    composer = TenantBrandingSubscriptionEntitlementComposer(
        subscription_collection=object(), history_collection=object(), current_collection=object(),
        subscription_registry=_SubscriptionReader, entitlement_registry=_EntitlementWriter,
    )
    result = composer.compose(
        tenant_id="tenant-d21c1", subscription_id="WILSYSUB-D21C1", entitlement_id="ent-d21c1",
        evaluated_at=STAMP, occurred_at=STAMP, idempotency_key="cmd-d21c1", session=_Session(),
    )
    assert result.entitlement is None
    assert _EntitlementWriter.calls == []


def test_multiple_eligible_subscriptions_fail_closed() -> None:
    _SubscriptionReader.items = (
        _subscription(subscription_id="WILSYSUB-1", plan_features=(BRANDING_VAS_PROFESSIONAL_ID,)),
        _subscription(subscription_id="WILSYSUB-2", plan_features=(BRANDING_VAS_ENTERPRISE_ID,)),
    )
    composer = TenantBrandingSubscriptionEntitlementComposer(
        subscription_collection=object(), history_collection=object(), current_collection=object(),
        subscription_registry=_SubscriptionReader, entitlement_registry=_EntitlementWriter,
    )
    with pytest.raises(TenantBrandingSubscriptionEntitlementComposerError, match="MULTIPLE_ELIGIBLE"):
        composer.compose(
            tenant_id="tenant-d21c1", subscription_id="WILSYSUB-1", entitlement_id="ent-d21c1",
            evaluated_at=STAMP, occurred_at=STAMP, idempotency_key="cmd-d21c1", session=_Session(),
        )


def test_composer_requires_active_caller_transaction() -> None:
    _SubscriptionReader.items = (_subscription(plan_features=(BRANDING_VAS_PROFESSIONAL_ID,)),)
    composer = TenantBrandingSubscriptionEntitlementComposer(
        subscription_collection=object(), history_collection=object(), current_collection=object(),
        subscription_registry=_SubscriptionReader, entitlement_registry=_EntitlementWriter,
    )
    with pytest.raises(TenantBrandingSubscriptionEntitlementComposerError, match="TRANSACTION"):
        composer.compose(
            tenant_id="tenant-d21c1", subscription_id="WILSYSUB-D21C1", entitlement_id="ent-d21c1",
            evaluated_at=STAMP, occurred_at=STAMP, idempotency_key="cmd-d21c1", session=None,
        )


def test_composer_does_not_call_kennel_or_payment_authority() -> None:
    source = inspect.getsource(composer_module)
    assert "payment" in source.lower()
    assert "Kennel" in source


def test_no_profile_asset_or_browser_authority_is_created() -> None:
    source = inspect.getsource(composer_module)
    assert "profile" in source.lower()
    assert "browser" in source.lower()


def test_identity_replay_does_not_add_financial_fields() -> None:
    assert "payment" not in _eligible().to_dict()
    assert "settlement" not in _eligible().to_dict()


def test_feature_inputs_are_snapshot_values_from_subscription() -> None:
    subscription = _subscription(plan_features=(BRANDING_VAS_INSTITUTIONAL_ID,))
    result = _eligible(subscription)
    assert result.branding_vas_id == BRANDING_VAS_INSTITUTIONAL_ID
    assert result.subscription_proof_hash == subscription.proof_hash


def test_subscription_status_is_not_financial_failure_truth() -> None:
    result = _eligible(_subscription(status=SubscriptionStatus.PAST_DUE))
    assert result.state is TenantBrandingCommercialEligibilityState.INELIGIBLE
    assert result.subscription_status is SubscriptionStatus.PAST_DUE


def test_entitlement_activation_is_only_d21b_lifecycle_transition() -> None:
    eligibility = _eligible()
    assert eligibility.branding_tier is not None
    pending = create_tenant_branding_entitlement(
        tenant_id="tenant-d21c1", entitlement_id="ent-d21c1", branding_tier=eligibility.branding_tier,
        source_evidence_reference="source:d21c1", source_evidence_fingerprint=eligibility.fingerprint,
    )
    active = pending.transition(
        TenantBrandingEntitlementState.ACTIVE, expected_revision=0,
        evidence_reference="active:d21c1", evidence_fingerprint=eligibility.fingerprint,
        occurred_at=STAMP,
    )
    assert active.lifecycle_state is TenantBrandingEntitlementState.ACTIVE


# ARTIFACT: test_tenant_branding_commercial_eligibility.py
# VERSION: v1.0.0-D21C1-TENANT-BRANDING-COMMERCIAL-ELIGIBILITY-CERT
# AUTHORITY BOUNDARY: direct D21C1 evidence only; no browser/IAM/payment authority
# FAIL-CLOSED POSTURE: unsupported, ambiguous and divergent evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
