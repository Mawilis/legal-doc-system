"""
TITLE: WILSY OS Workforce-Aware Tenant Authorization HTTP Real-Mongo Certificate
VERSION: v1.0.0-W3D-R8C-R4-REAL-MONGO-WORKFORCE-HTTP
AUTHORITY: Integration evidence for the production RequireTenantAuthorization seam.
EPITOME: Proves explicit workforce-required permissions consume current TENANT
         workforce truth in one Mongo transaction with current IAM while
         non-workforce permissions retain the sessionless path.
ABSOLUTE CANONICAL PATH:
    tests/integration/test_tenant_authorization_http_workforce_real_mongo.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-13.
CHANGELOG:
    v1.0.0-W3D-R8C-R4-REAL-MONGO-WORKFORCE-HTTP establishes the dedicated
    real-Mongo certificate for W3D conditional workforce admission.
SECURITY / PRIVACY POSTURE:
    Synthetic principals only. Real authentication is retained. UUID-isolated
    database only. No external tenant, customer, employee, credential or
    financial data is used.
TENANT BOUNDARY:
    Workforce currentness is exact TENANT scope plus exact principal binding.
    Cross-tenant workforce cannot satisfy the selected tenant.
AUTHORITY BOUNDARY:
    Workforce currentness is a prerequisite only when canonical permission
    metadata explicitly requires it. Workforce facts never grant permission,
    business role, authorization role, commercial entitlement or system power.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

import ast
import os
import threading
import uuid
from collections.abc import Iterator
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Any

os.environ.setdefault(
    "WILSY_JWT_SECRET",
    "W3D-R8C-R4-REAL-MONGO-CERT-ONLY-SECRET",
)

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient, monitoring
from pymongo.errors import PyMongoError

import tools.eos.api.tenant_authorization_http as http_subject
import tools.eos.kernel.db as kernel_db
import tools.eos.saas.auth.auth_registry as auth_registry_module
import tools.eos.saas.tenancy.tenant_registry as tenant_registry_module
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.auth.jwt_provider import (
    TokenPurpose,
    create_access_token,
)
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
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleRepository,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
)
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)
from tools.eos.workforce.registry.workforce_relationship_registry import (
    COLLECTION_NAME as WORKFORCE_COLLECTION,
    ensure_indexes as ensure_workforce_indexes,
    persist_revision,
)


VERSION = "v1.0.0-W3D-R8C-R4-REAL-MONGO-WORKFORCE-HTTP"

URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

TENANT = "tenant-r8c-r4"
OTHER_TENANT = "tenant-r8c-r4-other"
WORKFORCE_PRINCIPAL = "principal-r8c-r4-workforce"
CLIENT_PRINCIPAL = "principal-r8c-r4-client"

WORKFORCE_PERMISSION = "hr:employee_relation:write"
WORKFORCE_OPERATION = "hr_employee_relation_write"

NON_WORKFORCE_PERMISSION = "legal_operations:client_matter:read"
NON_WORKFORCE_OPERATION = "legal_client_matter_read"

NOW = datetime(2026, 10, 13, 7, 0, tzinfo=timezone.utc)


class MongoTrace(monitoring.CommandListener):
    """Capture transaction-scoped collection reads without changing authority."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.started_events: list[dict[str, Any]] = []

    def started(self, event: Any) -> None:  # type: ignore[override]
        command = event.command
        collection = command.get("find")

        if not isinstance(collection, str):
            return

        if command.get("autocommit") is not False:
            return

        with self._lock:
            self.started_events.append(
                {
                    "collection": collection,
                    "lsid": repr(command.get("lsid")),
                    "txn": repr(command.get("txnNumber")),
                }
            )

    def succeeded(self, event: Any) -> None:  # type: ignore[override]
        del event

    def failed(self, event: Any) -> None:  # type: ignore[override]
        del event

    def reset(self) -> None:
        with self._lock:
            self.started_events.clear()


class CountingClient:
    """Observe production HTTP session creation while delegating to PyMongo."""

    def __init__(
        self,
        client: MongoClient[Any],
    ) -> None:
        self.client = client
        self.start_session_calls = 0

    def start_session(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        self.start_session_calls += 1
        return self.client.start_session(
            *args,
            **kwargs,
        )

    def reset(self) -> None:
        self.start_session_calls = 0


class BrokenWorkforceCollection:
    """Bounded persistence failure used only for HTTP 503 translation evidence."""

    def find(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> Any:
        raise PyMongoError(
            "W3D_R8C_R4_SYNTHETIC_WORKFORCE_READ_FAILURE"
        )


class WorkforceFailureDatabase:
    """Expose one failing workforce collection without altering IAM persistence."""

    def __getitem__(
        self,
        name: str,
    ) -> Any:
        if name != WORKFORCE_COLLECTION:
            raise AssertionError(
                "HTTP workforce path requested unexpected collection"
            )

        return BrokenWorkforceCollection()


class Context:
    def __init__(
        self,
        *,
        mongo: MongoClient[Any],
        database: Any,
        trace: MongoTrace,
        counter: CountingClient,
    ) -> None:
        self.mongo = mongo
        self.database = database
        self.trace = trace
        self.counter = counter

        self.principals = database["principal_authorities"]
        self.memberships = database["tenant_memberships"]
        self.business_roles = database["tenant_business_roles"]
        self.roles = database["role_assignments"]
        self.workforce = database[WORKFORCE_COLLECTION]
        self.users = database["users"]


def _create_tenant(
    tenant_id: str,
) -> None:
    result = TenantRegistry.create(
        {
            "name": f"W3D R8C R4 Certificate {tenant_id}",
            "tenant_id": tenant_id,
        }
    )

    assert result.get("success") is True


def _seed_user(
    context: Context,
    *,
    principal_id: str,
    tenant_id: str,
) -> None:
    context.users.insert_one(
        {
            "user_id": principal_id,
            "email": f"{principal_id}@wilsyos.org",
            "firstName": "W3D",
            "lastName": "Certificate",
            "role": "USER",
            "permissions": [],
            "tenantId": tenant_id,
            "passwordHash": "bcrypt-test-only",
            "credential_revision": 0,
            "mfaRegistered": False,
            "hasSignedCovenant": False,
        }
    )


def _seed_iam(
    context: Context,
    *,
    principal_id: str,
    tenant_id: str,
    business_role: str,
    authorization_role: str,
) -> None:
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(
            principal_id,
            PrincipalStatus.ACTIVE,
            0,
        ),
        context.principals,
    )

    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal_id,
            tenant_id,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        context.memberships,
    )

    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal_id=principal_id,
            tenant_id=tenant_id,
            business_role=business_role,
            status=TenantBusinessRoleStatus.ACTIVE,
            revision=0,
            effective_at=NOW,
            revoked_at=None,
        ),
        context.business_roles,
    )

    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal_id,
            tenant_id,
            authorization_role,
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        context.roles,
    )


def _relationship(
    *,
    relationship_id: str = "relationship-r8c-r4",
    revision: int = 1,
    scope_id: str = TENANT,
    status: WorkforceRelationshipStatus,
    effective_from: datetime | None = None,
    effective_until: datetime | None = None,
    status_effective_at: datetime | None = None,
    supersedes_fingerprint: str | None = None,
) -> WorkforceRelationship:
    start = (
        effective_from
        if effective_from is not None
        else NOW - timedelta(days=30)
    )

    status_at = (
        status_effective_at
        if status_effective_at is not None
        else start
    )

    return WorkforceRelationship(
        relationship_id=relationship_id,
        revision=revision,
        scope_kind=WorkforceScopeKind.TENANT,
        scope_id=scope_id,
        principal_id=WORKFORCE_PRINCIPAL,
        relationship_type=WorkforceRelationshipType.EMPLOYEE,
        status=status,
        effective_from=start,
        effective_until=effective_until,
        status_effective_at=status_at,
        reason_reference="w3d-r8c-r4-real-mongo-cert",
        supersedes_fingerprint=supersedes_fingerprint,
    )


def _persist(
    context: Context,
    *relationships: WorkforceRelationship,
) -> None:
    with context.mongo.start_session() as session:
        with session.start_transaction():
            for relationship in relationships:
                persist_revision(
                    relationship,
                    collection=context.workforce,
                    session=session,
                )


def _token(
    principal_id: str,
    tenant_id: str,
) -> str:
    return create_access_token(
        {
            "identity_id": principal_id,
            "tenant_id": tenant_id,
            "roles": [],
            "permissions": [],
        },
        token_purpose=TokenPurpose.ACCESS,
        credential_revision=0,
    )


def _headers(
    principal_id: str,
    tenant_id: str,
) -> dict[str, str]:
    return {
        "Authorization": (
            "Bearer "
            + _token(
                principal_id,
                tenant_id,
            )
        ),
        "X-Tenant-ID": tenant_id,
    }


WORKFORCE_DEPENDENCY = RequireTenantAuthorization(
    WORKFORCE_PERMISSION,
    WORKFORCE_OPERATION,
)

NON_WORKFORCE_DEPENDENCY = RequireTenantAuthorization(
    NON_WORKFORCE_PERMISSION,
    NON_WORKFORCE_OPERATION,
)


def _build_app() -> FastAPI:
    app = FastAPI()
    register_error_handlers(
        app,
        debug=False,
    )

    @app.get("/cert/workforce")
    async def workforce_route(
        authority: TenantAuthorizationContext = Depends(
            WORKFORCE_DEPENDENCY
        ),
    ) -> dict[str, object]:
        return {
            "authorized": authority.decision.authorized,
            "reason": authority.decision.reason.value,
        }

    @app.get("/cert/non-workforce")
    async def non_workforce_route(
        authority: TenantAuthorizationContext = Depends(
            NON_WORKFORCE_DEPENDENCY
        ),
    ) -> dict[str, object]:
        return {
            "authorized": authority.decision.authorized,
            "reason": authority.decision.reason.value,
        }

    return app


@pytest.fixture()
def context(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Context]:
    trace = MongoTrace()

    mongo: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        retryWrites=True,
        event_listeners=[trace],
    )

    database = None

    try:
        hello = mongo.admin.command("hello")

        assert hello.get("setName") == "wilsyVendorCertRS"
        assert hello.get("isWritablePrimary") is True

        database = mongo[
            "w3d_r8c_r4_"
            + uuid.uuid4().hex
        ]

        context = Context(
            mongo=mongo,
            database=database,
            trace=trace,
            counter=CountingClient(mongo),
        )

        PrincipalAuthorityRepository.ensure_indexes(
            context.principals
        )
        TenantMembershipRepository.ensure_indexes(
            context.memberships
        )
        TenantBusinessRoleRepository.ensure_indexes(
            context.business_roles
        )
        RoleAssignmentRepository.ensure_indexes(
            context.roles
        )
        ensure_workforce_indexes(
            context.workforce
        )

        monkeypatch.setattr(
            kernel_db,
            "get_client",
            lambda: mongo,
        )
        monkeypatch.setattr(
            kernel_db,
            "get_database",
            lambda: database,
        )

        # tenant_authorization_http imported these callables directly.
        monkeypatch.setattr(
            http_subject,
            "get_client",
            lambda: context.counter,
        )
        monkeypatch.setattr(
            http_subject,
            "get_database",
            lambda: database,
        )

        # AuthRegistry imports the kernel module, so its durable revision read
        # stays real and lands in the same UUID-isolated database.
        monkeypatch.setattr(
            auth_registry_module.kernel_db,
            "get_database",
            lambda: database,
        )

        # TenantRegistry owns canonical tenant resolution via this collection.
        monkeypatch.setattr(
            tenant_registry_module,
            "tenants_collection",
            database["tenants"],
        )

        _create_tenant(TENANT)
        _create_tenant(OTHER_TENANT)

        _seed_user(
            context,
            principal_id=WORKFORCE_PRINCIPAL,
            tenant_id=TENANT,
        )
        _seed_user(
            context,
            principal_id=CLIENT_PRINCIPAL,
            tenant_id=TENANT,
        )

        _seed_iam(
            context,
            principal_id=WORKFORCE_PRINCIPAL,
            tenant_id=TENANT,
            business_role="tenant_hr_director",
            authorization_role="HR_DIRECTOR",
        )

        _seed_iam(
            context,
            principal_id=CLIENT_PRINCIPAL,
            tenant_id=TENANT,
            business_role="tenant_legal_client",
            authorization_role="LEGAL_CLIENT",
        )

        yield context

    finally:
        if database is not None:
            name = database.name
            mongo.drop_database(name)
            assert name not in mongo.list_database_names()

        mongo.close()


def _client() -> TestClient:
    return TestClient(
        _build_app(),
        raise_server_exceptions=False,
    )


def test_active_workforce_plus_current_iam_authorizes_real_http(
    context: Context,
) -> None:
    _persist(
        context,
        _relationship(
            status=WorkforceRelationshipStatus.ACTIVE,
        ),
    )

    context.counter.reset()

    response = _client().get(
        "/cert/workforce",
        headers=_headers(
            WORKFORCE_PRINCIPAL,
            TENANT,
        ),
    )

    assert response.status_code == 200
    assert response.json()["authorized"] is True
    assert context.counter.start_session_calls == 1


def test_absent_workforce_history_is_403_not_outage(
    context: Context,
) -> None:
    response = _client().get(
        "/cert/workforce",
        headers=_headers(
            WORKFORCE_PRINCIPAL,
            TENANT,
        ),
    )

    assert response.status_code == 403


def test_suspended_workforce_is_403(
    context: Context,
) -> None:
    _persist(
        context,
        _relationship(
            status=WorkforceRelationshipStatus.SUSPENDED,
        ),
    )

    response = _client().get(
        "/cert/workforce",
        headers=_headers(
            WORKFORCE_PRINCIPAL,
            TENANT,
        ),
    )

    assert response.status_code == 403


def test_ended_workforce_is_403(
    context: Context,
) -> None:
    _persist(
        context,
        _relationship(
            status=WorkforceRelationshipStatus.ENDED,
        ),
    )

    response = _client().get(
        "/cert/workforce",
        headers=_headers(
            WORKFORCE_PRINCIPAL,
            TENANT,
        ),
    )

    assert response.status_code == 403


def test_expired_active_relationship_is_403(
    context: Context,
) -> None:
    _persist(
        context,
        _relationship(
            status=WorkforceRelationshipStatus.ACTIVE,
            effective_from=NOW - timedelta(days=30),
            effective_until=NOW - timedelta(days=1),
            status_effective_at=NOW - timedelta(days=30),
        ),
    )

    response = _client().get(
        "/cert/workforce",
        headers=_headers(
            WORKFORCE_PRINCIPAL,
            TENANT,
        ),
    )

    assert response.status_code == 403


def test_future_suspension_does_not_apply_early(
    context: Context,
) -> None:
    active = _relationship(
        status=WorkforceRelationshipStatus.ACTIVE,
    )

    future_suspension = _relationship(
        revision=2,
        status=WorkforceRelationshipStatus.SUSPENDED,
        effective_from=active.effective_from,
        effective_until=None,
        status_effective_at=NOW + timedelta(days=2),
        supersedes_fingerprint=active.fingerprint,
    )

    _persist(
        context,
        active,
        future_suspension,
    )

    response = _client().get(
        "/cert/workforce",
        headers=_headers(
            WORKFORCE_PRINCIPAL,
            TENANT,
        ),
    )

    assert response.status_code == 200


def test_workforce_persistence_failure_maps_to_503(
    context: Context,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        http_subject,
        "get_database",
        lambda: WorkforceFailureDatabase(),
    )

    response = _client().get(
        "/cert/workforce",
        headers=_headers(
            WORKFORCE_PRINCIPAL,
            TENANT,
        ),
    )

    assert response.status_code == 503


def test_non_workforce_permission_opens_no_workforce_session(
    context: Context,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_client() -> object:
        raise AssertionError(
            "non-workforce permission opened Mongo workforce session"
        )

    def forbidden_database() -> object:
        raise AssertionError(
            "non-workforce permission requested workforce database"
        )

    monkeypatch.setattr(
        http_subject,
        "get_client",
        forbidden_client,
    )
    monkeypatch.setattr(
        http_subject,
        "get_database",
        forbidden_database,
    )

    response = _client().get(
        "/cert/non-workforce",
        headers=_headers(
            CLIENT_PRINCIPAL,
            TENANT,
        ),
    )

    assert response.status_code == 200
    assert response.json()["authorized"] is True


def test_cross_tenant_workforce_never_satisfies_selected_tenant(
    context: Context,
) -> None:
    _persist(
        context,
        _relationship(
            scope_id=OTHER_TENANT,
            status=WorkforceRelationshipStatus.ACTIVE,
        ),
    )

    response = _client().get(
        "/cert/workforce",
        headers=_headers(
            WORKFORCE_PRINCIPAL,
            TENANT,
        ),
    )

    assert response.status_code == 403


def test_real_transaction_uses_one_session_for_iam_and_workforce(
    context: Context,
) -> None:
    _persist(
        context,
        _relationship(
            status=WorkforceRelationshipStatus.ACTIVE,
        ),
    )

    context.trace.reset()
    context.counter.reset()

    response = _client().get(
        "/cert/workforce",
        headers=_headers(
            WORKFORCE_PRINCIPAL,
            TENANT,
        ),
    )

    assert response.status_code == 200
    assert context.counter.start_session_calls == 1

    transaction_reads = tuple(
        event
        for event in context.trace.started_events
        if event["collection"]
        in {
            "principal_authorities",
            "tenant_memberships",
            "tenant_business_roles",
            WORKFORCE_COLLECTION,
            "role_assignments",
        }
    )

    collections = {
        event["collection"]
        for event in transaction_reads
    }

    assert {
        "principal_authorities",
        "tenant_memberships",
        "tenant_business_roles",
        WORKFORCE_COLLECTION,
        "role_assignments",
    }.issubset(collections)

    session_ids = {
        event["lsid"]
        for event in transaction_reads
    }

    transaction_numbers = {
        event["txn"]
        for event in transaction_reads
    }

    assert len(session_ids) == 1
    assert len(transaction_numbers) == 1


def test_certificate_contains_no_authentication_bypass_or_financial_authority() -> None:
    """Prove the certificate does not install an auth bypass or money authority."""
    tree = ast.parse(
        Path(__file__).read_text(
            encoding="utf-8"
        )
    )

    imported_names: set[str] = set()
    dependency_override_mutations = 0
    suspicious_money_calls = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(alias.name)

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.name)

        elif isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
                ast.AugAssign,
                ast.Delete,
            ),
        ):
            targets: list[ast.AST] = []

            if isinstance(node, ast.Assign):
                targets.extend(node.targets)
            elif isinstance(node, ast.AnnAssign):
                targets.append(node.target)
            elif isinstance(node, ast.AugAssign):
                targets.append(node.target)
            else:
                targets.extend(node.targets)

            for target in targets:
                for part in ast.walk(target):
                    if (
                        isinstance(part, ast.Attribute)
                        and part.attr == "dependency_overrides"
                    ):
                        dependency_override_mutations += 1

                    if (
                        isinstance(part, ast.Subscript)
                        and isinstance(part.value, ast.Attribute)
                        and part.value.attr == "dependency_overrides"
                    ):
                        dependency_override_mutations += 1

        elif isinstance(node, ast.Call):
            function_name: str | None = None

            if isinstance(node.func, ast.Name):
                function_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                function_name = node.func.attr

            if function_name is not None:
                lowered = function_name.lower()

                if any(
                    marker in lowered
                    for marker in (
                        "payment",
                        "settlement",
                        "financial_execution",
                        "execute_payment",
                        "settle",
                    )
                ):
                    suspicious_money_calls += 1

    assert "verify_access_token" not in imported_names
    assert dependency_override_mutations == 0
    assert suspicious_money_calls == 0

    assert WORKFORCE_PERMISSION == "hr:employee_relation:write"
    assert WORKFORCE_OPERATION == "hr_employee_relation_write"
    assert (
        NON_WORKFORCE_PERMISSION
        == "legal_operations:client_matter:read"
    )
    assert NON_WORKFORCE_OPERATION == "legal_client_matter_read"


# ARTIFACT: test_tenant_authorization_http_workforce_real_mongo.py
# AUTHORITY BOUNDARY: certification evidence only; creates no runtime authority.
# TENANT POSTURE: exact tenant/principal workforce currentness and IAM isolation.
# FAIL-CLOSED POSTURE: missing, stale, cross-tenant or unavailable workforce denies.
# FINANCIAL AUTHORITY BOUNDARY: none; Kennel EOS remains exclusive.
