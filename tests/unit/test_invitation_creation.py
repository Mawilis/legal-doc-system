"""Unit certificate for sovereign invitation creation authority."""
# pyright: reportArgumentType=false, reportIncompatibleMethodOverride=false
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.invitation_creation import create_invitation, InvitationCreationComposition
import tools.eos.auth.invitation_creation as module

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
class Session:
    def with_transaction(self, callback): callback(self)
class Client:
    def start_session(self): return self
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def with_transaction(self, callback): callback(self)

def test_enterprise_admin_can_create_and_returns_separate_capability(monkeypatch):
    identity = SovereignIdentity(identity_id="inviter", tenant_id="tenant", username=None, email=None, auth_method="certificate", status=PrincipalStatus.ACTIVE)
    assignment = RoleAssignmentAuthority("inviter", "tenant", "ENTERPRISE_ADMIN", RoleAssignmentStatus.ACTIVE, 0)
    captured = {}
    monkeypatch.setattr(module, "get_client", lambda: Client())
    class DB:
        def __getitem__(self, key): return object()
    monkeypatch.setattr("tools.eos.kernel.db.get_database", lambda: DB())
    monkeypatch.setattr(module.PrincipalAuthorityRepository, "get", lambda *a, **k: PrincipalAuthority("inviter", PrincipalStatus.ACTIVE, 0))
    monkeypatch.setattr(module.TenantRegistry, "get", lambda *a, **k: object())
    monkeypatch.setattr(module.TenantMembershipRepository, "resolve", lambda *a, **k: object())
    monkeypatch.setattr(module.RoleAssignmentRepository, "list_assignments", lambda *a, **k: (assignment,))
    monkeypatch.setattr(module.InvitationRepository, "insert", lambda value, **k: captured.setdefault("value", value) or value)
    result = create_invitation(identity=identity, tenant_id="tenant", recipient_principal_id="recipient", authorization_role_id="AUDITOR", expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
    assert result.invitation.status.value == "ACTIVE" and result.invitation.revision == 0
    assert result.invitation.recipient_principal_id == "recipient" and result.invitation.authorization_role_id == "AUDITOR"
    assert len(result.invitation.capability_digest) == 128 and result.capability not in result.invitation.capability_digest

def test_denied_escalation_does_not_insert(monkeypatch):
    identity = SovereignIdentity(identity_id="inviter", tenant_id="tenant", username=None, email=None, auth_method="certificate", status=PrincipalStatus.ACTIVE)
    assignment = RoleAssignmentAuthority("inviter", "tenant", "ENTERPRISE_ADMIN", RoleAssignmentStatus.ACTIVE, 0)
    monkeypatch.setattr(module, "get_client", lambda: Client())
    class DB:
        def __getitem__(self, key): return object()
    monkeypatch.setattr("tools.eos.kernel.db.get_database", lambda: DB())
    monkeypatch.setattr(module.PrincipalAuthorityRepository, "get", lambda *a, **k: PrincipalAuthority("inviter", PrincipalStatus.ACTIVE, 0))
    monkeypatch.setattr(module.TenantRegistry, "get", lambda *a, **k: object())
    monkeypatch.setattr(module.TenantMembershipRepository, "resolve", lambda *a, **k: object())
    monkeypatch.setattr(module.RoleAssignmentRepository, "list_assignments", lambda *a, **k: (assignment,))
    insert = lambda *a, **k: pytest.fail("insert must not be called")
    monkeypatch.setattr(module.InvitationRepository, "insert", insert)
    with pytest.raises(module.InvitationCreationError, match="GRANT_NOT_PERMITTED"):
        create_invitation(identity=identity, tenant_id="tenant", recipient_principal_id="recipient", authorization_role_id="ENTERPRISE_ADMIN", expires_at=datetime.now(timezone.utc) + timedelta(hours=1))

def _identity():
    return SovereignIdentity(identity_id="inviter", tenant_id="tenant", username=None, email=None, auth_method="certificate", status=PrincipalStatus.ACTIVE)

def _wire(monkeypatch, assignments):
    monkeypatch.setattr(module, "get_client", lambda: Client())
    class DB:
        def __getitem__(self, key): return object()
    monkeypatch.setattr("tools.eos.kernel.db.get_database", lambda: DB())
    monkeypatch.setattr(module.PrincipalAuthorityRepository, "get", lambda *a, **k: PrincipalAuthority(a[0], PrincipalStatus.ACTIVE, 0))
    monkeypatch.setattr(module.TenantRegistry, "get", lambda *a, **k: object())
    monkeypatch.setattr(module.TenantMembershipRepository, "resolve", lambda *a, **k: object())
    monkeypatch.setattr(module.RoleAssignmentRepository, "list_assignments", lambda *a, **k: tuple(assignments))

@pytest.mark.parametrize(("source", "target", "allowed"), [
    ("ENTERPRISE_ADMIN", "AUDITOR", True), ("ENTERPRISE_ADMIN", "SERVICE_WORKER", True),
    ("ENTERPRISE_ADMIN", "ENTERPRISE_ADMIN", False), ("ENTERPRISE_ADMIN", "SOVEREIGN_ARCHITECT", False),
    ("SOVEREIGN_ARCHITECT", "AUDITOR", False), ("AUDITOR", "AUDITOR", False),
    ("SERVICE_WORKER", "AUDITOR", False),
])
def test_authority_matrix(monkeypatch, source, target, allowed):
    assignment = RoleAssignmentAuthority("inviter", "tenant", source, RoleAssignmentStatus.ACTIVE, 0)
    _wire(monkeypatch, (assignment,))
    inserted = []
    monkeypatch.setattr(module.InvitationRepository, "insert", lambda value, **k: inserted.append(value))
    kwargs = dict(identity=_identity(), tenant_id="tenant", recipient_principal_id="recipient", authorization_role_id=target, expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
    if allowed:
        assert create_invitation(**kwargs).invitation.authorization_role_id == target
    else:
        with pytest.raises(module.InvitationCreationError, match="GRANT_NOT_PERMITTED"):
            create_invitation(**kwargs)
        assert not inserted

def test_multi_role_uses_complete_assignment_set(monkeypatch):
    assignments = tuple(RoleAssignmentAuthority("inviter", "tenant", role, RoleAssignmentStatus.ACTIVE, 0) for role in ("AUDITOR", "ENTERPRISE_ADMIN"))
    _wire(monkeypatch, assignments)
    seen = {}
    monkeypatch.setattr(module.RoleAssignmentRepository, "list_assignments", lambda *a, **k: seen.setdefault("assignments", tuple(assignments)))
    monkeypatch.setattr(module.InvitationRepository, "insert", lambda *a, **k: None)
    result = create_invitation(identity=_identity(), tenant_id="tenant", recipient_principal_id="recipient", authorization_role_id="AUDITOR", expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
    assert result.invitation.authorization_role_id == "AUDITOR" and len(seen["assignments"]) == 2

def test_all_operations_receive_same_session_and_digest_is_canonical(monkeypatch):
    sessions = []
    assignment = RoleAssignmentAuthority("inviter", "tenant", "ENTERPRISE_ADMIN", RoleAssignmentStatus.ACTIVE, 0)
    _wire(monkeypatch, (assignment,))
    for target in (module.PrincipalAuthorityRepository, module.TenantRegistry, module.TenantMembershipRepository, module.RoleAssignmentRepository, module.InvitationRepository):
        for name in ("get", "resolve", "list_assignments", "insert"):
            if hasattr(getattr(target, name, None), "__call__"):
                original = getattr(target, name)
                def wrapped(*args, __orig=original, **kwargs):
                    if "session" in kwargs: sessions.append(kwargs["session"])
                    return __orig(*args, **kwargs)
                monkeypatch.setattr(target, name, wrapped)
    monkeypatch.setattr(module.InvitationRepository, "insert", lambda value, **k: (sessions.append(k["session"]), None)[1])
    result = create_invitation(identity=_identity(), tenant_id="tenant", recipient_principal_id="recipient", authorization_role_id="AUDITOR", expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
    assert sessions and len({id(s) for s in sessions}) == 1
    assert result.invitation.capability_digest == __import__("hashlib").sha3_512(result.capability.encode()).hexdigest()

def test_mixed_client_graph_rejected():
    class C:
        def __init__(self, client): self.database = SimpleNamespace(client=client)
    with pytest.raises(module.InvitationCreationError, match="MIXED_CLIENT_GRAPH"):
        InvitationCreationComposition(object(), C(object()), C(object()), C(object()), C(object()), C(object()))

def test_business_api_has_no_infrastructure_parameters():
    import inspect
    names = set(inspect.signature(create_invitation).parameters)
    assert names == {"identity", "tenant_id", "recipient_principal_id", "authorization_role_id", "expires_at"}

def test_retry_callback_reuses_frozen_authority_material(monkeypatch):
    """A retrying transaction callback observes one frozen command envelope."""
    class RetrySession(Session):
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def with_transaction(self, callback):
            callback(self); callback(self)
    class RetryClient(Client):
        def start_session(self): return RetrySession()
    _wire(monkeypatch, (RoleAssignmentAuthority("inviter", "tenant", "ENTERPRISE_ADMIN", RoleAssignmentStatus.ACTIVE, 0),))
    monkeypatch.setattr(module, "get_client", lambda: RetryClient())
    class DB:
        def __getitem__(self, key): return object()
    monkeypatch.setattr("tools.eos.kernel.db.get_database", lambda: DB())
    assignment = RoleAssignmentAuthority("inviter", "tenant", "ENTERPRISE_ADMIN", RoleAssignmentStatus.ACTIVE, 0)
    monkeypatch.setattr(module.RoleAssignmentRepository, "list_assignments", lambda *a, **k: (assignment,))
    seen = []
    monkeypatch.setattr(module.InvitationRepository, "insert", lambda value, **kwargs: seen.append(value))
    result = create_invitation(identity=_identity(), tenant_id="tenant", recipient_principal_id="recipient", authorization_role_id="AUDITOR", expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
    assert len(seen) == 2
    assert all((v.invitation_id, v.capability_digest, v.created_at, v.expires_at, v.recipient_principal_id, v.authorization_role_id) == (seen[0].invitation_id, seen[0].capability_digest, seen[0].created_at, seen[0].expires_at, seen[0].recipient_principal_id, seen[0].authorization_role_id) for v in seen)
    assert result.capability and result.invitation.capability_digest == seen[0].capability_digest
