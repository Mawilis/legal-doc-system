"""Real replica-set transaction certification for hiring candidate and offer state."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import os
import uuid

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.hiring_lifecycle import (
    CandidateApplication, CandidateStage, CandidateStageEvidence,
    EmploymentOffer, OfferTerms,
)
from tools.eos.saas.hr.hiring_lifecycle_registry import (
    CANDIDATE_COLLECTION, OFFER_COLLECTION, EVENT_COLLECTION,
    HiringLifecycleRegistry, HiringLifecycleRegistryConflict,
)

URI = os.getenv("HIRING_TEST_MONGODB_URI")
pytestmark = pytest.mark.skipif(not URI, reason="HIRING_TEST_MONGODB_URI is not configured")
NOW = datetime(2026, 11, 7, 10, tzinfo=timezone.utc)


def _candidate(tenant: str, identity: str) -> CandidateApplication:
    return CandidateApplication(
        tenant_id=tenant, candidate_id=identity, requisition_id="REQ-001",
        candidate_profile_reference=f"candidate-profile://opaque/{identity}",
        source="CAREERS_PORTAL", created_by_principal_id="hr-manager", created_at=NOW,
    )


def _offer(tenant: str, identity: str) -> EmploymentOffer:
    return EmploymentOffer(
        tenant_id=tenant, offer_id=identity, requisition_id="REQ-001",
        candidate_id="CAN-001",
        terms=OfferTerms(
            position_title="Platform Engineer", employment_type="PERMANENT",
            work_location="Johannesburg", currency="ZAR",
            gross_compensation_minor=8500000, pay_frequency="MONTHLY",
            start_date=date(2027, 1, 1), expires_at=NOW + timedelta(days=21),
        ),
        prepared_by_principal_id="hr-manager", created_at=NOW,
    )


def _run(client, callback):
    with client.start_session() as session:
        return session.with_transaction(
            callback, read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority", j=True),
            read_preference=ReadPreference.PRIMARY,
        )


def test_replica_set_candidate_offer_commit_replay_rollback_revision_and_tenant_scope():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    database_name = f"hiring_cert_{uuid.uuid4().hex}"
    database = client[database_name]
    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        assert hello.get("setName"), "A MongoDB replica set is required"
        assert hello.get("isWritablePrimary") is True
        candidates = database.get_collection(
            CANDIDATE_COLLECTION, write_concern=WriteConcern("majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        offers = database.get_collection(
            OFFER_COLLECTION, write_concern=WriteConcern("majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        events = database.get_collection(
            EVENT_COLLECTION, write_concern=WriteConcern("majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        HiringLifecycleRegistry.ensure_indexes(candidates, offers, events)
        registry = HiringLifecycleRegistry(candidates, offers, events)
        tenant = f"WILSY-CERT-{uuid.uuid4().hex}"
        candidate = _candidate(tenant, "CAN-REAL-001")
        offer = _offer(tenant, "OFFER-REAL-001")

        _run(client, lambda tx: registry.create_candidate(
            candidate, actor_principal_id="hr-manager", occurred_at=NOW,
            session=tx, idempotency_key="candidate-create-1",
        ))
        _run(client, lambda tx: registry.create_offer(
            offer, actor_principal_id="hr-manager", occurred_at=NOW,
            session=tx, idempotency_key="offer-create-1",
        ))
        assert candidates.count_documents({"tenant_id": tenant}) == 1
        assert offers.count_documents({"tenant_id": tenant}) == 1
        assert events.count_documents({"tenant_id": tenant}) == 2

        # Mongo's generated _id must not violate the domain's strict schema.
        assert _run(client, lambda tx: registry.get_candidate(
            tenant_id=tenant, candidate_id=candidate.candidate_id, session=tx,
        )) == candidate
        assert _run(client, lambda tx: registry.get_offer(
            tenant_id=tenant, offer_id=offer.offer_id, session=tx,
        )) == offer
        assert _run(client, lambda tx: registry.create_candidate(
            candidate, actor_principal_id="hr-manager", occurred_at=NOW,
            session=tx, idempotency_key="candidate-create-1",
        )) == candidate

        advanced = candidate.advance(
            CandidateStage.SCREENING,
            CandidateStageEvidence(
                actor_principal_id="hr-manager", target_stage=CandidateStage.SCREENING,
                reason="Initial screening completed", evidence_reference="hr-evidence://screening/1",
                evidence_fingerprint="a" * 128, occurred_at=NOW,
            ), expected_revision=1,
        )
        _run(client, lambda tx: registry.transition_candidate(
            current=candidate, updated=advanced, actor_principal_id="hr-manager",
            action="CANDIDATE_SCREENING", occurred_at=NOW,
            expected_revision=1, session=tx,
            idempotency_key="candidate-screening-transition",
            command_fingerprint="b" * 128,
        ))
        replay = _run(client, lambda tx: registry.get_transition_replay(
            tenant_id=tenant, aggregate_type="CANDIDATE",
            aggregate_id=candidate.candidate_id, action="CANDIDATE_SCREENING",
            idempotency_key="candidate-screening-transition",
            command_fingerprint="b" * 128, session=tx,
        ))
        assert replay == advanced
        with pytest.raises(HiringLifecycleRegistryConflict):
            _run(client, lambda tx: registry.get_transition_replay(
                tenant_id=tenant, aggregate_type="CANDIDATE",
                aggregate_id=candidate.candidate_id, action="CANDIDATE_SCREENING",
                idempotency_key="candidate-screening-transition",
                command_fingerprint="c" * 128, session=tx,
            ))
        assert candidates.find_one({"tenant_id": tenant, "candidate_id": candidate.candidate_id})["revision"] == 2
        assert events.count_documents({"tenant_id": tenant, "aggregate_id": candidate.candidate_id}) == 2

        with pytest.raises(HiringLifecycleRegistryConflict):
            _run(client, lambda tx: registry.transition_candidate(
                current=candidate, updated=advanced, actor_principal_id="hr-manager",
                action="STALE_SCREENING", occurred_at=NOW,
                expected_revision=1, session=tx,
            ))

        class Abort(Exception):
            pass
        rolled_back = _candidate(tenant, "CAN-ROLLBACK")
        with pytest.raises(Abort):
            def abort(tx):
                registry.create_candidate(
                    rolled_back, actor_principal_id="hr-manager", occurred_at=NOW,
                    session=tx, idempotency_key="candidate-rollback",
                )
                raise Abort()
            _run(client, abort)
        assert candidates.find_one({"tenant_id": tenant, "candidate_id": rolled_back.candidate_id}) is None
        assert events.find_one({"tenant_id": tenant, "idempotency_key": "candidate-rollback"}) is None

        assert _run(client, lambda tx: registry.get_candidate(
            tenant_id="OTHER-TENANT", candidate_id=candidate.candidate_id, session=tx,
        )) if False else True
        from tools.eos.saas.hr.hiring_lifecycle_registry import HiringLifecycleNotFound
        with pytest.raises(HiringLifecycleNotFound):
            _run(client, lambda tx: registry.get_candidate(
                tenant_id="OTHER-TENANT", candidate_id=candidate.candidate_id, session=tx,
            ))
    finally:
        client.drop_database(database_name)
        client.close()
