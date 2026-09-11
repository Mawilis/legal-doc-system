"""TITLE: Platform Billing Provider Policy Runtime Binding.
VERSION: v1.0.0-M11E2D5C2G-P2B-R1.
AUTHORITY: Kennel EOS runtime policy designation evidence only.
EPITOME: Immutable tenant/lane binding to one exact policy revision.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/domain/platform_billing_provider_policy_runtime_binding.py
COLLABORATION / OWNERSHIP: Kennel EOS platform policy authority.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes immutable runtime binding facts.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant and outbound lane are mandatory.
AUTHORITY BOUNDARY: Designation only; no request, routing, execution, or settlement.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib, json
class PlatformBillingProviderPolicyRuntimeBindingError(ValueError): pass
@dataclass(frozen=True, slots=True)
class PlatformBillingProviderPolicyRuntimeBinding:
    binding_id:str; tenant_id:str; lane:str; binding_revision:int; provider_policy_id:str; provider_policy_revision:int; provider_policy_fingerprint:str; activation_authorization_evidence_id:str; activation_authorization_evidence_fingerprint:str; previous_binding_id:str|None; previous_binding_fingerprint:str|None; activated_at:datetime; created_at:datetime; binding_fingerprint:str=""
    def __post_init__(self):
        for n in ("binding_id","tenant_id","provider_policy_id","provider_policy_fingerprint","activation_authorization_evidence_id","activation_authorization_evidence_fingerprint"):
            if not isinstance(getattr(self,n),str) or not getattr(self,n).strip(): raise PlatformBillingProviderPolicyRuntimeBindingError(f"{n} is invalid")
        if self.lane!="PLATFORM_BILLING_OUTBOUND" or self.binding_revision<1 or self.provider_policy_revision<1: raise PlatformBillingProviderPolicyRuntimeBindingError("binding identity is invalid")
        if any(not isinstance(t,datetime) or t.tzinfo is None for t in (self.activated_at,self.created_at)): raise PlatformBillingProviderPolicyRuntimeBindingError("timestamp is invalid")
        expected=self.derive_fingerprint()
        if self.binding_fingerprint and self.binding_fingerprint!=expected: raise PlatformBillingProviderPolicyRuntimeBindingError("fingerprint is invalid")
        object.__setattr__(self,"binding_fingerprint",expected)
    def payload(self):
        return {"binding_id":self.binding_id,"tenant_id":self.tenant_id,"lane":self.lane,"binding_revision":self.binding_revision,"provider_policy_id":self.provider_policy_id,"provider_policy_revision":self.provider_policy_revision,"provider_policy_fingerprint":self.provider_policy_fingerprint,"activation_authorization_evidence_id":self.activation_authorization_evidence_id,"activation_authorization_evidence_fingerprint":self.activation_authorization_evidence_fingerprint,"previous_binding_id":self.previous_binding_id,"previous_binding_fingerprint":self.previous_binding_fingerprint,"activated_at":self.activated_at.astimezone(timezone.utc).isoformat(),"created_at":self.created_at.astimezone(timezone.utc).isoformat()}
    def to_persisted(self): return {**self.payload(),"binding_fingerprint":self.binding_fingerprint}
    def derive_fingerprint(self): return hashlib.sha3_512(json.dumps(self.payload(),sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
# ARTIFACT: platform_billing_provider_policy_runtime_binding.py
# VERSION: v1.0.0-M11E2D5C2G-P2B-R1
# AUTHORITY BOUNDARY: runtime designation only
# TENANT POSTURE: exact tenant/lane scope
# FAIL-CLOSED POSTURE: malformed and corrupt facts reject
# END OF WILSY OS SOVEREIGN ARTIFACT
