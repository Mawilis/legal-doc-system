"""TITLE: WILSY OS Sheriff Professional Indemnity Insurance Evidence.
VERSION: v1.0.0-SHERIFF-PROFESSIONAL-INDEMNITY-INSURANCE-EVIDENCE
AUTHORITY: Immutable documentary evidence of Sheriff PI insurance only.
EPITOME: Preserve exact policyholder and covered-principal scope, Sheriff
    office, appointment linkage, insurer/policy provenance, cover and
    deductible amounts, covered-liability fingerprint, Board acceptance and
    minimum-standard fingerprints, validity window, cancellation and successor
    lineage without inferring Board satisfaction from policy existence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/sheriff_professional_indemnity_insurance_evidence.py
COLLABORATION / OWNERSHIP: Sheriffs Act section 30(1)(b) requires professional
    indemnity insurance to the satisfaction of the Board; section 30(2) allows
    the Board to prescribe minimum cover and contingencies. Insurer, Board,
    appointment, FFC, identity, currentness and IAM authorities remain separate.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-PROFESSIONAL-INDEMNITY-INSURANCE-EVIDENCE
    Adds distinct policy evidence linked to the exact Board acceptance and
    Board minimum-standard fingerprints; no hard-coded cover threshold.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Opaque references, fingerprints and integer minor
    units only; no raw identity documents, credentials or policy narratives.
TENANT BOUNDARY: Exact tenant, policyholder, covered natural-person principals,
    Sheriff office, appointment and policy provenance.
AUTHORITY BOUNDARY: Documentary insurance evidence only. Does not authenticate
    the insurer or Board, establish policy currentness or Board satisfaction,
    replace FFC, grant queue/IAM access, or authorize service/legal execution.
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

from tools.eos.legal_operations.domain.sheriff_appointment_source_evidence import (
    SheriffAppointmentCapacity,
    SheriffSourceObservationState,
    SheriffSourceVerificationMethod,
)


VERSION: Final[str] = "v1.0.0-SHERIFF-PROFESSIONAL-INDEMNITY-INSURANCE-EVIDENCE"
SCHEMA: Final[str] = "WILSY-SHERIFF-PI-INSURANCE-EVIDENCE/V1"
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/?#=&%-]{0,511}$"
)
_HEX_128: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_CURRENCY: Final[re.Pattern[str]] = re.compile(r"^[A-Z]{3}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "root", "*"}
)


class SheriffPiInsuranceEvidenceError(ValueError):
    """Reject malformed professional-indemnity insurance evidence."""

    def __init__(self, code: str) -> None:
        """Create one stable, content-free validation code."""
        self.code = code
        super().__init__(code)


class SheriffPiPolicyObservedStatus(StrEnum):
    """Observed policy state; expiry is derived from the explicit validity window."""

    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"


def _identifier(name: str, value: object) -> str:
    """Require one canonical bounded opaque identifier."""
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise SheriffPiInsuranceEvidenceError(
            f"SHERIFF_PI_INSURANCE_{name.upper()}_INVALID"
        )
    if name == "tenant_id" and value.casefold() in _FORBIDDEN_TENANTS:
        raise SheriffPiInsuranceEvidenceError(
            "SHERIFF_PI_INSURANCE_TENANT_ID_INVALID"
        )
    return value


def _digest(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 fingerprint."""
    if type(value) is not str or _HEX_128.fullmatch(value) is None:
        raise SheriffPiInsuranceEvidenceError(
            f"SHERIFF_PI_INSURANCE_{name.upper()}_INVALID"
        )
    return value


def _instant(name: str, value: object) -> datetime:
    """Require an aware UTC instant with whole-second precision."""
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise SheriffPiInsuranceEvidenceError(
            f"SHERIFF_PI_INSURANCE_{name.upper()}_INVALID"
        )
    normalized = value.astimezone(timezone.utc)
    if normalized != value or normalized.microsecond:
        raise SheriffPiInsuranceEvidenceError(
            f"SHERIFF_PI_INSURANCE_{name.upper()}_NONCANONICAL"
        )
    return normalized


@dataclass(frozen=True, slots=True)
class SheriffProfessionalIndemnityInsuranceEvidence:
    """One immutable observation of a Sheriff professional-indemnity policy.

    The Board's satisfaction and applicable minimum cover are represented by
    separate required evidence fingerprints. Policy existence alone is never
    treated as compliance with section 30(1)(b). Coverage amounts use integer
    minor units and an explicit currency code; no threshold is hard-coded.
    """

    tenant_id: str
    policy_evidence_id: str
    revision: int
    policyholder_principal_id: str
    covered_principal_ids: tuple[str, ...]
    covered_capacities: tuple[SheriffAppointmentCapacity | str, ...]
    sheriff_office_id: str
    appointment_evidence_fingerprints: tuple[str, ...]
    insurer_reference: str
    policy_reference: str
    policy_fingerprint: str
    coverage_scope_fingerprint: str
    coverage_amount_minor: int
    deductible_amount_minor: int
    currency_code: str
    board_acceptance_reference: str
    board_acceptance_fingerprint: str
    board_minimum_standard_reference: str
    board_minimum_standard_fingerprint: str
    issued_at: datetime
    valid_from: datetime
    valid_until: datetime
    observed_status: SheriffPiPolicyObservedStatus | str
    source_uri: str
    source_observation_state: SheriffSourceObservationState | str
    source_verification_method: SheriffSourceVerificationMethod | str
    source_verification_reference: str
    verified_by_principal_id: str
    observed_at: datetime
    cancelled_at: datetime | None = None
    cancellation_reference: str | None = None
    cancellation_fingerprint: str | None = None
    supersedes_fingerprint: str | None = None
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = field(default="", compare=True)

    def __post_init__(self) -> None:
        """Validate exact coverage scope, Board evidence and policy chronology."""
        for name in (
            "tenant_id",
            "policy_evidence_id",
            "policyholder_principal_id",
            "sheriff_office_id",
            "insurer_reference",
            "policy_reference",
            "board_acceptance_reference",
            "board_minimum_standard_reference",
            "source_uri",
            "source_verification_reference",
            "verified_by_principal_id",
        ):
            object.__setattr__(self, name, _identifier(name, getattr(self, name)))
        for name in (
            "policy_fingerprint",
            "coverage_scope_fingerprint",
            "board_acceptance_fingerprint",
            "board_minimum_standard_fingerprint",
        ):
            object.__setattr__(self, name, _digest(name, getattr(self, name)))
        if type(self.revision) is not int or self.revision < 1:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_REVISION_INVALID"
            )
        if self.policyholder_principal_id == self.verified_by_principal_id:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_SELF_ATTESTATION_FORBIDDEN"
            )
        if type(self.coverage_amount_minor) is not int or self.coverage_amount_minor <= 0:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_COVERAGE_AMOUNT_INVALID"
            )
        if type(self.deductible_amount_minor) is not int or self.deductible_amount_minor < 0:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_DEDUCTIBLE_INVALID"
            )
        if type(self.currency_code) is not str or _CURRENCY.fullmatch(self.currency_code) is None:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_CURRENCY_INVALID"
            )
        if type(self.covered_principal_ids) is not tuple or not self.covered_principal_ids:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_COVERED_PRINCIPALS_REQUIRED"
            )
        covered = tuple(
            _identifier("covered_principal_id", item)
            for item in self.covered_principal_ids
        )
        if len(set(covered)) != len(covered) or self.policyholder_principal_id not in covered:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_COVERED_PRINCIPAL_SCOPE_INVALID"
            )
        object.__setattr__(self, "covered_principal_ids", covered)
        if (
            type(self.appointment_evidence_fingerprints) is not tuple
            or len(self.appointment_evidence_fingerprints) != len(covered)
        ):
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_APPOINTMENT_FINGERPRINT_SCOPE_INVALID"
            )
        appointment_fingerprints = tuple(
            _digest("appointment_evidence_fingerprint", item)
            for item in self.appointment_evidence_fingerprints
        )
        object.__setattr__(
            self, "appointment_evidence_fingerprints", appointment_fingerprints
        )
        if type(self.covered_capacities) is not tuple or not self.covered_capacities:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_COVERED_CAPACITIES_REQUIRED"
            )
        try:
            capacities = tuple(
                SheriffAppointmentCapacity(item) for item in self.covered_capacities
            )
        except (TypeError, ValueError) as error:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_COVERED_CAPACITY_INVALID"
            ) from error
        allowed_capacities = {
            SheriffAppointmentCapacity.SHERIFF,
            SheriffAppointmentCapacity.ACTING_SHERIFF,
            SheriffAppointmentCapacity.DEPUTY_SHERIFF,
        }
        if not set(capacities).issubset(allowed_capacities):
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_COVERED_CAPACITY_INVALID"
            )
        object.__setattr__(self, "covered_capacities", capacities)
        if len(covered) != len(capacities):
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_PRINCIPAL_CAPACITY_CARDINALITY_MISMATCH"
            )

        try:
            status = SheriffPiPolicyObservedStatus(self.observed_status)
            observation = SheriffSourceObservationState(self.source_observation_state)
            method = SheriffSourceVerificationMethod(self.source_verification_method)
        except (TypeError, ValueError) as error:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_SOURCE_ENUM_INVALID"
            ) from error
        required_method = {
            SheriffSourceObservationState.HUMAN_OBSERVED_PUBLIC_RECORD:
                SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION,
            SheriffSourceObservationState.ATTESTED_DOCUMENT_REVIEW:
                SheriffSourceVerificationMethod.ATTESTED_DOCUMENT_REVIEW,
            SheriffSourceObservationState.AUTHENTICATED_RESPONSE:
                SheriffSourceVerificationMethod.AUTHENTICATED_REGULATOR_RESPONSE,
        }.get(observation)
        if required_method is not None and method is not required_method:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_SOURCE_METHOD_MISMATCH"
            )
        object.__setattr__(self, "observed_status", status)
        object.__setattr__(self, "source_observation_state", observation)
        object.__setattr__(self, "source_verification_method", method)

        issued = _instant("issued_at", self.issued_at)
        start = _instant("valid_from", self.valid_from)
        end = _instant("valid_until", self.valid_until)
        observed = _instant("observed_at", self.observed_at)
        if end <= start or observed < issued:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_VALIDITY_OR_OBSERVATION_CHRONOLOGY_INVALID"
            )
        object.__setattr__(self, "issued_at", issued)
        object.__setattr__(self, "valid_from", start)
        object.__setattr__(self, "valid_until", end)
        object.__setattr__(self, "observed_at", observed)

        cancelled = None if self.cancelled_at is None else _instant("cancelled_at", self.cancelled_at)
        cancel_ref = (
            None if self.cancellation_reference is None
            else _identifier("cancellation_reference", self.cancellation_reference)
        )
        cancel_fp = (
            None if self.cancellation_fingerprint is None
            else _digest("cancellation_fingerprint", self.cancellation_fingerprint)
        )
        if status is SheriffPiPolicyObservedStatus.CANCELLED:
            if cancelled is None or cancel_ref is None or cancel_fp is None:
                raise SheriffPiInsuranceEvidenceError(
                    "SHERIFF_PI_INSURANCE_CANCELLATION_EVIDENCE_REQUIRED"
                )
            if cancelled < issued or observed < cancelled:
                raise SheriffPiInsuranceEvidenceError(
                    "SHERIFF_PI_INSURANCE_CANCELLATION_CHRONOLOGY_INVALID"
                )
        elif any(item is not None for item in (cancelled, cancel_ref, cancel_fp)):
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_UNEXPECTED_CANCELLATION_EVIDENCE"
            )
        object.__setattr__(self, "cancelled_at", cancelled)
        object.__setattr__(self, "cancellation_reference", cancel_ref)
        object.__setattr__(self, "cancellation_fingerprint", cancel_fp)

        predecessor = (
            None if self.supersedes_fingerprint is None
            else _digest("supersedes_fingerprint", self.supersedes_fingerprint)
        )
        if self.revision == 1 and predecessor is not None:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_ROOT_SUPERSEDES_FORBIDDEN"
            )
        if self.revision > 1 and predecessor is None:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_SUCCESSOR_REQUIRED"
            )
        object.__setattr__(self, "supersedes_fingerprint", predecessor)
        if self.schema != SCHEMA or self.version != VERSION:
            raise SheriffPiInsuranceEvidenceError(
                "SHERIFF_PI_INSURANCE_SCHEMA_VERSION_INVALID"
            )
        calculated = self._compute_fingerprint()
        if self.fingerprint:
            supplied = _digest("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, calculated):
                raise SheriffPiInsuranceEvidenceError(
                    "SHERIFF_PI_INSURANCE_FINGERPRINT_MISMATCH"
                )
        object.__setattr__(self, "fingerprint", calculated)

    def semantic_dict(self) -> dict[str, object]:
        """Return all immutable semantic fields without the computed fingerprint."""
        return {
            "schema": self.schema,
            "version": self.version,
            "tenant_id": self.tenant_id,
            "policy_evidence_id": self.policy_evidence_id,
            "revision": self.revision,
            "policyholder_principal_id": self.policyholder_principal_id,
            "covered_principal_ids": list(self.covered_principal_ids),
            "covered_capacities": [
                SheriffAppointmentCapacity(item).value for item in self.covered_capacities
            ],
            "sheriff_office_id": self.sheriff_office_id,
            "appointment_evidence_fingerprints": list(self.appointment_evidence_fingerprints),
            "insurer_reference": self.insurer_reference,
            "policy_reference": self.policy_reference,
            "policy_fingerprint": self.policy_fingerprint,
            "coverage_scope_fingerprint": self.coverage_scope_fingerprint,
            "coverage_amount_minor": self.coverage_amount_minor,
            "deductible_amount_minor": self.deductible_amount_minor,
            "currency_code": self.currency_code,
            "board_acceptance_reference": self.board_acceptance_reference,
            "board_acceptance_fingerprint": self.board_acceptance_fingerprint,
            "board_minimum_standard_reference": self.board_minimum_standard_reference,
            "board_minimum_standard_fingerprint": self.board_minimum_standard_fingerprint,
            "issued_at": self.issued_at.isoformat(),
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat(),
            "observed_status": SheriffPiPolicyObservedStatus(self.observed_status).value,
            "source_uri": self.source_uri,
            "source_observation_state": SheriffSourceObservationState(self.source_observation_state).value,
            "source_verification_method": SheriffSourceVerificationMethod(self.source_verification_method).value,
            "source_verification_reference": self.source_verification_reference,
            "verified_by_principal_id": self.verified_by_principal_id,
            "observed_at": self.observed_at.isoformat(),
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "cancellation_reference": self.cancellation_reference,
            "cancellation_fingerprint": self.cancellation_fingerprint,
            "supersedes_fingerprint": self.supersedes_fingerprint,
        }

    def _compute_fingerprint(self) -> str:
        """Hash the complete canonical policy and Board evidence scope."""
        encoded = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return sha3_512(encoded).hexdigest()

    def to_dict(self) -> dict[str, object]:
        """Serialize documentary policy evidence without implying currentness."""
        return {**self.semantic_dict(), "fingerprint": self.fingerprint}

    @property
    def is_current(self) -> bool:
        """Policy evidence is not a complete currentness or Board-satisfaction decision."""
        return False

    @property
    def permits_operational_access(self) -> bool:
        """Insurance evidence alone never grants office or queue access."""
        return False

    @property
    def permits_service_execution(self) -> bool:
        """Insurance evidence alone never authorizes service or execution."""
        return False


__all__ = [
    "VERSION",
    "SCHEMA",
    "SheriffPiInsuranceEvidenceError",
    "SheriffPiPolicyObservedStatus",
    "SheriffProfessionalIndemnityInsuranceEvidence",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: sheriff_professional_indemnity_insurance_evidence.py
# VERSION: v1.0.0-SHERIFF-PROFESSIONAL-INDEMNITY-INSURANCE-EVIDENCE
# AUTHORITY BOUNDARY: policy evidence only; no insurer authentication, Board satisfaction, currentness or access
# TENANT POSTURE: exact tenant, policyholder, covered principals, office, appointment and policy scope
# FAIL-CLOSED POSTURE: missing Board evidence, malformed coverage scope, stale or cancelled policy denies
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
