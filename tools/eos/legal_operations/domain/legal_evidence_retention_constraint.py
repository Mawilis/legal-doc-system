"""WILSY OS Legal Evidence retention constraint domain.

TITLE: Legal Evidence Retention Constraint
VERSION: v1.0.0-L10A2R-C4D4A-LEGAL-EVIDENCE-RETENTION-CONSTRAINT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Bind exact Legal Evidence provider-object identity to immutable,
         externally sourced retention evidence and assess only whether an
         explicit retain-until interval remains active.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_retention_constraint.py
COLLABORATION / OWNERSHIP:
    C4D4A owns pure retention-constraint evidence only. Authoritative source
    selection, durable registry/orchestration, legal-hold governance, orphan
    proof, deletion authorization and provider execution remain separately
    certified later gates. Commercial Legal Evidence capacity policy may state
    capability only and is never legal retention truth.
CERTIFICATION / UPDATE DATE: 2026-09-30
CHANGELOG:
    v1.0.0-L10A2R-C4D4A establishes immutable tenant/provider-object retention
    constraints, explicit-source evidence binding, deterministic SHA3-512
    integrity and caller-supplied-time ACTIVE/ELAPSED temporal assessment
    without statutory-period inference or downstream authority.
COMPLIANCE:
    Governance-aligned evidence primitive only. This module does not interpret,
    select or assert POPIA, Companies Act, LPC, FICA, contractual, court or
    other statutory retention periods.
SECURITY / PRIVACY POSTURE:
    Pure immutable in-process evidence. No credentials, secrets, raw object
    bytes, MongoDB, provider IO, filesystem IO, network state or wall clock.
TENANT BOUNDARY:
    Exact non-global tenant identity is mandatory and fingerprinted together
    with exact provider/storage/object-version and source evidence identity.
AUTHORITY BOUNDARY:
    Retention-constraint evidence and deterministic temporal assessment only.
    No policy selection, legal-hold state, orphan proof, deletion authorization,
    availability, IAM, Court execution or provider mutation authority.
FINANCIAL AUTHORITY BOUNDARY:
    No billing, invoice, charge, payment, execution or settlement truth.
    Kennel EOS remains exclusive financial execution authority.

PURPOSE:
    Bind one exact tenant-scoped Legal Evidence object to immutable externally
    supplied retention-constraint evidence without inventing statutory periods,
    commercial entitlement, legal-hold state, orphan status or deletion authority.

SOURCE POSTURE:
    This domain does not determine which statute, contract, court direction,
    client mandate, policy or other source is legally authoritative. The caller
    must supply one opaque source evidence reference and SHA3-512 fingerprint.
    Later orchestration/registry gates will own admissible source authority.

TIME POSTURE:
    No wall-clock access exists. Evaluation requires one explicit aware datetime.

COMMERCIAL POSTURE:
    LegalEvidenceRetentionClass and legal_hold_available from the commercial
    capacity policy are capability/catalogue facts only and are not accepted as
    retention obligation or hold state here.

FAIL-CLOSED DECLARATION:
    Malformed identity, pseudo/global tenant scope, malformed source evidence,
    naive datetimes, temporal inversion, fingerprint drift and later-authority
    claims reject.
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
    "v1.0.0-L10A2R-C4D4A-LEGAL-EVIDENCE-RETENTION-CONSTRAINT"
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


class LegalEvidenceRetentionConstraintError(ValueError):
    """Stable fail-closed C4D4A retention-constraint error."""


class LegalEvidenceRetentionState(StrEnum):
    """Closed temporal state vocabulary; never deletion authority."""

    ACTIVE = "ACTIVE"
    ELAPSED = "ELAPSED"


def _identity(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or _IDENTITY_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceRetentionConstraintError(
            f"L10A2R_C4D4A_{name.upper()}_INVALID"
        )

    return value


def _tenant(
    value: object,
) -> str:
    tenant = _identity(
        "tenant_id",
        value,
    )

    if tenant.casefold() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceRetentionConstraintError(
            "L10A2R_C4D4A_TENANT_REQUIRED"
        )

    return tenant


def _sha3(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or _SHA3_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceRetentionConstraintError(
            f"L10A2R_C4D4A_{name.upper()}_INVALID"
        )

    return value


def _utc(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceRetentionConstraintError(
            f"L10A2R_C4D4A_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _digest(
    payload: dict[str, object],
) -> str:
    return hashlib.sha3_512(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidenceRetentionConstraint:
    """Immutable exact retention constraint for one provider object version."""

    tenant_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    imposed_at: datetime
    retain_until: datetime
    legal_hold_cleared: bool = False
    orphan_proven: bool = False
    provider_delete_authorized: bool = False
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        if (
            self.legal_hold_cleared is not False
            or self.orphan_proven is not False
            or self.provider_delete_authorized is not False
        ):
            raise LegalEvidenceRetentionConstraintError(
                "L10A2R_C4D4A_LATER_AUTHORITY_FORBIDDEN"
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
        retain_until = _utc(
            "retain_until",
            self.retain_until,
        )

        if retain_until < imposed:
            raise LegalEvidenceRetentionConstraintError(
                "L10A2R_C4D4A_RETENTION_INTERVAL_INVALID"
            )

        payload: dict[str, object] = {
            "tenant_id": tenant,
            "provider_name": provider,
            "storage_reference": storage,
            "object_version_reference": version,
            "source_evidence_reference": source_reference,
            "source_evidence_fingerprint": source_fingerprint,
            "imposed_at": imposed.isoformat(),
            "retain_until": retain_until.isoformat(),
            "legal_hold_cleared": False,
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
                raise LegalEvidenceRetentionConstraintError(
                    "L10A2R_C4D4A_FINGERPRINT_MISMATCH"
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
            "retain_until",
            retain_until,
        )
        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidenceRetentionAssessment:
    """Temporal retention assessment with all later authority fixed false."""

    constraint: LegalEvidenceRetentionConstraint
    assessed_at: datetime
    state: LegalEvidenceRetentionState
    retention_elapsed: bool
    legal_hold_cleared: bool = False
    orphan_proven: bool = False
    provider_delete_authorized: bool = False

    def __post_init__(
        self,
    ) -> None:
        if (
            type(self.constraint)
            is not LegalEvidenceRetentionConstraint
        ):
            raise LegalEvidenceRetentionConstraintError(
                "L10A2R_C4D4A_CONSTRAINT_REQUIRED"
            )

        at = _utc(
            "assessed_at",
            self.assessed_at,
        )

        if at < self.constraint.imposed_at:
            raise LegalEvidenceRetentionConstraintError(
                "L10A2R_C4D4A_ASSESSMENT_PRECEDES_CONSTRAINT"
            )

        expected_elapsed = (
            at >= self.constraint.retain_until
        )
        expected_state = (
            LegalEvidenceRetentionState.ELAPSED
            if expected_elapsed
            else LegalEvidenceRetentionState.ACTIVE
        )

        if (
            self.state is not expected_state
            or self.retention_elapsed is not expected_elapsed
        ):
            raise LegalEvidenceRetentionConstraintError(
                "L10A2R_C4D4A_ASSESSMENT_STATE_INVALID"
            )

        if (
            self.legal_hold_cleared is not False
            or self.orphan_proven is not False
            or self.provider_delete_authorized is not False
        ):
            raise LegalEvidenceRetentionConstraintError(
                "L10A2R_C4D4A_LATER_AUTHORITY_FORBIDDEN"
            )

        object.__setattr__(
            self,
            "assessed_at",
            at,
        )


def assess_legal_evidence_retention(
    constraint: LegalEvidenceRetentionConstraint,
    *,
    assessed_at: datetime,
) -> LegalEvidenceRetentionAssessment:
    """Assess only whether one explicit retention interval remains active."""

    if (
        type(constraint)
        is not LegalEvidenceRetentionConstraint
    ):
        raise LegalEvidenceRetentionConstraintError(
            "L10A2R_C4D4A_CONSTRAINT_REQUIRED"
        )

    at = _utc(
        "assessed_at",
        assessed_at,
    )

    if at < constraint.imposed_at:
        raise LegalEvidenceRetentionConstraintError(
            "L10A2R_C4D4A_ASSESSMENT_PRECEDES_CONSTRAINT"
        )

    elapsed = (
        at >= constraint.retain_until
    )

    return LegalEvidenceRetentionAssessment(
        constraint=constraint,
        assessed_at=at,
        state=(
            LegalEvidenceRetentionState.ELAPSED
            if elapsed
            else LegalEvidenceRetentionState.ACTIVE
        ),
        retention_elapsed=elapsed,
    )


__all__ = [
    "VERSION",
    "LegalEvidenceRetentionAssessment",
    "LegalEvidenceRetentionConstraint",
    "LegalEvidenceRetentionConstraintError",
    "LegalEvidenceRetentionState",
    "assess_legal_evidence_retention",
]


# ARTIFACT: legal_evidence_retention_constraint.py
# VERSION: v1.0.0-L10A2R-C4D4A-LEGAL-EVIDENCE-RETENTION-CONSTRAINT
# AUTHORITY BOUNDARY: immutable retention constraint + temporal assessment only
# TENANT POSTURE: exact non-global tenant/provider-object/source evidence binding
# FAIL-CLOSED POSTURE: malformed scope, time, source evidence, drift, or later-authority claims reject
# SOURCE POSTURE: source evidence supplied; authority selection occurs elsewhere
# COMMERCIAL POSTURE: commercial retention capability is not legal retention truth
# CLOCK POSTURE: explicit caller-supplied aware datetime only
# LEGAL HOLD POSTURE: no hold-state or clearance authority
# ORPHAN POSTURE: retention elapsed is not orphan proof
# DELETION POSTURE: retention elapsed never authorizes deletion
# PROVIDER MUTATION POSTURE: none
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
