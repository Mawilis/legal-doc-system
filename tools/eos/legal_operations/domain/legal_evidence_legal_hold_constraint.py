"""WILSY OS Legal Evidence legal-hold constraint domain.

TITLE: Legal Evidence Legal Hold Constraint
VERSION: v1.0.0-L10A2R-C4D4B-LEGAL-EVIDENCE-LEGAL-HOLD-CONSTRAINT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Bind exact Legal Evidence provider-object identity to immutable,
         externally sourced legal-hold evidence and determine only whether that
         directive blocks disposition at an explicit observation instant.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_legal_hold_constraint.py
COLLABORATION / OWNERSHIP:
    C4D4B owns pure legal-hold constraint evidence only. Authoritative hold
    source selection, durable persistence, IAM issuance/release permission,
    retention governance, orphan proof, deletion authorization and provider
    execution remain separately certified gates.
CERTIFICATION / UPDATE DATE: 2026-09-30
CHANGELOG:
    v1.0.0-L10A2R-C4D4B establishes immutable tenant/provider-object legal-hold
    directives, source-evidence binding, deterministic SHA3-512 integrity and
    explicit ACTIVE/RELEASED disposition-blocking semantics without granting
    downstream deletion or provider authority.
COMPLIANCE:
    Governance-aligned evidence primitive only. This module does not determine
    whether litigation, investigation, court, client, regulatory or other facts
    legally require a hold and does not select an authoritative legal source.
SECURITY / PRIVACY POSTURE:
    Pure immutable in-process evidence. No credentials, secrets, raw evidence
    bytes, MongoDB, provider IO, filesystem IO, network state or wall clock.
TENANT BOUNDARY:
    Exact non-global tenant identity is mandatory and fingerprinted with exact
    provider/storage/object-version, hold and source-evidence identity.
AUTHORITY BOUNDARY:
    Legal-hold constraint evidence and deterministic blocking semantics only.
    No retention satisfaction, orphan proof, deletion authorization, provider
    mutation, availability, IAM, Court execution or commercial authority.
FINANCIAL AUTHORITY BOUNDARY:
    No billing, invoice, charge, payment, execution or settlement truth.
    Kennel EOS remains exclusive financial execution authority.

PURPOSE:
    Represent one already-sourced hold directive without inferring legal basis,
    principal authorization, retention state or provider deletion permission.

SOURCE POSTURE:
    The caller supplies opaque authoritative-source evidence. This domain does
    not determine whether that source is legally sufficient.

TIME POSTURE:
    No wall-clock access exists. Every timestamp is explicit and timezone-aware.

FAIL-CLOSED DECLARATION:
    Malformed identity, pseudo/global tenant scope, malformed fingerprints,
    invalid temporal ordering, fingerprint drift and downstream-authority claims
    reject.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Final


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D4B-LEGAL-EVIDENCE-LEGAL-HOLD-CONSTRAINT"
)

_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,511}$"
)

_SHA3_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "global_root",
        "root",
        "master",
        "*",
    }
)


class LegalEvidenceLegalHoldConstraintError(ValueError):
    """Stable fail-closed C4D4B legal-hold constraint error."""


class LegalEvidenceLegalHoldState(StrEnum):
    """Closed legal-hold evidence states; never deletion authority."""

    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"


def _identity(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or _IDENTITY_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceLegalHoldConstraintError(
            f"L10A2R_C4D4B_{name.upper()}_INVALID"
        )
    return value


def _tenant(value: object) -> str:
    tenant = _identity(
        "tenant_id",
        value,
    )
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceLegalHoldConstraintError(
            "L10A2R_C4D4B_TENANT_REQUIRED"
        )
    return tenant


def _sha3(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or _SHA3_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceLegalHoldConstraintError(
            f"L10A2R_C4D4B_{name.upper()}_INVALID"
        )
    return value


def _utc(name: str, value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceLegalHoldConstraintError(
            f"L10A2R_C4D4B_{name.upper()}_INVALID"
        )
    return value.astimezone(
        timezone.utc
    )


def _digest(payload: dict[str, object]) -> str:
    return hashlib.sha3_512(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalEvidenceLegalHoldConstraint:
    """Immutable legal-hold directive evidence for one provider object version."""

    tenant_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str
    hold_reference: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    imposed_at: datetime
    state: LegalEvidenceLegalHoldState
    released_at: datetime | None = None
    retention_satisfied: bool = False
    orphan_proven: bool = False
    provider_delete_authorized: bool = False
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if (
            self.retention_satisfied is not False
            or self.orphan_proven is not False
            or self.provider_delete_authorized is not False
        ):
            raise LegalEvidenceLegalHoldConstraintError(
                "L10A2R_C4D4B_LATER_AUTHORITY_FORBIDDEN"
            )

        tenant = _tenant(
            self.tenant_id
        )
        provider = _identity(
            "provider_name",
            self.provider_name,
        )
        storage = _identity(
            "storage_reference",
            self.storage_reference,
        )
        version = _identity(
            "object_version_reference",
            self.object_version_reference,
        )
        hold = _identity(
            "hold_reference",
            self.hold_reference,
        )
        source_reference = _identity(
            "source_evidence_reference",
            self.source_evidence_reference,
        )
        source_fingerprint = _sha3(
            "source_evidence_fingerprint",
            self.source_evidence_fingerprint,
        )
        imposed = _utc(
            "imposed_at",
            self.imposed_at,
        )

        try:
            state = LegalEvidenceLegalHoldState(
                self.state
            )
        except (TypeError, ValueError) as error:
            raise LegalEvidenceLegalHoldConstraintError(
                "L10A2R_C4D4B_STATE_INVALID"
            ) from error

        released: datetime | None = None

        if state is LegalEvidenceLegalHoldState.ACTIVE:
            if self.released_at is not None:
                raise LegalEvidenceLegalHoldConstraintError(
                    "L10A2R_C4D4B_ACTIVE_RELEASE_TIME_FORBIDDEN"
                )
        else:
            if self.released_at is None:
                raise LegalEvidenceLegalHoldConstraintError(
                    "L10A2R_C4D4B_RELEASE_TIME_REQUIRED"
                )

            released = _utc(
                "released_at",
                self.released_at,
            )

            if released < imposed:
                raise LegalEvidenceLegalHoldConstraintError(
                    "L10A2R_C4D4B_RELEASE_PRECEDES_HOLD"
                )

        payload: dict[str, object] = {
            "tenant_id": tenant,
            "provider_name": provider,
            "storage_reference": storage,
            "object_version_reference": version,
            "hold_reference": hold,
            "source_evidence_reference": source_reference,
            "source_evidence_fingerprint": source_fingerprint,
            "imposed_at": imposed.isoformat(),
            "state": state.value,
            "released_at": (
                released.isoformat()
                if released is not None
                else None
            ),
            "retention_satisfied": False,
            "orphan_proven": False,
            "provider_delete_authorized": False,
            "constraint_version": VERSION,
        }

        digest = _digest(
            payload
        )

        if self.fingerprint:
            if (
                not isinstance(self.fingerprint, str)
                or _SHA3_RE.fullmatch(self.fingerprint) is None
                or not hmac.compare_digest(
                    self.fingerprint,
                    digest,
                )
            ):
                raise LegalEvidenceLegalHoldConstraintError(
                    "L10A2R_C4D4B_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "provider_name",
            provider,
        )
        object.__setattr__(
            self,
            "storage_reference",
            storage,
        )
        object.__setattr__(
            self,
            "object_version_reference",
            version,
        )
        object.__setattr__(
            self,
            "hold_reference",
            hold,
        )
        object.__setattr__(
            self,
            "source_evidence_reference",
            source_reference,
        )
        object.__setattr__(
            self,
            "source_evidence_fingerprint",
            source_fingerprint,
        )
        object.__setattr__(
            self,
            "imposed_at",
            imposed,
        )
        object.__setattr__(
            self,
            "state",
            state,
        )
        object.__setattr__(
            self,
            "released_at",
            released,
        )
        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )


@dataclass(frozen=True, slots=True)
class LegalEvidenceLegalHoldAssessment:
    """One hold assessment with downstream authority fixed false."""

    constraint: LegalEvidenceLegalHoldConstraint
    assessed_at: datetime
    disposition_blocked: bool
    retention_satisfied: bool = False
    orphan_proven: bool = False
    provider_delete_authorized: bool = False

    def __post_init__(self) -> None:
        if type(self.constraint) is not LegalEvidenceLegalHoldConstraint:
            raise LegalEvidenceLegalHoldConstraintError(
                "L10A2R_C4D4B_CONSTRAINT_REQUIRED"
            )

        at = _utc(
            "assessed_at",
            self.assessed_at,
        )

        if at < self.constraint.imposed_at:
            raise LegalEvidenceLegalHoldConstraintError(
                "L10A2R_C4D4B_ASSESSMENT_PRECEDES_HOLD"
            )

        expected_blocked = (
            self.constraint.state
            is LegalEvidenceLegalHoldState.ACTIVE
            or (
                self.constraint.released_at is not None
                and at < self.constraint.released_at
            )
        )

        if self.disposition_blocked is not expected_blocked:
            raise LegalEvidenceLegalHoldConstraintError(
                "L10A2R_C4D4B_ASSESSMENT_STATE_INVALID"
            )

        if (
            self.retention_satisfied is not False
            or self.orphan_proven is not False
            or self.provider_delete_authorized is not False
        ):
            raise LegalEvidenceLegalHoldConstraintError(
                "L10A2R_C4D4B_LATER_AUTHORITY_FORBIDDEN"
            )

        object.__setattr__(
            self,
            "assessed_at",
            at,
        )


def assess_legal_evidence_legal_hold(
    constraint: LegalEvidenceLegalHoldConstraint,
    *,
    assessed_at: datetime,
) -> LegalEvidenceLegalHoldAssessment:
    """Assess only whether one sourced hold directive blocks disposition."""

    if type(constraint) is not LegalEvidenceLegalHoldConstraint:
        raise LegalEvidenceLegalHoldConstraintError(
            "L10A2R_C4D4B_CONSTRAINT_REQUIRED"
        )

    at = _utc(
        "assessed_at",
        assessed_at,
    )

    if at < constraint.imposed_at:
        raise LegalEvidenceLegalHoldConstraintError(
            "L10A2R_C4D4B_ASSESSMENT_PRECEDES_HOLD"
        )

    blocked = (
        constraint.state
        is LegalEvidenceLegalHoldState.ACTIVE
        or (
            constraint.released_at is not None
            and at < constraint.released_at
        )
    )

    return LegalEvidenceLegalHoldAssessment(
        constraint=constraint,
        assessed_at=at,
        disposition_blocked=blocked,
    )


__all__ = [
    "VERSION",
    "LegalEvidenceLegalHoldAssessment",
    "LegalEvidenceLegalHoldConstraint",
    "LegalEvidenceLegalHoldConstraintError",
    "LegalEvidenceLegalHoldState",
    "assess_legal_evidence_legal_hold",
]


# ARTIFACT: legal_evidence_legal_hold_constraint.py
# VERSION: v1.0.0-L10A2R-C4D4B-LEGAL-EVIDENCE-LEGAL-HOLD-CONSTRAINT
# AUTHORITY BOUNDARY: immutable sourced legal-hold constraint evidence only
# TENANT POSTURE: exact non-global tenant/provider-object/hold/source binding
# FAIL-CLOSED POSTURE: malformed scope, source, chronology, drift, or authority claims reject
# RETENTION POSTURE: no retention satisfaction authority
# ORPHAN POSTURE: hold state never proves orphan status
# DELETION POSTURE: hold release never authorizes provider deletion
# PROVIDER MUTATION POSTURE: none
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
