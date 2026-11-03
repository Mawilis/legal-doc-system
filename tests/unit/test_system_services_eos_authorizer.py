from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from tools.eos.system_services.eos_authorizer import (
    SystemServicesAuthorizationError,
    SystemServicesAuthorizationUnavailable,
    SystemServicesEosAuthorizer,
)
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)

AT = datetime(2026, 11, 3, 12, tzinfo=timezone.utc)
PRINCIPAL = "principal-staff-1"
PLATFORM_SCOPE = "platform-workforce"


class Transaction:
    in_transaction = True


class Possession:
    def __init__(self, assignment=True):
        self.assignment = assignment
        self.calls = []

    def resolve(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(principal_id=kwargs["principal_id"], permission_id=kwargs["permission_id"]) if self.assignment else None


def relationship(status=WorkforceRelationshipStatus.ACTIVE, scope_kind=WorkforceScopeKind.PLATFORM):
    return WorkforceRelationship(
        relationship_id="employment-1",
        revision=1,
        scope_kind=scope_kind,
        scope_id=PLATFORM_SCOPE,
        principal_id=PRINCIPAL,
        relationship_type=WorkforceRelationshipType.EMPLOYEE,
        status=status,
        effective_from=AT - timedelta(days=10),
        effective_until=None,
        status_effective_at=AT - timedelta(days=10),
        reason_reference="hr-evidence-1",
        supersedes_fingerprint=None,
    )


def make_authorizer(monkeypatch, relationships, possession=None):
    import tools.eos.system_services.eos_authorizer as module

    calls = []
    def list_relationships(scope_kind, scope_id, principal_id, *, collection, session):
        calls.append((scope_kind, scope_id, principal_id, collection, session))
        return tuple(relationships)

    monkeypatch.setattr(module, "list_principal_relationships", list_relationships)
    resolver = possession or Possession()
    authorizer = SystemServicesEosAuthorizer(
        possession_resolver=resolver,
        workforce_collection=object(),
        platform_scope_id=PLATFORM_SCOPE,
        clock=lambda: AT,
    )
    return authorizer, resolver, calls


def test_authorizes_only_current_permission_and_active_platform_workforce(monkeypatch):
    authorizer, resolver, calls = make_authorizer(monkeypatch, [relationship()])
    tx = Transaction()

    assert authorizer.require(
        principal_id=PRINCIPAL,
        permission_id="system_services:queue:read",
        session=tx,
    ) is None
    assert resolver.calls[0]["session"] is tx
    assert calls[0][0:3] == ("PLATFORM", PLATFORM_SCOPE, PRINCIPAL)
    assert calls[0][4] is tx


def test_missing_permission_assignment_denies_before_workforce_read(monkeypatch):
    authorizer, _, calls = make_authorizer(
        monkeypatch, [relationship()], possession=Possession(assignment=False)
    )
    with pytest.raises(SystemServicesAuthorizationError, match="CURRENT_SYSTEM_PERMISSION_REQUIRED"):
        authorizer.require(
            principal_id=PRINCIPAL,
            permission_id="system_services:queue:read",
            session=Transaction(),
        )
    assert calls == []


def test_suspended_platform_workforce_denies(monkeypatch):
    authorizer, _, _ = make_authorizer(
        monkeypatch, [relationship(WorkforceRelationshipStatus.SUSPENDED)]
    )
    with pytest.raises(SystemServicesAuthorizationError, match="ACTIVE_PLATFORM_WORKFORCE_REQUIRED"):
        authorizer.require(
            principal_id=PRINCIPAL,
            permission_id="system_services:queue:read",
            session=Transaction(),
        )


def test_tenant_workforce_evidence_cannot_satisfy_system_permission(monkeypatch):
    authorizer, _, _ = make_authorizer(
        monkeypatch, [relationship(scope_kind=WorkforceScopeKind.TENANT)]
    )
    with pytest.raises(SystemServicesAuthorizationUnavailable, match="PLATFORM_WORKFORCE_SCOPE_MISMATCH"):
        authorizer.require(
            principal_id=PRINCIPAL,
            permission_id="system_services:queue:read",
            session=Transaction(),
        )


def test_tenant_permission_cannot_enter_system_services_authorizer(monkeypatch):
    authorizer, _, calls = make_authorizer(monkeypatch, [relationship()])
    with pytest.raises(SystemServicesAuthorizationError, match="SYSTEM_WORKFORCE_PERMISSION_REQUIRED"):
        authorizer.require(
            principal_id=PRINCIPAL,
            permission_id="legal_operations:queue:read",
            session=Transaction(),
        )
    assert calls == []


def test_missing_transaction_fails_closed(monkeypatch):
    authorizer, _, calls = make_authorizer(monkeypatch, [relationship()])
    with pytest.raises(SystemServicesAuthorizationUnavailable, match="ACTIVE_TRANSACTION_REQUIRED"):
        authorizer.require(
            principal_id=PRINCIPAL,
            permission_id="system_services:queue:read",
            session=None,
        )
    assert calls == []


def test_explicit_platform_scope_id_is_mandatory():
    with pytest.raises(SystemServicesAuthorizationUnavailable, match="PLATFORM_SCOPE_ID_REQUIRED"):
        SystemServicesEosAuthorizer(
            possession_resolver=Possession(),
            workforce_collection=object(),
            platform_scope_id=" ",
        )


def test_mismatched_assignment_binding_is_unavailable(monkeypatch):
    class MismatchedPossession:
        def resolve(self, **kwargs):
            return SimpleNamespace(
                principal_id="another-principal",
                permission_id=kwargs["permission_id"],
            )

    authorizer, _, calls = make_authorizer(
        monkeypatch, [relationship()], possession=MismatchedPossession()
    )
    with pytest.raises(SystemServicesAuthorizationUnavailable, match="SYSTEM_ASSIGNMENT_BINDING_INVALID"):
        authorizer.require(
            principal_id=PRINCIPAL,
            permission_id="system_services:queue:read",
            session=Transaction(),
        )
    assert calls == []
