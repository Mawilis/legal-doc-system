"""TITLE: Platform Billing Provider Routing Decision.
VERSION: v1.0.0-M11-P4.
AUTHORITY: Kennel EOS / Wilsy OS Core Governance.
EPITOME: Immutable provider selection derived from historical request policy.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/domain/platform_billing_provider_routing_decision.py
COLLABORATION / OWNERSHIP: Kennel EOS routing authority.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes deterministic single-provider routing evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped opaque identifiers; no secrets.
TENANT BOUNDARY: Every decision is tenant scoped.
AUTHORITY BOUNDARY: Selects provider only; never executes funds.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS execution remains separate.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib, json

@dataclass(frozen=True, slots=True)
class PlatformBillingProviderRoutingDecision:
    tenant_id: str
    routing_decision_id: str
    source_execution_request_id: str
    source_execution_request_fingerprint: str
    source_provider_policy_id: str
    source_provider_policy_revision: int
    source_provider_policy_fingerprint: str
    selected_provider: str
    decided_at: datetime
    routing_decision_fingerprint: str = ""

    def __post_init__(self) -> None:
        if not all(isinstance(getattr(self, n), str) and getattr(self, n).strip() for n in ("tenant_id","routing_decision_id","source_execution_request_id","source_execution_request_fingerprint","source_provider_policy_id","source_provider_policy_fingerprint","selected_provider")):
            raise ValueError("routing identity is invalid")
        if not isinstance(self.source_provider_policy_revision, int) or self.source_provider_policy_revision < 1: raise ValueError("policy revision is invalid")
        if not isinstance(self.decided_at, datetime) or self.decided_at.tzinfo is None: raise ValueError("decided_at is invalid")
        expected=self.derive_fingerprint()
        if self.routing_decision_fingerprint and self.routing_decision_fingerprint != expected: raise ValueError("routing fingerprint is invalid")
        object.__setattr__(self,"decided_at",self.decided_at.astimezone(timezone.utc))
        object.__setattr__(self,"routing_decision_fingerprint",expected)

    def payload(self) -> dict[str, object]:
        return {"tenant_id":self.tenant_id,"routing_decision_id":self.routing_decision_id,"source_execution_request_id":self.source_execution_request_id,"source_execution_request_fingerprint":self.source_execution_request_fingerprint,"source_provider_policy_id":self.source_provider_policy_id,"source_provider_policy_revision":self.source_provider_policy_revision,"source_provider_policy_fingerprint":self.source_provider_policy_fingerprint,"selected_provider":self.selected_provider,"decided_at":self.decided_at.isoformat()}
    def derive_fingerprint(self) -> str: return hashlib.sha3_512(json.dumps(self.payload(),sort_keys=True,separators=(",",":")).encode()).hexdigest()
    def to_persisted(self) -> dict[str, object]: return {**self.payload(),"routing_decision_fingerprint":self.routing_decision_fingerprint}

# ARTIFACT: platform_billing_provider_routing_decision.py
# VERSION: v1.0.0-M11-P4
# AUTHORITY BOUNDARY: provider selection only; no execution
# TENANT POSTURE: exact tenant scope
# FAIL-CLOSED POSTURE: ambiguity, conflict, and corruption reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
