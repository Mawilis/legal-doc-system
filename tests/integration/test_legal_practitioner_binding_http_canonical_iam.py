"""WILSY P12C-R4M-P3B canonical practitioner HTTP IAM certificate.

VERSION: v1.0.0-P12C-R4M-P3B-REAL-IAM-HTTP
Uses the unmodified canonical authorization composer and actual HTTP
dependency. Authentication identity and repository state are controlled
fixtures, not claims of a live signed-in principal or durable IAM stores.
Downstream transaction is isolated. No database or startup execution.
"""

from __future__ import annotations

from pathlib import Path
import runpy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tools.eos.api import tenant_authorization_http as iam
from tools.eos.api import legal_practitioner_matter_binding_router as api
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_authorization import TenantAuthorizationReason

ROOT = Path(__file__).resolve().parents[2]
PRE = runpy.run_path(
    str(
        ROOT / "tests/unit/"
        "test_legal_practitioner_matter_binding_provision_current_iam.py"
    )
)

ROOT_PATH = "/api/legal-operations/practitioner-bindings"
COMMANDS = (
    (
        ROOT_PATH,
        {
            "case_matter_id": "matter-A",
            "practitioner_principal_id": "lawyer-A",
            "binding_id": "binding-A",
            "access_evidence_id": "evidence-A",
            "expected_access_evidence_fingerprint": "a" * 128,
        },
    ),
    (
        ROOT_PATH + "/revocations",
        {
            "binding_id": "binding-A",
            "evidence_reference": "revocation-A",
        },
    ),
)


class CombinedRoleReader:
    """Use separately owned business and authorization role readers."""

    def __init__(self, business, authorization):
        self.business = business
        self.authorization = authorization

    def resolve(self, principal_id, tenant_id, role_id, *, session=None):
        if role_id == "LEGAL_PARTNER":
            return self.authorization.resolve(
                principal_id, tenant_id, role_id, session=session
            )
        return self.business.resolve(
            principal_id, tenant_id, role_id, session=session
        )


def inactive(enum):
    return next(value for value in enum if value is not enum.ACTIVE)


@pytest.mark.parametrize("endpoint,payload", COMMANDS)
@pytest.mark.parametrize(
    "scenario,expected_status",
    [
        ("eligible", 201),
        ("principal_inactive", 403),
        ("membership_inactive", 403),
        ("foreign_tenant", 403),
        ("wrong_business_role", 403),
        ("missing_permission_grant", 403),
        ("principal_unavailable", 503),
    ],
)
def test_http_canonical_partner_iam(
    monkeypatch, endpoint, payload, scenario, expected_status
):
    """Only the real IAM decision can admit a command transaction."""
    assert api._PROVISION.permission_id == PRE["PERM"]
    assert api._PROVISION.operation == PRE["OP"]
    assert iam.authorize_tenant_operation is not None

    principal = PRE["PrincipalReader"](
        status=(
            inactive(PrincipalStatus)
            if scenario == "principal_inactive"
            else PrincipalStatus.ACTIVE
        ),
        unavailable=scenario == "principal_unavailable",
    )
    membership = PRE["MembershipReader"](
        status=(
            inactive(TenantMembershipStatus)
            if scenario == "membership_inactive"
            else TenantMembershipStatus.ACTIVE
        )
    )
    business = PRE["BusinessRoles"](
        roles=(
            ("tenant_legal_attorney",)
            if scenario == "wrong_business_role"
            else ("tenant_legal_partner",)
        )
    )
    authorization = PRE["AuthorizationRoles"](
        status=(
            inactive(RoleAssignmentStatus)
            if scenario == "missing_permission_grant"
            else RoleAssignmentStatus.ACTIVE
        )
    )
    roles = CombinedRoleReader(business, authorization)

    identity = SovereignIdentity(
        identity_id=PRE["ACTOR"],
        tenant_id="UNTRUSTED_TOKEN_TENANT",
        username="partner-test",
        email="partner@example.test",
        auth_method="test",
        status=PrincipalStatus.ACTIVE,
        roles=["ROOT", "TENANT_ADMIN"],
        permissions=["*"],
    )

    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(api.router, prefix="/api")

    # Authentication is controlled; actual tenant IAM is not overridden.
    app.dependency_overrides[iam.get_current_identity] = (
        lambda: identity
    )
    app.dependency_overrides[iam.get_principal_authority_repository] = (
        lambda: principal
    )
    app.dependency_overrides[iam.get_tenant_membership_repository] = (
        lambda: membership
    )
    app.dependency_overrides[iam.get_role_assignment_repository] = (
        lambda: roles
    )

    # The command endpoint also requests these repositories directly.
    app.dependency_overrides[api.get_authorization_role_repository] = (
        lambda: authorization
    )

    assert api._PROVISION not in app.dependency_overrides

    observed = []

    def transaction(callback):
        observed.append(endpoint)
        return {"canonical_iam": "ADMITTED"}

    monkeypatch.setattr(api, "_transaction", transaction)

    tenant = (
        "foreign-tenant"
        if scenario == "foreign_tenant"
        else PRE["TENANT"]
    )

    try:
        client = TestClient(app, raise_server_exceptions=True)
        response = client.post(
            endpoint,
            json=payload,
            headers={"X-Tenant-ID": tenant},
        )

        assert response.status_code == expected_status, (
            scenario, endpoint, response.status_code, response.text
        )
        if scenario == "eligible":
            assert response.json() == {"canonical_iam": "ADMITTED"}
            assert observed == [endpoint]
        else:
            assert observed == []
    finally:
        app.dependency_overrides.clear()

    assert all(
        call[0] == PRE["ACTOR"] for call in principal.calls
    )
    assert identity.tenant_id == "UNTRUSTED_TOKEN_TENANT"


# ARTIFACT: test_legal_practitioner_binding_http_canonical_iam.py
# VERSION: v1.0.0-P12C-R4M-P3B-REAL-IAM-HTTP
# AUTHORITY: canonical tenant IAM HTTP dependency only
# AUTHENTICATION: controlled identity fixture
# AUTHORIZATION DECISION: real canonical implementation
# DATABASE / FINANCIAL EXECUTION: none
# END OF WILSY OS SOVEREIGN ARTIFACT
