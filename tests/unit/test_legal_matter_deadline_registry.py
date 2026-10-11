"""D2 deadline registry unit certificate.

TITLE: Wilsy OS Legal Matter Deadline Registry Unit Certificate
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D2-DEADLINE-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify indexes, transactions, replay, isolation and strict D1 hydration.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system-legal-deadline-engine/tests/unit/test_legal_matter_deadline_registry.py
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D2-DEADLINE-REGISTRY-CERT establishes adversarial D2 unit evidence.
TENANT BOUNDARY: Every fake query is exact tenant scoped.
AUTHORITY BOUNDARY: Persistence behavior only; no deadline calculation or mutation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Transaction, divergence, corruption and IO drift fail.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any
import inspect

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_matter_deadline import LegalMatterDeadline
from tools.eos.legal_operations.registry import legal_matter_deadline_registry as registry

NOW = datetime(2026, 10, 11, 8, 0, tzinfo=timezone.utc)


def deadline(**changes: object) -> LegalMatterDeadline:
    values: dict[str, object] = {"tenant_id": "tenant-a", "case_matter_id": "matter-1", "deadline_id": "deadline-1", "deadline_kind": "FILING", "title": "Evidenced deadline", "due_at": NOW + timedelta(days=7), "source_type": "COURT_ORDER", "source_reference": "evidence:order-1", "source_evidence_fingerprint": "a" * 128, "jurisdiction_reference": "jurisdiction:court-1", "created_at": NOW}
    values.update(changes)
    return LegalMatterDeadline(**values)  # type: ignore[arg-type]


class Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class Cursor:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
    def sort(self, keys: object) -> "Cursor":
        del keys
        return self
    def limit(self, count: int) -> "Cursor":
        return Cursor(self.rows[:count])
    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self.rows)


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, object]] = []
        self.indexes: list[tuple[object, dict[str, object]]] = []
        self.insert_error: BaseException | None = None
    def with_options(self, **kwargs: object) -> "Collection":
        self.calls.append(("with_options", None, kwargs)); return self
    def create_index(self, keys: object, **kwargs: object) -> str:
        self.indexes.append((keys, dict(kwargs))); return str(kwargs["name"])
    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        self.calls.append(("find", session, deepcopy(query)))
        return Cursor([deepcopy(row) for row in self.rows if all(row.get(k) == v for k, v in query.items())])
    def insert_one(self, document: dict[str, object], *, session: object) -> object:
        self.calls.append(("insert_one", session, deepcopy(document)))
        if self.insert_error: raise self.insert_error
        self.rows.append(deepcopy(document)); return object()


def test_collection_and_deterministic_non_ttl_indexes() -> None:
    collection = Collection(); registry.ensure_indexes(collection)
    assert registry.COLLECTION == "legal_matter_deadlines"
    assert [x[1]["name"] for x in collection.indexes] == [registry.TENANT_DEADLINE_UNIQUE_INDEX, registry.MATTER_DEADLINE_INDEX, registry.MATTER_DUE_INDEX, registry.MATTER_STATUS_DUE_INDEX]
    assert collection.indexes[0] == ([("tenant_id", 1), ("deadline_id", 1)], {"unique": True, "name": registry.TENANT_DEADLINE_UNIQUE_INDEX})
    assert all("expireAfterSeconds" not in options for _, options in collection.indexes)


@pytest.mark.parametrize("session", (None, Session(False)))
def test_active_transaction_required_before_database_access(session: object) -> None:
    collection = Collection()
    with pytest.raises(registry.LegalMatterDeadlineRegistryTransactionRequiredError): registry.persist_deadline(deadline(), collection, session=session)
    assert collection.calls == []


def test_exact_payload_session_replay_and_divergence() -> None:
    collection, session, value = Collection(), Session(), deadline()
    assert registry.persist_deadline(value, collection, session=session) == value
    assert collection.rows == [value.to_dict()] and collection.calls[-1][1] is session
    assert registry.persist_deadline(value, collection, session=session) == value
    assert len(collection.rows) == 1
    with pytest.raises(registry.LegalMatterDeadlineRegistryConflictError): registry.persist_deadline(deadline(title="different"), collection, session=session)


def test_cross_tenant_identity_get_and_foreign_absence() -> None:
    collection, session = Collection(), Session()
    left, right = deadline(), deadline(tenant_id="tenant-b")
    for value in (left, right): registry.persist_deadline(value, collection, session=session)
    assert registry.get_deadline("tenant-a", "deadline-1", collection, session=session) == left
    assert registry.get_deadline("tenant-b", "deadline-1", collection, session=session) == right
    with pytest.raises(registry.LegalMatterDeadlineRegistryNotFoundError): registry.get_deadline("tenant-c", "deadline-1", collection, session=session)


def test_matter_listing_is_scoped_ordered_and_does_not_infer_overdue() -> None:
    collection, session = Collection(), Session()
    later = deadline(deadline_id="deadline-z", due_at=NOW + timedelta(days=9))
    earlier = deadline(deadline_id="deadline-a", due_at=NOW + timedelta(days=2), status="SATISFIED")
    for value in (later, deadline(tenant_id="tenant-b", deadline_id="foreign"), earlier): registry.persist_deadline(value, collection, session=session)
    assert registry.list_matter_deadlines("tenant-a", "matter-1", collection, session=session) == (earlier, later)
    assert all("overdue" not in row for row in collection.rows)


@pytest.mark.parametrize("mutation", ("fingerprint", "extra"))
def test_strict_d1_hydration_rejects_corruption(mutation: str) -> None:
    collection, session = Collection(), Session(); registry.persist_deadline(deadline(), collection, session=session)
    if mutation == "fingerprint": collection.rows[0]["fingerprint"] = "b" * 128
    else: collection.rows[0]["payment_authority"] = True
    with pytest.raises(registry.LegalMatterDeadlineRegistryPersistedRecordInvalidError): registry.get_deadline("tenant-a", "deadline-1", collection, session=session)


def test_duplicate_race_and_authority_boundaries() -> None:
    collection = Collection(); collection.insert_error = DuplicateKeyError("race")
    with pytest.raises(registry.LegalMatterDeadlineRegistryRetryRequiredError): registry.persist_deadline(deadline(), collection, session=Session())
    names = set(dir(registry.LegalMatterDeadlineRegistry))
    assert names.isdisjoint({"update", "upsert", "delete", "start_transaction", "commit", "retry"})
    source = inspect.getsource(registry)
    assert "MongoClient(" not in source and "expireAfterSeconds" not in source
    assert "update_one(" not in source and "payment_authority" not in source and "ai_generated" not in source


# ARTIFACT: test_legal_matter_deadline_registry.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D2-DEADLINE-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct immutable registry certificate only
# TENANT POSTURE: exact tenant predicates and cross-tenant identity isolation
# FAIL-CLOSED POSTURE: transaction, divergence, race, corruption and IO drift reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
