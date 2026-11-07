"""Institutional signer evidence verifier contract.

Caller-supplied references are lookup coordinates only. A successful result may
be issued only by a separately approved adapter that resolves identity proofing,
signatory mandate and approval attestation against authoritative sources.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Final, Protocol, runtime_checkable

VERSION: Final[str] = "v1.0.0-INSTITUTIONAL-SIGNER-EVIDENCE-VERIFIER-CONTRACT"
TENANT_ID: Final[str] = "WILSYTENANT-4CD2FZ4O"
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}\\Z")


class InstitutionalSignerEvidenceVerificationError(RuntimeError):
    """Bounded fail-closed evidence verification denial."""
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _identifier(name: str, value: object) -> str:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise InstitutionalSignerEvidenceVerificationError(
            f"INSTITUTIONAL_SIGNER_{name.upper()}_INVALID"
        )
    return value


def _instant(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise InstitutionalSignerEvidenceVerificationError(
            "INSTITUTIONAL_SIGNER_EVALUATED_AT_INVALID"
        )
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class InstitutionalSignerEvidenceVerificationRequest:
    """Exact scope for one evidence verification; references are not proof."""
    tenant_id: str
    certificate_fingerprint_sha256: str
    subject_principal_id: str
    evidence_reference: str
    evidence_kind: str
    evaluated_at: datetime

    def __post_init__(self) -> None:
        if self.tenant_id != TENANT_ID:
            raise InstitutionalSignerEvidenceVerificationError(
                "INSTITUTIONAL_SIGNER_TENANT_SCOPE_INVALID"
            )
        for field in (
            "certificate_fingerprint_sha256", "subject_principal_id",
            "evidence_reference", "evidence_kind",
        ):
            _identifier(field, getattr(self, field))
        if not re.fullmatch(r"[0-9a-f]{64}", self.certificate_fingerprint_sha256):
            raise InstitutionalSignerEvidenceVerificationError(
                "INSTITUTIONAL_SIGNER_CERTIFICATE_FINGERPRINT_INVALID"
            )
        object.__setattr__(self, "evaluated_at", _instant(self.evaluated_at))


@runtime_checkable
class VerifiedInstitutionalEvidenceRecord(Protocol):
    """Fields an authoritative source adapter must return after verification."""
    tenant_id: str
    evidence_reference: str
    evidence_fingerprint_sha256: str
    source_system_id: str
    source_record_id: str
    source_revision: str
    status: str
    valid_from: datetime
    valid_until: datetime | None
    revoked: bool
    verified_at: datetime


@runtime_checkable
class VerifiedSignerIdentityProofing(VerifiedInstitutionalEvidenceRecord, Protocol):
    """Identity proofing bound to the exact principal and certificate."""
    subject_principal_id: str
    certificate_fingerprint_sha256: str
    identity_assurance_level: str


@runtime_checkable
class VerifiedSignerMandate(VerifiedInstitutionalEvidenceRecord, Protocol):
    """Institutional signatory mandate for the exact principal and certificate."""
    subject_principal_id: str
    certificate_fingerprint_sha256: str
    legal_entity_reference: str
    mandate_scope: str


@runtime_checkable
class VerifiedSignerApprovalAttestation(VerifiedInstitutionalEvidenceRecord, Protocol):
    """Approval attestation bound to an independent reviewer and enrollment."""
    reviewer_principal_id: str
    certificate_fingerprint_sha256: str
    enrollment_requester_principal_id: str
    approval_scope: str


@dataclass(frozen=True, slots=True, init=False)
class VerifiedInstitutionalSignerEvidence:
    """Opaque result; public construction is disabled until adapter approval."""
    request: InstitutionalSignerEvidenceVerificationRequest
    identity_proofing: VerifiedSignerIdentityProofing
    signatory_mandate: VerifiedSignerMandate
    provenance_fingerprint_sha256: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        del args, kwargs
        raise InstitutionalSignerEvidenceVerificationError(
            "INSTITUTIONAL_SIGNER_EVIDENCE_AUTHORITY_UNAVAILABLE"
        )


@runtime_checkable
class InstitutionalSignerEvidenceVerifier(Protocol):
    """Read-only authoritative verifier; never creates signer or IAM authority."""
    def verify_enrollment(
        self, *, tenant_id: str, certificate_fingerprint_sha256: str,
        subject_principal_id: str, identity_proofing_reference: str,
        signatory_mandate_reference: str, evaluated_at: datetime,
        session: object,
    ) -> VerifiedInstitutionalSignerEvidence:
        """Verify both source records, exact cross-bindings and currentness."""
        ...

    def verify_approval(
        self, *, tenant_id: str, certificate_fingerprint_sha256: str,
        enrollment_requester_principal_id: str, reviewer_principal_id: str,
        approval_attestation_reference: str, evaluated_at: datetime,
        session: object,
    ) -> VerifiedSignerApprovalAttestation:
        """Verify authoritative approval and enforce reviewer/requester separation."""
        ...


class UnavailableInstitutionalSignerEvidenceVerifier:
    """Default-deny adapter until governance selects authoritative sources."""
    def verify_enrollment(self, **_kwargs: object) -> VerifiedInstitutionalSignerEvidence:
        raise InstitutionalSignerEvidenceVerificationError(
            "INSTITUTIONAL_SIGNER_EVIDENCE_AUTHORITY_UNAVAILABLE"
        )

    def verify_approval(self, **_kwargs: object) -> VerifiedSignerApprovalAttestation:
        raise InstitutionalSignerEvidenceVerificationError(
            "INSTITUTIONAL_SIGNER_EVIDENCE_AUTHORITY_UNAVAILABLE"
        )


__all__ = [
    "VERSION", "TENANT_ID",
    "InstitutionalSignerEvidenceVerificationError",
    "InstitutionalSignerEvidenceVerificationRequest",
    "InstitutionalSignerEvidenceVerifier",
    "UnavailableInstitutionalSignerEvidenceVerifier",
    "VerifiedInstitutionalSignerEvidence",
    "VerifiedInstitutionalEvidenceRecord",
    "VerifiedSignerIdentityProofing",
    "VerifiedSignerMandate",
    "VerifiedSignerApprovalAttestation",
]
