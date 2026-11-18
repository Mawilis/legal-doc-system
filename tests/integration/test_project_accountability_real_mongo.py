"""TITLE: WILSY OS Project Accountability Real Replica-Set Certificate
VERSION: v1.1.0-PROJECT-511-REPLICA-SCALE-CERT
AUTHORITY: Synthetic integration evidence for Python EOS project persistence.
EPITOME: Exercise principal membership/role currentness, tenant department
         immutable command evidence, project CAS, readback and revocation
         against an isolated disposable MongoDB replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_project_accountability_real_mongo.py
COLLABORATION / OWNERSHIP: Projects router, canonical tenant IAM repositories,
         ProjectRegistry and disposable CI replica set only.
CERTIFICATION / UPDATE DATE: 2026-11-17
CHANGELOG: v1.1.0-PROJECT-511-REPLICA-SCALE-CERT adds disposable real-replica certification for
         511 source-valid tenant projects, complete indexed page traversal,
         immutable tenant isolation and summary counts.
         v1.0.0-PROJECT-ACCOUNTABILITY-REPLICA-CERT establishes exact-tenant
         persistence proof without creating production records.
HISTORICAL CHANGELOG: v1.1.0-PROJECT-511-REPLICA-SCALE-CERT establishes exact-tenant
         persistence proof without creating a real principal, tenant, IAM grant,
         employee, subscription, activation or production record.
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
        instant = datetime.now(timezone.utc)
        rows = [
            Project(
                tenant_id="scale-tenant-a", project_id=f"prj-{number:048x}",
                name=f"Verified project {number}", code=f"SCALE-{number:04}",
                summary=None, status=ProjectStatus.PLANNED,
                owner_principal_id=None, department_id=None,
                start_date=None, target_date=None,
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
            summary=None, status=ProjectStatus.ACTIVE,
            owner_principal_id=None, department_id=None,
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
                return counts, first, first_has_more, final, final_has_more
            counts, first, first_more, last, last_more = session.with_transaction(
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
    finally:
        client.drop_database(database.name)
        client.close()


# ARTIFACT: test_project_accountability_real_mongo.py
# VERSION: v1.1.0-PROJECT-511-REPLICA-SCALE-CERT
# AUTHORITY BOUNDARY: Synthetic transaction and source-currentness evidence only.
# TENANT POSTURE: Disposable exact-tenant records; no outside persistence.
# FAIL-CLOSED POSTURE: Revoked owner and foreign-tenant reads deny.
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
