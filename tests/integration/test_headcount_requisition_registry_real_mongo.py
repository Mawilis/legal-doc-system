from datetime import datetime, timezone
import os
import uuid

import pytest
from pymongo import MongoClient

from tools.eos.saas.domain.headcount_requisition import HeadcountRequisition
from tools.eos.saas.hr.headcount_requisition_registry import (
    HeadcountRequisitionRegistryConflict,
    HeadcountRequisitionRegistryNotFound,
    HeadcountRequisitionRegistryTransactionRequired,
    COLLECTION,
    create_requisition,
    ensure_indexes,
    get_requisition,
    replace_requisition,
)


@pytest.fixture
def mongo_scope():
    uri = os.environ.get("TEST_VENDOR_MONGO_URI")
    if not uri:
        pytest.skip("TEST_VENDOR_MONGO_URI is required for replica-set certification")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    database_name = f"headcount_registry_{uuid.uuid4().hex}"
    database = client[database_name]
    collection = database[COLLECTION]
    ensure_indexes(collection)
    try:
        yield client, collection
    finally:
        client.drop_database(database_name)
        client.close()


def draft():
    return HeadcountRequisition(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        requisition_id="REQ-REAL-MONGO-001",
        department_id="ENGINEERING",
        position_title="Platform Engineer",
        employment_type="PERMANENT",
        work_location="HYBRID",
        headcount=1,
        business_justification="Approved reliability capacity.",
        requested_by_principal_id="principal-requester",
    )


def test_headcount_registry_requires_transaction_and_guards_tenant_revision(mongo_scope):
    client, collection = mongo_scope
    value = draft()

    with client.start_session() as session:
        with pytest.raises(HeadcountRequisitionRegistryTransactionRequired):
            create_requisition(value, collection, session=session)

        with session.start_transaction():
            create_requisition(value, collection, session=session)
            loaded = get_requisition(value.tenant_id, value.requisition_id, collection, session=session)
            assert loaded.to_dict() == value.to_dict()

    submitted = value.submit(
        actor_principal_id="principal-requester",
        submitted_at=datetime(2026, 11, 7, tzinfo=timezone.utc),
        expected_revision=1,
    )
    with client.start_session() as session:
        with session.start_transaction():
            replace_requisition(
                submitted,
                expected_revision=1,
                expected_fingerprint=value.fingerprint,
                collection=collection,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            loaded = get_requisition(value.tenant_id, value.requisition_id, collection, session=session)
            assert loaded.status.value == "SUBMITTED"
            assert loaded.revision == 2
            with pytest.raises(HeadcountRequisitionRegistryConflict):
                replace_requisition(
                    submitted,
                    expected_revision=1,
                    expected_fingerprint=value.fingerprint,
                    collection=collection,
                    session=session,
                )
            with pytest.raises(HeadcountRequisitionRegistryNotFound):
                get_requisition("OTHER-TENANT", value.requisition_id, collection, session=session)
