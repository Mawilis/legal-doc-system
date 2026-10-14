"""
Immutable privileged-eligibility evidence domain.

VERSION:
v1.0.0-P2-R2-A1-PRIVILEGED-ELIGIBILITY-EVIDENCE

PURPOSE:
Persistable audit evidence for one exact P2 privileged-eligibility evaluation.

CRITICAL AUTHORITY BOUNDARY:
Evidence is historic audit material only.

PAST ELIGIBILITY != CURRENT ELIGIBILITY.
ELIGIBILITY EVIDENCE != ROLE ASSIGNMENT.
ELIGIBILITY EVIDENCE != PRIVILEGED ACTIVATION.
ELIGIBILITY EVIDENCE != CURRENT AUTHORITY.
ELIGIBILITY EVIDENCE != SECURITY ASSURANCE.
ELIGIBILITY EVIDENCE != SESSION AUTHORITY.
ELIGIBILITY EVIDENCE != BREAK GLASS.
ELIGIBILITY EVIDENCE != FINANCIAL AUTHORITY.

Every later privileged activation must independently re-evaluate current
authority/currentness. This artifact must never be consumed as a substitute
for live/current IAM facts.

PERSISTENCE POSTURE:
One immutable row per evaluation. No revision or sequence chain. No TTL.
The later registry owns exact-replay/collision classification but does not own
authentication, authorization, role mutation, activation, or transactions.
"""

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha3_512
import json
from typing import Final, Mapping

from tools.eos.auth.privileged_eligibility import (
    PrivilegedEligibilityDecision,
    PrivilegedEligibilityReason,
    PrivilegedTargetClass,
)


LEGACY_VERSION: Final[str] = (
    "v1.0.0-P2-R2-A1-"
    "PRIVILEGED-ELIGIBILITY-EVIDENCE"
)

LEGACY_SCHEMA: Final[str] = (
    "WILSY-PRIVILEGED-ELIGIBILITY-EVIDENCE/V1"
)

VERSION: Final[str] = (
    "v2.0.0-P2-R5-R3-"
    "PRIVILEGED-ELIGIBILITY-EVIDENCE"
)

SCHEMA: Final[str] = (
    "WILSY-PRIVILEGED-ELIGIBILITY-EVIDENCE/V2"
)

_FINGERPRINT_HEX_LENGTH: Final[int] = 128


class PrivilegedEligibilityEvidenceError(
    ValueError
):
    """Base evidence validation failure."""


class PrivilegedEligibilityEvidencePersistedRecordInvalidError(
    PrivilegedEligibilityEvidenceError
):
    """Persisted evidence failed strict hydration."""


def _nonblank(
    value: object,
    field: str,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise PrivilegedEligibilityEvidenceError(
            field.upper()
            + "_INVALID"
        )

    return value


def _optional_nonblank(
    value: object,
    field: str,
) -> str | None:
    if value is None:
        return None

    return _nonblank(
        value,
        field,
    )


def _aware_datetime(
    value: object,
    field: str,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PrivilegedEligibilityEvidenceError(
            field.upper()
            + "_INVALID"
        )

    return value


def _canonical(
    value: Mapping[str, object],
) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _fingerprint(
    value: Mapping[str, object],
) -> str:
    return sha3_512(
        _canonical(value)
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class PrivilegedEligibilityEvidence:
    """Immutable privileged-eligibility evidence.

    V1 rows remain readable as historical evidence.  Every object newly
    produced by ``from_decision`` is V2.  Platform-system-root V2 evidence
    requires complete durable prerequisite lineage; tenant evidence must
    not carry platform prerequisite lineage.

    This object grants no permission or activation authority.
    """

    eligibility_evidence_id: str

    principal_id: str
    privileged_role_id: str

    target_class: PrivilegedTargetClass
    tenant_id: str | None

    principal_current: bool
    tenant_membership_current: bool | None
    workforce_required: bool
    tenant_workforce_current: bool | None
    platform_prerequisite_proven: bool | None

    platform_prerequisite_id: str | None
    platform_prerequisite_revision: int | None
    platform_prerequisite_fingerprint: str | None
    platform_prerequisite_source_evidence_reference: str | None

    eligible: bool
    reason: PrivilegedEligibilityReason

    evaluated_at: datetime
    idempotency_key: str

    eligibility_evidence_fingerprint: str

    @staticmethod
    def _lineage_complete(
        *,
        platform_prerequisite_id: object,
        platform_prerequisite_revision: object,
        platform_prerequisite_fingerprint: object,
        platform_prerequisite_source_evidence_reference: object,
    ) -> tuple[str, int, str, str]:
        prerequisite_id = _nonblank(
            platform_prerequisite_id,
            "platform_prerequisite_id",
        )

        revision = platform_prerequisite_revision
        if (
            isinstance(revision, bool)
            or not isinstance(revision, int)
            or revision < 1
        ):
            raise PrivilegedEligibilityEvidenceError(
                "PLATFORM_PREREQUISITE_REVISION_INVALID"
            )

        prerequisite_fingerprint = _nonblank(
            platform_prerequisite_fingerprint,
            "platform_prerequisite_fingerprint",
        )

        if (
            len(prerequisite_fingerprint) != 128
            or prerequisite_fingerprint
            != prerequisite_fingerprint.lower()
            or any(
                char not in "0123456789abcdef"
                for char in prerequisite_fingerprint
            )
        ):
            raise PrivilegedEligibilityEvidenceError(
                "PLATFORM_PREREQUISITE_FINGERPRINT_INVALID"
            )

        source_reference = _nonblank(
            platform_prerequisite_source_evidence_reference,
            "platform_prerequisite_source_evidence_reference",
        )

        return (
            prerequisite_id,
            revision,
            prerequisite_fingerprint,
            source_reference,
        )

    def _has_no_lineage(
        self,
    ) -> bool:
        return all(
            value is None
            for value in (
                self.platform_prerequisite_id,
                self.platform_prerequisite_revision,
                self.platform_prerequisite_fingerprint,
                self.platform_prerequisite_source_evidence_reference,
            )
        )

    def _legacy_payload(
        self,
        *,
        evaluated_at: datetime | None = None,
    ) -> dict[str, object]:
        moment = (
            self.evaluated_at
            if evaluated_at is None
            else evaluated_at
        )

        return {
            "schema": LEGACY_SCHEMA,
            "version": LEGACY_VERSION,
            "eligibility_evidence_id":
                self.eligibility_evidence_id,
            "principal_id":
                self.principal_id,
            "privileged_role_id":
                self.privileged_role_id,
            "target_class":
                self.target_class.value,
            "tenant_id":
                self.tenant_id,
            "principal_current":
                self.principal_current,
            "tenant_membership_current":
                self.tenant_membership_current,
            "workforce_required":
                self.workforce_required,
            "tenant_workforce_current":
                self.tenant_workforce_current,
            "platform_prerequisite_proven":
                self.platform_prerequisite_proven,
            "eligible":
                self.eligible,
            "reason":
                self.reason.value,
            "evaluated_at":
                moment.isoformat(),
            "idempotency_key":
                self.idempotency_key,
        }

    def _payload(
        self,
        *,
        evaluated_at: datetime | None = None,
    ) -> dict[str, object]:
        moment = (
            self.evaluated_at
            if evaluated_at is None
            else evaluated_at
        )

        return {
            "schema": SCHEMA,
            "version": VERSION,
            "eligibility_evidence_id":
                self.eligibility_evidence_id,
            "principal_id":
                self.principal_id,
            "privileged_role_id":
                self.privileged_role_id,
            "target_class":
                self.target_class.value,
            "tenant_id":
                self.tenant_id,
            "principal_current":
                self.principal_current,
            "tenant_membership_current":
                self.tenant_membership_current,
            "workforce_required":
                self.workforce_required,
            "tenant_workforce_current":
                self.tenant_workforce_current,
            "platform_prerequisite_proven":
                self.platform_prerequisite_proven,
            "platform_prerequisite_id":
                self.platform_prerequisite_id,
            "platform_prerequisite_revision":
                self.platform_prerequisite_revision,
            "platform_prerequisite_fingerprint":
                self.platform_prerequisite_fingerprint,
            "platform_prerequisite_source_evidence_reference":
                self.platform_prerequisite_source_evidence_reference,
            "eligible":
                self.eligible,
            "reason":
                self.reason.value,
            "evaluated_at":
                moment.isoformat(),
            "idempotency_key":
                self.idempotency_key,
        }

    def __post_init__(
        self,
    ) -> None:
        _nonblank(
            self.eligibility_evidence_id,
            "eligibility_evidence_id",
        )
        _nonblank(
            self.principal_id,
            "principal_id",
        )
        _nonblank(
            self.privileged_role_id,
            "privileged_role_id",
        )

        if not isinstance(
            self.target_class,
            PrivilegedTargetClass,
        ):
            raise PrivilegedEligibilityEvidenceError(
                "TARGET_CLASS_INVALID"
            )

        tenant = _optional_nonblank(
            self.tenant_id,
            "tenant_id",
        )

        if not isinstance(
            self.principal_current,
            bool,
        ):
            raise PrivilegedEligibilityEvidenceError(
                "PRINCIPAL_CURRENT_INVALID"
            )

        for field, value in (
            (
                "TENANT_MEMBERSHIP_CURRENT",
                self.tenant_membership_current,
            ),
            (
                "TENANT_WORKFORCE_CURRENT",
                self.tenant_workforce_current,
            ),
            (
                "PLATFORM_PREREQUISITE_PROVEN",
                self.platform_prerequisite_proven,
            ),
        ):
            if (
                value is not None
                and not isinstance(value, bool)
            ):
                raise PrivilegedEligibilityEvidenceError(
                    field + "_INVALID"
                )

        if not isinstance(
            self.workforce_required,
            bool,
        ):
            raise PrivilegedEligibilityEvidenceError(
                "WORKFORCE_REQUIRED_INVALID"
            )

        if not isinstance(
            self.eligible,
            bool,
        ):
            raise PrivilegedEligibilityEvidenceError(
                "ELIGIBLE_INVALID"
            )

        if not isinstance(
            self.reason,
            PrivilegedEligibilityReason,
        ):
            raise PrivilegedEligibilityEvidenceError(
                "REASON_INVALID"
            )

        evaluated = _aware_datetime(
            self.evaluated_at,
            "evaluated_at",
        )

        _nonblank(
            self.idempotency_key,
            "idempotency_key",
        )

        if (
            self.target_class
            is PrivilegedTargetClass.TENANT_PRIVILEGED
        ):
            if tenant is None:
                raise PrivilegedEligibilityEvidenceError(
                    "TENANT_SCOPE_REQUIRED"
                )

        elif (
            self.target_class
            is PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT
        ):
            if tenant is not None:
                raise PrivilegedEligibilityEvidenceError(
                    "PLATFORM_SCOPE_TENANT_FORBIDDEN"
                )

        legacy_expected = _fingerprint(
            self._legacy_payload(
                evaluated_at=evaluated,
            )
        )

        if (
            self._has_no_lineage()
            and self.eligibility_evidence_fingerprint
            == legacy_expected
        ):
            # Historical V1 is readable but has no durable prerequisite
            # lineage and therefore cannot satisfy future platform
            # currentness.
            return

        if (
            self.target_class
            is PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT
        ):
            self._lineage_complete(
                platform_prerequisite_id=
                    self.platform_prerequisite_id,
                platform_prerequisite_revision=
                    self.platform_prerequisite_revision,
                platform_prerequisite_fingerprint=
                    self.platform_prerequisite_fingerprint,
                platform_prerequisite_source_evidence_reference=
                    self.platform_prerequisite_source_evidence_reference,
            )

        else:
            if not self._has_no_lineage():
                raise PrivilegedEligibilityEvidenceError(
                    "TENANT_PLATFORM_LINEAGE_FORBIDDEN"
                )

        expected = _fingerprint(
            self._payload(
                evaluated_at=evaluated,
            )
        )

        if (
            self.eligibility_evidence_fingerprint
            != expected
        ):
            raise PrivilegedEligibilityEvidenceError(
                "EVIDENCE_FINGERPRINT_INVALID"
            )

    @classmethod
    def from_decision(
        cls,
        *,
        eligibility_evidence_id: object,
        decision: object,
        evaluated_at: object,
        idempotency_key: object,
        platform_prerequisite_id: object = None,
        platform_prerequisite_revision: object = None,
        platform_prerequisite_fingerprint: object = None,
        platform_prerequisite_source_evidence_reference: object = None,
    ) -> "PrivilegedEligibilityEvidence":
        if not isinstance(
            decision,
            PrivilegedEligibilityDecision,
        ):
            raise PrivilegedEligibilityEvidenceError(
                "DECISION_INVALID"
            )

        if decision.target_class is None:
            raise PrivilegedEligibilityEvidenceError(
                "DECISION_TARGET_CLASS_INVALID"
            )

        evidence_id = _nonblank(
            eligibility_evidence_id,
            "eligibility_evidence_id",
        )

        moment = _aware_datetime(
            evaluated_at,
            "evaluated_at",
        )

        replay_key = _nonblank(
            idempotency_key,
            "idempotency_key",
        )

        if (
            decision.target_class
            is PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT
        ):
            (
                prerequisite_id,
                prerequisite_revision,
                prerequisite_fingerprint,
                prerequisite_source_reference,
            ) = cls._lineage_complete(
                platform_prerequisite_id=
                    platform_prerequisite_id,
                platform_prerequisite_revision=
                    platform_prerequisite_revision,
                platform_prerequisite_fingerprint=
                    platform_prerequisite_fingerprint,
                platform_prerequisite_source_evidence_reference=
                    platform_prerequisite_source_evidence_reference,
            )

        else:
            supplied = (
                platform_prerequisite_id,
                platform_prerequisite_revision,
                platform_prerequisite_fingerprint,
                platform_prerequisite_source_evidence_reference,
            )

            if any(
                value is not None
                for value in supplied
            ):
                raise PrivilegedEligibilityEvidenceError(
                    "TENANT_PLATFORM_LINEAGE_FORBIDDEN"
                )

            prerequisite_id = None
            prerequisite_revision = None
            prerequisite_fingerprint = None
            prerequisite_source_reference = None

        provisional = {
            "schema": SCHEMA,
            "version": VERSION,
            "eligibility_evidence_id":
                evidence_id,
            "principal_id":
                decision.principal_id,
            "privileged_role_id":
                decision.privileged_role_id,
            "target_class":
                decision.target_class.value,
            "tenant_id":
                decision.tenant_id,
            "principal_current":
                decision.principal_current,
            "tenant_membership_current":
                decision.tenant_membership_current,
            "workforce_required":
                decision.workforce_required,
            "tenant_workforce_current":
                decision.tenant_workforce_current,
            "platform_prerequisite_proven":
                decision.platform_prerequisite_proven,
            "platform_prerequisite_id":
                prerequisite_id,
            "platform_prerequisite_revision":
                prerequisite_revision,
            "platform_prerequisite_fingerprint":
                prerequisite_fingerprint,
            "platform_prerequisite_source_evidence_reference":
                prerequisite_source_reference,
            "eligible":
                decision.eligible,
            "reason":
                decision.reason.value,
            "evaluated_at":
                moment.isoformat(),
            "idempotency_key":
                replay_key,
        }

        return cls(
            eligibility_evidence_id=
                evidence_id,
            principal_id=
                decision.principal_id,
            privileged_role_id=
                decision.privileged_role_id,
            target_class=
                decision.target_class,
            tenant_id=
                decision.tenant_id,
            principal_current=
                decision.principal_current,
            tenant_membership_current=
                decision.tenant_membership_current,
            workforce_required=
                decision.workforce_required,
            tenant_workforce_current=
                decision.tenant_workforce_current,
            platform_prerequisite_proven=
                decision.platform_prerequisite_proven,
            platform_prerequisite_id=
                prerequisite_id,
            platform_prerequisite_revision=
                prerequisite_revision,
            platform_prerequisite_fingerprint=
                prerequisite_fingerprint,
            platform_prerequisite_source_evidence_reference=
                prerequisite_source_reference,
            eligible=
                decision.eligible,
            reason=
                decision.reason,
            evaluated_at=
                moment,
            idempotency_key=
                replay_key,
            eligibility_evidence_fingerprint=
                _fingerprint(provisional),
        )

    def to_persisted(
        self,
    ) -> dict[str, object]:
        legacy_expected = _fingerprint(
            self._legacy_payload()
        )

        if (
            self._has_no_lineage()
            and self.eligibility_evidence_fingerprint
            == legacy_expected
        ):
            return {
                **self._legacy_payload(),
                "eligibility_evidence_fingerprint":
                    self.eligibility_evidence_fingerprint,
            }

        return {
            **self._payload(),
            "eligibility_evidence_fingerprint":
                self.eligibility_evidence_fingerprint,
        }

    @classmethod
    def from_persisted(
        cls,
        row: object,
    ) -> "PrivilegedEligibilityEvidence":
        if not isinstance(row, Mapping):
            raise (
                PrivilegedEligibilityEvidencePersistedRecordInvalidError(
                    "PERSISTED_RECORD_INVALID"
                )
            )

        legacy_keys = {
            "schema",
            "version",
            "eligibility_evidence_id",
            "principal_id",
            "privileged_role_id",
            "target_class",
            "tenant_id",
            "principal_current",
            "tenant_membership_current",
            "workforce_required",
            "tenant_workforce_current",
            "platform_prerequisite_proven",
            "eligible",
            "reason",
            "evaluated_at",
            "idempotency_key",
            "eligibility_evidence_fingerprint",
        }

        current_keys = {
            *legacy_keys,
            "platform_prerequisite_id",
            "platform_prerequisite_revision",
            "platform_prerequisite_fingerprint",
            "platform_prerequisite_source_evidence_reference",
        }

        legacy = (
            row.get("schema") == LEGACY_SCHEMA
            and row.get("version") == LEGACY_VERSION
        )

        current = (
            row.get("schema") == SCHEMA
            and row.get("version") == VERSION
        )

        if legacy:
            if set(row) != legacy_keys:
                raise (
                    PrivilegedEligibilityEvidencePersistedRecordInvalidError(
                        "PERSISTED_SHAPE_INVALID"
                    )
                )

        elif current:
            if set(row) != current_keys:
                raise (
                    PrivilegedEligibilityEvidencePersistedRecordInvalidError(
                        "PERSISTED_SHAPE_INVALID"
                    )
                )

        else:
            if row.get("schema") not in {
                LEGACY_SCHEMA,
                SCHEMA,
            }:
                raise (
                    PrivilegedEligibilityEvidencePersistedRecordInvalidError(
                        "PERSISTED_SCHEMA_INVALID"
                    )
                )

            raise (
                PrivilegedEligibilityEvidencePersistedRecordInvalidError(
                    "PERSISTED_VERSION_INVALID"
                )
            )

        try:
            target_class = PrivilegedTargetClass(
                row["target_class"]
            )

            reason = PrivilegedEligibilityReason(
                row["reason"]
            )

            evaluated_raw = row["evaluated_at"]

            if not isinstance(
                evaluated_raw,
                str,
            ):
                raise ValueError

            evaluated_at = datetime.fromisoformat(
                evaluated_raw
            )

            return cls(
                eligibility_evidence_id=
                    row["eligibility_evidence_id"],
                principal_id=
                    row["principal_id"],
                privileged_role_id=
                    row["privileged_role_id"],
                target_class=
                    target_class,
                tenant_id=
                    row["tenant_id"],
                principal_current=
                    row["principal_current"],
                tenant_membership_current=
                    row["tenant_membership_current"],
                workforce_required=
                    row["workforce_required"],
                tenant_workforce_current=
                    row["tenant_workforce_current"],
                platform_prerequisite_proven=
                    row["platform_prerequisite_proven"],
                platform_prerequisite_id=(
                    None
                    if legacy
                    else row["platform_prerequisite_id"]
                ),
                platform_prerequisite_revision=(
                    None
                    if legacy
                    else row["platform_prerequisite_revision"]
                ),
                platform_prerequisite_fingerprint=(
                    None
                    if legacy
                    else row["platform_prerequisite_fingerprint"]
                ),
                platform_prerequisite_source_evidence_reference=(
                    None
                    if legacy
                    else row[
                        "platform_prerequisite_source_evidence_reference"
                    ]
                ),
                eligible=
                    row["eligible"],
                reason=
                    reason,
                evaluated_at=
                    evaluated_at,
                idempotency_key=
                    row["idempotency_key"],
                eligibility_evidence_fingerprint=
                    row["eligibility_evidence_fingerprint"],
            )

        except (
            KeyError,
            TypeError,
            ValueError,
            PrivilegedEligibilityEvidenceError,
        ) as error:
            raise (
                PrivilegedEligibilityEvidencePersistedRecordInvalidError(
                    "PERSISTED_RECORD_INVALID"
                )
            ) from error



__all__ = [
    "VERSION",
    "SCHEMA",
    "PrivilegedEligibilityEvidenceError",
    "PrivilegedEligibilityEvidencePersistedRecordInvalidError",
    "PrivilegedEligibilityEvidence",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: privileged_eligibility_evidence.py
# VERSION: v1.0.0-P2-R2-A1-PRIVILEGED-ELIGIBILITY-EVIDENCE
# IMMUTABILITY: one evidence row per evaluation; no revision/sequence chain
# CURRENTNESS: past eligibility never proves current eligibility
# AUTHORITY: no role assignment, activation, session, break-glass, or finance
# SECURITY ASSURANCE: absent; owned by later P3
# TTL: forbidden for durable evidence
# FINANCIAL EXECUTION AUTHORITY: None
# END OF WILSY OS SOVEREIGN ARTIFACT
