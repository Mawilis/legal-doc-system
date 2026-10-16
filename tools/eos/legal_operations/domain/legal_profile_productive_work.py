"""
TITLE: WILSY OS Legal Profile Productive Work Composition

VERSION: v1.0.1-PW-P2-PROFILE-PRODUCTIVE-WORK-COMPOSITION

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_profile_productive_work.py

COLLABORATION / OWNERSHIP:
    Productive-work read service consumes this pure composition contract;
    Legal work, assignment and supervision domains retain source truth.

CERTIFICATION / UPDATE DATE: 2026-10-16

COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2.

SECURITY / PRIVACY POSTURE:
    Exact tenant/principal correlation; no PII logging or cross-tenant fallback.

EPITOME:
    Deterministically compose one principal's immutable Legal daily-work
    projection from already-governed operating-role metadata, work-item truth,
    assignment truth and supervision truth.

AUTHORITY BOUNDARY:
    Read-model composition only. This module creates no authentication, tenant
    membership, IAM, permission, role-assignment, work-assignment, supervision,
    professional, matter, workflow-transition, billing, payment or settlement
    authority.

TENANT BOUNDARY:
    Exact tenant/principal inputs only. Foreign-tenant work, assignment or
    supervision truth fails closed instead of being silently filtered.

FINANCIAL AUTHORITY BOUNDARY:
    NONE. Capability labels and operating-role metadata never create financial
    execution authority. Kennel EOS remains the exclusive financial execution
    and settlement boundary.

CHANGELOG:
    2026-10-16 v1.0.1-PW-P2-PROFILE-PRODUCTIVE-WORK-COMPOSITION
    completes the sovereign header and versioned end seal without changing
    productive-work behavior or authority.
    2026-10-15 v1.0.0-PW-P2-PROFILE-PRODUCTIVE-WORK-COMPOSITION
    adds the first title-independent Legal productive-work projection.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Final, Iterable

from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
)
from tools.eos.legal_operations.domain.legal_work_supervision_binding import (
    LegalWorkSupervisionBinding,
)


VERSION: Final[str] = (
    "v1.0.1-PW-P2-PROFILE-PRODUCTIVE-WORK-COMPOSITION"
)

SCHEMA: Final[str] = (
    "WILSY-LEGAL-PROFILE-PRODUCTIVE-WORK/V1"
)

_TERMINAL_WORK_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "COMPLETED",
        "CANCELLED",
    }
)


class LegalProductiveWorkCompositionError(ValueError):
    """Fail-closed productive-work composition error."""


def _require_text(
    value: object,
    *,
    field: str,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value.strip() != value
    ):
        raise LegalProductiveWorkCompositionError(
            f"{field.upper()}_INVALID"
        )
    return value


def _require_positive_revision(
    value: object,
    *,
    field: str,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 1
    ):
        raise LegalProductiveWorkCompositionError(
            f"{field.upper()}_INVALID"
        )
    return value


def _require_aware_datetime(
    value: object,
    *,
    field: str,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalProductiveWorkCompositionError(
            f"{field.upper()}_INVALID"
        )
    return value


def _canonical_text_tuple(
    values: Iterable[str],
    *,
    field: str,
) -> tuple[str, ...]:
    canonical: set[str] = set()

    for value in values:
        canonical.add(
            _require_text(
                value,
                field=field,
            )
        )

    return tuple(sorted(canonical))


def _enum_token(value: object) -> str:
    candidate = getattr(value, "value", value)
    return str(candidate).strip().upper()


def _work_status(
    value: LegalWorkItem,
) -> str:
    return _enum_token(value.status)


def _is_open_work(
    value: LegalWorkItem,
) -> bool:
    return _work_status(value) not in _TERMINAL_WORK_STATUSES


def _work_sort_key(
    value: LegalWorkItem,
) -> tuple[bool, datetime, str]:
    due = value.due_at

    if due is None:
        return (
            True,
            datetime.max.replace(
                tzinfo=value.created_at.tzinfo
            ),
            value.work_item_id,
        )

    return (
        False,
        due,
        value.work_item_id,
    )


@dataclass(frozen=True, slots=True)
class LegalProductiveWorkOperatingContext:
    """Non-authorizing effective operating-role metadata for one principal."""

    operating_role_id: str
    operating_role_revision: int
    display_name: str
    capability_ids: tuple[str, ...] = ()
    office_references: tuple[str, ...] = ()
    practice_references: tuple[str, ...] = ()
    business_unit_references: tuple[str, ...] = ()
    jurisdiction_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "operating_role_id",
            _require_text(
                self.operating_role_id,
                field="operating_role_id",
            ),
        )

        object.__setattr__(
            self,
            "operating_role_revision",
            _require_positive_revision(
                self.operating_role_revision,
                field="operating_role_revision",
            ),
        )

        object.__setattr__(
            self,
            "display_name",
            _require_text(
                self.display_name,
                field="display_name",
            ),
        )

        for field_name in (
            "capability_ids",
            "office_references",
            "practice_references",
            "business_unit_references",
            "jurisdiction_references",
        ):
            object.__setattr__(
                self,
                field_name,
                _canonical_text_tuple(
                    getattr(self, field_name),
                    field=field_name,
                ),
            )


@dataclass(frozen=True, slots=True)
class LegalProductiveWorkProjection:
    """Immutable daily-work projection; never an authorization decision."""

    tenant_id: str
    principal_id: str
    as_of: datetime
    operating_contexts: tuple[
        LegalProductiveWorkOperatingContext,
        ...
    ]
    capability_ids: tuple[str, ...]
    assigned_work_items: tuple[LegalWorkItem, ...]
    supervised_work_items: tuple[LegalWorkItem, ...]
    overdue_work_items: tuple[LegalWorkItem, ...]
    due_soon_work_items: tuple[LegalWorkItem, ...]
    schema: str = SCHEMA
    version: str = VERSION


def _validate_tenant_truth(
    *,
    tenant_id: str,
    work_items: tuple[LegalWorkItem, ...],
    assignments: tuple[LegalWorkAssignment, ...],
    supervision_bindings: tuple[
        LegalWorkSupervisionBinding,
        ...
    ],
) -> None:
    for work_item in work_items:
        if work_item.tenant_id != tenant_id:
            raise LegalProductiveWorkCompositionError(
                "TENANT_WORK_ITEM_SCOPE_MISMATCH"
            )

    for assignment in assignments:
        if assignment.tenant_id != tenant_id:
            raise LegalProductiveWorkCompositionError(
                "TENANT_ASSIGNMENT_SCOPE_MISMATCH"
            )

    for binding in supervision_bindings:
        if binding.tenant_id != tenant_id:
            raise LegalProductiveWorkCompositionError(
                "TENANT_SUPERVISION_SCOPE_MISMATCH"
            )


def _index_work_items(
    work_items: tuple[LegalWorkItem, ...],
) -> dict[str, LegalWorkItem]:
    indexed: dict[str, LegalWorkItem] = {}

    for item in work_items:
        existing = indexed.get(
            item.work_item_id
        )

        if (
            existing is not None
            and existing != item
        ):
            raise LegalProductiveWorkCompositionError(
                "WORK_ITEM_IDENTITY_COLLISION"
            )

        indexed[item.work_item_id] = item

    return indexed


def _effective_supervision(
    binding: LegalWorkSupervisionBinding,
    *,
    principal_id: str,
    as_of: datetime,
) -> bool:
    if binding.supervisor_principal_id != principal_id:
        return False

    if binding.effective_from > as_of:
        return False

    if (
        binding.effective_until is not None
        and binding.effective_until <= as_of
    ):
        return False

    return True


def _supervised_ids(
    *,
    principal_id: str,
    as_of: datetime,
    work_by_id: dict[str, LegalWorkItem],
    supervision_bindings: tuple[
        LegalWorkSupervisionBinding,
        ...
    ],
) -> set[str]:
    selected: set[str] = set()

    for binding in supervision_bindings:
        if not _effective_supervision(
            binding,
            principal_id=principal_id,
            as_of=as_of,
        ):
            continue

        scope = _enum_token(
            binding.scope
        )

        if scope == "WORK_ITEM":
            if binding.work_item_id is None:
                raise LegalProductiveWorkCompositionError(
                    "SUPERVISION_WORK_ITEM_REQUIRED"
                )

            if binding.work_item_id not in work_by_id:
                raise LegalProductiveWorkCompositionError(
                    "SUPERVISION_WORK_ITEM_NOT_FOUND"
                )

            selected.add(
                binding.work_item_id
            )
            continue

        if scope in {
            "MATTER",
            "CASE_MATTER",
        }:
            for item in work_by_id.values():
                if (
                    item.case_matter_id
                    == binding.case_matter_id
                ):
                    selected.add(
                        item.work_item_id
                    )

    return selected


def compose_legal_productive_work(
    *,
    tenant_id: str,
    principal_id: str,
    as_of: datetime,
    operating_contexts: tuple[
        LegalProductiveWorkOperatingContext,
        ...
    ],
    work_items: tuple[LegalWorkItem, ...],
    assignments: tuple[LegalWorkAssignment, ...],
    supervision_bindings: tuple[
        LegalWorkSupervisionBinding,
        ...
    ],
    due_soon_window: timedelta = timedelta(
        hours=24
    ),
) -> LegalProductiveWorkProjection:
    """Compose deterministic principal work without creating authority."""

    tenant_id = _require_text(
        tenant_id,
        field="tenant_id",
    )
    principal_id = _require_text(
        principal_id,
        field="principal_id",
    )
    as_of = _require_aware_datetime(
        as_of,
        field="as_of",
    )

    if (
        not isinstance(
            due_soon_window,
            timedelta,
        )
        or due_soon_window
        < timedelta(0)
    ):
        raise LegalProductiveWorkCompositionError(
            "DUE_SOON_WINDOW_INVALID"
        )

    work_items = tuple(
        work_items
    )
    assignments = tuple(
        assignments
    )
    supervision_bindings = tuple(
        supervision_bindings
    )

    _validate_tenant_truth(
        tenant_id=tenant_id,
        work_items=work_items,
        assignments=assignments,
        supervision_bindings=supervision_bindings,
    )

    contexts_by_identity: dict[
        tuple[str, int],
        LegalProductiveWorkOperatingContext,
    ] = {}

    for context in operating_contexts:
        if not isinstance(
            context,
            LegalProductiveWorkOperatingContext,
        ):
            raise LegalProductiveWorkCompositionError(
                "OPERATING_CONTEXT_INVALID"
            )

        key = (
            context.operating_role_id,
            context.operating_role_revision,
        )

        existing = contexts_by_identity.get(
            key
        )

        if (
            existing is not None
            and existing != context
        ):
            raise LegalProductiveWorkCompositionError(
                "OPERATING_CONTEXT_COLLISION"
            )

        contexts_by_identity[key] = context

    ordered_contexts = tuple(
        sorted(
            contexts_by_identity.values(),
            key=lambda item: (
                item.operating_role_id,
                item.operating_role_revision,
            ),
        )
    )

    capability_ids = tuple(
        sorted(
            {
                capability
                for context in ordered_contexts
                for capability in context.capability_ids
            }
        )
    )

    work_by_id = _index_work_items(
        work_items
    )

    assigned_ids: set[str] = set()

    for assignment in assignments:
        if (
            assignment.work_item_id
            not in work_by_id
        ):
            raise LegalProductiveWorkCompositionError(
                "ASSIGNMENT_WORK_ITEM_NOT_FOUND"
            )

        work_item = work_by_id[
            assignment.work_item_id
        ]

        if (
            work_item.case_matter_id
            != assignment.case_matter_id
        ):
            raise LegalProductiveWorkCompositionError(
                "ASSIGNMENT_MATTER_SCOPE_MISMATCH"
            )

        if (
            assignment.assignee_principal_id
            == principal_id
        ):
            assigned_ids.add(
                assignment.work_item_id
            )

    supervised_ids = _supervised_ids(
        principal_id=principal_id,
        as_of=as_of,
        work_by_id=work_by_id,
        supervision_bindings=supervision_bindings,
    )

    assigned = tuple(
        sorted(
            (
                work_by_id[work_item_id]
                for work_item_id
                in assigned_ids
                if _is_open_work(
                    work_by_id[work_item_id]
                )
            ),
            key=_work_sort_key,
        )
    )

    supervised = tuple(
        sorted(
            (
                work_by_id[work_item_id]
                for work_item_id
                in supervised_ids
                if (
                    work_item_id
                    not in assigned_ids
                    and _is_open_work(
                        work_by_id[
                            work_item_id
                        ]
                    )
                )
            ),
            key=_work_sort_key,
        )
    )

    actionable_by_id = {
        item.work_item_id: item
        for item in (
            *assigned,
            *supervised,
        )
    }

    overdue = tuple(
        sorted(
            (
                item
                for item
                in actionable_by_id.values()
                if (
                    item.due_at is not None
                    and item.due_at < as_of
                )
            ),
            key=_work_sort_key,
        )
    )

    due_soon = tuple(
        sorted(
            (
                item
                for item
                in actionable_by_id.values()
                if (
                    item.due_at is not None
                    and as_of
                    <= item.due_at
                    <= as_of + due_soon_window
                )
            ),
            key=_work_sort_key,
        )
    )

    return LegalProductiveWorkProjection(
        tenant_id=tenant_id,
        principal_id=principal_id,
        as_of=as_of,
        operating_contexts=ordered_contexts,
        capability_ids=capability_ids,
        assigned_work_items=assigned,
        supervised_work_items=supervised,
        overdue_work_items=overdue,
        due_soon_work_items=due_soon,
    )


# STRUCTURAL SELF-AUDIT:
# - title-independent operating-role composition only
# - assignments determine personal work; role names never do
# - supervision remains separate from assignment
# - tenant mismatches fail closed
# - due/overdue state is derived only
# - deterministic ordering and multi-role de-duplication
# - no IAM/permission/command projection
# - no billing/payment/settlement authority
#
# ARTIFACT: legal_profile_productive_work.py
# VERSION: v1.0.1-PW-P2-PROFILE-PRODUCTIVE-WORK-COMPOSITION
# AUTHORITY BOUNDARY: deterministic read-model composition only
# TENANT POSTURE: exact tenant/principal correlation; mismatches fail closed
# FAIL-CLOSED POSTURE: invalid, corrupt, or inconsistent source truth rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
