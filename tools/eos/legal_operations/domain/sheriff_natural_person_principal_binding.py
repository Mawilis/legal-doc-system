"""TITLE: WILSY OS Sheriff Natural-Person Identity to Principal Binding.
VERSION: v1.0.0-SHERIFF-NATURAL-PERSON-PRINCIPAL-BINDING
AUTHORITY: Non-authorizing identity proof and principal-binding verification.
EPITOME: Bind an opaque natural-person subject reference to one WILSY principal
    and exact Ministerial appointment without storing national ID numbers,
    names, birth dates, addresses, biometrics or identity-document payloads.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/sheriff_natural_person_principal_binding.py
COLLABORATION / OWNERSHIP: Identity issuer owns the identity assertion; the
    Minister owns Sheriff appointment; WILSY IAM owns principal lifecycle;
    Legal Operations owns the binding decision. Each authority is independent.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-NATURAL-PERSON-PRINCIPAL-BINDING
    Adds opaque identity proof, exact appointment/principal binding and a
    fail-closed verification decision while no identity-issuer trust root exists.
COMPLIANCE: POPIA sections 10, 19; GDPR Articles 5, 25, 32; SOC 2 CC6.1.
SECURITY / PRIVACY POSTURE: No raw identity numbers, documents, biometrics,
    names, dates of birth or addresses are accepted or retained.
TENANT BOUNDARY: Exact tenant, identity subject, WILSY principal, office,
    appointment fingerprint and verifier principal.
AUTHORITY BOUNDARY: Identity binding only. No Minister authentication,
    statutory appointment, Board approval, FFC/insurance currentness, IAM grant,
    office/queue access, service command or legal execution.
TRANSACTION BOUNDARY: Pure evaluation; no persistence, network, transaction,
    registry, retry, commit, abort, route or production activation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import hmac
import json
import re
from typing import Final

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.sheriff_appointment_source_evidence import (
    SheriffAppointmentSourceEvidence,
    SheriffSourceObservationState,
    SheriffSourceVerificationMethod,
)


VERSION: Final[str] = "v1.0.0-SHERIFF-NATURAL-PERSON-PRINCIPAL-BINDING"
SCHEMA: Final[str] = "WILSY-SHERIFF-NATURAL-PERSON-PRINCIPAL-BINDING/V1"
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/?#=&%-]{0,511}$"
)
_HEX_128: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "root", "*"}
)


class SheriffNaturalPersonBindingError(ValueError):
    """Reject malformed natural-person identity proof or principal binding."""

    def __init__(self, code: str) -> None:
        """Create one stable, content-free failure code."""
        self.code = code
        super().__init__(code)


class SheriffNaturalPersonBindingReason(StrEnum):
    """Stable identity-binding denial reasons."""

    ACTOR_INACTIVE = "ACTOR_INACTIVE"
    ACTOR_SCOPE_MISMATCH = "ACTOR_SCOPE_MISMATCH"
    TENANT_SCOPE_MISMATCH = "TENANT_SCOPE_MISMATCH"
    SUBJECT_SCOPE_MISMATCH = "SUBJECT_SCOPE_MISMATCH"
    PRINCIPAL_SCOPE_MISMATCH = "PRINCIPAL_SCOPE_MISMATCH"
    APPOINTMENT_SCOPE_MISMATCH = "APPOINTMENT_SCOPE_MISMATCH"
    IDENTITY_PROOF_FINGERPRINT_MISMATCH = "IDENTITY_PROOF_FINGERPRINT_MISMATCH"
    IDENTITY_PROOF_NOT_AUTHENTICATED = "IDENTITY_PROOF_NOT_AUTHENTICATED"
    IDENTITY_PROOF_NOT_YET_VALID = "IDENTITY_PROOF_NOT_YET_VALID"
    IDENTITY_PROOF_EXPIRED = "IDENTITY_PROOF_EXPIRED"
    BINDING_NOT_YET_EFFECTIVE = "BINDING_NOT_YET_EFFECTIVE"
    BINDING_EXPIRED = "BINDING_EXPIRED"
    IDENTITY_ISSUER_TRUST_ROOT_UNAVAILABLE = "IDENTITY_ISSUER_TRUST_ROOT_UNAVAILABLE"


def _identifier(name: str, value: object) -> str:
    """Require one canonical bounded opaque identifier."""
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise SheriffNaturalPersonBindingError(
            f"SHERIFF_NATURAL_PERSON_{name.upper()}_INVALID"
        )
    if name == "tenant_id" and value.casefold() in _FORBIDDEN_TENANTS:
        raise SheriffNaturalPersonBindingError(
            "SHERIFF_NATURAL_PERSON_TENANT_ID_INVALID"
        )
    return value


def _digest(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 fingerprint."""
    if type(value) is not str or _HEX_128.fullmatch(value) is None:
        raise SheriffNaturalPersonBindingError(
            f"SHERIFF_NATURAL_PERSON_{name.upper()}_INVALID"
        )
    return value


def _instant(name: str, value: object) -> datetime:
    """Require an aware UTC instant with whole-second precision."""
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise SheriffNaturalPersonBindingError(
            f"SHERIFF_NATURAL_PERSON_{name.upper()}_INVALID"
        )
    normalized = value.astimezone(timezone.utc)
    if normalized != value or normalized.microsecond:
        raise SheriffNaturalPersonBindingError(
            f"SHERIFF_NATURAL_PERSON_{name.upper()}_NONCANONICAL"
        )
    return normalized


@dataclass(frozen=True, slots=True)
class SheriffNaturalPersonIdentityProof:
    """Opaque identity assertion from an external issuer; no personal data.

    The subject reference is issuer-scoped and opaque. The record intentionally
    excludes national identity numbers, names, dates of birth, addresses,
    biometric templates, document images and raw identity-document payloads.
    An authenticated-response label is only source provenance, not trust-root
    authentication of the identity issuer.
    """

    tenant_id: str
    identity_proof_id: str
    revision: int
    identity_subject_reference: str
    identity_issuer_reference: str
    identity_proof_reference: str
    identity_proof_fingerprint: str
    source_uri: str
    source_observation_state: SheriffSourceObservationState | str
    source_verification_method: SheriffSourceVerificationMethod | str
    source_verification_reference: str
    verified_by_principal_id: str
    observed_at: datetime
    valid_from: datetime
    valid_until: datetime
    supersedes_fingerprint: str | None = None
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate opaque issuer identity proof and bind the entire record."""
        for name in (
            "tenant_id",
            "identity_proof_id",
            "identity_subject_reference",
            "identity_issuer_reference",
            "identity_proof_reference",
            "source_uri",
            "source_verification_reference",
            "verified_by_principal_id",
        ):
            object.__setattr__(self, name, _identifier(name, getattr(self, name)))
        object.__setattr__(
            self,
            "identity_proof_fingerprint",
            _digest("identity_proof_fingerprint", self.identity_proof_fingerprint),
        )
        if type(self.revision) is not int or self.revision < 1:
            raise SheriffNaturalPersonBindingError(
                "SHERIFF_NATURAL_PERSON_REVISION_INVALID"
            )
        try:
            observation = SheriffSourceObservationState(self.source_observation_state)
            method = SheriffSourceVerificationMethod(self.source_verification_method)
        except (TypeError, ValueError) as error:
            raise SheriffNaturalPersonBindingError(
                "SHERIFF_NATURAL_PERSON_SOURCE_ENUM_INVALID"
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
            raise SheriffNaturalPersonBindingError(
                "SHERIFF_NATURAL_PERSON_SOURCE_METHOD_MISMATCH"
            )
        object.__setattr__(self, "source_observation_state", observation)
        object.__setattr__(self, "source_verification_method", method)

        observed = _instant("observed_at", self.observed_at)
        start = _instant("valid_from", self.valid_from)
        end = _instant("valid_until", self.valid_until)
        if end <= start:
            raise SheriffNaturalPersonBindingError(
                "SHERIFF_NATURAL_PERSON_VALIDITY_WINDOW_INVALID"
            )
        object.__setattr__(self, "observed_at", observed)
        object.__setattr__(self, "valid_from", start)
        object.__setattr__(self, "valid_until", end)
        predecessor = (
            None if self.supersedes_fingerprint is None
            else _digest("supersedes_fingerprint", self.supersedes_fingerprint)
        )
        if self.revision == 1 and predecessor is not None:
            raise SheriffNaturalPersonBindingError(
                "SHERIFF_NATURAL_PERSON_ROOT_SUPERSEDES_FORBIDDEN"
            )
        if self.revision > 1 and predecessor is None:
            raise SheriffNaturalPersonBindingError(
                "SHERIFF_NATURAL_PERSON_SUCCESSOR_REQUIRED"
            )
        object.__setattr__(self, "supersedes_fingerprint", predecessor)
        if self.schema != SCHEMA or self.version != VERSION:
            raise SheriffNaturalPersonBindingError(
                "SHERIFF_NATURAL_PERSON_SCHEMA_VERSION_INVALID"
            )
        calculated = self._compute_fingerprint()
        if self.fingerprint:
            supplied = _digest("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, calculated):
                raise SheriffNaturalPersonBindingError(
                    "SHERIFF_NATURAL_PERSON_FINGERPRINT_MISMATCH"
                )
        object.__setattr__(self, "fingerprint", calculated)

    def semantic_dict(self) -> dict[str, object]:
        """Return every opaque identity proof field without raw personal data."""
        return {
            "schema": self.schema,
            "version": self.version,
            "tenant_id": self.tenant_id,
            "identity_proof_id": self.identity_proof_id,
            "revision": self.revision,
            "identity_subject_reference": self.identity_subject_reference,
            "identity_issuer_reference": self.identity_issuer_reference,
            "identity_proof_reference": self.identity_proof_reference,
            "identity_proof_fingerprint": self.identity_proof_fingerprint,
            "source_uri": self.source_uri,
            "source_observation_state": SheriffSourceObservationState(self.source_observation_state).value,
            "source_verification_method": SheriffSourceVerificationMethod(self.source_verification_method).value,
            "source_verification_reference": self.source_verification_reference,
            "verified_by_principal_id": self.verified_by_principal_id,
            "observed_at": self.observed_at.isoformat(),
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat(),
            "supersedes_fingerprint": self.supersedes_fingerprint,
        }

    def _compute_fingerprint(self) -> str:
        """Hash the complete opaque identity assertion."""
        encoded = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return sha3_512(encoded).hexdigest()

    @property
    def is_identity_verified(self) -> bool:
        """An issuer assertion alone does not establish a verified identity."""
        return False


@dataclass(frozen=True, slots=True)
class SheriffNaturalPersonPrincipalBinding:
    """Bind one WILSY principal to an opaque identity subject and appointment."""

    tenant_id: str
    principal_id: str
    identity_subject_reference: str
    identity_proof_fingerprint: str
    appointment_evidence_fingerprint: str
    sheriff_office_id: str
    capacity: str
    bound_by_principal_id: str
    effective_from: datetime
    effective_until: datetime | None = None
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact principal/subject/appointment scope."""
        for name in (
            "tenant_id",
            "principal_id",
            "identity_subject_reference",
            "sheriff_office_id",
            "capacity",
            "bound_by_principal_id",
        ):
            object.__setattr__(self, name, _identifier(name, getattr(self, name)))
        for name in ("identity_proof_fingerprint", "appointment_evidence_fingerprint"):
            object.__setattr__(self, name, _digest(name, getattr(self, name)))
        if self.principal_id == self.bound_by_principal_id:
            raise SheriffNaturalPersonBindingError(
                "SHERIFF_NATURAL_PERSON_SELF_BINDING_FORBIDDEN"
            )
        start = _instant("effective_from", self.effective_from)
        end = None if self.effective_until is None else _instant("effective_until", self.effective_until)
        if end is not None and end <= start:
            raise SheriffNaturalPersonBindingError(
                "SHERIFF_NATURAL_PERSON_BINDING_WINDOW_INVALID"
            )
        object.__setattr__(self, "effective_from", start)
        object.__setattr__(self, "effective_until", end)
        if self.schema != SCHEMA or self.version != VERSION:
            raise SheriffNaturalPersonBindingError(
                "SHERIFF_NATURAL_PERSON_BINDING_SCHEMA_INVALID"
            )
        calculated = sha3_512(
            json.dumps(
                {
                    "schema": self.schema,
                    "version": self.version,
                    "tenant_id": self.tenant_id,
                    "principal_id": self.principal_id,
                    "identity_subject_reference": self.identity_subject_reference,
                    "identity_proof_fingerprint": self.identity_proof_fingerprint,
                    "appointment_evidence_fingerprint": self.appointment_evidence_fingerprint,
                    "sheriff_office_id": self.sheriff_office_id,
                    "capacity": self.capacity,
                    "bound_by_principal_id": self.bound_by_principal_id,
                    "effective_from": start.isoformat(),
                    "effective_until": end.isoformat() if end else None,
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        if self.fingerprint:
            supplied = _digest("binding_fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, calculated):
                raise SheriffNaturalPersonBindingError(
                    "SHERIFF_NATURAL_PERSON_BINDING_FINGERPRINT_MISMATCH"
                )
        object.__setattr__(self, "fingerprint", calculated)


@dataclass(frozen=True, slots=True, init=False)
class SheriffNaturalPersonBindingDecision:
    """Internally issued non-authorizing identity-binding decision."""

    schema: str
    version: str
    tenant_id: str
    principal_id: str
    identity_subject_reference: str
    identity_proof_fingerprint: str
    appointment_evidence_fingerprint: str
    evaluated_at: datetime
    reason: SheriffNaturalPersonBindingReason
    replay_identity: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Reject direct construction and dataclasses.replace forgery."""
        del args, kwargs
        raise SheriffNaturalPersonBindingError(
            "SHERIFF_NATURAL_PERSON_DECISION_DIRECT_CONSTRUCTION_FORBIDDEN"
        )

    @property
    def natural_person_identity_verified(self) -> bool:
        """No issuer trust root exists, so this decision can never verify identity."""
        return False

    @property
    def permits_operational_access(self) -> bool:
        """Identity binding alone never grants Sheriff access."""
        return False

    @property
    def permits_legal_execution(self) -> bool:
        """Identity binding alone never authorizes legal execution."""
        return False


def _issue_decision(**values: object) -> SheriffNaturalPersonBindingDecision:
    """Issue one closed-shape immutable decision from the verifier only."""
    if set(values) != {item.name for item in fields(SheriffNaturalPersonBindingDecision)}:
        raise SheriffNaturalPersonBindingError(
            "SHERIFF_NATURAL_PERSON_DECISION_SHAPE_INVALID"
        )
    decision = object.__new__(SheriffNaturalPersonBindingDecision)
    for name, value in values.items():
        object.__setattr__(decision, name, value)
    return decision


def verify_sheriff_natural_person_binding(
    *,
    proof: SheriffNaturalPersonIdentityProof,
    binding: SheriffNaturalPersonPrincipalBinding,
    appointment: SheriffAppointmentSourceEvidence,
    actor_authority: PrincipalAuthority,
    evaluated_at: datetime,
) -> SheriffNaturalPersonBindingDecision:
    """Verify exact identity/appointment/principal linkage and fail closed.

    This checks the opaque identity proof fingerprint, subject reference,
    tenant, WILSY principal, office, appointment and active verifier. An
    authenticated-response label is not a substitute for an authenticated
    identity-issuer trust root. No such root is configured here, so the
    strongest otherwise-valid result is IDENTITY_ISSUER_TRUST_ROOT_UNAVAILABLE.

    No raw identity data, persistence, IAM grant, queue access or execution occurs.
    """
    if type(proof) is not SheriffNaturalPersonIdentityProof:
        raise SheriffNaturalPersonBindingError("SHERIFF_NATURAL_PERSON_PROOF_REQUIRED")
    if type(binding) is not SheriffNaturalPersonPrincipalBinding:
        raise SheriffNaturalPersonBindingError("SHERIFF_NATURAL_PERSON_BINDING_REQUIRED")
    if type(appointment) is not SheriffAppointmentSourceEvidence:
        raise SheriffNaturalPersonBindingError("SHERIFF_NATURAL_PERSON_APPOINTMENT_REQUIRED")
    if type(actor_authority) is not PrincipalAuthority:
        raise SheriffNaturalPersonBindingError("SHERIFF_NATURAL_PERSON_ACTOR_AUTHORITY_REQUIRED")
    try:
        canonical_appointment = replace(appointment)
    except Exception as error:
        raise SheriffNaturalPersonBindingError(
            "SHERIFF_NATURAL_PERSON_APPOINTMENT_CORRUPT"
        ) from error
    at = _instant("evaluated_at", evaluated_at)

    reason = SheriffNaturalPersonBindingReason.IDENTITY_ISSUER_TRUST_ROOT_UNAVAILABLE
    if actor_authority.status is not PrincipalStatus.ACTIVE:
        reason = SheriffNaturalPersonBindingReason.ACTOR_INACTIVE
    elif (
        binding.bound_by_principal_id != actor_authority.principal_id
        or actor_authority.principal_id == binding.principal_id
    ):
        reason = SheriffNaturalPersonBindingReason.ACTOR_SCOPE_MISMATCH
    elif (
        proof.tenant_id != binding.tenant_id
        or canonical_appointment.tenant_id != binding.tenant_id
    ):
        reason = SheriffNaturalPersonBindingReason.TENANT_SCOPE_MISMATCH
    elif (
        proof.identity_subject_reference != binding.identity_subject_reference
        or canonical_appointment.verified_subject_reference
        != binding.identity_subject_reference
    ):
        reason = SheriffNaturalPersonBindingReason.SUBJECT_SCOPE_MISMATCH
    elif (
        canonical_appointment.principal_id != binding.principal_id
        or binding.principal_id != canonical_appointment.principal_id
    ):
        reason = SheriffNaturalPersonBindingReason.PRINCIPAL_SCOPE_MISMATCH
    elif (
        canonical_appointment.sheriff_office_id != binding.sheriff_office_id
        or canonical_appointment.capacity.value != binding.capacity
        or canonical_appointment.fingerprint != binding.appointment_evidence_fingerprint
    ):
        reason = SheriffNaturalPersonBindingReason.APPOINTMENT_SCOPE_MISMATCH
    elif not hmac.compare_digest(proof.identity_proof_fingerprint, binding.identity_proof_fingerprint):
        reason = SheriffNaturalPersonBindingReason.IDENTITY_PROOF_FINGERPRINT_MISMATCH
    elif proof.source_observation_state is not SheriffSourceObservationState.AUTHENTICATED_RESPONSE:
        reason = SheriffNaturalPersonBindingReason.IDENTITY_PROOF_NOT_AUTHENTICATED
    elif at < binding.effective_from:
        reason = SheriffNaturalPersonBindingReason.BINDING_NOT_YET_EFFECTIVE
    elif binding.effective_until is not None and at >= binding.effective_until:
        reason = SheriffNaturalPersonBindingReason.BINDING_EXPIRED
    elif at < proof.valid_from:
        reason = SheriffNaturalPersonBindingReason.IDENTITY_PROOF_NOT_YET_VALID
    elif at >= proof.valid_until:
        reason = SheriffNaturalPersonBindingReason.IDENTITY_PROOF_EXPIRED

    material = {
        "schema": SCHEMA,
        "version": VERSION,
        "tenant_id": binding.tenant_id,
        "principal_id": binding.principal_id,
        "identity_subject_reference": binding.identity_subject_reference,
        "identity_proof_fingerprint": proof.identity_proof_fingerprint,
        "identity_proof_record_fingerprint": proof.fingerprint,
        "appointment_evidence_fingerprint": binding.appointment_evidence_fingerprint,
        "evaluated_at": at.isoformat(),
        "reason": reason.value,
    }
    replay = sha3_512(
        json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()
    return _issue_decision(
        schema=SCHEMA,
        version=VERSION,
        tenant_id=binding.tenant_id,
        principal_id=binding.principal_id,
        identity_subject_reference=binding.identity_subject_reference,
        identity_proof_fingerprint=proof.identity_proof_fingerprint,
        appointment_evidence_fingerprint=binding.appointment_evidence_fingerprint,
        evaluated_at=at,
        reason=reason,
        replay_identity=replay,
    )


__all__ = [
    "VERSION",
    "SCHEMA",
    "SheriffNaturalPersonBindingError",
    "SheriffNaturalPersonBindingReason",
    "SheriffNaturalPersonIdentityProof",
    "SheriffNaturalPersonPrincipalBinding",
    "SheriffNaturalPersonBindingDecision",
    "verify_sheriff_natural_person_binding",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: sheriff_natural_person_principal_binding.py
# VERSION: v1.0.0-SHERIFF-NATURAL-PERSON-PRINCIPAL-BINDING
# AUTHORITY BOUNDARY: opaque identity binding only; no statutory or operational authority
# PRIVACY POSTURE: no ID numbers, names, DOBs, addresses, biometrics or raw documents
# FAIL-CLOSED POSTURE: identity issuer trust root unavailable; identity remains unverified
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
