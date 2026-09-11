"""TITLE: Accounts Payable Provider Policy Runtime Binding Orchestration.
VERSION: v1.0.3-M11E2C3-R4F-R2-R1.
AUTHORITY: Kennel EOS exact ACTIVATE transition.
EPITOME: Binds one exact AP policy revision as current.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/orchestration/accounts_payable_provider_policy_runtime_binding.py
COLLABORATION / OWNERSHIP: Kennel EOS AP runtime authority.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.3-M11E2C3-R4F-R2-R1 rejects reuse of consumed activation authorization evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant and policy provenance are enforced.
AUTHORITY BOUNDARY: Currentness only; no provider selection or execution.
"""
from datetime import datetime
from typing import Any
import hashlib
from ..domain.accounts_payable_provider_policy_runtime_binding import AccountsPayableProviderPolicyRuntimeBinding
from ..registry.accounts_payable_provider_policy_registry import AccountsPayableProviderPolicyRegistry
from ..domain.accounts_payable_provider_policy import AP_POLICY_FAMILY
from ..registry.accounts_payable_provider_policy_runtime_binding_registry import AccountsPayableProviderPolicyRuntimeBindingRegistry
class AccountsPayableProviderPolicyRuntimeBindingOrchestrationError(RuntimeError): pass
def bind_accounts_payable_provider_policy_runtime(*,tenant_id:str,policy_id:str,policy_revision:int,authorization_decision_id:str,policy_collection:Any,authorization_registry:Any,binding_collection:Any,binding_id:str,activated_at:datetime,created_at:datetime,session:Any=None)->AccountsPayableProviderPolicyRuntimeBinding:
    if session is None or getattr(session,'in_transaction',False) is not True:raise AccountsPayableProviderPolicyRuntimeBindingOrchestrationError('ACTIVE_TRANSACTION_REQUIRED')
    policy=AccountsPayableProviderPolicyRegistry.get(tenant_id,policy_id,policy_collection,revision=policy_revision,session=session)
    evidence=authorization_registry.get(tenant_id=tenant_id,authorization_decision_id=authorization_decision_id,session=session)
    subject=f'accounts-payable-provider-policy:{tenant_id}:{policy_id}:{policy_revision}'
    expected_subject_fingerprint=hashlib.sha3_512(subject.encode()).hexdigest()
    if getattr(evidence,'operation',None)!='accounts_payable_provider_policy_activate' or getattr(evidence,'permission',None)!='accounts_payable:provider_policy:admin' or getattr(evidence,'tenant_id',None)!=tenant_id or getattr(evidence,'subject_reference',None)!=subject or getattr(evidence,'subject_evidence_fingerprint',None)!=expected_subject_fingerprint:raise AccountsPayableProviderPolicyRuntimeBindingOrchestrationError('ACTIVATE_EVIDENCE_INVALID')
    current=AccountsPayableProviderPolicyRuntimeBindingRegistry.current(tenant_id,binding_collection,session=session)
    if current is not None and (current.tenant_id, current.family, current.provider_policy_id, current.provider_policy_revision, current.provider_policy_fingerprint)==(policy.tenant_id, AP_POLICY_FAMILY, policy.policy_id, policy.policy_revision, policy.policy_fingerprint):
        raise AccountsPayableProviderPolicyRuntimeBindingOrchestrationError('ALREADY_CURRENT_POLICY_REPLAY')
    if current is None and AccountsPayableProviderPolicyRuntimeBindingRegistry.has_history(tenant_id,binding_collection,session=session):
        raise AccountsPayableProviderPolicyRuntimeBindingOrchestrationError('FAIL_CLOSED_INCONSISTENT_CURRENTNESS')
    if AccountsPayableProviderPolicyRuntimeBindingRegistry.has_consumed_activation_authorization(tenant_id, evidence.authorization_decision_id, evidence.subject_evidence_fingerprint, binding_collection, session=session):
        raise AccountsPayableProviderPolicyRuntimeBindingOrchestrationError('CONSUMED_ACTIVATION_AUTHORIZATION_REPLAY')
    rev=1 if current is None else current.binding_revision+1
    binding=AccountsPayableProviderPolicyRuntimeBinding(binding_id=binding_id,tenant_id=tenant_id,binding_revision=rev,provider_policy_id=policy_id,provider_policy_revision=policy_revision,provider_policy_fingerprint=policy.policy_fingerprint,activation_authorization_evidence_id=evidence.authorization_decision_id,activation_authorization_evidence_fingerprint=evidence.subject_evidence_fingerprint,previous_binding_id=None if current is None else current.binding_id,previous_binding_fingerprint=None if current is None else current.binding_fingerprint,activated_at=activated_at,created_at=created_at)
    return AccountsPayableProviderPolicyRuntimeBindingRegistry.create(binding,binding_collection,session=session)
# ARTIFACT: accounts_payable_provider_policy_runtime_binding.py
# VERSION: v1.0.3-M11E2C3-R4F-R2-R1
# AUTHORITY BOUNDARY: exact AP ACTIVATE currentness transition
# TENANT POSTURE: tenant/policy/evidence continuity
# FAIL-CLOSED POSTURE: absent or mismatched evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
