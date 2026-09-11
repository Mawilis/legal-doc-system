"""TITLE: Accounts Payable Provider Policy.
VERSION: v1.0.0-M11E2C2.
AUTHORITY: Kennel EOS payable-provider eligibility authority.
EPITOME: Immutable tenant-scoped AP provider eligibility revisions.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/domain/accounts_payable_provider_policy.py
COLLABORATION / OWNERSHIP: Kennel EOS AP authority lane.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes immutable AP eligibility facts.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every policy is scoped to exactly one tenant.
AUTHORITY BOUNDARY: Eligibility only; no currentness, routing, or execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes movements.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib, json

VERSION = "v1.0.0-M11E2C2"
AP_POLICY_FAMILY = "ACCOUNTS_PAYABLE"

class AccountsPayableProviderPolicyError(ValueError):
    """Raised when an AP policy is malformed or cryptographically inconsistent."""

@dataclass(frozen=True, slots=True)
class AccountsPayableProviderPolicy:
    policy_id: str
    tenant_id: str
    policy_revision: int
    eligible_provider_names: tuple[str, ...]
    authorization_decision_id: str
    authorization_decision_fingerprint: str
    created_at: datetime
    status: str = "ISSUED"
    policy_fingerprint: str = ""

    def __post_init__(self) -> None:
        for name in ("policy_id", "tenant_id", "authorization_decision_id", "authorization_decision_fingerprint"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise AccountsPayableProviderPolicyError(f"{name} is invalid")
        if self.policy_revision < 1 or isinstance(self.policy_revision, bool):
            raise AccountsPayableProviderPolicyError("policy_revision is invalid")
        if not isinstance(self.eligible_provider_names, tuple) or any(not isinstance(p, str) or not p.strip() for p in self.eligible_provider_names):
            raise AccountsPayableProviderPolicyError("eligible_provider_names is invalid")
        canonical = tuple(sorted(set(self.eligible_provider_names)))
        if canonical != self.eligible_provider_names:
            raise AccountsPayableProviderPolicyError("eligible_provider_names must be unique and canonicalized")
        if not isinstance(self.created_at, datetime) or self.created_at.tzinfo is None:
            raise AccountsPayableProviderPolicyError("created_at is invalid")
        if not isinstance(self.status, str) or self.status != "ISSUED":
            raise AccountsPayableProviderPolicyError("status is invalid")
        expected = self.derive_fingerprint()
        if self.policy_fingerprint and self.policy_fingerprint != expected:
            raise AccountsPayableProviderPolicyError("policy_fingerprint is invalid")
        object.__setattr__(self, "policy_fingerprint", expected)

    def canonical_payload(self) -> dict[str, object]:
        return {"policy_id": self.policy_id, "tenant_id": self.tenant_id, "policy_revision": self.policy_revision,
                "family": AP_POLICY_FAMILY, "eligible_provider_names": self.eligible_provider_names,
                "authorization_decision_id": self.authorization_decision_id,
                "authorization_decision_fingerprint": self.authorization_decision_fingerprint,
                "created_at": self.created_at.astimezone(timezone.utc).isoformat(), "status": self.status}

    def derive_fingerprint(self) -> str:
        return hashlib.sha3_512(json.dumps(self.canonical_payload(), sort_keys=True, separators=(",", ":"), default=list).encode()).hexdigest()

    def to_persisted(self) -> dict[str, object]:
        return {**self.canonical_payload(), "eligible_provider_names": list(self.eligible_provider_names), "policy_fingerprint": self.policy_fingerprint}

# ARTIFACT: accounts_payable_provider_policy.py
# VERSION: v1.0.0-M11E2C2
# AUTHORITY BOUNDARY: AP eligibility only; no selection or execution
# TENANT POSTURE: exact tenant scope
# FAIL-CLOSED POSTURE: malformed and corrupt policy facts reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
