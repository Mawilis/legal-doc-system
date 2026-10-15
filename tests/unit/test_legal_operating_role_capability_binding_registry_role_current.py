"""
TITLE: WILSY OS CX27 Capability Role-Indexed Current Read Contract

VERSION: v1.0.0-PW-P6A-RED-CAPABILITY-ROLE-CURRENT-READ

EPITOME:
    Freeze the read-only public registry contract required to hydrate
    productive-work operating contexts from durable CX27 capability truth.

AUTHORITY BOUNDARY:
    Capability association is descriptive operating metadata only.
    It never establishes IAM permission possession, assignment authority,
    supervision authority, workflow authority, or financial authority.

LOOKUP KEY:
    tenant_id + operating_role_id + operating_role_revision + at

RETURN:
    Zero or more effective current binding leaves across independent immutable
    capability-binding chains for the exact operating-role revision.

TRANSACTION:
    Caller owns one already-active Mongo transaction.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_operating_role_capability_binding import (
    LegalOperatingRoleCapabilityBinding,
)
from tools.eos.legal_operations.registry.legal_operating_role_capability_binding_registry import (
    LegalOperatingRoleCapabilityBindingRegistry,
    RegistryTransactionRequiredError,
)


NOW = datetime(
    2026,
    10,
    15,
    18,
    0,
    tzinfo=UTC,
)

TENANT = "tenant-a"
ROLE = "role-custom-1"
ROLE_REVISION = 3


class _Cursor:
    def __init__(
        self,
        rows: list[dict[str, object]],
    ) -> None:
        self._rows = list(
            rows
        )

    def sort(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> "_Cursor":
        return self

    def __iter__(self):
        return iter(
            self._rows
        )


class _Collection:
    def __init__(self) -> None:
        self.rows: list[
            dict[str, object]
        ] = []

    @staticmethod
    def _matches(
        row: dict[str, object],
        query: dict[str, object],
    ) -> bool:
        return all(
            row.get(key) == value
            for key, value
            in query.items()
        )

    def find(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> _Cursor:
        return _Cursor(
            [
                dict(row)
                for row in self.rows
                if self._matches(
                    row,
                    query,
                )
            ]
        )

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        for row in self.rows:
            if self._matches(
                row,
                query,
            ):
                return dict(
                    row
                )

        return None


def _session(
    active: bool = True,
) -> object:
    return SimpleNamespace(
        in_transaction=active
    )


def _binding(
    binding_id: str,
    binding_revision: int,
    capability_ids: tuple[str, ...],
    *,
    tenant_id: str = TENANT,
    role_id: str = ROLE,
    role_revision: int = ROLE_REVISION,
    effective_from: datetime = NOW,
    supersedes_fingerprint: str | None = None,
) -> LegalOperatingRoleCapabilityBinding:
    return LegalOperatingRoleCapabilityBinding(
        tenant_id=tenant_id,
        capability_binding_id=binding_id,
        operating_role_id=role_id,
        operating_role_revision=role_revision,
        capability_binding_revision=binding_revision,
        capability_ids=capability_ids,
        effective_from=effective_from,
        supersedes_fingerprint=supersedes_fingerprint,
    )


def _role_current(
    registry: LegalOperatingRoleCapabilityBindingRegistry,
    *,
    tenant_id: str = TENANT,
    role_id: str = ROLE,
    role_revision: int = ROLE_REVISION,
    at: datetime = NOW,
    session: object,
) -> tuple[
    LegalOperatingRoleCapabilityBinding,
    ...
]:
    return registry.list_current_for_operating_role_revision(
        tenant_id,
        role_id,
        role_revision,
        at,
        session=session,
    )


def test_role_indexed_current_read_requires_active_caller_transaction() -> None:
    registry = LegalOperatingRoleCapabilityBindingRegistry(
        _Collection()
    )

    with pytest.raises(
        RegistryTransactionRequiredError,
        match="ACTIVE",
    ):
        _role_current(
            registry,
            session=_session(False),
        )


def test_zero_current_bindings_returns_empty_tuple() -> None:
    registry = LegalOperatingRoleCapabilityBindingRegistry(
        _Collection()
    )

    assert (
        _role_current(
            registry,
            session=_session(),
        )
        == ()
    )


def test_returns_multiple_independent_current_binding_chains() -> None:
    collection = _Collection()

    registry = LegalOperatingRoleCapabilityBindingRegistry(
        collection
    )

    first = _binding(
        "capability-binding-a",
        1,
        (
            "PRACTICE_DISPUTES",
        ),
    )

    second = _binding(
        "capability-binding-b",
        1,
        (
            "PRACTICE_CORPORATE",
        ),
    )

    collection.rows.extend(
        [
            first.to_dict(),
            second.to_dict(),
        ]
    )

    result = _role_current(
        registry,
        session=_session(),
    )

    assert tuple(
        value.capability_binding_id
        for value in result
    ) == (
        "capability-binding-a",
        "capability-binding-b",
    )


def test_current_read_resolves_successor_leaf_per_binding_identity() -> None:
    collection = _Collection()

    registry = LegalOperatingRoleCapabilityBindingRegistry(
        collection
    )

    first = _binding(
        "capability-binding-a",
        1,
        (
            "PRACTICE_DISPUTES",
        ),
    )

    successor = _binding(
        "capability-binding-a",
        2,
        (
            "PRACTICE_DISPUTES",
            "PRACTICE_CORPORATE",
        ),
        effective_from=(
            NOW
            + timedelta(hours=1)
        ),
        supersedes_fingerprint=first.fingerprint,
    )

    collection.rows.extend(
        [
            first.to_dict(),
            successor.to_dict(),
        ]
    )

    before = _role_current(
        registry,
        at=NOW + timedelta(minutes=30),
        session=_session(),
    )

    after = _role_current(
        registry,
        at=NOW + timedelta(hours=2),
        session=_session(),
    )

    assert before == (
        first,
    )

    assert after == (
        successor,
    )


def test_future_binding_chain_is_not_current_early() -> None:
    collection = _Collection()

    registry = LegalOperatingRoleCapabilityBindingRegistry(
        collection
    )

    future = _binding(
        "capability-binding-future",
        1,
        (
            "PRACTICE_DISPUTES",
        ),
        effective_from=(
            NOW
            + timedelta(hours=1)
        ),
    )

    collection.rows.append(
        future.to_dict()
    )

    assert (
        _role_current(
            registry,
            at=NOW,
            session=_session(),
        )
        == ()
    )

    assert (
        _role_current(
            registry,
            at=NOW + timedelta(hours=2),
            session=_session(),
        )
        == (
            future,
        )
    )


def test_exact_operating_role_revision_is_enforced() -> None:
    collection = _Collection()

    registry = LegalOperatingRoleCapabilityBindingRegistry(
        collection
    )

    matching = _binding(
        "capability-binding-current-role",
        1,
        (
            "PRACTICE_DISPUTES",
        ),
    )

    other_revision = _binding(
        "capability-binding-old-role",
        1,
        (
            "PRACTICE_CORPORATE",
        ),
        role_revision=2,
    )

    other_role = _binding(
        "capability-binding-other-role",
        1,
        (
            "PRACTICE_DISPUTES",
        ),
        role_id="role-other",
    )

    collection.rows.extend(
        [
            other_revision.to_dict(),
            other_role.to_dict(),
            matching.to_dict(),
        ]
    )

    assert (
        _role_current(
            registry,
            session=_session(),
        )
        == (
            matching,
        )
    )


def test_foreign_tenant_is_indistinguishable_from_absence() -> None:
    collection = _Collection()

    registry = LegalOperatingRoleCapabilityBindingRegistry(
        collection
    )

    collection.rows.append(
        _binding(
            "capability-binding-a",
            1,
            (
                "PRACTICE_DISPUTES",
            ),
        ).to_dict()
    )

    assert (
        _role_current(
            registry,
            tenant_id="tenant-b",
            session=_session(),
        )
        == ()
    )


def test_current_read_is_deterministic_by_binding_identity() -> None:
    collection = _Collection()

    registry = LegalOperatingRoleCapabilityBindingRegistry(
        collection
    )

    zulu = _binding(
        "capability-binding-z",
        1,
        (
            "PRACTICE_DISPUTES",
        ),
    )

    alpha = _binding(
        "capability-binding-a",
        1,
        (
            "PRACTICE_CORPORATE",
        ),
    )

    collection.rows.extend(
        [
            zulu.to_dict(),
            alpha.to_dict(),
        ]
    )

    result = _role_current(
        registry,
        session=_session(),
    )

    assert tuple(
        value.capability_binding_id
        for value in result
    ) == (
        "capability-binding-a",
        "capability-binding-z",
    )


def test_role_current_read_exposes_no_authority_surface() -> None:
    registry = LegalOperatingRoleCapabilityBindingRegistry(
        _Collection()
    )

    for forbidden in (
        "authorize",
        "grant_permission",
        "assign",
        "supervise",
        "pay",
        "invoice",
        "settle",
    ):
        assert not hasattr(
            registry,
            forbidden,
        )


# AUTHORITY BOUNDARY:
# current capability association lookup only.
# Capability metadata is not IAM permission possession.
