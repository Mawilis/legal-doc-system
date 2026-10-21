"""WILSY P9-R105-P4G-P5-R1 ethical-wall read barrier.

Read-only authoritative restriction-history inspection. Not an operational
access check, clearance, issuer, transport authorization, or AI retrieval grant.
All outcomes remain unauthorized until separate conjunctive security gates
and real endpoint enforcement have been independently certified.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Final

from tools.eos.legal_operations.domain.legal_practitioner_ethical_wall_currentness import (
    LegalPractitionerEthicalWallCurrentness,
    LegalPractitionerEthicalWallCurrentnessState,
    project_legal_practitioner_ethical_wall_currentness,
)
from tools.eos.legal_operations.registry.legal_practitioner_ethical_wall_restriction_registry import (
    list_restrictions_for_scope,
)

VERSION: Final[str] = "v1.0.0-P9-R105-P4G-P5-R1"


class EthicalWallReadBarrierState(StrEnum):
    DENY_RESTRICTED = "DENY_RESTRICTED"
    DENY_UNVERIFIED = "DENY_UNVERIFIED"
    DENY_UNAVAILABLE = "DENY_UNAVAILABLE"


@dataclass(frozen=True, slots=True)
class EthicalWallReadBarrierResult:
    state: EthicalWallReadBarrierState
    currentness: LegalPractitionerEthicalWallCurrentness | None

    @property
    def authorized(self) -> bool:
        return False

    @property
    def permits_content(self) -> bool:
        return False


def inspect_practitioner_ethical_wall_read_barrier(
    *,
    tenant_id: str,
    case_matter_id: str,
    practitioner_principal_id: str,
    evaluation_time: datetime,
    restriction_collection: Any,
    session: Any,
) -> EthicalWallReadBarrierResult:
    """Inspect wall truth in an active transaction, never issue an ALLOW.

    DENY_UNVERIFIED means no restriction is currently recorded, not proof
    that conflict, matter access, confidentiality and IAM are satisfied.
    """
    if session is None or getattr(session, "in_transaction", False) is not True:
        return EthicalWallReadBarrierResult(
            EthicalWallReadBarrierState.DENY_UNAVAILABLE, None
        )

    try:
        history = list_restrictions_for_scope(
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            restricted_practitioner_principal_id=practitioner_principal_id,
            collection=restriction_collection,
            session=session,
        )
        result = project_legal_practitioner_ethical_wall_currentness(
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            restricted_practitioner_principal_id=practitioner_principal_id,
            evaluation_time=evaluation_time,
            restrictions=history,
        )
    except Exception:
        return EthicalWallReadBarrierResult(
            EthicalWallReadBarrierState.DENY_UNAVAILABLE, None
        )

    if result.state is LegalPractitionerEthicalWallCurrentnessState.RESTRICTED:
        state = EthicalWallReadBarrierState.DENY_RESTRICTED
    elif result.state is (
        LegalPractitionerEthicalWallCurrentnessState.NO_RECORDED_RESTRICTION
    ):
        state = EthicalWallReadBarrierState.DENY_UNVERIFIED
    else:
        state = EthicalWallReadBarrierState.DENY_UNAVAILABLE

    return EthicalWallReadBarrierResult(state, result)


__all__ = (
    "VERSION",
    "EthicalWallReadBarrierState",
    "EthicalWallReadBarrierResult",
    "inspect_practitioner_ethical_wall_read_barrier",
)

# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P5-R1
# CONTENT DELIVERY / CLEARANCE / ISSUANCE / WAIVER / FINANCE: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
