"""
TITLE: WILSY OS Productive-Work Authenticated HTTP Real-Mongo Certificate
VERSION: v1.0.0-PW-P11B-AUTHENTICATED-PRODUCTIVE-WORK-HTTP-REAL-MONGO-CERT
AUTHORITY: Durable IAM -> authenticated HTTP -> snapshot transaction ->
           durable productive-work read proof only.
TENANT BOUNDARY: Tenant/principal are derived from authenticated authorization
                 context and remain exact through all durable reads.
FINANCIAL AUTHORITY BOUNDARY: NONE. Kennel EOS remains exclusive.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import os
import uuid
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.client_session import ClientSession

import tools.eos.api.legal_operations_router as legal_router
import tools.eos.api.tenant_authorization_http as authorization_http
import tools.eos.auth.authentication as authentication
import tools.eos.auth.tenant_access as tenant_access

from tools.eos.api.errors import register_error_handlers
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
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
)
from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_item import LegalWorkItem
from tools.eos.legal_operations.registry.legal_operating_role_capability_binding_registry import (
    LegalOperatingRoleCapabilityBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_operating_role_definition_registry import (
    LegalOperatingRoleDefinitionRegistry,
)
from tools.eos.legal_operations.registry.legal_operating_role_scope_binding_registry import (
    LegalOperatingRoleScopeBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_principal_operating_role_binding_registry import (
    LegalPrincipalOperatingRoleBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_work_assignment_registry import (
    LegalWorkAssignmentRegistry,
)
from tools.eos.legal_operations.registry.legal_work_item_registry import (
    LegalWorkItemRegistry,
)
from tools.eos.legal_operations.registry.legal_work_supervision_binding_registry import (
    LegalWorkSupervisionBindingRegistry,
)


URI = os.environ[
    "WILSY_PW_HTTP_REAL_MONGO_URI"
]

NOW = datetime(
    2026,
    10,
    16,
    1,
    0,
    tzinfo=UTC,
)


class _PrincipalReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        *,
        session: ClientSession | None = None,
    ) -> Any:
        return PrincipalAuthorityRepository.get(
            principal_id,
            self.collection,
            session=session,
        )


class _MembershipReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: ClientSession | None = None,
    ) -> Any:
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            self.collection,
            session=session,
        )


class _RoleReader:
    def __init__(
        self,
        role_collection: Any,
        business_collection: Any,
    ) -> None:
        self.role_collection = role_collection
        self.business_collection = business_collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: ClientSession | None = None,
    ) -> Any:
        if role_id in TENANT_ROLES:
            try:
                value = TenantBusinessRoleRepository.resolve(
                    principal_id,
                    tenant_id,
                    self.business_collection,
                    session=session,
                )
            except TenantBusinessRoleNotFoundError as error:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
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
            self.role_collection,
            session=session,
        )


def _collections(database: Any) -> dict[str, Any]:
    return {
        "principal": database["principal_authorities"],
        "membership": database["tenant_memberships"],
        "business": database["tenant_business_roles"],
        "role": database["role_assignments"],
        "work": database["legal_work_items"],
        "assignment": database["legal_work_assignments"],
        "supervision": database[
            "legal_work_supervision_bindings"
        ],
        "operating_role": database[
            "legal_operating_role_definitions"
        ],
        "capability": database[
            "legal_operating_role_capability_bindings"
        ],
        "scope": database[
            "legal_operating_role_scope_bindings"
        ],
        "occupancy": database[
            "legal_principal_operating_role_bindings"
        ],
    }


def _ensure_indexes(values: dict[str, Any]) -> None:
    PrincipalAuthorityRepository.ensure_indexes(
        values["principal"]
    )
    TenantMembershipRepository.ensure_indexes(
        values["membership"]
    )
    TenantBusinessRoleRepository.ensure_indexes(
        values["business"]
    )
    RoleAssignmentRepository.ensure_indexes(
        values["role"]
    )
    LegalWorkItemRegistry(
        values["work"]
    ).ensure_indexes()
    LegalWorkAssignmentRegistry(
        values["assignment"]
    ).ensure_indexes()
    LegalWorkSupervisionBindingRegistry(
        values["supervision"]
    ).ensure_indexes()
    LegalOperatingRoleDefinitionRegistry(
        values["operating_role"]
    ).ensure_indexes()
    LegalOperatingRoleCapabilityBindingRegistry(
        values["capability"]
    ).ensure_indexes()
    LegalOperatingRoleScopeBindingRegistry(
        values["scope"]
    ).ensure_indexes()
    LegalPrincipalOperatingRoleBindingRegistry(
        values["occupancy"]
    ).ensure_indexes()


def _identity(
    principal: str,
    tenant: str,
) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=principal,
        tenant_id=tenant,
        username=principal,
        email=f"{principal}@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _seed_iam(
    values: dict[str, Any],
    principal: str,
    tenant: str,
) -> None:
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(
            principal,
            PrincipalStatus.ACTIVE,
            0,
        ),
        values["principal"],
    )

    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal,
            tenant,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        values["membership"],
    )

    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal,
            tenant,
            "tenant_legal_attorney",
            TenantBusinessRoleStatus.ACTIVE,
            0,
            NOW,
            None,
        ),
        values["business"],
    )

    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal,
            tenant,
            "LEGAL_ATTORNEY",
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        values["role"],
    )


def _seed_work(
    client: MongoClient[Any],
    values: dict[str, Any],
    principal: str,
    tenant: str,
) -> None:
    work = LegalWorkItem(
        work_item_id="work-http-1",
        tenant_id=tenant,
        case_matter_id="matter-http-1",
        title="Prepare governed filing",
        source_kind="LEGAL_WORKFLOW_STAGE",
        source_reference="stage:http-1",
        source_evidence_fingerprint="a" * 128,
        status="OPEN",
        created_at=NOW,
        due_at=NOW + timedelta(hours=8),
        completion_evidence_reference=None,
        completion_evidence_fingerprint=None,
        completed_at=None,
        cancellation_reason_reference=None,
        cancelled_at=None,
    )

    assignment = LegalWorkAssignment(
        assignment_id="assignment-http-1",
        tenant_id=tenant,
        case_matter_id="matter-http-1",
        work_item_id="work-http-1",
        assignee_principal_id=principal,
        assigned_by_principal_id="principal-assigner",
        assigned_at=NOW,
        assignment_reason_reference="reason:daily-work",
        authorization_evidence_reference="authz:daily-work",
        supersedes_assignment_id=None,
    )

    with client.start_session() as session:
        with session.start_transaction():
            LegalWorkItemRegistry(
                values["work"]
            ).create_or_replay(
                work,
                session=session,
            )

            LegalWorkAssignmentRegistry(
                values["assignment"]
            ).persist(
                assignment,
                session=session,
            )


def _app(
    client: MongoClient[Any],
    database: Any,
    values: dict[str, Any],
    principal: str,
    tenant: str,
) -> FastAPI:
    app = FastAPI()
    register_error_handlers(
        app,
        debug=False,
    )

    app.dependency_overrides[
        authorization_http.get_current_identity
    ] = lambda: _identity(
        principal,
        tenant,
    )

    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: _PrincipalReader(
        values["principal"]
    )

    app.dependency_overrides[
        tenant_access.get_tenant_membership_repository
    ] = lambda: _MembershipReader(
        values["membership"]
    )

    app.dependency_overrides[
        authorization_http.get_role_assignment_repository
    ] = lambda: _RoleReader(
        values["role"],
        values["business"],
    )

    legal_router._db_handles = lambda: (
        client,
        database,
    )

    app.include_router(
        legal_router.router,
        prefix="/api",
    )

    return app


def test_real_mongo_authenticated_productive_work_http() -> None:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )

    tenant = (
        "tenant-pw-http-"
        + uuid.uuid4().hex
    )

    principal = (
        "principal-pw-http-"
        + uuid.uuid4().hex
    )

    database = client[
        "wilsy_pw_http_"
        + uuid.uuid4().hex
    ]

    try:
        hello = client.admin.command(
            "hello"
        )

        assert hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        ) is True

        assert hello.get(
            "logicalSessionTimeoutMinutes"
        ) is not None

        values = _collections(
            database
        )

        _ensure_indexes(
            values
        )

        _seed_iam(
            values,
            principal,
            tenant,
        )

        _seed_work(
            client,
            values,
            principal,
            tenant,
        )

        with TestClient(
            _app(
                client,
                database,
                values,
                principal,
                tenant,
            )
        ) as api:
            response = api.get(
                "/api/legal-operations/productive-work",
                headers={
                    "X-Tenant-ID": tenant,
                },
            )

        assert response.status_code == 200

        body = response.json()

        assert body["tenant_id"] == tenant
        assert body["principal_id"] == principal

        assert [
            value["work_item_id"]
            for value in body[
                "assigned_work_items"
            ]
        ] == [
            "work-http-1"
        ]

        assert body[
            "supervised_work_items"
        ] == []

        assert body[
            "operating_contexts"
        ] == []

        serialized = response.text.casefold()

        for forbidden in (
            "principal-assigner",
            "authz:daily-work",
            "reason:daily-work",
            "payment",
            "settlement",
            "revenue",
            "sheriff_operational_queue",
            "deputy_personal_active_work",
        ):
            assert forbidden not in serialized

        assert (
            values["work"].count_documents({})
            == 1
        )

        assert (
            values["assignment"].count_documents({})
            == 1
        )

        assert (
            values["supervision"].count_documents({})
            == 0
        )

    finally:
        client.drop_database(
            database.name
        )
        client.close()


# ARTIFACT: test_legal_productive_work_http_real_mongo.py
# VERSION: v1.0.0-PW-P11B-AUTHENTICATED-PRODUCTIVE-WORK-HTTP-REAL-MONGO-CERT
# AUTHORITY: own-principal authenticated durable productive-work read only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
