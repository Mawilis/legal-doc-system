"""Derived currentness for immutable WILSY workforce history.

VERSION:
    v1.0.0-WILSY-W3B-WORKFORCE-CURRENTNESS

AUTHORITY:
    Pure derivation from one complete ordered workforce relationship history.

This module does not grant IAM authority and owns no persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final, Sequence

from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
)


VERSION: Final[str] = (
    "v1.0.0-WILSY-W3B-WORKFORCE-CURRENTNESS"
)


class WorkforceRelationshipCurrentnessError(ValueError):
    """History cannot be safely resolved."""


@dataclass(frozen=True, slots=True)
class WorkforceRelationshipCurrentness:
    """Fail-closed currentness projection, not authorization."""

    relationship: WorkforceRelationship
    observed_at: datetime
    is_effective: bool
    is_active: bool

    def __post_init__(self) -> None:
        if (
            not isinstance(self.observed_at, datetime)
            or self.observed_at.tzinfo is None
            or self.observed_at.utcoffset() is None
        ):
            raise WorkforceRelationshipCurrentnessError(
                "OBSERVED_AT_INVALID"
            )

        if type(self.is_effective) is not bool:
            raise WorkforceRelationshipCurrentnessError(
                "IS_EFFECTIVE_INVALID"
            )

        if type(self.is_active) is not bool:
            raise WorkforceRelationshipCurrentnessError(
                "IS_ACTIVE_INVALID"
            )

        if self.is_active and not self.is_effective:
            raise WorkforceRelationshipCurrentnessError(
                "ACTIVE_WITHOUT_EFFECTIVE_INVALID"
            )


def derive_workforce_relationship_currentness(
    history: Sequence[WorkforceRelationship],
    observed_at: datetime,
) -> WorkforceRelationshipCurrentness:
    """Derive one relationship's currentness from complete ordered history."""

    if (
        not isinstance(observed_at, datetime)
        or observed_at.tzinfo is None
        or observed_at.utcoffset() is None
    ):
        raise WorkforceRelationshipCurrentnessError(
            "OBSERVED_AT_INVALID"
        )

    if not isinstance(history, Sequence) or not history:
        raise WorkforceRelationshipCurrentnessError(
            "HISTORY_REQUIRED"
        )

    values = tuple(history)

    if any(
        not isinstance(
            value,
            WorkforceRelationship,
        )
        for value in values
    ):
        raise WorkforceRelationshipCurrentnessError(
            "HISTORY_TYPE_INVALID"
        )

    first = values[0]

    expected_revision = 1
    previous: WorkforceRelationship | None = None

    for value in values:
        if value.revision != expected_revision:
            raise WorkforceRelationshipCurrentnessError(
                "REVISION_SEQUENCE_INVALID"
            )

        if (
            value.relationship_id
            != first.relationship_id
            or value.scope_kind
            is not first.scope_kind
            or value.scope_id
            != first.scope_id
            or value.principal_id
            != first.principal_id
            or value.relationship_type
            is not first.relationship_type
        ):
            raise WorkforceRelationshipCurrentnessError(
                "HISTORY_IDENTITY_MISMATCH"
            )

        if previous is None:
            if value.supersedes_fingerprint is not None:
                raise WorkforceRelationshipCurrentnessError(
                    "FIRST_REVISION_LINEAGE_INVALID"
                )
        else:
            if (
                value.supersedes_fingerprint
                != previous.fingerprint
            ):
                raise WorkforceRelationshipCurrentnessError(
                    "FINGERPRINT_CHAIN_INVALID"
                )

            if (
                value.status_effective_at
                < previous.status_effective_at
            ):
                raise WorkforceRelationshipCurrentnessError(
                    "STATUS_TIME_REGRESSION"
                )

            if (
                previous.status
                is WorkforceRelationshipStatus.ENDED
            ):
                raise WorkforceRelationshipCurrentnessError(
                    "ENDED_RELATIONSHIP_TERMINAL"
                )

        previous = value
        expected_revision += 1

    applicable = tuple(
        value
        for value in values
        if value.status_effective_at <= observed_at
    )

    selected = (
        applicable[-1]
        if applicable
        else values[0]
    )

    effective = (
        observed_at >= selected.effective_from
        and (
            selected.effective_until is None
            or observed_at < selected.effective_until
        )
        and observed_at >= selected.status_effective_at
    )

    active = (
        effective
        and selected.status
        is WorkforceRelationshipStatus.ACTIVE
    )

    return WorkforceRelationshipCurrentness(
        relationship=selected,
        observed_at=observed_at,
        is_effective=effective,
        is_active=active,
    )


__all__ = [
    "VERSION",
    "WorkforceRelationshipCurrentness",
    "WorkforceRelationshipCurrentnessError",
    "derive_workforce_relationship_currentness",
]


# CURRENTNESS IS DERIVED, NOT MUTABLE AUTHORITY.
# SUSPENDED != ACTIVE.
# ENDED != ACTIVE.
# EXPIRED != ACTIVE.
# IAM AUTHORITY: NONE.
# FINANCIAL EXECUTION AUTHORITY: NONE.
