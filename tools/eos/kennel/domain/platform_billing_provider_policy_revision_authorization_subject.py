"""TITLE: Platform Billing Provider-Policy Revision Authorization Subject.
VERSION: v1.0.0-M11E2D5C2G-P2B-S1.
AUTHORITY: Kennel EOS canonical subject provenance.
EPITOME: Deterministically binds tenant and exact provider-policy revision.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/domain/platform_billing_provider_policy_revision_authorization_subject.py
COLLABORATION / OWNERSHIP: Kennel EOS policy authorization boundary.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes revision-bound activation subjects.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Tenant is cryptographically bound.
AUTHORITY BOUNDARY: Subject evidence only; does not authorize or persist.
"""
from dataclasses import dataclass
import hashlib, json
from .platform_billing_provider_policy import PlatformBillingProviderPolicy
@dataclass(frozen=True, slots=True)
class PlatformBillingProviderPolicyRevisionAuthorizationSubject:
    tenant_id:str; provider_policy_id:str; provider_policy_revision:int; provider_policy_fingerprint:str; lane:str="PLATFORM_BILLING_OUTBOUND"
    @classmethod
    def from_policy(cls, policy: PlatformBillingProviderPolicy):
        if not isinstance(policy,PlatformBillingProviderPolicy): raise TypeError("policy is invalid")
        return cls(policy.tenant_id,policy.policy_id,policy.policy_revision,policy.policy_fingerprint,policy.lane)
    def payload(self): return {"schema":"WILSY-PLATFORM-POLICY-REVISION-SUBJECT/V1","tenant_id":self.tenant_id,"provider_policy_id":self.provider_policy_id,"provider_policy_revision":self.provider_policy_revision,"provider_policy_fingerprint":self.provider_policy_fingerprint,"lane":self.lane}
    @property
    def subject_reference(self): return "platform-policy-revision:"+self.tenant_id+":"+self.provider_policy_id+":"+str(self.provider_policy_revision)
    @property
    def subject_evidence_fingerprint(self): return hashlib.sha3_512(json.dumps(self.payload(),sort_keys=True,separators=(",",":")).encode()).hexdigest()
# ARTIFACT: platform_billing_provider_policy_revision_authorization_subject.py
# VERSION: v1.0.0-M11E2D5C2G-P2B-S1
# AUTHORITY BOUNDARY: canonical subject provenance only
# TENANT POSTURE: exact tenant/policy revision scope
# FAIL-CLOSED POSTURE: non-policy inputs reject
# END OF WILSY OS SOVEREIGN ARTIFACT
