"""Real replica-set certificate for POS location assignment authority."""
from __future__ import annotations

from datetime import datetime, timezone
import os
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.pos_location_assignment import (
    POSLocationAssignment, POSLocationAssignmentStatus,
)
from tools.eos.saas.billing import pos_location_assignment_registry as registry


MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 11, 6, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"host Mongo unavailable during hello: {type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET or not hello.get("isWritablePrimary"):
            pytest.skip("expected writable wilsyVendorCertRS replica set")
        database = client[f"pos_location_rm_{uuid.uuid4().hex}"]
        history = database.get_collection(registry.HISTORY_COLLECTION, write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))
        current = database.get_collection(registry.CURRENT_COLLECTION, write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))
        registry.ensure_indexes(history, current)
        yield client, history, current
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _assignment(tenant="tenant-a", location="store-a", principal="operator-a"):
    return POSLocationAssignment(
        tenant_id=tenant, location_id=location, principal_id=principal,
        assignment_id=f"assignment-{uuid.uuid4().hex}", revision=0,
        status=POSLocationAssignmentStatus.ACTIVE,
        authority_reference="workforce-assignment:123",
        authority_fingerprint="a" * 128, idempotency_key=f"issue-{uuid.uuid4().hex}",
        occurred_at=NOW, changed_by_principal_id="principal-issuer",
    )


def _transaction(client, callback):
    with client.start_session() as session:
        return session.with_transaction(callback)


def test_real_replica_set_issue_resolve_revoke_and_tenant_location_isolation(mongo_context):
    client, history, current = mongo_context
    value = _assignment()
    issued = _transaction(client, lambda tx: registry.issue(value, history, current, session=tx))
    assert issued.to_dict() == value.to_dict()
    assert history.count_documents({"tenant_id": value.tenant_id, "assignment_id": value.assignment_id}) == 1

    resolved = _transaction(client, lambda tx: registry.resolve(value.tenant_id, value.location_id, value.principal_id, current, session=tx))
    assert resolved.to_dict() == value.to_dict()
    with pytest.raises(registry.POSLocationAssignmentNotFound):
        _transaction(client, lambda tx: registry.resolve("tenant-b", value.location_id, value.principal_id, current, session=tx))
    with pytest.raises(registry.POSLocationAssignmentNotFound):
        _transaction(client, lambda tx: registry.resolve(value.tenant_id, "store-b", value.principal_id, current, session=tx))

    revoked = _transaction(client, lambda tx: registry.revoke(
        tenant_id=value.tenant_id, location_id=value.location_id,
        principal_id=value.principal_id, assignment_id=value.assignment_id,
        expected_revision=0, authority_reference="governed-revocation:synthetic",
        authority_fingerprint="b" * 128, idempotency_key=f"revoke-{uuid.uuid4().hex}",
        occurred_at=NOW, changed_by_principal_id="principal-issuer",
        reason="assignment ended", history=history, current=current, session=tx,
    ))
    assert revoked.status is POSLocationAssignmentStatus.REVOKED and revoked.revision == 1
    assert history.count_documents({"tenant_id": value.tenant_id, "assignment_id": value.assignment_id}) == 2
    with pytest.raises(registry.POSLocationAssignmentNotFound):
        _transaction(client, lambda tx: registry.resolve(value.tenant_id, value.location_id, value.principal_id, current, session=tx))


def test_real_replica_set_rejects_stale_revocation_without_history_mutation(mongo_context):
    client, history, current = mongo_context
    value = _assignment()
    _transaction(client, lambda tx: registry.issue(value, history, current, session=tx))
    with pytest.raises(registry.POSLocationAssignmentConflict):
        _transaction(client, lambda tx: registry.revoke(
            tenant_id=value.tenant_id, location_id=value.location_id,
            principal_id=value.principal_id, assignment_id=value.assignment_id,
            expected_revision=9, authority_reference="governed-revocation:synthetic",
            authority_fingerprint="b" * 128, idempotency_key=f"revoke-{uuid.uuid4().hex}",
            occurred_at=NOW, changed_by_principal_id="principal-issuer",
            reason="stale command", history=history, current=current, session=tx,
        ))
    assert history.count_documents({"tenant_id": value.tenant_id, "assignment_id": value.assignment_id}) == 1
    assert current.count_documents({"tenant_id": value.tenant_id, "location_id": value.location_id, "status": "ACTIVE"}) == 1
