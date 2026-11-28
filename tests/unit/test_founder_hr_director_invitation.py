"""TITLE: WILSY OS Transitional Founder HR Director Invitation Certificate.
VERSION: v1.0.0-FOUNDER-HR-DIRECTOR-SCOPE-CERT
AUTHORITY: Synthetic source admission tests for the existing invitation route.
EPITOME: Certify only the exact active Founder can self-invite HR Director;
         non-Founder, cross-tenant, recipient mismatch and missing evidence deny.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_founder_hr_director_invitation.py
COLLABORATION / OWNERSHIP: Tenant IAM invitation policy and Founder employer scope.
CERTIFICATION / UPDATE DATE: 2026-11-27
CHANGELOG: v1.0.0-FOUNDER-HR-DIRECTOR-SCOPE-CERT verifies the in-transaction
           Founder-only delegation and immutable invitation boundary.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers, no real credentials or PII.
TENANT BOUNDARY: Exact canonical company tenant; deny other tenant.
AUTHORITY BOUNDARY: In-memory invitation construction; no role issued.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

import tools.eos.auth.invitation_creation as module
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID

NOW = datetime(2026, 11, 27, 10, 0, tzinfo=timezone.utc)


class Rows:
    def __init__(self, rows):
        self.rows = rows

    def limit(self, n):
        return self.rows[:n]


class Designations:
    def __init__(self, rows):
        self.rows = rows
        self.calls = 0

    def find(self, query, projection, *, session):
        self.calls += 1
        assert query == {
            "tenant_id": WILSY_COMPANY_TENANT_ID, "designation": "Founder",
        }
        assert projection.get("_id") == 0
        assert session is not None
        return Rows(self.rows)


class Database:
    def __init__(self, client, rows):
        self.client = client
        self.designations = Designations(rows)

    def __getitem__(self, key):
        assert key == "institutional_principal_designations"
        return self.designations


class Collection:
    def __init__(self, database):
        self.database = database


def build(monkeypatch, *, rows, role="ENTERPRISE_ADMIN"):
    client = object()
    db = Database(client, rows)
    collection = Collection(db)
    composition = module.InvitationCreationComposition(
        client, collection, collection, collection, collection, collection,
    )
    monkeypatch.setattr(
        module.PrincipalAuthorityRepository, "get",
        lambda *_args, **_kwargs: PrincipalAuthority("founder-test", PrincipalStatus.ACTIVE, 0),
    )
    monkeypatch.setattr(module.TenantRegistry, "get", lambda *_a, **_k: object())
    monkeypatch.setattr(module.TenantMembershipRepository, "resolve", lambda *_a, **_k: object())
    monkeypatch.setattr(
        module.RoleAssignmentRepository, "list_assignments",
        lambda *_a, **_k: (RoleAssignmentAuthority(
            "founder-test", WILSY_COMPANY_TENANT_ID, role,
            RoleAssignmentStatus.ACTIVE, 0,
        ),),
    )
    saved = []
    monkeypatch.setattr(module.InvitationRepository, "insert", lambda invitation, **_k: saved.append(invitation))
    return composition, db, saved


def identity(tenant=WILSY_COMPANY_TENANT_ID):
    return SovereignIdentity(
        identity_id="founder-test", tenant_id=tenant,
        username=None, email=None, auth_method="certificate",
        status=PrincipalStatus.ACTIVE,
    )


def invoke(composition, *, tenant=WILSY_COMPANY_TENANT_ID, recipient="founder-test"):
    return composition._create_in_transaction(
        session=object(), identity=identity(tenant),
        tenant_id=tenant, recipient_principal_id=recipient,
        authorization_role_id="HR_DIRECTOR",
        expires_at=NOW + timedelta(hours=1),
        invitation_id="test-invitation", capability_digest="a" * 128,
        created_at=NOW,
    )


def valid_founder():
    return {
        "principal_id": "founder-test", "state": "ACTIVE",
        "business_role": "tenant_owner", "grants_permissions": False,
    }


def test_verified_founder_may_create_only_self_bound_director_invitation(monkeypatch):
    composition, db, saved = build(monkeypatch, rows=[valid_founder()])
    result = invoke(composition)
    assert len(saved) == 1
    assert result.authorization_role_id == "HR_DIRECTOR"
    assert result.recipient_principal_id == "founder-test"
    assert db.designations.calls == 1


@pytest.mark.parametrize("rows", [
    [],
    [{**valid_founder(), "state": "SUSPENDED"}],
    [{**valid_founder(), "grants_permissions": True}],
    [{**valid_founder(), "principal_id": "other"}],
    [valid_founder(), valid_founder()],
])
def test_missing_or_invalid_founder_denies_without_inserting(monkeypatch, rows):
    composition, _, saved = build(monkeypatch, rows=rows)
    with pytest.raises(module.InvitationCreationError, match="DESIGNATION_DENIED"):
        invoke(composition)
    assert saved == []


def test_other_recipient_denied_before_founder_lookup(monkeypatch):
    composition, db, saved = build(monkeypatch, rows=[valid_founder()])
    with pytest.raises(module.InvitationCreationError, match="SCOPE_DENIED"):
        invoke(composition, recipient="not-founder")
    assert saved == []
    assert db.designations.calls == 0


def test_other_tenant_denied_and_never_reads_founder(monkeypatch):
    composition, db, saved = build(monkeypatch, rows=[valid_founder()])
    with pytest.raises(module.InvitationCreationError):
        invoke(composition, tenant="foreign-tenant")
    assert saved == []
    assert db.designations.calls == 0


def test_no_enterprise_admin_delegation_edge_no_invitation(monkeypatch):
    composition, db, saved = build(monkeypatch, rows=[valid_founder()], role="AUDITOR")
    with pytest.raises(module.InvitationCreationError, match="GRANT_NOT_PERMITTED"):
        invoke(composition)
    assert saved == []
    assert db.designations.calls == 0


# ARTIFACT: tests/unit/test_founder_hr_director_invitation.py
# VERSION: v1.0.0-FOUNDER-HR-DIRECTOR-SCOPE-CERT
# AUTHORITY BOUNDARY: Synthetic invitation-only tests; no role creation or approval.
# TENANT POSTURE: Canonical employer only; cross-tenant and foreign recipients deny.
# FAIL-CLOSED POSTURE: Missing, ambiguous or stale Founder evidence never grants.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
