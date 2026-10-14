from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.auth.platform_privileged_eligibility_prerequisite import (
    SCOPE,
    PlatformPrerequisiteStatus,
    PlatformPrivilegedEligibilityPrerequisite,
    PlatformPrivilegedEligibilityPrerequisiteError,
)
from tools.eos.auth.platform_privileged_eligibility_prerequisite_registry import (
    PlatformPrerequisiteRegistryError,
    PlatformPrivilegedEligibilityPrerequisiteRegistry,
)
from tools.eos.auth.current_platform_privileged_eligibility_prerequisite import (
    CurrentPlatformPrivilegedEligibilityPrerequisiteResolver,
)


NOW = datetime(
    2026,
    10,
    14,
    18,
    0,
    tzinfo=timezone.utc,
)

PRINCIPAL = "principal-sovereign-a"
PREREQUISITE = "platform-prerequisite-a"
EVIDENCE = "core-governance:evidence-a"

PRIVILEGE_CLASS = "SOVEREIGN_ARCHITECT"


class Session:
    in_transaction = True


class Cursor:
    def __init__(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        self.rows = rows

    def sort(
        self,
        key: str,
        direction: int,
    ) -> Cursor:
        reverse = direction < 0

        self.rows.sort(
            key=lambda row: int(
                row.get(
                    key,
                    0,
                )
            ),
            reverse=reverse,
        )

        return self

    def __iter__(
        self,
    ):
        return iter(
            self.rows
        )


class Collection:
    def __init__(
        self,
    ) -> None:
        self.rows: list[
            dict[str, Any]
        ] = []

    def create_index(
        self,
        *_: Any,
        **__: Any,
    ) -> str:
        return "index"

    def insert_one(
        self,
        row: dict[str, Any],
        *,
        session: object = None,
    ) -> object:
        self.rows.append(
            deepcopy(
                row
            )
        )

        return object()

    def find_one(
        self,
        query: dict[str, Any],
        *,
        session: object = None,
    ) -> dict[str, Any] | None:
        for row in self.rows:
            if all(
                row.get(key)
                == value
                for key, value
                in query.items()
            ):
                return deepcopy(
                    row
                )

        return None

    def find(
        self,
        query: dict[str, Any],
        *,
        session: object = None,
    ) -> Cursor:
        return Cursor(
            [
                deepcopy(
                    row
                )
                for row in self.rows
                if all(
                    row.get(key)
                    == value
                    for key, value
                    in query.items()
                )
            ]
        )


class PrincipalCollection:
    def __init__(
        self,
        *,
        active: bool = True,
    ) -> None:
        self.active = active
        self.sessions: list[
            object
        ] = []

    def find_one(
        self,
        query: dict[str, Any],
        *,
        session: object = None,
    ) -> dict[str, Any] | None:
        self.sessions.append(
            session
        )

        if (
            query.get(
                "principal_id"
            )
            != PRINCIPAL
        ):
            return None

        return {
            "principal_id":
                PRINCIPAL,
            "status":
                (
                    "ACTIVE"
                    if self.active
                    else "SUSPENDED"
                ),
            "revision":
                1,
        }


def value(
    *,
    evidence: str = EVIDENCE,
) -> PlatformPrivilegedEligibilityPrerequisite:
    return (
        PlatformPrivilegedEligibilityPrerequisite
        .designate(
            platform_prerequisite_id=
                PREREQUISITE,
            principal_id=
                PRINCIPAL,
            effective_from=
                NOW,
            source_evidence_reference=
                evidence,
            effective_until=
                NOW
                + timedelta(
                    hours=1
                ),
        )
    )


def test_exact_designation_is_immutable_and_bounded() -> None:
    item = value()

    assert (
        item.platform_prerequisite_id
        == PREREQUISITE
    )

    assert (
        item.principal_id
        == PRINCIPAL
    )

    assert (
        item.privilege_class
        == PRIVILEGE_CLASS
    )

    assert (
        item.scope
        == SCOPE
    )

    assert (
        item.status
        is PlatformPrerequisiteStatus.ACTIVE
    )

    assert (
        item.revision
        == 1
    )

    assert (
        item.source_evidence_reference
        == EVIDENCE
    )

    assert (
        len(
            item.prerequisite_fingerprint
        )
        == 128
    )

    with pytest.raises(
        Exception
    ):
        item.principal_id = "other"  # type: ignore[misc]


def test_no_initial_or_hard_coded_principal_authority() -> None:
    import tools.eos.auth.platform_privileged_eligibility_prerequisite as module

    source = open(
        module.__file__,
        encoding="utf-8",
    ).read()

    assert (
        "principal-sovereign-a"
        not in source
    )

    assert (
        "SUPER_ADMIN"
        not in source
    )

    assert (
        "FOUNDER"
        not in source
    )

    assert (
        "privileged_activation:issue"
        not in source
    )

    assert (
        "system_permission_assignment:write"
        not in source
    )


def test_wrong_or_wildcard_identity_rejected() -> None:
    with pytest.raises(
        PlatformPrivilegedEligibilityPrerequisiteError
    ):
        PlatformPrivilegedEligibilityPrerequisite.designate(
            platform_prerequisite_id="*",
            principal_id=PRINCIPAL,
            effective_from=NOW,
            source_evidence_reference=EVIDENCE,
        )

    with pytest.raises(
        PlatformPrivilegedEligibilityPrerequisiteError
    ):
        PlatformPrivilegedEligibilityPrerequisite.designate(
            platform_prerequisite_id=PREREQUISITE,
            principal_id="*",
            effective_from=NOW,
            source_evidence_reference=EVIDENCE,
        )


def test_effective_window_is_half_open() -> None:
    item = value()

    assert item.is_current_at(
        NOW
    )

    assert item.is_current_at(
        NOW
        + timedelta(
            minutes=59
        )
    )

    assert not item.is_current_at(
        NOW
        + timedelta(
            hours=1
        )
    )


@pytest.mark.parametrize(
    "status",
    (
        PlatformPrerequisiteStatus.RETIRED,
        PlatformPrerequisiteStatus.REVOKED,
    ),
)
def test_terminal_successor_is_not_current(
    status: PlatformPrerequisiteStatus,
) -> None:
    item = value()

    successor = item.transition(
        status=status,
        effective_from=
            NOW
            + timedelta(
                minutes=5
            ),
        source_evidence_reference=
            "core-governance:retire-a",
    )

    assert (
        successor.revision
        == 2
    )

    assert (
        successor.status
        is status
    )

    assert not successor.is_current_at(
        NOW
        + timedelta(
            minutes=6
        )
    )


def test_registry_append_and_exact_read() -> None:
    collection = Collection()

    registry = (
        PlatformPrivilegedEligibilityPrerequisiteRegistry(
            collection
        )
    )

    item = value()

    result = registry.append(
        item,
        session=Session(),  # type: ignore[arg-type]
    )

    assert result == item

    durable = registry.get(
        platform_prerequisite_id=
            PREREQUISITE,
        revision=1,
        session=Session(),  # type: ignore[arg-type]
    )

    assert durable == item


def test_registry_requires_active_transaction_for_append() -> None:
    collection = Collection()

    registry = (
        PlatformPrivilegedEligibilityPrerequisiteRegistry(
            collection
        )
    )

    with pytest.raises(
        PlatformPrerequisiteRegistryError
    ):
        registry.append(
            value(),
            session=None,  # type: ignore[arg-type]
        )

    assert (
        collection.rows
        == []
    )


def test_registry_current_resolution() -> None:
    collection = Collection()

    registry = (
        PlatformPrivilegedEligibilityPrerequisiteRegistry(
            collection
        )
    )

    item = value()

    registry.append(
        item,
        session=Session(),  # type: ignore[arg-type]
    )

    current = registry.resolve_current(
        principal_id=
            PRINCIPAL,
        privilege_class=
            PRIVILEGE_CLASS,
        scope=
            SCOPE,
        at=
            NOW
            + timedelta(
                minutes=1
            ),
        session=Session(),  # type: ignore[arg-type]
    )

    assert current == item


def test_current_resolver_conjoins_active_principal_and_prerequisite() -> None:
    collection = Collection()

    registry = (
        PlatformPrivilegedEligibilityPrerequisiteRegistry(
            collection
        )
    )

    item = value()

    session = Session()

    registry.append(
        item,
        session=session,  # type: ignore[arg-type]
    )

    principals = (
        PrincipalCollection(
            active=True
        )
    )

    resolver = (
        CurrentPlatformPrivilegedEligibilityPrerequisiteResolver(
            principal_collection=
                principals,
            prerequisite_registry=
                registry,
        )
    )

    current = resolver.resolve(
        principal_id=
            PRINCIPAL,
        privilege_class=
            PRIVILEGE_CLASS,
        scope=
            SCOPE,
        at=
            NOW
            + timedelta(
                minutes=1
            ),
        session=session,  # type: ignore[arg-type]
    )

    assert current == item

    assert principals.sessions == [
        session
    ]


def test_current_resolver_denies_inactive_principal() -> None:
    collection = Collection()

    registry = (
        PlatformPrivilegedEligibilityPrerequisiteRegistry(
            collection
        )
    )

    registry.append(
        value(),
        session=Session(),  # type: ignore[arg-type]
    )

    resolver = (
        CurrentPlatformPrivilegedEligibilityPrerequisiteResolver(
            principal_collection=
                PrincipalCollection(
                    active=False
                ),
            prerequisite_registry=
                registry,
        )
    )

    assert (
        resolver.resolve(
            principal_id=
                PRINCIPAL,
            privilege_class=
                PRIVILEGE_CLASS,
            scope=
                SCOPE,
            at=
                NOW
                + timedelta(
                    minutes=1
                ),
            session=Session(),  # type: ignore[arg-type]
        )
        is None
    )


def test_current_resolver_denies_wrong_class_or_scope() -> None:
    collection = Collection()

    registry = (
        PlatformPrivilegedEligibilityPrerequisiteRegistry(
            collection
        )
    )

    resolver = (
        CurrentPlatformPrivilegedEligibilityPrerequisiteResolver(
            principal_collection=
                PrincipalCollection(),
            prerequisite_registry=
                registry,
        )
    )

    assert (
        resolver.resolve(
            principal_id=
                PRINCIPAL,
            privilege_class=
                "ENTERPRISE_ADMIN",
            scope=
                SCOPE,
            at=
                NOW,
            session=Session(),  # type: ignore[arg-type]
        )
        is None
    )

    assert (
        resolver.resolve(
            principal_id=
                PRINCIPAL,
            privilege_class=
                PRIVILEGE_CLASS,
            scope=
                "TENANT",
            at=
                NOW,
            session=Session(),  # type: ignore[arg-type]
        )
        is None
    )


def test_resolver_has_no_mutation_or_transaction_lifecycle_surface() -> None:
    resolver = (
        CurrentPlatformPrivilegedEligibilityPrerequisiteResolver(
            principal_collection=
                PrincipalCollection(),
            prerequisite_registry=
                PlatformPrivilegedEligibilityPrerequisiteRegistry(
                    Collection()
                ),
        )
    )

    for name in (
        "append",
        "insert",
        "update",
        "delete",
        "start_session",
        "start_transaction",
        "commit_transaction",
        "abort_transaction",
        "activate",
        "assign_permission",
        "break_glass",
        "execute_financial",
    ):
        assert not hasattr(
            resolver,
            name,
        )
