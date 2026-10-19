"""WILSY P9-R105-P4G-P6-R3C conjunctive documentary read guard.

Inspects ethical-wall evidence first, then practitioner policy evidence.
Both use the same caller-owned active transaction and server-owned UTC time.

Documentary policy ALLOW_UNVERIFIED is not an operational access grant.
No content release, IAM issuance, conflict waiver, wall lift, or finance.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Callable, Final

from tools.eos.legal_operations.domain.legal_practitioner_matter_access_currentness import (
    LegalPractitionerMatterAccessCurrentnessState as AccessState,
    project_legal_practitioner_matter_access_currentness,
)
from tools.eos.legal_operations.registry.legal_practitioner_matter_access_history_reader import (
    read_practitioner_matter_access_history,
)
from tools.eos.legal_operations.service.legal_practitioner_ethical_wall_read_barrier import (
    EthicalWallReadBarrierState as WallState,
    inspect_practitioner_ethical_wall_read_barrier,
)

VERSION: Final[str] = "v1.0.0-P9-R105-P4G-P6-R3C"


class ConjunctiveReadGuardState(StrEnum):
    DENY_WALL = "DENY_WALL"
    DENY_DOCUMENTARY_ACCESS = "DENY_DOCUMENTARY_ACCESS"
    DENY_UNVERIFIED = "DENY_UNVERIFIED"
    DENY_UNAVAILABLE = "DENY_UNAVAILABLE"


@dataclass(frozen=True, slots=True)
class ConjunctiveReadGuardResult:
    state: ConjunctiveReadGuardState
    wall_fingerprints: tuple[str, ...] = ()
    practitioner_access_fingerprints: tuple[str, ...] = ()

    @property
    def permits_content(self) -> bool:
        return False

    @property
    def authorized(self) -> bool:
        return False


def inspect_conjunctive_practitioner_read_guard(
    *,
    tenant_id: str,
    case_matter_id: str,
    practitioner_principal_id: str,
    wall_collection: Any,
    practitioner_access_collection: Any,
    session: Any,
    server_clock: Callable[[], datetime] | None = None,
) -> ConjunctiveReadGuardResult:
    """Return denial-safe evidence findings, never a content authorization.

    The optional clock is an internal, injected testing seam; callers must
    not bind it to an HTTP parameter or principal-provided timestamp.
    """
    unavailable = ConjunctiveReadGuardResult(
        ConjunctiveReadGuardState.DENY_UNAVAILABLE
    )
    if session is None:
        return unavailable
    try:
        if getattr(session, "in_transaction", False) is not True:
            return unavailable
        instant = (
            datetime.now(timezone.utc)
            if server_clock is None else server_clock()
        )
        if (
            type(instant) is not datetime
            or instant.tzinfo is None
            or instant.utcoffset() is None
        ):
            return unavailable
        instant = instant.astimezone(timezone.utc)

        wall = inspect_practitioner_ethical_wall_read_barrier(
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            practitioner_principal_id=practitioner_principal_id,
            evaluation_time=instant,
            restriction_collection=wall_collection,
            session=session,
        )

        if wall.state is WallState.DENY_RESTRICTED:
            fingerprints = (
                wall.currentness.decisive_restriction_fingerprints
                if wall.currentness is not None else ()
            )
            return ConjunctiveReadGuardResult(
                ConjunctiveReadGuardState.DENY_WALL,
                wall_fingerprints=fingerprints,
            )
        if wall.state is not WallState.DENY_UNVERIFIED:
            return unavailable

        evidence = read_practitioner_matter_access_history(
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            practitioner_principal_id=practitioner_principal_id,
            collection=practitioner_access_collection,
            session=session,
        )
        current = project_legal_practitioner_matter_access_currentness(
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            practitioner_principal_id=practitioner_principal_id,
            evaluation_time=instant,
            evidence=evidence,
        )

        if current.state in (
            AccessState.DENY_BLOCKED,
            AccessState.AMBIGUOUS_BLOCKED,
            AccessState.CORRUPT_BLOCKED,
        ):
            state = ConjunctiveReadGuardState.DENY_DOCUMENTARY_ACCESS
        else:
            # Even a genuine, current ALLOW remains documentary evidence.
            # Independent current conflict, IAM, matter membership, and
            # operational security checks have not been composed here.
            state = ConjunctiveReadGuardState.DENY_UNVERIFIED

        return ConjunctiveReadGuardResult(
            state,
            practitioner_access_fingerprints=current.decisive_fingerprints,
        )
    except Exception:
        return unavailable


__all__ = (
    "VERSION",
    "ConjunctiveReadGuardState",
    "ConjunctiveReadGuardResult",
    "inspect_conjunctive_practitioner_read_guard",
)

# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P6-R3C
# DENIAL-SAFE DOCUMENTARY FINDING ONLY; NO CONTENT ACCESS GRANT
# END OF WILSY OS SOVEREIGN ARTIFACT
