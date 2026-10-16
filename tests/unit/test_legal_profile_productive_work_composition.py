"""
TITLE: WILSY OS Legal Profile Productive Work Composition Unit Certificate

VERSION: v1.0.0-PW-P1-RED-PROFILE-PRODUCTIVE-WORK-COMPOSITION

EPITOME:
    Freeze the missing pure composition contract that converts already-governed
    Legal operating-role occupancy, capability metadata, scope metadata,
    assignment, supervision and work-item truth into one immutable principal
    daily-work projection without manufacturing IAM, assignment, supervision,
    legal, financial, payment or settlement authority.

AUTHORITY BOUNDARY:
    Read-model composition only. Operating-role title, capability metadata,
    scope metadata and occupancy are descriptive/non-authorizing. The composer
    may consume independently governed authority results but may never infer
    authorization from role names or capability IDs.

TENANT POSTURE:
    Exact tenant/principal inputs only. Foreign-tenant work, assignment,
    supervision or operating-role context must fail closed.

FINANCIAL POSTURE:
    NONE. No billing, payment, settlement or Kennel EOS authority.

CHANGELOG:
    2026-10-15 v1.0.0-PW-P1-RED-PROFILE-PRODUCTIVE-WORK-COMPOSITION
    freezes the test-first contract before production implementation.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta

import pytest

from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkCompositionError,
    LegalProductiveWorkOperatingContext,
    LegalProductiveWorkProjection,
    compose_legal_productive_work,
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


NOW = datetime(2026, 10, 15, 18, 0, tzinfo=UTC)
TENANT = "tenant-a"
PRINCIPAL = "principal-a"
OTHER_PRINCIPAL = "principal-b"
MATTER = "matter-a"


def _work(
    work_item_id: str,
    *,
    tenant_id: str = TENANT,
    matter_id: str = MATTER,
    due_at: datetime | None = None,
    created_at: datetime = NOW,
) -> LegalWorkItem:
    return LegalWorkItem(
        work_item_id=work_item_id,
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        title=f"Work {work_item_id}",
        source_kind="LEGAL_WORKFLOW_STAGE",
        source_reference=f"stage:{work_item_id}",
        source_evidence_fingerprint=("a" * 128),
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
    *,
    tenant_id: str = TENANT,
    assignee: str = PRINCIPAL,
) -> LegalWorkAssignment:
    return LegalWorkAssignment(
        assignment_id=assignment_id,
        tenant_id=tenant_id,
        case_matter_id=MATTER,
        work_item_id=work_item_id,
        assignee_principal_id=assignee,
        assigned_by_principal_id="principal-assigner",
        assigned_at=NOW,
        assignment_reason_reference="reason:staffing",
        authorization_evidence_reference="authz:assignment",
        supersedes_assignment_id=None,
    )


def _supervision(
    binding_id: str,
    work_item_id: str,
    *,
    tenant_id: str = TENANT,
    supervisor: str = PRINCIPAL,
    supervisee: str = OTHER_PRINCIPAL,
) -> LegalWorkSupervisionBinding:
    return LegalWorkSupervisionBinding(
        supervision_binding_id=binding_id,
        tenant_id=tenant_id,
        case_matter_id=MATTER,
        scope=LegalSupervisionScope.WORK_ITEM,
        work_item_id=work_item_id,
        supervisee_principal_id=supervisee,
        supervisor_principal_id=supervisor,
        control_level=LegalSupervisionControlLevel.REVIEW_REQUIRED,
        supervision_plan_reference="plan:supervision",
        supervision_basis_reference="basis:engagement",
        effective_from=NOW - timedelta(hours=1),
        effective_until=None,
        supersedes_supervision_binding_id=None,
    )


def _context(
    role_id: str,
    *,
    capabilities: tuple[str, ...] = (),
    offices: tuple[str, ...] = (),
    practices: tuple[str, ...] = (),
    business_units: tuple[str, ...] = (),
    jurisdictions: tuple[str, ...] = (),
) -> LegalProductiveWorkOperatingContext:
    return LegalProductiveWorkOperatingContext(
        operating_role_id=role_id,
        operating_role_revision=1,
        display_name=f"Role {role_id}",
        capability_ids=capabilities,
        office_references=offices,
        practice_references=practices,
        business_unit_references=business_units,
        jurisdiction_references=jurisdictions,
    )


def test_projection_is_immutable_and_principal_tenant_scoped() -> None:
    work = _work(
        "work-a",
        due_at=NOW + timedelta(hours=4),
    )

    projection = compose_legal_productive_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        operating_contexts=(
            _context(
                "custom-disputes-associate",
                capabilities=("CAP_MATTER_EXECUTION",),
                practices=("DISPUTES",),
            ),
        ),
        work_items=(work,),
        assignments=(
            _assignment("assignment-a", "work-a"),
        ),
        supervision_bindings=(),
    )

    assert isinstance(
        projection,
        LegalProductiveWorkProjection,
    )
    assert projection.tenant_id == TENANT
    assert projection.principal_id == PRINCIPAL
    assert projection.as_of == NOW
    assert tuple(
        item.work_item_id
        for item in projection.assigned_work_items
    ) == ("work-a",)

    with pytest.raises(
        (FrozenInstanceError, AttributeError),
    ):
        projection.principal_id = "principal-mutated"  # type: ignore[misc]


def test_custom_role_title_does_not_require_source_code_branch() -> None:
    projection = compose_legal_productive_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        operating_contexts=(
            _context(
                "tenant-defined-principal-associate-za",
                capabilities=(
                    "CAP_MATTER_EXECUTION",
                    "CAP_DOCUMENT_REVIEW",
                ),
                offices=("JOHANNESBURG",),
                practices=("DISPUTES",),
                jurisdictions=("ZA",),
            ),
        ),
        work_items=(
            _work("work-custom"),
        ),
        assignments=(
            _assignment(
                "assignment-custom",
                "work-custom",
            ),
        ),
        supervision_bindings=(),
    )

    assert tuple(
        context.operating_role_id
        for context in projection.operating_contexts
    ) == ("tenant-defined-principal-associate-za",)

    assert tuple(
        item.work_item_id
        for item in projection.assigned_work_items
    ) == ("work-custom",)


def test_multi_role_context_is_deterministic_and_deduplicated() -> None:
    work = _work("work-one")

    projection = compose_legal_productive_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        operating_contexts=(
            _context(
                "matter-partner",
                capabilities=("CAP_SUPERVISION",),
            ),
            _context(
                "practice-group-head",
                capabilities=(
                    "CAP_SUPERVISION",
                    "CAP_PRACTICE_OVERSIGHT",
                ),
            ),
        ),
        work_items=(work,),
        assignments=(
            _assignment("assignment-one", "work-one"),
            _assignment("assignment-two", "work-one"),
        ),
        supervision_bindings=(),
    )

    assert tuple(
        context.operating_role_id
        for context in projection.operating_contexts
    ) == (
        "matter-partner",
        "practice-group-head",
    )

    assert projection.capability_ids == (
        "CAP_PRACTICE_OVERSIGHT",
        "CAP_SUPERVISION",
    )

    assert tuple(
        item.work_item_id
        for item in projection.assigned_work_items
    ) == ("work-one",)


def test_assignment_controls_personal_work_not_role_name() -> None:
    assigned = _work("work-assigned")
    unassigned = _work("work-unassigned")

    projection = compose_legal_productive_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        operating_contexts=(
            _context(
                "senior-lawyer-whose-title-grants-nothing",
                capabilities=("CAP_MATTER_EXECUTION",),
            ),
        ),
        work_items=(assigned, unassigned),
        assignments=(
            _assignment(
                "assignment-assigned",
                "work-assigned",
            ),
            _assignment(
                "assignment-other",
                "work-unassigned",
                assignee=OTHER_PRINCIPAL,
            ),
        ),
        supervision_bindings=(),
    )

    assert tuple(
        item.work_item_id
        for item in projection.assigned_work_items
    ) == ("work-assigned",)


def test_supervision_projects_review_work_without_reassigning_it() -> None:
    supervised = _work("work-supervised")

    projection = compose_legal_productive_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        operating_contexts=(
            _context(
                "supervising-lawyer",
                capabilities=("CAP_SUPERVISION",),
            ),
        ),
        work_items=(supervised,),
        assignments=(
            _assignment(
                "assignment-supervisee",
                "work-supervised",
                assignee=OTHER_PRINCIPAL,
            ),
        ),
        supervision_bindings=(
            _supervision(
                "supervision-a",
                "work-supervised",
            ),
        ),
    )

    assert projection.assigned_work_items == ()
    assert tuple(
        item.work_item_id
        for item in projection.supervised_work_items
    ) == ("work-supervised",)


def test_due_and_overdue_are_derived_without_mutating_work_truth() -> None:
    overdue = _work(
        "work-overdue",
        created_at=NOW - timedelta(hours=1),
        due_at=NOW - timedelta(minutes=1),
    )
    due_soon = _work(
        "work-soon",
        due_at=NOW + timedelta(hours=2),
    )
    later = _work(
        "work-later",
        due_at=NOW + timedelta(days=2),
    )

    projection = compose_legal_productive_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        operating_contexts=(
            _context("attorney"),
        ),
        work_items=(
            later,
            due_soon,
            overdue,
        ),
        assignments=(
            _assignment("assignment-later", "work-later"),
            _assignment("assignment-soon", "work-soon"),
            _assignment(
                "assignment-overdue",
                "work-overdue",
            ),
        ),
        supervision_bindings=(),
        due_soon_window=timedelta(hours=24),
    )

    assert tuple(
        item.work_item_id
        for item in projection.overdue_work_items
    ) == ("work-overdue",)

    assert tuple(
        item.work_item_id
        for item in projection.due_soon_work_items
    ) == ("work-soon",)


def test_foreign_tenant_truth_fails_closed() -> None:
    with pytest.raises(
        LegalProductiveWorkCompositionError,
        match="TENANT",
    ):
        compose_legal_productive_work(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            as_of=NOW,
            operating_contexts=(
                _context("attorney"),
            ),
            work_items=(
                _work(
                    "foreign-work",
                    tenant_id="tenant-b",
                ),
            ),
            assignments=(),
            supervision_bindings=(),
        )


def test_missing_assignment_does_not_become_personal_work() -> None:
    projection = compose_legal_productive_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        operating_contexts=(
            _context(
                "tenant-defined-lawyer",
                capabilities=("CAP_MATTER_EXECUTION",),
            ),
        ),
        work_items=(
            _work("unassigned-work"),
        ),
        assignments=(),
        supervision_bindings=(),
    )

    assert projection.assigned_work_items == ()


def test_composer_exposes_no_command_or_financial_authority() -> None:
    projection = compose_legal_productive_work(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        operating_contexts=(
            _context(
                "finance-profile",
                capabilities=(
                    "FINANCE_BILLING",
                    "FINANCE_TRUST_ACCOUNTING",
                ),
            ),
        ),
        work_items=(),
        assignments=(),
        supervision_bindings=(),
    )

    assert not hasattr(
        projection,
        "authorized_commands",
    )
    assert not hasattr(
        projection,
        "permissions",
    )
    assert not hasattr(
        projection,
        "payment_authority",
    )
    assert not hasattr(
        projection,
        "settlement_authority",
    )


def test_projection_order_is_stable_independent_of_input_order() -> None:
    one = _work(
        "work-one",
        due_at=NOW + timedelta(hours=3),
    )
    two = _work(
        "work-two",
        due_at=NOW + timedelta(hours=1),
    )

    kwargs = {
        "tenant_id": TENANT,
        "principal_id": PRINCIPAL,
        "as_of": NOW,
        "operating_contexts": (
            _context("custom-role"),
        ),
        "supervision_bindings": (),
    }

    forward = compose_legal_productive_work(
        **kwargs,
        work_items=(one, two),
        assignments=(
            _assignment("assignment-one", "work-one"),
            _assignment("assignment-two", "work-two"),
        ),
    )

    reverse = compose_legal_productive_work(
        **kwargs,
        work_items=(two, one),
        assignments=(
            _assignment("assignment-two", "work-two"),
            _assignment("assignment-one", "work-one"),
        ),
    )

    assert forward == reverse


# AUTHORITY BOUNDARY:
# deterministic read-model composition only; no IAM, assignment creation,
# supervision creation, legal authority, billing, payment or settlement.
