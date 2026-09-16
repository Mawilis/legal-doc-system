"""Direct M13-P6C certificate for WILSY AI capacity composition.

TITLE: WILSY AI Usage Capacity Orchestrator Certificate
VERSION: v1.1.0-M13-P6C
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove same-snapshot P4/P6B composition into the frozen P6A
         derivation without adding persistence, quota, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_usage_capacity_orchestrator.py
COLLABORATION / OWNERSHIP: Direct certificate for the P6C composition owner;
                            P4, P6B, and P6A remain canonical authorities.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: v1.0.0-M13-P6C certifies canonical P4 identity forwarding,
           caller-session propagation, governed failure preservation, and
           unchanged P6A capacity output.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: In-memory doubles only; no clients, secrets,
                             providers, network, or financial operations.
TENANT BOUNDARY: Every lookup is explicitly tenant-scoped; pseudo-tenants
                 are rejected by the composition boundary.
AUTHORITY BOUNDARY: Composition only; P6A owns capacity derivation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
"""
from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.saas.billing.wilsy_ai_commercial_policy import (
    WilsyAITier,
    get_wilsy_ai_commercial_policy,
)
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import (
    WilsyAIEntitlementRegistryError,
)
from tools.eos.saas.billing.wilsy_ai_usage_capacity import (
    WilsyAIUsageCapacityError,
)
from tools.eos.saas.billing.wilsy_ai_usage_capacity_orchestrator import (
    WilsyAIUsageCapacityOrchestrator,
    WilsyAIUsageCapacityOrchestratorError,
)
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import (
    WilsyAIUsageObservationRegistryError,
)
from tools.eos.saas.domain.wilsy_ai_entitlement import (
    WilsyAIEntitlement,
    WilsyAIEntitlementState,
)
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation
from tools.eos.saas.domain.wilsy_ai_usage_window import WilsyAIUsageWindowEvidence


FP = "a" * 128
AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)
ACTIVATED_AT = datetime(2026, 9, 1, tzinfo=timezone.utc)


class Session:
    in_transaction = True


class EntitlementRegistry:
    def __init__(self, value: WilsyAIEntitlement | None = None, error: Exception | None = None) -> None:
        self.value = value
        self.error = error
        self.calls: list[dict[str, Any]] = []

    def get(self, **kwargs: Any) -> WilsyAIEntitlement:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        assert self.value is not None
        return self.value


class ObservationRegistry:
    def __init__(self, value: tuple[WilsyAIUsageObservation, ...] = (), error: Exception | None = None) -> None:
        self.value = value
        self.error = error
        self.calls: list[dict[str, Any]] = []

    def get_bounded_for_p6a(self, **kwargs: Any) -> tuple[WilsyAIUsageObservation, ...]:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.value

    def get_complete_window_for_p6a(self, **kwargs: Any) -> WilsyAIUsageWindowEvidence:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        entitlement_id = kwargs["entitlement_id"]
        return WilsyAIUsageWindowEvidence(
            tenant_id=kwargs["tenant_id"], entitlement_id=entitlement_id,
            module_id=kwargs["module_id"], entitlement_revision=kwargs["expected_entitlement_revision"],
            entitlement_fingerprint=kwargs["expected_entitlement_fingerprint"], as_of=kwargs["as_of"],
            window_start=kwargs["as_of"].replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            window_end=kwargs["as_of"], observation_count=len(self.value),
            observation_fingerprints=tuple(item.fingerprint for item in self.value), observations=self.value,
        )


def pending_entitlement() -> WilsyAIEntitlement:
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    return WilsyAIEntitlement(
        tenant_id="tenant-p6c",
        entitlement_id="entitlement-p6c",
        module_id="module-p6c",
        module_name="Owner Inbox",
        tier=WilsyAITier.STARTER,
        policy_fingerprint=policy.policy_fingerprint,
        lifecycle_state=WilsyAIEntitlementState.PENDING_SOURCE,
        source_requirements=("records",),
        capability_grants=("ai.summary",),
        source_readiness_evidence_reference="ready",
        source_readiness_evidence_fingerprint=FP,
    )


def active_entitlement() -> WilsyAIEntitlement:
    return pending_entitlement().transition(
        WilsyAIEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activation-evidence",
        evidence_fingerprint=FP,
        occurred_at=ACTIVATED_AT,
    )


def observation(entitlement: WilsyAIEntitlement) -> WilsyAIUsageObservation:
    return WilsyAIUsageObservation(
        entitlement.tenant_id,
        "usage-p6c",
        entitlement.entitlement_id,
        entitlement.lifecycle_revision,
        entitlement.fingerprint,
        entitlement.module_id,
        2,
        10,
        20,
        1,
        datetime(2026, 9, 12, 11, tzinfo=timezone.utc),
        "source-p6c",
        FP,
    )


def owner(
    entitlement: WilsyAIEntitlement,
    observations: tuple[WilsyAIUsageObservation, ...] = (),
    *,
    entitlement_error: Exception | None = None,
    observation_error: Exception | None = None,
) -> tuple[WilsyAIUsageCapacityOrchestrator, EntitlementRegistry, ObservationRegistry]:
    entitlement_registry = EntitlementRegistry(entitlement, entitlement_error)
    observation_registry = ObservationRegistry(observations, observation_error)
    return (
        WilsyAIUsageCapacityOrchestrator(
            entitlement_registry=entitlement_registry,
            observation_registry=observation_registry,
        ),
        entitlement_registry,
        observation_registry,
    )


def test_canonical_p4_identity_and_same_session_reach_frozen_p6a() -> None:
    entitlement = active_entitlement()
    orchestrator, p4, p6b = owner(entitlement, (observation(entitlement),))
    session = Session()
    capacity = orchestrator.derive_capacity(
        tenant_id=entitlement.tenant_id,
        entitlement_id=entitlement.entitlement_id,
        as_of=AS_OF,
        session=session,
    )
    assert capacity.daily_consumed_request_units == 2
    assert capacity.monthly_consumed_automation_actions == 1
    assert p4.calls[0] == {
        "tenant_id": entitlement.tenant_id,
        "entitlement_id": entitlement.entitlement_id,
        "session": session,
    }
    assert p6b.calls[0] == {
        "tenant_id": entitlement.tenant_id,
        "entitlement_id": entitlement.entitlement_id,
        "module_id": entitlement.module_id,
        "expected_entitlement_revision": entitlement.lifecycle_revision,
        "expected_entitlement_fingerprint": entitlement.fingerprint,
        "as_of": AS_OF,
        "session": session,
    }


def test_caller_transaction_ownership_and_empty_complete_window_derives_zero() -> None:
    entitlement = active_entitlement()
    orchestrator, _, _ = owner(entitlement)
    session = Session()
    result = orchestrator.derive_capacity(tenant_id=entitlement.tenant_id, entitlement_id=entitlement.entitlement_id, as_of=AS_OF, session=session)
    assert result.daily_consumed_request_units == 0 and result.monthly_consumed_automation_actions == 0
    assert session.in_transaction is True
    assert not any(name in dir(orchestrator) for name in ("start_transaction", "commit", "abort", "retry_transaction"))


def test_inactive_entitlement_rejection_is_preserved_from_p6a() -> None:
    entitlement = pending_entitlement()
    orchestrator, _, _ = owner(entitlement, (observation(entitlement),))
    with pytest.raises(WilsyAIUsageCapacityError, match="M13P6A_ENTITLEMENT_NOT_ACTIVE"):
        orchestrator.derive_capacity(
            tenant_id=entitlement.tenant_id,
            entitlement_id=entitlement.entitlement_id,
            as_of=AS_OF,
            session=Session(),
        )


def test_p4_and_p6b_governed_failures_are_not_reinterpreted() -> None:
    entitlement = active_entitlement()
    p4_error = WilsyAIEntitlementRegistryError("M13P4_PERSISTENCE_UNAVAILABLE")
    orchestrator, _, _ = owner(entitlement, entitlement_error=p4_error)
    with pytest.raises(WilsyAIEntitlementRegistryError, match="M13P4_PERSISTENCE_UNAVAILABLE"):
        orchestrator.derive_capacity(tenant_id=entitlement.tenant_id, entitlement_id=entitlement.entitlement_id, as_of=AS_OF, session=Session())

    p6b_error = WilsyAIUsageObservationRegistryError("M13P6B_PERSISTENCE_UNAVAILABLE")
    orchestrator, _, _ = owner(entitlement, observation_error=p6b_error)
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P6B_PERSISTENCE_UNAVAILABLE"):
        orchestrator.derive_capacity(tenant_id=entitlement.tenant_id, entitlement_id=entitlement.entitlement_id, as_of=AS_OF, session=Session())


@pytest.mark.parametrize(
    ("tenant_id", "entitlement_id", "as_of", "session", "code"),
    [
        ("default", "entitlement-p6c", AS_OF, Session(), "M13P6C_TENANT_FORBIDDEN"),
        ("tenant-p6c", "", AS_OF, Session(), "M13P6C_ENTITLEMENT_ID_REQUIRED"),
        ("tenant-p6c", "entitlement-p6c", datetime(2026, 9, 12, 12), Session(), "M13P6C_AS_OF_INVALID"),
        ("tenant-p6c", "entitlement-p6c", AS_OF, Session(), "M13P6C_TRANSACTION_REQUIRED"),
    ],
)
def test_explicit_boundary_inputs_fail_closed(
    tenant_id: str,
    entitlement_id: str,
    as_of: datetime,
    session: Session,
    code: str,
) -> None:
    if code == "M13P6C_TRANSACTION_REQUIRED":
        session.in_transaction = False  # type: ignore[misc]
    orchestrator, _, _ = owner(active_entitlement(), (observation(active_entitlement()),))
    with pytest.raises(WilsyAIUsageCapacityOrchestratorError, match=code):
        orchestrator.derive_capacity(tenant_id=tenant_id, entitlement_id=entitlement_id, as_of=as_of, session=session)


def test_no_quota_commercial_or_financial_authority_surface() -> None:
    names = set(dir(WilsyAIUsageCapacityOrchestrator))
    assert not names.intersection({"aggregate", "quota", "overage", "invoice", "payment", "execute", "settle", "persist"})


# ARTIFACT: test_wilsy_ai_usage_capacity_orchestrator.py
# VERSION: v1.1.0-M13-P6C
# AUTHORITY BOUNDARY: P4/P6B/P6A composition certificate only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
