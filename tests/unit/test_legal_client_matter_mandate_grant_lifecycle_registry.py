"""Synthetic certificate for the immutable mandate-grant lifecycle registry.

TITLE: WILSY OS Legal Client Matter Mandate Grant Lifecycle Registry Certificate
VERSION: v1.0.0-L9B8-CLIENT-MANDATE-GRANT-LIFECYCLE-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify tenant-scoped append-only lifecycle evidence, exact replay,
         strict hydration, deterministic history, and authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_grant_lifecycle_registry.py
CERTIFICATION / UPDATE DATE: 2026-09-27
TRANSACTION BOUNDARY: Synthetic collection/session fakes only; no Mongo/network.
"""
from __future__ import annotations

import ast
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_lifecycle import (
    LegalClientMatterMandateGrantLifecycle,
)
from tools.eos.legal_operations.registry.legal_client_matter_mandate_grant_lifecycle_registry import (
    COLLECTION,
    EVENT_ID_INDEX_NAME,
    EVENT_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    HISTORY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    LegalClientMatterMandateGrantLifecycleRegistryConflictError,
    LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError,
    LegalClientMatterMandateGrantLifecycleRegistryTransactionRequiredError,
    ensure_indexes,
    get_event,
    get_event_by_fingerprint,
    list_events_for_grant,
    persist_event,
)
from tests.unit.test_legal_client_matter_mandate_grant_lifecycle import (
    event,
    supersession,
)


class Session:
    """Minimal active caller-owned transaction marker."""

    in_transaction = True


class Cursor:
    """Small Mongo-like cursor implementing the registry read contract."""

    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def sort(self, keys: list[tuple[str, int]]) -> "Cursor":
        for key, direction in reversed(keys):
            self.rows.sort(key=lambda row: str(row.get(key)), reverse=direction < 0)
        return self

    def limit(self, count: int) -> "Cursor":
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class Collection:
    """Recording fake for exact session propagation and bounded mutations."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []
        self.calls: list[tuple[str, object]] = []

    def with_options(self, **_: object) -> "Collection":
        return self

    def create_index(self, keys: list[tuple[str, int]], *, unique: bool, name: str) -> str:
        self.indexes.append({"keys": keys, "unique": unique, "name": name})
        return name

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        self.calls.append(("find", session))
        return Cursor(
            [dict(row) for row in self.rows if all(row.get(key) == value for key, value in query.items())]
        )

    def insert_one(self, document: dict[str, object], *, session: object) -> object:
        self.calls.append(("insert_one", session))
        self.rows.append(dict(document))
        return object()


def test_collection_indexes_are_exact_and_have_no_ttl() -> None:
    collection = Collection()
    ensure_indexes(collection)
    assert COLLECTION == "legal_client_matter_mandate_grant_lifecycle"
    assert {index["name"] for index in collection.indexes} == {
        EVENT_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        HISTORY_INDEX_NAME,
        EVENT_INDEX_NAME,
    }
    assert not any("expireAfterSeconds" in index for index in collection.indexes)
    assert sum(bool(index["unique"]) for index in collection.indexes) == 3


def test_active_caller_transaction_is_required() -> None:
    with pytest.raises(LegalClientMatterMandateGrantLifecycleRegistryTransactionRequiredError):
        persist_event(event(), Collection(), session=None)
    with pytest.raises(LegalClientMatterMandateGrantLifecycleRegistryTransactionRequiredError):
        get_event("tenant-l9b4", "lifecycle-l9b6-1", Collection(), session=type("Inactive", (), {"in_transaction": False})())


def test_revoke_and_supersede_insert_with_exact_session() -> None:
    collection = Collection()
    session = Session()
    revoked = persist_event(event(), collection, session=session)
    superseded_collection = Collection()
    superseded = persist_event(supersession(), superseded_collection, session=session)
    assert str(revoked.event) == "REVOKED"
    assert str(superseded.event) == "SUPERSEDED"
    assert len(collection.rows) == 1 and len(superseded_collection.rows) == 1
    assert all(call_session is session for _, call_session in collection.calls + superseded_collection.calls)


def test_exact_replay_by_event_id_and_idempotency_is_single_row() -> None:
    collection = Collection()
    value = event()
    assert persist_event(value, collection, session=Session()).to_dict() == value.to_dict()
    assert persist_event(value, collection, session=Session()).to_dict() == value.to_dict()
    assert len(collection.rows) == 1


def test_exact_fingerprint_read_replays_without_mutation() -> None:
    collection = Collection()
    value = event()
    persist_event(value, collection, session=Session())
    before = len(collection.rows)
    assert get_event_by_fingerprint("tenant-l9b4", value.fingerprint, collection, session=Session()) == value
    assert len(collection.rows) == before


def test_divergent_event_id_and_idempotency_collisions_fail_closed() -> None:
    collection = Collection()
    value = event()
    persist_event(value, collection, session=Session())
    with pytest.raises(LegalClientMatterMandateGrantLifecycleRegistryConflictError):
        persist_event(event(lifecycle_event_id="different-event"), collection, session=Session())
    with pytest.raises(LegalClientMatterMandateGrantLifecycleRegistryConflictError):
        persist_event(event(lifecycle_event_id="different-id", idempotency_key=value.idempotency_key), collection, session=Session())


def test_tenant_isolation_has_no_cross_tenant_existence_oracle() -> None:
    collection = Collection()
    value = event()
    persist_event(value, collection, session=Session())
    with pytest.raises(Exception) as raised:
        get_event("other-tenant", value.lifecycle_event_id, collection, session=Session())
    assert "NOT_FOUND" in str(raised.value)
    assert all("other-tenant" not in repr(row) for row in collection.rows)


def test_get_and_history_are_strict_and_deterministically_ordered() -> None:
    collection = Collection()
    later = event(lifecycle_event_id="later", idempotency_key="later-key")
    earlier = event(lifecycle_event_id="earlier", idempotency_key="earlier-key", effective_from=later.effective_from.replace(minute=0))
    persist_event(later, collection, session=Session())
    persist_event(earlier, collection, session=Session())
    assert get_event("tenant-l9b4", later.lifecycle_event_id, collection, session=Session()) == later
    values = list_events_for_grant("tenant-l9b4", later.client_grant_id, collection, session=Session())
    assert [value.lifecycle_event_id for value in values] == ["earlier", "later"]


def test_strict_hydration_rejects_corrupt_rows_and_unknown_fields() -> None:
    collection = Collection()
    value = event()
    raw = value.to_dict()
    raw["unexpected"] = "tamper"
    collection.rows.append(raw)
    with pytest.raises(LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError):
        get_event("tenant-l9b4", value.lifecycle_event_id, collection, session=Session())
    collection.rows.clear()
    raw = value.to_dict()
    raw["event"] = "UNKNOWN"
    collection.rows.append(raw)
    with pytest.raises(LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError):
        get_event("tenant-l9b4", value.lifecycle_event_id, collection, session=Session())


def test_duplicate_identity_is_not_selected() -> None:
    collection = Collection()
    value = event()
    collection.rows.extend([value.to_dict(), value.to_dict()])
    with pytest.raises(LegalClientMatterMandateGrantLifecycleRegistryPersistedRecordInvalidError):
        get_event("tenant-l9b4", value.lifecycle_event_id, collection, session=Session())


def test_equal_effective_events_are_preserved_for_later_composition() -> None:
    collection = Collection()
    first = event(lifecycle_event_id="first", idempotency_key="first-key")
    second = event(lifecycle_event_id="second", idempotency_key="second-key")
    persist_event(first, collection, session=Session())
    persist_event(second, collection, session=Session())
    assert len(list_events_for_grant("tenant-l9b4", first.client_grant_id, collection, session=Session())) == 2


def test_registry_does_not_infer_currentness_or_mutate_other_authorities() -> None:
    source = open(
        "tools/eos/legal_operations/registry/legal_client_matter_mandate_grant_lifecycle_registry.py",
        encoding="utf-8",
    ).read()
    tree = ast.parse(source)
    imports = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert any(module.endswith("legal_client_matter_mandate_grant_lifecycle") for module in imports)
    assert "get_current" not in source and "currentness" in source
    assert "update_one" not in source and "delete_many" not in source
    assert "email" not in repr(Collection().__dict__).casefold()


def test_no_raw_pii_and_strict_domain_return_types() -> None:
    collection = Collection()
    value = event()
    persist_event(value, collection, session=Session())
    result = get_event("tenant-l9b4", value.lifecycle_event_id, collection, session=Session())
    assert isinstance(result, LegalClientMatterMandateGrantLifecycle)
    assert set(collection.rows[0]) == set(value.to_dict())
    assert not any(key in collection.rows[0] for key in ("email", "display_name", "password", "token", "jwt"))


# ARTIFACT: test_legal_client_matter_mandate_grant_lifecycle_registry.py
# VERSION: v1.0.0-L9B8-CLIENT-MANDATE-GRANT-LIFECYCLE-REGISTRY-CERT
# RESULT: synthetic unit certificate only; no real-Mongo lifecycle certificate
# END OF WILSY OS SOVEREIGN ARTIFACT
