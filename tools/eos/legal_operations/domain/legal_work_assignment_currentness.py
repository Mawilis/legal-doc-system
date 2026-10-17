"""
TITLE: WILSY OS Legal Work Assignment Historical Currentness
VERSION: v1.0.0-P14-R20R7-LEGAL-WORK-ASSIGNMENT-CURRENTNESS
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Resolve which immutable LegalWorkAssignment owned one exact work item at
    one explicit evaluation instant.

POSTURE:
    Pure deterministic historical projection only. This artifact does not
    authorize assignment, completion, IAM, matter access, supervision,
    workflow transition, legal events, billing, payment or settlement.

TEMPORAL SEMANTICS:
    - immutable assignment lineage is validated fail closed;
    - successor assigned_at must be strictly later than predecessor;
    - evaluated_at is explicit, timezone-aware and normalized to UTC;
    - the selected assignment is the latest lineage node whose assigned_at is
      less than or equal to evaluated_at;
    - successors after evaluated_at are future facts and do not affect the
      historical result;
    - no eligible node means UNASSIGNED at that instant.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Final, NoReturn

from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)


VERSION: Final[str] = (
    "v1.0.0-P14-R20R7-LEGAL-WORK-ASSIGNMENT-CURRENTNESS"
)


class LegalWorkAssignmentCurrentnessError(
    ValueError
):
    """Stable fail-closed historical assignment-currentness failure."""

    def __init__(
        self,
        code: str,
    ) -> None:
        self.code = code
        super().__init__(
            code
        )


def _fail(
    code: str,
) -> NoReturn:
    raise LegalWorkAssignmentCurrentnessError(
        code
    )


def _moment(
    value: object,
) -> datetime:
    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            "P14_R20R7_EVALUATED_AT_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _ordered_history(
    values: tuple[
        LegalWorkAssignment,
        ...,
    ],
) -> tuple[
    LegalWorkAssignment,
    ...,
]:
    if not values:
        return ()

    first = values[0]

    tenant = first.tenant_id
    matter = first.case_matter_id
    work_item = first.work_item_id

    by_id: dict[
        str,
        LegalWorkAssignment,
    ] = {}

    children: dict[
        str,
        list[LegalWorkAssignment],
    ] = {}

    roots: list[
        LegalWorkAssignment
    ] = []

    for value in values:
        if not isinstance(
            value,
            LegalWorkAssignment,
        ):
            _fail(
                "P14_R20R7_ASSIGNMENT_TYPE_INVALID"
            )

        if (
            value.tenant_id != tenant
            or value.case_matter_id != matter
            or value.work_item_id != work_item
        ):
            _fail(
                "P14_R20R7_LINEAGE_SCOPE_MISMATCH"
            )

        if value.assignment_id in by_id:
            _fail(
                "P14_R20R7_DUPLICATE_ASSIGNMENT_ID"
            )

        by_id[
            value.assignment_id
        ] = value

        predecessor = (
            value.supersedes_assignment_id
        )

        if predecessor is None:
            roots.append(
                value
            )
        else:
            children.setdefault(
                predecessor,
                [],
            ).append(
                value
            )

    if len(
        roots
    ) != 1:
        _fail(
            "P14_R20R7_INITIAL_ASSIGNMENT_AMBIGUOUS"
        )

    for predecessor, successors in children.items():
        if predecessor not in by_id:
            _fail(
                "P14_R20R7_PREDECESSOR_NOT_FOUND"
            )

        if len(
            successors
        ) != 1:
            _fail(
                "P14_R20R7_BRANCHED_HISTORY"
            )

    ordered: list[
        LegalWorkAssignment
    ] = []

    seen: set[
        str
    ] = set()

    current = roots[
        0
    ]

    while True:
        if current.assignment_id in seen:
            _fail(
                "P14_R20R7_CYCLIC_HISTORY"
            )

        seen.add(
            current.assignment_id
        )

        ordered.append(
            current
        )

        successors = children.get(
            current.assignment_id,
            [],
        )

        if not successors:
            break

        successor = successors[
            0
        ]

        if (
            successor.assigned_at
            <= current.assigned_at
        ):
            _fail(
                "P14_R20R7_ASSIGNED_AT_NOT_INCREASING"
            )

        current = successor

    if len(
        seen
    ) != len(
        values
    ):
        _fail(
            "P14_R20R7_DISCONNECTED_HISTORY"
        )

    return tuple(
        ordered
    )


def resolve_legal_work_assignment_as_of(
    assignments: tuple[
        LegalWorkAssignment,
        ...,
    ],
    *,
    evaluated_at: datetime,
) -> LegalWorkAssignment | None:
    """Return the exact immutable assignment current at evaluated_at."""
    moment = _moment(
        evaluated_at
    )

    history = _ordered_history(
        assignments
    )

    selected: (
        LegalWorkAssignment
        | None
    ) = None

    for assignment in history:
        assigned_at = assignment.assigned_at.astimezone(
            timezone.utc
        )

        if assigned_at > moment:
            break

        selected = assignment

    return selected


@dataclass(
    frozen=True,
    slots=True,
)
class LegalWorkAssignmentCurrentness:
    """Immutable pure projection of assignment currentness at one instant."""

    evaluated_at: datetime
    assignment: (
        LegalWorkAssignment
        | None
    )

    @classmethod
    def resolve(
        cls,
        assignments: tuple[
            LegalWorkAssignment,
            ...,
        ],
        *,
        evaluated_at: datetime,
    ) -> "LegalWorkAssignmentCurrentness":
        moment = _moment(
            evaluated_at
        )

        return cls(
            evaluated_at=moment,
            assignment=(
                resolve_legal_work_assignment_as_of(
                    assignments,
                    evaluated_at=moment,
                )
            ),
        )


__all__ = [
    "VERSION",
    "LegalWorkAssignmentCurrentness",
    "LegalWorkAssignmentCurrentnessError",
    "resolve_legal_work_assignment_as_of",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_work_assignment_currentness.py
# VERSION: v1.0.0-P14-R20R7-LEGAL-WORK-ASSIGNMENT-CURRENTNESS
# PURE HISTORICAL CURRENTNESS: YES
# FUTURE FACT EXCLUSION: YES
# PERSISTENCE AUTHORITY: NONE
# IAM AUTHORITY: NONE
# COMPLETION AUTHORITY: NONE
# ASSIGNMENT MUTATION AUTHORITY: NONE
# SUPERVISION AUTHORITY: NONE
# WORKFLOW / LEGAL EVENT AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
