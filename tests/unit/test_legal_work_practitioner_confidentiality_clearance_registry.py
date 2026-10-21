"""G47 — transactional documentary clearance registry certificate."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from tools.eos.legal_operations.domain.legal_work_practitioner_confidentiality_clearance import (
    PractitionerConfidentialityClearanceEvent as Event,
)
from tools.eos.legal_operations.registry import (
    legal_work_practitioner_confidentiality_clearance_registry as reg,
)

NOW = datetime(2026, 10, 21, 9, tzinfo=timezone.utc)


class Session:
    in_transaction = True


class Cursor:
    def __init__(self, documents):
        self.documents = documents

    def limit(self, maximum):
        return self.documents[:maximum]


class MemoryCollection:
    def __init__(self):
        self.documents = []
        self.indexes = []
        self.inserts = 0

    def create_index(self, keys, **kwargs):
        self.indexes.append((tuple(keys), kwargs))

    def find(self, query, *, session):
        assert session.in_transaction
        return Cursor([
            dict(doc) for doc in self.documents
            if all(doc.get(key) == value for key, value in query.items())
        ])

    def find_one(self, query, *, session):
        return next(iter(self.find(query, session=session).documents), None)

    def insert_one(self, document, *, session):
        assert session.in_transaction
        self.documents.append(dict(document))
        self.inserts += 1
        return SimpleNamespace(inserted_id="memory-id")


def event(**updates):
    """Typed canonical fixture; overrides remain domain-validated."""
    from dataclasses import replace

    canonical = Event(
        tenant_id="tenant-a",
        case_matter_id="matter-a",
        practitioner_principal_id="practitioner-a",
        clearance_event_id="root-a",
        predecessor_event_id=None,
        decision="CLEARED",
        effective_at=NOW,
        expires_at=NOW + timedelta(days=30),
        issuer_principal_id="partner-a",
        issuer_authorization_evidence_reference="iam-a",
        conflict_provenance_fingerprint="a" * 128,
        confidentiality_decision_reference="review-a",
    )
    return replace(canonical, **updates)


def history(collection, session=None, **scope):
    values = dict(
        tenant_id="tenant-a", case_matter_id="matter-a",
        practitioner_principal_id="practitioner-a",
    )
    values.update(scope)
    return reg.list_history(
        **values, collection=collection,
        session=session if session is not None else Session(),
    )


@pytest.mark.parametrize("session", [None, SimpleNamespace(in_transaction=False)])
def test_g47_transaction_required_before_read_or_write(session):
    collection = MemoryCollection()
    with pytest.raises(reg.ClearanceTransactionRequired):
        reg.append(event=event(), collection=collection, session=session)
    with pytest.raises(reg.ClearanceTransactionRequired):
        reg.list_history(
            tenant_id="tenant-a", case_matter_id="matter-a",
            practitioner_principal_id="practitioner-a",
            collection=collection, session=session,
        )
    assert collection.documents == []


def test_g47_index_contract_uniqueness_without_ttl():
    c = MemoryCollection()
    reg.ensure_indexes(c)
    assert len(c.indexes) == 5
    assert sum(item[1].get("unique") is True for item in c.indexes) == 4
    assert not any("expireAfterSeconds" in item[1] for item in c.indexes)
    assert {item[1]["name"] for item in c.indexes} == {
        reg.IDENTITY_INDEX, reg.ROOT_INDEX, reg.SUCCESSOR_INDEX,
        reg.FINGERPRINT_INDEX, reg.SCOPE_INDEX,
    }


def test_g47_append_exact_replay_single_durable_row():
    c = MemoryCollection()
    first = event()
    assert reg.append(event=first, collection=c, session=Session()) == first
    assert reg.append(event=event(), collection=c, session=Session()) == first
    assert len(history(c)) == 1
    assert c.inserts == 1


def test_g47_divergent_identity_replay_rejected():
    c = MemoryCollection()
    reg.append(event=event(), collection=c, session=Session())
    with pytest.raises(reg.ClearanceConflict):
        reg.append(
            event=event(confidentiality_decision_reference="review-other"),
            collection=c, session=Session(),
        )
    assert c.inserts == 1


def test_g47_root_fork_rejected_without_write():
    c = MemoryCollection()
    reg.append(event=event(), collection=c, session=Session())
    with pytest.raises(reg.ClearanceConflict):
        reg.append(
            event=event(clearance_event_id="another-root"),
            collection=c, session=Session(),
        )
    assert c.inserts == 1


def test_g47_revocation_successor_and_history():
    c = MemoryCollection()
    root = event()
    reg.append(event=root, collection=c, session=Session())
    revoked = event(
        clearance_event_id="revocation",
        predecessor_event_id=root.clearance_event_id,
        decision="REVOKED",
        effective_at=NOW + timedelta(days=1),
    )
    reg.append(event=revoked, collection=c, session=Session())
    assert len(history(c)) == 2
    assert c.inserts == 2


def test_g47_foreign_tenant_history_invisible():
    c = MemoryCollection()
    reg.append(event=event(), collection=c, session=Session())
    assert history(c, tenant_id="foreign-tenant") == ()


def test_g47_tampered_durable_fingerprint_rejected():
    c = MemoryCollection()
    reg.append(event=event(), collection=c, session=Session())
    c.documents[0]["fingerprint"] = "f" * 128
    with pytest.raises(reg.ClearancePersistedInvalid):
        history(c)


def test_g47_orphan_and_future_reactivation_rejected():
    c = MemoryCollection()
    with pytest.raises(reg.ClearanceConflict):
        reg.append(event=event(
            predecessor_event_id="unknown",
            clearance_event_id="orphan",
            decision="REVOKED",
        ), collection=c, session=Session())
    assert c.inserts == 0


def test_g47_stored_clearance_is_not_authorization():
    c = MemoryCollection()
    reg.append(event=event(), collection=c, session=Session())
    assert not hasattr(reg, "authorize_matter_read")
    assert not hasattr(reg, "grant_operational_access")
    assert len(history(c)) == 1


def test_g50_bson_utc_round_trip_and_naive_rejection():
    """Canonical timestamps survive UTC-aware BSON only."""
    from datetime import timezone
    from bson import BSON, CodecOptions

    original = event()
    wire = BSON.encode(reg._encode(original))

    naive_record = BSON(wire).decode()
    assert naive_record["effective_at"].tzinfo is None
    with pytest.raises(reg.ClearancePersistedInvalid):
        reg._decode(naive_record)

    utc_options = CodecOptions(
        tz_aware=True, tzinfo=timezone.utc
    )
    utc_record = BSON(wire).decode(codec_options=utc_options)
    assert utc_record["effective_at"].tzinfo is not None
    assert utc_record["expires_at"].tzinfo is not None

    restored = reg._decode(utc_record)
    assert restored == original
    assert restored.fingerprint == original.fingerprint



# G52 — documentary persistence is never independent clearance authority.

def test_g52_forged_issuer_field_rejected():
    c = MemoryCollection()
    reg.append(event=event(), collection=c, session=Session())
    c.documents[0]["issuer_principal_id"] = "forged-partner"
    with pytest.raises(reg.ClearancePersistedInvalid):
        history(c)


def test_g52_unknown_persisted_attribute_rejected():
    c = MemoryCollection()
    reg.append(event=event(), collection=c, session=Session())
    c.documents[0]["ethical_wall_cleared"] = True
    with pytest.raises(reg.ClearancePersistedInvalid):
        history(c)


def test_g52_orphan_with_existing_unrelated_history_rejected():
    c = MemoryCollection()
    reg.append(event=event(), collection=c, session=Session())
    orphan = event(
        clearance_event_id="g52-orphan",
        predecessor_event_id="missing",
        decision="REVOKED",
        effective_at=NOW + timedelta(days=1),
    )
    with pytest.raises(reg.ClearanceConflict):
        reg.append(event=orphan, collection=c, session=Session())
    assert c.inserts == 1


def test_g52_successor_fork_rejected():
    c = MemoryCollection()
    root = event()
    reg.append(event=root, collection=c, session=Session())
    first = event(
        clearance_event_id="g52-first",
        predecessor_event_id=root.clearance_event_id,
        decision="DENIED",
        effective_at=NOW + timedelta(days=1),
    )
    reg.append(event=first, collection=c, session=Session())
    fork = event(
        clearance_event_id="g52-fork",
        predecessor_event_id=root.clearance_event_id,
        decision="REVOKED",
        effective_at=NOW + timedelta(days=2),
    )
    with pytest.raises(reg.ClearanceConflict):
        reg.append(event=fork, collection=c, session=Session())
    assert c.inserts == 2


def test_g52_foreign_matter_history_invisible():
    c = MemoryCollection()
    root = event()
    reg.append(event=root, collection=c, session=Session())
    assert history(c, case_matter_id="different-matter") == ()
    assert history(c, practitioner_principal_id="different-practitioner") == ()


def test_g52_read_storage_failure_is_stable():
    class FailingRead(MemoryCollection):
        def find(self, query, *, session):
            raise OSError("unavailable")

    c = FailingRead()
    with pytest.raises(reg.ClearancePersistenceUnavailable):
        history(c)


def test_g52_write_storage_failure_is_stable():
    class FailingWrite(MemoryCollection):
        def insert_one(self, document, *, session):
            raise OSError("unavailable")

    c = FailingWrite()
    with pytest.raises(reg.ClearancePersistenceUnavailable):
        reg.append(event=event(), collection=c, session=Session())
    assert c.inserts == 0
