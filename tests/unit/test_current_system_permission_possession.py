"""
TITLE:
    WILSY OS Current System Permission Possession Direct Certificate

VERSION:
    v1.0.0-P4-R4-D9-CURRENT-SYSTEM-PERMISSION-POSSESSION-CERT

PURPOSE:
    Certify current ACTIVE principal + current ACTIVE exact SYSTEM assignment
    using a real D7 registry instance over a bounded fake collection.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from pymongo.client_session import ClientSession

import tools.eos.auth.current_system_permission_possession as module
from tools.eos.auth.current_system_permission_possession import (
    CurrentSystemPermissionPossessionError,
    CurrentSystemPermissionPossessionResolver,
)
from tools.eos.auth.principal_authority import (
    PrincipalAuthority,
)
from tools.eos.auth.principal_status import (
    PrincipalStatus,
)
from tools.eos.auth.system_permission_assignment import (
    SystemPermissionAssignment,
)
from tools.eos.auth.system_permission_assignment_registry import (
    SystemPermissionAssignmentRegistry,
)


NOW = datetime(
    2026,
    10,
    14,
    17,
    30,
    tzinfo=timezone.utc,
)

PERMISSION = "privileged_activation:issue"


class FakeCollection:
    def __init__(
        self,
        rows: list[dict[str, object]] | None = None,
    ) -> None:
        self.rows = list(
            rows or []
        )

    @staticmethod
    def _matches(
        row: dict[str, object],
        query: dict[str, object],
    ) -> bool:
        return all(
            row.get(key) == value
            for key, value in query.items()
        )

    def find(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> list[dict[str, object]]:
        del session

        return [
            deepcopy(row)
            for row in self.rows
            if self._matches(
                row,
                query,
            )
        ]

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, object] | None:
        del session

        for row in self.rows:
            if self._matches(
                row,
                query,
            ):
                return deepcopy(row)

        return None


def assignment(
    *,
    assignment_id: str = "assignment-a",
    principal_id: str = "principal-a",
) -> SystemPermissionAssignment:
    return SystemPermissionAssignment.assign(
        assignment_id=assignment_id,
        principal_id=principal_id,
        permission_id=PERMISSION,
        assigned_by_principal_id="grantor-a",
        assigned_at=NOW,
        assignment_evidence_reference="evidence-a",
    )


def row(
    value: SystemPermissionAssignment,
) -> dict[str, object]:
    payload = value.authority_payload()

    payload["assigned_at"] = (
        value.assigned_at
    )
    payload["revoked_at"] = (
        value.revoked_at
    )

    return {
        **payload,
        "assignment_fingerprint":
            value.assignment_fingerprint,
        "_operation_kind":
            "ASSIGN",
        "_operation_idempotency_key":
            "create-a",
    }


def resolver(
    value: SystemPermissionAssignment | None,
) -> tuple[
    CurrentSystemPermissionPossessionResolver,
    SystemPermissionAssignmentRegistry,
    FakeCollection,
]:
    rows = (
        []
        if value is None
        else [row(value)]
    )

    collection = FakeCollection(
        rows
    )

    registry = (
        SystemPermissionAssignmentRegistry(
            collection
        )
    )

    instance = (
        CurrentSystemPermissionPossessionResolver(
            principal_collection=object(),
            assignment_registry=registry,
        )
    )

    return (
        instance,
        registry,
        collection,
    )


def test_active_principal_and_current_assignment_allow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = assignment()

    instance, _, _ = resolver(
        value
    )

    session = Mock(
        spec=ClientSession
    )

    observed: list[
        ClientSession | None
    ] = []

    def get(
        principal_id: str,
        collection: object = None,
        *,
        session: ClientSession | None = None,
    ) -> PrincipalAuthority:
        assert collection is not None

        observed.append(
            session
        )

        return PrincipalAuthority(
            principal_id,
            PrincipalStatus.ACTIVE,
            4,
        )

    monkeypatch.setattr(
        module.PrincipalAuthorityRepository,
        "get",
        staticmethod(get),
    )

    assert instance.resolve(
        principal_id="principal-a",
        permission_id=PERMISSION,
        session=session,
    ) == value

    assert observed == [
        session
    ]


@pytest.mark.parametrize(
    "status",
    tuple(
        status
        for status in PrincipalStatus
        if status is not PrincipalStatus.ACTIVE
    ),
)
def test_nonactive_principal_denies(
    monkeypatch: pytest.MonkeyPatch,
    status: PrincipalStatus,
) -> None:
    instance, _, _ = resolver(
        assignment()
    )

    def get(
        principal_id: str,
        collection: object = None,
        *,
        session: ClientSession | None = None,
    ) -> PrincipalAuthority:
        del collection
        del session

        return PrincipalAuthority(
            principal_id,
            status,
            8,
        )

    monkeypatch.setattr(
        module.PrincipalAuthorityRepository,
        "get",
        staticmethod(get),
    )

    assert instance.resolve(
        principal_id="principal-a",
        permission_id=PERMISSION,
    ) is None


def test_missing_assignment_denies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    instance, _, _ = resolver(
        None
    )

    def get(
        principal_id: str,
        collection: object = None,
        *,
        session: ClientSession | None = None,
    ) -> PrincipalAuthority:
        del collection
        del session

        return PrincipalAuthority(
            principal_id,
            PrincipalStatus.ACTIVE,
            1,
        )

    monkeypatch.setattr(
        module.PrincipalAuthorityRepository,
        "get",
        staticmethod(get),
    )

    assert instance.possesses(
        principal_id="principal-a",
        permission_id=PERMISSION,
    ) is False


@pytest.mark.parametrize(
    "permission_id",
    (
        "legal_operations:evidence:write",
        "tenant:profile:read",
        "artifacts:read",
        "not:a:real:permission",
    ),
)
def test_non_system_or_unknown_permission_rejects(
    permission_id: str,
) -> None:
    instance, _, _ = resolver(
        None
    )

    with pytest.raises(
        CurrentSystemPermissionPossessionError
    ):
        instance.resolve(
            principal_id="principal-a",
            permission_id=permission_id,
        )


def test_exact_clientsession_is_passed_to_principal_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = assignment()

    instance, _, _ = resolver(
        value
    )

    session = Mock(
        spec=ClientSession
    )

    seen: list[
        ClientSession | None
    ] = []

    def get(
        principal_id: str,
        collection: object = None,
        *,
        session: ClientSession | None = None,
    ) -> PrincipalAuthority:
        del principal_id

        assert collection is not None

        seen.append(
            session
        )

        return PrincipalAuthority(
            "principal-a",
            PrincipalStatus.ACTIVE,
            2,
        )

    monkeypatch.setattr(
        module.PrincipalAuthorityRepository,
        "get",
        staticmethod(get),
    )

    assert instance.resolve(
        principal_id="principal-a",
        permission_id=PERMISSION,
        session=session,
    ) == value

    assert seen == [
        session
    ]


def test_principal_binding_mismatch_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    instance, _, _ = resolver(
        assignment()
    )

    def get(
        principal_id: str,
        collection: object = None,
        *,
        session: ClientSession | None = None,
    ) -> PrincipalAuthority:
        del principal_id
        del collection
        del session

        return PrincipalAuthority(
            "principal-b",
            PrincipalStatus.ACTIVE,
            1,
        )

    monkeypatch.setattr(
        module.PrincipalAuthorityRepository,
        "get",
        staticmethod(get),
    )

    with pytest.raises(
        CurrentSystemPermissionPossessionError,
        match="PRINCIPAL_BINDING_INVALID",
    ):
        instance.resolve(
            principal_id="principal-a",
            permission_id=PERMISSION,
        )


def test_same_clientsession_reaches_real_registry_collection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = assignment()

    class SessionCollection(
        FakeCollection
    ):
        def __init__(self) -> None:
            super().__init__(
                [row(value)]
            )
            self.sessions: list[
                object
            ] = []

        def find(
            self,
            query: dict[str, object],
            *,
            session: object = None,
        ) -> list[dict[str, object]]:
            self.sessions.append(
                session
            )
            return super().find(
                query,
                session=session,
            )

    collection = (
        SessionCollection()
    )

    registry = (
        SystemPermissionAssignmentRegistry(
            collection
        )
    )

    instance = (
        CurrentSystemPermissionPossessionResolver(
            principal_collection=object(),
            assignment_registry=registry,
        )
    )

    session = Mock(
        spec=ClientSession
    )

    principal_sessions: list[
        ClientSession | None
    ] = []

    def get(
        principal_id: str,
        collection: object = None,
        *,
        session: ClientSession | None = None,
    ) -> PrincipalAuthority:
        assert collection is not None

        principal_sessions.append(
            session
        )

        return PrincipalAuthority(
            principal_id,
            PrincipalStatus.ACTIVE,
            1,
        )

    monkeypatch.setattr(
        module.PrincipalAuthorityRepository,
        "get",
        staticmethod(get),
    )

    assert instance.resolve(
        principal_id="principal-a",
        permission_id=PERMISSION,
        session=session,
    ) == value

    assert principal_sessions == [
        session
    ]

    assert collection.sessions
    assert all(
        observed is session
        for observed
        in collection.sessions
    )


def test_no_authority_creation_surface() -> None:
    instance, _, _ = resolver(
        None
    )

    for forbidden in (
        "assign",
        "grant",
        "revoke",
        "activate",
        "issue",
        "create",
        "persist",
        "authorize_p4",
        "break_glass",
        "execute_financial",
    ):
        assert not hasattr(
            instance,
            forbidden,
        )


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# ARTIFACT: tests/unit/test_current_system_permission_possession.py
# VERSION: v1.0.0-P4-R4-D9-CURRENT-SYSTEM-PERMISSION-POSSESSION-CERT
# REAL D7 REGISTRY INSTANCE: YES
# FAKE COLLECTION ONLY: YES
# CURRENT PRINCIPAL: REQUIRED
# CURRENT SYSTEM ASSIGNMENT: REQUIRED
# SESSION TYPE: ClientSession | None
# SAME CALLER SESSION: REQUIRED
# WRITES: NONE
# P4 ISSUANCE AUTHORIZATION: NONE
# PRIVILEGED ACTIVATION AUTHORITY: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS TEST ARTIFACT
