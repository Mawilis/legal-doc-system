"""TITLE: Platform Billing Provider-Policy Runtime Binding Orchestration.
VERSION: v1.0.0-M11E2D5C2G-P2B-R3.
AUTHORITY: Kennel EOS authorized ACTIVATE transition.
EPITOME: Resolves durable policy and authorization before creating a binding.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/orchestration/platform_billing_provider_policy_runtime_binding.py
COLLABORATION / OWNERSHIP: Kennel EOS policy runtime authority.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes durable ACTIVATE-to-binding chain.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant/policy/lane scope is enforced.
AUTHORITY BOUNDARY: Runtime designation only; no routing or execution.
"""
from datetime import datetime
from typing import Any
from ..domain.platform_billing_provider_policy_revision_authorization_subject import PlatformBillingProviderPolicyRevisionAuthorizationSubject
from ..domain.platform_billing_provider_policy_runtime_binding import PlatformBillingProviderPolicyRuntimeBinding
from ..registry.platform_billing_provider_policy_registry import PlatformBillingProviderPolicyRegistry
from ..registry.platform_billing_provider_policy_runtime_binding_registry import PlatformBillingProviderPolicyRuntimeBindingRegistry

class PlatformBillingProviderPolicyRuntimeBindingOrchestrationError(RuntimeError): pass

def bind_platform_billing_provider_policy_runtime(*, tenant_id: str, policy_id: str, policy_revision: int, authorization_decision_id: str, policy_collection: Any, authorization_registry: Any, binding_collection: Any, binding_id: str, activated_at: datetime, created_at: datetime, session: Any=None) -> PlatformBillingProviderPolicyRuntimeBinding:
    """Create an immutable binding from exact durable policy and ACTIVATE evidence."""
    try:
        policy=PlatformBillingProviderPolicyRegistry.get(tenant_id,policy_id,policy_collection,revision=policy_revision,session=session)
        if policy is None: raise PlatformBillingProviderPolicyRuntimeBindingOrchestrationError("POLICY_NOT_FOUND")
        subject=PlatformBillingProviderPolicyRevisionAuthorizationSubject.from_policy(policy)
        evidence=authorization_registry.get(tenant_id=tenant_id,authorization_decision_id=authorization_decision_id,session=session)
        if getattr(evidence,"tenant_id",None)!=tenant_id or getattr(evidence,"authorization_decision_id",None)!=authorization_decision_id or evidence.operation!="platform_billing_provider_policy_activate" or evidence.permission!="platform_billing:provider_policy:admin" or evidence.subject_reference!=subject.subject_reference or evidence.subject_evidence_fingerprint!=subject.subject_evidence_fingerprint:
            raise PlatformBillingProviderPolicyRuntimeBindingOrchestrationError("ACTIVATE_EVIDENCE_INVALID")
        current=PlatformBillingProviderPolicyRuntimeBindingRegistry.current(tenant_id,policy.lane,binding_collection,session=session)
        revision=1 if current is None else current.binding_revision+1
        binding=PlatformBillingProviderPolicyRuntimeBinding(binding_id=binding_id,tenant_id=tenant_id,lane=policy.lane,binding_revision=revision,provider_policy_id=policy.policy_id,provider_policy_revision=policy.policy_revision,provider_policy_fingerprint=policy.policy_fingerprint,activation_authorization_evidence_id=evidence.authorization_decision_id,activation_authorization_evidence_fingerprint=evidence.subject_evidence_fingerprint,previous_binding_id=None if current is None else current.binding_id,previous_binding_fingerprint=None if current is None else current.binding_fingerprint,activated_at=activated_at,created_at=created_at)
        return PlatformBillingProviderPolicyRuntimeBindingRegistry.create(binding,binding_collection,session=session)
    except PlatformBillingProviderPolicyRuntimeBindingOrchestrationError: raise
    except Exception as error: raise PlatformBillingProviderPolicyRuntimeBindingOrchestrationError("RUNTIME_BINDING_FAILED") from error

# ARTIFACT: platform_billing_provider_policy_runtime_binding.py
# VERSION: v1.0.0-M11E2D5C2G-P2B-R3
# AUTHORITY BOUNDARY: authorized runtime designation only
# TENANT POSTURE: exact tenant/lane scope
# FAIL-CLOSED POSTURE: absent or mismatched evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
