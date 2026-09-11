"""TITLE: Accounts Payable Provider Policy Runtime Binding.
VERSION: v1.0.0-M11E2C3.
AUTHORITY: Kennel EOS AP current-policy designation.
EPITOME: Immutable tenant-scoped binding to one exact AP policy revision.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/domain/accounts_payable_provider_policy_runtime_binding.py
COLLABORATION / OWNERSHIP: Kennel EOS AP runtime authority.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes AP binding facts.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant and AP family are mandatory.
AUTHORITY BOUNDARY: Currentness only; no provider selection or execution.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib, json
AP_POLICY_FAMILY="ACCOUNTS_PAYABLE"
class AccountsPayableProviderPolicyRuntimeBindingError(ValueError): pass
@dataclass(frozen=True, slots=True)
class AccountsPayableProviderPolicyRuntimeBinding:
    binding_id:str; tenant_id:str; binding_revision:int; provider_policy_id:str; provider_policy_revision:int; provider_policy_fingerprint:str; activation_authorization_evidence_id:str; activation_authorization_evidence_fingerprint:str; previous_binding_id:str|None; previous_binding_fingerprint:str|None; activated_at:datetime; created_at:datetime; binding_fingerprint:str=""; family:str=AP_POLICY_FAMILY
    def __post_init__(self):
        for n in ("binding_id","tenant_id","provider_policy_id","provider_policy_fingerprint","activation_authorization_evidence_id","activation_authorization_evidence_fingerprint"):
            if not isinstance(getattr(self,n),str) or not getattr(self,n).strip(): raise AccountsPayableProviderPolicyRuntimeBindingError(f"{n} is invalid")
        if self.family!=AP_POLICY_FAMILY or self.binding_revision<1 or self.provider_policy_revision<1: raise AccountsPayableProviderPolicyRuntimeBindingError("binding identity is invalid")
        if any(not isinstance(t,datetime) or t.tzinfo is None for t in (self.activated_at,self.created_at)): raise AccountsPayableProviderPolicyRuntimeBindingError("timestamp is invalid")
        expected=self.derive_fingerprint()
        if self.binding_fingerprint and self.binding_fingerprint!=expected: raise AccountsPayableProviderPolicyRuntimeBindingError("fingerprint is invalid")
        object.__setattr__(self,"binding_fingerprint",expected)
    def payload(self): return {"binding_id":self.binding_id,"tenant_id":self.tenant_id,"family":self.family,"binding_revision":self.binding_revision,"provider_policy_id":self.provider_policy_id,"provider_policy_revision":self.provider_policy_revision,"provider_policy_fingerprint":self.provider_policy_fingerprint,"activation_authorization_evidence_id":self.activation_authorization_evidence_id,"activation_authorization_evidence_fingerprint":self.activation_authorization_evidence_fingerprint,"previous_binding_id":self.previous_binding_id,"previous_binding_fingerprint":self.previous_binding_fingerprint,"activated_at":self.activated_at.astimezone(timezone.utc).isoformat(),"created_at":self.created_at.astimezone(timezone.utc).isoformat()}
    def derive_fingerprint(self): return hashlib.sha3_512(json.dumps(self.payload(),sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
    def to_persisted(self): return {**self.payload(),"binding_fingerprint":self.binding_fingerprint}
# ARTIFACT: accounts_payable_provider_policy_runtime_binding.py
# VERSION: v1.0.0-M11E2C3
# AUTHORITY BOUNDARY: AP currentness only; no selection or execution
# TENANT POSTURE: exact tenant/family scope
# FAIL-CLOSED POSTURE: malformed and corrupt facts reject
# END OF WILSY OS SOVEREIGN ARTIFACT
