"""TITLE: Authorized Platform Billing Provider Policy Issuance. VERSION: v1.0.0-M11E2D5C2F.
AUTHORITY: Kennel EOS; consumes durable tenant authorization evidence.
EPITOME: Creates immutable outbound provider-policy revision one.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/orchestration/platform_billing_provider_policy_issuance.py
COLLABORATION / OWNERSHIP: Kennel EOS policy orchestration.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes evidence-gated policy issuance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Evidence and policy tenant must match.
AUTHORITY BOUNDARY: No routing, provider execution, or settlement.
"""
from datetime import datetime
from typing import Any
from ..domain.platform_billing_provider_policy import PlatformBillingProviderPolicy, PolicyStatus
class PlatformBillingProviderPolicyIssuanceError(RuntimeError): pass
def issue_platform_billing_provider_policy(*, authorization_evidence: Any, tenant_id: str, provider_names: tuple[str,...], subject_reference: str, subject_fingerprint: str, collection: Any, policy_id: str, effective_at: datetime, created_at: datetime, session: Any=None) -> PlatformBillingProviderPolicy:
    """Issue revision one only from matching durable CREATE authorization evidence."""
    if authorization_evidence is None or getattr(authorization_evidence,"tenant_id",None)!=tenant_id or getattr(authorization_evidence,"permission",None)!="platform_billing:provider_policy:admin" or getattr(authorization_evidence,"operation",None)!="platform_billing_provider_policy_create" or getattr(authorization_evidence,"subject_reference",None)!=subject_reference or getattr(authorization_evidence,"subject_evidence_fingerprint",None)!=subject_fingerprint: raise PlatformBillingProviderPolicyIssuanceError("ADMIN_AUTHORIZATION_EVIDENCE_INVALID")
    policy=PlatformBillingProviderPolicy(policy_id=policy_id,tenant_id=tenant_id,lane="PLATFORM_BILLING_OUTBOUND",authorized_provider_names=provider_names,policy_revision=1,policy_authorization_reference=authorization_evidence.authorization_decision_id,effective_at=effective_at,expires_at=None,created_at=created_at,status=PolicyStatus.ACTIVE)
    from ..registry.platform_billing_provider_policy_registry import PlatformBillingProviderPolicyRegistry
    return PlatformBillingProviderPolicyRegistry.create(policy,collection,session=session)
# ARTIFACT: platform_billing_provider_policy_issuance.py
# VERSION: v1.0.0-M11E2D5C2F
# AUTHORITY BOUNDARY: authorization-evidence-gated policy issuance only
# TENANT POSTURE: exact evidence/policy tenant continuity
# FAIL-CLOSED POSTURE: missing or mismatched evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
