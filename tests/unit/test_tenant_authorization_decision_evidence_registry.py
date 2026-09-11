"""TITLE: WILSY OS Tenant Authorization Decision Evidence Registry Certificate.
VERSION: v1.1.0-M11-R8-R3B-P6A-CERT
AUTHORITY: Durable generic tenant privilege evidence certification only.
EPITOME: Proves exact operation, permission, principal, tenant, opaque subject,
and current policy-version capture without typed collection issuance.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_authorization_decision_evidence_registry.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-09.
CHANGELOG: v1.1.0-M11-R8-R3B-P6A-CERT adds the dedicated inbound collection
authorization-request evidence composition and current-version assertions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Tenant-scoped transaction evidence; no provider or
financial execution authority is created.
TENANT BOUNDARY: Exact tenant and principal identity are required for reads,
idempotency, and durable evidence.
AUTHORITY BOUNDARY: Generic privilege evidence only; typed subject issuance is separate.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
import pytest
from typing import Any, cast

from tools.eos.auth.tenant_authorization_decision_evidence_registry import *
from tools.eos.auth.tenant_authorization import TenantAuthorizationDecision, TenantAuthorizationReason
import tools.eos.auth.tenant_authorization_decision_evidence_registry as registry_module

class Session:
    in_transaction = True

class Collection:
    def __init__(self): self.rows=[]; self.calls=[]
    def create_index(self, *args, **kwargs): self.calls.append((args, kwargs))
    def find_one(self, query, *, session):
        self.calls.append(("find", query, session)); return next((r for r in self.rows if all(r.get(k)==v for k,v in query.items())), None)
    def insert_one(self, row, *, session): self.calls.append(("insert", row, session)); self.rows.append(dict(row)); return SimpleNamespace()

class Principal:
    def resolve(self, principal_id, *, session=None): return SimpleNamespace(status=__import__("tools.eos.auth.principal_status", fromlist=["PrincipalStatus"]).PrincipalStatus.ACTIVE)
class Membership:
    def resolve(self, principal_id, tenant_id, *, session=None): return SimpleNamespace(status=__import__("tools.eos.auth.tenant_membership", fromlist=["TenantMembershipStatus"]).TenantMembershipStatus.ACTIVE, revision=3)
class Assignment:
    def resolve(self, principal_id, tenant_id, role_id, *, session=None):
        return SimpleNamespace(status=__import__("tools.eos.auth.role_assignment", fromlist=["RoleAssignmentStatus"]).RoleAssignmentStatus.ACTIVE, revision=4)
class Business(Assignment): pass

@pytest.fixture(autouse=True)
def canonical_authorizer(monkeypatch):
    monkeypatch.setattr(registry_module, "authorize_tenant_operation", lambda **kwargs: TenantAuthorizationDecision(True, TenantAuthorizationReason.AUTHORIZED, "tenant_owner", "ENTERPRISE_ADMIN"))

def registry(collection: Any = None) -> TenantAuthorizationDecisionEvidenceRegistry:
    return TenantAuthorizationDecisionEvidenceRegistry(cast(Any, collection or Collection()), principal_repository=Principal(), membership_repository=Membership(), role_assignment_repository=Assignment(), business_role_repository=Business())

def kwargs(**extra: Any) -> dict[str, Any]:
    value=dict(tenant_id="t1", principal_id="p1", operation="platform_billing_release", permission="platform_billing:release", subject_reference="subject-1", subject_evidence_fingerprint="a"*128, idempotency_key="i1", session=Session())
    value.update(extra); return value

def test_requires_active_caller_transaction():
    with pytest.raises(TenantAuthorizationDecisionEvidenceTransactionRequiredError): registry().issue(**kwargs(session=None))
    s=Session(); s.in_transaction=False
    with pytest.raises(TenantAuthorizationDecisionEvidenceTransactionRequiredError): registry().issue(**kwargs(session=s))

def test_new_issue_persists_transaction_pending_evidence():
    c=Collection(); value=registry(c).issue(**kwargs()); assert value.tenant_id == "t1" and len(c.rows)==1

def test_denied_does_not_persist(monkeypatch):
    c=Collection()
    monkeypatch.setattr("tools.eos.auth.tenant_authorization_decision_evidence_registry.authorize_tenant_operation", lambda **kwargs: TenantAuthorizationDecision(False, TenantAuthorizationReason.PERMISSION_NOT_GRANTED))
    with pytest.raises(TenantAuthorizationDecisionEvidenceAuthorizationDeniedError): registry(c).issue(**cast(dict[str, Any], kwargs()))
    assert c.rows == []

def test_exact_replay_is_historic_and_stable():
    c=Collection(); r=registry(c); first=r.issue(**kwargs()); replay=r.issue(**kwargs()); assert replay == first and len(c.rows)==1

def test_divergent_replay_conflicts_without_second_insert():
    c=Collection(); r=registry(c); r.issue(**kwargs());
    with pytest.raises(TenantAuthorizationDecisionEvidenceConflictError): r.issue(**kwargs(subject_reference="subject-2"))
    assert len(c.rows)==1

def test_same_key_different_tenant_is_independent():
    c=Collection(); r=registry(c); a=r.issue(**kwargs()); b=r.issue(**kwargs(tenant_id="t2")); assert a.tenant_id != b.tenant_id and len(c.rows)==2

def test_indexes_are_explicit_and_outside_issue():
    c=Collection(); r=registry(c); r.ensure_indexes(); assert len(c.calls)==2

def test_session_identity_reaches_reads_and_insert():
    c=Collection(); s=Session(); r=registry(c); r.issue(**kwargs(session=s)); assert all(call[-1] is s for call in c.calls if call[0] in ("find", "insert"))

def test_generated_identity_and_time_are_safe():
    value=registry().issue(**kwargs()); assert ":" not in value.authorization_decision_id and value.authorized_at.tzinfo is timezone.utc

def test_caller_cannot_supply_derived_authority_fields():
    with pytest.raises(TypeError): registry().issue(**kwargs(business_role="tenant_owner"))

def test_replay_does_not_reauthorize():
    c=Collection(); r=registry(c); r.issue(**kwargs())
    replay = registry(c).issue(**cast(dict[str, Any], kwargs()))
    assert replay.authorization_decision_id

def test_activate_evidence_exact_readback(monkeypatch):
    """Certify exact activate evidence readback without selection or reauthorization."""
    from tools.eos.auth.tenant_authorization import authorize_tenant_operation as real_authorize
    from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
    from tools.eos.auth.role_assignment import RoleAssignmentStatus
    class Reader:
        def __init__(self, role): self.role=role
        def resolve(self, principal_id, tenant_id, role_id, *, session=None):
            if role_id != self.role: raise RoleAssignmentNotFoundError("missing")
            return SimpleNamespace(status=RoleAssignmentStatus.ACTIVE, revision=1)
    monkeypatch.setattr(registry_module, "authorize_tenant_operation", real_authorize)
    c=Collection(); r=TenantAuthorizationDecisionEvidenceRegistry(cast(Any,c), principal_repository=Principal(), membership_repository=Membership(), role_assignment_repository=Reader("PLATFORM_BILLING_PROVIDER_POLICY_ADMIN"), business_role_repository=Reader("tenant_platform_billing_provider_policy_admin"))
    kw: dict[str, Any] = dict(tenant_id="t1",principal_id="p1",operation="platform_billing_provider_policy_activate",permission="platform_billing:provider_policy:admin",subject_reference="tenant:t1:provider-policy:p1",subject_evidence_fingerprint="b"*128,idempotency_key="activate-1",session=Session())
    issued=r.issue(**kw); read=r.get(tenant_id="t1",authorization_decision_id=issued.authorization_decision_id,session=cast(Any,Session()))
    assert read == issued and read.operation == kw["operation"] and read.permission == kw["permission"]
    with pytest.raises(TenantAuthorizationDecisionEvidencePersistenceError): r.get(tenant_id="t2",authorization_decision_id=issued.authorization_decision_id,session=cast(Any,Session()))

def test_provider_policy_admin_real_authorization_and_durable_readback(monkeypatch):
    """Execute the real provider-policy-admin authorization/evidence boundary."""
    from tools.eos.auth.tenant_authorization import authorize_tenant_operation as real_authorize
    from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
    from tools.eos.auth.role_assignment import RoleAssignmentStatus
    class Reader:
        def __init__(self, role, revision): self.role, self.revision = role, revision
        def resolve(self, principal_id, tenant_id, role_id, *, session=None):
            if role_id != self.role: raise RoleAssignmentNotFoundError("missing")
            return SimpleNamespace(status=RoleAssignmentStatus.ACTIVE, revision=self.revision)
    monkeypatch.setattr(registry_module, "authorize_tenant_operation", real_authorize)
    c = Collection()
    r = TenantAuthorizationDecisionEvidenceRegistry(cast(Any, c), principal_repository=Principal(), membership_repository=Membership(), role_assignment_repository=Reader("PLATFORM_BILLING_PROVIDER_POLICY_ADMIN", 8), business_role_repository=Reader("tenant_platform_billing_provider_policy_admin", 7))
    kw: dict[str, Any] = dict(tenant_id="t1", principal_id="p1", operation="platform_billing_provider_policy_create", permission="platform_billing:provider_policy:admin", subject_reference="tenant:t1:provider-policy:outbound", subject_evidence_fingerprint="a" * 128, idempotency_key="provider-policy-1", session=Session())
    value = r.issue(**kw)
    assert value.business_role == "tenant_platform_billing_provider_policy_admin"
    assert value.operation == kw["operation"] and value.subject_reference == kw["subject_reference"]
    assert r.issue(**kw) == value and len(c.rows) == 1


def test_inbound_collection_privilege_real_authorization_and_evidence_capture(monkeypatch):
    """Capture the exact generic privilege evidence without constructing a typed subject."""
    from tools.eos.auth.tenant_authorization import authorize_tenant_operation as real_authorize
    from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
    from tools.eos.auth.role_assignment import RoleAssignmentStatus
    from tools.eos.auth import permission_namespace, roles, tenant_authority_policy, tenant_authorization

    class Reader:
        def __init__(self, role: str, revision: int):
            self.role, self.revision = role, revision

        def resolve(self, principal_id, tenant_id, role_id, *, session=None):
            if role_id != self.role:
                raise RoleAssignmentNotFoundError("missing")
            return SimpleNamespace(status=RoleAssignmentStatus.ACTIVE, revision=self.revision)

    monkeypatch.setattr(registry_module, "authorize_tenant_operation", real_authorize)
    c = Collection()
    r = TenantAuthorizationDecisionEvidenceRegistry(
        cast(Any, c),
        principal_repository=Principal(),
        membership_repository=Membership(),
        role_assignment_repository=Reader("INBOUND_COLLECTION_AUTHORIZATION_ADMIN", 8),
        business_role_repository=Reader("tenant_inbound_collection_authorization_admin", 7),
    )
    kw: dict[str, Any] = dict(
        tenant_id="tenant-inbound",
        principal_id="principal-inbound",
        operation="inbound_collection_authorization_create",
        permission="inbound_collection:authorization:create",
        subject_reference="opaque:inbound-intent:1",
        subject_evidence_fingerprint="c" * 128,
        idempotency_key="inbound-privilege-1",
        session=Session(),
    )
    value = r.issue(**kw)
    assert value.tenant_id == kw["tenant_id"]
    assert value.principal_id == kw["principal_id"]
    assert value.operation == kw["operation"]
    assert value.permission == kw["permission"]
    assert value.business_role == "tenant_inbound_collection_authorization_admin"
    assert value.authorization_role == "INBOUND_COLLECTION_AUTHORIZATION_ADMIN"
    assert value.subject_reference == kw["subject_reference"]
    assert value.subject_evidence_fingerprint == kw["subject_evidence_fingerprint"]
    assert value.permission_namespace_version == permission_namespace.VERSION
    assert value.authorization_role_policy_version == roles.VERSION
    assert value.tenant_business_role_policy_version == tenant_authority_policy.VERSION
    assert value.tenant_authorization_composition_version == tenant_authorization.VERSION
    assert len(c.rows) == 1

# ARTIFACT: test_tenant_authorization_decision_evidence_registry.py
# VERSION: v1.1.0-M11-R8-R3B-P6A-CERT
# AUTHORITY BOUNDARY: durable evidence certificate only; no financial execution.
# TENANT POSTURE: transaction and tenant scope are explicit.
# END OF WILSY OS SOVEREIGN ARTIFACT
