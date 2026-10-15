"""
TITLE:
    WILSY OS Current Bootstrap Authority Direct Certificate
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tools.eos.auth.current_system_permission_bootstrap_authority import (
    CurrentSystemPermissionBootstrapAuthorityResolver,
)

from tools.eos.auth.system_permission_bootstrap_authority import (
    SystemPermissionBootstrapAuthority,
)

from tools.eos.auth.system_permission_bootstrap_authority_registry import (
    SystemPermissionBootstrapAuthorityRegistry,
)


PURPOSE = (
    "SEED_SYSTEM_PERMISSION_ASSIGNMENT_COMMAND_AUTHORITY"
)

OTHER_PURPOSE = (
    "SEED_SYSTEM_PERMISSION_REVOCATION_COMMAND_AUTHORITY"
)

NOW = datetime(
    2026,
    10,
    14,
    22,
    30,
    tzinfo=timezone.utc,
)


class Session:
    pass


class PrincipalCollection:
    def __init__(
        self,
        *,
        status: str = "ACTIVE",
        principal_id: str = "principal-a",
    ) -> None:
        self.status = status
        self.principal_id = principal_id
        self.sessions: list[object] = []

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, object] | None:
        self.sessions.append(session)

        if (
            query.get("principal_id")
            != self.principal_id
        ):
            return None

        return {
            "principal_id": self.principal_id,
            "status": self.status,
            "revision": 0,
        }


class FakeCursor:
    def __init__(
        self,
        rows: list[dict[str, object]],
    ) -> None:
        self.rows = rows

    def sort(
        self,
        *_: object,
    ) -> FakeCursor:
        return self

    def __iter__(self):
        return iter(self.rows)


class BootstrapCollection:
    def __init__(
        self,
        authority:
            SystemPermissionBootstrapAuthority | None,
    ) -> None:
        self.authority = authority
        self.sessions: list[object] = []

    def find(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> FakeCursor:
        self.sessions.append(session)

        rows: list[dict[str, object]] = []

        if (
            self.authority is not None
            and query.get("actor_principal_id")
            == self.authority.actor_principal_id
            and query.get("purpose")
            == self.authority.purpose
        ):
            row = self.authority.to_dict()
            row["issued_at"] = self.authority.issued_at
            row["retired_at"] = self.authority.retired_at
            rows.append(row)

        return FakeCursor(rows)


def bootstrap() -> SystemPermissionBootstrapAuthority:
    return SystemPermissionBootstrapAuthority.issue(
        bootstrap_id="bootstrap-a",
        actor_principal_id="principal-a",
        purpose=PURPOSE,
        evidence_reference="installation-evidence-a",
        issued_at=NOW,
    )


def resolver(
    *,
    status: str = "ACTIVE",
    authority:
        SystemPermissionBootstrapAuthority | None = None,
) -> tuple[
    CurrentSystemPermissionBootstrapAuthorityResolver,
    PrincipalCollection,
    BootstrapCollection,
]:
    principal_collection = PrincipalCollection(
        status=status
    )

    bootstrap_collection = BootstrapCollection(
        authority
    )

    bootstrap_registry = (
        SystemPermissionBootstrapAuthorityRegistry(
            bootstrap_collection
        )
    )

    return (
        CurrentSystemPermissionBootstrapAuthorityResolver(
            principal_collection=principal_collection,
            bootstrap_registry=bootstrap_registry,
        ),
        principal_collection,
        bootstrap_collection,
    )


def test_active_principal_and_active_exact_bootstrap_allow() -> None:
    value = bootstrap()

    current, _, _ = resolver(
        authority=value
    )

    assert current.resolve(
        principal_id="principal-a",
        purpose=PURPOSE,
    ) == value


@pytest.mark.parametrize(
    "status",
    (
        "SUSPENDED",
        "REVOKED",
    ),
)
def test_nonactive_principal_denies(
    status: str,
) -> None:
    current, _, _ = resolver(
        status=status,
        authority=bootstrap(),
    )

    assert current.resolve(
        principal_id="principal-a",
        purpose=PURPOSE,
    ) is None


def test_missing_principal_denies() -> None:
    principal = PrincipalCollection(
        principal_id="principal-other"
    )

    bootstrap_collection = BootstrapCollection(
        bootstrap()
    )

    registry = (
        SystemPermissionBootstrapAuthorityRegistry(
            bootstrap_collection
        )
    )

    current = (
        CurrentSystemPermissionBootstrapAuthorityResolver(
            principal_collection=principal,
            bootstrap_registry=registry,
        )
    )

    assert current.resolve(
        principal_id="principal-a",
        purpose=PURPOSE,
    ) is None


def test_missing_bootstrap_denies() -> None:
    current, _, _ = resolver(
        authority=None
    )

    assert current.resolve(
        principal_id="principal-a",
        purpose=PURPOSE,
    ) is None


def test_exact_purpose_required() -> None:
    current, _, _ = resolver(
        authority=bootstrap()
    )

    assert current.resolve(
        principal_id="principal-a",
        purpose=OTHER_PURPOSE,
    ) is None


def test_same_session_propagated_to_both_reads() -> None:
    current, principal, bootstrap_collection = resolver(
        authority=bootstrap()
    )

    session = Session()

    current.resolve(
        principal_id="principal-a",
        purpose=PURPOSE,
        session=session,  # type: ignore[arg-type]
    )

    assert principal.sessions == [session]
    assert bootstrap_collection.sessions == [session]


def test_no_authority_creation_surface() -> None:
    current, _, _ = resolver(
        authority=bootstrap()
    )

    for forbidden in (
        "create",
        "issue",
        "assign",
        "grant",
        "revoke",
        "retire",
        "activate",
        "authorize",
        "break_glass",
        "execute_financial",
    ):
        assert not hasattr(
            current,
            forbidden,
        )


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# ARTIFACT: tests/unit/test_current_system_permission_bootstrap_authority.py
# CURRENT PRINCIPAL REQUIRED: YES
# CURRENT EXACT BOOTSTRAP PURPOSE REQUIRED: YES
# SAME CALLER SESSION: YES
# READ ONLY: YES
# AUTHORITY CREATION: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS TEST ARTIFACT
