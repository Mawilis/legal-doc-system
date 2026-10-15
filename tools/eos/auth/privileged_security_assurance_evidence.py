"""
Immutable historic evidence for one P3 privileged security-assurance evaluation.

VERSION:
v1.0.0-P3-R2-A1-PRIVILEGED-SECURITY-ASSURANCE-EVIDENCE

BOUNDARY:

Historic evidence != current security assurance.
Historic sufficient evidence != current privileged authority.

This value records one already-completed P3 evaluation. It does not re-evaluate
P3, verify MFA, establish workload identity, create sessions or tokens, assign
roles, establish P2 eligibility, activate privilege, create break glass, or
exercise financial authority.

No tenant field is present because the certified P3-R1 decision contract owns
no tenant input. No sequence chain, expiry, TTL, source revision, or invented
proof fingerprint is added.

Raw passwords, password hashes, MFA/TOTP secrets, OTPs, session/refresh
bearers, JWTs, API keys, private keys, and workload credentials are forbidden
from the evidence surface.
"""

from dataclasses import (
    dataclass,
    fields,
)
from datetime import (
    datetime,
    timezone,
)
from enum import StrEnum
from hashlib import sha3_512
import hmac
import json
import re
from typing import (
    Final,
    Mapping,
)

from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssuranceChannel,
    PrivilegedAssurancePurpose,
    PrivilegedAssuranceReason,
    PrivilegedSecurityAssuranceDecision,
)


VERSION: Final[str] = (
    "v1.0.0-P3-R2-A1-"
    "PRIVILEGED-SECURITY-ASSURANCE-EVIDENCE"
)

SCHEMA: Final[str] = (
    "WILSY-PRIVILEGED-SECURITY-"
    "ASSURANCE-EVIDENCE/V1"
)

MAX_IDENTIFIER_LENGTH: Final[int] = 512

_SHA3_512 = re.compile(
    r"^[0-9a-f]{128}$"
)


class PrivilegedSecurityAssuranceEvidenceError(
    ValueError
):
    """Fail-closed immutable evidence validation error."""


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
        or len(value) > MAX_IDENTIFIER_LENGTH
    ):
        raise (
            PrivilegedSecurityAssuranceEvidenceError(
                name + " is invalid"
            )
        )

    return value


def _optional_reference(
    value: object,
) -> str | None:
    if value is None:
        return None

    return _text(
        "workload_proof_reference",
        value,
    )


def _required_bool(
    name: str,
    value: object,
) -> bool:
    if not isinstance(
        value,
        bool,
    ):
        raise (
            PrivilegedSecurityAssuranceEvidenceError(
                name + " is invalid"
            )
        )

    return value


def _optional_bool(
    name: str,
    value: object,
) -> bool | None:
    if value is None:
        return None

    return _required_bool(
        name,
        value,
    )


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
            PrivilegedSecurityAssuranceEvidenceError(
                "evaluated_at is invalid"
            )
        )

    return value.astimezone(
        timezone.utc
    )


@dataclass(
    frozen=True,
    slots=True,
)
class PrivilegedSecurityAssuranceEvidence:
    """Immutable historic record of one exact already-evaluated P3 decision."""

    assurance_evidence_id: str

    principal_id: str

    assurance_channel: (
        PrivilegedAssuranceChannel
    )

    assurance_purpose: (
        PrivilegedAssurancePurpose
    )

    principal_current: bool
    credential_current: bool
    assurance_proof_current: bool

    session_current: bool | None

    factor_verification_current: (
        bool | None
    )

    authentication_recency_current: (
        bool | None
    )

    workload_proof_current: bool | None

    workload_proof_reference: (
        str | None
    )

    sufficient: bool

    reason: PrivilegedAssuranceReason

    evaluated_at: datetime

    idempotency_key: str

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "assurance_evidence_id",
            _text(
                "assurance_evidence_id",
                self.assurance_evidence_id,
            ),
        )

        object.__setattr__(
            self,
            "principal_id",
            _text(
                "principal_id",
                self.principal_id,
            ),
        )

        object.__setattr__(
            self,
            "idempotency_key",
            _text(
                "idempotency_key",
                self.idempotency_key,
            ),
        )

        if not isinstance(
            self.assurance_channel,
            PrivilegedAssuranceChannel,
        ):
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "assurance_channel is invalid"
                )
            )

        if not isinstance(
            self.assurance_purpose,
            PrivilegedAssurancePurpose,
        ):
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "assurance_purpose is invalid"
                )
            )

        if not isinstance(
            self.reason,
            PrivilegedAssuranceReason,
        ):
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "reason is invalid"
                )
            )

        for name in (
            "principal_current",
            "credential_current",
            "assurance_proof_current",
            "sufficient",
        ):
            object.__setattr__(
                self,
                name,
                _required_bool(
                    name,
                    getattr(
                        self,
                        name,
                    ),
                ),
            )

        for name in (
            "session_current",
            "factor_verification_current",
            "authentication_recency_current",
            "workload_proof_current",
        ):
            object.__setattr__(
                self,
                name,
                _optional_bool(
                    name,
                    getattr(
                        self,
                        name,
                    ),
                ),
            )

        object.__setattr__(
            self,
            "workload_proof_reference",
            _optional_reference(
                self.workload_proof_reference
            ),
        )

        object.__setattr__(
            self,
            "evaluated_at",
            _timestamp(
                self.evaluated_at
            ),
        )

        if (
            self.sufficient
            and self.reason
            is not PrivilegedAssuranceReason
            .SUFFICIENT
        ):
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "decision result is inconsistent"
                )
            )

        if (
            not self.sufficient
            and self.reason
            is PrivilegedAssuranceReason
            .SUFFICIENT
        ):
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "decision result is inconsistent"
                )
            )

        if (
            self.assurance_channel
            is PrivilegedAssuranceChannel
            .INTERACTIVE_STRONG_AUTH
        ):
            if (
                self.workload_proof_current
                is not None
                or self.workload_proof_reference
                is not None
            ):
                raise (
                    PrivilegedSecurityAssuranceEvidenceError(
                        "channel evidence shape is invalid"
                    )
                )

        elif (
            self.assurance_channel
            is PrivilegedAssuranceChannel
            .NONINTERACTIVE_WORKLOAD_PROOF
        ):
            if (
                self.session_current
                is not None
                or self.factor_verification_current
                is not None
                or self.authentication_recency_current
                is not None
            ):
                raise (
                    PrivilegedSecurityAssuranceEvidenceError(
                        "channel evidence shape is invalid"
                    )
                )

        else:
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "assurance_channel is invalid"
                )
            )

    @classmethod
    def from_decision(
        cls,
        *,
        assurance_evidence_id: str,
        decision: (
            PrivilegedSecurityAssuranceDecision
        ),
        principal_current: bool,
        credential_current: bool,
        assurance_proof_current: bool,
        session_current: bool | None,
        factor_verification_current: (
            bool | None
        ),
        authentication_recency_current: (
            bool | None
        ),
        workload_proof_current: (
            bool | None
        ),
        workload_proof_reference: (
            str | None
        ),
        evaluated_at: datetime,
        idempotency_key: str,
    ) -> "PrivilegedSecurityAssuranceEvidence":
        """Record one already-evaluated decision without re-running P3."""

        if not isinstance(
            decision,
            PrivilegedSecurityAssuranceDecision,
        ):
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "decision is invalid"
                )
            )

        return cls(
            assurance_evidence_id=
                assurance_evidence_id,
            principal_id=
                decision.principal_id,
            assurance_channel=
                decision.assurance_channel,
            assurance_purpose=
                decision.assurance_purpose,
            principal_current=
                principal_current,
            credential_current=
                credential_current,
            assurance_proof_current=
                assurance_proof_current,
            session_current=
                session_current,
            factor_verification_current=
                factor_verification_current,
            authentication_recency_current=
                authentication_recency_current,
            workload_proof_current=
                workload_proof_current,
            workload_proof_reference=
                workload_proof_reference,
            sufficient=
                decision.sufficient,
            reason=
                decision.reason,
            evaluated_at=
                evaluated_at,
            idempotency_key=
                idempotency_key,
        )

    def evidence_payload(
        self,
    ) -> dict[str, object]:
        """Return exact canonical semantic payload for deterministic sealing."""

        return {
            "schema":
                SCHEMA,
            "assurance_evidence_id":
                self.assurance_evidence_id,
            "principal_id":
                self.principal_id,
            "assurance_channel":
                self.assurance_channel.value,
            "assurance_purpose":
                self.assurance_purpose.value,
            "principal_current":
                self.principal_current,
            "credential_current":
                self.credential_current,
            "assurance_proof_current":
                self.assurance_proof_current,
            "session_current":
                self.session_current,
            "factor_verification_current":
                self.factor_verification_current,
            "authentication_recency_current":
                self.authentication_recency_current,
            "workload_proof_current":
                self.workload_proof_current,
            "workload_proof_reference":
                self.workload_proof_reference,
            "sufficient":
                self.sufficient,
            "reason":
                self.reason.value,
            "evaluated_at":
                self.evaluated_at.isoformat(
                    timespec="microseconds"
                ),
            "idempotency_key":
                self.idempotency_key,
        }

    @property
    def assurance_evidence_fingerprint(
        self,
    ) -> str:
        """Deterministic lowercase SHA3-512 over exact evidence semantics."""

        canonical = json.dumps(
            self.evidence_payload(),
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            ensure_ascii=True,
        ).encode(
            "ascii"
        )

        return sha3_512(
            canonical
        ).hexdigest()

    def to_persisted(
        self,
    ) -> dict[str, object]:
        """Return strict persisted shape without performing persistence."""

        return {
            **self.evidence_payload(),
            "assurance_evidence_fingerprint":
                self.assurance_evidence_fingerprint,
        }

    @classmethod
    def from_persisted(
        cls,
        document: Mapping[
            str,
            object,
        ],
    ) -> "PrivilegedSecurityAssuranceEvidence":
        """Strictly hydrate one historic evidence row and verify its seal."""

        data_fields = {
            field.name
            for field in fields(
                cls
            )
        }

        expected = (
            data_fields
            | {
                "schema",
                "assurance_evidence_fingerprint",
            }
        )

        if (
            not isinstance(
                document,
                Mapping,
            )
            or set(document)
            != expected
        ):
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "persisted evidence shape is invalid"
                )
            )

        if (
            document.get(
                "schema"
            )
            != SCHEMA
        ):
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "schema is invalid"
                )
            )

        raw_time = document.get(
            "evaluated_at"
        )

        if not isinstance(
            raw_time,
            str,
        ):
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "evaluated_at is not canonical"
                )
            )

        try:
            parsed_time = (
                datetime.fromisoformat(
                    raw_time
                )
            )
        except ValueError as error:
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "evaluated_at is invalid"
                )
            ) from error

        canonical_time = (
            _timestamp(
                parsed_time
            ).isoformat(
                timespec="microseconds"
            )
        )

        if raw_time != canonical_time:
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "evaluated_at is not canonical"
                )
            )

        try:
            channel = (
                PrivilegedAssuranceChannel(
                    document[
                        "assurance_channel"
                    ]
                )
            )

            purpose = (
                PrivilegedAssurancePurpose(
                    document[
                        "assurance_purpose"
                    ]
                )
            )

            reason = (
                PrivilegedAssuranceReason(
                    document[
                        "reason"
                    ]
                )
            )
        except (
            ValueError,
            TypeError,
        ) as error:
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "persisted enum value is invalid"
                )
            ) from error

        value = cls(
            assurance_evidence_id=
                document[
                    "assurance_evidence_id"
                ],  # type: ignore[arg-type]
            principal_id=
                document[
                    "principal_id"
                ],  # type: ignore[arg-type]
            assurance_channel=
                channel,
            assurance_purpose=
                purpose,
            principal_current=
                document[
                    "principal_current"
                ],  # type: ignore[arg-type]
            credential_current=
                document[
                    "credential_current"
                ],  # type: ignore[arg-type]
            assurance_proof_current=
                document[
                    "assurance_proof_current"
                ],  # type: ignore[arg-type]
            session_current=
                document[
                    "session_current"
                ],  # type: ignore[arg-type]
            factor_verification_current=
                document[
                    "factor_verification_current"
                ],  # type: ignore[arg-type]
            authentication_recency_current=
                document[
                    "authentication_recency_current"
                ],  # type: ignore[arg-type]
            workload_proof_current=
                document[
                    "workload_proof_current"
                ],  # type: ignore[arg-type]
            workload_proof_reference=
                document[
                    "workload_proof_reference"
                ],  # type: ignore[arg-type]
            sufficient=
                document[
                    "sufficient"
                ],  # type: ignore[arg-type]
            reason=
                reason,
            evaluated_at=
                parsed_time,
            idempotency_key=
                document[
                    "idempotency_key"
                ],  # type: ignore[arg-type]
        )

        stored = document.get(
            "assurance_evidence_fingerprint"
        )

        if (
            not isinstance(
                stored,
                str,
            )
            or _SHA3_512.fullmatch(
                stored
            )
            is None
        ):
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "assurance evidence fingerprint is invalid"
                )
            )

        if not hmac.compare_digest(
            stored,
            value.assurance_evidence_fingerprint,
        ):
            raise (
                PrivilegedSecurityAssuranceEvidenceError(
                    "persisted evidence fingerprint is invalid"
                )
            )

        return value


__all__ = [
    "VERSION",
    "SCHEMA",
    "PrivilegedSecurityAssuranceEvidence",
    "PrivilegedSecurityAssuranceEvidenceError",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: privileged_security_assurance_evidence.py
# VERSION: v1.0.0-P3-R2-A1-PRIVILEGED-SECURITY-ASSURANCE-EVIDENCE
# TENANT FIELD: absent by certified P3-R1 contract
# CURRENTNESS: historical only; never proves current assurance
# CHANNEL NULLABILITY: inapplicable channel fields persist as null
# SEQUENCE CHAIN: none
# TTL / EXPIRY: none
# SECRET / BEARER MATERIAL: forbidden
# PERSISTENCE: none
# ACTIVATION: none
# FINANCIAL AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
