"""Direct certificate for the M13-P4 entitlement registry.

TITLE: WILSY AI Entitlement Registry Direct Certificate
VERSION: v1.0.0-M13-P4
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove durable-registry semantics with an in-memory collection double.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_entitlement_registry.py
COLLABORATION / OWNERSHIP: Direct certificate for the P4 registry owner.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M13-P4 certifies idempotent replay, tenant isolation,
           uniqueness, strict hydration, and caller transaction ownership.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from datetime import datetime, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.billing.wilsy_ai_commercial_policy import WilsyAITier, get_wilsy_ai_commercial_policy
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import WilsyAIEntitlementConflictError, WilsyAIEntitlementNotFoundError, WilsyAIEntitlementRegistry, ensure_indexes
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlement, WilsyAIEntitlementState

FP = "a" * 128
NOW = datetime(2026, 9, 12, tzinfo=timezone.utc)


class Collection:
    def __init__(self) -> None: self.rows: list[dict[str, Any]] = []; self.indexes: list[tuple[Any, Any]] = []
    def with_options(self, **_: Any) -> "Collection": return self
    def create_index(self, keys: Any, **kwargs: Any) -> str: self.indexes.append((keys, kwargs)); return str(kwargs["name"])
    def find_one(self, query: dict[str, Any], *, session: Any) -> dict[str, Any] | None:
        assert session is not None
        return next((r for r in self.rows if all(r.get(k) == v for k, v in query.items())), None)
    def insert_one(self, document: dict[str, Any], *, session: Any) -> None:
        assert session is not None
        if any(r.get("tenant_id") == document["tenant_id"] and r.get("module_id") == document["module_id"] for r in self.rows): raise DuplicateKeyError("module")
        if any(r.get("tenant_id") == document["tenant_id"] and r.get("idempotency_key") == document["idempotency_key"] for r in self.rows): raise DuplicateKeyError("key")
        self.rows.append(dict(document))
    def update_one(self, query: dict[str, Any], update: dict[str, Any], *, session: Any) -> Any:
        assert session is not None
        for row in self.rows:
            if all(row.get(k) == v for k, v in query.items()):
                row.update(update["$set"])
                return type("Result", (), {"matched_count": 1})()
        return type("Result", (), {"matched_count": 0})()


def value(tenant: str = "tenant-a", module: str = "module-a") -> WilsyAIEntitlement:
    return WilsyAIEntitlement(tenant, f"ent-{tenant}-{module}", module, "Owner Inbox", WilsyAITier.STARTER, get_wilsy_ai_commercial_policy(WilsyAITier.STARTER).policy_fingerprint, WilsyAIEntitlementState.PENDING_SOURCE, ("records",), ("ai.summary",), "ready", FP)


def test_create_exact_replay_and_session_propagation() -> None:
    collection, session = Collection(), object(); registry = WilsyAIEntitlementRegistry(collection); ensure_indexes(collection)
    first = registry.create_or_replay(value(), idempotency_key="k1", session=session); second = registry.create_or_replay(value(), idempotency_key="k1", session=session)
    assert first == second and len(collection.rows) == 1
    assert registry.get(tenant_id="tenant-a", entitlement_id=first.entitlement_id, session=session) == first


def test_divergent_key_and_duplicate_module_fail_closed() -> None:
    collection, session = Collection(), object(); registry = WilsyAIEntitlementRegistry(collection); registry.create_or_replay(value(), idempotency_key="k1", session=session)
    with pytest.raises(WilsyAIEntitlementConflictError): registry.create_or_replay(value(module="module-b"), idempotency_key="k1", session=session)
    with pytest.raises(WilsyAIEntitlementConflictError): registry.create_or_replay(value(module="module-a"), idempotency_key="k2", session=session)


def test_tenant_isolation_and_corruption_rejection() -> None:
    collection, session = Collection(), object(); registry = WilsyAIEntitlementRegistry(collection); registry.create_or_replay(value(), idempotency_key="k1", session=session)
    with pytest.raises(WilsyAIEntitlementNotFoundError): registry.get(tenant_id="tenant-b", entitlement_id="ent-tenant-a-module-a", session=session)
    collection.rows[0]["fingerprint"] = "f" * 128
    with pytest.raises(Exception): registry.get(tenant_id="tenant-a", entitlement_id="ent-tenant-a-module-a", session=session)


def test_registry_has_no_transaction_methods() -> None:
    assert not any(name in dir(WilsyAIEntitlementRegistry) for name in ("start_transaction", "commit_transaction", "abort_transaction"))


def test_revisioned_cas_transitions_and_stale_cross_tenant_rejection() -> None:
    collection, session = Collection(), object(); registry = WilsyAIEntitlementRegistry(collection); registry.create_or_replay(value(), idempotency_key="k1", session=session)
    active = registry.transition(tenant_id="tenant-a", entitlement_id="ent-tenant-a-module-a", target_state=WilsyAIEntitlementState.ACTIVE, expected_revision=0, evidence_reference="act", evidence_fingerprint=FP, occurred_at=NOW, session=session)
    assert active.lifecycle_revision == 1
    suspended = registry.transition(tenant_id="tenant-a", entitlement_id=active.entitlement_id, target_state=WilsyAIEntitlementState.SUSPENDED, expected_revision=1, evidence_reference="susp", evidence_fingerprint=FP, occurred_at=NOW, session=session)
    assert suspended.lifecycle_revision == 2
    with pytest.raises(WilsyAIEntitlementConflictError): registry.transition(tenant_id="tenant-a", entitlement_id=active.entitlement_id, target_state=WilsyAIEntitlementState.REVOKED, expected_revision=1, evidence_reference="rev", evidence_fingerprint=FP, occurred_at=NOW, session=session)
    with pytest.raises(WilsyAIEntitlementNotFoundError): registry.transition(tenant_id="tenant-b", entitlement_id=active.entitlement_id, target_state=WilsyAIEntitlementState.ACTIVE, expected_revision=2, evidence_reference="x", evidence_fingerprint=FP, occurred_at=NOW, session=session)


def test_missing_persisted_field_is_governed_corruption() -> None:
    collection, session = Collection(), object(); registry = WilsyAIEntitlementRegistry(collection); registry.create_or_replay(value(), idempotency_key="k1", session=session)
    del collection.rows[0]["policy_fingerprint"]
    with pytest.raises(Exception, match="M13P4_CORRUPT_ENTITLEMENT"): registry.get(tenant_id="tenant-a", entitlement_id="ent-tenant-a-module-a", session=session)
