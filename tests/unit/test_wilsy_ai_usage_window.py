"""Direct certificate for immutable M13-P6B complete usage-window evidence.

TITLE: WILSY AI Usage Window Evidence Certificate
VERSION: v1.0.0-M13-P6B
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove deterministic complete-window identity, strict binding, and
         legitimate empty first-use evidence without synthetic usage events.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_usage_window.py
COLLABORATION / OWNERSHIP: P6B domain certificate; P5A remains source-fact
                            authority and P6A remains capacity authority.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-M13-P6B certifies empty/nonempty windows, ordering,
           chronology, strict hydration, and SHA3-512 identity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from dataclasses import replace
from datetime import datetime, timezone

import pytest

from tools.eos.saas.billing.wilsy_ai_commercial_policy import WilsyAITier, get_wilsy_ai_commercial_policy
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlement, WilsyAIEntitlementState
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation
from tools.eos.saas.domain.wilsy_ai_usage_window import WilsyAIUsageWindowEvidence, WilsyAIUsageWindowEvidenceError

FP = "a" * 128
AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)


def entitlement() -> WilsyAIEntitlement:
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    pending = WilsyAIEntitlement(
        tenant_id="tenant-window", entitlement_id="ent-window", module_id="module-window", module_name="Inbox",
        tier=WilsyAITier.STARTER, policy_fingerprint=policy.policy_fingerprint,
        lifecycle_state=WilsyAIEntitlementState.PENDING_SOURCE, source_requirements=("records",),
        capability_grants=("ai.summary",), source_readiness_evidence_reference="ready",
        source_readiness_evidence_fingerprint=FP,
    )
    return pending.transition(WilsyAIEntitlementState.ACTIVE, expected_revision=0,
                              evidence_reference="active", evidence_fingerprint=FP,
                              occurred_at=datetime(2026, 9, 1, tzinfo=timezone.utc))


def observation(ent: WilsyAIEntitlement, ident: str = "one", when: datetime = AS_OF) -> WilsyAIUsageObservation:
    return WilsyAIUsageObservation(ent.tenant_id, ident, ent.entitlement_id, ent.lifecycle_revision,
                                   ent.fingerprint, ent.module_id, 1, 2, 3, 1, when,
                                   "source-" + ident, FP)


def window(ent: WilsyAIEntitlement, observations: tuple[WilsyAIUsageObservation, ...] = ()) -> WilsyAIUsageWindowEvidence:
    return WilsyAIUsageWindowEvidence(
        tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id,
        entitlement_revision=ent.lifecycle_revision, entitlement_fingerprint=ent.fingerprint,
        as_of=AS_OF, window_start=datetime(2026, 9, 1, tzinfo=timezone.utc), window_end=AS_OF,
        observation_count=len(observations), observation_fingerprints=tuple(item.fingerprint for item in observations),
        observations=observations,
    )


def test_empty_complete_window_is_valid_and_has_no_synthetic_observation() -> None:
    value = window(entitlement())
    assert value.observation_count == 0 and value.observations == () and value.observation_fingerprints == ()
    assert value.fingerprint == window(entitlement()).fingerprint
    assert value.to_dict()["observations"] == []


def test_nonempty_window_is_bound_and_canonical() -> None:
    ent = entitlement(); item = observation(ent)
    value = window(ent, (item,))
    assert value.observation_count == 1 and value.observations == (item,)
    assert value.observation_fingerprints == (item.fingerprint,)
    assert WilsyAIUsageWindowEvidence.from_dict(value.to_dict()) == value


def test_order_duplicate_binding_and_boundary_drift_fail_closed() -> None:
    ent = entitlement(); first = observation(ent, "first", datetime(2026, 9, 1, 1, tzinfo=timezone.utc)); second = observation(ent, "second", AS_OF)
    with pytest.raises(WilsyAIUsageWindowEvidenceError, match="ORDER_INVALID"):
        window(ent, (second, first))
    with pytest.raises(WilsyAIUsageWindowEvidenceError, match="DUPLICATE_EVIDENCE"):
        window(ent, (first, first))
    with pytest.raises(WilsyAIUsageWindowEvidenceError, match="SCHEMA_INVALID"):
        WilsyAIUsageWindowEvidence.from_dict({**window(ent).to_dict(), "unexpected": True})
    with pytest.raises(WilsyAIUsageWindowEvidenceError, match="FINGERPRINT_MISMATCH"):
        WilsyAIUsageWindowEvidence.from_dict({**window(ent).to_dict(), "fingerprint": "b" * 128})


def test_window_rejects_out_of_window_or_binding_mismatch() -> None:
    ent = entitlement()
    with pytest.raises(WilsyAIUsageWindowEvidenceError, match="BINDING_CONFLICT"):
        window(ent, (observation(ent, "old", datetime(2026, 8, 31, tzinfo=timezone.utc)),))
    changed = replace(observation(ent), fingerprint="", tenant_id="tenant-other")
    with pytest.raises(WilsyAIUsageWindowEvidenceError, match="BINDING_CONFLICT"):
        window(ent, (changed,))


# ARTIFACT: test_wilsy_ai_usage_window.py
# VERSION: v1.0.0-M13-P6B
# AUTHORITY BOUNDARY: complete-window evidence certificate only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
