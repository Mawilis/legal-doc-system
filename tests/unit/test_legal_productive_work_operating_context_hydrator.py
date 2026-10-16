"""
TITLE: WILSY OS CX27 Productive-Work Operating-Context Hydrator Contract

VERSION: v1.0.0-PW-P7A-RED-CX27-OPERATING-CONTEXT-HYDRATOR

EPITOME:
    Freeze the read-only composition contract that converts durable CX27
    principal occupancy, exact operating-role revision, capability metadata,
    and organizational-scope metadata into productive-work operating contexts.

SOVEREIGN COMPOSITION:
    current principal occupancy
        -> exact occupied role revision
        -> current capability bindings for that exact revision
        -> current scope bindings for that exact revision
        -> LegalProductiveWorkOperatingContext

AUTHORITY BOUNDARY:
    This composition establishes no IAM permission, record/client/matter
    access, assignment, supervision, workflow, professional, financial, or
    execution authority.

TRANSACTION:
    Caller owns one already-active transaction and the identical session is
    propagated unchanged through every durable read.
"""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_operating_role_capability_binding import (
    LegalOperatingRoleCapabilityBinding,
)
from tools.eos.legal_operations.domain.legal_operating_role_definition import (
    LegalOperatingRoleDefinition,
)
from tools.eos.legal_operations.domain.legal_operating_role_scope_binding import (
    LegalOperatingRoleScopeBinding,
)
from tools.eos.legal_operations.domain.legal_principal_operating_role_binding import (
    LegalPrincipalOperatingRoleBinding,
)
from tools.eos.legal_operations.service.legal_productive_work_operating_context_hydrator import (
    LegalProductiveWorkOperatingContextHydrator,
    LegalProductiveWorkOperatingContextHydratorError,
    LegalProductiveWorkOperatingContextHydratorTransactionRequiredError,
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
PRINCIPAL = "principal-a"

ROLE_A = "role-custom-litigation-lead"
ROLE_A_REVISION = 3

ROLE_B = "role-custom-cross-border-reviewer"
ROLE_B_REVISION = 2


def _session(
    active: bool = True,
) -> object:
    return SimpleNamespace(
        in_transaction=active
    )


def _occupancy(
    *,
    binding_id: str = "occupancy-a",
    binding_revision: int = 1,
    principal_id: str = PRINCIPAL,
    role_id: str = ROLE_A,
    role_revision: int = ROLE_A_REVISION,
) -> LegalPrincipalOperatingRoleBinding:
    return LegalPrincipalOperatingRoleBinding(
        tenant_id=TENANT,
        principal_operating_role_binding_id=binding_id,
        binding_revision=binding_revision,
        principal_id=principal_id,
        operating_role_id=role_id,
        operating_role_revision=role_revision,
        effective_from=NOW,
        effective_until=None,
        source_reference="source:tenant-operating-model",
        source_evidence_fingerprint="a" * 128,
        supersedes_fingerprint=None,
    )


def _role(
    *,
    role_id: str = ROLE_A,
    role_revision: int = ROLE_A_REVISION,
    display_name: str = "Litigation Lead Specialist",
) -> LegalOperatingRoleDefinition:
    return LegalOperatingRoleDefinition(
        tenant_id=TENANT,
        operating_role_id=role_id,
        role_revision=role_revision,
        display_name=display_name,
        description="Tenant-defined descriptive operating role",
        effective_from=NOW,
        supersedes_fingerprint=(
            None
            if role_revision == 1
            else "b" * 128
        ),
    )


def _capability(
    binding_id: str,
    capabilities: tuple[str, ...],
    *,
    role_id: str = ROLE_A,
    role_revision: int = ROLE_A_REVISION,
) -> LegalOperatingRoleCapabilityBinding:
    return LegalOperatingRoleCapabilityBinding(
        tenant_id=TENANT,
        capability_binding_id=binding_id,
        operating_role_id=role_id,
        operating_role_revision=role_revision,
        capability_binding_revision=1,
        capability_ids=capabilities,
        effective_from=NOW,
        supersedes_fingerprint=None,
    )


def _scope(
    binding_id: str,
    *,
    role_id: str = ROLE_A,
    role_revision: int = ROLE_A_REVISION,
    offices: tuple[str, ...] = (),
    practices: tuple[str, ...] = (),
    business_units: tuple[str, ...] = (),
    jurisdictions: tuple[str, ...] = (),
) -> LegalOperatingRoleScopeBinding:
    return LegalOperatingRoleScopeBinding(
        tenant_id=TENANT,
        scope_binding_id=binding_id,
        operating_role_id=role_id,
        operating_role_revision=role_revision,
        scope_binding_revision=1,
        office_references=offices,
        practice_references=practices,
        business_unit_references=business_units,
        jurisdiction_references=jurisdictions,
        effective_from=NOW,
        supersedes_fingerprint=None,
    )


class _OccupancyRegistry:
    def __init__(
        self,
        values: tuple[
            LegalPrincipalOperatingRoleBinding,
            ...
        ] = (),
    ) -> None:
        self.values = values
        self.calls: list[
            tuple[
                str,
                str,
                datetime,
                object,
            ]
        ] = []

    def list_current_for_principal(
        self,
        tenant_id: str,
        principal_id: str,
        at: datetime,
        *,
        session: object,
    ) -> tuple[
        LegalPrincipalOperatingRoleBinding,
        ...
    ]:
        self.calls.append(
            (
                tenant_id,
                principal_id,
                at,
                session,
            )
        )

        return self.values


class _RoleDefinitionRegistry:
    def __init__(
        self,
        values: dict[
            tuple[str, int],
            LegalOperatingRoleDefinition,
        ] | None = None,
    ) -> None:
        self.values = (
            values
            if values is not None
            else {}
        )

        self.calls: list[
            tuple[
                str,
                str,
                int,
                object,
            ]
        ] = []

    def get_revision(
        self,
        tenant_id: str,
        identity: str,
        revision: int,
        *,
        session: object,
    ) -> LegalOperatingRoleDefinition:
        self.calls.append(
            (
                tenant_id,
                identity,
                revision,
                session,
            )
        )

        return self.values[
            (
                identity,
                revision,
            )
        ]


class _CapabilityRegistry:
    def __init__(
        self,
        values: dict[
            tuple[str, int],
            tuple[
                LegalOperatingRoleCapabilityBinding,
                ...
            ],
        ] | None = None,
    ) -> None:
        self.values = (
            values
            if values is not None
            else {}
        )

        self.calls: list[
            tuple[
                str,
                str,
                int,
                datetime,
                object,
            ]
        ] = []

    def list_current_for_operating_role_revision(
        self,
        tenant_id: str,
        operating_role_id: str,
        operating_role_revision: int,
        at: datetime,
        *,
        session: object,
    ) -> tuple[
        LegalOperatingRoleCapabilityBinding,
        ...
    ]:
        self.calls.append(
            (
                tenant_id,
                operating_role_id,
                operating_role_revision,
                at,
                session,
            )
        )

        return self.values.get(
            (
                operating_role_id,
                operating_role_revision,
            ),
            (),
        )


class _ScopeRegistry:
    def __init__(
        self,
        values: dict[
            tuple[str, int],
            tuple[
                LegalOperatingRoleScopeBinding,
                ...
            ],
        ] | None = None,
    ) -> None:
        self.values = (
            values
            if values is not None
            else {}
        )

        self.calls: list[
            tuple[
                str,
                str,
                int,
                datetime,
                object,
            ]
        ] = []

    def list_current_for_operating_role_revision(
        self,
        tenant_id: str,
        operating_role_id: str,
        operating_role_revision: int,
        at: datetime,
        *,
        session: object,
    ) -> tuple[
        LegalOperatingRoleScopeBinding,
        ...
    ]:
        self.calls.append(
            (
                tenant_id,
                operating_role_id,
                operating_role_revision,
                at,
                session,
            )
        )

        return self.values.get(
            (
                operating_role_id,
                operating_role_revision,
            ),
            (),
        )


def _hydrator(
    *,
    occupancies: tuple[
        LegalPrincipalOperatingRoleBinding,
        ...
    ] = (),
    roles: dict[
        tuple[str, int],
        LegalOperatingRoleDefinition,
    ] | None = None,
    capabilities: dict[
        tuple[str, int],
        tuple[
            LegalOperatingRoleCapabilityBinding,
            ...
        ],
    ] | None = None,
    scopes: dict[
        tuple[str, int],
        tuple[
            LegalOperatingRoleScopeBinding,
            ...
        ],
    ] | None = None,
) -> tuple[
    LegalProductiveWorkOperatingContextHydrator,
    _OccupancyRegistry,
    _RoleDefinitionRegistry,
    _CapabilityRegistry,
    _ScopeRegistry,
]:
    occupancy_registry = _OccupancyRegistry(
        occupancies
    )

    role_registry = _RoleDefinitionRegistry(
        roles
    )

    capability_registry = _CapabilityRegistry(
        capabilities
    )

    scope_registry = _ScopeRegistry(
        scopes
    )

    hydrator = (
        LegalProductiveWorkOperatingContextHydrator(
            principal_operating_role_registry=
                occupancy_registry,
            operating_role_definition_registry=
                role_registry,
            operating_role_capability_registry=
                capability_registry,
            operating_role_scope_registry=
                scope_registry,
        )
    )

    return (
        hydrator,
        occupancy_registry,
        role_registry,
        capability_registry,
        scope_registry,
    )


def test_active_caller_transaction_required_before_any_registry_read() -> None:
    (
        hydrator,
        occupancy_registry,
        role_registry,
        capability_registry,
        scope_registry,
    ) = _hydrator()

    with pytest.raises(
        LegalProductiveWorkOperatingContextHydratorTransactionRequiredError,
        match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
    ):
        hydrator.hydrate(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            at=NOW,
            session=_session(False),
        )

    assert occupancy_registry.calls == []
    assert role_registry.calls == []
    assert capability_registry.calls == []
    assert scope_registry.calls == []


def test_no_current_occupancy_returns_empty_contexts() -> None:
    (
        hydrator,
        _,
        _,
        _,
        _,
    ) = _hydrator()

    assert hydrator.hydrate(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        at=NOW,
        session=_session(),
    ) == ()


def test_exact_occupied_role_revision_and_same_session_are_used() -> None:
    occupancy = _occupancy()

    role = _role()

    capability = _capability(
        "cap-a",
        (
            "PRACTICE_DISPUTES",
        ),
    )

    scope = _scope(
        "scope-a",
        offices=(
            "office:jhb",
        ),
    )

    (
        hydrator,
        occupancy_registry,
        role_registry,
        capability_registry,
        scope_registry,
    ) = _hydrator(
        occupancies=(
            occupancy,
        ),
        roles={
            (
                ROLE_A,
                ROLE_A_REVISION,
            ): role,
        },
        capabilities={
            (
                ROLE_A,
                ROLE_A_REVISION,
            ): (
                capability,
            ),
        },
        scopes={
            (
                ROLE_A,
                ROLE_A_REVISION,
            ): (
                scope,
            ),
        },
    )

    session = _session()

    result = hydrator.hydrate(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        at=NOW,
        session=session,
    )

    assert len(result) == 1

    context = result[0]

    assert context.operating_role_id == ROLE_A
    assert (
        context.operating_role_revision
        == ROLE_A_REVISION
    )
    assert context.display_name == (
        "Litigation Lead Specialist"
    )

    assert occupancy_registry.calls == [
        (
            TENANT,
            PRINCIPAL,
            NOW,
            session,
        )
    ]

    assert role_registry.calls == [
        (
            TENANT,
            ROLE_A,
            ROLE_A_REVISION,
            session,
        )
    ]

    assert capability_registry.calls == [
        (
            TENANT,
            ROLE_A,
            ROLE_A_REVISION,
            NOW,
            session,
        )
    ]

    assert scope_registry.calls == [
        (
            TENANT,
            ROLE_A,
            ROLE_A_REVISION,
            NOW,
            session,
        )
    ]


def test_multiple_capability_bindings_union_and_deduplicate_deterministically() -> None:
    occupancy = _occupancy()

    (
        hydrator,
        _,
        _,
        _,
        _,
    ) = _hydrator(
        occupancies=(
            occupancy,
        ),
        roles={
            (
                ROLE_A,
                ROLE_A_REVISION,
            ): _role(),
        },
        capabilities={
            (
                ROLE_A,
                ROLE_A_REVISION,
            ): (
                _capability(
                    "cap-z",
                    (
                        "PRACTICE_DISPUTES",
                        "PRACTICE_CORPORATE",
                    ),
                ),
                _capability(
                    "cap-a",
                    (
                        "PRACTICE_CORPORATE",
                    ),
                ),
            ),
        },
    )

    result = hydrator.hydrate(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        at=NOW,
        session=_session(),
    )

    assert result[0].capability_ids == (
        "PRACTICE_CORPORATE",
        "PRACTICE_DISPUTES",
    )


def test_multiple_scope_bindings_union_each_dimension_deterministically() -> None:
    occupancy = _occupancy()

    (
        hydrator,
        _,
        _,
        _,
        _,
    ) = _hydrator(
        occupancies=(
            occupancy,
        ),
        roles={
            (
                ROLE_A,
                ROLE_A_REVISION,
            ): _role(),
        },
        scopes={
            (
                ROLE_A,
                ROLE_A_REVISION,
            ): (
                _scope(
                    "scope-z",
                    offices=(
                        "office:jhb",
                        "office:cpt",
                    ),
                    practices=(
                        "practice:disputes",
                    ),
                ),
                _scope(
                    "scope-a",
                    offices=(
                        "office:jhb",
                    ),
                    business_units=(
                        "business-unit:africa",
                    ),
                    jurisdictions=(
                        "jurisdiction:ZA",
                    ),
                ),
            ),
        },
    )

    result = hydrator.hydrate(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        at=NOW,
        session=_session(),
    )

    context = result[0]

    assert context.office_references == (
        "office:cpt",
        "office:jhb",
    )

    assert context.practice_references == (
        "practice:disputes",
    )

    assert context.business_unit_references == (
        "business-unit:africa",
    )

    assert context.jurisdiction_references == (
        "jurisdiction:ZA",
    )


def test_multi_role_contexts_are_deterministic_and_title_independent() -> None:
    first_occupancy = _occupancy(
        binding_id="occupancy-z",
        role_id=ROLE_A,
        role_revision=ROLE_A_REVISION,
    )

    second_occupancy = _occupancy(
        binding_id="occupancy-a",
        role_id=ROLE_B,
        role_revision=ROLE_B_REVISION,
    )

    (
        hydrator,
        _,
        _,
        _,
        _,
    ) = _hydrator(
        occupancies=(
            first_occupancy,
            second_occupancy,
        ),
        roles={
            (
                ROLE_A,
                ROLE_A_REVISION,
            ): _role(
                role_id=ROLE_A,
                role_revision=ROLE_A_REVISION,
                display_name="Arbitrary Bespoke Alpha",
            ),
            (
                ROLE_B,
                ROLE_B_REVISION,
            ): _role(
                role_id=ROLE_B,
                role_revision=ROLE_B_REVISION,
                display_name="Arbitrary Bespoke Zulu",
            ),
        },
    )

    result = hydrator.hydrate(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        at=NOW,
        session=_session(),
    )

    assert tuple(
        context.operating_role_id
        for context in result
    ) == tuple(
        sorted(
            (
                ROLE_A,
                ROLE_B,
            )
        )
    )

    assert {
        context.display_name
        for context in result
    } == {
        "Arbitrary Bespoke Alpha",
        "Arbitrary Bespoke Zulu",
    }


@pytest.mark.parametrize(
    (
        "corruption",
        "code",
    ),
    (
        (
            "role",
            "ROLE_DEFINITION_SCOPE_MISMATCH",
        ),
        (
            "capability",
            "CAPABILITY_BINDING_SCOPE_MISMATCH",
        ),
        (
            "scope",
            "SCOPE_BINDING_SCOPE_MISMATCH",
        ),
    ),
)
def test_cross_registry_scope_mismatch_fails_closed(
    corruption: str,
    code: str,
) -> None:
    occupancy = _occupancy()

    role = _role()

    capability = _capability(
        "cap-a",
        (
            "PRACTICE_DISPUTES",
        ),
    )

    scope = _scope(
        "scope-a",
        offices=(
            "office:jhb",
        ),
    )

    if corruption == "role":
        role = _role(
            role_id="role-wrong",
            role_revision=ROLE_A_REVISION,
        )

    if corruption == "capability":
        capability = _capability(
            "cap-a",
            (
                "PRACTICE_DISPUTES",
            ),
            role_id="role-wrong",
        )

    if corruption == "scope":
        scope = _scope(
            "scope-a",
            role_id="role-wrong",
            offices=(
                "office:jhb",
            ),
        )

    (
        hydrator,
        _,
        _,
        _,
        _,
    ) = _hydrator(
        occupancies=(
            occupancy,
        ),
        roles={
            (
                ROLE_A,
                ROLE_A_REVISION,
            ): role,
        },
        capabilities={
            (
                ROLE_A,
                ROLE_A_REVISION,
            ): (
                capability,
            ),
        },
        scopes={
            (
                ROLE_A,
                ROLE_A_REVISION,
            ): (
                scope,
            ),
        },
    )

    with pytest.raises(
        LegalProductiveWorkOperatingContextHydratorError,
        match=code,
    ):
        hydrator.hydrate(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            at=NOW,
            session=_session(),
        )


def test_duplicate_occupancy_for_same_exact_role_revision_deduplicates_reads() -> None:
    first = _occupancy(
        binding_id="occupancy-a",
    )

    duplicate = _occupancy(
        binding_id="occupancy-b",
    )

    (
        hydrator,
        _,
        role_registry,
        capability_registry,
        scope_registry,
    ) = _hydrator(
        occupancies=(
            duplicate,
            first,
        ),
        roles={
            (
                ROLE_A,
                ROLE_A_REVISION,
            ): _role(),
        },
    )

    result = hydrator.hydrate(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        at=NOW,
        session=_session(),
    )

    assert len(result) == 1
    assert len(role_registry.calls) == 1
    assert len(capability_registry.calls) == 1
    assert len(scope_registry.calls) == 1


def test_hydrator_exposes_no_mutation_access_or_financial_authority() -> None:
    (
        hydrator,
        _,
        _,
        _,
        _,
    ) = _hydrator()

    for forbidden in (
        "authorize",
        "grant_permission",
        "grant_access",
        "assign",
        "supervise",
        "create_role",
        "bind_role",
        "pay",
        "invoice",
        "settle",
    ):
        assert not hasattr(
            hydrator,
            forbidden,
        )


# SOVEREIGN SEPARATION:
# occupancy != authorization
# role definition != permission
# capability metadata != IAM
# organizational scope metadata != record or matter access
# operating context != assignment or supervision
# financial execution remains exclusively outside this hydrator
