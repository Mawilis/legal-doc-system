"""TITLE: WILSY OS Productive-Work Read Authority Real-Mongo Certificate.
VERSION: v1.0.0-PW-P11A-PRODUCTIVE-WORK-READ-REAL-MONGO-CERT
AUTHORITY: Evidence-only certification of persisted productive-work read IAM.
EPITOME: Proves the frozen productive-work read authorization conjunction
against isolated, durable principal, membership and role-assignment truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_productive_work_read_authority_real_mongo.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-16
CHANGELOG:
    2026-10-16 v1.0.0-PW-P11A-PRODUCTIVE-WORK-READ-REAL-MONGO-CERT proves
    the four exact allowed business/grant role pairs, same-tenant isolation,
    revoked membership denial and no persistence mutation during decisions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Generated identifiers and a disposable loopback
database only; no credentials, production data or PII are emitted.
TENANT BOUNDARY: Authorization requires ACTIVE membership in the exact tenant.
AUTHORITY BOUNDARY: Certifies IAM composition only; no HTTP, record scope,
workflow mutation, assignment, supervision or legal-act authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution truth.
"""
from __future__ import annotations

import hashlib
import json
import os
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from pymongo import MongoClient
from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository


VERSION = "v1.0.0-PW-P11A-PRODUCTIVE-WORK-READ-REAL-MONGO-CERT"
PERMISSION = "legal_operations:productive_work:read"
OPERATION = "legal_productive_work_read"
ROLE_PAIRS = (
    ("tenant_legal_partner", "LEGAL_PARTNER"),
    ("tenant_legal_attorney", "LEGAL_ATTORNEY"),
    ("tenant_legal_paralegal", "LEGAL_PARALEGAL"),
    ("tenant_legal_secretary", "LEGAL_SECRETARY"),
)


class _PrincipalReader:
    def __init__(self, collection: Collection) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        *,
        session: ClientSession | None = None,
    ) -> PrincipalAuthority:
        return PrincipalAuthorityRepository.resolve(
            principal_id, collection=self.collection, session=session
        )


class _MembershipReader:
    def __init__(self, collection: Collection) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: ClientSession | None = None,
    ) -> TenantMembershipAuthority:
        return TenantMembershipRepository.resolve(
            principal_id, tenant_id, collection=self.collection, session=session
        )


class _RoleReader:
    def __init__(self, collection: Collection) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: ClientSession | None = None,
    ) -> RoleAssignmentAuthority:
        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            collection=self.collection,
            session=session,
        )


def _digest(collection: Collection) -> str:
    rows = [{key: value for key, value in row.items() if key != "_id"} for row in collection.find({})]
    rows.sort(key=lambda row: json.dumps(row, sort_keys=True, default=str))
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha3_512(payload.encode("utf-8")).hexdigest()


def _authorize(
    principals: Collection,
    memberships: Collection,
    assignments: Collection,
    principal_id: str,
    tenant_id: str,
) -> TenantAuthorizationDecision:
    return authorize_tenant_operation(
        principal_id=principal_id,
        tenant_id=tenant_id,
        permission_id=PERMISSION,
        operation=OPERATION,
        principal_repository=_PrincipalReader(principals),
        membership_repository=_MembershipReader(memberships),
        business_role_repository=_RoleReader(assignments),
        role_assignment_repository=_RoleReader(assignments),
    )


def test_productive_work_read_authority_persisted_conjunction() -> None:
    """Prove all allowed pairs, tenant isolation, revocation and read-only behavior."""
    uri = os.environ["PW_P11A_MONGO_URI"]
    expected_set = parse_qs(urlparse(uri).query).get("replicaSet", [None])[0]
    assert expected_set
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    database_name = f"pw_p11a_authority_cert_{uuid4().hex}"
    database = client[database_name]
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == expected_set
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        principals = database["principal_authorities"]
        memberships = database["tenant_memberships"]
        assignments = database["role_assignments"]
        PrincipalAuthorityRepository.ensure_indexes(principals)
        TenantMembershipRepository.ensure_indexes(memberships)
        RoleAssignmentRepository.ensure_indexes(assignments)

        tenant_id = f"tenant-{uuid4().hex}"
        for business_role, grant_role in ROLE_PAIRS:
            principal_id = f"principal-{uuid4().hex}"
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0), principals
            )
            TenantMembershipRepository.insert(
                TenantMembershipAuthority(
                    principal_id, tenant_id, TenantMembershipStatus.ACTIVE, 0
                ),
                memberships,
            )
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(
                    principal_id, tenant_id, business_role, RoleAssignmentStatus.ACTIVE, 0
                ),
                assignments,
            )
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(
                    principal_id, tenant_id, grant_role, RoleAssignmentStatus.ACTIVE, 0
                ),
                assignments,
            )
            before = tuple(_digest(item) for item in (principals, memberships, assignments))
            decision = _authorize(
                principals, memberships, assignments, principal_id, tenant_id
            )
            assert decision.authorized is True
            assert decision.reason is TenantAuthorizationReason.AUTHORIZED
            assert decision.business_role == business_role
            assert decision.authorization_role == grant_role
            assert before == tuple(
                _digest(item) for item in (principals, memberships, assignments)
            )
            assert _authorize(
                principals, memberships, assignments, principal_id, "other-tenant"
            ).reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND

        revoked_principal = f"principal-{uuid4().hex}"
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(revoked_principal, PrincipalStatus.ACTIVE, 0), principals
        )
        TenantMembershipRepository.insert(
            TenantMembershipAuthority(
                revoked_principal, tenant_id, TenantMembershipStatus.REVOKED, 0
            ),
            memberships,
        )
        assert _authorize(
            principals, memberships, assignments, revoked_principal, tenant_id
        ).reason is TenantAuthorizationReason.MEMBERSHIP_INACTIVE
    finally:
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()


# ARTIFACT: test_legal_productive_work_read_authority_real_mongo.py
# VERSION: v1.0.0-PW-P11A-PRODUCTIVE-WORK-READ-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: persisted IAM composition evidence only; no HTTP or domain record authority
# TENANT POSTURE: exact ACTIVE same-tenant membership is mandatory and cross-tenant absence discloses nothing
# FAIL-CLOSED POSTURE: missing, inactive, mismatched and unavailable authority denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
