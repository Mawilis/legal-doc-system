"""Real replica-set transaction certification for headcount requisitions."""
from __future__ import annotations

from datetime import datetime, timezone
import os
import uuid

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.headcount_requisition import (
    HeadcountApproval, HeadcountRequisition, RequisitionDecision,
)
from tools.eos.saas.hr.headcount_requisition_registry import (
    COLLECTION, EVENT_COLLECTION, HeadcountRequisitionRegistry,
)

URI = os.getenv("HEADCOUNT_TEST_MONGODB_URI")
pytestmark = pytest.mark.skipif(not URI, reason="HEADCOUNT_TEST_MONGODB_URI is not configured")


def _requisition(tenant: str, identity: str) -> HeadcountRequisition:
    return HeadcountRequisition(
        tenant_id=tenant, requisition_id=identity, department_id="engineering",
        position_title="Platform Engineer", employment_type="PERMANENT",
        work_location="Johannesburg", headcount=1,
        business_justification="Replica-set transaction certification",
        requested_by_principal_id="principal-requester",
    )


def test_real_replica_set_commits_requisition_and_immutable_events_atomically():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    database_name = f"headcount_cert_{uuid.uuid4().hex}"
    database = client[database_name]
    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        assert hello.get("setName"), "A replica set is required for transaction certification"
        assert hello.get("isWritablePrimary") is True

        current = database.get_collection(
            COLLECTION, write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        events = database.get_collection(
            EVENT_COLLECTION, write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        HeadcountRequisitionRegistry.ensure_indexes(current, events)
        registry = HeadcountRequisitionRegistry(current, events)
        tenant = f"WILSY-CERT-{uuid.uuid4().hex}"
        item = _requisition(tenant, "REQ-REAL-MONGO-1")

        with client.start_session() as session:
            session.with_transaction(
                lambda tx: registry.create_or_replay(
                    item, idempotency_key="create-1",
                    actor_principal_id="principal-requester",
                    occurred_at=datetime.now(timezone.utc), session=tx,
                ),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )

        assert current.count_documents({"tenant_id": tenant}) == 1
        assert events.count_documents({"tenant_id": tenant}) == 1

        now = datetime.now(timezone.utc)
        submitted = item.submit(
            actor_principal_id="principal-requester", submitted_at=now,
            expected_revision=1,
        )
        request_fingerprint = "a" * 128
        with client.start_session() as session:
            saved = session.with_transaction(
                lambda tx: registry.transition(
                    tenant_id=tenant, requisition_id=item.requisition_id,
                    expected_revision=1, updated=submitted, action="SUBMITTED",
                    actor_principal_id="principal-requester",
                    idempotency_key="submit-1",
                    request_fingerprint=request_fingerprint,
                    occurred_at=now, session=tx,
                ),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
        assert saved.revision == 2
        with client.start_session() as session:
            replay = registry.replay_transition(
                tenant_id=tenant, idempotency_key="submit-1",
                request_fingerprint=request_fingerprint, session=session,
            )
        assert replay == submitted

        approval = HeadcountApproval(
            decision_id="decision-real-mongo",
            actor_principal_id="independent-approver",
            decision=RequisitionDecision.APPROVE,
            reason="Independent approval",
            decided_at=now,
        )
        approved = submitted.decide(approval, expected_revision=2)
        with client.start_session() as session:
            session.with_transaction(
                lambda tx: registry.transition(
                    tenant_id=tenant, requisition_id=item.requisition_id,
                    expected_revision=2, updated=approved, action="APPROVE",
                    actor_principal_id="independent-approver",
                    idempotency_key="approve-1",
                    request_fingerprint="b" * 128,
                    occurred_at=now, session=tx,
                ),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
        assert current.find_one({"tenant_id": tenant, "requisition_id": item.requisition_id})["revision"] == 3
        assert events.count_documents({"tenant_id": tenant}) == 3
        assert current.count_documents({"tenant_id": "OTHER-TENANT"}) == 0

        class AbortCertification(Exception):
            pass

        aborted = _requisition(tenant, "REQ-ABORT-ME")
        with pytest.raises(AbortCertification):
            with client.start_session() as session:
                def abort(tx):
                    registry.create_or_replay(
                        aborted, idempotency_key="abort-create",
                        actor_principal_id="principal-requester",
                        occurred_at=now, session=tx,
                    )
                    raise AbortCertification()
                session.with_transaction(
                    abort,
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
        assert current.find_one({"tenant_id": tenant, "requisition_id": "REQ-ABORT-ME"}) is None
        assert events.find_one({"tenant_id": tenant, "idempotency_key": "abort-create"}) is None
    finally:
        client.drop_database(database_name)
        client.close()
