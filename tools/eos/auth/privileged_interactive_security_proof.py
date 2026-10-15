"""
Pure domain for one interactive current-security proof.

VERSION:
v1.0.0-P3-R3A-PRIVILEGED-INTERACTIVE-SECURITY-PROOF

PURPOSE:

Represent the minimum secret-free facts produced by a trusted interactive
authentication/factor-verification source for later P3 current-assurance
composition.

THIS DOMAIN DOES NOT VERIFY MFA.

THIS DOMAIN DOES NOT DECIDE AUTHENTICATION RECENCY.

THIS DOMAIN DOES NOT CHECK CURRENT SESSION STATE.

THIS DOMAIN DOES NOT CHECK CURRENT CREDENTIAL REVISION.

Those currentness comparisons belong to later security policy/orchestration.

PROOF != ROLE.
PROOF != P2 ELIGIBILITY.
PROOF != P3 ASSURANCE DECISION.
PROOF != PRIVILEGED ACTIVATION.
PROOF != BREAK GLASS.
PROOF != FINANCIAL AUTHORITY.

Raw factor secrets, OTPs, session tokens, JWTs, passwords, refresh tokens,
private keys, API keys, and workload credentials are forbidden.
"""

from dataclasses import dataclass
from datetime import (
    datetime,
    timezone,
)
from enum import StrEnum
from typing import Final


VERSION: Final[str] = (
    "v1.0.0-P3-R3A-"
    "PRIVILEGED-INTERACTIVE-SECURITY-PROOF"
)

MAX_REFERENCE_LENGTH: Final[int] = 1024


class PrivilegedInteractiveSecurityProofError(
    ValueError
):
    """Fail-closed pure-domain validation error."""


class PrivilegedInteractiveProofStatus(
    StrEnum
):
    """Lifecycle state supplied by the trusted proof source."""

    VERIFIED = "VERIFIED"
    REVOKED = "REVOKED"
    INVALIDATED = "INVALIDATED"


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
        or len(value)
        > MAX_REFERENCE_LENGTH
    ):
        raise (
            PrivilegedInteractiveSecurityProofError(
                name + " is invalid"
            )
        )

    return value


def _revision(
    value: object,
) -> int:
    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
        or value < 0
    ):
        raise (
            PrivilegedInteractiveSecurityProofError(
                "credential_revision is invalid"
            )
        )

    return value


def _timestamp(
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
        raise (
            PrivilegedInteractiveSecurityProofError(
                "authenticated_at is invalid"
            )
        )

    return value.astimezone(
        timezone.utc
    )


@dataclass(
    frozen=True,
    slots=True,
)
class PrivilegedInteractiveSecurityProof:
    """Secret-free source fact for one interactive verification event."""

    proof_id: str

    principal_id: str

    factor_verification_reference: str

    authenticated_at: datetime

    credential_revision: int

    session_reference: str

    proof_status: (
        PrivilegedInteractiveProofStatus
    )

    proof_reference: str

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "proof_id",
            "principal_id",
            "factor_verification_reference",
            "session_reference",
            "proof_reference",
        ):
            object.__setattr__(
                self,
                name,
                _text(
                    name,
                    getattr(
                        self,
                        name,
                    ),
                ),
            )

        object.__setattr__(
            self,
            "authenticated_at",
            _timestamp(
                self.authenticated_at
            ),
        )

        object.__setattr__(
            self,
            "credential_revision",
            _revision(
                self.credential_revision
            ),
        )

        if not isinstance(
            self.proof_status,
            PrivilegedInteractiveProofStatus,
        ):
            raise (
                PrivilegedInteractiveSecurityProofError(
                    "proof_status is invalid"
                )
            )

    @property
    def factor_verification_successful(
        self,
    ) -> bool:
        """Expose only lifecycle truth; this property creates no authority."""

        return (
            self.proof_status
            is PrivilegedInteractiveProofStatus
            .VERIFIED
        )


__all__ = [
    "VERSION",
    "PrivilegedInteractiveProofStatus",
    "PrivilegedInteractiveSecurityProof",
    "PrivilegedInteractiveSecurityProofError",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: privileged_interactive_security_proof.py
# VERSION: v1.0.0-P3-R3A-PRIVILEGED-INTERACTIVE-SECURITY-PROOF
# DOMAIN: pure / immutable / secret-free
# TENANT FIELD: absent; no tenant authority invented
# PRINCIPAL KIND: absent; no human/service/machine classification invented
# MFA VERIFICATION IMPLEMENTATION: none
# AUTHENTICATION RECENCY POLICY: none
# SESSION CURRENTNESS LOOKUP: none
# CREDENTIAL CURRENTNESS LOOKUP: none
# REGISTRY / PERSISTENCE: none
# P3 ASSURANCE DECISION: none
# PRIVILEGED ACTIVATION: none
# BREAK GLASS: none
# FINANCIAL AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
