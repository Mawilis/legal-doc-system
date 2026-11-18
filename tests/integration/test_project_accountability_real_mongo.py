"""TITLE: WILSY OS Project Accountability Real Replica-Set Certificate
VERSION: v1.5.0-INDEXED-OWNER-PROJECT-REPLICA-CERT
AUTHORITY: Synthetic integration evidence for Python EOS project persistence.
EPITOME: Exercise principal membership/role currentness, tenant department
         immutable command evidence, project CAS, readback and revocation
         against an isolated disposable MongoDB replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_project_accountability_real_mongo.py
COLLABORATION / OWNERSHIP: Projects router, canonical tenant IAM repositories,
         ProjectRegistry and disposable CI replica set only.
CERTIFICATION / UPDATE DATE: 2026-11-18
CHANGELOG: v1.5.0-INDEXED-OWNER-PROJECT-REPLICA-CERT verifies exact tenant+owner indexed pagination of 256 matching records across 511 synthetic projects, with foreign-tenant denial in an isolated real Mongo replica.
CHANGELOG: v1.5.0-INDEXED-OWNER-PROJECT-REPLICA-CERT certifies coloured note create, author colour-CAS revision, provider-independent Mongo readback and immutable event fingerprints while preserving legacy colourless note replay.
CHANGELOG: v1.5.0-INDEXED-OWNER-PROJECT-REPLICA-CERT verifies tenant-bound first/last name reads from a synthetic durable auth user while project owner commands still use exact principal identity; foreign identity names cannot leak.
CHANGELOG: v1.5.0-INDEXED-OWNER-PROJECT-REPLICA-CERT certifies transactional note revisions,
         author denial, replay, foreign-tenant absence and immutable note events
         on disposable MongoDB; no real principal or project activation.
CHANGELOG: v1.5.0-INDEXED-OWNER-PROJECT-REPLICA-CERT adds disposable real-replica certification for
         511 source-valid tenant projects, complete indexed page traversal,
         immutable tenant isolation and summary counts.
         v1.0.0-PROJECT-ACCOUNTABILITY-REPLICA-CERT establishes exact-tenant
         persistence proof without creating production records.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque IDs and disposable DB only.
TENANT BOUNDARY: Every read, mutation, event and revocation is exact-tenant.
AUTHORITY BOUNDARY: The injected transaction seam isolates persistence tests;
         HTTP IAM and Projects entitlement are separately certified and are
         NOT bypassed in production routes.
FINANCIAL AUTHORITY BOUNDARY: No payments; Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import os
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import HTTPException, Response
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api import projects_router as router
from tools.eos.saas.domain.project import Project, ProjectStatus
from tools.eos.saas.domain.project_note import ProjectNote
from tools.eos.saas.projects.project_note_registry import (
    ProjectNoteRegistry, ProjectNoteConflict, ProjectNoteNotFound,
    note_id_for_command,
)
from tools.eos.saas.projects.project_registry import (
    ProjectNotFound, ProjectRegistry,
)


def test_real_replica_project_owner_department_assignment_and_revocation(monkeypatch):
    """Certify transaction-backed department and assignment truth in isolation."""
    uri = os.environ.get("TEST_PROJECTS_ACCOUNTABILITY_MONGO_URI")
    if not uri:
        pytest.skip("Disposable MongoDB replica-set URI not configured")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=4000)
    database = client.get_database("wilsy_projects_accountability_cert")
    try:
        client.admin.command("ping")
        # This database belongs exclusively to the disposable CI replica set.
        client.drop_database(database.name)
        projects = database.get_collection("wilsy_projects")
        events = database.get_collection("wilsy_project_events")
        ProjectRegistry.ensure_indexes(projects, events)
        registry = ProjectRegistry(projects, events)
        tenant = "cert-tenant-a"
        principal_id = "cert-owner-a"
        project_id = "prj-" + "a" * 48
        now = datetime.now(timezone.utc)
        database["principal_authorities"].insert_one({
            "principal_id": principal_id, "status": "ACTIVE", "revision": 0,
        })
        database["users"].insert_many([
            {"user_id": principal_id, "tenantId": tenant,
             "firstName": "Verified", "lastName": "Owner"},
            {"user_id": principal_id, "tenantId": "foreign-tenant",
             "firstName": "Foreign", "lastName": "Person"},
        ])
        database["tenant_memberships"].insert_one({
            "principal_id": principal_id, "tenant_id": tenant,
            "status": "ACTIVE", "revision": 0,
        })
        database["tenant_business_roles"].insert_one({
            "principal_id": principal_id, "tenant_id": tenant,
            "business_role": "tenant_owner", "status": "ACTIVE",
            "revision": 0, "effective_at": now, "revoked_at": None,
        })
        value = Project(
            tenant_id=tenant, project_id=project_id, name="Tenant project",
            code="CERT-PROJECT", summary=None, status=ProjectStatus.PLANNED,
            owner_principal_id=None, department_id=None,
            start_date=date(2026, 11, 1), target_date=None,
            source_type="internal", external_source_reference=None,
            created_by_principal_id=principal_id, created_at=now,
            updated_by_principal_id=principal_id, updated_at=now,
        )
        with client.start_session() as session:
            session.with_transaction(
                lambda tx: registry.create_or_replay(
                    project=value, actor_principal_id=principal_id,
                    idempotency_key="create-project", occurred_at=now, session=tx,
                ),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
        context = SimpleNamespace(
            tenant_id=tenant, identity=SimpleNamespace(identity_id=principal_id),
        )
        monkeypatch.setattr(router.kernel_db, "get_database", lambda: database)

        # Persistence-only seam. Real HTTP authorizations and active product
        # entitlement continue to be enforced by production _transaction.
        def transaction(_context, callback, **_kwargs):
            with client.start_session() as session:
                return session.with_transaction(
                    lambda tx: callback(registry, tx),
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
        monkeypatch.setattr(router, "_transaction", transaction)

        initial = router.project_assignment_options(Response(), context)
        assert initial["tenant_id"] == tenant
        assert initial["principals"] == [{
            "principal_id": principal_id, "eligibility": "VERIFIED_CURRENT",
            "first_name": "Verified", "last_name": "Owner",
        }]
        assert initial["departments"] == []
        department_result = router.provision_project_department(
            router.DepartmentCreateRequest(name="Engineering"),
            Response(), "department-request", context, context,
        )
        replay = router.provision_project_department(
            router.DepartmentCreateRequest(name="Engineering"),
            Response(), "department-request", context, context,
        )
        assert replay == department_result
        department_id = department_result["department"]["department_id"]
        assert database["wilsy_tenant_department_events"].count_documents({
            "tenant_id": tenant, "department_id": department_id,
        }) == 1
        options = router.project_assignment_options(Response(), context)
        assert options["departments"][0]["department_id"] == department_id

        assigned = router.assign_project_accountability(
            router.ProjectAssignmentRequest(
                expected_revision=1, owner_principal_id=principal_id,
                department_id=department_id,
            ), Response(), project_id, "assign-request", context,
        )
        assert assigned["project"]["status"] == "planned"
        assert assigned["project"]["revision"] == 2
        assert assigned["project"]["owner_principal_id"] == principal_id
        assert assigned["project"]["department_id"] == department_id
        fresh = router.get_project(Response(), project_id, False, context)
        assert fresh["project"] == assigned["project"]
        assert len(fresh["events"]) == 2
        assert fresh["events"][-1]["event_type"] == "PROJECT_UPDATED"

        with client.start_session() as session:
            with pytest.raises(ProjectNotFound):
                registry.get(tenant_id="cert-tenant-b", project_id=project_id, session=session)

        # Currentness removal never rewrites historical project/event evidence.
        database["tenant_memberships"].update_one(
            {"tenant_id": tenant, "principal_id": principal_id},
            {"$set": {"status": "REVOKED"}},
        )
        with pytest.raises(HTTPException) as denied:
            router.assign_project_accountability(
                router.ProjectAssignmentRequest(
                    expected_revision=2, owner_principal_id=principal_id,
                    department_id=department_id,
                ), Response(), project_id, "revoked-assign-request", context,
            )
        assert denied.value.status_code == 409
        assert denied.value.detail == "PROJECT_OWNER_NOT_ELIGIBLE"
        with pytest.raises(HTTPException) as activation:
            router.update_project(
                router.ProjectUpdateRequest(
                    expected_revision=2, status=ProjectStatus.ACTIVE,
                ), Response(), project_id, "attempt-activate", context,
            )
        assert activation.value.status_code == 409
        assert database["wilsy_projects"].find_one({
            "tenant_id": tenant, "project_id": project_id,
        })["status"] == "planned"
    finally:
        client.drop_database(database.name)
        client.close()


def test_real_replica_511_project_summary_and_verified_pages() -> None:
    """Read 511 exact-tenant projects across real Mongo indexes and transactions."""
    uri = os.environ.get("TEST_PROJECTS_ACCOUNTABILITY_MONGO_URI")
    if not uri:
        pytest.skip("Disposable MongoDB replica-set URI not configured")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=4000)
    database = client.get_database("wilsy_projects_scale_cert")
    try:
        client.admin.command("ping")
        client.drop_database(database.name)
        collection = database.get_collection("wilsy_projects")
        events = database.get_collection("wilsy_project_events")
        ProjectRegistry.ensure_indexes(collection, events)
        index = collection.index_information()
        assert index["wilsy_project_tenant_active_recent"]["key"] == [
            ("tenant_id", 1), ("archived_at", 1), ("updated_at", -1), ("project_id", 1),
        ]
        assert index["wilsy_project_tenant_status_recent"]["key"] == [
            ("tenant_id", 1), ("archived_at", 1), ("status", 1),
            ("updated_at", -1), ("project_id", 1),
        ]
        assert index["wilsy_project_tenant_owner_recent"]["key"] == [
            ("tenant_id", 1), ("owner_principal_id", 1),
            ("archived_at", 1), ("updated_at", -1), ("project_id", 1),
        ]
        instant = datetime.now(timezone.utc)
        rows = [
            Project(
                tenant_id="scale-tenant-a", project_id=f"prj-{number:048x}",
                name=f"Verified project {number}", code=f"SCALE-{number:04}",
                summary=None, status=ProjectStatus.PLANNED,
                owner_principal_id="scale-principal" if number % 2 == 0 else "other-principal",
                department_id=None, start_date=None, target_date=None,
                source_type="internal", external_source_reference=None,
                created_by_principal_id="scale-principal",
                created_at=instant, updated_by_principal_id="scale-principal",
                updated_at=instant,
            ).to_dict()
            for number in range(511)
        ]
        rows.append(Project(
            tenant_id="scale-tenant-b", project_id="prj-" + "f" * 48,
            name="Foreign tenant project", code="FOREIGN",
            summary=None, status=ProjectStatus.PLANNED,
            owner_principal_id="scale-principal", department_id=None,
            start_date=None, target_date=None,
            source_type="internal", external_source_reference=None,
            created_by_principal_id="foreign-principal",
            created_at=instant, updated_by_principal_id="foreign-principal",
            updated_at=instant,
        ).to_dict())
        collection.insert_many(rows, ordered=True)
        registry = ProjectRegistry(collection, events)
        with client.start_session() as session:
            def read(tx: Any):
                counts = registry.summary_for_tenant(
                    tenant_id="scale-tenant-a", session=tx,
                )
                first, first_has_more = registry.list_page_for_tenant(
                    tenant_id="scale-tenant-a", session=tx, limit=500,
                )
                final, final_has_more = registry.list_page_for_tenant(
                    tenant_id="scale-tenant-a", session=tx,
                    limit=500, offset=500,
                )
                owner_pages = []
                owner_offset = 0
                while True:
                    page, more = registry.list_page_for_tenant(
                        tenant_id="scale-tenant-a", session=tx, limit=100,
                        offset=owner_offset, owner_principal_id="scale-principal",
                    )
                    owner_pages.extend(page)
                    owner_offset += len(page)
                    if not more:
                        break
                return counts, first, first_has_more, final, final_has_more, owner_pages
            counts, first, first_more, last, last_more, owned = session.with_transaction(
                read,
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
        assert counts == {
            "total": 511, "active": 0, "planned": 511,
            "on_hold": 0, "done": 0, "cancelled": 0,
        }
        assert len(first) == 500 and first_more is True
        assert len(last) == 11 and last_more is False
        ids = {item.project_id for item in (*first, *last)}
        assert len(ids) == 511
        assert all(item.tenant_id == "scale-tenant-a" for item in (*first, *last))
        assert len(owned) == 256
        assert len({item.project_id for item in owned}) == 256
        assert all(item.tenant_id == "scale-tenant-a"
                   and item.owner_principal_id == "scale-principal" for item in owned)
        assert "prj-" + "f" * 48 not in {item.project_id for item in owned}
    finally:
        client.drop_database(database.name)
        client.close()


def test_real_replica_project_notes_replay_author_cas_and_tenant_isolation() -> None:
    """Proof that note collaboration persists independently of project lifecycle."""
    uri = os.environ.get("TEST_PROJECTS_ACCOUNTABILITY_MONGO_URI")
    if not uri:
        pytest.skip("Disposable MongoDB replica-set URI not configured")
    client: MongoClient[Any] = MongoClient(uri, serverSelectionTimeoutMS=4000)
    database = client.get_database("wilsy_project_notes_cert")
    try:
        client.admin.command("ping")
        client.drop_database(database.name)
        notes = database.get_collection("wilsy_project_notes")
        events = database.get_collection("wilsy_project_note_events")
        ProjectNoteRegistry.ensure_indexes(notes, events)
        registry = ProjectNoteRegistry(notes, events)
        tenant = "note-cert-tenant"
        project_id = "prj-" + "d" * 48
        actor = "note-author"
        key = "note-create-idempotency"
        identity = note_id_for_command(tenant, project_id, actor, key)
        instant = datetime.now(timezone.utc)
        original = ProjectNote(
            tenant_id=tenant, project_id=project_id, note_id=identity,
            author_principal_id=actor, body="Verified project discussion",
            created_at=instant, updated_at=instant,
        )

        def created(tx: Any) -> ProjectNote:
            return registry.create_or_replay(
                note=original, actor_principal_id=actor, idempotency_key=key,
                occurred_at=instant, session=tx,
            )

        with client.start_session() as session:
            recorded = session.with_transaction(
                created,
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
            replayed = session.with_transaction(
                created,
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
            assert replayed == recorded
            with pytest.raises(ProjectNoteNotFound):
                registry.get(
                    tenant_id="foreign-tenant", project_id=project_id,
                    note_id=identity, session=session,
                )
            first, first_more = registry.list_for_project(
                tenant_id=tenant, project_id=project_id, session=session,
            )
            assert len(first) == 1 and first_more is False

        with client.start_session() as session:
            with pytest.raises(ProjectNoteConflict, match="AUTHOR_DENIED"):
                session.with_transaction(
                    lambda tx: registry.revise_or_replay(
                        tenant_id=tenant, project_id=project_id, note_id=identity,
                        actor_principal_id="different-author",
                        expected_revision=1, body="Unauthorized",
                        idempotency_key="bad-editor", occurred_at=instant, session=tx,
                    ),
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
            updated = session.with_transaction(
                lambda tx: registry.revise_or_replay(
                    tenant_id=tenant, project_id=project_id, note_id=identity,
                    actor_principal_id=actor, expected_revision=1,
                    body="Revised discussion", idempotency_key="note-revision",
                    occurred_at=instant, session=tx,
                ),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
            assert updated.revision == 2
            with pytest.raises(ProjectNoteConflict, match="REVISION_CONFLICT"):
                session.with_transaction(
                    lambda tx: registry.revise_or_replay(
                        tenant_id=tenant, project_id=project_id, note_id=identity,
                        actor_principal_id=actor, expected_revision=1,
                        body="Stale revision", idempotency_key="stale-editor",
                        occurred_at=instant, session=tx,
                    ),
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
            history = registry.list_events(
                tenant_id=tenant, project_id=project_id,
                note_id=identity, session=session,
            )
            assert [event["event_type"] for event in history] == [
                "PROJECT_NOTE_CREATED", "PROJECT_NOTE_REVISED",
            ]
            assert events.count_documents({"tenant_id": tenant}) == 2

        sticky_key = "sticky-colour-create"
        sticky_id = note_id_for_command(tenant, project_id, actor, sticky_key)
        sticky = ProjectNote(
            tenant_id=tenant, project_id=project_id, note_id=sticky_id,
            author_principal_id=actor, body="Delivery coordination",
            colour="yellow", created_at=instant, updated_at=instant,
        )
        with client.start_session() as session:
            saved = session.with_transaction(
                lambda tx: registry.create_or_replay(
                    note=sticky, actor_principal_id=actor,
                    idempotency_key=sticky_key, occurred_at=instant, session=tx,
                ),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
            assert saved.colour == "yellow"
            recoloured = session.with_transaction(
                lambda tx: registry.revise_or_replay(
                    tenant_id=tenant, project_id=project_id, note_id=sticky_id,
                    actor_principal_id=actor, expected_revision=1,
                    body="Delivery coordination", colour="mint",
                    idempotency_key="sticky-mint", occurred_at=instant, session=tx,
                ),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
            assert recoloured.revision == 2
            assert recoloured.colour == "mint"
            assert recoloured.fingerprint != saved.fingerprint
            reread = registry.get(
                tenant_id=tenant, project_id=project_id,
                note_id=sticky_id, session=session,
            )
            assert reread == recoloured
            assert [row["event_type"] for row in registry.list_events(
                tenant_id=tenant, project_id=project_id,
                note_id=sticky_id, session=session,
            )] == ["PROJECT_NOTE_CREATED", "PROJECT_NOTE_REVISED"]
    finally:
        client.drop_database(database.name)
        client.close()


# ARTIFACT: test_project_accountability_real_mongo.py
# VERSION: v1.5.0-INDEXED-OWNER-PROJECT-REPLICA-CERT
# AUTHORITY BOUNDARY: Synthetic transaction and source-currentness evidence only.
# TENANT POSTURE: Disposable exact-tenant records; no outside persistence.
# FAIL-CLOSED POSTURE: Revoked owner and foreign-tenant reads deny.
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
