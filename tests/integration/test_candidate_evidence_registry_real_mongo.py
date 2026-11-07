"""Replica-set certification for immutable candidate evidence custody metadata."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import uuid

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.candidate_evidence import CandidateEvidenceKind, CandidateEvidenceObjectMetadata
from tools.eos.saas.hr.candidate_evidence_registry import (
    COLLECTION, EVENT_COLLECTION, CandidateEvidenceRegistry,
    CandidateEvidenceRegistryConflict, CandidateEvidenceRegistryNotFound,
)

URI = os.getenv("HIRING_TEST_MONGODB_URI")
pytestmark = pytest.mark.skipif(not URI, reason="HIRING_TEST_MONGODB_URI is not configured")
NOW = datetime(2026, 11, 7, 12, tzinfo=timezone.utc)


def _run(client, callback):
    with client.start_session() as session:
        return session.with_transaction(
            callback, read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority", j=True),
            read_preference=ReadPreference.PRIMARY,
        )


def _evidence(kind, offer_id=None):
    return CandidateEvidenceObjectMetadata(
        tenant_id="WILSYTENANT-4CD2FZ4O", candidate_id="CAN-CUSTODY-001",
        evidence_id="EVD-001", evidence_version_id="EVDV-001",
        evidence_kind=kind, media_type="application/pdf",
        original_filename="evidence.pdf", byte_length=2048,
        content_digest_sha3_512="a" * 128, storage_provider_id="aws_s3",
        storage_object_reference="opaque-object-reference",
        object_version_reference="opaque-object-version",
        provider_integrity_reference="opaque-provider-integrity",
        ingestion_reference="ING-001", created_at=NOW,
        created_by_principal_id="principal-hr-director", offer_id=offer_id,
        retention_until=NOW + timedelta(days=365),
    )


def test_candidate_evidence_metadata_commit_replay_conflict_rollback_and_tenant_scope():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    name = f"candidate_evidence_{uuid.uuid4().hex}"
    db = client[name]
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        metadata = db.get_collection(COLLECTION, write_concern=WriteConcern("majority", j=True), read_concern=ReadConcern("majority"))
        events = db.get_collection(EVENT_COLLECTION, write_concern=WriteConcern("majority", j=True), read_concern=ReadConcern("majority"))
        CandidateEvidenceRegistry.ensure_indexes(metadata, events)
        registry = CandidateEvidenceRegistry(metadata, events)

        profile = _evidence(CandidateEvidenceKind.CANDIDATE_PROFILE)
        assert _run(client, lambda tx: registry.register(
            profile, actor_principal_id="principal-hr-director",
            idempotency_key="profile-evidence-1", session=tx,
        )) == profile
        assert _run(client, lambda tx: registry.register(
            profile, actor_principal_id="principal-hr-director",
            idempotency_key="profile-evidence-1", session=tx,
        )) == profile
        assert _run(client, lambda tx: registry.get(
            tenant_id=profile.tenant_id, candidate_id=profile.candidate_id,
            evidence_id=profile.evidence_id, evidence_version_id=profile.evidence_version_id,
            session=tx,
        )) == profile
        assert "content_bytes" not in metadata.find_one({"tenant_id": profile.tenant_id})
        assert events.count_documents({"tenant_id": profile.tenant_id}) == 1

        divergent = _evidence(CandidateEvidenceKind.SIGNED_OFFER, "OFFER-001")
        with pytest.raises(CandidateEvidenceRegistryConflict):
            _run(client, lambda tx: registry.register(
                divergent, actor_principal_id="principal-hr-director",
                idempotency_key="profile-evidence-1", session=tx,
            ))

        class Abort(Exception): pass
        rolled_back = CandidateEvidenceObjectMetadata(
            tenant_id=profile.tenant_id, candidate_id=profile.candidate_id,
            evidence_id="EVD-ROLLBACK", evidence_version_id="EVDV-ROLLBACK",
            evidence_kind=CandidateEvidenceKind.CANDIDATE_PROFILE,
            media_type="application/pdf", original_filename="rollback.pdf",
            byte_length=128, content_digest_sha3_512="b" * 128,
            storage_provider_id="aws_s3", storage_object_reference="opaque-rollback",
            object_version_reference="opaque-rollback-version",
            provider_integrity_reference="opaque-rollback-integrity",
            ingestion_reference="ING-ROLLBACK", created_at=NOW,
            created_by_principal_id="principal-hr-director",
        )
        with pytest.raises(Abort):
            def abort(tx):
                registry.register(rolled_back, actor_principal_id="principal-hr-director", idempotency_key="rollback", session=tx)
                raise Abort()
            _run(client, abort)
        assert metadata.find_one({"tenant_id": profile.tenant_id, "evidence_id": "EVD-ROLLBACK"}) is None
        assert events.find_one({"tenant_id": profile.tenant_id, "idempotency_key": "rollback"}) is None

        with pytest.raises(CandidateEvidenceRegistryNotFound):
            _run(client, lambda tx: registry.get(
                tenant_id="OTHER-TENANT", candidate_id=profile.candidate_id,
                evidence_id=profile.evidence_id, evidence_version_id=profile.evidence_version_id,
                session=tx,
            ))
    finally:
        client.drop_database(name)
        client.close()
