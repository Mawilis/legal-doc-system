"""TITLE: Platform Billing Provider Policy. VERSION: v1.0.0-M11E2D5C2F.
AUTHORITY: Kennel EOS policy eligibility evidence only.
EPITOME: Immutable tenant-scoped outbound provider-policy revisions.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/domain/platform_billing_provider_policy.py
COLLABORATION / OWNERSHIP: Kennel EOS platform policy domain.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes immutable provider eligibility revisions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque provider identifiers; no secrets.
TENANT BOUNDARY: Every policy is scoped to one tenant.
AUTHORITY BOUNDARY: Eligibility only; no routing or execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains execution authority.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib, json

VERSION = "v1.0.0-M11E2D5C2F"
class PolicyStatus(StrEnum): ACTIVE="ACTIVE"; REVOKED="REVOKED"
class PlatformBillingProviderPolicyError(ValueError): pass

@dataclass(frozen=True, slots=True)
class PlatformBillingProviderPolicy:
    policy_id: str; tenant_id: str; lane: str; authorized_provider_names: tuple[str,...]; policy_revision: int; policy_authorization_reference: str; effective_at: datetime; expires_at: datetime|None; created_at: datetime; status: PolicyStatus; policy_fingerprint: str = ""
    def __post_init__(self):
        for n in ("policy_id","tenant_id","policy_authorization_reference"):
            v=getattr(self,n)
            if not isinstance(v,str) or not v.strip(): raise PlatformBillingProviderPolicyError(f"{n} is invalid")
        if self.lane != "PLATFORM_BILLING_OUTBOUND": raise PlatformBillingProviderPolicyError("lane is invalid")
        if not isinstance(self.authorized_provider_names,tuple) or not self.authorized_provider_names or any(not isinstance(x,str) or not x.strip() for x in self.authorized_provider_names) or len(set(self.authorized_provider_names)) != len(self.authorized_provider_names): raise PlatformBillingProviderPolicyError("providers are invalid")
        if not isinstance(self.policy_revision,int) or isinstance(self.policy_revision,bool) or self.policy_revision < 1: raise PlatformBillingProviderPolicyError("revision is invalid")
        for t in (self.effective_at,self.created_at):
            if not isinstance(t,datetime) or t.tzinfo is None: raise PlatformBillingProviderPolicyError("timestamp is invalid")
        if self.expires_at is not None and (self.expires_at.tzinfo is None or self.expires_at <= self.effective_at): raise PlatformBillingProviderPolicyError("expiry is invalid")
        if not isinstance(self.status,PolicyStatus): raise PlatformBillingProviderPolicyError("status is invalid")
        expected=self.derive_fingerprint()
        if self.policy_fingerprint and self.policy_fingerprint != expected: raise PlatformBillingProviderPolicyError("fingerprint is invalid")
        object.__setattr__(self,"policy_fingerprint",expected)
    def canonical_payload(self):
        return {"policy_id":self.policy_id,"tenant_id":self.tenant_id,"lane":self.lane,"authorized_provider_names":self.authorized_provider_names,"policy_revision":self.policy_revision,"policy_authorization_reference":self.policy_authorization_reference,"effective_at":self.effective_at.astimezone(timezone.utc).isoformat(),"expires_at":self.expires_at.astimezone(timezone.utc).isoformat() if self.expires_at else None,"created_at":self.created_at.astimezone(timezone.utc).isoformat(),"status":self.status.value}
    def derive_fingerprint(self): return hashlib.sha3_512(json.dumps(self.canonical_payload(),sort_keys=True,separators=(",",":"),default=list).encode()).hexdigest()
    def to_persisted(self): return {**self.canonical_payload(),"authorized_provider_names":list(self.authorized_provider_names),"policy_fingerprint":self.policy_fingerprint}

# ARTIFACT: platform_billing_provider_policy.py
# VERSION: v1.0.0-M11E2D5C2F
# AUTHORITY BOUNDARY: policy eligibility only; no routing or execution
# TENANT POSTURE: exact tenant scope
# FAIL-CLOSED POSTURE: malformed and corrupt policy facts reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
