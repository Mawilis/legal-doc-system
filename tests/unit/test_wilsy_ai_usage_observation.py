"""Direct P5A certificate for immutable WILSY AI usage observations.

TITLE: WILSY AI Usage Observation Direct Certificate
VERSION: v1.0.2-M13-P5A
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove strict source-evidenced consumption facts without persistence,
         quota, commercial, execution, or settlement authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_usage_observation.py
COLLABORATION / OWNERSHIP: Direct certificate for the P5A domain owner.
CERTIFICATION / UPDATE DATE: 2026-11-11
CHANGELOG: v1.0.2-M13-P5A records the verified sovereign metadata correction; test and production behavior are unchanged.
           v1.0.1-M13-P5A verifies provider-SDK import purity in a fresh interpreter, independent of suite order.
           v1.0.0-M13-P5A certifies deterministic identity, strict hydration,
           numeric/timestamp validation, immutability, and authority firewall.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic source-usage evidence only; no provider credentials or customer content.
TENANT BOUNDARY: Each observation is bound to its exact synthetic tenant and source evidence.
AUTHORITY BOUNDARY: Immutable usage-observation evidence only; no quota, payment, or execution authority.
FINANCIAL AUTHORITY BOUNDARY: No payment, execution, settlement, or ledger authority; Kennel EOS exclusively owns financial execution.
"""
from dataclasses import replace
from datetime import datetime, timezone
import re
from typing import Any, cast

import pytest

from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation, WilsyAIUsageObservationError

NOW = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)
FP = "a" * 128


def observation(**changes: object) -> WilsyAIUsageObservation:
    values: dict[str, object] = {
        "tenant_id": "tenant-a", "usage_observation_id": "usage-1", "entitlement_id": "ent-1", "entitlement_revision": 1,
        "entitlement_fingerprint": FP, "module_id": "module-a", "request_units": 1, "input_tokens": 10,
        "output_tokens": 20, "automation_actions": 0, "occurred_at": NOW,
        "source_evidence_reference": "provider-event-1", "source_evidence_fingerprint": FP,
    }
    values.update(changes)
    return WilsyAIUsageObservation(**cast(Any, values))


def test_deterministic_sha3_fingerprint_and_round_trip() -> None:
    first, second = observation(), observation()
    assert first.fingerprint == second.fingerprint and re.fullmatch(r"[0-9a-f]{128}", first.fingerprint)
    assert WilsyAIUsageObservation.from_dict(first.to_dict()) == first


def test_every_semantic_mutation_changes_fingerprint() -> None:
    base = observation()
    fields = (("tenant_id", "tenant-b"), ("usage_observation_id", "usage-2"), ("entitlement_id", "ent-2"), ("entitlement_revision", 2), ("entitlement_fingerprint", "b" * 128), ("module_id", "module-b"), ("request_units", 2), ("input_tokens", 11), ("output_tokens", 21), ("automation_actions", 1), ("occurred_at", NOW.replace(hour=13)), ("source_evidence_reference", "provider-event-2"), ("source_evidence_fingerprint", "b" * 128))
    for field, value in fields:
        assert replace(base, fingerprint="", **{field: value}).fingerprint != base.fingerprint


def test_missing_extra_and_corrupt_fields_reject() -> None:
    payload = observation().to_dict()
    with pytest.raises(WilsyAIUsageObservationError): WilsyAIUsageObservation.from_dict({**payload, "extra": 1})
    with pytest.raises(WilsyAIUsageObservationError): WilsyAIUsageObservation.from_dict({k: v for k, v in payload.items() if k != "source_evidence_reference"})
    payload["fingerprint"] = "f" * 128
    with pytest.raises(WilsyAIUsageObservationError): WilsyAIUsageObservation.from_dict(payload)


@pytest.mark.parametrize("field,value", [("request_units", 0), ("request_units", -1), ("input_tokens", -1), ("output_tokens", -1), ("automation_actions", -1), ("request_units", True), ("input_tokens", False), ("entitlement_revision", True)])
def test_numeric_values_are_strict(field: str, value: object) -> None:
    with pytest.raises(WilsyAIUsageObservationError): observation(**{field: value})


@pytest.mark.parametrize("value", [datetime(2026, 9, 12), "not-a-time"])
def test_timestamp_must_be_aware_and_valid(value: object) -> None:
    with pytest.raises(WilsyAIUsageObservationError): observation(occurred_at=value)


@pytest.mark.parametrize("field", ["tenant_id", "usage_observation_id", "entitlement_id", "module_id"])
def test_explicit_identity_and_global_tenant_required(field: str) -> None:
    with pytest.raises(WilsyAIUsageObservationError): observation(**{field: ""})
    with pytest.raises(WilsyAIUsageObservationError): observation(tenant_id="global")


def test_malformed_evidence_fingerprints_reject() -> None:
    with pytest.raises(WilsyAIUsageObservationError): observation(entitlement_fingerprint="x")
    with pytest.raises(WilsyAIUsageObservationError): observation(source_evidence_fingerprint="B" * 128)


def test_immutable_and_financial_quota_execution_firewall() -> None:
    value = observation()
    with pytest.raises((AttributeError, TypeError)): value.request_units = 2  # type: ignore[misc]
    assert not any(key in value.to_dict() for key in ("tier", "price", "quota", "remaining", "overage", "invoice", "payment", "settlement", "execution", "roi", "valueMetrics"))


def test_import_is_side_effect_free() -> None:
    import subprocess
    import sys
    from pathlib import Path

    script = (
        "import importlib, sys; "
        "importlib.import_module('tools.eos.saas.domain.wilsy_ai_usage_observation'); "
        "bad = sorted(name for name in sys.modules if name == 'requests' or "
        "name.startswith('requests.') or name == 'boto3' or name.startswith('boto3.')); "
        "assert not bad, bad"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_wilsy_ai_usage_observation.py
# VERSION: v1.0.2-M13-P5A
# AUTHORITY BOUNDARY: immutable source-observation domain tests only
# TENANT POSTURE: exact synthetic source and tenant bindings are mandatory
# FAIL-CLOSED POSTURE: invalid observations and provider imports reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
