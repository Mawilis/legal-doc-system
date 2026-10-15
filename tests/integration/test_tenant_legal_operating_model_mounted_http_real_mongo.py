"""
WILSY OS mounted Tenant Legal Operating Model HTTP real-Mongo certificate.

TITLE: Mounted Tenant Legal Operating Model HTTP Real-Mongo / Real-IAM Certificate
VERSION: v1.0.0-CX26-R4-MOUNTED-HTTP-REAL-MONGO-REAL-IAM-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS certification.
EPITOME: Prove the canonical mounted /api/legal/operating-model HTTP boundary reaches
         real transactional Mongo persistence and real durable tenant IAM while
         overriding authentication projection and database location only.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: 2026-10-15 v1.0.0-CX26-R4-MOUNTED-HTTP-REAL-MONGO-REAL-IAM-CERT
           establishes mounted POST/GET, exact replay, divergent replay,
           stale CAS, tenant-scope denial, durable-IAM denial, transaction
           rollback, and tenant-isolation evidence against a writable replica set.
SECURITY / PRIVACY POSTURE: Synthetic authentication identity only; authorization
                            remains real durable IAM.
TENANT BOUNDARY: Explicit X-Tenant-ID must equal authenticated tenant and all
                 durable operating-model predicates remain tenant-first.
AUTHORITY BOUNDARY: Tenant Legal operating-model configuration only. This
                    certificate grants no role, permission, workflow, legal
                    execution, commercial, subscription, billing, or financial
                    authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution and settlement.
TRANSACTION BOUNDARY: Production router owns the real Mongo session, transaction,
                      commit, and abort lifecycle exercised here.
FAIL-CLOSED DECLARATION: Scope mismatch, IAM denial, stale revision, divergent
                         idempotency, transaction failure, and persistence
                         ambiguity reject without unauthorized durable mutation.
"""
from __future__ import annotations

from contextlib import contextmanager
import os
from typing import Any, Iterator
import uuid

from fastapi.routing import APIRoute, _iter_routes_with_context
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
import pytest

from tools.eos.api import server as server_api
from tools.eos.api import tenant_legal_operating_model_router as router_module
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
)
from tools.eos.legal_operations.registry import (
    tenant_legal_operating_model_registry as registry_module,
)


VERSION = "v1.0.0-CX26-R4-MOUNTED-HTTP-REAL-MONGO-REAL-IAM-CERT"

MONGO_URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
PATH = "/api/legal/operating-model"


class PrincipalReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        *,
        session: Any = None,
    ) -> object:
        return PrincipalAuthorityRepository.resolve(
            principal_id,
            collection=self.collection,
            session=session,
        )


class MembershipReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> object:
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            collection=self.collection,
            session=session,
        )


class RoleReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> object:
        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            collection=self.collection,
            session=session,
        )


def _identity(
    principal_id: str,
    tenant_id: str,
) -> SovereignIdentity:
    """Return authentication projection only; durable IAM remains authoritative."""
    return SovereignIdentity(
        identity_id=principal_id,
        tenant_id=tenant_id,
        username="tom-admin",
        email=None,
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _seed_identity(
    *,
    principal_id: str,
    tenant_id: str,
    principals: Any,
    memberships: Any,
    assignments: Any,
    business_role: str = "tenant_admin",
    authorization_role: str = "ENTERPRISE_ADMIN",
) -> None:
    """Seed exact durable IAM truth using sovereign repositories."""
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(
            principal_id,
            PrincipalStatus.ACTIVE,
            0,
        ),
        principals,
    )

    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal_id,
            tenant_id,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        memberships,
    )

    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal_id,
            tenant_id,
            business_role,
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        assignments,
    )

    if authorization_role != business_role:
        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                principal_id,
                tenant_id,
                authorization_role,
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            assignments,
        )


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Provide one writable UUID-isolated replica-set database."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        socketTimeoutMS=5000,
        retryWrites=True,
        tz_aware=True,
    )

    database: Any = None

    try:
        hello = client.admin.command("hello")

        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        ) is True
        assert hello.get(
            "logicalSessionTimeoutMinutes"
        ) is not None

        database = client[
            f"wilsy_cx26_r4_http_{uuid.uuid4().hex}"
        ]

        principals = database["principal_authorities"]
        memberships = database["tenant_memberships"]
        assignments = database["role_assignments"]

        models = database.get_collection(
            registry_module.COLLECTION_NAME,
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
            read_concern=ReadConcern("majority"),
        )

        PrincipalAuthorityRepository.ensure_indexes(
            principals
        )
        TenantMembershipRepository.ensure_indexes(
            memberships
        )
        RoleAssignmentRepository.ensure_indexes(
            assignments
        )

        registry_module.TenantLegalOperatingModelRegistry(
            models
        ).ensure_indexes()

        yield {
            "client": client,
            "database": database,
            "principals": principals,
            "memberships": memberships,
            "assignments": assignments,
            "models": models,
        }
    finally:
        if database is not None:
            name = database.name
            client.drop_database(name)
            assert name not in client.list_database_names()

        client.close()


def _assert_canonical_mount() -> None:
    """Prove this certificate uses the production-mounted route."""
    pairs: list[tuple[str, tuple[str, ...]]] = []

    for route, context in _iter_routes_with_context(
        server_api.app.routes
    ):
        if not isinstance(route, APIRoute):
            continue

        path = (
            context.path
            if context is not None
            else route.path
        )

        methods = (
            context.methods
            if context is not None
            else (route.methods or set())
        )

        if path == PATH:
            pairs.append(
                (
                    path,
                    tuple(sorted(methods)),
                )
            )

    assert sorted(pairs) == [
        (PATH, ("GET",)),
        (PATH, ("POST",)),
    ]


@contextmanager
def _mounted_client(
    monkeypatch: pytest.MonkeyPatch,
    context: dict[str, Any],
    *,
    principal_id: str,
    tenant_id: str,
) -> Iterator[TestClient]:
    """Bind only auth projection, real IAM readers, and the real Mongo locator."""
    _assert_canonical_mount()

    app = server_api.app
    original_overrides = dict(
        app.dependency_overrides
    )

    principals = context["principals"]
    memberships = context["memberships"]
    assignments = context["assignments"]

    principal_reader = PrincipalReader(
        principals
    )
    membership_reader = MembershipReader(
        memberships
    )
    role_reader = RoleReader(
        assignments
    )

    app.dependency_overrides[
        router_module.get_current_identity
    ] = lambda: _identity(
        principal_id,
        tenant_id,
    )

    app.dependency_overrides[
        router_module.get_principal_authority_repository
    ] = lambda: principal_reader

    app.dependency_overrides[
        router_module.get_tenant_membership_repository
    ] = lambda: membership_reader

    app.dependency_overrides[
        router_module.get_role_assignment_repository
    ] = lambda: role_reader

    app.dependency_overrides[
        router_module.get_authorization_role_repository
    ] = lambda: role_reader

    monkeypatch.setattr(
        router_module,
        "get_client",
        lambda: context["client"],
    )

    monkeypatch.setattr(
        router_module,
        "get_database",
        lambda: context["database"],
    )

    assert (
        router_module.configure_tenant_legal_operating_model
        not in app.dependency_overrides
    )
    assert (
        router_module.get_current_tenant_legal_operating_model
        not in app.dependency_overrides
    )

    try:
        yield TestClient(
            app,
            raise_server_exceptions=False,
        )
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(
            original_overrides
        )


def _post(
    client: TestClient,
    *,
    tenant_id: str,
    key: str,
    expected_revision: int | None,
    items: list[str],
):
    return client.post(
        PATH,
        headers={
            "X-Tenant-ID": tenant_id,
            "Idempotency-Key": key,
        },
        json={
            "expected_revision": expected_revision,
            "activated_item_ids": items,
        },
    )


def _rows(
    models: Any,
    tenant_id: str,
) -> list[dict[str, Any]]:
    return list(
        models.find(
            {"tenant_id": tenant_id},
            {"_id": 0},
        ).sort(
            [
                ("revision", 1),
                ("operating_model_id", 1),
            ]
        )
    )


def test_mounted_authorized_create_get_and_exact_replay(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prove mounted POST/GET and exact idempotent replay against real IAM/Mongo."""
    principal_id = f"principal-{uuid.uuid4().hex}"
    tenant_id = f"tenant-{uuid.uuid4().hex}"

    _seed_identity(
        principal_id=principal_id,
        tenant_id=tenant_id,
        principals=mongo_context["principals"],
        memberships=mongo_context["memberships"],
        assignments=mongo_context["assignments"],
    )

    with _mounted_client(
        monkeypatch,
        mongo_context,
        principal_id=principal_id,
        tenant_id=tenant_id,
    ) as client:
        first = _post(
            client,
            tenant_id=tenant_id,
            key="create-r1",
            expected_revision=None,
            items=[
                "PRACTICE_DISPUTES",
                "PERSONA_PARTNER",
            ],
        )

        assert first.status_code == 201, first.text

        first_body = first.json()

        assert first_body["tenant_id"] == tenant_id
        assert first_body["revision"] == 1
        assert first_body["activated_item_ids"] == [
            "PERSONA_PARTNER",
            "PRACTICE_DISPUTES",
        ]

        current = client.get(
            PATH,
            headers={
                "X-Tenant-ID": tenant_id,
            },
        )

        assert current.status_code == 200, current.text
        assert current.json() == first_body

        replay = _post(
            client,
            tenant_id=tenant_id,
            key="create-r1",
            expected_revision=None,
            items=[
                "PRACTICE_DISPUTES",
                "PERSONA_PARTNER",
            ],
        )

        assert replay.status_code == 201, replay.text
        assert replay.json() == first_body

    assert len(
        _rows(
            mongo_context["models"],
            tenant_id,
        )
    ) == 1


def test_mounted_divergent_same_key_is_409_and_zero_write(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Divergent same-key HTTP replay fails closed without durable mutation."""
    principal_id = f"principal-{uuid.uuid4().hex}"
    tenant_id = f"tenant-{uuid.uuid4().hex}"

    _seed_identity(
        principal_id=principal_id,
        tenant_id=tenant_id,
        principals=mongo_context["principals"],
        memberships=mongo_context["memberships"],
        assignments=mongo_context["assignments"],
    )

    with _mounted_client(
        monkeypatch,
        mongo_context,
        principal_id=principal_id,
        tenant_id=tenant_id,
    ) as client:
        first = _post(
            client,
            tenant_id=tenant_id,
            key="same-key",
            expected_revision=None,
            items=["PERSONA_PARTNER"],
        )

        assert first.status_code == 201, first.text

        before = _rows(
            mongo_context["models"],
            tenant_id,
        )

        divergent = _post(
            client,
            tenant_id=tenant_id,
            key="same-key",
            expected_revision=None,
            items=[
                "PERSONA_PARTNER",
                "PRACTICE_DISPUTES",
            ],
        )

        assert divergent.status_code == 409, divergent.text

    after = _rows(
        mongo_context["models"],
        tenant_id,
    )

    assert after == before
    assert len(after) == 1


def test_mounted_stale_expected_revision_is_409_and_zero_write(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stale mounted CAS cannot create a third immutable revision."""
    principal_id = f"principal-{uuid.uuid4().hex}"
    tenant_id = f"tenant-{uuid.uuid4().hex}"

    _seed_identity(
        principal_id=principal_id,
        tenant_id=tenant_id,
        principals=mongo_context["principals"],
        memberships=mongo_context["memberships"],
        assignments=mongo_context["assignments"],
    )

    with _mounted_client(
        monkeypatch,
        mongo_context,
        principal_id=principal_id,
        tenant_id=tenant_id,
    ) as client:
        first = _post(
            client,
            tenant_id=tenant_id,
            key="r1",
            expected_revision=None,
            items=["PERSONA_PARTNER"],
        )

        assert first.status_code == 201, first.text

        second = _post(
            client,
            tenant_id=tenant_id,
            key="r2",
            expected_revision=1,
            items=[
                "PERSONA_PARTNER",
                "RISK_CONFLICTS",
            ],
        )

        assert second.status_code == 201, second.text
        assert second.json()["revision"] == 2

        before = _rows(
            mongo_context["models"],
            tenant_id,
        )

        stale = _post(
            client,
            tenant_id=tenant_id,
            key="stale-r3",
            expected_revision=1,
            items=["PERSONA_PARTNER"],
        )

        assert stale.status_code == 409, stale.text

    after = _rows(
        mongo_context["models"],
        tenant_id,
    )

    assert after == before
    assert len(after) == 2


def test_mounted_foreign_tenant_scope_denied_before_write(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authenticated tenant projection cannot select another tenant."""
    principal_id = f"principal-{uuid.uuid4().hex}"
    tenant_id = f"tenant-{uuid.uuid4().hex}"
    foreign_tenant = f"foreign-{uuid.uuid4().hex}"

    _seed_identity(
        principal_id=principal_id,
        tenant_id=tenant_id,
        principals=mongo_context["principals"],
        memberships=mongo_context["memberships"],
        assignments=mongo_context["assignments"],
    )

    with _mounted_client(
        monkeypatch,
        mongo_context,
        principal_id=principal_id,
        tenant_id=tenant_id,
    ) as client:
        denied = _post(
            client,
            tenant_id=foreign_tenant,
            key="foreign",
            expected_revision=None,
            items=["PERSONA_PARTNER"],
        )

        assert denied.status_code == 403, denied.text

    assert (
        mongo_context["models"].count_documents({})
        == 0
    )


def test_mounted_real_iam_denial_precedes_operating_model_write(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Wrong durable business role is denied even with ENTERPRISE_ADMIN."""
    principal_id = f"principal-{uuid.uuid4().hex}"
    tenant_id = f"tenant-{uuid.uuid4().hex}"

    _seed_identity(
        principal_id=principal_id,
        tenant_id=tenant_id,
        principals=mongo_context["principals"],
        memberships=mongo_context["memberships"],
        assignments=mongo_context["assignments"],
        business_role="tenant_owner",
        authorization_role="ENTERPRISE_ADMIN",
    )

    with _mounted_client(
        monkeypatch,
        mongo_context,
        principal_id=principal_id,
        tenant_id=tenant_id,
    ) as client:
        denied = _post(
            client,
            tenant_id=tenant_id,
            key="iam-denied",
            expected_revision=None,
            items=["PERSONA_PARTNER"],
        )

        assert denied.status_code == 403, denied.text

    assert (
        mongo_context["models"].count_documents(
            {"tenant_id": tenant_id}
        )
        == 0
    )


def test_mounted_router_aborts_real_transaction_after_post_write_failure(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Router-owned transaction aborts if failure occurs after real service write."""
    principal_id = f"principal-{uuid.uuid4().hex}"
    tenant_id = f"tenant-{uuid.uuid4().hex}"

    _seed_identity(
        principal_id=principal_id,
        tenant_id=tenant_id,
        principals=mongo_context["principals"],
        memberships=mongo_context["memberships"],
        assignments=mongo_context["assignments"],
    )

    original = (
        router_module.configure_tenant_legal_operating_model
    )

    def fail_after_real_write(**kwargs: Any) -> Any:
        value = original(**kwargs)
        assert value.revision == 1
        raise RuntimeError(
            "CX26_R4_FORCED_POST_WRITE_ABORT"
        )

    monkeypatch.setattr(
        router_module,
        "configure_tenant_legal_operating_model",
        fail_after_real_write,
    )

    with _mounted_client(
        monkeypatch,
        mongo_context,
        principal_id=principal_id,
        tenant_id=tenant_id,
    ) as client:
        failed = _post(
            client,
            tenant_id=tenant_id,
            key="abort-r1",
            expected_revision=None,
            items=["PERSONA_PARTNER"],
        )

        assert failed.status_code == 503, failed.text

    assert (
        mongo_context["models"].count_documents(
            {"tenant_id": tenant_id}
        )
        == 0
    )


def test_mounted_two_tenants_keep_independent_current_truth(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mounted HTTP keeps two tenant histories and current reads independent."""
    principal_a = f"principal-a-{uuid.uuid4().hex}"
    principal_b = f"principal-b-{uuid.uuid4().hex}"
    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"

    for principal_id, tenant_id in (
        (principal_a, tenant_a),
        (principal_b, tenant_b),
    ):
        _seed_identity(
            principal_id=principal_id,
            tenant_id=tenant_id,
            principals=mongo_context["principals"],
            memberships=mongo_context["memberships"],
            assignments=mongo_context["assignments"],
        )

    with _mounted_client(
        monkeypatch,
        mongo_context,
        principal_id=principal_a,
        tenant_id=tenant_a,
    ) as client:
        response_a = _post(
            client,
            tenant_id=tenant_a,
            key="tenant-a-r1",
            expected_revision=None,
            items=["PERSONA_PARTNER"],
        )

        assert response_a.status_code == 201, response_a.text

        current_a = client.get(
            PATH,
            headers={"X-Tenant-ID": tenant_a},
        )

        assert current_a.status_code == 200, current_a.text
        assert current_a.json()["tenant_id"] == tenant_a

    with _mounted_client(
        monkeypatch,
        mongo_context,
        principal_id=principal_b,
        tenant_id=tenant_b,
    ) as client:
        response_b = _post(
            client,
            tenant_id=tenant_b,
            key="tenant-b-r1",
            expected_revision=None,
            items=["PRACTICE_DISPUTES"],
        )

        assert response_b.status_code == 201, response_b.text

        current_b = client.get(
            PATH,
            headers={"X-Tenant-ID": tenant_b},
        )

        assert current_b.status_code == 200, current_b.text
        assert current_b.json()["tenant_id"] == tenant_b

    assert (
        mongo_context["models"].count_documents(
            {"tenant_id": tenant_a}
        )
        == 1
    )
    assert (
        mongo_context["models"].count_documents(
            {"tenant_id": tenant_b}
        )
        == 1
    )


# ARTIFACT: test_tenant_legal_operating_model_mounted_http_real_mongo.py
# VERSION: v1.0.0-CX26-R4-MOUNTED-HTTP-REAL-MONGO-REAL-IAM-CERT
# AUTHORITY BOUNDARY: mounted transport + real durable IAM + real TOM persistence only
# TENANT POSTURE: authenticated and explicit tenant scopes correlate exactly
# FAIL-CLOSED POSTURE: denial, stale/divergent command, rollback, and isolation are certified
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
