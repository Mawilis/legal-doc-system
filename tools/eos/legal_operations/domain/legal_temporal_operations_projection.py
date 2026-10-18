"""
TITLE:
    WILSY OS Legal Temporal Operations Projection

VERSION:
    v1.0.0-P4-P0-LEGAL-TEMPORAL-OPERATIONS-PROJECTION

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations

EPITOME:
    Immutable, deterministic, principal-scoped projection of evidenced
    legal-matter deadlines within existing Productive Work visibility.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_temporal_operations_projection.py

COLLABORATION / OWNERSHIP:
    Canonical Productive Work supplies matter visibility.
    Legal Matter Deadline supplies immutable temporal evidence.
    P4-P0 composes projection only; it owns no persistence or transport.

CERTIFICATION / UPDATE DATE:
    2026-10-18

CHANGELOG:
    2026-10-18 v1.0.0-P4-P0-LEGAL-TEMPORAL-OPERATIONS-PROJECTION establishes immutable temporal
    rows, exact visible-matter scope, deterministic ordering,
    provenance preservation and fail-closed mismatch rejection.
    R15A completes sovereign metadata without changing runtime behavior.

COMPLIANCE:
    POPIA section 19, GDPR Article 32 and SOC 2 CC7.2 are
    technical-control objectives, not independent legal-compliance claims.

SECURITY / PRIVACY POSTURE:
    Reject foreign-tenant deadlines, invisible matters, duplicate
    deadline identities and malformed matter visibility.
    Preserve existing source evidence without creating new authority.

TENANT BOUNDARY:
    Every admitted deadline must match the exact authenticated
    Productive Work tenant; principal scope is inherited unchanged.

AUTHORITY BOUNDARY:
    Read-only projection. No matter visibility grant, IAM, assignment,
    supervision, deadline mutation, legal-period calculation, overdue
    inference, court/hearing, AI or legal execution authority.

FINANCIAL AUTHORITY BOUNDARY:
    No billing, payment, settlement or execution authority.
    Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final

from tools.eos.legal_operations.domain.legal_matter_deadline import (
    LegalMatterDeadline,
)
from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkProjection,
)


VERSION: Final[str] = (
    "v1.0.0-P4-P0-LEGAL-TEMPORAL-OPERATIONS-PROJECTION"
)

SCHEMA: Final[str] = (
    "WILSY-LEGAL-TEMPORAL-OPERATIONS-PROJECTION/V1"
)


class LegalTemporalOperationsProjectionError(ValueError):
    """Fail-closed pure temporal projection contract error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class LegalTemporalOperationsRow:
    """One evidenced deadline already admitted by visible-matter scope."""

    case_matter_id: str
    deadline_id: str
    deadline_kind: object
    title: str
    due_at: datetime
    source_type: object
    source_reference: str
    source_evidence_fingerprint: str
    jurisdiction_reference: str
    status: object


@dataclass(frozen=True, slots=True)
class LegalTemporalOperationsProjection:
    """Principal-scoped immutable Legal temporal read model."""

    tenant_id: str
    principal_id: str
    as_of: datetime
    visible_matter_ids: tuple[str, ...]
    rows: tuple[LegalTemporalOperationsRow, ...]
    schema: str = SCHEMA
    version: str = VERSION


def _visible_matter_ids(
    productive_work: LegalProductiveWorkProjection,
) -> tuple[str, ...]:
    """
    Derive the v1 temporal visibility ceiling from Productive Work only.

    Assigned and supervised work are both already-visible Productive Work
    surfaces. Overdue/due-soon collections are derivative subsets and are
    deliberately not separate visibility sources.
    """

    matter_ids: set[str] = set()

    for item in (
        *productive_work.assigned_work_items,
        *productive_work.supervised_work_items,
    ):
        case_matter_id = item.case_matter_id

        if (
            not isinstance(case_matter_id, str)
            or not case_matter_id
            or case_matter_id != case_matter_id.strip()
        ):
            raise LegalTemporalOperationsProjectionError(
                "TEMPORAL_VISIBLE_MATTER_ID_INVALID"
            )

        matter_ids.add(case_matter_id)

    return tuple(sorted(matter_ids))


def compose_legal_temporal_operations_projection(
    *,
    productive_work: LegalProductiveWorkProjection,
    deadlines: tuple[LegalMatterDeadline, ...],
) -> LegalTemporalOperationsProjection:
    """
    Compose evidenced temporal facts for Productive-Work-visible matters.

    Any deadline outside the exact productive-work visible matter set is
    corruption/scope drift and fails closed rather than broadening visibility.
    """

    visible_matter_ids = _visible_matter_ids(
        productive_work
    )

    visible_matter_set = set(
        visible_matter_ids
    )

    seen_deadline_ids: set[str] = set()
    rows: list[LegalTemporalOperationsRow] = []

    for deadline in deadlines:
        if deadline.tenant_id != productive_work.tenant_id:
            raise LegalTemporalOperationsProjectionError(
                "TEMPORAL_DEADLINE_TENANT_SCOPE_MISMATCH"
            )

        if deadline.deadline_id in seen_deadline_ids:
            raise LegalTemporalOperationsProjectionError(
                "TEMPORAL_DEADLINE_ID_DUPLICATE"
            )

        seen_deadline_ids.add(
            deadline.deadline_id
        )

        if deadline.case_matter_id not in visible_matter_set:
            raise LegalTemporalOperationsProjectionError(
                "TEMPORAL_DEADLINE_MATTER_NOT_VISIBLE"
            )

        rows.append(
            LegalTemporalOperationsRow(
                case_matter_id=deadline.case_matter_id,
                deadline_id=deadline.deadline_id,
                deadline_kind=deadline.deadline_kind,
                title=deadline.title,
                due_at=deadline.due_at,
                source_type=deadline.source_type,
                source_reference=deadline.source_reference,
                source_evidence_fingerprint=(
                    deadline.source_evidence_fingerprint
                ),
                jurisdiction_reference=(
                    deadline.jurisdiction_reference
                ),
                status=deadline.status,
            )
        )

    ordered_rows = tuple(
        sorted(
            rows,
            key=lambda row: (
                row.due_at,
                row.case_matter_id,
                row.deadline_id,
            ),
        )
    )

    return LegalTemporalOperationsProjection(
        tenant_id=productive_work.tenant_id,
        principal_id=productive_work.principal_id,
        as_of=productive_work.as_of,
        visible_matter_ids=visible_matter_ids,
        rows=ordered_rows,
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalTemporalOperationsProjection",
    "LegalTemporalOperationsProjectionError",
    "LegalTemporalOperationsRow",
    "compose_legal_temporal_operations_projection",
]


# ARTIFACT: legal_temporal_operations_projection.py
# VERSION: v1.0.0-P4-P0-LEGAL-TEMPORAL-OPERATIONS-PROJECTION
# AUTHORITY BOUNDARY: immutable read projection of already-authorized Legal Matter Deadline evidence only
# TENANT POSTURE: exact Productive Work tenant/principal visibility; foreign and invisible facts rejected
# FAIL-CLOSED POSTURE: invalid matter identity, tenant mismatch, invisible scope and duplicate deadline identity reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
