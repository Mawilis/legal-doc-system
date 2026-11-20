"""WILSY Founder AI reconciliation's fail-closed commercial source certificate.

TITLE: Founder WILSY AI Entitlement Reconciliation Unit Certificate
VERSION: v1.0.0-EXACT-COMMERCIAL-SOURCE-CERT
AUTHORITY: Synthetic regression evidence; Python EOS owns commercial truth.
EPITOME: Verify no Founder inference, zero-rated source matching, tier feature
         gating, dry-run abstention, and existing P4-only activation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_founder_ai_entitlement_reconciliation.py
COLLABORATION / OWNERSHIP: Founder AI reconciliation, subscription term policy,
                           canonical D57B composer, P4 entitlement lifecycle.
CERTIFICATION / UPDATE DATE: 2026-11-20
CHANGELOG: v1.0.0-EXACT-COMMERCIAL-SOURCE-CERT adds synthetic Founder
           commercial mismatch and source-owned activation certificates.
COMPLIANCE: POPIA s19; GDPR Art32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic data and no production persistence.
TENANT BOUNDARY: Exact Founder tuple; no other tenant or plan is eligible.
AUTHORITY BOUNDARY: Test only; no subscription, IAM or entitlement grants.
FINANCIAL AUTHORITY BOUNDARY: No charges or payments; Kennel EOS exclusive.
FAIL-CLOSED DECLARATION: Absence, mismatch and approval failure stop before
                         composer or activation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.saas.billing import founder_ai_entitlement_reconciliation as module
from tools.eos.saas.billing.subscription_term_policy import SubscriptionTermKind
from tools.eos.saas.billing.wilsy_ai_vas_feature_catalogue import WilsyAIVASFeatureId
from tools.eos.saas.domain.subscription import SubscriptionStatus
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlementState

FEATURE = WilsyAIVASFeatureId.INSTITUTIONAL
NOW = datetime(2026, 11, 20, 8, tzinfo=timezone.utc)


def _case(monkeypatch: pytest.MonkeyPatch, *, plan_features: tuple[str, ...] | None = None,
          subscription_features: tuple[str, ...] | None = None,
          subscription_id: str = module.FOUNDER_SUBSCRIPTION_ID) -> tuple[dict[str, Any], Any]:
    """Install isolated exact-source fakes; only domain contracts are imported."""
    features = plan_features if plan_features is not None else (
        module.BRANDING_FEATURE, FEATURE.value,
    )
    sub_features = subscription_features if subscription_features is not None else features
    observed: dict[str, Any] = {"compose_calls": 0, "activation_calls": 0}
    session = SimpleNamespace(in_transaction=True)
    plan = SimpleNamespace(
        tenant_id=module.FOUNDER_TENANT_ID,
        plan_id=module.FOUNDER_PLAN_ID,
        plan_type=SimpleNamespace(value="FOUNDER_ENTERPRISE"),
        active=True, price=0, catalogue_version=2, features=features,
    )
    subscription = SimpleNamespace(
        subscription_id=subscription_id,
        tenant_id=module.FOUNDER_TENANT_ID,
        plan_id=module.FOUNDER_PLAN_ID,
        tier=SimpleNamespace(value="FOUNDER_ENTERPRISE"),
        billing_mode="PLATFORM", amount=0, status=SubscriptionStatus.ACTIVE,
        plan_catalogue_version=2, plan_features=sub_features,
    )
    monkeypatch.setattr(module, "_canonical_plan", lambda *_: plan)
    monkeypatch.setattr(module.SubscriptionRegistry, "list_entities",
                        lambda *_, **__: (subscription,))
    monkeypatch.setattr(module, "verify_subscription_integrity", lambda value: value is subscription)
    monkeypatch.setattr(module, "evaluate_subscription_term", lambda *_, **__: SimpleNamespace(
        kind=SubscriptionTermKind.PERPETUAL_PLATFORM_OWNER))
    def compose(**kwargs: Any) -> Any:
        observed["compose_calls"] += 1
        assert kwargs["tenant_id"] == module.FOUNDER_TENANT_ID
        assert kwargs["session"] is session
        return SimpleNamespace(subscription_id=module.FOUNDER_SUBSCRIPTION_ID,
                               feature_id=FEATURE,
                               entitlement=SimpleNamespace(
                                   tenant_id=module.FOUNDER_TENANT_ID,
                                   entitlement_id="ai-founder",
                                   lifecycle_state=WilsyAIEntitlementState.PENDING_SOURCE))
    def activate(**kwargs: Any) -> Any:
        observed["activation_calls"] += 1
        assert kwargs["session"] is session
        assert kwargs["activation_evidence_fingerprint"] == "f" * 128
        return SimpleNamespace(entitlement_id="ai-founder",
                               lifecycle_state=WilsyAIEntitlementState.ACTIVE)
    monkeypatch.setattr(module, "compose_subscription_wilsy_ai_entitlement", compose)
    monkeypatch.setattr(module, "activate_wilsy_ai_reasoning_entitlement", activate)
    return observed, session


def _call(session: Any, **overrides: Any) -> module.FounderAIReconciliationResult:
    """Exercise exact preflight with no persistence unless explicitly requested."""
    kwargs: dict[str, Any] = {
        "subscription_collection": object(),
        "plan_collection": object(),
        "entitlement_collection": object(),
        "session": session,
        "idempotency_key": "founder-ai-test",
        "feature_id": FEATURE,
    }
    kwargs.update(overrides)
    return module.reconcile_founder_ai_entitlement(**kwargs)


def test_default_dry_run_does_not_provision_or_activate(monkeypatch: pytest.MonkeyPatch) -> None:
    observed, session = _case(monkeypatch)
    result = _call(session)
    assert result.applied is False
    assert result.lifecycle == "ELIGIBLE_NOT_ACTIVATED"
    assert result.feature_id is FEATURE
    assert observed == {"compose_calls": 0, "activation_calls": 0}


def test_missing_ai_feature_rejects_before_any_p4_call(monkeypatch: pytest.MonkeyPatch) -> None:
    observed, session = _case(monkeypatch, plan_features=(module.BRANDING_FEATURE,))
    with pytest.raises(module.FounderAIReconciliationError,
                       match="FOUNDER_AI_EXPLICIT_TIER_FEATURE_REQUIRED"):
        _call(session, apply=True, activation_evidence_reference="governed",
              activation_evidence_fingerprint="f" * 128, occurred_at=NOW)
    assert observed == {"compose_calls": 0, "activation_calls": 0}


def test_plan_subscription_feature_divergence_rejects(monkeypatch: pytest.MonkeyPatch) -> None:
    observed, session = _case(monkeypatch, subscription_features=(module.BRANDING_FEATURE,))
    with pytest.raises(module.FounderAIReconciliationError,
                       match="FOUNDER_AI_PLAN_SUBSCRIPTION_SNAPSHOT_DIVERGENT"):
        _call(session)
    assert observed["compose_calls"] == 0


def test_wrong_founder_subscription_is_never_reconciled(monkeypatch: pytest.MonkeyPatch) -> None:
    observed, session = _case(monkeypatch, subscription_id="OTHER-SUBSCRIPTION")
    with pytest.raises(module.FounderAIReconciliationError,
                       match="FOUNDER_AI_SUBSCRIPTION_NOT_ELIGIBLE"):
        _call(session)
    assert observed["compose_calls"] == 0


@pytest.mark.parametrize("feature", [WilsyAIVASFeatureId.STARTER, WilsyAIVASFeatureId.GROWTH])
def test_wrong_approved_tier_never_activates(
    monkeypatch: pytest.MonkeyPatch, feature: WilsyAIVASFeatureId,
) -> None:
    observed, session = _case(monkeypatch)
    with pytest.raises(module.FounderAIReconciliationError,
                       match="FOUNDER_AI_EXPLICIT_TIER_FEATURE_REQUIRED"):
        _call(session, feature_id=feature, apply=True,
              activation_evidence_reference="approved", activation_evidence_fingerprint="f" * 128,
              occurred_at=NOW)
    assert observed["compose_calls"] == 0


def test_activation_requires_evidence_and_active_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed, session = _case(monkeypatch)
    with pytest.raises(module.FounderAIReconciliationError,
                       match="FOUNDER_AI_ACTIVATION_REFERENCE_REQUIRED"):
        _call(session, apply=True)
    with pytest.raises(module.FounderAIReconciliationError,
                       match="FOUNDER_AI_ACTIVE_TRANSACTION_REQUIRED"):
        _call(SimpleNamespace(in_transaction=False))
    assert observed["compose_calls"] == 0


def test_source_approved_apply_delegates_both_writes_to_canonical_services(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed, session = _case(monkeypatch)
    result = _call(
        session, apply=True, activation_evidence_reference="institutional-approval",
        activation_evidence_fingerprint="f" * 128, occurred_at=NOW,
    )
    assert result.lifecycle == "ACTIVE"
    assert result.applied is True
    assert result.entitlement_id == "ai-founder"
    assert observed == {"compose_calls": 1, "activation_calls": 1}


# ARTIFACT: test_founder_ai_entitlement_reconciliation.py
# VERSION: v1.0.0-EXACT-COMMERCIAL-SOURCE-CERT
# AUTHORITY BOUNDARY: synthetic exact-source and P4 activation evidence
# TENANT POSTURE: no cross-tenant source or Founder alias may admit issuance
# FAIL-CLOSED POSTURE: no feature, evidence or transaction means zero writes
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
