"""WILSY OS M13-P3 direct certificate for the Python WILSY AI policy owner.

TITLE: WILSY AI Commercial Policy Direct Certificate
VERSION: v1.0.0-M13-P3
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exact Node-policy migration, integer-ZAR semantics, immutable
         descriptors, deterministic SHA3-512 evidence, and authority firewall.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_commercial_policy.py
COLLABORATION / OWNERSHIP: Direct certificate for the Python commercial-policy
                            owner; PlanRegistry and WilsyAIVASAccess remain
                            separate downstream/base-catalogue authorities.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M13-P3 certifies all three migrated tiers, strict validation,
           deterministic fingerprints, immutability, and no-entitlement posture.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Pure in-process descriptors; no secrets, network,
                             persistence, providers, KMS, or external clients.
TENANT BOUNDARY: Catalogue facts do not grant tenant entitlement or activation.
AUTHORITY BOUNDARY: Policy description and integrity evidence only; no metering,
                    billing, charging, execution, settlement, or action approval.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and
                               settlement truth.
FAIL-CLOSED DECLARATION: Unknown, malformed, altered, or caller-overridden
                         policy data rejects deterministically.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import inspect
import json
from typing import Any

import pytest

from tools.eos.saas.billing.wilsy_ai_commercial_policy import (
    POLICIES,
    POLICY_IDENTITY,
    POLICY_SCHEMA,
    VERSION,
    WilsyAICommercialPolicy,
    WilsyAICommercialPolicyError,
    WilsyAITier,
    get_wilsy_ai_commercial_policy,
    hydrate_wilsy_ai_commercial_policy,
)


EXPECTED = {
    WilsyAITier.STARTER: {
        "label": "Wilsy AI Starter",
        "currency": "ZAR",
        "monthly_price_minor": 49_900,
        "setup_price_minor": 0,
        "daily_request_limit": 35,
        "monthly_automation_limit": 750,
        "analyst_seats": 1,
        "max_autonomous_actions_per_day": 5,
        "approval_threshold_minor": 250_000,
        "overage_price_per_request_minor": 300,
        "value_promise": "Daily admin reduction, inbox triage, customer follow-ups and document capture.",
    },
    WilsyAITier.GROWTH: {
        "label": "Wilsy AI Growth",
        "currency": "ZAR",
        "monthly_price_minor": 149_900,
        "setup_price_minor": 75_000,
        "daily_request_limit": 120,
        "monthly_automation_limit": 3_000,
        "analyst_seats": 3,
        "max_autonomous_actions_per_day": 25,
        "approval_threshold_minor": 1_000_000,
        "overage_price_per_request_minor": 200,
        "value_promise": "Owner-grade cash, margin, stock and customer-work automation with controlled execution.",
    },
    WilsyAITier.INSTITUTIONAL: {
        "label": "Wilsy AI Institutional",
        "currency": "ZAR",
        "monthly_price_minor": 549_900,
        "setup_price_minor": 250_000,
        "daily_request_limit": 450,
        "monthly_automation_limit": 12_000,
        "analyst_seats": 12,
        "max_autonomous_actions_per_day": 100,
        "approval_threshold_minor": 5_000_000,
        "overage_price_per_request_minor": 100,
        "value_promise": "Executive command automation, compliance evidence, industry playbooks and audit exports.",
    },
}


def test_exact_node_policy_values_are_integer_zar_minor_units() -> None:
    for tier, expected in EXPECTED.items():
        policy = get_wilsy_ai_commercial_policy(tier)
        actual = policy.to_dict()
        for field, value in expected.items():
            assert actual[field] == value
        assert all(
            isinstance(actual[field], int)
            for field in (
                "monthly_price_minor",
                "setup_price_minor",
                "approval_threshold_minor",
                "overage_price_per_request_minor",
            )
        )


def test_policy_identity_schema_and_fingerprint_are_explicit_and_deterministic() -> None:
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.GROWTH)
    payload = policy.to_dict()
    assert payload["schema"] == POLICY_SCHEMA
    assert payload["policy_identity"] == POLICY_IDENTITY
    assert payload["policy_version"] == VERSION
    assert isinstance(policy.fingerprint, str)
    assert len(policy.fingerprint) == 128
    assert policy.fingerprint == policy.fingerprint.lower()
    assert hydrate_wilsy_ai_commercial_policy(dict(reversed(tuple(payload.items())))) == policy
    assert json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def test_unknown_tier_and_latest_selection_fail_closed() -> None:
    for value in ("UNKNOWN", "LATEST", "", None):
        with pytest.raises(WilsyAICommercialPolicyError, match="UNKNOWN_TIER"):
            get_wilsy_ai_commercial_policy(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("currency", "USD", "CURRENCY_UNSUPPORTED"),
        ("monthly_price_minor", 49_900.0, "MONTHLY_PRICE_INVALID"),
        ("setup_price_minor", -1, "SETUP_PRICE_INVALID"),
        ("daily_request_limit", 0, "DAILY_LIMIT_INVALID"),
        ("monthly_automation_limit", 0, "MONTHLY_AUTOMATION_INVALID"),
        ("analyst_seats", 0, "ANALYST_SEATS_INVALID"),
        ("max_autonomous_actions_per_day", 0, "AUTONOMOUS_LIMIT_INVALID"),
    ],
)
def test_invalid_currency_money_and_capacities_fail_closed(
    field: str,
    value: object,
    error: str,
) -> None:
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    with pytest.raises(WilsyAICommercialPolicyError, match=error):
        replace(policy, **{field: value})


def test_caller_commercial_override_and_identity_override_fail_closed() -> None:
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    with pytest.raises(WilsyAICommercialPolicyError, match="CALLER_VALUE_OVERRIDE"):
        replace(policy, monthly_price_minor=99_900)
    with pytest.raises(WilsyAICommercialPolicyError, match="POLICY_IDENTITY_INVALID"):
        replace(policy, policy_version="v9.0.0")


def test_strict_hydration_rejects_missing_extra_and_corrupt_fingerprint() -> None:
    payload = get_wilsy_ai_commercial_policy(WilsyAITier.GROWTH).to_dict()
    missing = dict(payload)
    del missing["value_promise"]
    with pytest.raises(WilsyAICommercialPolicyError, match="DESCRIPTOR_SCHEMA_INVALID"):
        hydrate_wilsy_ai_commercial_policy(missing)
    extra = dict(payload)
    extra["unexpected"] = True
    with pytest.raises(WilsyAICommercialPolicyError, match="DESCRIPTOR_SCHEMA_INVALID"):
        hydrate_wilsy_ai_commercial_policy(extra)
    corrupt = dict(payload)
    corrupt["fingerprint"] = "0" * 128
    with pytest.raises(WilsyAICommercialPolicyError, match="FINGERPRINT_MISMATCH"):
        hydrate_wilsy_ai_commercial_policy(corrupt)


@pytest.mark.parametrize("field", sorted(EXPECTED[WilsyAITier.INSTITUTIONAL]))
def test_every_canonical_field_mutation_cannot_be_accepted(field: str) -> None:
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.INSTITUTIONAL)
    payload = policy.to_dict()
    original = payload[field]
    payload[field] = f"{original}-mutated" if isinstance(original, str) else -1
    with pytest.raises(WilsyAICommercialPolicyError):
        hydrate_wilsy_ai_commercial_policy(payload)


def test_descriptors_and_registry_are_immutable() -> None:
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    with pytest.raises(FrozenInstanceError):
        policy.monthly_price_minor = 1  # type: ignore[misc]
    with pytest.raises(TypeError):
        POLICIES[WilsyAITier.STARTER] = policy  # type: ignore[index]
    assert get_wilsy_ai_commercial_policy("WILSY_AI_STARTER") is policy


def test_import_and_authority_firewall_is_pure_policy_only() -> None:
    source = inspect.getsource(
        __import__("tools.eos.saas.billing.wilsy_ai_commercial_policy", fromlist=["*"])
    )
    assert "pymongo" not in source
    assert "requests" not in source
    assert "MongoClient" not in source
    keys = set(get_wilsy_ai_commercial_policy(WilsyAITier.STARTER).to_dict())
    assert keys == {
        "schema",
        "policy_identity",
        "policy_version",
        "tier",
        "label",
        "currency",
        "monthly_price_minor",
        "setup_price_minor",
        "daily_request_limit",
        "monthly_automation_limit",
        "analyst_seats",
        "max_autonomous_actions_per_day",
        "approval_threshold_minor",
        "overage_price_per_request_minor",
        "value_promise",
        "fingerprint",
    }
    forbidden = {
        "entitlement",
        "activation",
        "usage",
        "invoice",
        "charge",
        "settlement",
        "payment",
        "refund",
        "paid_state",
        "autonomous_action_authorization",
    }
    assert forbidden.isdisjoint(keys)


def test_registry_contains_only_the_closed_three_tiers() -> None:
    assert set(POLICIES) == set(WilsyAITier)
    assert len(POLICIES) == 3


# ARTIFACT: test_wilsy_ai_commercial_policy.py
# VERSION: v1.0.0-M13-P3
# AUTHORITY BOUNDARY: Direct certificate for pure commercial-policy evidence.
# TENANT POSTURE: Catalogue facts only; no tenant entitlement or activation.
# FAIL-CLOSED POSTURE: Unknown, malformed, altered, and overridden inputs reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
