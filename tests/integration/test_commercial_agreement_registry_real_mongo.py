from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.entitlement.commercial_agreement import (
    CommercialAgreement,
    CommercialAgreementState,
    CommercialRenewalMode,
)
from tools.eos.saas.entitlement.commercial_agreement_registry import (
    CURRENT_COLLECTION,
    HISTORY_COLLECTION,
    CommercialAgreementPersistenceOutcome,
    CommercialAgreementRegistryConflictError,
    CommercialAgreementRegistryNotFoundError,
    CommercialAgreementRegistryPersistedRecordInvalidError,
    create_or_replay,
    ensure_indexes,
    get_current,
    get_history,
    transition,
)
from tools.eos.saas.entitlement.commercial_offer_catalogue import (
    CommercialOfferId,
    get_commercial_offer,
)

MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000,
        retryWrites=True, tz_aware=True,
    )
    database = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"host Mongo unavailable during hello: {type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("replica set has no logical-session capability")
        database = client[f"wilsy_commercial_agreement_{uuid.uuid4().hex}"]
        history = database.get_collection(
            HISTORY_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        current = database.get_collection(
            CURRENT_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        ensure_indexes(history, current)
        yield client, history, current
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _draft(tenant: str, agreement_id: str = "agreement-1") -> CommercialAgreement:
    offer = get_commercial_offer(CommercialOfferId.LEGAL_OPERATIONS)
    return CommercialAgreement(
        tenant_id=tenant,
        agreement_id=agreement_id,
        offer_id=offer.offer_id,
        offer_fingerprint=offer.fingerprint,
        contract_reference=f"contract-{agreement_id}",
        contract_version="2026-11-01",
        counterparty_legal_name="Certificate Counterparty (Pty) Ltd",
        effective_at=NOW,
        expires_at=NOW + timedelta(days=365),
        renewal_mode=CommercialRenewalMode.MANUAL,
        notice_days=30,
        termination_terms_reference="terms-1",
    )


def _create(client, agreement, history, current):
    with client.start_session() as session:
        with session.start_transaction():
            return create_or_replay(agreement, history, current, session=session)


def _transition(client, tenant, agreement_id, target, revision, ref, fp, history, current):
    with client.start_session() as session:
        with session.start_transaction():
            return transition(
                tenant_id=tenant,
                agreement_id=agreement_id,
                target_state=target,
                expected_revision=revision,
                evidence_reference=ref,
                evidence_fingerprint=fp,
                occurred_at=NOW + timedelta(minutes=revision + 1),
                history_collection=history,
                current_collection=current,
                session=session,
            )


def test_real_indexes_are_exact_unique_and_non_expiring(mongo_context):
    _, history, current = mongo_context
    h = {item["name"]: item for item in history.list_indexes() if item["name"] != "_id_"}
    c = {item["name"]: item for item in current.list_indexes() if item["name"] != "_id_"}
    assert set(h) == {
        "commercial_agreement_tenant_revision_unique",
        "commercial_agreement_tenant_fingerprint_unique",
    }
    assert set(c) == {"commercial_agreement_current_tenant_identity_unique"}
    assert h["commercial_agreement_tenant_revision_unique"]["unique"] is True
    assert h["commercial_agreement_tenant_fingerprint_unique"]["unique"] is True
    assert c["commercial_agreement_current_tenant_identity_unique"]["unique"] is True
    assert all("expireAfterSeconds" not in item for item in [*h.values(), *c.values()])


def test_real_create_exact_replay_history_and_cross_tenant_absence(mongo_context):
    client, history, current = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    other = f"tenant-{uuid.uuid4().hex}"
    value = _draft(tenant)
    first = _create(client, value, history, current)
    replay = _create(client, value, history, current)
    assert first[0] is CommercialAgreementPersistenceOutcome.CREATED
    assert replay[0] is CommercialAgreementPersistenceOutcome.IDEMPOTENT_REPLAY
    assert history.count_documents({"tenant_id": tenant}) == 1
    assert current.count_documents({"tenant_id": tenant}) == 1
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(CommercialAgreementRegistryNotFoundError):
                get_current(other, value.agreement_id, history, current, session=session)
            assert get_history(tenant, value.agreement_id, history, session=session) == (value,)


def test_real_transaction_abort_leaves_no_history_or_pointer(mongo_context):
    client, history, current = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    value = _draft(tenant)
    with client.start_session() as session:
        session.start_transaction()
        create_or_replay(value, history, current, session=session)
        session.abort_transaction()
    assert history.count_documents({"tenant_id": tenant}) == 0
    assert current.count_documents({"tenant_id": tenant}) == 0


def test_real_revision_cas_replay_stale_writer_and_readback(mongo_context):
    client, history, current = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    value = _draft(tenant)
    _create(client, value, history, current)
    executed, executed_value = _transition(
        client, tenant, value.agreement_id, CommercialAgreementState.EXECUTED,
        0, "signature-1", "a" * 128, history, current,
    )
    assert executed is CommercialAgreementPersistenceOutcome.TRANSITIONED
    active, active_value = _transition(
        client, tenant, value.agreement_id, CommercialAgreementState.ACTIVE,
        1, "activation-1", "b" * 128, history, current,
    )
    assert active is CommercialAgreementPersistenceOutcome.TRANSITIONED
    replay, replay_value = _transition(
        client, tenant, value.agreement_id, CommercialAgreementState.ACTIVE,
        1, "activation-1", "b" * 128, history, current,
    )
    assert replay is CommercialAgreementPersistenceOutcome.IDEMPOTENT_REPLAY
    assert replay_value.to_dict() == active_value.to_dict()
    assert executed_value.lifecycle_revision == 1
    assert active_value.lifecycle_revision == 2
    assert len(get_history_after(client, tenant, value.agreement_id, history)) == 3
    with pytest.raises(CommercialAgreementRegistryConflictError):
        _transition(
            client, tenant, value.agreement_id, CommercialAgreementState.SUSPENDED,
            1, "stale-suspension", "c" * 128, history, current,
        )


def get_history_after(client, tenant, agreement_id, history):
    with client.start_session() as session:
        with session.start_transaction():
            return get_history(tenant, agreement_id, history, session=session)


def test_real_current_pointer_corruption_fails_closed(mongo_context):
    client, history, current = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    value = _draft(tenant)
    _create(client, value, history, current)
    current.update_one(
        {"tenant_id": tenant, "agreement_id": value.agreement_id},
        {"$set": {"agreement_fingerprint": "f" * 128}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(CommercialAgreementRegistryPersistedRecordInvalidError):
                get_current(tenant, value.agreement_id, history, current, session=session)
