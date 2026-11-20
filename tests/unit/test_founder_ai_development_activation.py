"""WILSY local-only Founder AI activation stage certification.

TITLE: Founder AI Development Activation Stage Unit Certificate
VERSION: v1.3.0-PRESERVED-FOUNDER-BUSINESS-FEATURES-CERT
AUTHORITY: Synthetic tests; PlanRegistry and EOS own business truth.
EPITOME: Verify no Atlas/production writes, explicit tier choice, staged
         commercial mutation, and independent source gating.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_founder_ai_development_activation.py
COLLABORATION / OWNERSHIP: Founder development activation, source registry APIs,
                           Mongo kernel's caller-owned transaction boundary.
CERTIFICATION / UPDATE DATE: 2026-11-20
CHANGELOG: v1.3.0-PRESERVED-FOUNDER-BUSINESS-FEATURES-CERT certifies that
           unrelated source-verified Founder modules are preserved rather than
           rejected by a duplicate AI-specific allowlist.
           v1.2.0-PRECONNECT-DENIAL-CERT certifies
           Atlas URI and production runtime are denied before the Mongo
           connect function executes, not only before the first write.
           v1.1.0-CANONICAL-STAGE-READBACK-CERT verifies canonical plan
           readback after a staged audited update, preventing successful
           replies for unobserved or stale plan state. v1.0.0-LOCAL-ROLLOUT-GATE-CERT adds production denial,
           local replica admission, explicit feature and dry-run proof.
COMPLIANCE: POPIA s19; GDPR Art32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: No live tenant records or credentials.
TENANT BOUNDARY: Exact Founder identity without root or tenant aliases.
AUTHORITY BOUNDARY: Unit test only; no commercial or IAM grants.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
FAIL-CLOSED POSTURE: Invalid stage, database or feature rejects before write.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.saas.billing import founder_ai_development_activation as module
from tools.eos.saas.billing.wilsy_ai_vas_feature_catalogue import WilsyAIVASFeatureId

FEATURE = WilsyAIVASFeatureId.INSTITUTIONAL


class DevelopmentDatabase:
    """Minimal synthetic namespace; no Mongo write capability."""

    name = "wilsy"

    def __getitem__(self, key: str) -> Any:
        return object()


class DevelopmentClient:
    """Expose only a safe, fake replica-set hello."""

    def __init__(self) -> None:
        self.admin = SimpleNamespace(command=lambda command: {
            "setName": "rs0", "isWritablePrimary": True,
        })


@pytest.fixture
def dev_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set exact local test transport; never use a live database."""
    monkeypatch.setenv("WILSY_ENV", "development")
    monkeypatch.setenv("MONGODB_URI", "mongodb://127.0.0.1:27017/wilsy?replicaSet=rs0")


def test_main_refuses_atlas_before_connect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The CLI must never open a socket to a production/Atlas URI."""
    import sys
    monkeypatch.setenv("WILSY_ENV", "development")
    monkeypatch.setenv("MONGODB_URI", "mongodb+srv://untrusted.invalid/wilsy")
    monkeypatch.setattr(sys, "argv", [
        "founder_ai_development_activation",
        "--stage", "plan", "--feature", FEATURE.value,
    ])
    monkeypatch.setattr(module, "connect_db",
                        lambda: pytest.fail("Must reject URI before connecting"))
    assert module.main() == 2


def test_production_environment_never_reaches_commercial_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Production env denies before a plan, subscription or P4 lookup."""
    monkeypatch.setenv("WILSY_ENV", "production")
    monkeypatch.setenv("MONGODB_URI", "mongodb://127.0.0.1:27017/wilsy")
    with pytest.raises(module.FounderAIDevelopmentActivationError,
                       match="FOUNDER_AI_DEV_ENV_REQUIRED"):
        module.execute_development_stage(
            stage="plan", feature=FEATURE,
            database=DevelopmentDatabase(), client=DevelopmentClient(), apply=True,
        )


@pytest.mark.parametrize("uri", [
    "mongodb+srv://atlas.example.invalid/wilsy",
    "mongodb://mongodb.example.invalid:27017/wilsy",
    "mongodb://localhost:27017,remote.example.invalid:27017/wilsy",
])
def test_remote_transport_denied_before_any_mutation(
    monkeypatch: pytest.MonkeyPatch, uri: str,
) -> None:
    """A remote or mixed host cannot enter the stage executor."""
    monkeypatch.setenv("WILSY_ENV", "development")
    monkeypatch.setenv("MONGODB_URI", uri)
    with pytest.raises(module.FounderAIDevelopmentActivationError,
                       match="FOUNDER_AI_LOOPBACK_"):
        module.execute_development_stage(
            stage="plan", feature=FEATURE,
            database=DevelopmentDatabase(), client=DevelopmentClient(), apply=True,
        )


def test_dry_run_reports_required_plan_change_without_writes(
    dev_env: None, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing feature is a source evolution request, never inferred access."""
    plan = SimpleNamespace(features=(module.BRANDING_FEATURE,))
    sub = SimpleNamespace()
    monkeypatch.setattr(module, "_exact_preflight", lambda *_: (plan, sub))
    monkeypatch.setattr(module.PlanRegistry, "update",
                        lambda *_, **__: pytest.fail("dry-run must never update"))
    result = module.execute_development_stage(
        stage="plan", feature=FEATURE,
        database=DevelopmentDatabase(), client=DevelopmentClient(),
    )
    assert result == {"stage": "plan", "state": "PLAN_FEATURE_UPDATE_REQUIRED", "writes": False}


def test_plan_stage_preserves_other_source_authorized_business_features(
    dev_env: None, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AI activation cannot erase unrelated canonical Founder modules."""
    other_feature = "wilsy.vas.legal.operations.enterprise.v1"
    plan = SimpleNamespace(
        features=(module.BRANDING_FEATURE, other_feature), price=0,
        plan_type=SimpleNamespace(value="FOUNDER_ENTERPRISE"),
    )
    observed: list[dict[str, Any]] = []
    monkeypatch.setattr(module, "_exact_preflight",
                        lambda *_: (plan, SimpleNamespace()))
    def update(plan_id: str, values: dict[str, Any], **options: Any) -> dict[str, Any]:
        observed.append(values)
        plan.features = tuple(values["features"])
        return {"success": True}
    monkeypatch.setattr(module.PlanRegistry, "update", update)
    result = module.execute_development_stage(
        stage="plan", feature=FEATURE,
        database=DevelopmentDatabase(), client=DevelopmentClient(), apply=True,
    )
    assert result["writes"] is True
    assert observed[0]["features"] == sorted([
        module.BRANDING_FEATURE, other_feature, FEATURE.value,
    ])


def test_already_current_plan_is_idempotent_no_write(
    dev_env: None, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A current source may not be rewritten merely because apply is present."""
    plan = SimpleNamespace(features=(module.BRANDING_FEATURE, FEATURE.value))
    monkeypatch.setattr(module, "_exact_preflight", lambda *_: (plan, SimpleNamespace()))
    monkeypatch.setattr(module.PlanRegistry, "update",
                        lambda *_, **__: pytest.fail("current source must not be updated"))
    result = module.execute_development_stage(
        stage="plan", feature=FEATURE,
        database=DevelopmentDatabase(), client=DevelopmentClient(), apply=True,
    )
    assert result["state"] == "ALREADY_CURRENT"
    assert result["writes"] is False


def test_explicit_plan_stage_calls_only_canonical_registry(
    dev_env: None, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Source evolution is delegated to PlanRegistry with exact tenant scope."""
    plan = SimpleNamespace(
        features=(module.BRANDING_FEATURE,), price=0,
        plan_type=SimpleNamespace(value="FOUNDER_ENTERPRISE"),
    )
    observed: list[tuple[Any, ...]] = []
    monkeypatch.setattr(module, "_exact_preflight", lambda *_: (plan, SimpleNamespace()))
    def update(plan_id: str, values: dict[str, Any], **options: Any) -> dict[str, Any]:
        observed.append((plan_id, values, options))
        plan.features = tuple(values["features"])
        return {"success": True}
    monkeypatch.setattr(module.PlanRegistry, "update", update)
    result = module.execute_development_stage(
        stage="plan", feature=FEATURE,
        database=DevelopmentDatabase(), client=DevelopmentClient(), apply=True,
    )
    assert observed == [
        (module.FOUNDER_PLAN_ID,
         {"features": sorted([module.BRANDING_FEATURE, FEATURE.value])},
         {"tenant_id": module.FOUNDER_TENANT_ID, "exact_tenant": True}),
    ]
    assert result["writes"] is True


def test_entitlement_step_denies_until_plan_and_subscription_match(
    dev_env: None, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No P4 admission from a plan with no explicit subscribed AI feature."""
    monkeypatch.setattr(module, "_exact_preflight", lambda *_: (
        SimpleNamespace(features=(module.BRANDING_FEATURE,)),
        SimpleNamespace(plan_features=(module.BRANDING_FEATURE,)),
    ))
    with pytest.raises(module.FounderAIDevelopmentActivationError,
                       match="FOUNDER_AI_PLAN_FEATURE_NOT_CURRENT"):
        module.execute_development_stage(
            stage="entitlement", feature=FEATURE,
            database=DevelopmentDatabase(), client=DevelopmentClient(), apply=True,
        )


# ARTIFACT: test_founder_ai_development_activation.py
# VERSION: v1.3.0-PRESERVED-FOUNDER-BUSINESS-FEATURES-CERT
# AUTHORITY BOUNDARY: synthetic development-only stage and registry checks
# TENANT POSTURE: exact Founder identity, no generic free-plan entitlement
# FAIL-CLOSED POSTURE: prod or remote transport rejects before write
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
