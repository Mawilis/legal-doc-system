"""TITLE: WILSY OS Regulatory Source Verification Boundary.
VERSION: v1.0.1-R64-AUTHENTICATED-REGULATORY-VERIFICATION
AUTHORITY: Non-ingesting verification and evidence-admission denial only.
EPITOME: Verify capture integrity, source classification, subject scope and
    evidence-kind-specific freshness before any R63 ingestion is considered,
    while denying ingestion until both an authenticated regulator trust root
    and a dedicated current actor permission are canonically available.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/regulatory_source_verification.py
COLLABORATION / OWNERSHIP: Legal Operations owns the bounded verification
    decision; R62 owns immutable documentary evidence; R63 owns persistence;
    the Legal Practice Council remains authoritative for published records.
CERTIFICATION / UPDATE DATE: 2026-10-22
CHANGELOG:
    2026-10-22 v1.0.1-R64-AUTHENTICATED-REGULATORY-VERIFICATION
    Removes constructible ingestion authority, closes direct/replace decision
    forgery, preserves normalized issuer typing, and denies explicit staleness.
    2026-10-21 v1.0.0-R64-AUTHENTICATED-REGULATORY-VERIFICATION
    Introduces six-state source classification, SHA3-512 capture/replay
    integrity, distinct practising-status and FFC freshness policies, current
    principal gating, and typed non-ingesting authority denial.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Raw capture bytes are transient and excluded from
    returned decisions; outputs contain opaque identifiers and digests only.
TENANT BOUNDARY: Evidence, capture and actor scope must match one exact tenant;
    cross-tenant inputs deny without registry access or existence disclosure.
AUTHORITY BOUNDARY: Verification is not LPC authentication, practising status,
    FFC authority, IAM, professional-practice, matter-content, access, review,
    approval, supervision, reassignment, or ingestion authority.
TRANSACTION BOUNDARY: Pure verification only. No session, transaction, registry
    read/write, retry, commit, abort, route, or network authority is present.
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
from typing import Final, Protocol, runtime_checkable

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.legal_practitioner_professional_standing_evidence import (
    LegalPractitionerProfessionalStandingEvidence as Evidence,
    ProfessionalEvidenceKind,
    ProfessionalEvidenceMethod,
)
from tools.eos.legal_operations.registry.legal_practitioner_professional_standing_evidence_registry import (
    AUTHORITATIVE_PUBLIC_SOURCES,
)


VERSION: Final[str] = "v1.0.1-R64-AUTHENTICATED-REGULATORY-VERIFICATION"
SCHEMA: Final[str] = "WILSY-REGULATORY-SOURCE-VERIFICATION/V1"
_SHA3_512: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{128}\Z")
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._:/?#=&%-]{0,511}\Z"
)


class RegulatorySourceVerificationError(ValueError):
    """Reject malformed verification inputs without retaining source content.

    This error owns no tenant, authentication, regulator, registry, transaction,
    professional-practice, operational-access, reassignment, or financial authority.
    """

    def __init__(self, code: str) -> None:
        """Create one stable content-free failure code."""
        self.code = code
        super().__init__(code)


class RegulatorySourceState(StrEnum):
    """Classify source evidence without collapsing observation into authority."""

    AUTHENTICATED_RESPONSE = "AUTHENTICATED_RESPONSE"
    HUMAN_OBSERVED_PUBLIC_RECORD = "HUMAN_OBSERVED_PUBLIC_RECORD"
    UNVERIFIED_SUBMISSION = "UNVERIFIED_SUBMISSION"
    STALE_RESPONSE = "STALE_RESPONSE"
    DISPUTED_EVIDENCE = "DISPUTED_EVIDENCE"
    UNAVAILABLE_SOURCE = "UNAVAILABLE_SOURCE"


class IssuerVerificationState(StrEnum):
    """Describe authentication provenance for the asserted external issuer."""

    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    HUMAN_OBSERVATION_ONLY = "HUMAN_OBSERVATION_ONLY"
    TRANSPORT_ONLY = "TRANSPORT_ONLY"
    CRYPTOGRAPHICALLY_VERIFIED = "CRYPTOGRAPHICALLY_VERIFIED"
    REVOKED = "REVOKED"


class RegulatoryVerificationReason(StrEnum):
    """Expose bounded outcomes for non-ingesting caller handling and audit."""

    ACTOR_INACTIVE = "ACTOR_INACTIVE"
    ACTOR_SCOPE_MISMATCH = "ACTOR_SCOPE_MISMATCH"
    CAPTURE_TAMPERED = "CAPTURE_TAMPERED"
    SOURCE_IMPERSONATION = "SOURCE_IMPERSONATION"
    SELF_ATTESTATION = "SELF_ATTESTATION"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    SOURCE_DISPUTED = "SOURCE_DISPUTED"
    SOURCE_UNVERIFIED = "SOURCE_UNVERIFIED"
    ISSUER_VERIFICATION_REVOKED = "ISSUER_VERIFICATION_REVOKED"
    AUTHENTICATED_ISSUER_TRUST_ROOT_UNAVAILABLE = (
        "AUTHENTICATED_ISSUER_TRUST_ROOT_UNAVAILABLE"
    )
    FRESHNESS_POLICY_UNKNOWN = "FRESHNESS_POLICY_UNKNOWN"
    EVIDENCE_STALE = "EVIDENCE_STALE"
    FFC_SOURCE_VALIDITY_REQUIRED = "FFC_SOURCE_VALIDITY_REQUIRED"
    FFC_SOURCE_VALIDITY_EXPIRED = "FFC_SOURCE_VALIDITY_EXPIRED"
    R63_INGESTION_PERMISSION_UNAVAILABLE = "R63_INGESTION_PERMISSION_UNAVAILABLE"


def _identifier(name: str, value: object) -> str:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise RegulatorySourceVerificationError(f"R64_{name.upper()}_INVALID")
    if name == "tenant_id" and value.casefold() in {"default", "global", "root", "*"}:
        raise RegulatorySourceVerificationError("R64_TENANT_ID_INVALID")
    return value


def _instant(name: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise RegulatorySourceVerificationError(f"R64_{name.upper()}_INVALID")
    result = value.astimezone(timezone.utc)
    if result != value or result.microsecond:
        raise RegulatorySourceVerificationError(f"R64_{name.upper()}_NONCANONICAL")
    return result


def _duration(name: str, value: object) -> timedelta | None:
    if value is None:
        return None
    if type(value) is not timedelta or value <= timedelta(0):
        raise RegulatorySourceVerificationError(f"R64_{name.upper()}_INVALID")
    if value.microseconds:
        raise RegulatorySourceVerificationError(f"R64_{name.upper()}_NONCANONICAL")
    return value


def _digest(name: str, value: object) -> str:
    if type(value) is not str or _SHA3_512.fullmatch(value) is None:
        raise RegulatorySourceVerificationError(f"R64_{name.upper()}_INVALID")
    return value


def _canonical_digest(material: dict[str, object]) -> str:
    def encode(value: object) -> object:
        if isinstance(value, StrEnum):
            return value.value
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, timedelta):
            return int(value.total_seconds())
        return value

    payload = json.dumps(
        {key: encode(value) for key, value in material.items()},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return sha3_512(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class RegulatoryFreshnessPolicy:
    """Define explicit local observation ages without inventing regulator validity.

    ``practising_status_max_age`` and ``ffc_capture_max_age`` are separately
    governed Wilsy observation-age requirements. ``None`` means no approved
    policy exists and therefore fails closed. An FFC additionally requires an
    independently captured source-record validity instant; this class never
    derives that instant from an annual renewal statement or calendar year.
    """

    policy_id: str
    practising_status_max_age: timedelta | None
    ffc_capture_max_age: timedelta | None

    def __post_init__(self) -> None:
        """Validate a named, second-granularity and strictly positive policy."""
        object.__setattr__(self, "policy_id", _identifier("policy_id", self.policy_id))
        object.__setattr__(
            self,
            "practising_status_max_age",
            _duration("practising_status_max_age", self.practising_status_max_age),
        )
        object.__setattr__(
            self,
            "ffc_capture_max_age",
            _duration("ffc_capture_max_age", self.ffc_capture_max_age),
        )

    def max_age_for(self, kind: ProfessionalEvidenceKind) -> timedelta | None:
        """Return the distinct approved observation-age requirement for a kind."""
        if kind is ProfessionalEvidenceKind.PRACTISING_STATUS:
            return self.practising_status_max_age
        return self.ffc_capture_max_age


@dataclass(frozen=True, slots=True)
class RegulatorySourceCapture:
    """Carry one transient source capture and its provenance into verification.

    Raw bytes are accepted only so this boundary can independently recompute the
    SHA3-512 digest; they are never returned or persisted. Source state records
    what the adapter actually established. A self-submitted document cannot be
    relabelled as a human-observed or authenticated regulator response.
    """

    tenant_id: str
    actor_principal_id: str
    submitted_by_principal_id: str
    subject_id: str
    jurisdiction: str
    evidence_kind: ProfessionalEvidenceKind | str
    issuer_source_id: str
    source_uri: str
    checked_at: datetime
    source_state: RegulatorySourceState | str
    issuer_verification_state: IssuerVerificationState | str
    issuer_verification_reference: str
    capture_digest: str
    captured_payload: bytes
    source_record_valid_until: datetime | None = None
    conflicting_capture_digest: str | None = None

    def __post_init__(self) -> None:
        """Canonicalize metadata while retaining capture bytes only transiently."""
        for name in (
            "tenant_id",
            "actor_principal_id",
            "submitted_by_principal_id",
            "subject_id",
            "issuer_source_id",
            "source_uri",
            "issuer_verification_reference",
        ):
            object.__setattr__(self, name, _identifier(name, getattr(self, name)))
        if self.jurisdiction != "ZA":
            raise RegulatorySourceVerificationError("R64_JURISDICTION_UNSUPPORTED")
        try:
            kind = ProfessionalEvidenceKind(self.evidence_kind)
            source_state = RegulatorySourceState(self.source_state)
            verification = IssuerVerificationState(self.issuer_verification_state)
        except (TypeError, ValueError) as error:
            raise RegulatorySourceVerificationError("R64_SOURCE_ENUM_INVALID") from error
        object.__setattr__(self, "evidence_kind", kind)
        object.__setattr__(self, "source_state", source_state)
        object.__setattr__(self, "issuer_verification_state", verification)
        object.__setattr__(self, "checked_at", _instant("checked_at", self.checked_at))
        if type(self.captured_payload) is not bytes or not self.captured_payload:
            raise RegulatorySourceVerificationError("R64_CAPTURE_PAYLOAD_INVALID")
        object.__setattr__(self, "capture_digest", _digest("capture_digest", self.capture_digest))
        if self.source_record_valid_until is not None:
            object.__setattr__(
                self,
                "source_record_valid_until",
                _instant("source_record_valid_until", self.source_record_valid_until),
            )
        if self.conflicting_capture_digest is not None:
            object.__setattr__(
                self,
                "conflicting_capture_digest",
                _digest("conflicting_capture_digest", self.conflicting_capture_digest),
            )


@runtime_checkable
class RegulatorySourceVerificationAdapter(Protocol):
    """Define a transport-neutral source adapter with no persistence authority.

    Implementations may fetch or receive source material, but must report the
    strongest state they independently established. Conformance to this
    protocol does not authenticate an issuer; a governed trust root is still
    required before ``AUTHENTICATED_RESPONSE`` can support ingestion.
    """

    def capture(self) -> RegulatorySourceCapture:
        """Return one bounded capture or an explicit unavailable-source capture."""
        ...


@dataclass(frozen=True, slots=True, init=False)
class RegulatoryVerificationDecision:
    """Return an internally issued decision that permanently denies authority.

    Direct construction is forbidden and ``dataclasses.replace`` therefore
    cannot manufacture a decision. The verifier creates instances only after
    evaluating all fail-closed gates. No authority-shaped mutable field exists:
    ingestion, operational access, professional practice, and reassignment are
    unconditional false properties. The replay identity binds source, subject,
    time, digest, provenance, freshness policy and the R62 evidence fingerprint.
    """

    schema: str
    version: str
    tenant_id: str
    actor_principal_id: str
    practitioner_principal_id: str
    verified_subject_id: str
    evidence_kind: ProfessionalEvidenceKind
    source_state: RegulatorySourceState
    issuer_verification_state: IssuerVerificationState
    checked_at: datetime
    capture_digest: str
    evidence_fingerprint: str
    freshness_policy_id: str
    reason: RegulatoryVerificationReason
    replay_identity: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Reject direct or ``dataclasses.replace`` authority fabrication."""
        del args, kwargs
        raise RegulatorySourceVerificationError(
            "R64_VERIFICATION_DECISION_DIRECT_CONSTRUCTION_FORBIDDEN"
        )

    @property
    def ingestion_authorized(self) -> bool:
        """Never authorize persistence from this non-ingesting capability."""
        return False

    @property
    def permits_operational_access(self) -> bool:
        """Never grant operational or matter access from regulatory evidence."""
        return False

    @property
    def permits_professional_practice(self) -> bool:
        """Never convert a verification decision into a practice grant."""
        return False

    @property
    def permits_reassignment_execution(self) -> bool:
        """Never create or widen reassignment execution authority."""
        return False


def _decision(**values: object) -> RegulatoryVerificationDecision:
    """Issue one closed-shape decision without exposing a construction token."""
    expected = {item.name for item in fields(RegulatoryVerificationDecision)}
    if set(values) != expected:
        raise RegulatorySourceVerificationError("R64_DECISION_SHAPE_INVALID")
    decision = object.__new__(RegulatoryVerificationDecision)
    for name, value in values.items():
        object.__setattr__(decision, name, value)
    return decision


def verify_regulatory_source(
    *,
    evidence: Evidence,
    capture: RegulatorySourceCapture,
    actor_authority: PrincipalAuthority,
    policy: RegulatoryFreshnessPolicy,
    evaluated_at: datetime,
) -> RegulatoryVerificationDecision:
    """Verify an R62 submission and return a typed non-ingesting R64 decision.

    The function independently rehydrates R62 evidence, checks the exact R63
    canonical source identity for its kind, recomputes the capture digest,
    rejects self-attestation and conflicts, evaluates kind-specific freshness,
    and requires an ACTIVE exact actor. It deliberately cannot persist: no
    authenticated LPC trust root or dedicated regulatory-ingestion permission
    exists in the repository at R64, so even a cryptographically described
    response returns an explicit authority-denied reason.

    Args:
        evidence: Existing immutable R62 documentary evidence.
        capture: Transient adapter output whose bytes are digest-verified here.
        actor_authority: Canonical current principal lifecycle snapshot.
        policy: Explicit per-kind Wilsy observation freshness policy.
        evaluated_at: Canonical UTC decision instant.

    Returns:
        A deterministic decision carrying no raw content and no ingest grant.

    Raises:
        RegulatorySourceVerificationError: If structural inputs are malformed
            or R62 evidence fails immutable rehydration.
    """
    if type(evidence) is not Evidence:
        raise RegulatorySourceVerificationError("R64_R62_EVIDENCE_REQUIRED")
    try:
        canonical_evidence = replace(evidence)
    except Exception as error:
        raise RegulatorySourceVerificationError("R64_R62_EVIDENCE_CORRUPT") from error
    if not hmac.compare_digest(canonical_evidence.fingerprint, evidence.fingerprint):
        raise RegulatorySourceVerificationError("R64_R62_EVIDENCE_CORRUPT")
    if type(capture) is not RegulatorySourceCapture:
        raise RegulatorySourceVerificationError("R64_SOURCE_CAPTURE_REQUIRED")
    if type(actor_authority) is not PrincipalAuthority:
        raise RegulatorySourceVerificationError("R64_ACTOR_AUTHORITY_REQUIRED")
    if type(policy) is not RegulatoryFreshnessPolicy:
        raise RegulatorySourceVerificationError("R64_FRESHNESS_POLICY_REQUIRED")
    at = _instant("evaluated_at", evaluated_at)
    kind = ProfessionalEvidenceKind(canonical_evidence.evidence_kind)

    reason = RegulatoryVerificationReason.R63_INGESTION_PERMISSION_UNAVAILABLE
    observed_state = RegulatorySourceState(capture.source_state)
    issuer_verification_state = IssuerVerificationState(
        capture.issuer_verification_state
    )
    calculated_digest = sha3_512(capture.captured_payload).hexdigest()
    expected_source = AUTHORITATIVE_PUBLIC_SOURCES[kind]

    if actor_authority.status is not PrincipalStatus.ACTIVE:
        reason = RegulatoryVerificationReason.ACTOR_INACTIVE
    elif (
        actor_authority.principal_id != capture.actor_principal_id
        or capture.tenant_id != canonical_evidence.tenant_id
        or capture.subject_id != canonical_evidence.verified_subject_id
        or capture.jurisdiction != canonical_evidence.jurisdiction
        or capture.evidence_kind is not kind
        or canonical_evidence.practitioner_principal_id
        != canonical_evidence.practitioner_principal_id.strip()
    ):
        reason = RegulatoryVerificationReason.ACTOR_SCOPE_MISMATCH
    elif not hmac.compare_digest(calculated_digest, capture.capture_digest):
        reason = RegulatoryVerificationReason.CAPTURE_TAMPERED
    elif (
        capture.issuer_source_id != expected_source[0]
        or capture.source_uri != expected_source[1]
        or canonical_evidence.issuer_source_id != expected_source[0]
        or canonical_evidence.source_uri != expected_source[1]
    ):
        reason = RegulatoryVerificationReason.SOURCE_IMPERSONATION
    elif (
        canonical_evidence.verification_method
        is ProfessionalEvidenceMethod.ATTESTED_DOCUMENT_REVIEW
        or capture.submitted_by_principal_id
        == canonical_evidence.practitioner_principal_id
        and observed_state
        in {
            RegulatorySourceState.UNVERIFIED_SUBMISSION,
            RegulatorySourceState.HUMAN_OBSERVED_PUBLIC_RECORD,
        }
    ):
        reason = RegulatoryVerificationReason.SELF_ATTESTATION
    elif observed_state is RegulatorySourceState.UNAVAILABLE_SOURCE:
        reason = RegulatoryVerificationReason.SOURCE_UNAVAILABLE
    elif (
        observed_state is RegulatorySourceState.DISPUTED_EVIDENCE
        or capture.conflicting_capture_digest is not None
        and not hmac.compare_digest(
            capture.conflicting_capture_digest, capture.capture_digest
        )
    ):
        reason = RegulatoryVerificationReason.SOURCE_DISPUTED
    elif observed_state is RegulatorySourceState.UNVERIFIED_SUBMISSION:
        reason = RegulatoryVerificationReason.SOURCE_UNVERIFIED
    elif observed_state is RegulatorySourceState.STALE_RESPONSE:
        reason = RegulatoryVerificationReason.EVIDENCE_STALE
    elif issuer_verification_state is IssuerVerificationState.REVOKED:
        reason = RegulatoryVerificationReason.ISSUER_VERIFICATION_REVOKED
    else:
        max_age = policy.max_age_for(kind)
        if max_age is None:
            reason = RegulatoryVerificationReason.FRESHNESS_POLICY_UNKNOWN
        elif capture.checked_at > at or at - capture.checked_at > max_age:
            reason = RegulatoryVerificationReason.EVIDENCE_STALE
            observed_state = RegulatorySourceState.STALE_RESPONSE
        elif kind is ProfessionalEvidenceKind.FIDELITY_FUND_CERTIFICATE_STATUS:
            if capture.source_record_valid_until is None:
                reason = RegulatoryVerificationReason.FFC_SOURCE_VALIDITY_REQUIRED
            elif at >= capture.source_record_valid_until:
                reason = RegulatoryVerificationReason.FFC_SOURCE_VALIDITY_EXPIRED
        if reason is RegulatoryVerificationReason.R63_INGESTION_PERMISSION_UNAVAILABLE:
            if (
                observed_state is RegulatorySourceState.AUTHENTICATED_RESPONSE
                or issuer_verification_state
                is IssuerVerificationState.CRYPTOGRAPHICALLY_VERIFIED
            ):
                reason = (
                    RegulatoryVerificationReason
                    .AUTHENTICATED_ISSUER_TRUST_ROOT_UNAVAILABLE
                )

    replay_identity = _canonical_digest(
        {
            "schema": SCHEMA,
            "version": VERSION,
            "tenant_id": canonical_evidence.tenant_id,
            "actor_principal_id": capture.actor_principal_id,
            "practitioner_principal_id": (
                canonical_evidence.practitioner_principal_id
            ),
            "verified_subject_id": canonical_evidence.verified_subject_id,
            "evidence_kind": kind,
            "issuer_source_id": capture.issuer_source_id,
            "source_uri": capture.source_uri,
            "checked_at": capture.checked_at,
            "capture_digest": capture.capture_digest,
            "issuer_verification_state": issuer_verification_state,
            "issuer_verification_reference": (
                capture.issuer_verification_reference
            ),
            "source_record_valid_until": capture.source_record_valid_until,
            "evidence_fingerprint": canonical_evidence.fingerprint,
            "freshness_policy_id": policy.policy_id,
        }
    )
    return _decision(
        schema=SCHEMA,
        version=VERSION,
        tenant_id=canonical_evidence.tenant_id,
        actor_principal_id=capture.actor_principal_id,
        practitioner_principal_id=canonical_evidence.practitioner_principal_id,
        verified_subject_id=canonical_evidence.verified_subject_id,
        evidence_kind=kind,
        source_state=observed_state,
        issuer_verification_state=issuer_verification_state,
        checked_at=capture.checked_at,
        capture_digest=capture.capture_digest,
        evidence_fingerprint=canonical_evidence.fingerprint,
        freshness_policy_id=policy.policy_id,
        reason=reason,
        replay_identity=replay_identity,
    )


__all__ = [
    "VERSION",
    "SCHEMA",
    "RegulatorySourceVerificationError",
    "RegulatorySourceState",
    "IssuerVerificationState",
    "RegulatoryVerificationReason",
    "RegulatoryFreshnessPolicy",
    "RegulatorySourceCapture",
    "RegulatorySourceVerificationAdapter",
    "RegulatoryVerificationDecision",
    "verify_regulatory_source",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: regulatory_source_verification.py
# VERSION: v1.0.1-R64-AUTHENTICATED-REGULATORY-VERIFICATION
# AUTHORITY BOUNDARY: non-ingesting source verification and typed denial only
# TENANT POSTURE: exact tenant evidence/capture scope; no registry disclosure
# FAIL-CLOSED POSTURE: malformed, forged, self-attested, stale, disputed,
# unavailable, revoked, cross-scope, unknown-policy or unauthorised input denies
# PROFESSIONAL PRACTICE / MATTER ACCESS / REASSIGNMENT AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
