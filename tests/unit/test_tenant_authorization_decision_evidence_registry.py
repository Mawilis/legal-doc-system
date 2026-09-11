"""Direct certificate for durable tenant authorization evidence issuance.
VERSION: v1.0.0-TENANT-AUTHORIZATION-DECISION-EVIDENCE-REGISTRY-CERT
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
        self.calls.append(("find", query, session)); return next((r for r in self.rows if r["tenant_id"]==query["tenant_id"] and r["idempotency_key"]==query["idempotency_key"]), None)
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

# ARTIFACT: test_tenant_authorization_decision_evidence_registry.py
# VERSION: v1.0.0-TENANT-AUTHORIZATION-DECISION-EVIDENCE-REGISTRY-CERT
# AUTHORITY BOUNDARY: durable evidence certificate only; no financial execution.
# TENANT POSTURE: transaction and tenant scope are explicit.
# END OF WILSY OS SOVEREIGN ARTIFACT
