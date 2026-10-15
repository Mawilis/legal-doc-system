"""
Pure domain for one noninteractive current-security proof.

VERSION:
v1.0.0-P3-R3D-PRIVILEGED-NONINTERACTIVE-SECURITY-PROOF

PURPOSE:

Represent the minimum secret-free facts produced by a trusted workload
credential or attestation source for later P3 current-assurance composition.

THIS DOMAIN DOES NOT VERIFY API KEYS.
THIS DOMAIN DOES NOT VERIFY PRIVATE KEYS.
THIS DOMAIN DOES NOT VERIFY CLIENT SECRETS.
THIS DOMAIN DOES NOT VALIDATE CERTIFICATES.
THIS DOMAIN DOES NOT VALIDATE JWT CLAIMS.
THIS DOMAIN DOES NOT DECIDE PRINCIPAL KIND.
THIS DOMAIN DOES NOT CREATE WORKLOAD IDENTITY.

SERVICE-ACCOUNT BOOLEAN != WORKLOAD PROOF.
JWT CLAIM != WORKLOAD PROOF.
ROLE NAME != WORKLOAD PROOF.
USERNAME != WORKLOAD PROOF.
CALLER ASSERTION != WORKLOAD PROOF.

PROOF != ROLE.
PROOF != P2 ELIGIBILITY.
PROOF != P3 ASSURANCE DECISION.
PROOF != PRIVILEGED ACTIVATION.
PROOF != BREAK GLASS.
PROOF != FINANCIAL AUTHORITY.

Raw API keys, private keys, client secrets, bearer tokens, JWTs, certificates,
workload credentials, passwords, MFA secrets, OTPs, and refresh tokens are
forbidden.
"""

from dataclasses import dataclass
from datetime import (
    datetime,
    timezone,
)
from enum import StrEnum
from typing import Final


VERSION: Final[str] = (
    "v1.0.0-P3-R3D-"
    "PRIVILEGED-NONINTERACTIVE-SECURITY-PROOF"
)

MAX_REFERENCE_LENGTH: Final[int] = 1024


class PrivilegedNoninteractiveSecurityProofError(
    ValueError
):
    """Fail-closed pure-domain validation error."""


class PrivilegedNoninteractiveProofStatus(
    StrEnum
):
    """Lifecycle state supplied by the trusted workload-proof source."""

    VERIFIED = "VERIFIED"
    REVOKED = "REVOKED"
    INVALIDATED = "INVALIDATED"


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > MAX_REFERENCE_LENGTH
    ):
        raise (
            PrivilegedNoninteractiveSecurityProofError(
                name + " is invalid"
            )
        )

    return value


def _timestamp(
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise (
            PrivilegedNoninteractiveSecurityProofError(
                "observed_at is invalid"
            )
        )

    return value.astimezone(
        timezone.utc
    )


@dataclass(
    frozen=True,
    slots=True,
)
class PrivilegedNoninteractiveSecurityProof:
    """Secret-free source fact for one workload credential/attestation proof."""

    proof_id: str

    principal_id: str

    proof_reference: str

    credential_or_attestation_reference: str

    observed_at: datetime

    proof_status: (
        PrivilegedNoninteractiveProofStatus
    )

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "proof_id",
            "principal_id",
            "proof_reference",
            "credential_or_attestation_reference",
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
            "observed_at",
            _timestamp(
                self.observed_at
            ),
        )

        if not isinstance(
            self.proof_status,
            PrivilegedNoninteractiveProofStatus,
        ):
            raise (
                PrivilegedNoninteractiveSecurityProofError(
                    "proof_status is invalid"
                )
            )

    @property
    def workload_proof_successful(
        self,
    ) -> bool:
        """Expose lifecycle truth only; this creates no privileged authority."""

        return (
            self.proof_status
            is PrivilegedNoninteractiveProofStatus
            .VERIFIED
        )


__all__ = [
    "VERSION",
    "PrivilegedNoninteractiveProofStatus",
    "PrivilegedNoninteractiveSecurityProof",
    "PrivilegedNoninteractiveSecurityProofError",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: privileged_noninteractive_security_proof.py
# VERSION: v1.0.0-P3-R3D-PRIVILEGED-NONINTERACTIVE-SECURITY-PROOF
# DOMAIN: pure / immutable / secret-free
# TENANT FIELD: absent; no tenant authority invented
# PRINCIPAL KIND: absent; no human/service/machine classification invented
# SERVICE ACCOUNT BOOLEAN AUTHORITY: none
# JWT CLAIM AUTHORITY: none
# WORKLOAD CREDENTIAL VERIFICATION: none
# ATTESTATION VALIDATION: none
# REGISTRY / PERSISTENCE: none
# P3 ASSURANCE DECISION: none
# PRIVILEGED ACTIVATION: none
# BREAK GLASS: none
# FINANCIAL AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
