"""TITLE: WILSY OS CRM Owner Work Registry Regression Certificate
VERSION: v1.0.0-COMPLETED-CRM-RECORD-READBACK-CERT
AUTHORITY: WILSY OS source-owned CRM persistence certification.
EPITOME: Verify exact-tenant create/replay, completion compare-and-set,
         persisted readback and absence of foreign-tenant disclosure.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_owner_commercial_work_registry.py
COLLABORATION / OWNERSHIP: CRM work item domain and registry; Python EOS
         owner workspace service and authenticated API.
CERTIFICATION / UPDATE DATE: 2026-11-17
CHANGELOG: v1.0.0-COMPLETED-CRM-RECORD-READBACK-CERT preserves existing source registry tests
           and certifies completed evidence remains retrievable from its
           owning exact-tenant record while foreign tenant reads deny.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic data only; no live records.
TENANT BOUNDARY: All fixtures verify tenant-first persistence coordinates.
AUTHORITY BOUNDARY: No test grants IAM or authorizes a production command.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS exclusively.
FAIL-CLOSED POSTURE: Missing, foreign, divergent or stale source rows reject.
"""

from datetime import datetime, timezone
from dataclasses import replace

import pytest

from tools.eos.crm.domain.owner_commercial_work_item import (
    OwnerCommercialWorkItem, OwnerWorkStatus,
)
from tools.eos.crm.persistence.owner_commercial_work_registry import (
    OwnerCommercialWorkRegistry, OwnerWorkRegistryConflict,
    OwnerWorkRegistryNotFound, OwnerWorkRegistryError, ensure_indexes,
)

NOW = datetime(2026, 11, 3, 8, tzinfo=timezone.utc)
TENANT = "WILSYTENANT-4CD2FZ4O"


class Cursor(list):
    def sort(self, *_args, **_kwargs):
        return self

    def limit(self, _value):
        return self


class Collection:
    def __init__(self):
        self.rows = []
        self.indexes = []

    def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))

    def find_one(self, query, session=None):
        assert session is not None
        return next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)

    def insert_one(self, document, session=None):
        assert session is not None
        self.rows.append(dict(document))

    def find(self, query, session=None):
        assert session is not None
        return Cursor(row for row in self.rows if all(row.get(k) == v for k, v in query.items()))

    def update_one(self, query, update, session=None):
        assert session is not None
        row = next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)
        if row is None:
            return type("Result", (), {"matched_count": 0})()
        row.update(update["$set"])
        return type("Result", (), {"matched_count": 1})()


def make_item(tenant=TENANT):
    return OwnerCommercialWorkItem.create(
        tenant_id=tenant, title="Prepare client follow-up",
        owner_principal_id="principal-1", now=NOW,
    )


def test_registry_requires_collection_and_caller_session():
    with pytest.raises(OwnerWorkRegistryError):
        OwnerCommercialWorkRegistry(None)
    registry = OwnerCommercialWorkRegistry(Collection())
    with pytest.raises(OwnerWorkRegistryError, match="SESSION_REQUIRED"):
        registry.create_or_replay(make_item(), idempotency_key="cmd-1", session=None)


def test_create_replay_is_exact_and_divergent_reuse_denies():
    registry = OwnerCommercialWorkRegistry(Collection())
    item = make_item()
    assert registry.create_or_replay(item, idempotency_key="cmd-1", session=object()) == item
    assert registry.create_or_replay(item, idempotency_key="cmd-1", session=object()) == item
    changed = make_item()
    changed = replace(changed, title="Different command")
    with pytest.raises(OwnerWorkRegistryConflict):
        registry.create_or_replay(changed, idempotency_key="cmd-1", session=object())


def test_get_and_list_are_exact_tenant_scoped():
    registry = OwnerCommercialWorkRegistry(Collection())
    item = make_item()
    registry.create_or_replay(item, idempotency_key="cmd-1", session=object())
    assert registry.get(tenant_id=TENANT, work_item_id=item.work_item_id, session=object()) == item
    with pytest.raises(OwnerWorkRegistryNotFound):
        registry.get(tenant_id="OTHER-TENANT", work_item_id=item.work_item_id, session=object())
    assert registry.list_for_tenant(tenant_id="OTHER-TENANT", session=object()) == ()


def test_daily_queue_projection_is_tenant_scoped():
    registry = OwnerCommercialWorkRegistry(Collection())
    item = make_item()
    registry.create_or_replay(item, idempotency_key="cmd-1", session=object())
    queue = registry.daily_queue(tenant_id=TENANT, now=NOW, session=object())
    assert len(queue) == 1
    assert queue[0]["work_item_id"] == item.work_item_id


def test_index_set_is_tenant_first_and_has_no_ttl():
    collection = Collection()
    ensure_indexes(collection)
    assert len(collection.indexes) == 3
    assert all(keys[0][0] == "tenant_id" for keys, _ in collection.indexes)
    assert all(kwargs.get("expireAfterSeconds") is None for _, kwargs in collection.indexes)


def test_terminal_work_item_not_in_daily_queue():
    registry = OwnerCommercialWorkRegistry(Collection())
    item = make_item()
    completed = replace(
        item, status=OwnerWorkStatus.COMPLETED,
        completed_at=NOW, updated_at=NOW,
    )
    # Completed records are excluded from actionable queue even when hydrated
    # from a source snapshot; registry creation remains an immutable insert.
    from tools.eos.crm.domain.owner_commercial_work_item import build_daily_queue
    assert build_daily_queue([completed], tenant_id=TENANT, now=NOW) == ()


def test_completion_is_tenant_scoped_compare_and_set_and_exact_replay():
    registry = OwnerCommercialWorkRegistry(Collection())
    item = make_item()
    registry.create_or_replay(item, idempotency_key="cmd-1", session=object())
    completed = registry.complete(
        tenant_id=TENANT, work_item_id=item.work_item_id,
        completion_note="Confirmed completed", now=NOW, session=object(),
    )
    assert completed.status is OwnerWorkStatus.COMPLETED
    assert registry.complete(
        tenant_id=TENANT, work_item_id=item.work_item_id,
        completion_note="Confirmed completed", now=NOW, session=object(),
    ) == completed
    with pytest.raises(OwnerWorkRegistryConflict):
        registry.complete(
            tenant_id=TENANT, work_item_id=item.work_item_id,
            completion_note="Different evidence", now=NOW, session=object(),
        )
    with pytest.raises(OwnerWorkRegistryNotFound):
        registry.complete(
            tenant_id="OTHER-TENANT", work_item_id=item.work_item_id,
            completion_note="Confirmed completed", now=NOW, session=object(),
        )


def test_completed_record_retains_source_evidence_under_exact_tenant() -> None:
    """Completed work remains readable without becoming active or cross-tenant."""
    registry = OwnerCommercialWorkRegistry(Collection())
    item = make_item()
    registry.create_or_replay(item, idempotency_key="cmd-detail", session=object())
    completed = registry.complete(
        tenant_id=TENANT, work_item_id=item.work_item_id,
        completion_note="Reviewed and verified evidence",
        now=NOW, session=object(),
    )
    persisted = registry.get(
        tenant_id=TENANT, work_item_id=item.work_item_id, session=object(),
    )
    assert persisted == completed
    assert persisted.status is OwnerWorkStatus.COMPLETED
    assert persisted.completion_note == "Reviewed and verified evidence"
    assert persisted.completed_at == NOW
    assert registry.daily_queue(
        tenant_id=TENANT, now=NOW, session=object(),
    ) == ()
    with pytest.raises(OwnerWorkRegistryNotFound):
        registry.get(
            tenant_id="OTHER-TENANT",
            work_item_id=item.work_item_id, session=object(),
        )


# ARTIFACT: tests/unit/test_owner_commercial_work_registry.py
# VERSION: v1.0.0-COMPLETED-CRM-RECORD-READBACK-CERT
# AUTHORITY BOUNDARY: Synthetic registry evidence only; no IAM grants.
# TENANT POSTURE: Exact tenant, no cross-tenant existence disclosure.
# FAIL-CLOSED POSTURE: Foreign records are indistinguishable from absent.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
