"""
TITLE: WILSY OS CX27 Productive-Work Operating-Context Hydrator Real-Mongo Certificate

VERSION: v1.0.0-PW-P7C-CX27-OPERATING-CONTEXT-HYDRATOR-REAL-MONGO

EPITOME:
    Certify durable CX27 operating-context hydration from real transactional
    Mongo truth across principal occupancy, exact occupied role revision,
    capability metadata and organizational-scope metadata.

AUTHORITY BOUNDARY:
    Descriptive productive-work composition only. No IAM permission,
    record/client/matter access, assignment, supervision, workflow,
    professional, financial, execution, or settlement authority.

TRANSACTION:
    Every durable read occurs through one caller-owned active transaction.
"""

from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from pymongo import MongoClient

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
from tools.eos.legal_operations.registry.legal_operating_role_capability_binding_registry import (
    LegalOperatingRoleCapabilityBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_operating_role_definition_registry import (
    LegalOperatingRoleDefinitionRegistry,
)
from tools.eos.legal_operations.registry.legal_operating_role_scope_binding_registry import (
    LegalOperatingRoleScopeBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_principal_operating_role_binding_registry import (
    LegalPrincipalOperatingRoleBindingRegistry,
)
from tools.eos.legal_operations.service.legal_productive_work_operating_context_hydrator import (
    LegalProductiveWorkOperatingContextHydrator,
    LegalProductiveWorkOperatingContextHydratorTransactionRequiredError,
)


URI = os.environ[
    "WILSY_PW_P7C_REAL_MONGO_URI"
]

NOW = datetime(
    2026,
    10,
    15,
    18,
    0,
    tzinfo=UTC,
)

TENANT = "tenant-p7c"
PRINCIPAL = "principal-p7c"

ROLE_A = "role-p7c-disputes-lead"
ROLE_B = "role-p7c-cross-border-reviewer"


@pytest.fixture()
def mongo_context() -> Any:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )

    client.admin.command(
        "ping"
    )

    database = client[
        "wilsy_pw_p7c_"
        + uuid.uuid4().hex
    ]

    role_registry = LegalOperatingRoleDefinitionRegistry(
        database[
            "legal_operating_role_definitions"
        ]
    )

    capability_registry = (
        LegalOperatingRoleCapabilityBindingRegistry(
            database[
                "legal_operating_role_capability_bindings"
            ]
        )
    )

    scope_registry = (
        LegalOperatingRoleScopeBindingRegistry(
            database[
                "legal_operating_role_scope_bindings"
            ]
        )
    )

    occupancy_registry = (
        LegalPrincipalOperatingRoleBindingRegistry(
            database[
                "legal_principal_operating_role_bindings"
            ]
        )
    )

    role_registry.ensure_indexes()
    capability_registry.ensure_indexes()
    scope_registry.ensure_indexes()
    occupancy_registry.ensure_indexes()

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

    try:
        yield (
            client,
            database,
            role_registry,
            capability_registry,
            scope_registry,
            occupancy_registry,
            hydrator,
        )
    finally:
        client.drop_database(
            database.name
        )
        client.close()


def _role(
    *,
    role_id: str,
    revision: int,
    display_name: str,
    predecessor: str | None = None,
    effective_from: datetime = NOW,
) -> LegalOperatingRoleDefinition:
    return LegalOperatingRoleDefinition(
        tenant_id=TENANT,
        operating_role_id=role_id,
        role_revision=revision,
        display_name=display_name,
        description="Durable tenant-defined operating role",
        effective_from=effective_from,
        supersedes_fingerprint=predecessor,
    )


def _capability(
    *,
    binding_id: str,
    role_id: str,
    role_revision: int,
    capabilities: tuple[str, ...],
    revision: int = 1,
    predecessor: str | None = None,
    effective_from: datetime = NOW,
) -> LegalOperatingRoleCapabilityBinding:
    return LegalOperatingRoleCapabilityBinding(
        tenant_id=TENANT,
        capability_binding_id=binding_id,
        operating_role_id=role_id,
        operating_role_revision=role_revision,
        capability_binding_revision=revision,
        capability_ids=capabilities,
        effective_from=effective_from,
        supersedes_fingerprint=predecessor,
    )


def _scope(
    *,
    binding_id: str,
    role_id: str,
    role_revision: int,
    offices: tuple[str, ...] = (),
    practices: tuple[str, ...] = (),
    business_units: tuple[str, ...] = (),
    jurisdictions: tuple[str, ...] = (),
    revision: int = 1,
    predecessor: str | None = None,
    effective_from: datetime = NOW,
) -> LegalOperatingRoleScopeBinding:
    return LegalOperatingRoleScopeBinding(
        tenant_id=TENANT,
        scope_binding_id=binding_id,
        operating_role_id=role_id,
        operating_role_revision=role_revision,
        scope_binding_revision=revision,
        office_references=offices,
        practice_references=practices,
        business_unit_references=business_units,
        jurisdiction_references=jurisdictions,
        effective_from=effective_from,
        supersedes_fingerprint=predecessor,
    )


def _occupancy(
    *,
    binding_id: str,
    role_id: str,
    role_revision: int,
    principal_id: str = PRINCIPAL,
    revision: int = 1,
    predecessor: str | None = None,
    effective_from: datetime = NOW,
    effective_until: datetime | None = None,
) -> LegalPrincipalOperatingRoleBinding:
    return LegalPrincipalOperatingRoleBinding(
        tenant_id=TENANT,
        principal_operating_role_binding_id=binding_id,
        binding_revision=revision,
        principal_id=principal_id,
        operating_role_id=role_id,
        operating_role_revision=role_revision,
        effective_from=effective_from,
        effective_until=effective_until,
        source_reference="source:p7c-operating-model",
        source_evidence_fingerprint="a" * 128,
        supersedes_fingerprint=predecessor,
    )


def _persist(
    client: MongoClient[Any],
    registry: Any,
    value: Any,
) -> Any:
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_revision(
                value,
                session=session,
            )


def _hydrate(
    client: MongoClient[Any],
    hydrator: LegalProductiveWorkOperatingContextHydrator,
    *,
    tenant_id: str = TENANT,
    principal_id: str = PRINCIPAL,
    at: datetime = NOW,
) -> Any:
    with client.start_session() as session:
        with session.start_transaction():
            return hydrator.hydrate(
                tenant_id=tenant_id,
                principal_id=principal_id,
                at=at,
                session=session,
            )


def test_real_active_transaction_required_before_any_read(
    mongo_context: Any,
) -> None:
    (
        client,
        _,
        _,
        _,
        _,
        _,
        hydrator,
    ) = mongo_context

    with pytest.raises(
        LegalProductiveWorkOperatingContextHydratorTransactionRequiredError,
        match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
    ):
        hydrator.hydrate(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            at=NOW,
            session=None,
        )

    with client.start_session() as inactive:
        with pytest.raises(
            LegalProductiveWorkOperatingContextHydratorTransactionRequiredError,
            match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
        ):
            hydrator.hydrate(
                tenant_id=TENANT,
                principal_id=PRINCIPAL,
                at=NOW,
                session=inactive,
            )


def test_real_exact_occupied_role_revision_not_newer_role_revision(
    mongo_context: Any,
) -> None:
    (
        client,
        _,
        role_registry,
        capability_registry,
        scope_registry,
        occupancy_registry,
        hydrator,
    ) = mongo_context

    role_v1 = _role(
        role_id=ROLE_A,
        revision=1,
        display_name="Disputes Lead V1",
    )

    _persist(
        client,
        role_registry,
        role_v1,
    )

    role_v2 = _role(
        role_id=ROLE_A,
        revision=2,
        display_name="Disputes Lead V2",
        predecessor=role_v1.fingerprint,
        effective_from=NOW + timedelta(hours=1),
    )

    _persist(
        client,
        role_registry,
        role_v2,
    )

    capability = _capability(
        binding_id="cap-role-a-v1",
        role_id=ROLE_A,
        role_revision=1,
        capabilities=(
            "PRACTICE_DISPUTES",
        ),
    )

    _persist(
        client,
        capability_registry,
        capability,
    )

    scope = _scope(
        binding_id="scope-role-a-v1",
        role_id=ROLE_A,
        role_revision=1,
        offices=(
            "office:jhb",
        ),
        practices=(
            "practice:disputes",
        ),
    )

    _persist(
        client,
        scope_registry,
        scope,
    )

    occupancy = _occupancy(
        binding_id="occupancy-role-a",
        role_id=ROLE_A,
        role_revision=1,
    )

    _persist(
        client,
        occupancy_registry,
        occupancy,
    )

    contexts = _hydrate(
        client,
        hydrator,
        at=NOW + timedelta(hours=2),
    )

    assert len(contexts) == 1
    assert contexts[0].operating_role_id == ROLE_A
    assert contexts[0].operating_role_revision == 1
    assert contexts[0].display_name == "Disputes Lead V1"
    assert contexts[0].capability_ids == (
        "PRACTICE_DISPUTES",
    )
    assert contexts[0].office_references == (
        "office:jhb",
    )


def test_real_multi_role_capability_and_scope_union(
    mongo_context: Any,
) -> None:
    (
        client,
        _,
        role_registry,
        capability_registry,
        scope_registry,
        occupancy_registry,
        hydrator,
    ) = mongo_context

    role_a = _role(
        role_id=ROLE_A,
        revision=1,
        display_name="Arbitrary Disputes Operator",
    )

    role_b = _role(
        role_id=ROLE_B,
        revision=1,
        display_name="Arbitrary Cross Border Operator",
    )

    _persist(
        client,
        role_registry,
        role_a,
    )

    _persist(
        client,
        role_registry,
        role_b,
    )

    for value in (
        _capability(
            binding_id="cap-a-1",
            role_id=ROLE_A,
            role_revision=1,
            capabilities=(
                "PRACTICE_DISPUTES",
                "PRACTICE_CORPORATE",
            ),
        ),
        _capability(
            binding_id="cap-a-2",
            role_id=ROLE_A,
            role_revision=1,
            capabilities=(
                "PRACTICE_CORPORATE",
            ),
        ),
        _capability(
            binding_id="cap-b-1",
            role_id=ROLE_B,
            role_revision=1,
            capabilities=(
                "PRACTICE_REAL_ESTATE",
            ),
        ),
    ):
        _persist(
            client,
            capability_registry,
            value,
        )

    for value in (
        _scope(
            binding_id="scope-a-office",
            role_id=ROLE_A,
            role_revision=1,
            offices=(
                "office:jhb",
                "office:cpt",
            ),
        ),
        _scope(
            binding_id="scope-a-practice",
            role_id=ROLE_A,
            role_revision=1,
            practices=(
                "practice:disputes",
            ),
            business_units=(
                "business-unit:africa",
            ),
            jurisdictions=(
                "jurisdiction:ZA",
            ),
        ),
        _scope(
            binding_id="scope-b",
            role_id=ROLE_B,
            role_revision=1,
            offices=(
                "office:london",
            ),
            jurisdictions=(
                "jurisdiction:GB",
            ),
        ),
    ):
        _persist(
            client,
            scope_registry,
            value,
        )

    for value in (
        _occupancy(
            binding_id="occupancy-z",
            role_id=ROLE_A,
            role_revision=1,
        ),
        _occupancy(
            binding_id="occupancy-a",
            role_id=ROLE_B,
            role_revision=1,
        ),
    ):
        _persist(
            client,
            occupancy_registry,
            value,
        )

    contexts = _hydrate(
        client,
        hydrator,
    )

    assert tuple(
        context.operating_role_id
        for context in contexts
    ) == tuple(
        sorted(
            (
                ROLE_A,
                ROLE_B,
            )
        )
    )

    by_role = {
        context.operating_role_id:
            context
        for context in contexts
    }

    assert by_role[
        ROLE_A
    ].capability_ids == (
        "PRACTICE_CORPORATE",
        "PRACTICE_DISPUTES",
    )

    assert by_role[
        ROLE_A
    ].office_references == (
        "office:cpt",
        "office:jhb",
    )

    assert by_role[
        ROLE_A
    ].practice_references == (
        "practice:disputes",
    )

    assert by_role[
        ROLE_A
    ].business_unit_references == (
        "business-unit:africa",
    )

    assert by_role[
        ROLE_A
    ].jurisdiction_references == (
        "jurisdiction:ZA",
    )

    assert by_role[
        ROLE_B
    ].capability_ids == (
        "PRACTICE_REAL_ESTATE",
    )

    assert by_role[
        ROLE_B
    ].office_references == (
        "office:london",
    )

    assert by_role[
        ROLE_B
    ].jurisdiction_references == (
        "jurisdiction:GB",
    )


def test_real_temporal_occupancy_controls_context_presence(
    mongo_context: Any,
) -> None:
    (
        client,
        _,
        role_registry,
        capability_registry,
        scope_registry,
        occupancy_registry,
        hydrator,
    ) = mongo_context

    role = _role(
        role_id=ROLE_A,
        revision=1,
        display_name="Temporary Reviewer",
    )

    _persist(
        client,
        role_registry,
        role,
    )

    _persist(
        client,
        capability_registry,
        _capability(
            binding_id="cap-temp",
            role_id=ROLE_A,
            role_revision=1,
            capabilities=(
                "PRACTICE_DISPUTES",
            ),
        ),
    )

    _persist(
        client,
        scope_registry,
        _scope(
            binding_id="scope-temp",
            role_id=ROLE_A,
            role_revision=1,
            jurisdictions=(
                "jurisdiction:ZA",
            ),
        ),
    )

    occupancy = _occupancy(
        binding_id="occupancy-temp",
        role_id=ROLE_A,
        role_revision=1,
        effective_from=NOW,
        effective_until=NOW + timedelta(hours=1),
    )

    _persist(
        client,
        occupancy_registry,
        occupancy,
    )

    before_expiry = _hydrate(
        client,
        hydrator,
        at=NOW + timedelta(minutes=30),
    )

    after_expiry = _hydrate(
        client,
        hydrator,
        at=NOW + timedelta(hours=2),
    )

    assert len(before_expiry) == 1
    assert after_expiry == ()


def test_real_foreign_tenant_and_principal_are_empty(
    mongo_context: Any,
) -> None:
    (
        client,
        _,
        role_registry,
        _,
        _,
        occupancy_registry,
        hydrator,
    ) = mongo_context

    role = _role(
        role_id=ROLE_A,
        revision=1,
        display_name="Tenant Scoped Operator",
    )

    _persist(
        client,
        role_registry,
        role,
    )

    occupancy = _occupancy(
        binding_id="occupancy-tenant-scope",
        role_id=ROLE_A,
        role_revision=1,
    )

    _persist(
        client,
        occupancy_registry,
        occupancy,
    )

    assert _hydrate(
        client,
        hydrator,
        tenant_id="tenant-neighbor",
    ) == ()

    assert _hydrate(
        client,
        hydrator,
        principal_id="principal-neighbor",
    ) == ()


# SOVEREIGN SEPARATION:
# principal occupancy != authorization
# exact operating-role revision != IAM role
# capability metadata != permission possession
# scope metadata != record/client/matter access
# operating context != assignment or supervision
# financial execution remains outside this hydrator
