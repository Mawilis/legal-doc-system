"""TITLE: Platform Billing Provider Policy Registry. VERSION: v1.0.0-M11E2D5C2F.
AUTHORITY: Durable tenant-scoped policy evidence; caller owns transactions.
EPITOME: Persists immutable provider-policy revisions with replay protection.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/registry/platform_billing_provider_policy_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS policy registry.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes strict persistence and hydration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every lookup and write requires exact tenant scope.
AUTHORITY BOUNDARY: Persistence only; no provider selection.
"""
from typing import Any
from datetime import datetime
from ..domain.platform_billing_provider_policy import PlatformBillingProviderPolicy, PlatformBillingProviderPolicyError, PolicyStatus
class PlatformBillingProviderPolicyRegistryError(RuntimeError): pass
class PlatformBillingProviderPolicyRegistry:
    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Install tenant/policy/revision uniqueness outside transactions."""
        collection.create_index([("tenant_id", 1), ("policy_id", 1), ("policy_revision", 1)], unique=True, name="platform_billing_provider_policy_revision_unique")
    @staticmethod
    def create(policy: PlatformBillingProviderPolicy, collection: Any, *, session: Any=None):
        try:
            query={"tenant_id":policy.tenant_id,"policy_id":policy.policy_id,"policy_revision":policy.policy_revision}
            existing=collection.find_one(query, **({"session":session} if session is not None else {}))
            if existing is not None:
                if dict(existing).get("policy_fingerprint") == policy.policy_fingerprint: return PlatformBillingProviderPolicyRegistry.get(policy.tenant_id,policy.policy_id,collection,revision=policy.policy_revision,session=session)
                raise PlatformBillingProviderPolicyRegistryError("POLICY_REVISION_CONFLICT")
            collection.insert_one(policy.to_persisted(), **({"session":session} if session is not None else {})); return policy
        except Exception as e: raise PlatformBillingProviderPolicyRegistryError("POLICY_PERSISTENCE_FAILED") from e
    @staticmethod
    def get(tenant_id: str, policy_id: str, collection: Any, *, revision: int|None=None, session: Any=None):
        q: dict[str, Any]={"tenant_id":tenant_id,"policy_id":policy_id};
        if revision is not None:q["policy_revision"]=revision
        try: row=collection.find_one(q, **({"session":session} if session is not None else {}))
        except Exception as e: raise PlatformBillingProviderPolicyRegistryError("POLICY_LOOKUP_FAILED") from e
        if row is None:return None
        try:
            row=dict(row); row.pop("_id",None); row["authorized_provider_names"]=tuple(row["authorized_provider_names"]); row["status"] = PolicyStatus(row["status"] if isinstance(row["status"],str) else row["status"].value)
            row["effective_at"]=datetime.fromisoformat(row["effective_at"]); row["created_at"]=datetime.fromisoformat(row["created_at"])
            if row.get("expires_at"): row["expires_at"]=datetime.fromisoformat(row["expires_at"])
            return PlatformBillingProviderPolicy(**row)
        except (KeyError,TypeError,ValueError,PlatformBillingProviderPolicyError) as e: raise PlatformBillingProviderPolicyRegistryError("POLICY_PERSISTED_RECORD_INVALID") from e
# ARTIFACT: platform_billing_provider_policy_registry.py
# VERSION: v1.0.0-M11E2D5C2F
# AUTHORITY BOUNDARY: durable policy evidence only
# TENANT POSTURE: exact tenant-scoped lookup
# FAIL-CLOSED POSTURE: corrupt records reject
# END OF WILSY OS SOVEREIGN ARTIFACT
