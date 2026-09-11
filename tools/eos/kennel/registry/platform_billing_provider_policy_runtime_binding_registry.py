"""TITLE: Platform Billing Provider-Policy Runtime Binding Registry.
VERSION: v1.0.0-M11E2D5C2G-P2B-R3.
AUTHORITY: Kennel EOS durable runtime-binding history.
EPITOME: Tenant/lane scoped immutable binding replay and head authority.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/registry/platform_billing_provider_policy_runtime_binding_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS runtime-policy binding orchestration.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes strict revision-chain persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every operation requires exact tenant and outbound lane.
AUTHORITY BOUNDARY: Persistence and chain integrity only; no authorization or provider selection.
"""
from typing import Any
from ..domain.platform_billing_provider_policy_runtime_binding import PlatformBillingProviderPolicyRuntimeBinding

class PlatformBillingProviderPolicyRuntimeBindingRegistryError(RuntimeError): pass

class PlatformBillingProviderPolicyRuntimeBindingRegistry:
    """Persist immutable binding revisions; caller owns session and transaction."""
    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        collection.create_index([( "tenant_id", 1),("lane",1),("binding_revision",1)], unique=True, name="platform_runtime_binding_revision_unique")
        collection.create_index([( "tenant_id", 1),("lane",1),("binding_id",1)], unique=True, name="platform_runtime_binding_identity_unique")
        collection.create_index([( "tenant_id", 1),("lane",1)], unique=True, name="platform_runtime_binding_current_head_unique", partialFilterExpression={"_kind":"head"})

    @staticmethod
    def _require_transaction(session: Any) -> Any:
        if session is None or getattr(session, "in_transaction", False) is not True:
            raise PlatformBillingProviderPolicyRuntimeBindingRegistryError("ACTIVE_TRANSACTION_REQUIRED")
        return session

    @staticmethod
    def create(binding: PlatformBillingProviderPolicyRuntimeBinding, collection: Any, *, session: Any=None) -> PlatformBillingProviderPolicyRuntimeBinding:
        try:
            tx = PlatformBillingProviderPolicyRuntimeBindingRegistry._require_transaction(session)
            q={"tenant_id":binding.tenant_id,"lane":binding.lane,"binding_revision":binding.binding_revision}
            existing=collection.find_one(q, session=tx)
            if existing is not None:
                current=PlatformBillingProviderPolicyRuntimeBindingRegistry._hydrate(existing)
                if current.binding_fingerprint == binding.binding_fingerprint: return current
                raise PlatformBillingProviderPolicyRuntimeBindingRegistryError("BINDING_REVISION_CONFLICT")
            headq={"tenant_id":binding.tenant_id,"lane":binding.lane,"_kind":"head"}
            head=collection.find_one(headq, session=tx)
            if binding.binding_revision == 1:
                if head is not None: raise PlatformBillingProviderPolicyRuntimeBindingRegistryError("HEAD_ALREADY_EXISTS")
            elif head is None or head.get("binding_revision") != binding.binding_revision-1 or head.get("binding_id") != binding.previous_binding_id or head.get("binding_fingerprint") != binding.previous_binding_fingerprint:
                raise PlatformBillingProviderPolicyRuntimeBindingRegistryError("PREDECESSOR_INVALID")
            history_doc = binding.to_persisted() if hasattr(binding,"to_persisted") else binding.payload() | {"binding_fingerprint":binding.binding_fingerprint}
            history_doc = {**history_doc, "_kind": "binding"}
            collection.insert_one(history_doc, session=tx)
            head_doc={"_kind":"head","tenant_id":binding.tenant_id,"lane":binding.lane,"binding_revision":binding.binding_revision,"binding_id":binding.binding_id,"binding_fingerprint":binding.binding_fingerprint}
            if hasattr(collection,"update_one"):
                predicate=dict(headq)
                if head is not None: predicate.update({"binding_revision":head["binding_revision"],"binding_id":head["binding_id"],"binding_fingerprint":head["binding_fingerprint"]})
                result=collection.update_one(predicate,{"$set":head_doc},upsert=head is None,session=tx)
                if getattr(result,"matched_count",0)==0 and getattr(result,"upserted_id",None) is None: raise PlatformBillingProviderPolicyRuntimeBindingRegistryError("STALE_HEAD")
            else:
                collection.insert_one(head_doc, session=tx)
            return binding
        except PlatformBillingProviderPolicyRuntimeBindingRegistryError: raise
        except Exception as error: raise PlatformBillingProviderPolicyRuntimeBindingRegistryError("BINDING_PERSISTENCE_FAILED") from error

    @staticmethod
    def _hydrate(row: Any) -> PlatformBillingProviderPolicyRuntimeBinding:
        body=dict(row); body.pop("_id",None)
        if body.pop("_kind", "binding") != "binding":
            raise PlatformBillingProviderPolicyRuntimeBindingRegistryError("BINDING_HISTORY_KIND_INVALID")
        from datetime import datetime
        for key in ("activated_at","created_at"):
            if isinstance(body.get(key),str): body[key]=datetime.fromisoformat(body[key])
        return PlatformBillingProviderPolicyRuntimeBinding(**body)

    @staticmethod
    def get(tenant_id: str, lane: str, collection: Any, *, revision: int|None=None, session: Any=None) -> PlatformBillingProviderPolicyRuntimeBinding|None:
        q={"tenant_id":tenant_id,"lane":lane}
        q["_kind"] = "binding"
        if revision is not None: q["binding_revision"]=str(revision) if False else revision  # type: ignore[reportArgumentType]
        try:
            row=collection.find_one(q, **({"session":session} if session is not None else {}))
            return None if row is None else PlatformBillingProviderPolicyRuntimeBindingRegistry._hydrate(row)
        except PlatformBillingProviderPolicyRuntimeBindingRegistryError: raise
        except Exception as error: raise PlatformBillingProviderPolicyRuntimeBindingRegistryError("BINDING_PERSISTED_RECORD_INVALID") from error

    @staticmethod
    def current(tenant_id: str, lane: str, collection: Any, *, session: Any=None) -> PlatformBillingProviderPolicyRuntimeBinding|None:
        try:
            head=collection.find_one({"tenant_id":tenant_id,"lane":lane,"_kind":"head"}, **({"session":session} if session is not None else {}))
            if head is None: return None
            row=collection.find_one({"tenant_id":tenant_id,"lane":lane,"_kind":"binding","binding_revision":head["binding_revision"],"binding_id":head["binding_id"],"binding_fingerprint":head["binding_fingerprint"]}, **({"session":session} if session is not None else {}))
            if row is None: raise PlatformBillingProviderPolicyRuntimeBindingRegistryError("HEAD_HISTORY_MISMATCH")
            if row.get("tenant_id") != head.get("tenant_id") or row.get("lane") != head.get("lane") or row.get("binding_revision") != head.get("binding_revision") or row.get("binding_id") != head.get("binding_id") or row.get("binding_fingerprint") != head.get("binding_fingerprint"): raise PlatformBillingProviderPolicyRuntimeBindingRegistryError("HEAD_HISTORY_MISMATCH")
            return PlatformBillingProviderPolicyRuntimeBindingRegistry._hydrate(row)
        except Exception as error: raise PlatformBillingProviderPolicyRuntimeBindingRegistryError("BINDING_HEAD_LOOKUP_FAILED") from error

# ARTIFACT: platform_billing_provider_policy_runtime_binding_registry.py
# VERSION: v1.0.0-M11E2D5C2G-P2B-R3
# AUTHORITY BOUNDARY: durable binding history only
# TENANT POSTURE: exact tenant/lane scope
# FAIL-CLOSED POSTURE: conflicts, forks, gaps, and corruption reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
