"""
TITLE: WILSY OS CX27 Scope Role-Indexed Current Read Contract

VERSION: v1.0.0-PW-P6D-RED-SCOPE-ROLE-CURRENT-READ

EPITOME:
    Freeze the read-only public registry contract required to hydrate
    productive-work operating contexts from durable CX27 scope truth.

AUTHORITY BOUNDARY:
    Scope associations are descriptive operating metadata only.
    They never establish record access, client access, matter authority,
    IAM permission possession, assignment, supervision, workflow, or
    financial authority.

LOOKUP KEY:
    tenant_id + operating_role_id + operating_role_revision + at

RETURN:
    Zero or more effective current binding leaves across independent immutable
    scope-binding chains for the exact operating-role revision.

TRANSACTION:
    Caller owns one already-active Mongo transaction.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_operating_role_scope_binding import (
    LegalOperatingRoleScopeBinding,
)
from tools.eos.legal_operations.registry.legal_operating_role_scope_binding_registry import (
    LegalOperatingRoleScopeBindingRegistry,
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
    *,
    tenant_id: str = TENANT,
    role_id: str = ROLE,
    role_revision: int = ROLE_REVISION,
    office_references: tuple[str, ...] = (
        "office:jhb",
    ),
    practice_references: tuple[str, ...] = (),
    business_unit_references: tuple[str, ...] = (),
    jurisdiction_references: tuple[str, ...] = (),
    effective_from: datetime = NOW,
    supersedes_fingerprint: str | None = None,
) -> LegalOperatingRoleScopeBinding:
    return LegalOperatingRoleScopeBinding(
        tenant_id=tenant_id,
        scope_binding_id=binding_id,
        operating_role_id=role_id,
        operating_role_revision=role_revision,
        scope_binding_revision=binding_revision,
        office_references=office_references,
        practice_references=practice_references,
        business_unit_references=business_unit_references,
        jurisdiction_references=jurisdiction_references,
        effective_from=effective_from,
        supersedes_fingerprint=supersedes_fingerprint,
    )


def _role_current(
    registry: LegalOperatingRoleScopeBindingRegistry,
    *,
    tenant_id: str = TENANT,
    role_id: str = ROLE,
    role_revision: int = ROLE_REVISION,
    at: datetime = NOW,
    session: object,
) -> tuple[
    LegalOperatingRoleScopeBinding,
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
    registry = LegalOperatingRoleScopeBindingRegistry(
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
    registry = LegalOperatingRoleScopeBindingRegistry(
        _Collection()
    )

    assert (
        _role_current(
            registry,
            session=_session(),
        )
        == ()
    )


def test_returns_multiple_independent_current_scope_chains() -> None:
    collection = _Collection()

    registry = LegalOperatingRoleScopeBindingRegistry(
        collection
    )

    office = _binding(
        "scope-binding-office",
        1,
        office_references=(
            "office:jhb",
        ),
    )

    practice = _binding(
        "scope-binding-practice",
        1,
        office_references=(),
        practice_references=(
            "practice:disputes",
        ),
    )

    collection.rows.extend(
        [
            practice.to_dict(),
            office.to_dict(),
        ]
    )

    result = _role_current(
        registry,
        session=_session(),
    )

    assert tuple(
        value.scope_binding_id
        for value in result
    ) == (
        "scope-binding-office",
        "scope-binding-practice",
    )


def test_current_read_resolves_successor_leaf_per_scope_identity() -> None:
    collection = _Collection()

    registry = LegalOperatingRoleScopeBindingRegistry(
        collection
    )

    first = _binding(
        "scope-binding-a",
        1,
        office_references=(
            "office:jhb",
        ),
    )

    successor = _binding(
        "scope-binding-a",
        2,
        office_references=(
            "office:jhb",
            "office:cpt",
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


def test_future_scope_chain_is_not_current_early() -> None:
    collection = _Collection()

    registry = LegalOperatingRoleScopeBindingRegistry(
        collection
    )

    future = _binding(
        "scope-binding-future",
        1,
        office_references=(),
        jurisdiction_references=(
            "jurisdiction:ZA",
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

    registry = LegalOperatingRoleScopeBindingRegistry(
        collection
    )

    matching = _binding(
        "scope-binding-current-role",
        1,
        practice_references=(
            "practice:disputes",
        ),
        office_references=(),
    )

    other_revision = _binding(
        "scope-binding-old-role",
        1,
        office_references=(
            "office:cpt",
        ),
        role_revision=2,
    )

    other_role = _binding(
        "scope-binding-other-role",
        1,
        office_references=(),
        business_unit_references=(
            "business-unit:africa",
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

    registry = LegalOperatingRoleScopeBindingRegistry(
        collection
    )

    collection.rows.append(
        _binding(
            "scope-binding-a",
            1,
            office_references=(
                "office:jhb",
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

    registry = LegalOperatingRoleScopeBindingRegistry(
        collection
    )

    zulu = _binding(
        "scope-binding-z",
        1,
        office_references=(),
        jurisdiction_references=(
            "jurisdiction:ZA",
        ),
    )

    alpha = _binding(
        "scope-binding-a",
        1,
        practice_references=(
            "practice:corporate",
        ),
        office_references=(),
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
        value.scope_binding_id
        for value in result
    ) == (
        "scope-binding-a",
        "scope-binding-z",
    )


def test_scope_current_read_exposes_no_access_or_authority_surface() -> None:
    registry = LegalOperatingRoleScopeBindingRegistry(
        _Collection()
    )

    for forbidden in (
        "authorize",
        "grant_permission",
        "grant_access",
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
# current organizational scope-description lookup only.
# Scope metadata never establishes record/client/matter/IAM authority.
