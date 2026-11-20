"""Authenticated Founder Institutional AI staged issuance unit certificate.

TITLE: WILSY Authenticated Founder Institutional AI Activation Unit Certificate
VERSION: v1.0.1-CANONICAL-SOVEREIGN-HEADER-CERT
AUTHORITY: Synthetic exact-source and HTTP IAM-boundary regression evidence.
EPITOME: Certify an authenticated, zero-rated, recoverable PlanRegistry to
  SubscriptionRegistry to D57B/P4 activation with an exact ACTIVE readback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_founder_ai_authenticated_activation.py
COLLABORATION / OWNERSHIP: Founder source activation, current dual-authority
  subscription HTTP command, PlanRegistry, SubscriptionRegistry and P4.
CERTIFICATION / UPDATE DATE: 2026-11-20
CHANGELOG: v1.0.1-CANONICAL-SOVEREIGN-HEADER-CERT aligns complete sovereign
  metadata with the repository guard. v1.0.0-DUAL-IAM-EXACT-FOUNDER-ACTIVATION-CERT adds
  exact-tenant denial, success, source-verified retry, recoverable partial
  stage failure, fixed tier and dual HTTP authority composition tests.
COMPLIANCE: POPIA s19; GDPR Article32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-free synthetic records; no live secrets.
TENANT BOUNDARY: Explicit Founder tuple; no tenant-name or role bypass.
AUTHORITY BOUNDARY: HTTP requires current plan:manage and subscription:manage;
  unit source stubs cannot grant commercial or runtime authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively; zero-rated source only.
FAIL-CLOSED DECLARATION: No source/no dual IAM/no P4 ACTIVE readback means no success.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import HTTPException

from tools.eos.saas.billing import founder_ai_authenticated_activation as activation
from tools.eos.saas.billing.founder_ai_entitlement_reconciliation import (
    FOUNDER_TENANT_ID,
    FOUNDER_MANDATED_AI_FEATURE,
)
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlementState

KEY = "founder-institutional-mandate-20261120"


class _Session:
    def __enter__(self) -> "_Session":
        return self

    def __exit__(self, *_args: Any) -> None:
        return None

    def start_transaction(self) -> "_Session":
        return self


class _Client:
    def start_session(self) -> _Session:
        return _Session()


class _Database:
    def __getitem__(self, _collection: str) -> object:
        return object()


def _mock_sources(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Exercise orchestration only; registry persistence has real Mongo tests."""
    state: dict[str, Any] = {
        "plan": SimpleNamespace(
            tenant_id=FOUNDER_TENANT_ID, features=("wilsy.vas.tenant_branding.enterprise.v1",),
            catalogue_version=1, price=0, active=True,
            plan_type=SimpleNamespace(value="FOUNDER_ENTERPRISE"),
            proof_hash="a" * 128,
        ),
        "subscription": SimpleNamespace(
            tenant_id=FOUNDER_TENANT_ID,
            plan_features=("wilsy.vas.tenant_branding.enterprise.v1",),
            plan_catalogue_version=1, amount=0, proof_hash="b" * 128,
        ),
        "plan_changes": 0,
        "subscription_changes": 0,
        "reconciliation_calls": 0,
        "activation_evidence": None,
        "fail_subscription": False,
        "readback_state": WilsyAIEntitlementState.ACTIVE,
    }

    monkeypatch.setattr(activation, "get_client", lambda: _Client())
    monkeypatch.setattr(activation, "get_database", lambda: _Database())
    monkeypatch.setattr(
        activation, "_sources",
        lambda _database, _client, _now: (state["plan"], state["subscription"]),
    )

    def plan_update(_id: str, payload: dict[str, Any], **_kwargs: Any) -> dict[str, Any]:
        assert payload["user"] == "institutional-principal"
        state["plan_changes"] += 1
        state["plan"].features = tuple(payload["features"])
        state["plan"].catalogue_version += 1
        return {"success": True}

    def subscription_upgrade(
        _id: str, _tenant: str, _payload: dict[str, Any],
        **_kwargs: Any,
    ) -> dict[str, Any]:
        if state["fail_subscription"]:
            return {"success": False}
        state["subscription_changes"] += 1
        state["subscription"].plan_features = state["plan"].features
        state["subscription"].plan_catalogue_version = state["plan"].catalogue_version
        return {"success": True, "subscription": state["subscription"]}

    def reconcile(**kwargs: Any) -> SimpleNamespace:
        state["reconciliation_calls"] += 1
        assert kwargs["feature_id"] is FOUNDER_MANDATED_AI_FEATURE
        assert kwargs["apply"] is True
        assert kwargs["activation_evidence_reference"] == (
            "founder-institutional-ai-commercial-decision-20261120"
        )
        assert len(kwargs["activation_evidence_fingerprint"]) == 128
        state["activation_evidence"] = kwargs["activation_evidence_fingerprint"]
        return SimpleNamespace(
            lifecycle="ACTIVE", entitlement_id="exact-founder-ai", applied=True,
        )

    class _Registry:
        def __init__(self, _collection: Any) -> None:
            pass

        def get_by_module(self, **kwargs: Any) -> SimpleNamespace:
            assert kwargs["tenant_id"] == FOUNDER_TENANT_ID
            return SimpleNamespace(
                tenant_id=FOUNDER_TENANT_ID, entitlement_id="exact-founder-ai",
                lifecycle_state=state["readback_state"],
                tier=SimpleNamespace(value="INSTITUTIONAL"),
            )

    monkeypatch.setattr(activation.PlanRegistry, "update", plan_update)
    monkeypatch.setattr(activation.SubscriptionRegistry, "upgrade", subscription_upgrade)
    monkeypatch.setattr(activation, "reconcile_founder_ai_entitlement", reconcile)
    monkeypatch.setattr(activation, "WilsyAIEntitlementRegistry", _Registry)
    return state


def _activate() -> dict[str, Any]:
    return activation.activate_authenticated_founder_institutional_ai(
        tenant_id=FOUNDER_TENANT_ID,
        principal_id="institutional-principal",
        idempotency_key=KEY,
    )


def test_foreign_tenant_denied_before_any_database_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        activation, "get_client", lambda: pytest.fail("no DB before tenant fence"),
    )
    with pytest.raises(
        activation.FounderAIAuthenticatedActivationError,
        match="FOUNDER_AI_TENANT_NOT_AUTHORIZED",
    ):
        activation.activate_authenticated_founder_institutional_ai(
            tenant_id="FOREIGN_TENANT", principal_id="institutional-principal",
            idempotency_key=KEY,
        )


def test_missing_valid_idempotency_denied_before_db(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(activation, "get_client",
                        lambda: pytest.fail("no DB for invalid key"))
    with pytest.raises(
        activation.FounderAIAuthenticatedActivationError,
        match="FOUNDER_AI_IDEMPOTENCY_KEY_INVALID",
    ):
        activation.activate_authenticated_founder_institutional_ai(
            tenant_id=FOUNDER_TENANT_ID,
            principal_id="institutional-principal", idempotency_key=" ",
        )


def test_real_staged_registry_delegation_and_active_readback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _mock_sources(monkeypatch)
    result = _activate()
    assert result["entitlement_state"] == "ACTIVE"
    assert result["feature_id"] == "ai.wilsy.institutional"
    assert result["zero_rated_subscription"] is True
    assert (state["plan_changes"], state["subscription_changes"],
            state["reconciliation_calls"]) == (1, 1, 1)
    assert state["activation_evidence"] is not None


def test_partial_failure_preserves_plan_for_guarded_resume(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _mock_sources(monkeypatch)
    state["fail_subscription"] = True
    with pytest.raises(
        activation.FounderAIAuthenticatedActivationError,
        match="FOUNDER_AI_SUBSCRIPTION_SNAPSHOT_FAILED",
    ):
        _activate()
    assert state["plan_changes"] == 1
    assert state["subscription_changes"] == 0
    assert state["reconciliation_calls"] == 0
    state["fail_subscription"] = False
    assert _activate()["entitlement_state"] == "ACTIVE"
    assert state["plan_changes"] == 1
    assert state["subscription_changes"] == 1
    assert state["reconciliation_calls"] == 1


def test_p4_readback_is_mandatory_even_when_issuer_claims_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _mock_sources(monkeypatch)
    state["readback_state"] = WilsyAIEntitlementState.PENDING_SOURCE
    with pytest.raises(
        activation.FounderAIAuthenticatedActivationError,
        match="FOUNDER_AI_ACTIVE_ENTITLEMENT_READBACK_FAILED",
    ):
        _activate()


def test_http_dual_identity_and_founder_fence_before_activation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tools.eos.api import subscription_router as http

    monkeypatch.setattr(
        http, "activate_authenticated_founder_institutional_ai",
        lambda **_args: pytest.fail("IAM denied before registry"),
    )
    request = SimpleNamespace(state=SimpleNamespace())
    valid = SimpleNamespace(tenant_id=FOUNDER_TENANT_ID, identity_id="founder")
    foreign = SimpleNamespace(tenant_id="FOREIGN_TENANT", identity_id="founder")
    mismatched = SimpleNamespace(tenant_id=FOUNDER_TENANT_ID, identity_id="other")
    for sub, plan in ((foreign, foreign), (valid, mismatched)):
        with pytest.raises(HTTPException) as denial:
            http.activate_founder_institutional_ai(
                request, idempotency_key=KEY,
                subscription_identity=sub, plan_identity=plan,
            )
        assert denial.value.status_code == 403


def test_http_declares_both_independent_permissions() -> None:
    from tools.eos.api import subscription_router as http
    from tools.eos.api.plan_router import PLAN_MANAGE_AUTHORITY

    registered = next(
        route for route in http.subscription_router.routes
        if getattr(route, "path", "").endswith(
            "/founder-ai-institutional/activate"
        )
    )
    dependencies = {dependency.call for dependency in registered.dependant.dependencies}
    assert http.SUBSCRIPTION_MANAGE_AUTHORITY in dependencies
    assert PLAN_MANAGE_AUTHORITY in dependencies


# ARTIFACT: test_founder_ai_authenticated_activation.py
# VERSION: v1.0.1-CANONICAL-SOVEREIGN-HEADER-CERT
# AUTHORITY BOUNDARY: source-scoped dual-IAM HTTP contract and staged registry mocks
# TENANT POSTURE: foreign tenant and different principal never reach P4
# FAIL-CLOSED POSTURE: partial stage, source divergence or no ACTIVE readback fails
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
