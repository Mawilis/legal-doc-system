"""TITLE: WILSY OS Sheriff Appointment Source Evidence
VERSION: v1.0.0-SHERIFF-APPOINTMENT-SOURCE-EVIDENCE
AUTHORITY: Immutable source-observation evidence only; no statutory appointment or operational authority.
EPITOME: Preserve verified provenance and exact statutory scope for a Sheriff,
    acting Sheriff, Deputy Sheriff, section 6A designee, or section 6B
    cross-area function appointment without manufacturing legal authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/sheriff_appointment_source_evidence.py
COLLABORATION / OWNERSHIP: Legal Operations owns the immutable observation
    contract; the Minister and South African Board for Sheriffs remain the
    relevant external statutory authorities; IAM remains independently owned.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-APPOINTMENT-SOURCE-EVIDENCE
    Introduces typed statutory-capacity evidence, scope, instrument provenance,
    effective dates and mandatory supporting evidence for special appointment
    paths. No persistence, verification trust root or authorization is added.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Opaque identifiers and SHA3-512 fingerprints only;
    no names, identity numbers, raw appointment documents or narrative content.
TENANT BOUNDARY: Exact non-pseudo tenant; no cross-tenant composition.
AUTHORITY BOUNDARY: Observation evidence only. This value is not an appointment,
    Fidelity Fund Certificate, Board approval, IAM grant, office access grant,
    service assignment, professional status or execution authority.
TRANSACTION BOUNDARY: Pure immutable value object; no persistence or transaction.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import hmac
import json
import re
from typing import Final, Mapping, NoReturn, cast


VERSION: Final[str] = "v1.0.0-SHERIFF-APPOINTMENT-SOURCE-EVIDENCE"
SCHEMA: Final[str] = "WILSY-SHERIFF-APPOINTMENT-SOURCE-EVIDENCE/V1"
_HEX_128: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{128}\Z")
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/?#=&%-]{0,511}\Z")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({"default", "global", "root", "*"})


class SheriffAppointmentSourceEvidenceError(ValueError):
    """Expose one stable, content-free source-evidence validation failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class SheriffAppointmentCapacity(StrEnum):
    """Represent distinct statutory capacities without collapsing them into IAM."""

    SHERIFF = "SHERIFF"
    ACTING_SHERIFF = "ACTING_SHERIFF"
    DEPUTY_SHERIFF = "DEPUTY_SHERIFF"
    SECTION_6A_DESIGNEE = "SECTION_6A_DESIGNEE"
    SECTION_6B_FUNCTION_APPOINTMENT = "SECTION_6B_FUNCTION_APPOINTMENT"


class SheriffAppointmentStatutoryBasis(StrEnum):
    """Identify the specific Sheriffs Act appointment/designation provision."""

    SECTION_2_1 = "SHERIFFS_ACT_90_OF_1986_S2_1"
    SECTION_2_3 = "SHERIFFS_ACT_90_OF_1986_S2_3"
    SECTION_5_1 = "SHERIFFS_ACT_90_OF_1986_S5_1"
    SECTION_5_1A = "SHERIFFS_ACT_90_OF_1986_S5_1A"
    SECTION_6_1 = "SHERIFFS_ACT_90_OF_1986_S6_1"
    SECTION_6A_1 = "SHERIFFS_ACT_90_OF_1986_S6A_1"
    SECTION_6B_1 = "SHERIFFS_ACT_90_OF_1986_S6B_1"


class SheriffAppointmentIssuerAuthority(StrEnum):
    """Identify the asserted statutory issuer, not an IAM role."""

    MINISTER = "MINISTER"
    SHERIFF = "SHERIFF"
    ACTING_SHERIFF = "ACTING_SHERIFF"


class SheriffSourceObservationState(StrEnum):
    """Classify provenance strength without treating observation as authority."""

    UNVERIFIED_SUBMISSION = "UNVERIFIED_SUBMISSION"
    HUMAN_OBSERVED_PUBLIC_RECORD = "HUMAN_OBSERVED_PUBLIC_RECORD"
    ATTESTED_DOCUMENT_REVIEW = "ATTESTED_DOCUMENT_REVIEW"
    AUTHENTICATED_RESPONSE = "AUTHENTICATED_RESPONSE"
    DISPUTED = "DISPUTED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"


class SheriffSourceVerificationMethod(StrEnum):
    """Describe how source material was observed or authenticated."""

    PUBLIC_WEB_OBSERVATION = "PUBLIC_WEB_OBSERVATION"
    ATTESTED_DOCUMENT_REVIEW = "ATTESTED_DOCUMENT_REVIEW"
    AUTHENTICATED_REGULATOR_RESPONSE = "AUTHENTICATED_REGULATOR_RESPONSE"


_CAPACITY_BASES: Final[dict[SheriffAppointmentCapacity, frozenset[SheriffAppointmentStatutoryBasis]]] = {
    SheriffAppointmentCapacity.SHERIFF: frozenset({
        SheriffAppointmentStatutoryBasis.SECTION_2_1,
        SheriffAppointmentStatutoryBasis.SECTION_2_3,
    }),
    SheriffAppointmentCapacity.ACTING_SHERIFF: frozenset({
        SheriffAppointmentStatutoryBasis.SECTION_5_1,
        SheriffAppointmentStatutoryBasis.SECTION_5_1A,
    }),
    SheriffAppointmentCapacity.DEPUTY_SHERIFF: frozenset({
        SheriffAppointmentStatutoryBasis.SECTION_6_1,
    }),
    SheriffAppointmentCapacity.SECTION_6A_DESIGNEE: frozenset({
        SheriffAppointmentStatutoryBasis.SECTION_6A_1,
    }),
    SheriffAppointmentCapacity.SECTION_6B_FUNCTION_APPOINTMENT: frozenset({
        SheriffAppointmentStatutoryBasis.SECTION_6B_1,
    }),
}


def _fail(code: str) -> NoReturn:
    raise SheriffAppointmentSourceEvidenceError(code)


def _identifier(name: str, value: object) -> str:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        _fail(f"SHERIFF_SOURCE_{name.upper()}_INVALID")
    if name == "tenant_id" and value.casefold() in _FORBIDDEN_TENANTS:
        _fail("SHERIFF_SOURCE_TENANT_ID_INVALID")
    return value


def _digest(name: str, value: object) -> str:
    if type(value) is not str or _HEX_128.fullmatch(value) is None:
        _fail(f"SHERIFF_SOURCE_{name.upper()}_INVALID")
    return value


def _instant(name: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        _fail(f"SHERIFF_SOURCE_{name.upper()}_INVALID")
    result = value.astimezone(timezone.utc)
    if result.microsecond:
        _fail(f"SHERIFF_SOURCE_{name.upper()}_NONCANONICAL")
    return result


def _references(name: str, value: object) -> tuple[str, ...]:
    if type(value) not in (tuple, list):
        _fail(f"SHERIFF_SOURCE_{name.upper()}_INVALID")
    normalized = tuple(_identifier(name, item) for item in cast(tuple[object, ...] | list[object], value))
    if not normalized or len(set(normalized)) != len(normalized):
        _fail(f"SHERIFF_SOURCE_{name.upper()}_INVALID")
    return tuple(sorted(normalized))


@dataclass(frozen=True, slots=True)
class SheriffAppointmentSourceEvidence:
    """Preserve one immutable, tenant-scoped observation of a statutory instrument.

    This record is deliberately documentary. Its source-observation state does
    not authenticate the issuer or make an appointment legally effective.
    Separate verifier trust, current Fidelity Fund Certificate/insurance
    evidence, IAM and office-scoped authorization gates remain mandatory.
    """

    tenant_id: str
    evidence_id: str
    revision: int
    principal_id: str
    verified_subject_reference: str
    sheriff_office_id: str
    district_id: str
    court_reference: str
    service_area_references: tuple[str, ...]
    capacity: SheriffAppointmentCapacity
    statutory_basis: SheriffAppointmentStatutoryBasis
    issuer_authority: SheriffAppointmentIssuerAuthority
    instrument_reference: str
    instrument_fingerprint: str
    source_uri: str
    source_observation_state: SheriffSourceObservationState
    source_verification_method: SheriffSourceVerificationMethod
    source_verification_reference: str
    verified_by_principal_id: str
    observed_at: datetime
    effective_from: datetime
    effective_until: datetime | None
    appointing_principal_id: str | None = None
    board_approval_reference: str | None = None
    board_approval_fingerprint: str | None = None
    board_confirmation_reference: str | None = None
    board_confirmation_fingerprint: str | None = None
    board_consultation_reference: str | None = None
    board_consultation_fingerprint: str | None = None
    conditions_fingerprint: str | None = None
    supersedes_fingerprint: str | None = None
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact statutory shape and canonicalize immutable source facts."""
        for name in (
            "tenant_id",
            "evidence_id",
            "principal_id",
            "verified_subject_reference",
            "sheriff_office_id",
            "district_id",
            "court_reference",
            "instrument_reference",
            "source_uri",
            "source_verification_reference",
            "verified_by_principal_id",
        ):
            object.__setattr__(self, name, _identifier(name, getattr(self, name)))

        if type(self.revision) is not int or self.revision < 1:
            _fail("SHERIFF_SOURCE_REVISION_INVALID")

        try:
            capacity = SheriffAppointmentCapacity(self.capacity)
            basis = SheriffAppointmentStatutoryBasis(self.statutory_basis)
            issuer = SheriffAppointmentIssuerAuthority(self.issuer_authority)
            observation = SheriffSourceObservationState(self.source_observation_state)
            method = SheriffSourceVerificationMethod(self.source_verification_method)
        except (TypeError, ValueError) as error:
            raise SheriffAppointmentSourceEvidenceError(
                "SHERIFF_SOURCE_ENUM_INVALID"
            ) from error

        if basis not in _CAPACITY_BASES[capacity]:
            _fail("SHERIFF_SOURCE_CAPACITY_BASIS_MISMATCH")

        expected_issuer = {
            SheriffAppointmentCapacity.SHERIFF: SheriffAppointmentIssuerAuthority.MINISTER,
            SheriffAppointmentCapacity.ACTING_SHERIFF: SheriffAppointmentIssuerAuthority.MINISTER,
            SheriffAppointmentCapacity.DEPUTY_SHERIFF: None,
            SheriffAppointmentCapacity.SECTION_6A_DESIGNEE: SheriffAppointmentIssuerAuthority.MINISTER,
            SheriffAppointmentCapacity.SECTION_6B_FUNCTION_APPOINTMENT: SheriffAppointmentIssuerAuthority.MINISTER,
        }[capacity]
        if expected_issuer is not None and issuer is not expected_issuer:
            _fail("SHERIFF_SOURCE_ISSUER_CAPACITY_MISMATCH")
        if capacity is SheriffAppointmentCapacity.DEPUTY_SHERIFF and issuer not in {
            SheriffAppointmentIssuerAuthority.SHERIFF,
            SheriffAppointmentIssuerAuthority.ACTING_SHERIFF,
        }:
            _fail("SHERIFF_SOURCE_DEPUTY_ISSUER_INVALID")

        areas = _references("service_area_reference", self.service_area_references)
        observed = _instant("observed_at", self.observed_at)
        effective_from = _instant("effective_from", self.effective_from)
        effective_until = (
            None if self.effective_until is None
            else _instant("effective_until", self.effective_until)
        )
        if effective_until is not None and effective_until <= effective_from:
            _fail("SHERIFF_SOURCE_EFFECTIVE_WINDOW_INVALID")
        # Future-dated appointments may be observed before commencement; the
        # currentness projection, not this immutable observation, decides use.

        appointing = (
            None if self.appointing_principal_id is None
            else _identifier("appointing_principal_id", self.appointing_principal_id)
        )
        approval_ref = (
            None if self.board_approval_reference is None
            else _identifier("board_approval_reference", self.board_approval_reference)
        )
        approval_fp = (
            None if self.board_approval_fingerprint is None
            else _digest("board_approval_fingerprint", self.board_approval_fingerprint)
        )
        confirmation_ref = (
            None if self.board_confirmation_reference is None
            else _identifier("board_confirmation_reference", self.board_confirmation_reference)
        )
        confirmation_fp = (
            None if self.board_confirmation_fingerprint is None
            else _digest("board_confirmation_fingerprint", self.board_confirmation_fingerprint)
        )
        consultation_ref = (
            None if self.board_consultation_reference is None
            else _identifier("board_consultation_reference", self.board_consultation_reference)
        )
        consultation_fp = (
            None if self.board_consultation_fingerprint is None
            else _digest("board_consultation_fingerprint", self.board_consultation_fingerprint)
        )

        if capacity is SheriffAppointmentCapacity.DEPUTY_SHERIFF:
            if appointing is None or approval_ref is None or approval_fp is None:
                _fail("SHERIFF_SOURCE_DEPUTY_BOARD_APPROVAL_REQUIRED")
        else:
            if appointing is not None:
                _fail("SHERIFF_SOURCE_APPOINTING_PRINCIPAL_FORBIDDEN")
            if approval_ref is not None or approval_fp is not None:
                _fail("SHERIFF_SOURCE_BOARD_APPROVAL_UNEXPECTED")

        if basis is SheriffAppointmentStatutoryBasis.SECTION_2_3:
            if confirmation_ref is None or confirmation_fp is None:
                _fail("SHERIFF_SOURCE_SECTION_2_3_BOARD_CONFIRMATION_REQUIRED")
        if basis is SheriffAppointmentStatutoryBasis.SECTION_5_1:
            if confirmation_ref is None or confirmation_fp is None:
                _fail("SHERIFF_SOURCE_SECTION_5_1_BOARD_CONFIRMATION_REQUIRED")
        if basis is SheriffAppointmentStatutoryBasis.SECTION_6B_1:
            if consultation_ref is None or consultation_fp is None:
                _fail("SHERIFF_SOURCE_SECTION_6B_BOARD_CONSULTATION_REQUIRED")
        if (confirmation_ref is None) != (confirmation_fp is None):
            _fail("SHERIFF_SOURCE_BOARD_CONFIRMATION_PAIR_INVALID")
        if (consultation_ref is None) != (consultation_fp is None):
            _fail("SHERIFF_SOURCE_BOARD_CONSULTATION_PAIR_INVALID")
        if basis in {
            SheriffAppointmentStatutoryBasis.SECTION_2_3,
            SheriffAppointmentStatutoryBasis.SECTION_5_1,
        } and (confirmation_ref is None or confirmation_fp is None):
            _fail("SHERIFF_SOURCE_BOARD_CONFIRMATION_REQUIRED")
        if basis not in {
            SheriffAppointmentStatutoryBasis.SECTION_2_3,
            SheriffAppointmentStatutoryBasis.SECTION_5_1,
        } and any((confirmation_ref, confirmation_fp)):
            _fail("SHERIFF_SOURCE_BOARD_CONFIRMATION_UNEXPECTED")
        if basis is not SheriffAppointmentStatutoryBasis.SECTION_6B_1 and any((consultation_ref, consultation_fp)):
            _fail("SHERIFF_SOURCE_BOARD_CONSULTATION_UNEXPECTED")

        conditions_fp = (
            None if self.conditions_fingerprint is None
            else _digest("conditions_fingerprint", self.conditions_fingerprint)
        )
        predecessor = (
            None if self.supersedes_fingerprint is None
            else _digest("supersedes_fingerprint", self.supersedes_fingerprint)
        )
        if self.revision == 1 and predecessor is not None:
            _fail("SHERIFF_SOURCE_ROOT_SUPERSEDES_FORBIDDEN")
        if self.revision > 1 and predecessor is None:
            _fail("SHERIFF_SOURCE_SUCCESSOR_REQUIRED")
        if self.schema != SCHEMA or self.version != VERSION:
            _fail("SHERIFF_SOURCE_SCHEMA_VERSION_INVALID")

        object.__setattr__(self, "capacity", capacity)
        object.__setattr__(self, "statutory_basis", basis)
        object.__setattr__(self, "issuer_authority", issuer)
        object.__setattr__(self, "source_observation_state", observation)
        object.__setattr__(self, "source_verification_method", method)
        object.__setattr__(self, "service_area_references", areas)
        object.__setattr__(self, "observed_at", observed)
        object.__setattr__(self, "effective_from", effective_from)
        object.__setattr__(self, "effective_until", effective_until)
        object.__setattr__(self, "appointing_principal_id", appointing)
        object.__setattr__(self, "board_approval_reference", approval_ref)
        object.__setattr__(self, "board_approval_fingerprint", approval_fp)
        object.__setattr__(self, "board_confirmation_reference", confirmation_ref)
        object.__setattr__(self, "board_confirmation_fingerprint", confirmation_fp)
        object.__setattr__(self, "board_consultation_reference", consultation_ref)
        object.__setattr__(self, "board_consultation_fingerprint", consultation_fp)
        object.__setattr__(self, "conditions_fingerprint", conditions_fp)
        object.__setattr__(self, "supersedes_fingerprint", predecessor)

        computed = self._compute_fingerprint()
        if self.fingerprint:
            supplied = _digest("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, computed):
                _fail("SHERIFF_SOURCE_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", computed)

    def semantic_dict(self) -> dict[str, object]:
        """Return the exact deterministic semantic source-evidence payload."""
        return {
            "schema": self.schema,
            "version": self.version,
            "tenant_id": self.tenant_id,
            "evidence_id": self.evidence_id,
            "revision": self.revision,
            "principal_id": self.principal_id,
            "verified_subject_reference": self.verified_subject_reference,
            "sheriff_office_id": self.sheriff_office_id,
            "district_id": self.district_id,
            "court_reference": self.court_reference,
            "service_area_references": list(self.service_area_references),
            "capacity": self.capacity.value,
            "statutory_basis": self.statutory_basis.value,
            "issuer_authority": self.issuer_authority.value,
            "instrument_reference": self.instrument_reference,
            "instrument_fingerprint": self.instrument_fingerprint,
            "source_uri": self.source_uri,
            "source_observation_state": self.source_observation_state.value,
            "source_verification_method": self.source_verification_method.value,
            "source_verification_reference": self.source_verification_reference,
            "verified_by_principal_id": self.verified_by_principal_id,
            "observed_at": self.observed_at.isoformat(),
            "effective_from": self.effective_from.isoformat(),
            "effective_until": (
                self.effective_until.isoformat() if self.effective_until is not None else None
            ),
            "appointing_principal_id": self.appointing_principal_id,
            "board_approval_reference": self.board_approval_reference,
            "board_approval_fingerprint": self.board_approval_fingerprint,
            "board_confirmation_reference": self.board_confirmation_reference,
            "board_confirmation_fingerprint": self.board_confirmation_fingerprint,
            "board_consultation_reference": self.board_consultation_reference,
            "board_consultation_fingerprint": self.board_consultation_fingerprint,
            "conditions_fingerprint": self.conditions_fingerprint,
            "supersedes_fingerprint": self.supersedes_fingerprint,
        }

    def _compute_fingerprint(self) -> str:
        raw = json.dumps(
            self.semantic_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        return sha3_512(raw).hexdigest()

    def to_dict(self) -> dict[str, object]:
        """Serialize immutable source evidence without granting legal authority."""
        return {**self.semantic_dict(), "fingerprint": self.fingerprint}

    @property
    def permits_operational_access(self) -> bool:
        """Source evidence never authorizes access to a Sheriff office or queue."""
        return False

    @property
    def permits_legal_execution(self) -> bool:
        """Source evidence never authorizes service, execution or a legal act."""
        return False

    @property
    def is_authenticated_appointment(self) -> bool:
        """A source observation is never promoted to an authenticated appointment."""
        return False


__all__ = [
    "SCHEMA",
    "VERSION",
    "SheriffAppointmentCapacity",
    "SheriffAppointmentIssuerAuthority",
    "SheriffAppointmentSourceEvidence",
    "SheriffAppointmentSourceEvidenceError",
    "SheriffAppointmentStatutoryBasis",
    "SheriffSourceObservationState",
    "SheriffSourceVerificationMethod",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: tools/eos/legal_operations/domain/sheriff_appointment_source_evidence.py
# VERSION: v1.0.0-SHERIFF-APPOINTMENT-SOURCE-EVIDENCE
# AUTHORITY BOUNDARY: immutable source observation only; no appointment, IAM, access or execution authority
# TENANT POSTURE: exact tenant; cross-tenant composition is not supported
# FAIL-CLOSED POSTURE: malformed, mismatched or incomplete statutory evidence rejects
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
