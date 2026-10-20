"""WILSY P12C-R4H isolated HTTP-to-real-Mongo transaction certificate.

Reuses the certified disposable P9 provisioning replica-set fixture.
Exercises actual FastAPI request dispatch, API-owned Mongo transactions,
canonical access-evidence registry reads, and physical immutable binding
writes. IAM/lifecycle/conflict currentness are isolated by predecessor
fixture mocks and therefore are NOT certified end-to-end in this module.

No ambient Mongo URI, protected port, production database, real IAM
grant, financial execution, or matter-content permission.
"""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path
import runpy
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tools.eos.api import legal_practitioner_matter_binding_router as api
from tools.eos.api.errors import register_error_handlers
from tools.eos.legal_operations.registry import (
    legal_practitioner_matter_access_registry as access_registry,
    legal_practitioner_matter_binding_registry as binding_registry,
)

ROOT = Path(__file__).resolve().parents[2]
PRE = runpy.run_path(
    str(
        ROOT
        / "tests/integration/"
        "test_legal_practitioner_matter_binding_provisioning_real_mongo.py"
    )
)


@pytest.fixture(scope="module")
def isolated_mongo():
    """Reuse the predecessor's disposable localhost replica-set owner."""
    yield from PRE["isolated_mongo"].__wrapped__()


@pytest.fixture()
def collections(isolated_mongo):
    """Reuse UUID-scoped physical registry collections and cleanup."""
    yield from PRE["collections"].__wrapped__(isolated_mongo)


def test_http_grant_and_revoke_commit_immutable_mongo_history(
    monkeypatch, collections
):
    """HTTP commands commit two immutable physical binding snapshots."""
    kwargs, ctx, access, binding, mongo_client = PRE["prepare"](
        monkeypatch, collections
    )
    PRE["seed"](mongo_client, access, ctx["evidence"])

    assert binding.count_documents({}) == 0

    database = access.database

    class CanonicalDatabase:
        """Map candidate production collection names to fixture collections."""

        def get_collection(self, name):
            if name == api.ACCESS_EVIDENCE_COLLECTION:
                return access
            if name == api.BINDING_COLLECTION:
                return binding
            if name in (
                api.DISPOSITION_COLLECTION,
                api.LIFECYCLE_COLLECTION,
            ):
                return database.get_collection(name)
            raise AssertionError(("UNEXPECTED_COLLECTION", name))

    monkeypatch.setattr(api, "get_client", lambda: mongo_client)
    monkeypatch.setattr(
        api, "get_database", lambda: CanonicalDatabase()
    )
    monkeypatch.setattr(api, "get_by_id", access_registry.get_by_id)

    source_disposition = SimpleNamespace(
        tenant_id=kwargs["tenant_id"],
        case_matter_id=kwargs["case_matter_id"],
        fingerprint=ctx["evidence"].source_evidence_fingerprint,
        client_party_id=kwargs["client_party_id"],
        subject_identity_fingerprint=kwargs[
            "subject_identity_fingerprint"
        ],
    )

    def disposition_lookup(
        tenant_id, fingerprint, collection, *, session
    ):
        assert session.in_transaction is True
        assert tenant_id == kwargs["tenant_id"]
        assert fingerprint == source_disposition.fingerprint
        return source_disposition

    monkeypatch.setattr(
        api,
        "get_disposition_by_fingerprint",
        disposition_lookup,
    )

    class Clock:
        """Server-time seam pinned to predecessor's certified chronology."""

        current = PRE["POS"]["AT"]

        @classmethod
        def now(cls, tz):
            return cls.current

    monkeypatch.setattr(api, "datetime", Clock)

    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(api.router, prefix="/api")
    app.dependency_overrides[api._PROVISION] = lambda: SimpleNamespace(
        tenant_id=kwargs["tenant_id"],
        identity=SimpleNamespace(
            identity_id=kwargs["authenticated_principal_id"]
        ),
    )

    dependencies = {
        api.get_principal_authority_repository: kwargs[
            "principal_repository"
        ],
        api.get_tenant_membership_repository: kwargs[
            "membership_repository"
        ],
        api.get_role_assignment_repository: kwargs[
            "business_role_repository"
        ],
        api.get_authorization_role_repository: kwargs[
            "role_assignment_repository"
        ],
    }
    for factory, repository in dependencies.items():
        app.dependency_overrides[factory] = (
            lambda value=repository: value
        )

    root = "/api/legal-operations/practitioner-bindings"
    client = TestClient(app, raise_server_exceptions=True)

    grant = client.post(
        root,
        json={
            "case_matter_id": kwargs["case_matter_id"],
            "practitioner_principal_id": kwargs[
                "practitioner_principal_id"
            ],
            "binding_id": kwargs["binding_id"],
            "access_evidence_id": kwargs["access_evidence_id"],
            "expected_access_evidence_fingerprint": kwargs[
                "expected_access_evidence_fingerprint"
            ],
        },
    )

    assert grant.status_code == 201, grant.text
    assert grant.json()["status"] == "ACTIVE"
    assert binding.count_documents({}) == 1

    Clock.current = PRE["POS"]["AT"] + timedelta(hours=1)

    revoke = client.post(
        root + "/revocations",
        json={
            "binding_id": kwargs["binding_id"],
            "evidence_reference": "revocation-evidence-1",
        },
    )

    assert revoke.status_code == 201, revoke.text
    assert revoke.json()["status"] == "REVOKED"
    assert binding.count_documents({}) == 2

    with mongo_client.start_session() as session:
        with session.start_transaction():
            history = binding_registry.read_binding_history(
                tenant_id=kwargs["tenant_id"],
                binding_id=kwargs["binding_id"],
                collection=binding,
                session=session,
            )

    assert len(history) == 2
    assert [item.status.value for item in history] == [
        "ACTIVE",
        "REVOKED",
    ]

    app.dependency_overrides.clear()



@pytest.mark.parametrize(
    "seed_evidence,expected_status",
    [(False, 403), (True, 503)],
)
def test_physical_http_missing_authority_denied(
    monkeypatch, collections, seed_evidence, expected_status
):
    """Reject absent policy or conflict disposition before any binding write."""
    kwargs, ctx, access, binding, mongo_client = PRE["prepare"](
        monkeypatch, collections
    )

    if seed_evidence:
        PRE["seed"](mongo_client, access, ctx["evidence"])

    class Database:
        def get_collection(self, name):
            if name == api.ACCESS_EVIDENCE_COLLECTION:
                return access
            if name == api.BINDING_COLLECTION:
                return binding
            return access.database.get_collection(name)

    monkeypatch.setattr(api, "get_client", lambda: mongo_client)
    monkeypatch.setattr(api, "get_database", lambda: Database())
    monkeypatch.setattr(api, "get_by_id", access_registry.get_by_id)

    from tools.eos.legal_operations.registry.legal_client_matter_conflict_disposition_registry import (
        get_disposition_by_fingerprint,
    )
    monkeypatch.setattr(
        api,
        "get_disposition_by_fingerprint",
        get_disposition_by_fingerprint,
    )

    def forbidden_grant(**kwargs):
        pytest.fail("MISSING_AUTHORITY_REACHED_BINDING_WRITE")

    monkeypatch.setattr(api, "grant_binding", forbidden_grant)

    application = FastAPI()
    register_error_handlers(application, debug=False)
    application.include_router(api.router, prefix="/api")
    application.dependency_overrides[api._PROVISION] = (
        lambda: SimpleNamespace(
            tenant_id=kwargs["tenant_id"],
            identity=SimpleNamespace(
                identity_id=kwargs["authenticated_principal_id"]
            ),
        )
    )

    client = TestClient(application, raise_server_exceptions=True)
    response = client.post(
        "/api/legal-operations/practitioner-bindings",
        json={
            "case_matter_id": kwargs["case_matter_id"],
            "practitioner_principal_id": kwargs[
                "practitioner_principal_id"
            ],
            "binding_id": kwargs["binding_id"],
            "access_evidence_id": kwargs["access_evidence_id"],
            "expected_access_evidence_fingerprint": kwargs[
                "expected_access_evidence_fingerprint"
            ],
        },
    )

    assert response.status_code == expected_status, response.text
    assert binding.count_documents({}) == 0
    application.dependency_overrides.clear()



def test_physical_three_registry_index_sets(
    collections, isolated_mongo
):
    """Install and inspect canonical indexes on an isolated replica set."""
    from tools.eos.legal_operations.registry import (
        legal_client_matter_conflict_disposition_registry as disposition_registry,
    )

    access, binding, client = collections
    db = access.database
    disposition = db.get_collection(disposition_registry.COLLECTION)

    assert client.admin.command("hello")["isWritablePrimary"] is True

    installers = (
        (access_registry, access),
        (binding_registry, binding),
        (disposition_registry, disposition),
    )

    for registry, collection in installers:
        registry.ensure_indexes(collection)
        registry.ensure_indexes(collection)

        indexes = {
            item["name"]: item
            for item in collection.list_indexes()
        }

        assert "_id_" in indexes
        assert len(indexes) >= 3
        assert any(
            item.get("unique") is True
            for name, item in indexes.items()
            if name != "_id_"
        )
        assert all(
            "expireAfterSeconds" not in item
            for item in indexes.values()
        )

    assert disposition.name == (
        "legal_client_matter_conflict_dispositions"
    )
    assert disposition_registry.FINGERPRINT_INDEX_NAME in {
        item["name"] for item in disposition.list_indexes()
    }
    assert binding_registry.COLLECTION_NAME == (
        "legal_practitioner_matter_bindings"
    )
    assert api.ACCESS_EVIDENCE_COLLECTION == (
        "legal_practitioner_matter_access_evidence"
    )


# ARTIFACT: test_legal_practitioner_matter_binding_http_real_mongo.py
# VERSION: v1.2.0-P12C-R4K-PHYSICAL-INDEX-READINESS
# AUTHORITY BOUNDARY: isolated HTTP/persistence certificate only
# TENANT POSTURE: exact tenant-scoped registry reads and writes
# FAIL-CLOSED POSTURE: no successful response without committed snapshot
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
