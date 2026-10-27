"""Direct certificate for the append-only G64 workspace registry.

VERSION: v1.0.0-G64-IMMUTABLE-WORKSPACE-REGISTRY-TEST
AUTHORITY: Persistence-boundary tests only; no route or access activation.
"""
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.g64_ratification_workspace_evidence import (
    G64RatificationWorkspaceRecord,
    G64RecordState,
    new_pending_decisions,
)
from tools.eos.legal_operations.registry.g64_ratification_workspace_registry import (
    G64RegistryConflictError,
    G64RegistryCorruptRecordError,
    G64RegistryTransactionRequiredError,
    append_record,
    ensure_indexes,
    list_history,
    read_record,
)

NOW = datetime(2026, 10, 27, tzinfo=timezone.utc)
FINGERPRINT = "b" * 128


class Session:
    in_transaction = True


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


class Collection:
    def __init__(self):
        self.rows = {}
        self.options = {}
        self.created_indexes = []

    def create_index(self, keys, **kwargs):
        self.created_indexes.append((keys, kwargs))
        return kwargs.get("name")

    def with_options(self, **kwargs):
        self.options = kwargs
        return self

    def find_one(self, query, session=None):
        assert session is not None
        return self.rows.get((query["tenant_id"], query["institution_id"], query["record_id"]))

    def insert_one(self, document, session=None):
        assert session is not None
        key = (document["tenant_id"], document["institution_id"], document["record_id"])
        if key in self.rows:
            raise RuntimeError("duplicate")
        self.rows[key] = document

    def find(self, query, session=None):
        assert session is not None
        return Cursor([
            value for (tenant, institution, _), value in self.rows.items()
            if tenant == query["tenant_id"] and institution == query["institution_id"]
        ])


def record():
    return G64RatificationWorkspaceRecord(
        record_id="g64-record-001",
        institution_id="wilsy-pty-ltd",
        ratifier_principal_id="principal-pending-verification",
        contract_version="v1.0.0-P47-R95-G62-DRAFT",
        contract_sha3_512_fingerprint=FINGERPRINT,
        created_at=NOW,
        state=G64RecordState.DRAFT,
        decisions=new_pending_decisions(),
    )


def test_append_record_requires_caller_owned_active_transaction():
    with pytest.raises(G64RegistryTransactionRequiredError):
        append_record(tenant_id="tenant-001", record=record(), collection=Collection(), session=None)


def test_append_and_exact_replay_preserve_one_immutable_record():
    collection = Collection()
    first = record()
    append_record(tenant_id="tenant-001", record=first, collection=collection, session=Session())
    append_record(tenant_id="tenant-001", record=first, collection=collection, session=Session())
    assert len(collection.rows) == 1
    assert read_record(
        tenant_id="tenant-001",
        institution_id="wilsy-pty-ltd",
        record_id="g64-record-001",
        collection=collection,
        session=Session(),
    )["payload"]["permits_operational_access"] is False


def test_divergent_replay_of_same_identity_is_rejected():
    collection = Collection()
    first = record()
    append_record(tenant_id="tenant-001", record=first, collection=collection, session=Session())
    changed = G64RatificationWorkspaceRecord(
        record_id=first.record_id,
        institution_id=first.institution_id,
        ratifier_principal_id=first.ratifier_principal_id,
        contract_version=first.contract_version,
        contract_sha3_512_fingerprint=first.contract_sha3_512_fingerprint,
        created_at=first.created_at,
        state=first.state,
        decisions=first.decisions,
        supporting_evidence=(),
    )
    changed_doc = changed.to_document()
    changed_doc["supporting_evidence"] = [{"locator": "different"}]
    collection.rows[("tenant-001", "wilsy-pty-ltd", "g64-record-001")] = {
        "schema": "WILSY-G64-RATIFICATION-WORKSPACE-REGISTRY/V1",
        "version": "v1.0.0-G64-IMMUTABLE-WORKSPACE-REGISTRY",
        "tenant_id": "tenant-001",
        "institution_id": "wilsy-pty-ltd",
        "record_id": "g64-record-001",
        "evidence_sha3_512": changed.evidence_fingerprint(),
        "payload": changed_doc,
    }
    with pytest.raises(G64RegistryConflictError):
        append_record(tenant_id="tenant-001", record=first, collection=collection, session=Session())


def test_history_is_institution_scoped_and_bounded():
    collection = Collection()
    append_record(tenant_id="tenant-001", record=record(), collection=collection, session=Session())
    assert len(list_history(
        tenant_id="tenant-001",
        institution_id="wilsy-pty-ltd",
        collection=collection,
        session=Session(),
        limit=10,
    )) == 1
    assert list_history(
        tenant_id="tenant-001",
        institution_id="another-institution",
        collection=collection,
        session=Session(),
        limit=10,
    ) == ()


def test_read_recomputes_fingerprint_instead_of_trusting_matching_claims():
    collection = Collection()
    append_record(tenant_id="tenant-001", record=record(), collection=collection, session=Session())
    stored = collection.rows[("tenant-001", "wilsy-pty-ltd", "g64-record-001")]
    stored["payload"]["ratifier_principal_id"] = "tampered-principal"
    # The envelope and payload still repeat the original digest; integrity must
    # be recomputed from semantic fields, not inferred from those repeated claims.
    with pytest.raises(G64RegistryCorruptRecordError):
        read_record(
            tenant_id="tenant-001",
            institution_id="wilsy-pty-ltd",
            record_id="g64-record-001",
            collection=collection,
            session=Session(),
        )


def test_history_recomputes_fingerprint_for_every_row():
    collection = Collection()
    append_record(tenant_id="tenant-001", record=record(), collection=collection, session=Session())
    collection.rows[("tenant-001", "wilsy-pty-ltd", "g64-record-001")]["payload"]["state"] = "RATIFIED"
    from tools.eos.legal_operations.registry.g64_ratification_workspace_registry import (
        G64RegistryCorruptRecordError,
    )
    with pytest.raises(G64RegistryCorruptRecordError):
        list_history(
            tenant_id="tenant-001",
            institution_id="wilsy-pty-ltd",
            collection=collection,
            session=Session(),
            limit=10,
        )


def test_same_institution_and_record_id_are_isolated_by_tenant():
    collection = Collection()
    item = record()
    append_record(tenant_id="tenant-001", record=item, collection=collection, session=Session())
    append_record(tenant_id="tenant-002", record=item, collection=collection, session=Session())
    assert len(collection.rows) == 2
    assert len(list_history(
        tenant_id="tenant-001", institution_id="wilsy-pty-ltd",
        collection=collection, session=Session(), limit=10,
    )) == 1
    assert len(list_history(
        tenant_id="tenant-002", institution_id="wilsy-pty-ltd",
        collection=collection, session=Session(), limit=10,
    )) == 1


def test_unique_registry_index_includes_tenant_and_institution_scope():
    collection = Collection()
    ensure_indexes(collection)
    assert collection.created_indexes == [(
        [("tenant_id", 1), ("institution_id", 1), ("record_id", 1)],
        {"unique": True, "name": "g64_workspace_tenant_institution_record_unique"},
    )]


def test_read_cannot_cross_tenant_even_for_same_institution_and_record_id():
    collection = Collection()
    item = record()
    append_record(tenant_id="tenant-001", record=item, collection=collection, session=Session())
    with pytest.raises(Exception) as captured:
        read_record(
            tenant_id="tenant-002", institution_id="wilsy-pty-ltd",
            record_id="g64-record-001", collection=collection, session=Session(),
        )
    assert getattr(captured.value, "code", None) == "G64_REGISTRY_RECORD_NOT_FOUND"
