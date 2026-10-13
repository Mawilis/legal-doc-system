"""Direct certificate for W3C tenant workforce leaver orchestration."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)
from tools.eos.workforce.orchestration import (
    tenant_workforce_leaver_orchestrator as orchestrator,
)


AT = datetime(
    2026,
    10,
    13,
    6,
    0,
    tzinfo=timezone.utc,
)

TENANT = "tenant-w3c"
PRINCIPAL = "principal-w3c"
RELATIONSHIP = "employment-w3c"


class ActiveSession:
    in_transaction = True


class InactiveSession:
    in_transaction = False


def relationship(
    *,
    revision: int = 1,
    status: WorkforceRelationshipStatus = (
        WorkforceRelationshipStatus.ACTIVE
    ),
    previous: WorkforceRelationship | None = None,
    scope_kind: WorkforceScopeKind = WorkforceScopeKind.TENANT,
    scope_id: str = TENANT,
    principal_id: str = PRINCIPAL,
    relationship_id: str = RELATIONSHIP,
    status_effective_at: datetime = AT,
    reason_reference: str = "join-ref",
) -> WorkforceRelationship:
    return WorkforceRelationship(
        relationship_id=relationship_id,
        revision=revision,
        scope_kind=scope_kind,
        scope_id=scope_id,
        principal_id=principal_id,
        relationship_type=WorkforceRelationshipType.EMPLOYEE,
        status=status,
        effective_from=AT,
        effective_until=(
            status_effective_at
            if status is WorkforceRelationshipStatus.ENDED
            else None
        ),
        status_effective_at=status_effective_at,
        reason_reference=reason_reference,
        supersedes_fingerprint=(
            None
            if previous is None
            else previous.fingerprint
        ),
    )


class Harness:
    def __init__(
        self,
        *,
        first_status: WorkforceRelationshipStatus = (
            WorkforceRelationshipStatus.ACTIVE
        ),
    ) -> None:
        self.first = relationship(
            status=first_status,
        )
        self.history = [self.first]

        self.membership = TenantMembershipAuthority(
            PRINCIPAL,
            TENANT,
            TenantMembershipStatus.ACTIVE,
            0,
        )

        self.assignments = [
            RoleAssignmentAuthority(
                PRINCIPAL,
                TENANT,
                "LEGAL_PARTNER",
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            RoleAssignmentAuthority(
                PRINCIPAL,
                TENANT,
                "AUDITOR",
                RoleAssignmentStatus.REVOKED,
                4,
            ),
        ]

        self.sessions = 3
        self.refresh = 2

        self.calls: list[
            tuple[str, object]
        ] = []


def patch(
    monkeypatch: pytest.MonkeyPatch,
    harness: Harness,
) -> Any:
    def list_history(
        scope_kind: str,
        scope_id: str,
        relationship_id: str,
        *,
        collection: object,
        session: object,
    ) -> tuple[WorkforceRelationship, ...]:
        assert scope_kind == "TENANT"
        assert collection == "workforce"
        assert session is ACTIVE_SESSION
        return tuple(harness.history)

    def persist_revision(
        value: WorkforceRelationship,
        *,
        collection: object,
        session: object,
    ) -> WorkforceRelationship:
        assert collection == "workforce"
        assert session is ACTIVE_SESSION
        harness.history.append(
            value
        )
        harness.calls.append(
            ("workforce", value)
        )
        return value

    def resolve_membership(
        principal_id: str,
        tenant_id: str,
        collection: object,
        *,
        session: object,
    ) -> TenantMembershipAuthority:
        assert collection == "membership"
        assert session is ACTIVE_SESSION
        return harness.membership

    def cas_membership(
        value: TenantMembershipAuthority,
        expected_revision: int,
        collection: object,
        *,
        session: object,
    ) -> TenantMembershipAuthority:
        assert expected_revision == harness.membership.revision
        assert collection == "membership"
        assert session is ACTIVE_SESSION
        harness.membership = value
        harness.calls.append(
            ("membership", value)
        )
        return value

    def list_assignments(
        principal_id: str,
        tenant_id: str,
        collection: object,
        *,
        session: object,
    ) -> tuple[RoleAssignmentAuthority, ...]:
        assert collection == "roles"
        assert session is ACTIVE_SESSION
        return tuple(
            harness.assignments
        )

    def cas_assignment(
        value: RoleAssignmentAuthority,
        expected_revision: int,
        collection: object,
        *,
        session: object,
    ) -> RoleAssignmentAuthority:
        assert collection == "roles"
        assert session is ACTIVE_SESSION

        index = next(
            index
            for index, item
            in enumerate(harness.assignments)
            if item.role_id == value.role_id
        )

        assert (
            harness.assignments[index].revision
            == expected_revision
        )

        harness.assignments[index] = value
        harness.calls.append(
            ("role", value)
        )
        return value

    monkeypatch.setattr(
        orchestrator.workforce_relationship_registry,
        "list_history",
        list_history,
    )
    monkeypatch.setattr(
        orchestrator.workforce_relationship_registry,
        "persist_revision",
        persist_revision,
    )
    monkeypatch.setattr(
        orchestrator.TenantMembershipRepository,
        "resolve",
        resolve_membership,
    )
    monkeypatch.setattr(
        orchestrator.TenantMembershipRepository,
        "compare_and_swap",
        cas_membership,
    )
    monkeypatch.setattr(
        orchestrator.RoleAssignmentRepository,
        "list_assignments",
        list_assignments,
    )
    monkeypatch.setattr(
        orchestrator.RoleAssignmentRepository,
        "compare_and_swap",
        cas_assignment,
    )

    class Auth:
        def revoke_sessions(
            self,
            tenant_id: str,
            user_id: str,
            *,
            session: object,
        ) -> int:
            assert tenant_id == TENANT
            assert user_id == PRINCIPAL
            assert session is ACTIVE_SESSION
            harness.calls.append(
                ("sessions", tenant_id)
            )
            value = harness.sessions
            harness.sessions = 0
            return value

        def revoke_refresh_tokens(
            self,
            tenant_id: str,
            user_id: str,
            *,
            session: object,
        ) -> int:
            assert tenant_id == TENANT
            assert user_id == PRINCIPAL
            assert session is ACTIVE_SESSION
            harness.calls.append(
                ("refresh", tenant_id)
            )
            value = harness.refresh
            harness.refresh = 0
            return value

    return Auth()


ACTIVE_SESSION = ActiveSession()


def invoke(
    monkeypatch: pytest.MonkeyPatch,
    harness: Harness,
    *,
    ended_at: datetime | object = AT + timedelta(hours=1),
    reason: str | object = "termination-ref",
    tenant: str | object = TENANT,
    principal: str | object = PRINCIPAL,
    relationship_id: str | object = RELATIONSHIP,
    session: object = ACTIVE_SESSION,
) -> orchestrator.TenantWorkforceLeaverResult:
    auth = patch(
        monkeypatch,
        harness,
    )

    return orchestrator.close_tenant_workforce_access(
        tenant_id=tenant,
        principal_id=principal,
        relationship_id=relationship_id,
        ended_at=ended_at,
        reason_reference=reason,
        workforce_collection="workforce",
        membership_collection="membership",
        role_assignment_collection="roles",
        auth_registry=auth,
        session=session,
    )


def test_active_leaver_closes_exact_tenant_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    h = Harness()

    result = invoke(
        monkeypatch,
        h,
    )

    assert (
        result.relationship.status
        is WorkforceRelationshipStatus.ENDED
    )
    assert (
        result.relationship.scope_kind
        is WorkforceScopeKind.TENANT
    )
    assert result.relationship.scope_id == TENANT
    assert result.relationship.principal_id == PRINCIPAL

    assert (
        result.membership.status
        is TenantMembershipStatus.REVOKED
    )

    assert result.revoked_role_ids == (
        "LEGAL_PARTNER",
    )

    assert (
        h.assignments[0].status
        is RoleAssignmentStatus.REVOKED
    )
    assert (
        h.assignments[1].status
        is RoleAssignmentStatus.REVOKED
    )

    assert result.revoked_session_count == 3
    assert result.revoked_refresh_token_count == 2
    assert result.exact_replay is False

    assert [
        kind
        for kind, _value in h.calls
    ] == [
        "workforce",
        "membership",
        "role",
        "sessions",
        "refresh",
    ]


def test_suspended_relationship_can_end(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    h = Harness(
        first_status=WorkforceRelationshipStatus.SUSPENDED,
    )

    result = invoke(
        monkeypatch,
        h,
    )

    assert (
        result.relationship.status
        is WorkforceRelationshipStatus.ENDED
    )


def test_exact_replay_does_not_append_or_revoke_roles_again(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    h = Harness()

    first = invoke(
        monkeypatch,
        h,
    )

    assert first.exact_replay is False

    h.calls.clear()

    second = invoke(
        monkeypatch,
        h,
    )

    assert second.exact_replay is True
    assert second.revoked_role_ids == ()
    assert second.revoked_session_count == 0
    assert second.revoked_refresh_token_count == 0

    assert [
        kind
        for kind, _value in h.calls
    ] == [
        "sessions",
        "refresh",
    ]


def test_divergent_ended_replay_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    h = Harness()

    invoke(
        monkeypatch,
        h,
    )

    with pytest.raises(
        orchestrator.TenantWorkforceLeaverConflictError,
        match="DIVERGENT_ENDED_REPLAY",
    ):
        invoke(
            monkeypatch,
            h,
            reason="different-reason",
        )


def test_scope_mismatch_rejected_before_iam(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    h = Harness()

    h.history = [
        relationship(
            scope_id="tenant-other",
        )
    ]

    with pytest.raises(
        orchestrator.TenantWorkforceLeaverInputError,
        match="SCOPE_OR_PRINCIPAL_MISMATCH",
    ):
        invoke(
            monkeypatch,
            h,
        )

    assert h.calls == []


def test_principal_mismatch_rejected_before_iam(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    h = Harness()

    h.history = [
        relationship(
            principal_id="principal-other",
        )
    ]

    with pytest.raises(
        orchestrator.TenantWorkforceLeaverInputError,
        match="SCOPE_OR_PRINCIPAL_MISMATCH",
    ):
        invoke(
            monkeypatch,
            h,
        )

    assert h.calls == []


def test_platform_relationship_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    h = Harness()

    h.history = [
        relationship(
            scope_kind=WorkforceScopeKind.PLATFORM,
            scope_id="wilsy-platform",
        )
    ]

    with pytest.raises(
        orchestrator.TenantWorkforceLeaverInputError,
        match="SCOPE_OR_PRINCIPAL_MISMATCH",
    ):
        invoke(
            monkeypatch,
            h,
        )

    assert h.calls == []


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        " tenant-w3c",
        "tenant-w3c ",
    ],
)
def test_invalid_tenant_rejected(
    monkeypatch: pytest.MonkeyPatch,
    value: object,
) -> None:
    h = Harness()

    with pytest.raises(
        orchestrator.TenantWorkforceLeaverInputError,
    ):
        invoke(
            monkeypatch,
            h,
            tenant=value,
        )


def test_inactive_transaction_rejected_before_reads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    h = Harness()

    auth = patch(
        monkeypatch,
        h,
    )

    with pytest.raises(
        orchestrator.TenantWorkforceLeaverTransactionRequiredError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        orchestrator.close_tenant_workforce_access(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            relationship_id=RELATIONSHIP,
            ended_at=AT + timedelta(hours=1),
            reason_reference="termination-ref",
            workforce_collection="workforce",
            membership_collection="membership",
            role_assignment_collection="roles",
            auth_registry=auth,
            session=InactiveSession(),
        )

    assert h.calls == []


def test_future_latest_status_prevents_backdated_end(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    h = Harness()

    future = relationship(
        revision=2,
        status=WorkforceRelationshipStatus.SUSPENDED,
        previous=h.first,
        status_effective_at=AT + timedelta(hours=4),
        reason_reference="future-suspension",
    )

    h.history.append(
        future
    )

    with pytest.raises(
        orchestrator.TenantWorkforceLeaverConflictError,
        match="END_BEFORE_LATEST_STATUS_EFFECTIVE_AT",
    ):
        invoke(
            monkeypatch,
            h,
            ended_at=AT + timedelta(hours=2),
        )

    assert h.calls == []


def test_module_contains_no_global_principal_mutation() -> None:
    source = orchestrator.__file__

    assert source is not None

    text = Path(source).read_text()

    assert "PrincipalAuthorityRepository" not in text
    assert "PrincipalStatus.REVOKED" not in text
    assert "PrincipalStatus.SUSPENDED" not in text
    assert "financial_execution" not in text.lower()
