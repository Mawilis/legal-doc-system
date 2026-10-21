'''WILSY OS R95 operational matter access persistence preflight.

Historical events are non-authorizing. Persistence requires
an already-active caller-owned transaction. No network tests.
'''

from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.legal_work_operational_matter_access import (
    LegalWorkMatterAccessEvent,
)
from tools.eos.legal_operations.registry.legal_work_operational_matter_access_registry import (
    LegalWorkMatterAccessRegistry,
    LegalWorkMatterAccessRegistryError,
)

NOW = datetime(2026, 10, 21, 9, 0, tzinfo=timezone.utc)

class FakeSession:
    def __init__(self, active):
        self.in_transaction = active

class ForbiddenCollection:
    def __getattr__(self, name):
        raise AssertionError("UNAUTHORIZED_DATABASE_OPERATION:" + name)

def event():
    return LegalWorkMatterAccessEvent(
        tenant_id="tenant-001",
        case_matter_id="matter-001",
        practitioner_principal_id="practitioner-001",
        event_id="event-001",
        predecessor_event_id=None,
        decision="GRANTED",
        occurred_at=NOW,
        issuer_principal_id="partner-001",
        issuer_authorization_evidence_reference="issuer-evidence-001",
        reason_reference="appointment-001",
    )

@pytest.mark.parametrize("session", [
    None, FakeSession(False), FakeSession(None),
])
def test_append_requires_active_transaction_before_io(session):
    with pytest.raises(LegalWorkMatterAccessRegistryError):
        LegalWorkMatterAccessRegistry.append(
            event(), ForbiddenCollection(), session=session
        )

@pytest.mark.parametrize("session", [
    None, FakeSession(False), FakeSession(None),
])
def test_history_requires_active_transaction_before_io(session):
    with pytest.raises(LegalWorkMatterAccessRegistryError):
        LegalWorkMatterAccessRegistry.list_history(
            tenant_id="tenant-001",
            case_matter_id="matter-001",
            practitioner_principal_id="practitioner-001",
            collection=ForbiddenCollection(),
            session=session,
        )


class MemoryCollection:
    """Minimal fake: deliberately does not synthesize Mongo _id."""

    def __init__(self):
        self.documents = []
        self.indexes = []

    def find(self, query, *, session):
        assert session.in_transaction is True
        return [
            dict(row)
            for row in self.documents
            if all(row.get(key) == value for key, value in query.items())
        ]

    def insert_one(self, document, *, session):
        assert session.in_transaction is True
        self.documents.append(dict(document))

    def create_index(self, fields, **kwargs):
        self.indexes.append((fields, kwargs))


def test_append_and_read_without_database_generated_id():
    collection = MemoryCollection()
    session = FakeSession(True)
    written = LegalWorkMatterAccessRegistry.append(
        event(), collection, session=session
    )
    assert written.event_id == "event-001"
    rows = LegalWorkMatterAccessRegistry.list_history(
        tenant_id="tenant-001",
        case_matter_id="matter-001",
        practitioner_principal_id="practitioner-001",
        collection=collection,
        session=session,
    )
    assert len(rows) == 1
    assert rows[0].fingerprint == written.fingerprint


def test_exact_replay_does_not_duplicate_history():
    collection = MemoryCollection()
    session = FakeSession(True)
    first = LegalWorkMatterAccessRegistry.append(
        event(), collection, session=session
    )
    replay = LegalWorkMatterAccessRegistry.append(
        event(), collection, session=session
    )
    assert first.fingerprint == replay.fingerprint
    assert len(collection.documents) == 1


def test_divergent_replay_rejected():
    collection = MemoryCollection()
    session = FakeSession(True)
    LegalWorkMatterAccessRegistry.append(
        event(), collection, session=session
    )
    from dataclasses import replace
    divergent = replace(event(), reason_reference="different-reason")
    with pytest.raises(LegalWorkMatterAccessRegistryError):
        LegalWorkMatterAccessRegistry.append(
            divergent, collection, session=session
        )
    assert len(collection.documents) == 1


def test_corrupted_history_rejected_without_insert():
    collection = MemoryCollection()
    session = FakeSession(True)
    LegalWorkMatterAccessRegistry.append(
        event(), collection, session=session
    )
    collection.documents[0]["reason_reference"] = "tampered"
    with pytest.raises(LegalWorkMatterAccessRegistryError):
        LegalWorkMatterAccessRegistry.list_history(
            tenant_id="tenant-001",
            case_matter_id="matter-001",
            practitioner_principal_id="practitioner-001",
            collection=collection,
            session=session,
        )
    with pytest.raises(LegalWorkMatterAccessRegistryError):
        LegalWorkMatterAccessRegistry.append(
            event(), collection, session=session
        )
    assert len(collection.documents) == 1


def test_foreign_scope_not_returned():
    collection = MemoryCollection()
    session = FakeSession(True)
    LegalWorkMatterAccessRegistry.append(
        event(), collection, session=session
    )
    other = LegalWorkMatterAccessRegistry.list_history(
        tenant_id="tenant-foreign",
        case_matter_id="matter-001",
        practitioner_principal_id="practitioner-001",
        collection=collection,
        session=session,
    )
    assert other == ()


def test_indexes_include_event_and_successor_uniqueness():
    collection = MemoryCollection()
    LegalWorkMatterAccessRegistry.ensure_indexes(collection)
    named = {opts["name"]: opts for _, opts in collection.indexes}
    assert named["work_access_tenant_event_unique"]["unique"] is True
    assert named["work_access_tenant_predecessor_unique"]["unique"] is True
    assert all("expireAfterSeconds" not in opts for opts in named.values())


def test_root_grant_unique_index_contract():
    """Two simultaneous roots cannot both become durable authority history."""
    collection = MemoryCollection()
    LegalWorkMatterAccessRegistry.ensure_indexes(collection)

    matching = [
        (fields, options)
        for fields, options in collection.indexes
        if options.get("name") == "work_access_tenant_scope_root_unique"
    ]
    assert len(matching) == 1

    fields, options = matching[0]
    assert fields == [
        ("tenant_id", 1),
        ("case_matter_id", 1),
        ("practitioner_principal_id", 1),
    ]
    assert options["unique"] is True
    assert options["partialFilterExpression"] == {
        "predecessor_event_id": {"$type": "null"}
    }
    assert "expireAfterSeconds" not in options
