"""TITLE: WILSY OS Sheriff Fidelity Fund Certificate Evidence.
VERSION: v1.0.0-SHERIFF-FIDELITY-FUND-CERTIFICATE-EVIDENCE
AUTHORITY: Immutable documentary evidence of Board-issued FFCs only.
EPITOME: Preserve exact Board certificate reference, subject capacity,
    appointment linkage, validity basis, explicit validity window, cancellation
    evidence, source provenance and append-only successor lineage without
    confusing an FFC with Board readiness confirmation or an acting-sheriff
    prescribed-contribution alternative.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/sheriff_fidelity_fund_certificate_evidence.py
COLLABORATION / OWNERSHIP: The South African Board for Sheriffs issues and may
    cancel Fidelity Fund Certificates under sections 30-34; the Minister's
    appointment and Board readiness decisions remain separate. Insurance,
    identity, source authentication and IAM are separate gates.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-FIDELITY-FUND-CERTIFICATE-EVIDENCE
    Adds distinct evidence for section 32(2) calendar-year certificates and
    section 32(3) acting-sheriff fixed-term certificates, including cancellation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Opaque identifiers and SHA3-512 fingerprints only.
TENANT BOUNDARY: Exact tenant, natural-person principal, Sheriff office,
    appointment and certificate provenance.
AUTHORITY BOUNDARY: Documentary certificate evidence only. Does not authenticate
    the Board, prove currentness, replace the acting-sheriff contribution path,
    satisfy professional-indemnity insurance, grant queue/IAM access or authorize
    service or legal execution.
TRANSACTION BOUNDARY: Pure immutable value construction; no I/O or persistence.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import hmac
import json
import re
from typing import Final

from tools.eos.legal_operations.domain.sheriff_appointment_source_evidence import (
    SheriffAppointmentCapacity,
    SheriffSourceObservationState,
    SheriffSourceVerificationMethod,
)


VERSION: Final[str] = "v1.0.0-SHERIFF-FIDELITY-FUND-CERTIFICATE-EVIDENCE"
SCHEMA: Final[str] = "WILSY-SHERIFF-FFC-EVIDENCE/V1"
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/?#=&%-]{0,511}$"
)
_HEX_128: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "root", "*"}
)


class SheriffFfcEvidenceError(ValueError):
    """Reject malformed Fidelity Fund Certificate documentary evidence."""

    def __init__(self, code: str) -> None:
        """Create one stable, content-free validation code."""
        self.code = code
        super().__init__(code)


class SheriffFfcValidityBasis(StrEnum):
    """Keep section 32(2) calendar-year and 32(3) acting fixed-term paths distinct."""

    SECTION_32_2_CALENDAR_YEAR = "SECTION_32_2_CALENDAR_YEAR"
    SECTION_32_3_ACTING_FIXED_TERM = "SECTION_32_3_ACTING_FIXED_TERM"


class SheriffFfcObservedStatus(StrEnum):
    """Record observed certificate state without asserting complete currentness."""

    ISSUED = "ISSUED"
    CANCELLED = "CANCELLED"


def _identifier(name: str, value: object) -> str:
    """Require one canonical bounded opaque identifier."""
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise SheriffFfcEvidenceError(f"SHERIFF_FFC_{name.upper()}_INVALID")
    if name == "tenant_id" and value.casefold() in _FORBIDDEN_TENANTS:
        raise SheriffFfcEvidenceError("SHERIFF_FFC_TENANT_ID_INVALID")
    return value


def _digest(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 fingerprint."""
    if type(value) is not str or _HEX_128.fullmatch(value) is None:
        raise SheriffFfcEvidenceError(f"SHERIFF_FFC_{name.upper()}_INVALID")
    return value


def _instant(name: str, value: object) -> datetime:
    """Require an aware UTC instant with whole-second precision."""
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise SheriffFfcEvidenceError(f"SHERIFF_FFC_{name.upper()}_INVALID")
    normalized = value.astimezone(timezone.utc)
    if normalized != value or normalized.microsecond:
        raise SheriffFfcEvidenceError(f"SHERIFF_FFC_{name.upper()}_NONCANONICAL")
    return normalized


def _add_months(value: datetime, months: int) -> datetime:
    """Add calendar months while clamping month-end dates safely."""
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def _add_year(value: datetime) -> datetime:
    """Add one calendar year while clamping leap-day dates safely."""
    try:
        return value.replace(year=value.year + 1)
    except ValueError:
        return value.replace(year=value.year + 1, day=28)


@dataclass(frozen=True, slots=True)
class SheriffFfcEvidence:
    """One immutable observation of a Board-issued Fidelity Fund Certificate.

    A section 32(2) certificate expires at the end of its stated certificate
    year. A section 32(3) certificate is an acting-sheriff fixed-term instrument
    whose term must be between one calendar month and one calendar year. A
    section 5 acting-sheriff contribution under section 30(1)(c)(ii) is not an
    FFC and must be represented by a separate evidence type.
    """

    tenant_id: str
    certificate_id: str
    revision: int
    subject_principal_id: str
    subject_capacity: SheriffAppointmentCapacity | str
    sheriff_office_id: str
    appointment_evidence_fingerprint: str
    certificate_reference: str
    certificate_fingerprint: str
    issuer_reference: str
    validity_basis: SheriffFfcValidityBasis | str
    issued_at: datetime
    valid_from: datetime
    valid_until: datetime
    observed_status: SheriffFfcObservedStatus | str
    source_uri: str
    source_observation_state: SheriffSourceObservationState | str
    source_verification_method: SheriffSourceVerificationMethod | str
    source_verification_reference: str
    verified_by_principal_id: str
    observed_at: datetime
    certificate_year: int | None = None
    cancelled_at: datetime | None = None
    cancellation_reference: str | None = None
    cancellation_fingerprint: str | None = None
    supersedes_fingerprint: str | None = None
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = field(default="", compare=True)

    def __post_init__(self) -> None:
        """Validate capacity, certificate term, cancellation and provenance."""
        for name in (
            "tenant_id",
            "certificate_id",
            "subject_principal_id",
            "sheriff_office_id",
            "certificate_reference",
            "issuer_reference",
            "source_uri",
            "source_verification_reference",
            "verified_by_principal_id",
        ):
            object.__setattr__(self, name, _identifier(name, getattr(self, name)))
        for name in (
            "appointment_evidence_fingerprint",
            "certificate_fingerprint",
        ):
            object.__setattr__(self, name, _digest(name, getattr(self, name)))
        if type(self.revision) is not int or self.revision < 1:
            raise SheriffFfcEvidenceError("SHERIFF_FFC_REVISION_INVALID")
        if self.subject_principal_id == self.verified_by_principal_id:
            raise SheriffFfcEvidenceError("SHERIFF_FFC_SELF_ATTESTATION_FORBIDDEN")
        try:
            capacity = SheriffAppointmentCapacity(self.subject_capacity)
            basis = SheriffFfcValidityBasis(self.validity_basis)
            status = SheriffFfcObservedStatus(self.observed_status)
            observation = SheriffSourceObservationState(self.source_observation_state)
            method = SheriffSourceVerificationMethod(self.source_verification_method)
        except (TypeError, ValueError) as error:
            raise SheriffFfcEvidenceError("SHERIFF_FFC_ENUM_INVALID") from error
        if capacity not in {
            SheriffAppointmentCapacity.SHERIFF,
            SheriffAppointmentCapacity.ACTING_SHERIFF,
            SheriffAppointmentCapacity.DEPUTY_SHERIFF,
        }:
            raise SheriffFfcEvidenceError("SHERIFF_FFC_CAPACITY_INVALID")
        required_method = {
            SheriffSourceObservationState.HUMAN_OBSERVED_PUBLIC_RECORD:
                SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION,
            SheriffSourceObservationState.ATTESTED_DOCUMENT_REVIEW:
                SheriffSourceVerificationMethod.ATTESTED_DOCUMENT_REVIEW,
            SheriffSourceObservationState.AUTHENTICATED_RESPONSE:
                SheriffSourceVerificationMethod.AUTHENTICATED_REGULATOR_RESPONSE,
        }.get(observation)
        if required_method is not None and method is not required_method:
            raise SheriffFfcEvidenceError("SHERIFF_FFC_SOURCE_METHOD_MISMATCH")
        object.__setattr__(self, "subject_capacity", capacity)
        object.__setattr__(self, "validity_basis", basis)
        object.__setattr__(self, "observed_status", status)
        object.__setattr__(self, "source_observation_state", observation)
        object.__setattr__(self, "source_verification_method", method)

        issued = _instant("issued_at", self.issued_at)
        start = _instant("valid_from", self.valid_from)
        end = _instant("valid_until", self.valid_until)
        observed = _instant("observed_at", self.observed_at)
        if start < issued or end <= start:
            raise SheriffFfcEvidenceError("SHERIFF_FFC_VALIDITY_WINDOW_INVALID")
        object.__setattr__(self, "issued_at", issued)
        object.__setattr__(self, "valid_from", start)
        object.__setattr__(self, "valid_until", end)
        object.__setattr__(self, "observed_at", observed)
        if observed < issued:
            raise SheriffFfcEvidenceError("SHERIFF_FFC_OBSERVATION_CHRONOLOGY_INVALID")

        if basis is SheriffFfcValidityBasis.SECTION_32_2_CALENDAR_YEAR:
            year = self.certificate_year
            if type(year) is not int or year < 1990 or year > 9998:
                raise SheriffFfcEvidenceError("SHERIFF_FFC_CERTIFICATE_YEAR_REQUIRED")
            expected_end = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
            if end != expected_end:
                raise SheriffFfcEvidenceError("SHERIFF_FFC_CALENDAR_YEAR_END_MISMATCH")
            if end.year != year:
                raise SheriffFfcEvidenceError("SHERIFF_FFC_CERTIFICATE_YEAR_MISMATCH")
        else:
            if capacity is not SheriffAppointmentCapacity.ACTING_SHERIFF:
                raise SheriffFfcEvidenceError("SHERIFF_FFC_SECTION_32_3_ACTING_ONLY")
            if self.certificate_year is not None:
                raise SheriffFfcEvidenceError("SHERIFF_FFC_ACTING_YEAR_UNEXPECTED")
            if end < _add_months(start, 1) or end > _add_year(start):
                raise SheriffFfcEvidenceError("SHERIFF_FFC_ACTING_TERM_OUT_OF_RANGE")
        if basis is SheriffFfcValidityBasis.SECTION_32_2_CALENDAR_YEAR and self.certificate_year is None:
            raise SheriffFfcEvidenceError("SHERIFF_FFC_CERTIFICATE_YEAR_REQUIRED")
        if basis is SheriffFfcValidityBasis.SECTION_32_3_ACTING_FIXED_TERM and self.certificate_year is not None:
            raise SheriffFfcEvidenceError("SHERIFF_FFC_ACTING_YEAR_UNEXPECTED")

        cancelled = None if self.cancelled_at is None else _instant("cancelled_at", self.cancelled_at)
        cancel_ref = (
            None if self.cancellation_reference is None
            else _identifier("cancellation_reference", self.cancellation_reference)
        )
        cancel_fp = (
            None if self.cancellation_fingerprint is None
            else _digest("cancellation_fingerprint", self.cancellation_fingerprint)
        )
        if status is SheriffFfcObservedStatus.CANCELLED:
            if cancelled is None or cancel_ref is None or cancel_fp is None:
                raise SheriffFfcEvidenceError("SHERIFF_FFC_CANCELLATION_EVIDENCE_REQUIRED")
            if cancelled < issued or observed < cancelled:
                raise SheriffFfcEvidenceError("SHERIFF_FFC_CANCELLATION_CHRONOLOGY_INVALID")
        elif any(item is not None for item in (cancelled, cancel_ref, cancel_fp)):
            raise SheriffFfcEvidenceError("SHERIFF_FFC_UNEXPECTED_CANCELLATION_EVIDENCE")
        object.__setattr__(self, "cancelled_at", cancelled)
        object.__setattr__(self, "cancellation_reference", cancel_ref)
        object.__setattr__(self, "cancellation_fingerprint", cancel_fp)

        predecessor = (
            None if self.supersedes_fingerprint is None
            else _digest("supersedes_fingerprint", self.supersedes_fingerprint)
        )
        if self.revision == 1 and predecessor is not None:
            raise SheriffFfcEvidenceError("SHERIFF_FFC_ROOT_SUPERSEDES_FORBIDDEN")
        if self.revision > 1 and predecessor is None:
            raise SheriffFfcEvidenceError("SHERIFF_FFC_SUCCESSOR_REQUIRED")
        object.__setattr__(self, "supersedes_fingerprint", predecessor)
        if self.schema != SCHEMA or self.version != VERSION:
            raise SheriffFfcEvidenceError("SHERIFF_FFC_SCHEMA_VERSION_INVALID")
        calculated = self._compute_fingerprint()
        if self.fingerprint:
            supplied = _digest("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, calculated):
                raise SheriffFfcEvidenceError("SHERIFF_FFC_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", calculated)

    def semantic_dict(self) -> dict[str, object]:
        """Return every immutable semantic field without the fingerprint."""
        return {
            "schema": self.schema,
            "version": self.version,
            "tenant_id": self.tenant_id,
            "certificate_id": self.certificate_id,
            "revision": self.revision,
            "subject_principal_id": self.subject_principal_id,
            "subject_capacity": SheriffAppointmentCapacity(self.subject_capacity).value,
            "sheriff_office_id": self.sheriff_office_id,
            "appointment_evidence_fingerprint": self.appointment_evidence_fingerprint,
            "certificate_reference": self.certificate_reference,
            "certificate_fingerprint": self.certificate_fingerprint,
            "issuer_reference": self.issuer_reference,
            "validity_basis": SheriffFfcValidityBasis(self.validity_basis).value,
            "issued_at": self.issued_at.isoformat(),
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat(),
            "observed_status": SheriffFfcObservedStatus(self.observed_status).value,
            "source_uri": self.source_uri,
            "source_observation_state": SheriffSourceObservationState(self.source_observation_state).value,
            "source_verification_method": SheriffSourceVerificationMethod(self.source_verification_method).value,
            "source_verification_reference": self.source_verification_reference,
            "verified_by_principal_id": self.verified_by_principal_id,
            "observed_at": self.observed_at.isoformat(),
            "certificate_year": self.certificate_year,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "cancellation_reference": self.cancellation_reference,
            "cancellation_fingerprint": self.cancellation_fingerprint,
            "supersedes_fingerprint": self.supersedes_fingerprint,
        }

    def _compute_fingerprint(self) -> str:
        """Hash the complete canonical certificate observation."""
        encoded = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return sha3_512(encoded).hexdigest()

    def to_dict(self) -> dict[str, object]:
        """Serialize FFC evidence without implying statutory currentness."""
        return {**self.semantic_dict(), "fingerprint": self.fingerprint}

    @property
    def is_current(self) -> bool:
        """A single observed certificate is not a complete currentness decision."""
        return False

    @property
    def permits_operational_access(self) -> bool:
        """FFC evidence alone never grants Sheriff office or queue access."""
        return False

    @property
    def permits_service_execution(self) -> bool:
        """FFC evidence alone never authorizes legal service or execution."""
        return False


__all__ = [
    "VERSION",
    "SCHEMA",
    "SheriffFfcEvidenceError",
    "SheriffFfcValidityBasis",
    "SheriffFfcObservedStatus",
    "SheriffFfcEvidence",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: sheriff_fidelity_fund_certificate_evidence.py
# VERSION: v1.0.0-SHERIFF-FIDELITY-FUND-CERTIFICATE-EVIDENCE
# AUTHORITY BOUNDARY: Board certificate evidence only; no currentness, insurance or access authority
# TENANT POSTURE: exact tenant, natural-person principal, office, appointment and certificate scope
# FAIL-CLOSED POSTURE: malformed validity, capacity, cancellation or source provenance rejects
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
