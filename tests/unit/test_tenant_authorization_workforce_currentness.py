\
"""Direct W3D-R8B workforce-currentness authorization certificate."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipStatus,
)
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)


PID = "principal-r8b"
TENANT = "tenant-r8b"


class _Principal:
    status = PrincipalStatus.ACTIVE


class _Membership:
    status = TenantMembershipStatus.ACTIVE


class _Business:
    def __init__(
        self,
        role_id: str,
        status: RoleAssignmentStatus,
    ) -> None:
        self.role_id = role_id
        self.status = status


class _Assignment:
    def __init__(
        self,
        status: RoleAssignmentStatus = (
            RoleAssignmentStatus.ACTIVE
        ),
    ) -> None:
        self.status = status


class PrincipalRepository:
    def resolve(
        self,
        principal_id: str,
        *,
        session: object = None,
    ) -> object:
        assert principal_id == PID
        return _Principal()


class MembershipRepository:
    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: object = None,
    ) -> object:
        assert principal_id == PID
        assert tenant_id == TENANT
        return _Membership()


class BusinessRoleRepository:
    def __init__(
        self,
        active_role: str,
    ) -> None:
        self.active_role = active_role

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: object = None,
    ) -> object:
        assert principal_id == PID
        assert tenant_id == TENANT

        return _Business(
            role_id,
            (
                RoleAssignmentStatus.ACTIVE
                if role_id == self.active_role
                else RoleAssignmentStatus.REVOKED
            ),
        )


class AuthorizationRoleRepository:
    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: object = None,
    ) -> object:
        assert principal_id == PID
        assert tenant_id == TENANT
        assert role_id == "HR_DIRECTOR"
        return _Assignment()


class ActiveSession:
    in_transaction = True


class InactiveSession:
    in_transaction = False


class Cursor:
    def __init__(
        self,
        rows: tuple[dict[str, Any], ...],
    ) -> None:
        self._rows = rows

    def sort(
        self,
        *_args: object,
        **_kwargs: object,
    ) -> "Cursor":
        return self

    def __iter__(self):
        return iter(self._rows)


class WorkforceCollection:
    def __init__(
        self,
        rows: tuple[dict[str, Any], ...],
    ) -> None:
        self.rows = rows
        self.reads = 0

    def find(
        self,
        query: dict[str, Any],
        *,
        session: object,
    ) -> Cursor:
        assert query == {
            "scope_kind": "TENANT",
            "scope_id": TENANT,
            "principal_id": PID,
        }
        assert session is not None
        self.reads += 1
        return Cursor(self.rows)


def _workforce_row(
    *,
    status: WorkforceRelationshipStatus,
) -> dict[str, Any]:
    value = WorkforceRelationship(
        relationship_id="relationship-r8b",
        revision=1,
        scope_kind=WorkforceScopeKind.TENANT,
        scope_id=TENANT,
        principal_id=PID,
        relationship_type=WorkforceRelationshipType.EMPLOYEE,
        status=status,
        effective_from=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        effective_until=None,
        status_effective_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        reason_reference="r8b-test",
        supersedes_fingerprint=None,
    )
    return value.to_dict()


def _authorize(
    *,
    permission: str,
    operation: str,
    business_role: str,
    authorization_role: str,
    session: object = None,
    collection: object = None,
):
    class Role(AuthorizationRoleRepository):
        def resolve(
            self,
            principal_id: str,
            tenant_id: str,
            role_id: str,
            *,
            session: object = None,
        ) -> object:
            assert principal_id == PID
            assert tenant_id == TENANT

            return _Assignment(
                (
                    RoleAssignmentStatus.ACTIVE
                    if role_id == authorization_role
                    else RoleAssignmentStatus.REVOKED
                )
            )

    return authorize_tenant_operation(
        principal_id=PID,
        tenant_id=TENANT,
        permission_id=permission,
        operation=operation,
        principal_repository=PrincipalRepository(),
        membership_repository=MembershipRepository(),
        business_role_repository=BusinessRoleRepository(
            business_role
        ),
        role_assignment_repository=Role(),
        session=session,
        workforce_relationship_collection=collection,
    )


def test_non_workforce_permission_remains_sessionless_and_does_not_read_workforce() -> None:
    decision = _authorize(
        permission="audit:read",
        operation="audit_read",
        business_role="tenant_auditor",
        authorization_role="AUDITOR",
    )

    assert decision.authorized is True
    assert (
        decision.reason
        is TenantAuthorizationReason.AUTHORIZED
    )


def test_workforce_required_permission_denies_without_transaction() -> None:
    decision = _authorize(
        permission="hr:employee_relation:write",
        operation="hr_employee_relation_write",
        business_role="tenant_hr_director",
        authorization_role="HR_DIRECTOR",
        collection=WorkforceCollection(
            (_workforce_row(
                status=WorkforceRelationshipStatus.ACTIVE,
            ),)
        ),
    )

    assert decision.authorized is False
    assert (
        decision.reason
        is TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE
    )


def test_workforce_required_permission_denies_inactive_transaction() -> None:
    decision = _authorize(
        permission="hr:employee_relation:write",
        operation="hr_employee_relation_write",
        business_role="tenant_hr_director",
        authorization_role="HR_DIRECTOR",
        session=InactiveSession(),
        collection=WorkforceCollection(
            (_workforce_row(
                status=WorkforceRelationshipStatus.ACTIVE,
            ),)
        ),
    )

    assert decision.authorized is False
    assert (
        decision.reason
        is TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE
    )


def test_workforce_required_permission_denies_without_collection() -> None:
    decision = _authorize(
        permission="hr:employee_relation:write",
        operation="hr_employee_relation_write",
        business_role="tenant_hr_director",
        authorization_role="HR_DIRECTOR",
        session=ActiveSession(),
    )

    assert decision.authorized is False
    assert (
        decision.reason
        is TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE
    )


def test_absent_workforce_history_is_not_current_not_outage() -> None:
    decision = _authorize(
        permission="hr:employee_relation:write",
        operation="hr_employee_relation_write",
        business_role="tenant_hr_director",
        authorization_role="HR_DIRECTOR",
        session=ActiveSession(),
        collection=WorkforceCollection(()),
    )

    assert decision.authorized is False
    assert (
        decision.reason
        is TenantAuthorizationReason.WORKFORCE_NOT_CURRENT
    )


def test_suspended_workforce_relationship_denies_before_final_role_grant() -> None:
    class ForbiddenRoleRepository:
        def resolve(self, *args: object, **kwargs: object) -> object:
            raise AssertionError(
                "final role must not be read after workforce denial"
            )

    decision = authorize_tenant_operation(
        principal_id=PID,
        tenant_id=TENANT,
        permission_id="hr:employee_relation:write",
        operation="hr_employee_relation_write",
        principal_repository=PrincipalRepository(),
        membership_repository=MembershipRepository(),
        business_role_repository=BusinessRoleRepository(
            "tenant_hr_director"
        ),
        role_assignment_repository=ForbiddenRoleRepository(),
        session=ActiveSession(),
        workforce_relationship_collection=WorkforceCollection(
            (_workforce_row(
                status=WorkforceRelationshipStatus.SUSPENDED,
            ),)
        ),
    )

    assert decision.authorized is False
    assert (
        decision.reason
        is TenantAuthorizationReason.WORKFORCE_NOT_CURRENT
    )


def test_active_workforce_relationship_allows_normal_iam_to_continue() -> None:
    collection = WorkforceCollection(
        (_workforce_row(
            status=WorkforceRelationshipStatus.ACTIVE,
        ),)
    )

    decision = _authorize(
        permission="hr:employee_relation:write",
        operation="hr_employee_relation_write",
        business_role="tenant_hr_director",
        authorization_role="HR_DIRECTOR",
        session=ActiveSession(),
        collection=collection,
    )

    assert decision.authorized is True
    assert (
        decision.reason
        is TenantAuthorizationReason.AUTHORIZED
    )
    assert collection.reads == 1


def test_client_permission_remains_non_workforce() -> None:
    decision = _authorize(
        permission="legal_operations:client_matter:read",
        operation="legal_client_matter_read",
        business_role="tenant_legal_client",
        authorization_role="LEGAL_CLIENT",
    )

    assert decision.authorized is True
    assert (
        decision.reason
        is TenantAuthorizationReason.AUTHORIZED
    )
