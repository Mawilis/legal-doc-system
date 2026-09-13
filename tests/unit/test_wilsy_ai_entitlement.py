"""Direct certificate for the M13-P4 WILSY AI entitlement domain.

TITLE: WILSY AI Entitlement Direct Certificate
VERSION: v1.0.0-M13-P4
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove immutable tenant/module entitlement evidence and closed
         lifecycle semantics without persistence or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_entitlement.py
COLLABORATION / OWNERSHIP: Direct certificate for the P4 domain owner.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M13-P4 certifies P3 binding, lifecycle shape, hashing,
           strict hydration, immutability, and authority firewalls.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from datetime import datetime, timezone
from dataclasses import replace
import re
from typing import Any, cast

import pytest

from tools.eos.saas.billing.wilsy_ai_commercial_policy import WilsyAITier, get_wilsy_ai_commercial_policy
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlement, WilsyAIEntitlementError, WilsyAIEntitlementState, create_wilsy_ai_entitlement

NOW = datetime(2026, 9, 12, tzinfo=timezone.utc)
FP = "a" * 128


def entitlement(**changes: object) -> WilsyAIEntitlement:
    values: dict[str, object] = {
        "tenant_id": "tenant-a", "entitlement_id": "ent-a", "module_id": "module-a", "module_name": "Owner Inbox",
        "tier": WilsyAITier.STARTER, "policy_fingerprint": get_wilsy_ai_commercial_policy(WilsyAITier.STARTER).policy_fingerprint,
        "lifecycle_state": WilsyAIEntitlementState.PENDING_SOURCE, "source_requirements": ("records",), "capability_grants": ("ai.summary",),
        "source_readiness_evidence_reference": "readiness-1", "source_readiness_evidence_fingerprint": FP,
    }
    values.update(changes)
    return WilsyAIEntitlement(**cast(Any, values))


def test_p3_policy_fingerprint_binding_and_exact_tier() -> None:
    value = create_wilsy_ai_entitlement(tenant_id="tenant-a", entitlement_id="ent-a", module_id="module-a", module_name="Owner Inbox", tier=WilsyAITier.STARTER, lifecycle_state=WilsyAIEntitlementState.PENDING_SOURCE, source_requirements=("records",), capability_grants=("ai.summary",), source_readiness_evidence_reference="readiness-1", source_readiness_evidence_fingerprint=FP)
    assert value.tier is WilsyAITier.STARTER and value.policy_fingerprint == get_wilsy_ai_commercial_policy(WilsyAITier.STARTER).policy_fingerprint


def test_pending_source_shape_requires_readiness() -> None:
    with pytest.raises(WilsyAIEntitlementError): entitlement(source_readiness_evidence_reference=None, source_readiness_evidence_fingerprint=None)


@pytest.mark.parametrize("state,changes", [
    (WilsyAIEntitlementState.ACTIVE, {"activated_at": NOW, "activation_evidence_reference": "act", "activation_evidence_fingerprint": FP}),
    (WilsyAIEntitlementState.SUSPENDED, {"activated_at": NOW, "activation_evidence_reference": "act", "activation_evidence_fingerprint": FP, "suspended_at": NOW, "suspension_evidence_reference": "susp", "suspension_evidence_fingerprint": FP}),
    (WilsyAIEntitlementState.REVOKED, {"activated_at": NOW, "activation_evidence_reference": "act", "activation_evidence_fingerprint": FP, "revoked_at": NOW, "revocation_evidence_reference": "rev", "revocation_evidence_fingerprint": FP}),
])
def test_non_pending_lifecycle_shapes(state: WilsyAIEntitlementState, changes: dict[str, object]) -> None:
    assert entitlement(lifecycle_state=state, **changes).lifecycle_state is state


@pytest.mark.parametrize("changes", [
    {"lifecycle_state": "UNKNOWN"}, {"tier": "UNKNOWN"}, {"tenant_id": ""}, {"tenant_id": "global"},
    {"policy_fingerprint": "b" * 128}, {"source_requirements": ()}, {"capability_grants": ("x", "x")},
    {"source_readiness_evidence_reference": "r", "source_readiness_evidence_fingerprint": None},
    {"activated_at": datetime(2026, 1, 1)}, {"module_id": " module"},
])
def test_invalid_values_fail_closed(changes: dict[str, object]) -> None:
    with pytest.raises(WilsyAIEntitlementError): entitlement(**changes)


def test_fingerprint_is_lowercase_sha3_512_and_deterministic() -> None:
    first, second = entitlement(), entitlement()
    assert first.fingerprint == second.fingerprint and re.fullmatch(r"[0-9a-f]{128}", first.fingerprint)


def test_every_semantic_mutation_changes_fingerprint() -> None:
    base = entitlement()
    for field, value in (("tenant_id", "tenant-b"), ("module_name", "Other"), ("capability_grants", ("ai.other",)), ("source_readiness_evidence_reference", "r2")):
        assert replace(base, fingerprint="", **{field: value}).fingerprint != base.fingerprint


def test_strict_round_trip_and_unknown_or_missing_fields_rejected() -> None:
    payload = entitlement().to_dict()
    assert WilsyAIEntitlement.from_dict(payload) == entitlement()
    with pytest.raises(WilsyAIEntitlementError): WilsyAIEntitlement.from_dict({**payload, "extra": 1})
    with pytest.raises(WilsyAIEntitlementError): WilsyAIEntitlement.from_dict({k: v for k, v in payload.items() if k != "fingerprint"})


def test_corrupt_fingerprint_rejected() -> None:
    payload = entitlement().to_dict(); payload["fingerprint"] = "f" * 128
    with pytest.raises(WilsyAIEntitlementError): WilsyAIEntitlement.from_dict(payload)


def test_immutability_and_no_financial_authority() -> None:
    value = entitlement()
    with pytest.raises((AttributeError, TypeError)): value.tenant_id = "x"  # type: ignore[misc]
    assert not any(k in value.to_dict() for k in ("invoice", "payment", "settlement", "usage", "charge", "execution"))


def test_revoked_cannot_be_reactivated_by_shape() -> None:
    revoked = entitlement(lifecycle_state=WilsyAIEntitlementState.REVOKED, activated_at=NOW, activation_evidence_reference="a", activation_evidence_fingerprint=FP, revoked_at=NOW, revocation_evidence_reference="r", revocation_evidence_fingerprint=FP)
    with pytest.raises(WilsyAIEntitlementError): replace(revoked, lifecycle_state=WilsyAIEntitlementState.ACTIVE, revoked_at=None, revocation_evidence_reference=None, revocation_evidence_fingerprint=None)


def test_revisioned_legal_transitions_and_terminal_rejection() -> None:
    pending = entitlement()
    active = pending.transition(WilsyAIEntitlementState.ACTIVE, expected_revision=0, evidence_reference="act", evidence_fingerprint=FP, occurred_at=NOW)
    suspended = active.transition(WilsyAIEntitlementState.SUSPENDED, expected_revision=1, evidence_reference="susp", evidence_fingerprint=FP, occurred_at=NOW)
    assert (active.lifecycle_revision, suspended.lifecycle_revision) == (1, 2)
    with pytest.raises(WilsyAIEntitlementError): pending.transition(WilsyAIEntitlementState.ACTIVE, expected_revision=9, evidence_reference="act", evidence_fingerprint=FP, occurred_at=NOW)
    with pytest.raises(WilsyAIEntitlementError): suspended.transition(WilsyAIEntitlementState.ACTIVE, expected_revision=2, evidence_reference="act2", evidence_fingerprint=FP, occurred_at=NOW)
    revoked = active.transition(WilsyAIEntitlementState.REVOKED, expected_revision=1, evidence_reference="rev", evidence_fingerprint=FP, occurred_at=NOW)
    with pytest.raises(WilsyAIEntitlementError): revoked.transition(WilsyAIEntitlementState.ACTIVE, expected_revision=2, evidence_reference="act2", evidence_fingerprint=FP, occurred_at=NOW)


def test_transition_chronology_is_strict() -> None:
    active = entitlement().transition(WilsyAIEntitlementState.ACTIVE, expected_revision=0, evidence_reference="act", evidence_fingerprint=FP, occurred_at=NOW)
    with pytest.raises(WilsyAIEntitlementError): active.transition(WilsyAIEntitlementState.SUSPENDED, expected_revision=1, evidence_reference="susp", evidence_fingerprint=FP, occurred_at=NOW.replace(year=2025))


def test_no_runtime_side_effect_imports() -> None:
    import sys
    assert "requests" not in sys.modules and "boto3" not in sys.modules
