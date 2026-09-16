"""TITLE: WILSY AI Reasoning Entitlement Provisioning Authority.
VERSION: v1.0.0-C1B-R2
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Explicitly provisions the canonical P4 WILSY_AI_REASONING entitlement
         and never activates it from HTTP input or module presence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/wilsy_ai_entitlement_provisioning.py
COLLABORATION / OWNERSHIP: P4 entitlement domain/registry remain canonical;
                            this is a narrow explicit provisioning adapter.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1B-R2 establishes explicit tenant-bound provisioning.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Server-owned tenant and evidence inputs only.
TENANT BOUNDARY: Tenant identity is explicit and never caller-inferred.
AUTHORITY BOUNDARY: Entitlement provisioning only; no admission or execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Missing authoritative evidence and divergent replay deny.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final

from tools.eos.saas.billing.wilsy_ai_commercial_policy import WilsyAITier, get_wilsy_ai_commercial_policy
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlement, WilsyAIEntitlementState

VERSION: Final[str] = "v1.0.0-C1B-R2"
MODULE_ID: Final[str] = "WILSY_AI_REASONING"


class WilsyAIReasoningEntitlementProvisioningError(ValueError):
    """Raised when explicit provisioning evidence is incomplete or invalid."""


def provision_wilsy_ai_reasoning_entitlement(*, registry: Any, tenant_id: str, entitlement_id: str, tier: WilsyAITier | str, source_evidence_reference: str, source_evidence_fingerprint: str, idempotency_key: str, session: Any, module_name: str = "WILSY AI Reasoning", source_requirements: tuple[str, ...] = ("explicit_authoritative_provisioning",), capability_grants: tuple[str, ...] = ("wilsy_ai.reasoning.execute.v1",)) -> WilsyAIEntitlement:
    """Create or replay a P4 pending entitlement; caller controls transaction."""
    if registry is None or session is None or not isinstance(tenant_id, str) or tenant_id.casefold() in {"default", "global", "root", "*"}:
        raise WilsyAIReasoningEntitlementProvisioningError("C1B_ENTITLEMENT_INPUT_INVALID")
    try:
        tier_value = WilsyAITier(tier)
        policy = get_wilsy_ai_commercial_policy(tier_value)
        entitlement = WilsyAIEntitlement(
            tenant_id=tenant_id, entitlement_id=entitlement_id, module_id=MODULE_ID,
            module_name=module_name, tier=tier_value, policy_fingerprint=policy.policy_fingerprint,
            lifecycle_state=WilsyAIEntitlementState.PENDING_SOURCE,
            source_requirements=source_requirements, capability_grants=capability_grants,
            source_readiness_evidence_reference=source_evidence_reference,
            source_readiness_evidence_fingerprint=source_evidence_fingerprint,
        )
        return registry.create_or_replay(entitlement, idempotency_key=idempotency_key, session=session)
    except Exception as error:
        if isinstance(error, WilsyAIReasoningEntitlementProvisioningError):
            raise
        raise WilsyAIReasoningEntitlementProvisioningError("C1B_ENTITLEMENT_PROVISIONING_REJECTED") from error


def activate_wilsy_ai_reasoning_entitlement(*, registry: Any, entitlement: WilsyAIEntitlement, activation_evidence_reference: str, activation_evidence_fingerprint: str, occurred_at: datetime, session: Any) -> WilsyAIEntitlement:
    """Activate only through canonical P4 evidence-backed CAS transition."""
    if not isinstance(entitlement, WilsyAIEntitlement) or entitlement.module_id != MODULE_ID or session is None:
        raise WilsyAIReasoningEntitlementProvisioningError("C1B_ENTITLEMENT_ACTIVATION_INVALID")
    try:
        return registry.transition(tenant_id=entitlement.tenant_id, entitlement_id=entitlement.entitlement_id, target_state=WilsyAIEntitlementState.ACTIVE, expected_revision=entitlement.lifecycle_revision, evidence_reference=activation_evidence_reference, evidence_fingerprint=activation_evidence_fingerprint, occurred_at=occurred_at, session=session)
    except Exception as error:
        raise WilsyAIReasoningEntitlementProvisioningError("C1B_ENTITLEMENT_ACTIVATION_REJECTED") from error


__all__ = ["VERSION", "MODULE_ID", "WilsyAIReasoningEntitlementProvisioningError", "provision_wilsy_ai_reasoning_entitlement", "activate_wilsy_ai_reasoning_entitlement"]

# ARTIFACT: wilsy_ai_entitlement_provisioning.py
# VERSION: v1.0.0-C1B-R2
# AUTHORITY BOUNDARY: explicit P4 entitlement provisioning only
# TENANT POSTURE: tenant identity is server-bound and exact
# FAIL-CLOSED POSTURE: no request self-activation; P4 CAS preserved
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
