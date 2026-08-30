"""TITLE: WILSY OS Tenant Authorization HTTP Certification.
VERSION: v1.0.0-TENANT-AUTHORIZATION-HTTP-CERT
AUTHORITY: Test-local ASGI certification of the reusable tenant dependency.
EPITOME: Proves HTTP translation without production route wiring or persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_authorization_http.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.0 certifies positive, denied, unavailable, scope, and transport boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: Test-local identities only; projected roles and tenants never grant authority.
TENANT BOUNDARY: X-Tenant-ID is explicit scope and durable membership remains authoritative.
AUTHORITY BOUNDARY: Certifies HTTP translation only; no production route wiring or persistence mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

import inspect
from collections.abc import Mapping
from typing import cast

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

import tools.eos.api.tenant_authorization_http as boundary
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.roles import get_roles_granting_permission
from tools.eos.auth.tenant_access import get_current_tenant_identity
from tools.eos.auth.tenant_authorization import (
    AssignmentReader,
    MembershipReader,
    PrincipalReader,
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_business_role_authority import TENANT_ROLES
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
    TenantMembershipRepositoryError,
)

VERSION = "v1.0.0-TENANT-AUTHORIZATION-HTTP-CERT"
EXPECTED_PRIMARY_BLOB = "11f4033f16b3bffd08a3b2e0789a7fa326fba942"
_PID = "p"
_TENANT = "tenant-a"
_AUDIT_PERMISSION = "audit:read"
_AUDIT_OPERATION = "audit_read"
_AUDIT_GRANTING_ROLES = tuple(get_roles_granting_permission(_AUDIT_PERMISSION))


class _RecordingReader:
    """Deterministic resolve-only reader with mutation tripwires."""

    def __init__(
        self,
        values: Mapping[tuple[str, ...], object] | None = None,
        failures: Mapping[tuple[str, ...], Exception] | None = None,
    ) -> None:
        self.values = dict(values or {})
        self.failures = dict(failures or {})
        self.read_calls: list[tuple[str, ...]] = []
        self.write_calls = 0

    def resolve(self, *keys: str) -> object:
        key = tuple(keys)
        self.read_calls.append(key)
        failure = self.failures.get(key)
        if failure is not None:
            raise failure
        if key in self.values:
            return self.values[key]
        if len(key) == 1:
            raise PrincipalAuthorityNotFoundError("PRINCIPAL_AUTHORITY_NOT_FOUND")
        if len(key) == 2:
            raise TenantMembershipNotFoundError("TENANT_MEMBERSHIP_NOT_FOUND")
        raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")

    def _write_forbidden(self, *_args: object, **_kwargs: object) -> None:
        self.write_calls += 1
        pytest.fail("authorization attempted persistence mutation")

    def create(self, *_args: object, **_kwargs: object) -> None:
        self._write_forbidden(*_args, **_kwargs)

    def insert(self, *_args: object, **_kwargs: object) -> None:
        self._write_forbidden(*_args, **_kwargs)

    def update(self, *_args: object, **_kwargs: object) -> None:
        self._write_forbidden(*_args, **_kwargs)

    def replace(self, *_args: object, **_kwargs: object) -> None:
        self._write_forbidden(*_args, **_kwargs)

    def replace_one(self, *_args: object, **_kwargs: object) -> None:
        self._write_forbidden(*_args, **_kwargs)

    def compare_and_swap(self, *_args: object, **_kwargs: object) -> None:
        self._write_forbidden(*_args, **_kwargs)

    def delete(self, *_args: object, **_kwargs: object) -> None:
        self._write_forbidden(*_args, **_kwargs)

    def delete_one(self, *_args: object, **_kwargs: object) -> None:
        self._write_forbidden(*_args, **_kwargs)


def _identity(
    *,
    identity_id: str = _PID,
    tenant_id: str = "wrong-token-tenant",
    roles: list[str] | None = None,
    permissions: list[str] | None = None,
) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=identity_id,
        tenant_id=tenant_id,
        username="u",
        email="u@example.test",
        auth_method="test",
        status=PrincipalStatus.ACTIVE,
        roles=roles or [],
        permissions=permissions or [],
    )


def _active_principal(pid: str = _PID) -> PrincipalAuthority:
    return PrincipalAuthority(pid, PrincipalStatus.ACTIVE, 0)


def _inactive_principal(pid: str = _PID) -> PrincipalAuthority:
    for status in PrincipalStatus:
        if status is not PrincipalStatus.ACTIVE:
            return PrincipalAuthority(pid, status, 0)
    raise AssertionError("PrincipalStatus must define a non-ACTIVE state")


def _membership(
    *,
    pid: str = _PID,
    tid: str = _TENANT,
    status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
) -> TenantMembershipAuthority:
    return TenantMembershipAuthority(pid, tid, status, 0)


def _role(
    role_id: str,
    *,
    pid: str = _PID,
    tid: str = _TENANT,
    status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
) -> RoleAssignmentAuthority:
    return RoleAssignmentAuthority(pid, tid, role_id, status, 0)


def _valid_readers(
    *,
    pid: str = _PID,
    tid: str = _TENANT,
) -> tuple[_RecordingReader, _RecordingReader, _RecordingReader]:
    principal_reader = _RecordingReader({(pid,): _active_principal(pid)})
    membership_reader = _RecordingReader({(pid, tid): _membership(pid=pid, tid=tid)})
    role_values: dict[tuple[str, ...], object] = {
        (pid, tid, "tenant_auditor"): _role("tenant_auditor", pid=pid, tid=tid),
    }
    for role_id in _AUDIT_GRANTING_ROLES:
        role_values[(pid, tid, role_id)] = _role(role_id, pid=pid, tid=tid)
    role_reader = _RecordingReader(role_values)
    return principal_reader, membership_reader, role_reader


def _real_app(
    *,
    identity: SovereignIdentity,
    principal_reader: object,
    membership_reader: object,
    role_reader: object,
    permission_id: str = _AUDIT_PERMISSION,
    operation: str = _AUDIT_OPERATION,
) -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.dependency_overrides[boundary.get_current_identity] = lambda: identity
    app.dependency_overrides[boundary.get_principal_authority_repository] = (
        lambda: principal_reader
    )
    app.dependency_overrides[boundary.get_tenant_membership_repository] = (
        lambda: membership_reader
    )
    app.dependency_overrides[boundary.get_role_assignment_repository] = (
        lambda: role_reader
    )

    @app.get("/cert")
    async def cert(
        context: boundary.TenantAuthorizationContext = Depends(
            boundary.RequireTenantAuthorization(permission_id, operation)
        ),
    ) -> dict[str, str]:
        return {
            "principal_id": context.identity.identity_id,
            "tenant_id": context.tenant_id,
            "reason": context.decision.reason.value,
        }

    return app


def _decision(
    *,
    principal_reader: _RecordingReader,
    membership_reader: _RecordingReader,
    role_reader: _RecordingReader,
    pid: str = _PID,
    tid: str = _TENANT,
    permission_id: str = _AUDIT_PERMISSION,
    operation: str = _AUDIT_OPERATION,
) -> TenantAuthorizationDecision:
    return authorize_tenant_operation(
        principal_id=pid,
        tenant_id=tid,
        permission_id=permission_id,
        operation=operation,
        principal_repository=cast(PrincipalReader, principal_reader),
        membership_repository=cast(MembershipReader, membership_reader),
        business_role_repository=cast(AssignmentReader, role_reader),
        role_assignment_repository=cast(AssignmentReader, role_reader),
    )


def _assert_read_only(*readers: _RecordingReader) -> None:
    assert all(reader.write_calls == 0 for reader in readers)


def test_real_frozen_composition_http_positive() -> None:
    identity = _identity(
        roles=["ROOT", "GLOBAL_ROOT", "TENANT_ADMIN", "ADMIN", "AUDITOR"],
        permissions=["*", _AUDIT_PERMISSION],
    )
    principal_reader, membership_reader, role_reader = _valid_readers()
    with TestClient(
        _real_app(
            identity=identity,
            principal_reader=principal_reader,
            membership_reader=membership_reader,
            role_reader=role_reader,
        )
    ) as client:
        response = client.get("/cert", headers={"X-Tenant-ID": _TENANT})
    assert response.status_code == 200
    assert response.json() == {
        "principal_id": _PID,
        "tenant_id": _TENANT,
        "reason": TenantAuthorizationReason.AUTHORIZED.value,
    }
    assert identity.tenant_id == "wrong-token-tenant"
    _assert_read_only(principal_reader, membership_reader, role_reader)


def test_http_authentication_failures_remain_401() -> None:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.dependency_overrides[boundary.get_principal_authority_repository] = (
        lambda: _RecordingReader()
    )
    app.dependency_overrides[boundary.get_tenant_membership_repository] = (
        lambda: _RecordingReader()
    )
    app.dependency_overrides[boundary.get_role_assignment_repository] = (
        lambda: _RecordingReader()
    )

    @app.get("/auth")
    async def auth(
        _context: boundary.TenantAuthorizationContext = Depends(
            boundary.RequireTenantAuthorization(_AUDIT_PERMISSION, _AUDIT_OPERATION)
        ),
    ) -> dict[str, bool]:
        return {"ok": True}

    assert boundary.get_current_identity not in app.dependency_overrides
    with TestClient(app) as client:
        missing = client.get("/auth", headers={"X-Tenant-ID": _TENANT})
        invalid = client.get(
            "/auth",
            headers={
                "X-Tenant-ID": _TENANT,
                "Authorization": "Bearer definitely-invalid-token",
            },
        )
    assert missing.status_code == 401
    assert invalid.status_code == 401


def test_explicit_tenant_scope_is_required_and_not_projected() -> None:
    identity = _identity(tenant_id=_TENANT)
    principal_reader, membership_reader, role_reader = _valid_readers()
    app = _real_app(
        identity=identity,
        principal_reader=principal_reader,
        membership_reader=membership_reader,
        role_reader=role_reader,
    )
    with TestClient(app) as client:
        missing = client.get("/cert")
        non_trimmed = client.get("/cert", headers={"X-Tenant-ID": f" {_TENANT} "})
    assert missing.status_code == 403
    assert non_trimmed.status_code == 403
    assert identity.tenant_id == _TENANT


def test_real_principal_denial_matrix() -> None:
    membership_reader = _RecordingReader({(_PID, _TENANT): _membership()})
    role_reader = _RecordingReader()
    cases = (
        (
            _RecordingReader(
                failures={
                    (_PID,): PrincipalAuthorityNotFoundError(
                        "PRINCIPAL_AUTHORITY_NOT_FOUND"
                    )
                }
            ),
            TenantAuthorizationReason.PRINCIPAL_NOT_FOUND,
        ),
        (
            _RecordingReader({(_PID,): _inactive_principal()}),
            TenantAuthorizationReason.PRINCIPAL_INACTIVE,
        ),
    )
    for principal_reader, expected_reason in cases:
        decision = _decision(
            principal_reader=principal_reader,
            membership_reader=membership_reader,
            role_reader=role_reader,
        )
        assert decision.reason is expected_reason
        with TestClient(
            _real_app(
                identity=_identity(),
                principal_reader=principal_reader,
                membership_reader=membership_reader,
                role_reader=role_reader,
            )
        ) as client:
            assert (
                client.get("/cert", headers={"X-Tenant-ID": _TENANT}).status_code
                == 403
            )
        _assert_read_only(principal_reader, membership_reader, role_reader)


def test_real_membership_denial_matrix() -> None:
    principal_reader = _RecordingReader({(_PID,): _active_principal()})
    role_reader = _RecordingReader()
    cases = (
        (
            _RecordingReader(
                failures={
                    (_PID, _TENANT): TenantMembershipNotFoundError(
                        "TENANT_MEMBERSHIP_NOT_FOUND"
                    )
                }
            ),
            TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND,
        ),
        (
            _RecordingReader(
                {
                    (_PID, _TENANT): _membership(
                        status=TenantMembershipStatus.SUSPENDED
                    )
                }
            ),
            TenantAuthorizationReason.MEMBERSHIP_INACTIVE,
        ),
        (
            _RecordingReader(
                {
                    (_PID, _TENANT): _membership(
                        status=TenantMembershipStatus.REVOKED
                    )
                }
            ),
            TenantAuthorizationReason.MEMBERSHIP_INACTIVE,
        ),
    )
    for membership_reader, expected_reason in cases:
        decision = _decision(
            principal_reader=principal_reader,
            membership_reader=membership_reader,
            role_reader=role_reader,
        )
        assert decision.reason is expected_reason
        with TestClient(
            _real_app(
                identity=_identity(),
                principal_reader=principal_reader,
                membership_reader=membership_reader,
                role_reader=role_reader,
            )
        ) as client:
            assert (
                client.get("/cert", headers={"X-Tenant-ID": _TENANT}).status_code
                == 403
            )
        _assert_read_only(principal_reader, membership_reader, role_reader)


def test_real_business_role_denial_matrix() -> None:
    principal_reader = _RecordingReader({(_PID,): _active_principal()})
    membership_reader = _RecordingReader({(_PID, _TENANT): _membership()})
    cases = (
        (
            _RecordingReader(),
            TenantAuthorizationReason.NO_ACTIVE_TENANT_BUSINESS_ROLE,
        ),
        (
            _RecordingReader(
                {
                    (_PID, _TENANT, "tenant_auditor"): _role("tenant_auditor"),
                    (_PID, _TENANT, "tenant_manager"): _role("tenant_manager"),
                }
            ),
            TenantAuthorizationReason.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES,
        ),
    )
    for role_reader, expected_reason in cases:
        decision = _decision(
            principal_reader=principal_reader,
            membership_reader=membership_reader,
            role_reader=role_reader,
        )
        assert decision.reason is expected_reason
        with TestClient(
            _real_app(
                identity=_identity(),
                principal_reader=principal_reader,
                membership_reader=membership_reader,
                role_reader=role_reader,
            )
        ) as client:
            assert (
                client.get("/cert", headers={"X-Tenant-ID": _TENANT}).status_code
                == 403
            )
        _assert_read_only(principal_reader, membership_reader, role_reader)


def test_real_final_authorization_denial_matrix() -> None:
    principal_reader = _RecordingReader({(_PID,): _active_principal()})
    membership_reader = _RecordingReader({(_PID, _TENANT): _membership()})

    permission_not_granted_reader = _RecordingReader(
        {(_PID, _TENANT, "tenant_auditor"): _role("tenant_auditor")}
    )
    inactive_values: dict[tuple[str, ...], object] = {
        (_PID, _TENANT, "tenant_auditor"): _role("tenant_auditor")
    }
    for role_id in _AUDIT_GRANTING_ROLES:
        inactive_values[(_PID, _TENANT, role_id)] = _role(
            role_id, status=RoleAssignmentStatus.REVOKED
        )
    inactive_reader = _RecordingReader(inactive_values)

    cases = (
        (
            permission_not_granted_reader,
            TenantAuthorizationReason.PERMISSION_NOT_GRANTED,
        ),
        (
            inactive_reader,
            TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE,
        ),
    )
    for role_reader, expected_reason in cases:
        decision = _decision(
            principal_reader=principal_reader,
            membership_reader=membership_reader,
            role_reader=role_reader,
        )
        assert decision.reason is expected_reason
        with TestClient(
            _real_app(
                identity=_identity(),
                principal_reader=principal_reader,
                membership_reader=membership_reader,
                role_reader=role_reader,
            )
        ) as client:
            assert (
                client.get("/cert", headers={"X-Tenant-ID": _TENANT}).status_code
                == 403
            )
        _assert_read_only(principal_reader, membership_reader, role_reader)


def test_real_financial_execution_is_prohibited() -> None:
    principal_reader = _RecordingReader({(_PID,): _active_principal()})
    membership_reader = _RecordingReader({(_PID, _TENANT): _membership()})
    role_reader = _RecordingReader(
        {(_PID, _TENANT, "tenant_auditor"): _role("tenant_auditor")}
    )
    decision = _decision(
        principal_reader=principal_reader,
        membership_reader=membership_reader,
        role_reader=role_reader,
        operation="financial_execution",
    )
    assert decision.authorized is False
    assert (
        decision.reason
        is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED
    )
    with TestClient(
        _real_app(
            identity=_identity(),
            principal_reader=principal_reader,
            membership_reader=membership_reader,
            role_reader=role_reader,
            operation="financial_execution",
        )
    ) as client:
        response = client.get("/cert", headers={"X-Tenant-ID": _TENANT})
    assert response.status_code == 403
    _assert_read_only(principal_reader, membership_reader, role_reader)


def test_real_principal_repository_outage_is_503() -> None:
    principal_reader = _RecordingReader(
        failures={
            (_PID,): PrincipalAuthorityRepositoryError(
                "PRINCIPAL_AUTHORITY_READ_FAILED"
            )
        }
    )
    membership_reader = _RecordingReader({(_PID, _TENANT): _membership()})
    role_reader = _RecordingReader()
    decision = _decision(
        principal_reader=principal_reader,
        membership_reader=membership_reader,
        role_reader=role_reader,
    )
    assert decision.reason is TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE
    with TestClient(
        _real_app(
            identity=_identity(),
            principal_reader=principal_reader,
            membership_reader=membership_reader,
            role_reader=role_reader,
        )
    ) as client:
        assert client.get("/cert", headers={"X-Tenant-ID": _TENANT}).status_code == 503


def test_real_membership_repository_outage_is_503() -> None:
    principal_reader = _RecordingReader({(_PID,): _active_principal()})
    membership_reader = _RecordingReader(
        failures={
            (_PID, _TENANT): TenantMembershipRepositoryError(
                "TENANT_MEMBERSHIP_READ_FAILED"
            )
        }
    )
    role_reader = _RecordingReader()
    decision = _decision(
        principal_reader=principal_reader,
        membership_reader=membership_reader,
        role_reader=role_reader,
    )
    assert decision.reason is TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE
    with TestClient(
        _real_app(
            identity=_identity(),
            principal_reader=principal_reader,
            membership_reader=membership_reader,
            role_reader=role_reader,
        )
    ) as client:
        assert client.get("/cert", headers={"X-Tenant-ID": _TENANT}).status_code == 503


def test_real_business_role_repository_outage_is_503() -> None:
    principal_reader = _RecordingReader({(_PID,): _active_principal()})
    membership_reader = _RecordingReader({(_PID, _TENANT): _membership()})
    failures = {
        (_PID, _TENANT, role_id): RoleAssignmentRepositoryError(
            "ROLE_ASSIGNMENT_READ_FAILED"
        )
        for role_id in TENANT_ROLES
    }
    role_reader = _RecordingReader(failures=failures)
    decision = _decision(
        principal_reader=principal_reader,
        membership_reader=membership_reader,
        role_reader=role_reader,
    )
    assert (
        decision.reason
        is TenantAuthorizationReason.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE
    )
    with TestClient(
        _real_app(
            identity=_identity(),
            principal_reader=principal_reader,
            membership_reader=membership_reader,
            role_reader=role_reader,
        )
    ) as client:
        assert client.get("/cert", headers={"X-Tenant-ID": _TENANT}).status_code == 503


def test_real_final_role_repository_outage_is_503() -> None:
    principal_reader = _RecordingReader({(_PID,): _active_principal()})
    membership_reader = _RecordingReader({(_PID, _TENANT): _membership()})
    values = {
        (_PID, _TENANT, "tenant_auditor"): _role("tenant_auditor"),
    }
    failures = {
        (_PID, _TENANT, role_id): RoleAssignmentRepositoryError(
            "ROLE_ASSIGNMENT_READ_FAILED"
        )
        for role_id in _AUDIT_GRANTING_ROLES
        if role_id not in TENANT_ROLES
    }
    role_reader = _RecordingReader(values=values, failures=failures)
    decision = _decision(
        principal_reader=principal_reader,
        membership_reader=membership_reader,
        role_reader=role_reader,
    )
    assert (
        decision.reason
        is TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE
    )
    with TestClient(
        _real_app(
            identity=_identity(),
            principal_reader=principal_reader,
            membership_reader=membership_reader,
            role_reader=role_reader,
        )
    ) as client:
        assert client.get("/cert", headers={"X-Tenant-ID": _TENANT}).status_code == 503


def test_projected_roles_and_permissions_are_not_authority() -> None:
    identity = _identity(
        roles=["ROOT", "GLOBAL_ROOT", "TENANT_ADMIN", "ADMIN", "AUDITOR"],
        permissions=["*", _AUDIT_PERMISSION],
    )
    principal_reader = _RecordingReader({(_PID,): _active_principal()})
    membership_reader = _RecordingReader({(_PID, _TENANT): _membership()})
    role_reader = _RecordingReader(
        {(_PID, _TENANT, "tenant_auditor"): _role("tenant_auditor")}
    )
    assert {"ROOT", "GLOBAL_ROOT", "TENANT_ADMIN", "ADMIN", "AUDITOR"} <= set(
        identity.roles
    )
    assert {"*", _AUDIT_PERMISSION} <= set(identity.permissions)
    with TestClient(
        _real_app(
            identity=identity,
            principal_reader=principal_reader,
            membership_reader=membership_reader,
            role_reader=role_reader,
        )
    ) as client:
        response = client.get("/cert", headers={"X-Tenant-ID": _TENANT})
    assert response.status_code == 403
    assert {"ROOT", "GLOBAL_ROOT", "TENANT_ADMIN", "ADMIN", "AUDITOR"} <= set(
        identity.roles
    )
    assert {"*", _AUDIT_PERMISSION} <= set(identity.permissions)


def test_identity_tenant_projection_is_not_authority() -> None:
    principal_reader, membership_reader, role_reader = _valid_readers()
    with TestClient(
        _real_app(
            identity=_identity(tenant_id="wrong-token-tenant"),
            principal_reader=principal_reader,
            membership_reader=membership_reader,
            role_reader=role_reader,
        )
    ) as client:
        positive = client.get("/cert", headers={"X-Tenant-ID": _TENANT})
    assert positive.status_code == 200
    assert positive.json()["tenant_id"] == _TENANT

    tenant_b = "tenant-b"
    membership_b = _RecordingReader()
    with TestClient(
        _real_app(
            identity=_identity(tenant_id=_TENANT),
            principal_reader=_RecordingReader({(_PID,): _active_principal()}),
            membership_reader=membership_b,
            role_reader=_RecordingReader(),
        )
    ) as client:
        negative = client.get("/cert", headers={"X-Tenant-ID": tenant_b})
    assert negative.status_code == 403


def test_x_tenant_id_is_scope_not_authority() -> None:
    principal_reader = _RecordingReader({(_PID,): _active_principal()})
    membership_reader = _RecordingReader()
    role_reader = _RecordingReader()
    with TestClient(
        _real_app(
            identity=_identity(),
            principal_reader=principal_reader,
            membership_reader=membership_reader,
            role_reader=role_reader,
        )
    ) as client:
        response = client.get("/cert", headers={"X-Tenant-ID": _TENANT})
    assert response.status_code == 403
    assert (_PID, _TENANT) in membership_reader.read_calls


def test_exact_authorization_wiring_uses_same_role_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    principal_repository = object()
    membership_repository = object()
    role_repository = object()
    captured: dict[str, object] = {}

    def capture(**kwargs: object) -> TenantAuthorizationDecision:
        captured.update(kwargs)
        return TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
            "tenant_auditor",
            "AUDITOR",
        )

    monkeypatch.setattr(boundary, "authorize_tenant_operation", capture)
    app = _real_app(
        identity=_identity(),
        principal_reader=principal_repository,
        membership_reader=membership_repository,
        role_reader=role_repository,
    )
    with TestClient(app) as client:
        response = client.get("/cert", headers={"X-Tenant-ID": _TENANT})
    assert response.status_code == 200
    assert captured["principal_id"] == _PID
    assert captured["tenant_id"] == _TENANT
    assert captured["permission_id"] == _AUDIT_PERMISSION
    assert captured["operation"] == _AUDIT_OPERATION
    assert captured["principal_repository"] is principal_repository
    assert captured["membership_repository"] is membership_repository
    assert captured["business_role_repository"] is role_repository
    assert captured["role_assignment_repository"] is role_repository
    assert (
        captured["business_role_repository"]
        is captured["role_assignment_repository"]
    )


def test_canonical_dependency_contract_and_no_transport_authority() -> None:
    parameters = inspect.signature(boundary.RequireTenantAuthorization.__call__).parameters
    assert parameters["identity"].default.dependency is boundary.get_current_identity
    assert (
        parameters["principal_repository"].default.dependency
        is boundary.get_principal_authority_repository
    )
    assert (
        parameters["membership_repository"].default.dependency
        is boundary.get_tenant_membership_repository
    )
    assert (
        parameters["role_assignment_repository"].default.dependency
        is boundary.get_role_assignment_repository
    )
    dependencies = {
        parameter.default.dependency
        for parameter in parameters.values()
        if hasattr(parameter.default, "dependency")
    }
    assert get_current_tenant_identity not in dependencies
    forbidden = {
        "caller_role",
        "caller_roles",
        "role",
        "roles",
        "jwt_role",
        "jwt_roles",
        "jwt_permissions",
        "node_role",
        "node_roles",
        "trusted_role",
        "trusted_roles",
        "authorization_role",
        "authorization_roles",
        "permissions",
        "authorization_header",
        "auth_header",
    }
    assert forbidden.isdisjoint(parameters)


def test_inconsistent_decisions_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    decisions = (
        TenantAuthorizationDecision(
            True, TenantAuthorizationReason.PERMISSION_NOT_GRANTED
        ),
        TenantAuthorizationDecision(False, TenantAuthorizationReason.AUTHORIZED),
    )
    for decision in decisions:
        monkeypatch.setattr(
            boundary,
            "authorize_tenant_operation",
            lambda **_kwargs: decision,
        )
        app = _real_app(
            identity=_identity(),
            principal_reader=object(),
            membership_reader=object(),
            role_reader=object(),
        )
        with TestClient(app) as client:
            response = client.get("/cert", headers={"X-Tenant-ID": _TENANT})
        assert response.status_code == 503


def test_reason_sets_are_exact_and_explicit() -> None:
    expected_unavailable = frozenset(
        {
            TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE,
            TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE,
            TenantAuthorizationReason.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE,
            TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE,
        }
    )
    expected_denied = frozenset(
        {
            TenantAuthorizationReason.INVALID_INPUT,
            TenantAuthorizationReason.PRINCIPAL_NOT_FOUND,
            TenantAuthorizationReason.PRINCIPAL_INACTIVE,
            TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND,
            TenantAuthorizationReason.MEMBERSHIP_INACTIVE,
            TenantAuthorizationReason.NO_ACTIVE_TENANT_BUSINESS_ROLE,
            TenantAuthorizationReason.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES,
            TenantAuthorizationReason.PERMISSION_UNKNOWN,
            TenantAuthorizationReason.PERMISSION_NOT_CANONICAL,
            TenantAuthorizationReason.PERMISSION_NAMESPACE_MISMATCH,
            TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH,
            TenantAuthorizationReason.PERMISSION_NOT_GRANTED,
            TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE,
            TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE,
            TenantAuthorizationReason.SYSTEM_AUTHORITY_REQUIRED,
            TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED,
        }
    )
    assert boundary._UNAVAILABLE == expected_unavailable
    assert boundary._DENIED == expected_denied
    assert TenantAuthorizationReason.AUTHORIZED not in boundary._UNAVAILABLE
    assert TenantAuthorizationReason.AUTHORIZED not in boundary._DENIED
    assert boundary._DENIED.isdisjoint(boundary._UNAVAILABLE)



def test_authorization_is_read_only_for_success_denial_and_financial() -> None:
    scenarios: list[
        tuple[
            _RecordingReader,
            _RecordingReader,
            _RecordingReader,
            str,
            int,
        ]
    ] = []

    positive = _valid_readers()
    scenarios.append((*positive, _AUDIT_OPERATION, 200))

    denial = (
        _RecordingReader({(_PID,): _active_principal()}),
        _RecordingReader({(_PID, _TENANT): _membership()}),
        _RecordingReader(
            {(_PID, _TENANT, "tenant_auditor"): _role("tenant_auditor")}
        ),
    )
    scenarios.append((*denial, _AUDIT_OPERATION, 403))

    financial = (
        _RecordingReader({(_PID,): _active_principal()}),
        _RecordingReader({(_PID, _TENANT): _membership()}),
        _RecordingReader(
            {(_PID, _TENANT, "tenant_auditor"): _role("tenant_auditor")}
        ),
    )
    scenarios.append((*financial, "financial_execution", 403))

    for principal_reader, membership_reader, role_reader, operation, status_code in scenarios:
        with TestClient(
            _real_app(
                identity=_identity(),
                principal_reader=principal_reader,
                membership_reader=membership_reader,
                role_reader=role_reader,
                operation=operation,
            )
        ) as client:
            response = client.get("/cert", headers={"X-Tenant-ID": _TENANT})
        assert response.status_code == status_code
        _assert_read_only(principal_reader, membership_reader, role_reader)


def test_primary_contract_version_and_expected_blob_constant() -> None:
    assert VERSION == "v1.0.0-TENANT-AUTHORIZATION-HTTP-CERT"
    assert EXPECTED_PRIMARY_BLOB == "11f4033f16b3bffd08a3b2e0789a7fa326fba942"
    assert boundary.VERSION == "v1.0.0-TENANT-AUTHORIZATION-HTTP"


# ARTIFACT: test_tenant_authorization_http.py
# VERSION: v1.0.0-TENANT-AUTHORIZATION-HTTP-CERT
# AUTHORITY BOUNDARY: test-local HTTP dependency translation only
# TENANT POSTURE: explicit X-Tenant-ID scope; no projection authority
# FAIL-CLOSED POSTURE: only AUTHORIZED succeeds; unavailable maps to 503
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
