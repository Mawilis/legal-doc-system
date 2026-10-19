"""WILSY practitioner ethical-wall currentness.

VERSION: v1.0.0-P9-R105-P4G-P4-R2A
AUTHORITY: Pure fail-closed restriction-evidence projection only.
No empty-history clearance, waiver, lift, issuer, operational access or AI
retrieval authorization is established.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Final, Iterable

from tools.eos.legal_operations.domain.legal_practitioner_ethical_wall_restriction import (
    LegalPractitionerEthicalWallRestriction,
)

VERSION: Final[str] = "v1.0.0-P9-R105-P4G-P4-R2A"


class LegalPractitionerEthicalWallCurrentnessState(StrEnum):
    RESTRICTED = "RESTRICTED"
    NO_RECORDED_RESTRICTION = "NO_RECORDED_RESTRICTION"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


class LegalPractitionerEthicalWallCurrentnessError(ValueError):
    """Invalid evaluation scope or time."""


@dataclass(frozen=True, slots=True)
class LegalPractitionerEthicalWallCurrentness:
    tenant_id: str
    case_matter_id: str
    restricted_practitioner_principal_id: str
    evaluation_time: datetime
    state: LegalPractitionerEthicalWallCurrentnessState
    decisive_restriction_fingerprints: tuple[str, ...]
    observed_restriction_fingerprints: tuple[str, ...]

    @property
    def blocks_access(self) -> bool:
        return self.state is not (
            LegalPractitionerEthicalWallCurrentnessState.NO_RECORDED_RESTRICTION
        )

    @property
    def grants_access(self) -> bool:
        return False


def _identity(value: object) -> str:
    if (
        type(value) is not str or not value or len(value) > 200
        or value != value.strip()
        or any(ord(c) < 32 or ord(c) == 127 for c in value)
    ):
        raise LegalPractitionerEthicalWallCurrentnessError(
            "P9_WALL_CURRENTNESS_SCOPE_INVALID"
        )
    return value


def _time(value: object) -> datetime:
    if (
        type(value) is not datetime
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalPractitionerEthicalWallCurrentnessError(
            "P9_WALL_CURRENTNESS_TIME_INVALID"
        )
    return value.astimezone(timezone.utc)


def project_legal_practitioner_ethical_wall_currentness(
    *,
    tenant_id: str,
    case_matter_id: str,
    restricted_practitioner_principal_id: str,
    evaluation_time: datetime,
    restrictions: Iterable[LegalPractitionerEthicalWallRestriction],
) -> LegalPractitionerEthicalWallCurrentness:
    tenant = _identity(tenant_id)
    matter = _identity(case_matter_id)
    practitioner = _identity(restricted_practitioner_principal_id)
    at = _time(evaluation_time)

    def result(
        state: LegalPractitionerEthicalWallCurrentnessState,
        decisive: tuple[str, ...] = (),
        observed: tuple[str, ...] = (),
    ) -> LegalPractitionerEthicalWallCurrentness:
        return LegalPractitionerEthicalWallCurrentness(
            tenant_id=tenant,
            case_matter_id=matter,
            restricted_practitioner_principal_id=practitioner,
            evaluation_time=at,
            state=state,
            decisive_restriction_fingerprints=decisive,
            observed_restriction_fingerprints=observed,
        )

    try:
        items = tuple(restrictions)
    except Exception:
        return result(LegalPractitionerEthicalWallCurrentnessState.CORRUPT_BLOCKED)

    verified: dict[str, LegalPractitionerEthicalWallRestriction] = {}
    try:
        for item in items:
            if not isinstance(item, LegalPractitionerEthicalWallRestriction):
                return result(
                    LegalPractitionerEthicalWallCurrentnessState.CORRUPT_BLOCKED
                )
            canonical = LegalPractitionerEthicalWallRestriction.from_dict(
                item.to_dict()
            )
            if canonical != item or (
                canonical.tenant_id != tenant
                or canonical.case_matter_id != matter
                or canonical.restricted_practitioner_principal_id != practitioner
            ):
                return result(
                    LegalPractitionerEthicalWallCurrentnessState.CORRUPT_BLOCKED
                )
            previous = verified.get(canonical.restriction_id)
            if previous is not None and previous != canonical:
                return result(
                    LegalPractitionerEthicalWallCurrentnessState.CORRUPT_BLOCKED
                )
            verified[canonical.restriction_id] = canonical
    except Exception:
        return result(LegalPractitionerEthicalWallCurrentnessState.CORRUPT_BLOCKED)

    observed = tuple(sorted({x.fingerprint for x in verified.values()}))
    active = tuple(sorted({
        x.fingerprint for x in verified.values() if x.effective_from <= at
    }))
    if active:
        return result(
            LegalPractitionerEthicalWallCurrentnessState.RESTRICTED,
            active, observed,
        )
    return result(
        LegalPractitionerEthicalWallCurrentnessState.NO_RECORDED_RESTRICTION,
        (), observed,
    )


__all__ = (
    "VERSION",
    "LegalPractitionerEthicalWallCurrentnessState",
    "LegalPractitionerEthicalWallCurrentnessError",
    "LegalPractitionerEthicalWallCurrentness",
    "project_legal_practitioner_ethical_wall_currentness",
)

# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P4-R2A
# RESTRICTION PROJECTION ONLY; NO ACCESS CLEARANCE OR WAIVER
# END OF WILSY OS SOVEREIGN ARTIFACT
