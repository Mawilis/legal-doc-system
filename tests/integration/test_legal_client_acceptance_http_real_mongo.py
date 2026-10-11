"""Authenticated real-Mongo HTTP certificate for Legal Client Acceptance.

VERSION: v1.0.0-LEGAL-CLIENT-ACCEPTANCE-HTTP-REAL-MONGO-CERT
AUTHORITY: Existing Legal Client Acceptance authorities only.
EPITOME: Certify HTTP -> durable IAM -> Mongo transaction -> canonical context
         -> immutable acceptance, replay, denial, revalidation and boundaries.
TENANT BOUNDARY: Identity plus explicit X-Tenant-ID; durable stores decide.
AUTHORITY BOUNDARY: No engagement, representation, Court or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""

from __future__ import annotations

import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient

from tests.integration.test_legal_client_acceptance_context_orchestrator_real_mongo import (
    INSTRUMENT_ID,
    MATTER_ID,
    NOW,
    PRINCIPAL,
    TENANT,
    _Repo,
    _collections,
    _ensure_indexes,
    _identity,
    _seed,
)
from tools.eos.api import legal_client_acceptance_router as http
from tools.eos.api import tenant_authorization_http as authorization_http
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth import authentication, tenant_access
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    COLLECTION as BUSINESS_ROLE_COLLECTION,
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.legal_operations.registry import (
    legal_client_acceptance_registry as acceptance_registry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)


class _RoleReader:
    def __init__(self, authorization: Any, business: Any) -> None:
        self.authorization = authorization
        self.business = business

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> Any:
        if role_id in TENANT_ROLES:
            try:
                value = TenantBusinessRoleRepository.resolve(
                    principal_id,
                    tenant_id,
                    self.business,
                    session=session,
                )
            except TenantBusinessRoleNotFoundError as error:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                ) from error
            except TenantBusinessRoleRepositoryError as error:
                raise RoleAssignmentRepositoryError(
                    "TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
                ) from error
            if value.business_role != role_id:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                )
            return value

        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self.authorization,
            session=session,
        )


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, dict[str, Any]]]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5_000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == "wilsyVendorCertRS"
        assert hello.get("isWritablePrimary") is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None

        database = client[
            f"wilsy_client_acceptance_http_{uuid4().hex}"
        ]
        collections = _collections(database)
        collections["business"] = database[BUSINESS_ROLE_COLLECTION]
        collections["acceptance"] = database[acceptance_registry.COLLECTION]

        _ensure_indexes(collections)
        TenantBusinessRoleRepository.ensure_indexes(collections["business"])
        acceptance_registry.LegalClientAcceptanceRegistry.ensure_indexes(
            collections["acceptance"]
        )

        yield client, database, collections
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _seed_http_authority(
    client: MongoClient[Any],
    collections: dict[str, Any],
) -> None:
    _seed(client, collections)

    with client.start_session() as session:
        with session.start_transaction():
            TenantBusinessRoleRepository.insert(
                TenantBusinessRoleAuthority(
                    PRINCIPAL,
                    TENANT,
                    "tenant_legal_client",
                    TenantBusinessRoleStatus.ACTIVE,
                    0,
                    NOW,
                    None,
                ),
                collections["business"],
                session=session,
            )


def _client(
    monkeypatch: pytest.MonkeyPatch,
    client: MongoClient[Any],
    database: Any,
    collections: dict[str, Any],
) -> TestClient:
    app = FastAPI()
    register_error_handlers(app, debug=False)

    app.dependency_overrides[
        authorization_http.get_current_identity
    ] = _identity
    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: _Repo(collections["principal"], "principal")
    app.dependency_overrides[
        tenant_access.get_tenant_membership_repository
    ] = lambda: _Repo(collections["membership"], "membership")
    app.dependency_overrides[
        authorization_http.get_role_assignment_repository
    ] = lambda: _RoleReader(
        collections["assignment"],
        collections["business"],
    )

    app.include_router(http.router, prefix="/api")
    monkeypatch.setattr(
        http,
        "_db_handles",
        lambda: (client, database),
    )

    return TestClient(app, raise_server_exceptions=False)


def _context_payload() -> dict[str, str]:
    return {
        "acceptance_context_id": "context-http-real",
        "replay_key": "replay-http-real",
        "instrument_id": INSTRUMENT_ID,
    }


def test_authenticated_http_context_acceptance_and_exact_replay(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mongo, database, collections = mongo_context
    _seed_http_authority(mongo, collections)

    client = _client(monkeypatch, mongo, database, collections)
    headers = {"X-Tenant-ID": TENANT}

    context_route = (
        f"/api/legal-operations/client/matters/{MATTER_ID}/"
        "acceptance-contexts"
    )
    context = client.post(
        context_route,
        json=_context_payload(),
        headers=headers,
    )
    assert context.status_code == 201, context.text
    assert collections["context"].count_documents(
        {"tenant_id": TENANT}
    ) == 1

    acceptance_route = (
        "/api/legal-operations/client/acceptance-contexts/"
        "context-http-real/acceptances"
    )
    acceptance_headers = {
        "X-Tenant-ID": TENANT,
        "Idempotency-Key": "acceptance-http-real",
    }

    first = client.post(
        acceptance_route,
        json={"confirmed": True},
        headers=acceptance_headers,
    )
    assert first.status_code == 201, first.text
    assert collections["acceptance"].count_documents(
        {"tenant_id": TENANT}
    ) == 1

    replay = client.post(
        acceptance_route,
        json={"confirmed": True},
        headers=acceptance_headers,
    )
    assert replay.status_code == 201, replay.text
    assert replay.json() == first.json()
    assert collections["acceptance"].count_documents({}) == 1

    assert not {
        "engagements",
        "representations",
        "court_authorities",
        "financial_approvals",
    } & set(database.list_collection_names())


def test_real_iam_cross_tenant_denies_before_context_write(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mongo, database, collections = mongo_context
    _seed_http_authority(mongo, collections)

    client = _client(monkeypatch, mongo, database, collections)

    response = client.post(
        f"/api/legal-operations/client/matters/{MATTER_ID}/acceptance-contexts",
        json=_context_payload(),
        headers={"X-Tenant-ID": "tenant-foreign"},
    )

    assert response.status_code == 403, response.text
    assert collections["context"].count_documents({}) == 0
    assert collections["acceptance"].count_documents({}) == 0


def test_http_acceptance_revalidates_current_visibility(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mongo, database, collections = mongo_context
    _seed_http_authority(mongo, collections)

    client = _client(monkeypatch, mongo, database, collections)
    headers = {"X-Tenant-ID": TENANT}

    created = client.post(
        f"/api/legal-operations/client/matters/{MATTER_ID}/acceptance-contexts",
        json=_context_payload(),
        headers=headers,
    )
    assert created.status_code == 201, created.text

    collections["visibility"].delete_many({})

    rejected = client.post(
        "/api/legal-operations/client/acceptance-contexts/"
        "context-http-real/acceptances",
        json={"confirmed": True},
        headers={
            "X-Tenant-ID": TENANT,
            "Idempotency-Key": "acceptance-after-drift",
        },
    )

    assert rejected.status_code == 404, rejected.text
    assert collections["acceptance"].count_documents({}) == 0


# ARTIFACT: test_legal_client_acceptance_http_real_mongo.py
# VERSION: v1.0.0-LEGAL-CLIENT-ACCEPTANCE-HTTP-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: authenticated HTTP and canonical acceptance only
# TENANT POSTURE: durable IAM plus explicit tenant scope
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
