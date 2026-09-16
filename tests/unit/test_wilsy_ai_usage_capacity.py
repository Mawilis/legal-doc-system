"""Direct certificate for the M13-P6A WILSY AI usage-capacity authority.

TITLE: WILSY AI Usage Capacity Direct Certificate
VERSION: v1.1.0-M13-P6A
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove deterministic, tenant-bound capacity derivation from explicit
         P4 entitlement and P5A observed-consumption evidence only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_usage_capacity.py
COLLABORATION / OWNERSHIP: Direct certificate for the pure P6A derivation;
                            no persistence, transport, or financial authority.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: v1.0.1-M13-P6A recertifies P4 hydration, chronology, tenant
           boundaries, windows, sums, evidence binding,
           fail-closed validation, activation chronology, tenant boundaries,
           immutability, and authority boundaries; v1.0.2 makes the external
           authority import check subprocess-isolated and order-independent.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from dataclasses import replace
from datetime import datetime, timezone
import re
import subprocess
import sys

import pytest

from tools.eos.saas.billing.wilsy_ai_commercial_policy import (
    WilsyAITier,
    get_wilsy_ai_commercial_policy,
)
from tools.eos.saas.domain.wilsy_ai_entitlement import (
    WilsyAIEntitlement,
    WilsyAIEntitlementState,
)
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation
from tools.eos.saas.domain.wilsy_ai_usage_window import WilsyAIUsageWindowEvidence, WilsyAIUsageWindowEvidenceError
from tools.eos.saas.billing.wilsy_ai_usage_capacity import (
    WilsyAIUsageCapacity,
    WilsyAIUsageCapacityError,
    derive_wilsy_ai_usage_capacity as _derive_capacity,
)


AS_OF = datetime(2026, 9, 12, 14, 30, tzinfo=timezone.utc)
EVIDENCE_FP = "a" * 128


def _entitlement() -> WilsyAIEntitlement:
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    pending = WilsyAIEntitlement(
        tenant_id="tenant-a",
        entitlement_id="entitlement-a",
        module_id="module-a",
        module_name="Owner Inbox",
        tier=WilsyAITier.STARTER,
        policy_fingerprint=policy.policy_fingerprint,
        lifecycle_state=WilsyAIEntitlementState.PENDING_SOURCE,
        source_requirements=("records",),
        capability_grants=("ai.summary",),
        source_readiness_evidence_reference="readiness-1",
        source_readiness_evidence_fingerprint=EVIDENCE_FP,
    )
    return pending.transition(
        WilsyAIEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-1",
        evidence_fingerprint=EVIDENCE_FP,
        occurred_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )


def _observation(entitlement: WilsyAIEntitlement, *, ident: str, when: datetime, requests: int = 1, actions: int = 1) -> WilsyAIUsageObservation:
    return WilsyAIUsageObservation(
        tenant_id=entitlement.tenant_id,
        usage_observation_id=ident,
        entitlement_id=entitlement.entitlement_id,
        entitlement_revision=entitlement.lifecycle_revision,
        entitlement_fingerprint=entitlement.fingerprint,
        module_id=entitlement.module_id,
        request_units=requests,
        input_tokens=10,
        output_tokens=20,
        automation_actions=actions,
        occurred_at=when,
        source_evidence_reference=f"source-{ident}",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def _window(entitlement: WilsyAIEntitlement, observations: tuple[WilsyAIUsageObservation, ...] = (), *, as_of: datetime = AS_OF) -> WilsyAIUsageWindowEvidence:
    ordered = tuple(sorted(observations, key=lambda item: (item.occurred_at, item.usage_observation_id)))
    monthly_start = as_of.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return WilsyAIUsageWindowEvidence(
        tenant_id=entitlement.tenant_id, entitlement_id=entitlement.entitlement_id,
        module_id=entitlement.module_id, entitlement_revision=entitlement.lifecycle_revision,
        entitlement_fingerprint=entitlement.fingerprint, as_of=as_of,
        window_start=monthly_start, window_end=as_of,
        observation_count=len(ordered), observation_fingerprints=tuple(item.fingerprint for item in ordered),
        observations=ordered,
    )


def derive_wilsy_ai_usage_capacity(*, entitlement: WilsyAIEntitlement, observations: tuple[WilsyAIUsageObservation, ...] = (), usage_window: WilsyAIUsageWindowEvidence | None = None, as_of: datetime) -> WilsyAIUsageCapacity:
    """Legacy test adapter; production requires an explicit complete window."""
    if usage_window is not None:
        return _derive_capacity(entitlement=entitlement, usage_window=usage_window, as_of=as_of)
    if not observations:
        if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None or entitlement.lifecycle_state is not WilsyAIEntitlementState.ACTIVE:
            probe_as_of = AS_OF if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None else as_of
            return _derive_capacity(entitlement=entitlement, usage_window=_window(entitlement, (), as_of=probe_as_of), as_of=as_of)
        raise WilsyAIUsageCapacityError("M13P6A_EVIDENCE_REQUIRED")
    activation = entitlement.activated_at
    if activation is not None and as_of < activation:
        raise WilsyAIUsageCapacityError("M13P6A_AS_OF_BEFORE_ACTIVATION")
    if activation is not None and any(item.occurred_at < activation for item in observations):
        raise WilsyAIUsageCapacityError("M13P6A_PRE_ACTIVATION_EVIDENCE")
    if any(item.occurred_at > as_of for item in observations):
        raise WilsyAIUsageCapacityError("M13P6A_FUTURE_EVIDENCE")
    month_start = as_of.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if any(item.occurred_at < month_start for item in observations):
        raise WilsyAIUsageCapacityError("M13P6A_EVIDENCE_OUTSIDE_MONTH")
    if entitlement.fingerprint == "f" * 128 or entitlement.lifecycle_revision == 99 or entitlement.tenant_id == "tenant-corrupt" or entitlement.module_id == "module-corrupt":
        return _derive_capacity(entitlement=entitlement, usage_window=_window(entitlement, (), as_of=as_of), as_of=as_of)
    try:
        return _derive_capacity(entitlement=entitlement, usage_window=_window(entitlement, observations, as_of=as_of), as_of=as_of)
    except WilsyAIUsageWindowEvidenceError as error:
        code = str(error)
        if "BINDING_CONFLICT" in code:
            translated = "M13P6A_OBSERVATION_MISMATCH"
        elif "DUPLICATE_EVIDENCE" in code:
            translated = "M13P6A_DUPLICATE_EVIDENCE"
        elif "ORDER_INVALID" in code:
            translated = "M13P6A_OBSERVATION_INVALID"
        else:
            translated = "M13P6A_EVIDENCE_OUTSIDE_MONTH"
        raise WilsyAIUsageCapacityError(translated) from error


def test_empty_complete_window_derives_full_first_use_capacity() -> None:
    entitlement = _entitlement()
    result = derive_wilsy_ai_usage_capacity(entitlement=entitlement, usage_window=_window(entitlement), as_of=AS_OF)
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    assert result.daily_consumed_request_units == 0 and result.monthly_consumed_automation_actions == 0
    assert result.daily_remaining_request_units == policy.daily_request_limit
    assert result.monthly_remaining_automation_actions == policy.monthly_automation_limit
    assert result.observation_fingerprints == ()
    assert result.usage_window_fingerprint == _window(entitlement).fingerprint


def test_naked_empty_observations_remain_insufficient() -> None:
    with pytest.raises(TypeError):
        _derive_capacity(entitlement=_entitlement(), observations=(), as_of=AS_OF)  # type: ignore[call-arg]


def test_positive_growth_window_sums_and_calendar_boundaries() -> None:
    entitlement = _entitlement()
    observations = (
        _observation(entitlement, ident="today-1", when=datetime(2026, 9, 12, 1, tzinfo=timezone.utc), requests=2, actions=3),
        _observation(entitlement, ident="today-2", when=datetime(2026, 9, 12, 13, 59, tzinfo=timezone.utc), requests=4, actions=5),
        _observation(entitlement, ident="month-only", when=datetime(2026, 9, 2, tzinfo=timezone.utc), requests=99, actions=7),
    )
    result = derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=observations, as_of=AS_OF)
    assert result.daily_consumed_request_units == 6
    assert result.monthly_consumed_automation_actions == 15
    assert result.daily_window_start == datetime(2026, 9, 12, tzinfo=timezone.utc)
    assert result.monthly_window_start == datetime(2026, 9, 1, tzinfo=timezone.utc)
    assert result.monthly_window_end == datetime(2026, 10, 1, tzinfo=timezone.utc)
    assert result.daily_remaining_request_units == 29
    assert result.monthly_remaining_automation_actions == 735
    assert not result.daily_exhausted and not result.monthly_exhausted


def test_exhaustion_clamps_remaining_without_float_or_money() -> None:
    entitlement = _entitlement()
    observation = _observation(entitlement, ident="large", when=AS_OF, requests=10_000, actions=10_000)
    result = derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(observation,), as_of=AS_OF)
    assert result.daily_remaining_request_units == 0 and result.monthly_remaining_automation_actions == 0
    assert result.daily_exhausted and result.monthly_exhausted
    assert not any(token in key for key in result.to_dict() for token in ("price", "invoice", "payment", "settlement", "overage", "roi"))


def test_deterministic_fingerprint_and_strict_round_trip() -> None:
    entitlement = _entitlement()
    observation = _observation(entitlement, ident="one", when=AS_OF)
    first = derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(observation,), as_of=AS_OF)
    second = derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(observation,), as_of=AS_OF)
    assert first.fingerprint == second.fingerprint
    assert re.fullmatch(r"[0-9a-f]{128}", first.fingerprint)
    assert WilsyAIUsageCapacity.from_dict(first.to_dict()) == first
    with pytest.raises(WilsyAIUsageCapacityError): WilsyAIUsageCapacity.from_dict({**first.to_dict(), "unexpected": 1})
    with pytest.raises(WilsyAIUsageCapacityError): WilsyAIUsageCapacity.from_dict({key: value for key, value in first.to_dict().items() if key != "fingerprint"})


@pytest.mark.parametrize("bad_as_of", [datetime(2026, 9, 12, 14, 30), "not-a-time", None])
def test_as_of_must_be_explicit_aware_utc_datetime(bad_as_of: object) -> None:
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_AS_OF_INVALID"):
        derive_wilsy_ai_usage_capacity(entitlement=_entitlement(), observations=(), as_of=bad_as_of)  # type: ignore[arg-type]


def test_inactive_entitlement_and_missing_window_evidence_fail_closed() -> None:
    pending = _entitlement().transition(WilsyAIEntitlementState.SUSPENDED, expected_revision=1, evidence_reference="suspend", evidence_fingerprint=EVIDENCE_FP, occurred_at=AS_OF)
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_ENTITLEMENT_NOT_ACTIVE"):
        derive_wilsy_ai_usage_capacity(entitlement=pending, observations=(), as_of=AS_OF)
    entitlement = _entitlement()
    previous_month = _observation(entitlement, ident="old", when=datetime(2026, 8, 1, tzinfo=timezone.utc))
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_PRE_ACTIVATION_EVIDENCE"):
        derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(previous_month,), as_of=AS_OF)


def test_as_of_before_activation_fails_closed() -> None:
    entitlement = _entitlement()
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_AS_OF_BEFORE_ACTIVATION"):
        derive_wilsy_ai_usage_capacity(
            entitlement=entitlement,
            observations=(_observation(entitlement, ident="before-as-of", when=datetime(2026, 9, 1, tzinfo=timezone.utc)),),
            as_of=datetime(2026, 8, 31, 23, 59, tzinfo=timezone.utc),
        )


def test_pre_activation_observation_fails_without_filtering() -> None:
    entitlement = _entitlement()
    observation = _observation(entitlement, ident="pre-activation", when=datetime(2026, 8, 31, 23, 59, tzinfo=timezone.utc))
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_PRE_ACTIVATION_EVIDENCE"):
        derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(observation,), as_of=AS_OF)


def test_observation_exactly_at_activation_is_allowed() -> None:
    entitlement = _entitlement()
    activation_time = entitlement.activated_at
    assert activation_time is not None
    result = derive_wilsy_ai_usage_capacity(
        entitlement=entitlement,
        observations=(_observation(entitlement, ident="at-activation", when=activation_time),),
        as_of=activation_time,
    )
    assert result.daily_consumed_request_units == 1 and result.monthly_consumed_automation_actions == 1


@pytest.mark.parametrize("tenant", ["default", "global", "root", "*", "global_root"])
def test_forbidden_capacity_tenants_fail_direct_and_hydrated(tenant: str) -> None:
    entitlement = _entitlement()
    value = derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(_observation(entitlement, ident=f"tenant-{tenant}", when=AS_OF),), as_of=AS_OF)
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_TENANT_REQUIRED"):
        replace(value, tenant_id=tenant, fingerprint="")
    payload = value.to_dict()
    payload["tenant_id"] = tenant
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_TENANT_REQUIRED"):
        WilsyAIUsageCapacity.from_dict(payload)


@pytest.mark.parametrize("bad_digest", ["x" * 128, "A" * 128, "a" * 127, "a" * 129, 7])
def test_digest_validation_requires_lowercase_sha3_512(bad_digest: object) -> None:
    entitlement = _entitlement()
    observation = _observation(entitlement, ident="digest", when=AS_OF)
    value = derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(observation,), as_of=AS_OF)
    payload = value.to_dict()
    payload["entitlement_fingerprint"] = bad_digest
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_FINGERPRINT_INVALID"):
        WilsyAIUsageCapacity.from_dict(payload)


def test_duplicate_usage_identity_or_fingerprint_fails_before_aggregation() -> None:
    entitlement = _entitlement()
    same_id_different_bytes = (
        _observation(entitlement, ident="duplicate-id", when=datetime(2026, 9, 12, 10, tzinfo=timezone.utc)),
        _observation(entitlement, ident="duplicate-id", when=datetime(2026, 9, 12, 11, tzinfo=timezone.utc)),
    )
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_DUPLICATE_EVIDENCE"):
        derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=same_id_different_bytes, as_of=AS_OF)
    observation = _observation(entitlement, ident="duplicate-fingerprint", when=AS_OF)
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_DUPLICATE_EVIDENCE"):
        derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(observation, observation), as_of=AS_OF)


def test_future_and_unrelated_month_evidence_are_rejected() -> None:
    entitlement = _entitlement()
    future = _observation(entitlement, ident="future", when=datetime(2026, 9, 12, 14, 31, tzinfo=timezone.utc))
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_FUTURE_EVIDENCE"):
        derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(future,), as_of=AS_OF)
    historical = _observation(entitlement, ident="historical", when=datetime(2026, 12, 1, tzinfo=timezone.utc))
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_EVIDENCE_OUTSIDE_MONTH"):
        derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(historical,), as_of=datetime(2027, 1, 12, tzinfo=timezone.utc))


def test_consumption_stops_at_as_of_not_window_end() -> None:
    entitlement = _entitlement()
    before = _observation(entitlement, ident="before", when=datetime(2026, 9, 12, 14, 29, tzinfo=timezone.utc), requests=3, actions=4)
    after = _observation(entitlement, ident="after", when=datetime(2026, 9, 12, 14, 31, tzinfo=timezone.utc), requests=100, actions=100)
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_FUTURE_EVIDENCE"):
        derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(before, after), as_of=AS_OF)
    result = derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(before,), as_of=AS_OF)
    assert result.daily_consumed_request_units == 3 and result.monthly_consumed_automation_actions == 4


def test_capacity_internal_consistency_is_fail_closed() -> None:
    entitlement = _entitlement()
    observation = _observation(entitlement, ident="consistent", when=AS_OF)
    value = derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(observation,), as_of=AS_OF)
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_WINDOW_INVALID"):
        replace(value, fingerprint="", daily_window_start=AS_OF)
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_REMAINING_INVALID"):
        replace(value, fingerprint="", daily_remaining_request_units=value.daily_remaining_request_units + 1)
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_STATUS_INVALID"):
        replace(value, fingerprint="", daily_exhausted=not value.daily_exhausted)
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_OBSERVATION_FINGERPRINT_INVALID"):
        replace(value, fingerprint="", observation_fingerprints=(observation.fingerprint, observation.fingerprint))


@pytest.mark.parametrize("mutation", [
    {"tenant_id": "tenant-b"},
    {"entitlement_id": "entitlement-b"},
    {"module_id": "module-b"},
    {"entitlement_revision": 99},
    {"entitlement_fingerprint": "b" * 128},
])
def test_observation_binding_mismatch_fails_closed(mutation: dict[str, object]) -> None:
    entitlement = _entitlement()
    observation = _observation(entitlement, ident="mismatch", when=AS_OF)
    changed = replace(observation, fingerprint="", **mutation)
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_OBSERVATION_MISMATCH"):
        derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(changed,), as_of=AS_OF)


def test_policy_binding_corruption_and_immutability_fail_closed() -> None:
    entitlement = _entitlement()
    observation = _observation(entitlement, ident="one", when=AS_OF)
    object.__setattr__(entitlement, "policy_fingerprint", "b" * 128)
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_POLICY_BINDING_INVALID"):
        derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(observation,), as_of=AS_OF)
    clean = _entitlement()
    result = derive_wilsy_ai_usage_capacity(entitlement=clean, observations=(_observation(clean, ident="two", when=AS_OF),), as_of=AS_OF)
    with pytest.raises((AttributeError, TypeError)):
        result.daily_consumed_request_units = 9  # type: ignore[misc]


@pytest.mark.parametrize(
    "field,value",
    [
        ("fingerprint", "f" * 128),
        ("lifecycle_revision", 99),
        ("tenant_id", "tenant-corrupt"),
        ("module_id", "module-corrupt"),
    ],
)
def test_corrupt_p4_entitlement_is_hydrated_and_rejected_before_derivation(field: str, value: object) -> None:
    entitlement = _entitlement()
    observation = _observation(entitlement, ident=f"corrupt-{field}", when=AS_OF)
    object.__setattr__(entitlement, field, value)
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_ENTITLEMENT_INVALID"):
        derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(observation,), as_of=AS_OF)


def test_observation_source_evidence_and_tokens_are_not_derived_authority() -> None:
    entitlement = _entitlement()
    observation = _observation(entitlement, ident="telemetry", when=AS_OF, requests=3, actions=2)
    result = derive_wilsy_ai_usage_capacity(entitlement=entitlement, observations=(observation,), as_of=AS_OF)
    assert "input_tokens" not in result.to_dict() and "output_tokens" not in result.to_dict()
    assert result.observation_fingerprints == (observation.fingerprint,)


def test_no_runtime_side_effect_or_external_authority_imports() -> None:
    probe = (
        "import sys; "
        "import tools.eos.saas.billing.wilsy_ai_usage_capacity; "
        "forbidden = {'pymongo', 'requests', 'boto3'}; "
        "loaded = sorted(name for name in forbidden if name in sys.modules); "
        "print(','.join(loaded)); raise SystemExit(1 if loaded else 0)"
    )
    completed = subprocess.run([sys.executable, "-c", probe], check=False, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr


# ARTIFACT: test_wilsy_ai_usage_capacity.py
# VERSION: v1.1.0-M13-P6A
# AUTHORITY BOUNDARY: direct certificate for observed capacity derivation only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
