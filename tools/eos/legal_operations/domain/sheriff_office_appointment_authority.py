"""TITLE: WILSY OS Sheriff Office Appointment Evidence Authority
VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE
ARTIFACT: tools/eos/legal_operations/domain/sheriff_office_appointment_authority.py
AUTHORITY: Immutable recording of externally issued Sheriff appointment and current Fidelity Fund Certificate evidence.
EPITOME: Bind one authenticated WILSY principal to one canonical SheriffOffice through separately fingerprinted Ministerial appointment, office/jurisdiction scope, and Board Fidelity Fund Certificate evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/sheriff_office_appointment_authority.py
COLLABORATION / OWNERSHIP: Legal Operations owns evidence semantics; IAM owns authenticated principal and tenant authorization; P1 owns canonical SheriffOffice/District identity; the Minister and South African Board for Sheriffs remain external issuing authorities.
CLASSIFICATION: EMERGING CANONICAL
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG: v1.0.0 establishes immutable, effective-dated evidence facts for permanent and acting Sheriff appointments; no appointment is issued by WILSY.
COMPLIANCE: Sheriffs Act 90 of 1986, sections 2, 3, 5 and 30-34; POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers and SHA3-512 evidence fingerprints only; source documents remain outside this value object; no credentials or document contents are stored.
TENANT BOUNDARY: Exact non-pseudo tenant identity; every appointment binds one principal, one canonical office, and one canonical district.
AUTHORITY BOUNDARY: Records externally issued appointment/scope/FFC evidence and verifier attestation only; does not appoint a Sheriff, issue a Fidelity Fund Certificate, authenticate a source document, grant IAM, or independently authorize a request.
CURRENTNESS: Appointment term AND jurisdiction-matched FFC validity AND professional indemnity insurance validity AND verification time must all be current.
TRANSACTION OWNERSHIP: NONE; persistence and transaction lifecycle belong to the registry/orchestrator.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
FAIL-CLOSED DECLARATION: Missing, malformed, stale, ambiguous, mismatched, or unverifiable evidence rejects.

The source evidence is expected to identify the Ministerial appointment under
section 2 (or acting appointment under section 5), the office/court/area scope
under section 2 or section 3, and the current Fidelity Fund Certificate issued
by the South African Board for Sheriffs. A tenant administrator's role, a
business-role label, an operating-role scope descriptor, or a WILSY-created
record is not a substitute for those external instruments. The verifier fields
record who checked the source material; they do not cryptographically prove
that the issuing authority created it.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Final, Mapping, NoReturn, cast

VERSION: Final[str] = "v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE"
SCHEMA: Final[str] = "WILSY-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE/V1"
_APPOINTMENT_KINDS: Final[frozenset[str]] = frozenset({"PERMANENT", "ACTING"})
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({"default", "global", "root", "*"})
_HEX_128: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")


class SheriffOfficeAppointmentAuthorityError(ValueError):
    """Stable fail-closed appointment evidence validation error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise SheriffOfficeAppointmentAuthorityError(code)


def _text(name: str, value: object, limit: int = 240) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 32 for character in value)
    ):
        _fail(f"SHERIFF_APPOINTMENT_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    tenant = _text("tenant_id", value, 160)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("SHERIFF_APPOINTMENT_TENANT_ID_INVALID")
    return tenant


def _revision(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _fail("SHERIFF_APPOINTMENT_REVISION_INVALID")
    return value


def _moment(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(f"SHERIFF_APPOINTMENT_{name.upper()}_INVALID")
    return value.astimezone(timezone.utc)


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or not _HEX_128.fullmatch(value):
        _fail(f"SHERIFF_APPOINTMENT_{name.upper()}_INVALID")
    return value


@dataclass(frozen=True, slots=True)
class SheriffOfficeAppointmentAuthority:
    """Immutable evidence that one principal is appointed for one Sheriff office.

    This object records source instruments and a verifier attestation. It does
    not issue an appointment, validate a certificate with the Board, authenticate
    the source files, or grant access. Callers must independently establish
    current tenant IAM and canonical office/district identity in the same
    transaction as any authorization decision.
    """

    tenant_id: str
    appointment_id: str
    revision: int
    principal_id: str
    sheriff_office_id: str
    district_id: str
    appointment_kind: str
    appointment_instrument_reference: str
    appointment_instrument_fingerprint: str
    office_scope_instrument_reference: str
    office_scope_instrument_fingerprint: str
    fidelity_fund_certificate_reference: str
    fidelity_fund_certificate_fingerprint: str
    certificate_jurisdiction_reference: str
    professional_indemnity_insurance_reference: str
    professional_indemnity_insurance_fingerprint: str
    professional_indemnity_insurance_valid_from: datetime
    professional_indemnity_insurance_valid_until: datetime
    appointment_effective_from: datetime
    appointment_effective_until: datetime | None
    certificate_valid_from: datetime
    certificate_valid_until: datetime
    verified_by_principal_id: str
    verified_at: datetime
    supersedes_fingerprint: str | None = None
    schema: str = SCHEMA
    appointment_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        appointment_id = _text("appointment_id", self.appointment_id)
        revision = _revision(self.revision)
        principal = _text("principal_id", self.principal_id)
        office = _text("sheriff_office_id", self.sheriff_office_id)
        district = _text("district_id", self.district_id)
        kind = _text("appointment_kind", self.appointment_kind, 32)
        if kind not in _APPOINTMENT_KINDS:
            _fail("SHERIFF_APPOINTMENT_KIND_UNSUPPORTED")

        appointment_reference = _text(
            "appointment_instrument_reference",
            self.appointment_instrument_reference,
            500,
        )
        appointment_fingerprint = _fingerprint(
            "appointment_instrument_fingerprint",
            self.appointment_instrument_fingerprint,
        )
        scope_reference = _text(
            "office_scope_instrument_reference",
            self.office_scope_instrument_reference,
            500,
        )
        scope_fingerprint = _fingerprint(
            "office_scope_instrument_fingerprint",
            self.office_scope_instrument_fingerprint,
        )
        certificate_reference = _text(
            "fidelity_fund_certificate_reference",
            self.fidelity_fund_certificate_reference,
            500,
        )
        certificate_fingerprint = _fingerprint(
            "fidelity_fund_certificate_fingerprint",
            self.fidelity_fund_certificate_fingerprint,
        )
        certificate_jurisdiction = _text(
            "certificate_jurisdiction_reference",
            self.certificate_jurisdiction_reference,
            240,
        )
        insurance_reference = _text(
            "professional_indemnity_insurance_reference",
            self.professional_indemnity_insurance_reference,
            500,
        )
        insurance_fingerprint = _fingerprint(
            "professional_indemnity_insurance_fingerprint",
            self.professional_indemnity_insurance_fingerprint,
        )

        appointment_from = _moment(
            "appointment_effective_from",
            self.appointment_effective_from,
        )
        appointment_until = (
            None
            if self.appointment_effective_until is None
            else _moment("appointment_effective_until", self.appointment_effective_until)
        )
        if appointment_until is not None and appointment_until <= appointment_from:
            _fail("SHERIFF_APPOINTMENT_EFFECTIVE_WINDOW_INVALID")
        if kind == "ACTING" and appointment_until is None:
            _fail("SHERIFF_ACTING_APPOINTMENT_END_REQUIRED")

        certificate_from = _moment(
            "certificate_valid_from",
            self.certificate_valid_from,
        )
        certificate_until = _moment(
            "certificate_valid_until",
            self.certificate_valid_until,
        )
        if certificate_until <= certificate_from:
            _fail("SHERIFF_APPOINTMENT_CERTIFICATE_WINDOW_INVALID")
        insurance_from = _moment(
            "professional_indemnity_insurance_valid_from",
            self.professional_indemnity_insurance_valid_from,
        )
        insurance_until = _moment(
            "professional_indemnity_insurance_valid_until",
            self.professional_indemnity_insurance_valid_until,
        )
        if insurance_until <= insurance_from:
            _fail("SHERIFF_APPOINTMENT_INSURANCE_WINDOW_INVALID")

        verifier = _text("verified_by_principal_id", self.verified_by_principal_id)
        if verifier == principal:
            _fail("SHERIFF_APPOINTMENT_SELF_VERIFICATION_FORBIDDEN")
        verified_at = _moment("verified_at", self.verified_at)
        predecessor = (
            None
            if self.supersedes_fingerprint is None
            else _fingerprint("supersedes_fingerprint", self.supersedes_fingerprint)
        )
        if revision == 1 and predecessor is not None:
            _fail("SHERIFF_APPOINTMENT_FIRST_REVISION_SUPERSEDES_FORBIDDEN")
        if revision > 1 and predecessor is None:
            _fail("SHERIFF_APPOINTMENT_SUCCESSOR_SUPERSEDES_REQUIRED")
        if self.schema != SCHEMA or self.appointment_version != VERSION:
            _fail("SHERIFF_APPOINTMENT_SCHEMA_VERSION_INVALID")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "appointment_id", appointment_id)
        object.__setattr__(self, "revision", revision)
        object.__setattr__(self, "principal_id", principal)
        object.__setattr__(self, "sheriff_office_id", office)
        object.__setattr__(self, "district_id", district)
        object.__setattr__(self, "appointment_kind", kind)
        object.__setattr__(self, "appointment_instrument_reference", appointment_reference)
        object.__setattr__(self, "appointment_instrument_fingerprint", appointment_fingerprint)
        object.__setattr__(self, "office_scope_instrument_reference", scope_reference)
        object.__setattr__(self, "office_scope_instrument_fingerprint", scope_fingerprint)
        object.__setattr__(self, "fidelity_fund_certificate_reference", certificate_reference)
        object.__setattr__(self, "fidelity_fund_certificate_fingerprint", certificate_fingerprint)
        object.__setattr__(self, "certificate_jurisdiction_reference", certificate_jurisdiction)
        object.__setattr__(self, "professional_indemnity_insurance_reference", insurance_reference)
        object.__setattr__(self, "professional_indemnity_insurance_fingerprint", insurance_fingerprint)
        object.__setattr__(self, "professional_indemnity_insurance_valid_from", insurance_from)
        object.__setattr__(self, "professional_indemnity_insurance_valid_until", insurance_until)
        object.__setattr__(self, "appointment_effective_from", appointment_from)
        object.__setattr__(self, "appointment_effective_until", appointment_until)
        object.__setattr__(self, "certificate_valid_from", certificate_from)
        object.__setattr__(self, "certificate_valid_until", certificate_until)
        object.__setattr__(self, "verified_by_principal_id", verifier)
        object.__setattr__(self, "verified_at", verified_at)
        object.__setattr__(self, "supersedes_fingerprint", predecessor)

        computed = self._compute_fingerprint()
        if self.fingerprint:
            supplied = _fingerprint("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, computed):
                _fail("SHERIFF_APPOINTMENT_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", computed)

    def semantic_dict(self) -> dict[str, object]:
        """Return the exact deterministic evidence payload, excluding its fingerprint."""
        return {
            "schema": self.schema,
            "appointment_version": self.appointment_version,
            "tenant_id": self.tenant_id,
            "appointment_id": self.appointment_id,
            "revision": self.revision,
            "principal_id": self.principal_id,
            "sheriff_office_id": self.sheriff_office_id,
            "district_id": self.district_id,
            "appointment_kind": self.appointment_kind,
            "appointment_instrument_reference": self.appointment_instrument_reference,
            "appointment_instrument_fingerprint": self.appointment_instrument_fingerprint,
            "office_scope_instrument_reference": self.office_scope_instrument_reference,
            "office_scope_instrument_fingerprint": self.office_scope_instrument_fingerprint,
            "fidelity_fund_certificate_reference": self.fidelity_fund_certificate_reference,
            "fidelity_fund_certificate_fingerprint": self.fidelity_fund_certificate_fingerprint,
            "certificate_jurisdiction_reference": self.certificate_jurisdiction_reference,
            "professional_indemnity_insurance_reference": self.professional_indemnity_insurance_reference,
            "professional_indemnity_insurance_fingerprint": self.professional_indemnity_insurance_fingerprint,
            "professional_indemnity_insurance_valid_from": self.professional_indemnity_insurance_valid_from.isoformat(),
            "professional_indemnity_insurance_valid_until": self.professional_indemnity_insurance_valid_until.isoformat(),
            "appointment_effective_from": self.appointment_effective_from.isoformat(),
            "appointment_effective_until": (
                None
                if self.appointment_effective_until is None
                else self.appointment_effective_until.isoformat()
            ),
            "certificate_valid_from": self.certificate_valid_from.isoformat(),
            "certificate_valid_until": self.certificate_valid_until.isoformat(),
            "verified_by_principal_id": self.verified_by_principal_id,
            "verified_at": self.verified_at.isoformat(),
            "supersedes_fingerprint": self.supersedes_fingerprint,
        }

    def _compute_fingerprint(self) -> str:
        raw = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return hashlib.sha3_512(raw).hexdigest()

    def is_current(self, at: datetime) -> bool:
        """Return evidence-window currentness only; this is not IAM authorization."""
        moment = _moment("currentness_at", at)
        appointment_current = (
            self.appointment_effective_from <= moment
            and (
                self.appointment_effective_until is None
                or moment < self.appointment_effective_until
            )
        )
        certificate_current = (
            self.certificate_valid_from <= moment < self.certificate_valid_until
        )
        insurance_current = (
            self.professional_indemnity_insurance_valid_from
            <= moment
            < self.professional_indemnity_insurance_valid_until
        )
        return (
            appointment_current
            and certificate_current
            and insurance_current
            and self.verified_at <= moment
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize exact immutable appointment evidence."""
        return {**self.semantic_dict(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "SheriffOfficeAppointmentAuthority":
        """Strictly hydrate an exact persisted appointment evidence payload."""
        expected = {
            "schema",
            "appointment_version",
            "tenant_id",
            "appointment_id",
            "revision",
            "principal_id",
            "sheriff_office_id",
            "district_id",
            "appointment_kind",
            "appointment_instrument_reference",
            "appointment_instrument_fingerprint",
            "office_scope_instrument_reference",
            "office_scope_instrument_fingerprint",
            "fidelity_fund_certificate_reference",
            "fidelity_fund_certificate_fingerprint",
            "certificate_jurisdiction_reference",
            "professional_indemnity_insurance_reference",
            "professional_indemnity_insurance_fingerprint",
            "professional_indemnity_insurance_valid_from",
            "professional_indemnity_insurance_valid_until",
            "appointment_effective_from",
            "appointment_effective_until",
            "certificate_valid_from",
            "certificate_valid_until",
            "verified_by_principal_id",
            "verified_at",
            "supersedes_fingerprint",
            "fingerprint",
        }
        if set(payload) != expected:
            _fail("SHERIFF_APPOINTMENT_PAYLOAD_SCHEMA_INVALID")

        def parse_time(name: str, value: object, optional: bool = False) -> datetime | None:
            if optional and value is None:
                return None
            if not isinstance(value, str):
                _fail(f"SHERIFF_APPOINTMENT_{name.upper()}_INVALID")
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                _fail(f"SHERIFF_APPOINTMENT_{name.upper()}_INVALID")

        return cls(
            schema=cast(str, payload["schema"]),
            appointment_version=cast(str, payload["appointment_version"]),
            tenant_id=cast(str, payload["tenant_id"]),
            appointment_id=cast(str, payload["appointment_id"]),
            revision=cast(int, payload["revision"]),
            principal_id=cast(str, payload["principal_id"]),
            sheriff_office_id=cast(str, payload["sheriff_office_id"]),
            district_id=cast(str, payload["district_id"]),
            appointment_kind=cast(str, payload["appointment_kind"]),
            appointment_instrument_reference=cast(str, payload["appointment_instrument_reference"]),
            appointment_instrument_fingerprint=cast(str, payload["appointment_instrument_fingerprint"]),
            office_scope_instrument_reference=cast(str, payload["office_scope_instrument_reference"]),
            office_scope_instrument_fingerprint=cast(str, payload["office_scope_instrument_fingerprint"]),
            fidelity_fund_certificate_reference=cast(str, payload["fidelity_fund_certificate_reference"]),
            fidelity_fund_certificate_fingerprint=cast(str, payload["fidelity_fund_certificate_fingerprint"]),
            certificate_jurisdiction_reference=cast(str, payload["certificate_jurisdiction_reference"]),
            professional_indemnity_insurance_reference=cast(str, payload["professional_indemnity_insurance_reference"]),
            professional_indemnity_insurance_fingerprint=cast(str, payload["professional_indemnity_insurance_fingerprint"]),
            professional_indemnity_insurance_valid_from=cast(datetime, parse_time("professional_indemnity_insurance_valid_from", payload["professional_indemnity_insurance_valid_from"])),
            professional_indemnity_insurance_valid_until=cast(datetime, parse_time("professional_indemnity_insurance_valid_until", payload["professional_indemnity_insurance_valid_until"])),
            appointment_effective_from=cast(datetime, parse_time("appointment_effective_from", payload["appointment_effective_from"])),
            appointment_effective_until=cast(datetime | None, parse_time("appointment_effective_until", payload["appointment_effective_until"], True)),
            certificate_valid_from=cast(datetime, parse_time("certificate_valid_from", payload["certificate_valid_from"])),
            certificate_valid_until=cast(datetime, parse_time("certificate_valid_until", payload["certificate_valid_until"])),
            verified_by_principal_id=cast(str, payload["verified_by_principal_id"]),
            verified_at=cast(datetime, parse_time("verified_at", payload["verified_at"])),
            supersedes_fingerprint=cast(str | None, payload["supersedes_fingerprint"]),
            fingerprint=cast(str, payload["fingerprint"]),
        )


__all__ = [
    "VERSION",
    "SCHEMA",
    "SheriffOfficeAppointmentAuthority",
    "SheriffOfficeAppointmentAuthorityError",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: tools/eos/legal_operations/domain/sheriff_office_appointment_authority.py
# VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE
# AUTHORITY BOUNDARY: externally issued appointment and FFC evidence record only; no IAM or appointment issuance
# TENANT POSTURE: exact tenant/principal/office/district binding
# FAIL-CLOSED POSTURE: invalid schema, time windows, fingerprints, source references, or lineage reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
