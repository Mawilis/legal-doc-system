"""TITLE: WILSY OS Sheriff Ministerial Appointment Verification Boundary.
VERSION: v1.0.0-SHERIFF-MINISTERIAL-APPOINTMENT-VERIFICATION
AUTHORITY: Non-authorizing documentary verification and currentness denial only.
EPITOME: Validate exact ministerial appointment capture integrity, actor and
    subject scope, evidence freshness, and effective dates without converting
    source observation into statutory authority or Sheriff operational access.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/sheriff_ministerial_appointment_verification.py
COLLABORATION / OWNERSHIP: Legal Operations owns the decision contract; the
    Minister remains the statutory appointment authority; the South African
    Board for Sheriffs, verified natural-person identity, and IAM remain separate.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-MINISTERIAL-APPOINTMENT-VERIFICATION
    Adds integrity, scope, freshness, and effective-window checks for
    ministerial appointment source captures. No Minister trust root currently
    exists in this module, so every otherwise-valid capture remains blocked.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Raw capture bytes are transient; decisions retain
    opaque identifiers and digests only.
TENANT BOUNDARY: Exact tenant, principal, subject, instrument and actor scope.
AUTHORITY BOUNDARY: Documentary verification only. No Minister authentication,
    statutory appointment, Board approval, FFC/insurance currentness, identity
    proof, IAM, office access, queue access, service command or legal execution.
TRANSACTION BOUNDARY: Pure evaluation; no persistence, network, transaction,
    registry, retry, commit, abort, route or production activation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from hashlib import sha3_512
import hmac
import json
import re
from typing import Final

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.sheriff_appointment_source_evidence import (
    SheriffAppointmentIssuerAuthority,
    SheriffAppointmentSourceEvidence,
    SheriffSourceObservationState,
)


VERSION: Final[str] = "v1.0.0-SHERIFF-MINISTERIAL-APPOINTMENT-VERIFICATION"
SCHEMA: Final[str] = "WILSY-SHERIFF-MINISTERIAL-APPOINTMENT-VERIFICATION/V1"
_HEX_128: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{128}\Z")
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._:/?#=&%-]{0,511}\Z"
)
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({"default", "global", "root", "*"})


class SheriffMinisterialAppointmentVerificationError(ValueError):
    """Reject malformed appointment verification input without retaining it."""

    def __init__(self, code: str) -> None:
        """Create one stable, content-free failure code."""
        self.code = code
        super().__init__(code)


class MinisterialAppointmentVerificationReason(StrEnum):
    """Stable result reasons for source and statutory-currentness evaluation."""

    ACTOR_INACTIVE = "ACTOR_INACTIVE"
    ACTOR_SCOPE_MISMATCH = "ACTOR_SCOPE_MISMATCH"
    SELF_ATTESTATION = "SELF_ATTESTATION"
    ISSUER_CAPACITY_MISMATCH = "ISSUER_CAPACITY_MISMATCH"
    INSTRUMENT_SCOPE_MISMATCH = "INSTRUMENT_SCOPE_MISMATCH"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    SOURCE_DISPUTED = "SOURCE_DISPUTED"
    SOURCE_UNVERIFIED = "SOURCE_UNVERIFIED"
    FRESHNESS_POLICY_UNKNOWN = "FRESHNESS_POLICY_UNKNOWN"
    CAPTURE_FUTURE_DATED = "CAPTURE_FUTURE_DATED"
    CAPTURE_STALE = "CAPTURE_STALE"
    APPOINTMENT_NOT_YET_EFFECTIVE = "APPOINTMENT_NOT_YET_EFFECTIVE"
    APPOINTMENT_EXPIRED = "APPOINTMENT_EXPIRED"
    MINISTERIAL_ISSUER_TRUST_ROOT_UNAVAILABLE = (
        "MINISTERIAL_ISSUER_TRUST_ROOT_UNAVAILABLE"
    )


def _identifier(name: str, value: object) -> str:
    """Require one bounded canonical opaque identifier."""
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise SheriffMinisterialAppointmentVerificationError(
            f"SHERIFF_MINISTERIAL_{name.upper()}_INVALID"
        )
    if name == "tenant_id" and value.casefold() in _FORBIDDEN_TENANTS:
        raise SheriffMinisterialAppointmentVerificationError(
            "SHERIFF_MINISTERIAL_TENANT_ID_INVALID"
        )
    return value


def _instant(name: str, value: object) -> datetime:
    """Require a canonical UTC instant with whole-second precision."""
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise SheriffMinisterialAppointmentVerificationError(
            f"SHERIFF_MINISTERIAL_{name.upper()}_INVALID"
        )
    normalized = value.astimezone(timezone.utc)
    if normalized != value or normalized.microsecond:
        raise SheriffMinisterialAppointmentVerificationError(
            f"SHERIFF_MINISTERIAL_{name.upper()}_NONCANONICAL"
        )
    return normalized


def _digest(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 digest."""
    if type(value) is not str or _HEX_128.fullmatch(value) is None:
        raise SheriffMinisterialAppointmentVerificationError(
            f"SHERIFF_MINISTERIAL_{name.upper()}_INVALID"
        )
    return value


@dataclass(frozen=True, slots=True)
class MinisterialAppointmentFreshnessPolicy:
    """Declare a separately governed maximum age for source capture observations.

    A missing maximum age means no approved freshness policy exists and
    therefore blocks currentness. This is Wilsy observation freshness, not a
    statutory appointment term or a Minister-issued expiry date.
    """

    policy_id: str
    max_capture_age: timedelta | None

    def __post_init__(self) -> None:
        """Validate an explicit positive whole-second freshness policy."""
        object.__setattr__(self, "policy_id", _identifier("policy_id", self.policy_id))
        age = self.max_capture_age
        if age is not None and (
            type(age) is not timedelta or age <= timedelta(0) or age.microseconds
        ):
            raise SheriffMinisterialAppointmentVerificationError(
                "SHERIFF_MINISTERIAL_FRESHNESS_POLICY_INVALID"
            )


@dataclass(frozen=True, slots=True)
class MinisterialAppointmentCapture:
    """Carry transient source bytes and exact provenance into verification.

    The capture digest is recomputed at construction. Raw bytes are never
    copied into the verification decision. This capture does not authenticate
    the Minister or prove that the source is an official statutory record.
    """

    tenant_id: str
    actor_principal_id: str
    principal_id: str
    subject_reference: str
    instrument_reference: str
    instrument_fingerprint: str
    source_uri: str
    source_verification_reference: str
    checked_at: datetime
    captured_payload: bytes
    capture_digest: str

    def __post_init__(self) -> None:
        """Validate scope and recompute SHA3-512 over the transient payload."""
        for name in (
            "tenant_id",
            "actor_principal_id",
            "principal_id",
            "subject_reference",
            "instrument_reference",
            "source_uri",
            "source_verification_reference",
        ):
            object.__setattr__(self, name, _identifier(name, getattr(self, name)))
        object.__setattr__(
            self,
            "instrument_fingerprint",
            _digest("instrument_fingerprint", self.instrument_fingerprint),
        )
        object.__setattr__(self, "checked_at", _instant("checked_at", self.checked_at))
        if type(self.captured_payload) is not bytes or not self.captured_payload:
            raise SheriffMinisterialAppointmentVerificationError(
                "SHERIFF_MINISTERIAL_CAPTURE_PAYLOAD_INVALID"
            )
        supplied = _digest("capture_digest", self.capture_digest)
        calculated = sha3_512(self.captured_payload).hexdigest()
        if not hmac.compare_digest(supplied, calculated):
            raise SheriffMinisterialAppointmentVerificationError(
                "SHERIFF_MINISTERIAL_CAPTURE_DIGEST_MISMATCH"
            )


@dataclass(frozen=True, slots=True, init=False)
class MinisterialAppointmentVerificationDecision:
    """Internally issued, content-free documentary decision with no authority.

    Direct construction is forbidden. Every property that could be mistaken
    for statutory or operational permission is unconditionally false until a
    separately governed Minister trust root and independent authority gates
    are implemented and certified.
    """

    schema: str
    version: str
    tenant_id: str
    principal_id: str
    actor_principal_id: str
    evidence_fingerprint: str
    capture_digest: str
    checked_at: datetime
    evaluated_at: datetime
    freshness_policy_id: str
    reason: MinisterialAppointmentVerificationReason
    replay_identity: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Reject direct construction and dataclasses.replace forgery."""
        del args, kwargs
        raise SheriffMinisterialAppointmentVerificationError(
            "SHERIFF_MINISTERIAL_DECISION_DIRECT_CONSTRUCTION_FORBIDDEN"
        )

    @property
    def statutory_appointment_current(self) -> bool:
        """A documentary verification decision never establishes statutory status."""
        return False

    @property
    def permits_operational_access(self) -> bool:
        """A documentary verification decision never grants Sheriff access."""
        return False

    @property
    def permits_legal_execution(self) -> bool:
        """A documentary verification decision never authorizes legal execution."""
        return False


def _issue_decision(**values: object) -> MinisterialAppointmentVerificationDecision:
    """Issue one closed-shape immutable decision from the verifier only."""
    if set(values) != {item.name for item in fields(MinisterialAppointmentVerificationDecision)}:
        raise SheriffMinisterialAppointmentVerificationError(
            "SHERIFF_MINISTERIAL_DECISION_SHAPE_INVALID"
        )
    decision = object.__new__(MinisterialAppointmentVerificationDecision)
    for name, value in values.items():
        object.__setattr__(decision, name, value)
    return decision


def verify_ministerial_appointment(
    *,
    evidence: SheriffAppointmentSourceEvidence,
    capture: MinisterialAppointmentCapture,
    actor_authority: PrincipalAuthority,
    policy: MinisterialAppointmentFreshnessPolicy,
    evaluated_at: datetime,
) -> MinisterialAppointmentVerificationDecision:
    """Verify documentary capture integrity and return a non-authorizing decision.

    The verifier checks the exact immutable source-evidence value, actor
    lifecycle, tenant/principal/subject/instrument scope, capture integrity,
    observation freshness, and appointment effective dates. It does not infer
    Minister authentication from a URL, document, human review, or a caller
    supplied verification label. No canonical Minister trust root is currently
    available; therefore the strongest otherwise-valid result is an explicit
    trust-root-unavailable denial.

    No registry read, persistence, IAM grant, queue access or execution occurs.
    """
    if type(evidence) is not SheriffAppointmentSourceEvidence:
        raise SheriffMinisterialAppointmentVerificationError(
            "SHERIFF_MINISTERIAL_SOURCE_EVIDENCE_REQUIRED"
        )
    try:
        canonical_evidence = replace(evidence)
    except Exception as error:
        raise SheriffMinisterialAppointmentVerificationError(
            "SHERIFF_MINISTERIAL_SOURCE_EVIDENCE_CORRUPT"
        ) from error
    if not hmac.compare_digest(canonical_evidence.fingerprint, evidence.fingerprint):
        raise SheriffMinisterialAppointmentVerificationError(
            "SHERIFF_MINISTERIAL_SOURCE_EVIDENCE_CORRUPT"
        )
    if type(capture) is not MinisterialAppointmentCapture:
        raise SheriffMinisterialAppointmentVerificationError(
            "SHERIFF_MINISTERIAL_CAPTURE_REQUIRED"
        )
    if type(actor_authority) is not PrincipalAuthority:
        raise SheriffMinisterialAppointmentVerificationError(
            "SHERIFF_MINISTERIAL_ACTOR_AUTHORITY_REQUIRED"
        )
    if type(policy) is not MinisterialAppointmentFreshnessPolicy:
        raise SheriffMinisterialAppointmentVerificationError(
            "SHERIFF_MINISTERIAL_FRESHNESS_POLICY_REQUIRED"
        )
    at = _instant("evaluated_at", evaluated_at)

    reason = MinisterialAppointmentVerificationReason.MINISTERIAL_ISSUER_TRUST_ROOT_UNAVAILABLE
    if actor_authority.status is not PrincipalStatus.ACTIVE:
        reason = MinisterialAppointmentVerificationReason.ACTOR_INACTIVE
    elif (
        actor_authority.principal_id != capture.actor_principal_id
        or canonical_evidence.tenant_id != capture.tenant_id
        or canonical_evidence.principal_id != capture.principal_id
        or canonical_evidence.verified_subject_reference != capture.subject_reference
    ):
        reason = MinisterialAppointmentVerificationReason.ACTOR_SCOPE_MISMATCH
    elif capture.actor_principal_id == canonical_evidence.principal_id:
        reason = MinisterialAppointmentVerificationReason.SELF_ATTESTATION
    elif canonical_evidence.verified_by_principal_id != capture.actor_principal_id:
        reason = MinisterialAppointmentVerificationReason.ACTOR_SCOPE_MISMATCH
    elif canonical_evidence.issuer_authority is not SheriffAppointmentIssuerAuthority.MINISTER:
        reason = MinisterialAppointmentVerificationReason.ISSUER_CAPACITY_MISMATCH
    elif (
        canonical_evidence.instrument_reference != capture.instrument_reference
        or canonical_evidence.instrument_fingerprint != capture.instrument_fingerprint
        or canonical_evidence.source_uri != capture.source_uri
        or canonical_evidence.source_verification_reference
        != capture.source_verification_reference
    ):
        reason = MinisterialAppointmentVerificationReason.INSTRUMENT_SCOPE_MISMATCH
    elif canonical_evidence.source_observation_state is SheriffSourceObservationState.UNVERIFIED_SUBMISSION:
        reason = MinisterialAppointmentVerificationReason.SOURCE_UNVERIFIED
    elif canonical_evidence.source_observation_state is SheriffSourceObservationState.DISPUTED:
        reason = MinisterialAppointmentVerificationReason.SOURCE_DISPUTED
    elif canonical_evidence.source_observation_state is SheriffSourceObservationState.SOURCE_UNAVAILABLE:
        reason = MinisterialAppointmentVerificationReason.SOURCE_UNAVAILABLE
    elif policy.max_capture_age is None:
        reason = MinisterialAppointmentVerificationReason.FRESHNESS_POLICY_UNKNOWN
    elif capture.checked_at > at:
        reason = MinisterialAppointmentVerificationReason.CAPTURE_FUTURE_DATED
    elif at - capture.checked_at > policy.max_capture_age:
        reason = MinisterialAppointmentVerificationReason.CAPTURE_STALE
    elif at < canonical_evidence.effective_from:
        reason = MinisterialAppointmentVerificationReason.APPOINTMENT_NOT_YET_EFFECTIVE
    elif (
        canonical_evidence.effective_until is not None
        and at >= canonical_evidence.effective_until
    ):
        reason = MinisterialAppointmentVerificationReason.APPOINTMENT_EXPIRED

    replay_material = {
        "schema": SCHEMA,
        "version": VERSION,
        "tenant_id": canonical_evidence.tenant_id,
        "principal_id": canonical_evidence.principal_id,
        "actor_principal_id": capture.actor_principal_id,
        "evidence_fingerprint": canonical_evidence.fingerprint,
        "capture_digest": capture.capture_digest,
        "checked_at": capture.checked_at.isoformat(),
        "evaluated_at": at.isoformat(),
        "freshness_policy_id": policy.policy_id,
        "reason": reason.value,
    }
    replay_identity = sha3_512(
        json.dumps(
            replay_material, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
    ).hexdigest()
    return _issue_decision(
        schema=SCHEMA,
        version=VERSION,
        tenant_id=canonical_evidence.tenant_id,
        principal_id=canonical_evidence.principal_id,
        actor_principal_id=capture.actor_principal_id,
        evidence_fingerprint=canonical_evidence.fingerprint,
        capture_digest=capture.capture_digest,
        checked_at=capture.checked_at,
        evaluated_at=at,
        freshness_policy_id=policy.policy_id,
        reason=reason,
        replay_identity=replay_identity,
    )


__all__ = [
    "VERSION",
    "SCHEMA",
    "SheriffMinisterialAppointmentVerificationError",
    "MinisterialAppointmentVerificationReason",
    "MinisterialAppointmentFreshnessPolicy",
    "MinisterialAppointmentCapture",
    "MinisterialAppointmentVerificationDecision",
    "verify_ministerial_appointment",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: sheriff_ministerial_appointment_verification.py
# VERSION: v1.0.0-SHERIFF-MINISTERIAL-APPOINTMENT-VERIFICATION
# AUTHORITY BOUNDARY: documentary capture verification and denial only; no statutory or operational authority
# TENANT POSTURE: exact tenant, actor, principal, subject and instrument scope
# FAIL-CLOSED POSTURE: malformed, mismatched, stale, unavailable, disputed, expired or unauthenticated source denies
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
