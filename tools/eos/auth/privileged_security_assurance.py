"""
Pure privileged security-assurance decision domain.

VERSION:
v1.0.0-P3-R1-PRIVILEGED-SECURITY-ASSURANCE

PURPOSE:
Determine whether caller-supplied current security proofs are sufficient for
one exact privileged-lifecycle purpose.

CRITICAL AUTHORITY BOUNDARIES:

SECURITY ASSURANCE != ROLE ASSIGNMENT.
SECURITY ASSURANCE != PRIVILEGED ELIGIBILITY.
SECURITY ASSURANCE != PRIVILEGED ACTIVATION.
SECURITY ASSURANCE != SESSION CREATION.
SECURITY ASSURANCE != TOKEN ISSUANCE.
SECURITY ASSURANCE != BREAK GLASS.
SECURITY ASSURANCE != FINANCIAL AUTHORITY.

The domain is deliberately principal-kind agnostic. Assurance channel is not a
human/service/machine/AI classification. A trusted caller must supply the
applicable current proof channel.

PAST SUCCESSFUL ASSURANCE != CURRENT ASSURANCE.

This module owns no persistence, repositories, MFA verification mechanism,
session lifecycle, workload-identity mechanism, HTTP, MongoDB, or activation.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Final


VERSION: Final[str] = (
    "v1.0.0-P3-R1-"
    "PRIVILEGED-SECURITY-ASSURANCE"
)


class PrivilegedAssuranceChannel(
    StrEnum
):
    """Trusted proof-channel class, never principal-kind authority."""

    INTERACTIVE_STRONG_AUTH = (
        "INTERACTIVE_STRONG_AUTH"
    )

    NONINTERACTIVE_WORKLOAD_PROOF = (
        "NONINTERACTIVE_WORKLOAD_PROOF"
    )


class PrivilegedAssurancePurpose(
    StrEnum
):
    """Exact privileged lifecycle purpose for this assurance evaluation."""

    PRIVILEGED_ELIGIBILITY_TO_ACTIVATION = (
        "PRIVILEGED_ELIGIBILITY_TO_ACTIVATION"
    )

    PRIVILEGED_ACTIVATION_USE = (
        "PRIVILEGED_ACTIVATION_USE"
    )


class PrivilegedAssuranceReason(
    StrEnum
):
    """Stable fail-closed decision classifications."""

    SUFFICIENT = "SUFFICIENT"

    PRINCIPAL_NOT_CURRENT = (
        "PRINCIPAL_NOT_CURRENT"
    )

    CREDENTIAL_NOT_CURRENT = (
        "CREDENTIAL_NOT_CURRENT"
    )

    ASSURANCE_PROOF_NOT_CURRENT = (
        "ASSURANCE_PROOF_NOT_CURRENT"
    )

    SESSION_NOT_CURRENT = (
        "SESSION_NOT_CURRENT"
    )

    FACTOR_VERIFICATION_NOT_CURRENT = (
        "FACTOR_VERIFICATION_NOT_CURRENT"
    )

    AUTHENTICATION_NOT_RECENT = (
        "AUTHENTICATION_NOT_RECENT"
    )

    WORKLOAD_PROOF_NOT_CURRENT = (
        "WORKLOAD_PROOF_NOT_CURRENT"
    )

    CHANNEL_INPUT_MISMATCH = (
        "CHANNEL_INPUT_MISMATCH"
    )


@dataclass(
    frozen=True,
    slots=True,
)
class PrivilegedSecurityAssuranceDecision:
    """Pure immutable P3 assurance decision."""

    principal_id: str
    assurance_channel: (
        PrivilegedAssuranceChannel
    )
    assurance_purpose: (
        PrivilegedAssurancePurpose
    )
    sufficient: bool
    reason: PrivilegedAssuranceReason

    def __post_init__(
        self,
    ) -> None:
        if (
            not isinstance(
                self.principal_id,
                str,
            )
            or not self.principal_id
            or self.principal_id
            != self.principal_id.strip()
        ):
            raise ValueError(
                "PRINCIPAL_ID_INVALID"
            )

        if not isinstance(
            self.assurance_channel,
            PrivilegedAssuranceChannel,
        ):
            raise TypeError(
                "ASSURANCE_CHANNEL_INVALID"
            )

        if not isinstance(
            self.assurance_purpose,
            PrivilegedAssurancePurpose,
        ):
            raise TypeError(
                "ASSURANCE_PURPOSE_INVALID"
            )

        if not isinstance(
            self.sufficient,
            bool,
        ):
            raise TypeError(
                "SUFFICIENT_INVALID"
            )

        if not isinstance(
            self.reason,
            PrivilegedAssuranceReason,
        ):
            raise TypeError(
                "REASON_INVALID"
            )

        if (
            self.sufficient
            and self.reason
            is not PrivilegedAssuranceReason
            .SUFFICIENT
        ):
            raise ValueError(
                "SUFFICIENT_REASON_MISMATCH"
            )

        if (
            not self.sufficient
            and self.reason
            is PrivilegedAssuranceReason
            .SUFFICIENT
        ):
            raise ValueError(
                "INSUFFICIENT_REASON_MISMATCH"
            )


def _principal(
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
    ):
        raise ValueError(
            "PRINCIPAL_ID_INVALID"
        )

    return value


def _required_bool(
    value: object,
    field: str,
) -> bool:
    if not isinstance(
        value,
        bool,
    ):
        raise TypeError(
            field
            + "_INVALID"
        )

    return value


def _optional_bool_shape(
    value: object,
) -> bool:
    return (
        value is None
        or isinstance(
            value,
            bool,
        )
    )


def _optional_reference_shape(
    value: object,
) -> bool:
    return (
        value is None
        or (
            isinstance(
                value,
                str,
            )
            and bool(value)
            and value
            == value.strip()
        )
    )


def _decision(
    *,
    principal_id: str,
    assurance_channel: (
        PrivilegedAssuranceChannel
    ),
    assurance_purpose: (
        PrivilegedAssurancePurpose
    ),
    sufficient: bool,
    reason: PrivilegedAssuranceReason,
) -> PrivilegedSecurityAssuranceDecision:
    return (
        PrivilegedSecurityAssuranceDecision(
            principal_id=
                principal_id,
            assurance_channel=
                assurance_channel,
            assurance_purpose=
                assurance_purpose,
            sufficient=
                sufficient,
            reason=
                reason,
        )
    )


def evaluate_privileged_security_assurance(
    *,
    principal_id: object,
    principal_current: object,
    credential_current: object,
    assurance_channel: object,
    assurance_proof_current: object,
    assurance_purpose: object,
    session_current: object = None,
    factor_verification_current: object = None,
    authentication_recency_current: object = None,
    workload_proof_current: object = None,
    workload_proof_reference: object = None,
) -> PrivilegedSecurityAssuranceDecision:
    """Evaluate one exact current privileged security-assurance request.

    Common currentness is required for every channel:
      principal current
      credential current
      assurance proof current

    Interactive strong-auth additionally requires:
      current session
      current factor verification
      recent authentication

    Noninteractive workload proof additionally requires:
      current workload proof
      one nonblank proof reference

    Channel-specific material from the other channel is rejected as a
    CHANNEL_INPUT_MISMATCH. Missing channel-required proof is also denied
    instead of being guessed or defaulted.

    No role, eligibility, activation, session, token, factor, workload identity,
    break-glass state, persistence, or financial authority is created here.
    """

    principal = _principal(
        principal_id
    )

    principal_is_current = (
        _required_bool(
            principal_current,
            "PRINCIPAL_CURRENT",
        )
    )

    credential_is_current = (
        _required_bool(
            credential_current,
            "CREDENTIAL_CURRENT",
        )
    )

    proof_is_current = (
        _required_bool(
            assurance_proof_current,
            "ASSURANCE_PROOF_CURRENT",
        )
    )

    if not isinstance(
        assurance_channel,
        PrivilegedAssuranceChannel,
    ):
        raise TypeError(
            "ASSURANCE_CHANNEL_INVALID"
        )

    if not isinstance(
        assurance_purpose,
        PrivilegedAssurancePurpose,
    ):
        raise TypeError(
            "ASSURANCE_PURPOSE_INVALID"
        )

    if not all(
        (
            _optional_bool_shape(
                session_current
            ),
            _optional_bool_shape(
                factor_verification_current
            ),
            _optional_bool_shape(
                authentication_recency_current
            ),
            _optional_bool_shape(
                workload_proof_current
            ),
            _optional_reference_shape(
                workload_proof_reference
            ),
        )
    ):
        return _decision(
            principal_id=principal,
            assurance_channel=
                assurance_channel,
            assurance_purpose=
                assurance_purpose,
            sufficient=False,
            reason=(
                PrivilegedAssuranceReason
                .CHANNEL_INPUT_MISMATCH
            ),
        )

    if not principal_is_current:
        return _decision(
            principal_id=principal,
            assurance_channel=
                assurance_channel,
            assurance_purpose=
                assurance_purpose,
            sufficient=False,
            reason=(
                PrivilegedAssuranceReason
                .PRINCIPAL_NOT_CURRENT
            ),
        )

    if not credential_is_current:
        return _decision(
            principal_id=principal,
            assurance_channel=
                assurance_channel,
            assurance_purpose=
                assurance_purpose,
            sufficient=False,
            reason=(
                PrivilegedAssuranceReason
                .CREDENTIAL_NOT_CURRENT
            ),
        )

    if not proof_is_current:
        return _decision(
            principal_id=principal,
            assurance_channel=
                assurance_channel,
            assurance_purpose=
                assurance_purpose,
            sufficient=False,
            reason=(
                PrivilegedAssuranceReason
                .ASSURANCE_PROOF_NOT_CURRENT
            ),
        )

    if (
        assurance_channel
        is PrivilegedAssuranceChannel
        .INTERACTIVE_STRONG_AUTH
    ):
        if (
            workload_proof_current
            is not None
            or workload_proof_reference
            is not None
        ):
            return _decision(
                principal_id=principal,
                assurance_channel=
                    assurance_channel,
                assurance_purpose=
                    assurance_purpose,
                sufficient=False,
                reason=(
                    PrivilegedAssuranceReason
                    .CHANNEL_INPUT_MISMATCH
                ),
            )

        if (
            session_current
            is None
            or factor_verification_current
            is None
            or authentication_recency_current
            is None
        ):
            return _decision(
                principal_id=principal,
                assurance_channel=
                    assurance_channel,
                assurance_purpose=
                    assurance_purpose,
                sufficient=False,
                reason=(
                    PrivilegedAssuranceReason
                    .CHANNEL_INPUT_MISMATCH
                ),
            )

        if not session_current:
            return _decision(
                principal_id=principal,
                assurance_channel=
                    assurance_channel,
                assurance_purpose=
                    assurance_purpose,
                sufficient=False,
                reason=(
                    PrivilegedAssuranceReason
                    .SESSION_NOT_CURRENT
                ),
            )

        if not factor_verification_current:
            return _decision(
                principal_id=principal,
                assurance_channel=
                    assurance_channel,
                assurance_purpose=
                    assurance_purpose,
                sufficient=False,
                reason=(
                    PrivilegedAssuranceReason
                    .FACTOR_VERIFICATION_NOT_CURRENT
                ),
            )

        if not authentication_recency_current:
            return _decision(
                principal_id=principal,
                assurance_channel=
                    assurance_channel,
                assurance_purpose=
                    assurance_purpose,
                sufficient=False,
                reason=(
                    PrivilegedAssuranceReason
                    .AUTHENTICATION_NOT_RECENT
                ),
            )

        return _decision(
            principal_id=principal,
            assurance_channel=
                assurance_channel,
            assurance_purpose=
                assurance_purpose,
            sufficient=True,
            reason=(
                PrivilegedAssuranceReason
                .SUFFICIENT
            ),
        )

    if (
        session_current is not None
        or factor_verification_current
        is not None
        or authentication_recency_current
        is not None
    ):
        return _decision(
            principal_id=principal,
            assurance_channel=
                assurance_channel,
            assurance_purpose=
                assurance_purpose,
            sufficient=False,
            reason=(
                PrivilegedAssuranceReason
                .CHANNEL_INPUT_MISMATCH
            ),
        )

    if (
        workload_proof_current
        is None
        or workload_proof_reference
        is None
    ):
        return _decision(
            principal_id=principal,
            assurance_channel=
                assurance_channel,
            assurance_purpose=
                assurance_purpose,
            sufficient=False,
            reason=(
                PrivilegedAssuranceReason
                .CHANNEL_INPUT_MISMATCH
            ),
        )

    if not workload_proof_current:
        return _decision(
            principal_id=principal,
            assurance_channel=
                assurance_channel,
            assurance_purpose=
                assurance_purpose,
            sufficient=False,
            reason=(
                PrivilegedAssuranceReason
                .WORKLOAD_PROOF_NOT_CURRENT
            ),
        )

    return _decision(
        principal_id=principal,
        assurance_channel=
            assurance_channel,
        assurance_purpose=
            assurance_purpose,
        sufficient=True,
        reason=(
            PrivilegedAssuranceReason
            .SUFFICIENT
        ),
    )


__all__ = [
    "VERSION",
    "PrivilegedAssuranceChannel",
    "PrivilegedAssurancePurpose",
    "PrivilegedAssuranceReason",
    "PrivilegedSecurityAssuranceDecision",
    "evaluate_privileged_security_assurance",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: privileged_security_assurance.py
# VERSION: v1.0.0-P3-R1-PRIVILEGED-SECURITY-ASSURANCE
# PRINCIPAL KIND: deliberately absent
# CHANNELS: interactive strong auth / noninteractive workload proof
# CURRENTNESS: all required proof must be current at evaluation
# MFA REGISTRATION: never accepted as factor-verification authority
# AUTHORITY: no role, P2 eligibility, activation, session, token, or break glass
# PERSISTENCE: none
# FINANCIAL EXECUTION AUTHORITY: None
# END OF WILSY OS SOVEREIGN ARTIFACT
