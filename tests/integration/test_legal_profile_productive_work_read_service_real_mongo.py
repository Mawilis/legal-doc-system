"""
TITLE: WILSY OS Legal Profile Productive Work Read Service Real-Mongo Certificate

VERSION: v1.0.0-PW-P5-DURABLE-PRODUCTIVE-WORK-REAL-MONGO

EPITOME:
    Certify that one principal's productive-work projection is reconstructed
    from durable work-item, current-assignment, and current-supervision truth
    inside one caller-owned Mongo transaction.

AUTHORITY BOUNDARY:
    Read/projection only. No IAM, role grant, assignment command, supervision
    command, workflow mutation, billing, payment, execution, or settlement.

FINANCIAL POSTURE:
    NONE. Kennel EOS exclusively owns financial execution and settlement.
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
from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
)
from tools.eos.legal_operations.domain.legal_work_supervision_binding import (
    LegalSupervisionControlLevel,
    LegalSupervisionScope,
    LegalWorkSupervisionBinding,
)
from tools.eos.legal_operations.registry.legal_work_assignment_registry import (
    LegalWorkAssignmentRegistry,
)
from tools.eos.legal_operations.registry.legal_work_item_registry import (
    LegalWorkItemRegistry,
)
from tools.eos.legal_operations.registry.legal_work_supervision_binding_registry import (
    LegalWorkSupervisionBindingRegistry,
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
)
from tools.eos.legal_operations.service.legal_profile_productive_work_read_service import (
    LegalProductiveWorkReadService,
    LegalProductiveWorkReadServiceTransactionRequiredError,
)


URI = os.environ["WILSY_PW_REAL_MONGO_URI"]

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
OTHER = "principal-b"

MATTER_ASSIGNED = "matter-assigned"
MATTER_REVIEW = "matter-review"
MATTER_SUPERVISED = "matter-supervised"


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
        "wilsy_pw_productive_"
        + uuid.uuid4().hex
    ]

    work_collection = database[
        "legal_work_items"
    ]

    assignment_collection = database[
        "legal_work_assignments"
    ]

    supervision_collection = database[
        "legal_work_supervision_bindings"
    ]

    role_collection = database[
        "legal_operating_role_definitions"
    ]

    capability_collection = database[
        "legal_operating_role_capability_bindings"
    ]

    scope_collection = database[
        "legal_operating_role_scope_bindings"
    ]

    occupancy_collection = database[
        "legal_principal_operating_role_bindings"
    ]

    work_registry = LegalWorkItemRegistry(
        work_collection
    )

    assignment_registry = LegalWorkAssignmentRegistry(
        assignment_collection
    )

    supervision_registry = LegalWorkSupervisionBindingRegistry(
        supervision_collection
    )

    role_registry = LegalOperatingRoleDefinitionRegistry(
        role_collection
    )

    capability_registry = LegalOperatingRoleCapabilityBindingRegistry(
        capability_collection
    )

    scope_registry = LegalOperatingRoleScopeBindingRegistry(
        scope_collection
    )

    occupancy_registry = LegalPrincipalOperatingRoleBindingRegistry(
        occupancy_collection
    )

    work_registry.ensure_indexes()
    assignment_registry.ensure_indexes()
    supervision_registry.ensure_indexes()
    role_registry.ensure_indexes()
    capability_registry.ensure_indexes()
    scope_registry.ensure_indexes()
    occupancy_registry.ensure_indexes()

    _persist_operating_context_fixture(
        client,
        role_registry,
        capability_registry,
        scope_registry,
        occupancy_registry,
    )

    context_hydrator = LegalProductiveWorkOperatingContextHydrator(
        principal_operating_role_registry=occupancy_registry,
        operating_role_definition_registry=role_registry,
        operating_role_capability_registry=capability_registry,
        operating_role_scope_registry=scope_registry,
    )

    service = LegalProductiveWorkReadService(
        work_item_registry=work_registry,
        assignment_registry=assignment_registry,
        supervision_registry=supervision_registry,
        operating_context_hydrator=context_hydrator,
    )

    try:
        yield (
            client,
            database,
            work_registry,
            assignment_registry,
            supervision_registry,
            service,
        )
    finally:
        client.drop_database(
            database.name
        )
        client.close()


def _work(
    work_item_id: str,
    matter_id: str,
    *,
    created_at: datetime = NOW,
    due_at: datetime | None = None,
) -> LegalWorkItem:
    return LegalWorkItem(
        work_item_id=work_item_id,
        tenant_id=TENANT,
        case_matter_id=matter_id,
        title=f"Work {work_item_id}",
        source_kind="LEGAL_WORKFLOW_STAGE",
        source_reference=f"stage:{work_item_id}",
        source_evidence_fingerprint="a" * 128,
        status="OPEN",
        created_at=created_at,
        due_at=due_at,
        completion_evidence_reference=None,
        completion_evidence_fingerprint=None,
        completed_at=None,
        cancellation_reason_reference=None,
        cancelled_at=None,
    )


def _assignment(
    assignment_id: str,
    work_item_id: str,
    matter_id: str,
    assignee: str,
    *,
    assigned_at: datetime,
    supersedes: str | None = None,
) -> LegalWorkAssignment:
    return LegalWorkAssignment(
        assignment_id=assignment_id,
        tenant_id=TENANT,
        case_matter_id=matter_id,
        work_item_id=work_item_id,
        assignee_principal_id=assignee,
        assigned_by_principal_id="principal-assigner",
        assigned_at=assigned_at,
        assignment_reason_reference="reason:staffing",
        authorization_evidence_reference="authz:assignment",
        supersedes_assignment_id=supersedes,
    )


def _supervision(
    binding_id: str,
    *,
    matter_id: str,
    scope: LegalSupervisionScope,
    work_item_id: str | None,
    supervisor: str = PRINCIPAL,
    supervisee: str = OTHER,
    effective_from: datetime = NOW,
    effective_until: datetime | None = None,
    supersedes: str | None = None,
) -> LegalWorkSupervisionBinding:
    return LegalWorkSupervisionBinding(
        supervision_binding_id=binding_id,
        tenant_id=TENANT,
        case_matter_id=matter_id,
        scope=scope,
        work_item_id=work_item_id,
        supervisee_principal_id=supervisee,
        supervisor_principal_id=supervisor,
        control_level=(
            LegalSupervisionControlLevel.REVIEW_REQUIRED
        ),
        supervision_plan_reference="plan:review",
        supervision_basis_reference="basis:engagement",
        effective_from=effective_from,
        effective_until=effective_until,
        supersedes_supervision_binding_id=supersedes,
    )


def _persist_operating_context_fixture(
    client: MongoClient[Any],
    role_registry: LegalOperatingRoleDefinitionRegistry,
    capability_registry: LegalOperatingRoleCapabilityBindingRegistry,
    scope_registry: LegalOperatingRoleScopeBindingRegistry,
    occupancy_registry: LegalPrincipalOperatingRoleBindingRegistry,
) -> None:
    lead_role = LegalOperatingRoleDefinition(
        tenant_id=TENANT,
        operating_role_id="tenant-defined-lead-specialist",
        role_revision=1,
        display_name="Lead Specialist",
        description="Durable tenant-defined lead specialist",
        effective_from=NOW,
        supersedes_fingerprint=None,
    )

    reviewer_role = LegalOperatingRoleDefinition(
        tenant_id=TENANT,
        operating_role_id="tenant-defined-cross-border-reviewer",
        role_revision=1,
        display_name="Cross Border Reviewer",
        description="Durable tenant-defined cross-border reviewer",
        effective_from=NOW,
        supersedes_fingerprint=None,
    )

    lead_capability = LegalOperatingRoleCapabilityBinding(
        tenant_id=TENANT,
        capability_binding_id="capability-lead",
        operating_role_id=lead_role.operating_role_id,
        operating_role_revision=1,
        capability_binding_revision=1,
        capability_ids=(
            "PRACTICE_DISPUTES",
            "PRACTICE_CORPORATE",
        ),
        effective_from=NOW,
        supersedes_fingerprint=None,
    )

    reviewer_capability = LegalOperatingRoleCapabilityBinding(
        tenant_id=TENANT,
        capability_binding_id="capability-reviewer",
        operating_role_id=reviewer_role.operating_role_id,
        operating_role_revision=1,
        capability_binding_revision=1,
        capability_ids=(
            "PRACTICE_CORPORATE",
        ),
        effective_from=NOW,
        supersedes_fingerprint=None,
    )

    lead_scope = LegalOperatingRoleScopeBinding(
        tenant_id=TENANT,
        scope_binding_id="scope-lead",
        operating_role_id=lead_role.operating_role_id,
        operating_role_revision=1,
        scope_binding_revision=1,
        office_references=(
            "office:jhb",
        ),
        practice_references=(
            "practice:disputes",
        ),
        business_unit_references=(),
        jurisdiction_references=(
            "jurisdiction:ZA",
        ),
        effective_from=NOW,
        supersedes_fingerprint=None,
    )

    reviewer_scope = LegalOperatingRoleScopeBinding(
        tenant_id=TENANT,
        scope_binding_id="scope-reviewer",
        operating_role_id=reviewer_role.operating_role_id,
        operating_role_revision=1,
        scope_binding_revision=1,
        office_references=(
            "office:jhb",
        ),
        practice_references=(
            "practice:corporate",
        ),
        business_unit_references=(),
        jurisdiction_references=(
            "jurisdiction:ZA",
        ),
        effective_from=NOW,
        supersedes_fingerprint=None,
    )

    principal_lead = LegalPrincipalOperatingRoleBinding(
        tenant_id=TENANT,
        principal_operating_role_binding_id="occupancy-principal-lead",
        binding_revision=1,
        principal_id=PRINCIPAL,
        operating_role_id=lead_role.operating_role_id,
        operating_role_revision=1,
        effective_from=NOW,
        effective_until=None,
        source_reference="source:pw-p8f",
        source_evidence_fingerprint="a" * 128,
        supersedes_fingerprint=None,
    )

    principal_reviewer = LegalPrincipalOperatingRoleBinding(
        tenant_id=TENANT,
        principal_operating_role_binding_id="occupancy-principal-reviewer",
        binding_revision=1,
        principal_id=PRINCIPAL,
        operating_role_id=reviewer_role.operating_role_id,
        operating_role_revision=1,
        effective_from=NOW,
        effective_until=None,
        source_reference="source:pw-p8f",
        source_evidence_fingerprint="b" * 128,
        supersedes_fingerprint=None,
    )

    other_lead = LegalPrincipalOperatingRoleBinding(
        tenant_id=TENANT,
        principal_operating_role_binding_id="occupancy-other-lead",
        binding_revision=1,
        principal_id=OTHER,
        operating_role_id=lead_role.operating_role_id,
        operating_role_revision=1,
        effective_from=NOW,
        effective_until=None,
        source_reference="source:pw-p8f",
        source_evidence_fingerprint="c" * 128,
        supersedes_fingerprint=None,
    )

    with client.start_session() as session:
        with session.start_transaction():
            role_registry.persist_revision(
                lead_role,
                session=session,
            )

            role_registry.persist_revision(
                reviewer_role,
                session=session,
            )

            capability_registry.persist_revision(
                lead_capability,
                session=session,
            )

            capability_registry.persist_revision(
                reviewer_capability,
                session=session,
            )

            scope_registry.persist_revision(
                lead_scope,
                session=session,
            )

            scope_registry.persist_revision(
                reviewer_scope,
                session=session,
            )

            occupancy_registry.persist_revision(
                principal_lead,
                session=session,
            )

            occupancy_registry.persist_revision(
                principal_reviewer,
                session=session,
            )

            occupancy_registry.persist_revision(
                other_lead,
                session=session,
            )


def _persist_fixture(
    client: MongoClient[Any],
    work_registry: LegalWorkItemRegistry,
    assignment_registry: LegalWorkAssignmentRegistry,
    supervision_registry: LegalWorkSupervisionBindingRegistry,
) -> tuple[
    LegalWorkItem,
    LegalWorkItem,
    LegalWorkItem,
    LegalWorkItem,
    LegalWorkAssignment,
]:
    assigned = _work(
        "work-assigned",
        MATTER_ASSIGNED,
        due_at=NOW + timedelta(hours=4),
    )

    reviewed = _work(
        "work-reviewed",
        MATTER_REVIEW,
        due_at=NOW + timedelta(hours=2),
    )

    matter_one = _work(
        "work-matter-one",
        MATTER_SUPERVISED,
    )

    matter_two = _work(
        "work-matter-two",
        MATTER_SUPERVISED,
    )

    assignment = _assignment(
        "assignment-a",
        assigned.work_item_id,
        assigned.case_matter_id,
        PRINCIPAL,
        assigned_at=NOW,
    )

    work_supervision = _supervision(
        "supervision-work",
        matter_id=reviewed.case_matter_id,
        scope=LegalSupervisionScope.WORK_ITEM,
        work_item_id=reviewed.work_item_id,
    )

    matter_supervision = _supervision(
        "supervision-matter",
        matter_id=MATTER_SUPERVISED,
        scope=LegalSupervisionScope.MATTER,
        work_item_id=None,
    )

    with client.start_session() as session:
        with session.start_transaction():
            for item in (
                assigned,
                reviewed,
                matter_one,
                matter_two,
            ):
                work_registry.create_or_replay(
                    item,
                    session=session,
                )

            assignment_registry.persist(
                assignment,
                session=session,
            )

            supervision_registry.persist(
                work_supervision,
                session=session,
            )

            supervision_registry.persist(
                matter_supervision,
                session=session,
            )

    return (
        assigned,
        reviewed,
        matter_one,
        matter_two,
        assignment,
    )


def test_real_durable_projection_reconstructs_assignment_and_supervision(
    mongo_context: Any,
) -> None:
    (
        client,
        _,
        work_registry,
        assignment_registry,
        supervision_registry,
        service,
    ) = mongo_context

    (
        assigned,
        reviewed,
        matter_one,
        matter_two,
        _,
    ) = _persist_fixture(
        client,
        work_registry,
        assignment_registry,
        supervision_registry,
    )

    with client.start_session() as session:
        with session.start_transaction():
            projection = service.project(
                tenant_id=TENANT,
                principal_id=PRINCIPAL,
                as_of=NOW + timedelta(minutes=1),
                session=session,
            )

    assert tuple(
        item.work_item_id
        for item in projection.assigned_work_items
    ) == (
        assigned.work_item_id,
    )

    assert {
        item.work_item_id
        for item in projection.supervised_work_items
    } == {
        reviewed.work_item_id,
        matter_one.work_item_id,
        matter_two.work_item_id,
    }

    assert tuple(
        context.operating_role_id
        for context in projection.operating_contexts
    ) == (
        "tenant-defined-cross-border-reviewer",
        "tenant-defined-lead-specialist",
    )


def test_real_reassignment_changes_personal_productive_work(
    mongo_context: Any,
) -> None:
    (
        client,
        _,
        work_registry,
        assignment_registry,
        supervision_registry,
        service,
    ) = mongo_context

    (
        assigned,
        _,
        _,
        _,
        first,
    ) = _persist_fixture(
        client,
        work_registry,
        assignment_registry,
        supervision_registry,
    )

    with client.start_session() as session:
        with session.start_transaction():
            before = service.project(
                tenant_id=TENANT,
                principal_id=PRINCIPAL,
                as_of=NOW + timedelta(minutes=1),
                session=session,
            )

    assert assigned.work_item_id in {
        item.work_item_id
        for item in before.assigned_work_items
    }

    successor = _assignment(
        "assignment-b",
        assigned.work_item_id,
        assigned.case_matter_id,
        OTHER,
        assigned_at=NOW + timedelta(minutes=2),
        supersedes=first.assignment_id,
    )

    with client.start_session() as session:
        with session.start_transaction():
            assignment_registry.persist(
                successor,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            after_old = service.project(
                tenant_id=TENANT,
                principal_id=PRINCIPAL,
                as_of=NOW + timedelta(minutes=3),
                session=session,
            )

            after_new = service.project(
                tenant_id=TENANT,
                principal_id=OTHER,
                as_of=NOW + timedelta(minutes=3),
                session=session,
            )

    assert assigned.work_item_id not in {
        item.work_item_id
        for item in after_old.assigned_work_items
    }

    assert assigned.work_item_id in {
        item.work_item_id
        for item in after_new.assigned_work_items
    }


def test_real_expired_supervision_drops_from_projection(
    mongo_context: Any,
) -> None:
    (
        client,
        _,
        work_registry,
        assignment_registry,
        supervision_registry,
        service,
    ) = mongo_context

    reviewed = _work(
        "work-expiring-review",
        MATTER_REVIEW,
    )

    binding = _supervision(
        "supervision-expiring",
        matter_id=MATTER_REVIEW,
        scope=LegalSupervisionScope.WORK_ITEM,
        work_item_id=reviewed.work_item_id,
        effective_until=NOW + timedelta(hours=1),
    )

    with client.start_session() as session:
        with session.start_transaction():
            work_registry.create_or_replay(
                reviewed,
                session=session,
            )

            supervision_registry.persist(
                binding,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            before = service.project(
                tenant_id=TENANT,
                principal_id=PRINCIPAL,
                as_of=NOW + timedelta(minutes=30),
                session=session,
            )

            after = service.project(
                tenant_id=TENANT,
                principal_id=PRINCIPAL,
                as_of=NOW + timedelta(hours=2),
                session=session,
            )

    assert reviewed.work_item_id in {
        item.work_item_id
        for item in before.supervised_work_items
    }

    assert reviewed.work_item_id not in {
        item.work_item_id
        for item in after.supervised_work_items
    }


def test_real_foreign_tenant_projection_is_empty(
    mongo_context: Any,
) -> None:
    (
        client,
        _,
        work_registry,
        assignment_registry,
        supervision_registry,
        service,
    ) = mongo_context

    _persist_fixture(
        client,
        work_registry,
        assignment_registry,
        supervision_registry,
    )

    with client.start_session() as session:
        with session.start_transaction():
            projection = service.project(
                tenant_id="tenant-b",
                principal_id=PRINCIPAL,
                as_of=NOW + timedelta(minutes=1),
                session=session,
            )

    assert projection.assigned_work_items == ()
    assert projection.supervised_work_items == ()


def test_real_inactive_transaction_rejected_before_durable_reads(
    mongo_context: Any,
) -> None:
    (
        client,
        _,
        _,
        _,
        _,
        service,
    ) = mongo_context

    with client.start_session() as session:
        with pytest.raises(
            LegalProductiveWorkReadServiceTransactionRequiredError,
            match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
        ):
            service.project(
                tenant_id=TENANT,
                principal_id=PRINCIPAL,
                as_of=NOW,
                session=session,
            )


# AUTHORITY BOUNDARY:
# durable read/projection only.
# No IAM, assignment/supervision mutation, workflow mutation, or financial
# execution authority.
