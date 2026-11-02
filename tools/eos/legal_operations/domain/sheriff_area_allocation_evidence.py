"""TITLE: WILSY OS Sheriff Statutory Service-Area Allocation Evidence.
VERSION: v1.0.0-SHERIFF-STATUTORY-AREA-ALLOCATION-EVIDENCE
AUTHORITY: Immutable documentary evidence for Sheriffs Act section 3(2) only.
EPITOME: Preserve exact Ministerial area-allocation instrument, Board
    consultation, written Board confirmation of readiness to issue an FFC,
    appointment linkage, court jurisdiction, area-boundary fingerprint,
    effective window and append-only source revision lineage.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/sheriff_area_allocation_evidence.py
COLLABORATION / OWNERSHIP: The Minister owns statutory area allocation under
    section 3(2); the South African Board for Sheriffs owns its consultation
    and written FFC-readiness confirmation; source capture and currentness
    verification are separate gates.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-STATUTORY-AREA-ALLOCATION-EVIDENCE
    Adds a separate immutable evidence contract for section 3(2)(a) area
    allocation and section 3(2)(b) additional-sheriff appointment in an area.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Opaque identifiers and fingerprints only; no
    geometry payload, personal identity document, credential or raw content.
TENANT BOUNDARY: Exact tenant, sheriff principal, office, appointment,
    jurisdiction and service-area references.
AUTHORITY BOUNDARY: Documentary evidence only. Does not authenticate the
    Minister or Board, prove allocation currentness, grant service authority,
    establish FFC/insurance currentness, authorize queue access or activate IAM.
STATUTORY DISTINCTION: Section 6B appointments are excluded because section
    6B(1) expressly excludes service of process and other court documents.
TRANSACTION BOUNDARY: Pure immutable value construction; no I/O or persistence.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import hmac
import json
import re
from typing import Final


VERSION: Final[str] = "v1.0.0-SHERIFF-STATUTORY-AREA-ALLOCATION-EVIDENCE"
SCHEMA: Final[str] = "WILSY-SHERIFF-AREA-ALLOCATION-EVIDENCE/V1"
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/?#=&%-]{0,511}$"
)
_HEX_128: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "root", "*"}
)


class SheriffAreaAllocationEvidenceError(ValueError):
    """Reject malformed area-allocation documentary evidence."""

    def __init__(self, code: str) -> None:
        """Create one stable, content-free validation code."""
        self.code = code
        super().__init__(code)


class SheriffAreaAllocationBasis(StrEnum):
    """Separate the two Ministerial powers in Sheriffs Act section 3(2)."""

    SECTION_3_2_A_AREA_ALLOCATION = "SECTION_3_2_A_AREA_ALLOCATION"
    SECTION_3_2_B_ADDITIONAL_SHERIFF = "SECTION_3_2_B_ADDITIONAL_SHERIFF"


class SheriffAreaAllocationObservationState(StrEnum):
    """Describe observation provenance, never statutory allocation authority."""

    UNVERIFIED_SUBMISSION = "UNVERIFIED_SUBMISSION"
    HUMAN_OBSERVED_PUBLIC_RECORD = "HUMAN_OBSERVED_PUBLIC_RECORD"
    ATTESTED_DOCUMENT_REVIEW = "ATTESTED_DOCUMENT_REVIEW"
    AUTHENTICATED_RESPONSE = "AUTHENTICATED_RESPONSE"
    DISPUTED = "DISPUTED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"


class SheriffAreaAllocationVerificationMethod(StrEnum):
    """Identify the bounded method used to observe the source record."""

    PUBLIC_WEB_OBSERVATION = "PUBLIC_WEB_OBSERVATION"
    ATTESTED_DOCUMENT_REVIEW = "ATTESTED_DOCUMENT_REVIEW"
    AUTHENTICATED_REGULATOR_RESPONSE = "AUTHENTICATED_REGULATOR_RESPONSE"


_REQUIRED_METHOD: Final[dict[
    SheriffAreaAllocationObservationState,
    SheriffAreaAllocationVerificationMethod,
]] = {
    SheriffAreaAllocationObservationState.HUMAN_OBSERVED_PUBLIC_RECORD:
        SheriffAreaAllocationVerificationMethod.PUBLIC_WEB_OBSERVATION,
    SheriffAreaAllocationObservationState.ATTESTED_DOCUMENT_REVIEW:
        SheriffAreaAllocationVerificationMethod.ATTESTED_DOCUMENT_REVIEW,
    SheriffAreaAllocationObservationState.AUTHENTICATED_RESPONSE:
        SheriffAreaAllocationVerificationMethod.AUTHENTICATED_REGULATOR_RESPONSE,
}


def _identifier(name: str, value: object) -> str:
    """Require one canonical, bounded, non-pseudo identifier."""
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise SheriffAreaAllocationEvidenceError(
            f"SHERIFF_AREA_ALLOCATION_{name.upper()}_INVALID"
        )
    if name == "tenant_id" and value.casefold() in _FORBIDDEN_TENANTS:
        raise SheriffAreaAllocationEvidenceError(
            "SHERIFF_AREA_ALLOCATION_TENANT_ID_INVALID"
        )
    return value


def _digest(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 fingerprint."""
    if type(value) is not str or _HEX_128.fullmatch(value) is None:
        raise SheriffAreaAllocationEvidenceError(
            f"SHERIFF_AREA_ALLOCATION_{name.upper()}_INVALID"
        )
    return value


def _instant(name: str, value: object) -> datetime:
    """Require an aware UTC timestamp with whole-second precision."""
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise SheriffAreaAllocationEvidenceError(
            f"SHERIFF_AREA_ALLOCATION_{name.upper()}_INVALID"
        )
    normalized = value.astimezone(timezone.utc)
    if normalized != value or normalized.microsecond:
        raise SheriffAreaAllocationEvidenceError(
            f"SHERIFF_AREA_ALLOCATION_{name.upper()}_NONCANONICAL"
        )
    return normalized


@dataclass(frozen=True, slots=True)
class SheriffAreaAllocationEvidence:
    """One immutable observation of a Ministerial section 3(2) allocation.

    The Ministerial appointment and Board documents are referenced by exact
    fingerprints, not inferred from names or office labels. The Board's
    consultation and its written confirmation that it is prepared to issue an
    FFC are separate required evidence items. For section 3(2)(b), the group
    reference correlates multiple sheriffs appointed for the same area; this
    value represents only one sheriff's allocation record in that group.
    """

    tenant_id: str
    allocation_id: str
    revision: int
    sheriff_principal_id: str
    sheriff_office_id: str
    appointment_evidence_fingerprint: str
    appointed_court_reference: str
    allocated_court_reference: str
    district_id: str
    service_area_reference: str
    service_area_boundary_fingerprint: str
    allocation_basis: SheriffAreaAllocationBasis | str
    ministerial_instrument_reference: str
    ministerial_instrument_fingerprint: str
    board_consultation_reference: str
    board_consultation_fingerprint: str
    board_ffc_readiness_confirmation_reference: str
    board_ffc_readiness_confirmation_fingerprint: str
    source_uri: str
    source_observation_state: SheriffAreaAllocationObservationState | str
    source_verification_method: SheriffAreaAllocationVerificationMethod | str
    source_verification_reference: str
    verified_by_principal_id: str
    observed_at: datetime
    effective_from: datetime
    effective_until: datetime | None
    allocation_group_reference: str | None = None
    supersedes_fingerprint: str | None = None
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = field(default="", compare=True)

    def __post_init__(self) -> None:
        """Validate statutory evidence shape and bind all facts into SHA3-512."""
        for name in (
            "tenant_id",
            "allocation_id",
            "sheriff_principal_id",
            "sheriff_office_id",
            "appointed_court_reference",
            "allocated_court_reference",
            "district_id",
            "service_area_reference",
            "ministerial_instrument_reference",
            "board_consultation_reference",
            "board_ffc_readiness_confirmation_reference",
            "source_uri",
            "source_verification_reference",
            "verified_by_principal_id",
        ):
            object.__setattr__(self, name, _identifier(name, getattr(self, name)))
        for name in (
            "appointment_evidence_fingerprint",
            "service_area_boundary_fingerprint",
            "ministerial_instrument_fingerprint",
            "board_consultation_fingerprint",
            "board_ffc_readiness_confirmation_fingerprint",
        ):
            object.__setattr__(self, name, _digest(name, getattr(self, name)))

        if type(self.revision) is not int or self.revision < 1:
            raise SheriffAreaAllocationEvidenceError(
                "SHERIFF_AREA_ALLOCATION_REVISION_INVALID"
            )
        if self.verified_by_principal_id == self.sheriff_principal_id:
            raise SheriffAreaAllocationEvidenceError(
                "SHERIFF_AREA_ALLOCATION_SELF_ATTESTATION_FORBIDDEN"
            )
        try:
            basis = SheriffAreaAllocationBasis(self.allocation_basis)
            observation = SheriffAreaAllocationObservationState(
                self.source_observation_state
            )
            method = SheriffAreaAllocationVerificationMethod(
                self.source_verification_method
            )
        except (TypeError, ValueError) as error:
            raise SheriffAreaAllocationEvidenceError(
                "SHERIFF_AREA_ALLOCATION_ENUM_INVALID"
            ) from error
        required_method = _REQUIRED_METHOD.get(observation)
        if required_method is not None and method is not required_method:
            raise SheriffAreaAllocationEvidenceError(
                "SHERIFF_AREA_ALLOCATION_OBSERVATION_METHOD_MISMATCH"
            )
        object.__setattr__(self, "allocation_basis", basis)
        object.__setattr__(self, "source_observation_state", observation)
        object.__setattr__(self, "source_verification_method", method)

        observed = _instant("observed_at", self.observed_at)
        start = _instant("effective_from", self.effective_from)
        end = (
            None if self.effective_until is None
            else _instant("effective_until", self.effective_until)
        )
        if end is not None and end <= start:
            raise SheriffAreaAllocationEvidenceError(
                "SHERIFF_AREA_ALLOCATION_EFFECTIVE_WINDOW_INVALID"
            )
        object.__setattr__(self, "observed_at", observed)
        object.__setattr__(self, "effective_from", start)
        object.__setattr__(self, "effective_until", end)

        group = (
            None if self.allocation_group_reference is None
            else _identifier("allocation_group_reference", self.allocation_group_reference)
        )
        if basis is SheriffAreaAllocationBasis.SECTION_3_2_B_ADDITIONAL_SHERIFF:
            if group is None:
                raise SheriffAreaAllocationEvidenceError(
                    "SHERIFF_AREA_ALLOCATION_GROUP_REQUIRED"
                )
        elif group is not None:
            raise SheriffAreaAllocationEvidenceError(
                "SHERIFF_AREA_ALLOCATION_GROUP_UNEXPECTED"
            )
        object.__setattr__(self, "allocation_group_reference", group)

        predecessor = (
            None if self.supersedes_fingerprint is None
            else _digest("supersedes_fingerprint", self.supersedes_fingerprint)
        )
        if self.revision == 1 and predecessor is not None:
            raise SheriffAreaAllocationEvidenceError(
                "SHERIFF_AREA_ALLOCATION_ROOT_SUPERSEDES_FORBIDDEN"
            )
        if self.revision > 1 and predecessor is None:
            raise SheriffAreaAllocationEvidenceError(
                "SHERIFF_AREA_ALLOCATION_SUCCESSOR_REQUIRED"
            )
        object.__setattr__(self, "supersedes_fingerprint", predecessor)

        if self.schema != SCHEMA or self.version != VERSION:
            raise SheriffAreaAllocationEvidenceError(
                "SHERIFF_AREA_ALLOCATION_SCHEMA_VERSION_INVALID"
            )
        calculated = self._compute_fingerprint()
        if self.fingerprint:
            supplied = _digest("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, calculated):
                raise SheriffAreaAllocationEvidenceError(
                    "SHERIFF_AREA_ALLOCATION_FINGERPRINT_MISMATCH"
                )
        object.__setattr__(self, "fingerprint", calculated)

    def semantic_dict(self) -> dict[str, object]:
        """Return every immutable semantic field without the fingerprint."""
        return {
            "schema": self.schema,
            "version": self.version,
            "tenant_id": self.tenant_id,
            "allocation_id": self.allocation_id,
            "revision": self.revision,
            "sheriff_principal_id": self.sheriff_principal_id,
            "sheriff_office_id": self.sheriff_office_id,
            "appointment_evidence_fingerprint": self.appointment_evidence_fingerprint,
            "appointed_court_reference": self.appointed_court_reference,
            "allocated_court_reference": self.allocated_court_reference,
            "district_id": self.district_id,
            "service_area_reference": self.service_area_reference,
            "service_area_boundary_fingerprint": self.service_area_boundary_fingerprint,
            "allocation_basis": SheriffAreaAllocationBasis(self.allocation_basis).value,
            "ministerial_instrument_reference": self.ministerial_instrument_reference,
            "ministerial_instrument_fingerprint": self.ministerial_instrument_fingerprint,
            "board_consultation_reference": self.board_consultation_reference,
            "board_consultation_fingerprint": self.board_consultation_fingerprint,
            "board_ffc_readiness_confirmation_reference": (
                self.board_ffc_readiness_confirmation_reference
            ),
            "board_ffc_readiness_confirmation_fingerprint": (
                self.board_ffc_readiness_confirmation_fingerprint
            ),
            "source_uri": self.source_uri,
            "source_observation_state": SheriffAreaAllocationObservationState(self.source_observation_state).value,
            "source_verification_method": SheriffAreaAllocationVerificationMethod(self.source_verification_method).value,
            "source_verification_reference": self.source_verification_reference,
            "verified_by_principal_id": self.verified_by_principal_id,
            "observed_at": self.observed_at.isoformat(),
            "effective_from": self.effective_from.isoformat(),
            "effective_until": (
                self.effective_until.isoformat() if self.effective_until is not None else None
            ),
            "allocation_group_reference": self.allocation_group_reference,
            "supersedes_fingerprint": self.supersedes_fingerprint,
        }

    def _compute_fingerprint(self) -> str:
        """Hash canonical semantic evidence with SHA3-512."""
        encoded = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return sha3_512(encoded).hexdigest()

    def to_dict(self) -> dict[str, object]:
        """Serialize documentary allocation evidence without authority claims."""
        return {**self.semantic_dict(), "fingerprint": self.fingerprint}

    @property
    def is_statutorily_current(self) -> bool:
        """Area-allocation evidence is not its own currentness or trust decision."""
        return False

    @property
    def permits_operational_access(self) -> bool:
        """An allocation observation never grants Sheriff office/queue access."""
        return False

    @property
    def permits_service_execution(self) -> bool:
        """An allocation observation never authorizes service or legal execution."""
        return False


__all__ = [
    "VERSION",
    "SCHEMA",
    "SheriffAreaAllocationEvidenceError",
    "SheriffAreaAllocationBasis",
    "SheriffAreaAllocationObservationState",
    "SheriffAreaAllocationVerificationMethod",
    "SheriffAreaAllocationEvidence",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: sheriff_area_allocation_evidence.py
# VERSION: v1.0.0-SHERIFF-STATUTORY-AREA-ALLOCATION-EVIDENCE
# AUTHORITY BOUNDARY: section 3(2) documentary evidence only; no statutory currentness or service authority
# TENANT POSTURE: exact tenant, principal, office, appointment, court and service-area provenance
# FAIL-CLOSED POSTURE: missing Board consultation/FFC confirmation, invalid scope, stale or malformed evidence rejects
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
