"""Tests for append-only G64 review and second-approval evidence."""
import pytest

from tools.eos.legal_operations.registry.g64_ratification_review_registry import (
    G64ReviewRegistryError,
    append_review_event,
    ensure_indexes,
    list_review_events,
)


class Cursor:
    def __init__(self, rows):
        self.rows = list(rows)

    def sort(self, *_args):
        return self

    def limit(self, count):
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class Session:
    in_transaction = True


class Collection:
    def __init__(self):
        self.rows = {}
        self.indexes = []

    def with_options(self, **_kwargs):
        return self

    def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))
        return kwargs.get("name")

    def find_one(self, query, session=None):
        assert session is not None
        return self.rows.get(tuple(query.values()))

    def insert_one(self, document, session=None):
        assert session is not None
        key = (document["tenant_id"], document["institution_id"], document["record_id"], document["event_id"])
        if key in self.rows:
            raise RuntimeError("duplicate")
        self.rows[key] = document

    def find(self, query, session=None):
        assert session is not None
        return Cursor([
            row for row in self.rows.values()
            if row["tenant_id"] == query["tenant_id"]
            and row["institution_id"] == query["institution_id"]
            and row["record_id"] == query["record_id"]
        ])


def event():
    return {
        "event_id": "verification-001",
        "tenant_id": "t",
        "institution_id": "i",
        "record_id": "r",
        "event_type": "INDEPENDENT_VERIFICATION",
        "reviewer_principal_id": "independent-principal",
        "outcome": "PASS",
        "created_at": "2026-10-27T00:00:00+00:00",
        "authority_effect": "NONE",
        "ratification_complete": False,
        "permits_operational_access": False,
    }


def test_review_registry_requires_active_transaction():
    with pytest.raises(G64ReviewRegistryError, match="G64_REVIEW_ACTIVE_TRANSACTION_REQUIRED"):
        append_review_event(
            tenant_id="t", institution_id="i", record_id="r", event_id="e",
            payload=event(), collection=Collection(), session=None,
        )


def test_review_event_is_immutable_and_exact_replay_only():
    collection = Collection()
    kwargs = dict(
        tenant_id="t", institution_id="i", record_id="r",
        event_id="verification-001", payload=event(),
        collection=collection, session=Session(),
    )
    first = append_review_event(**kwargs)
    replay = append_review_event(**kwargs)
    assert first["payload_sha3_512"] == replay["payload_sha3_512"]
    changed = {**event(), "outcome": "FAIL"}
    with pytest.raises(G64ReviewRegistryError, match="G64_REVIEW_IMMUTABLE_EVENT_CONFLICT"):
        append_review_event(**{**kwargs, "payload": changed})


def test_review_history_recomputes_digest_and_is_scoped():
    collection = Collection()
    append_review_event(
        tenant_id="t", institution_id="i", record_id="r", event_id="verification-001",
        payload=event(), collection=collection, session=Session(),
    )
    assert len(list_review_events(
        tenant_id="t", institution_id="i", record_id="r",
        collection=collection, session=Session(),
    )) == 1
    assert list_review_events(
        tenant_id="other", institution_id="i", record_id="r",
        collection=collection, session=Session(),
    ) == ()


def test_review_indexes_are_unique_and_scoped():
    collection = Collection()
    ensure_indexes(collection)
    assert len(collection.indexes) == 4
    assert collection.indexes[0][1]["unique"] is True
    assert collection.indexes[2][1]["partialFilterExpression"]["payload.event_type"] == "SECOND_APPROVAL_POLICY"
    assert collection.indexes[3][1]["partialFilterExpression"]["payload.event_type"] == "SECOND_APPROVAL"


def test_exact_review_retry_ignores_only_server_generated_timestamp():
    collection = Collection()
    first = event()
    append_review_event(
        tenant_id="t", institution_id="i", record_id="r", event_id=first["event_id"],
        payload=first, collection=collection, session=Session(),
    )
    retry = {**first, "created_at": "2026-10-27T00:00:01+00:00"}
    result = append_review_event(
        tenant_id="t", institution_id="i", record_id="r", event_id=retry["event_id"],
        payload=retry, collection=collection, session=Session(),
    )
    assert result["payload"]["created_at"] == first["created_at"]
