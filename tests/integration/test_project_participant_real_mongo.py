"""TITLE: WILSY OS Project Participant Replica-Set Certificate
VERSION: v1.1.0-PRINCIPAL-PROJECT-DISCOVERY-REPLICA-CERT
AUTHORITY: Disposable MongoDB test-owned authority; never a real tenant grant.
EPITOME: Certify indexes, transactional participant grant/replay/revocation,
         source CAS, foreign-tenant absence and immutable event history.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_project_participant_real_mongo.py
COLLABORATION / OWNERSHIP: ProjectParticipantRegistry; existing Projects
         accountability CI owns the disposable replica and cleanup.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.1.0-PRINCIPAL-PROJECT-DISCOVERY-REPLICA-CERT proves
         principal-scoped project discovery and revocation immediately
         withdraws visibility without an inherited owner privilege.
CHANGELOG: v1.1.0-PRINCIPAL-PROJECT-DISCOVERY-REPLICA-CERT certifies revoked participants
         are hidden like unknown/foreign records even for stale retries.
CHANGELOG: v1.1.0-PRINCIPAL-PROJECT-DISCOVERY-REPLICA-CERT adds a test of durable
         explicit role evidence with cross-tenant denial and revision replay.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No real principal, subscription or project data.
TENANT BOUNDARY: Every Mongo operation is exact tenant/project scoped.
AUTHORITY BOUNDARY: Persistence proof only; HTTP admission remains separate.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.saas.projects.project_participant_registry import (
    ProjectParticipantRegistry, ProjectParticipantConflict,
    ProjectParticipantNotFound,
)


def test_disposable_project_participant_grant_replay_revoke() -> None:
    """Only a source-owned transaction persists one exact participant grant."""
    uri = os.environ.get("TEST_PROJECTS_ACCOUNTABILITY_MONGO_URI")
    if not uri:
        pytest.skip("Disposable MongoDB replica-set URI not configured")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=4000)
    database = client.get_database("wilsy_project_participant_cert")
    try:
        client.admin.command("ping")
        client.drop_database(database.name)
        participants = database["wilsy_project_participants"]
        events = database["wilsy_project_participant_events"]
        ProjectParticipantRegistry.ensure_indexes(participants, events)
        assert participants.index_information()["wilsy_project_participant_identity_unique"]["unique"]
        assert events.index_information()["wilsy_project_participant_replay_unique"]["unique"]
        store = ProjectParticipantRegistry(participants, events)
        tenant, foreign = "participant-tenant-a", "participant-tenant-b"
        project_id = "prj-" + "e" * 48
        principal = "participant-one"
        actor = "authorized-owner"
        instant = datetime.now(timezone.utc).replace(microsecond=0)

        def transaction(work):
            with client.start_session() as session:
                return session.with_transaction(
                    work, read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )

        def grant(session):
            return store.grant(
                tenant_id=tenant, project_id=project_id, principal_id=principal,
                role="CONTRIBUTOR", actor_principal_id=actor,
                idempotency_key="grant-1", occurred_at=instant, session=session,
            )
        first = transaction(grant)
        own_page, own_more = transaction(lambda session: store.projects_for_principal(
            tenant_id=tenant, principal_id=principal, session=session,
        ))
        assert own_page == (first,) and own_more is False
        foreign_principal_page, foreign_principal_more = transaction(
            lambda session: store.projects_for_principal(
                tenant_id=tenant, principal_id="unassigned-person", session=session,
            ),
        )
        assert foreign_principal_page == () and foreign_principal_more is False
        foreign_tenant_page, foreign_tenant_more = transaction(
            lambda session: store.projects_for_principal(
                tenant_id=foreign, principal_id=principal, session=session,
            ),
        )
        assert foreign_tenant_page == () and foreign_tenant_more is False
        replay = transaction(grant)
        assert first == replay
        assert first.state == "ACTIVE" and first.revision == 1
        assert events.count_documents({"tenant_id": tenant}) == 1
        with client.start_session() as session:
            assert store.get(
                tenant_id=tenant, project_id=project_id,
                principal_id=principal, session=session,
            ) == first
            with pytest.raises(ProjectParticipantNotFound):
                store.get(
                    tenant_id=foreign, project_id=project_id,
                    principal_id=principal, session=session,
                )
            page, more = store.page(
                tenant_id=tenant, project_id=project_id, session=session,
            )
            assert page == (first,) and more is False
            foreign_page, foreign_more = store.page(
                tenant_id=foreign, project_id=project_id, session=session,
            )
            assert foreign_page == () and foreign_more is False
        with pytest.raises(ProjectParticipantConflict, match="DIVERGENT_REPLAY"):
            transaction(lambda session: store.grant(
                tenant_id=tenant, project_id=project_id,
                principal_id="other-person", role="VIEWER",
                actor_principal_id=actor, idempotency_key="grant-1",
                occurred_at=instant, session=session,
            ))
        with pytest.raises(ProjectParticipantConflict, match="ALREADY_ASSIGNED"):
            transaction(lambda session: store.grant(
                tenant_id=tenant, project_id=project_id,
                principal_id=principal, role="CONTRIBUTOR",
                actor_principal_id=actor, idempotency_key="different-key",
                occurred_at=instant, session=session,
            ))

        def revoke(session):
            return store.revoke(
                tenant_id=tenant, project_id=project_id, principal_id=principal,
                actor_principal_id=actor, expected_revision=1,
                idempotency_key="revoke-1", occurred_at=instant + timedelta(seconds=1),
                session=session,
            )
        removed = transaction(revoke)
        assert removed.state == "REVOKED" and removed.revision == 2
        revoked_page, revoked_more = transaction(
            lambda session: store.projects_for_principal(
                tenant_id=tenant, principal_id=principal, session=session,
            ),
        )
        assert revoked_page == () and revoked_more is False
        assert transaction(revoke) == removed
        with client.start_session() as session:
            with pytest.raises(ProjectParticipantNotFound):
                store.get(
                    tenant_id=tenant, project_id=project_id,
                    principal_id=principal, session=session,
                )
            assert store.get(
                tenant_id=tenant, project_id=project_id,
                principal_id=principal, session=session, require_active=False,
            ) == removed
        with pytest.raises(ProjectParticipantNotFound):
            transaction(lambda session: store.revoke(
                tenant_id=tenant, project_id=project_id, principal_id=principal,
                actor_principal_id=actor, expected_revision=1,
                idempotency_key="revoke-stale",
                occurred_at=instant + timedelta(seconds=2), session=session,
            ))
        assert events.count_documents({"tenant_id": tenant}) == 2
        assert participants.count_documents({
            "tenant_id": tenant, "project_id": project_id,
            "principal_id": principal, "state": "REVOKED",
        }) == 1
        assert participants.count_documents({"tenant_id": foreign}) == 0
    finally:
        client.drop_database(database.name)
        client.close()


# ARTIFACT: test_project_participant_real_mongo.py
# VERSION: v1.1.0-PRINCIPAL-PROJECT-DISCOVERY-REPLICA-CERT
# AUTHORITY BOUNDARY: only synthetic source persistence, no live IAM
# TENANT POSTURE: foreign tenant and project reads return absence
# FAIL-CLOSED POSTURE: diverging replay, stale revision, revoked access denied
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
