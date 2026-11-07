"""Governed source-adapter contracts for institutional signer evidence.

This module defines the boundary between external authorities and the EOS
institutional signer verifier. Provider responses are untrusted until an
independent source-response authenticator validates their origin and integrity.
No concrete provider or positive verifier is configured here.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Final, Protocol, runtime_checkable

TENANT_ID: Final[str] = "WILSYTENANT-4CD2FZ4O"
EVIDENCE_KINDS: Final[frozenset[str]] = frozenset({
    "IDENTITY_PROOFING",
    "SIGNATORY_MANDATE",
    "INDEPENDENT_APPROVAL",
})
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}\\Z")
_FINGERPRINT = re.compile(r"[0-9a-f]{64}\\Z")


class InstitutionalSignerSourceAdapterError(RuntimeError):
    """Fail-closed adapter boundary error with a stable machine code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _identifier(field: str, value: object) -> str:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise InstitutionalSignerSourceAdapterError(
            f"INSTITUTIONAL_SIGNER_SOURCE_{field.upper()}_INVALID"
        )
    return value


def _instant(field: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise InstitutionalSignerSourceAdapterError(
            f"INSTITUTIONAL_SIGNER_SOURCE_{field.upper()}_INVALID"
        )
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class InstitutionalSignerSourceLookup:
    """Exact, least-privilege lookup scope; references are not evidence."""

    tenant_id: str
    evidence_kind: str
    evidence_reference: str
    subject_principal_id: str
    certificate_fingerprint_sha256: str
    evaluated_at: datetime
    legal_entity_reference: str | None = None
    enrollment_requester_principal_id: str | None = None
    reviewer_principal_id: str | None = None
    required_scope: str | None = None

    def __post_init__(self) -> None:
        if self.tenant_id != TENANT_ID:
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_TENANT_SCOPE_INVALID"
            )
        if self.evidence_kind not in EVIDENCE_KINDS:
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_EVIDENCE_KIND_INVALID"
            )
        for name in ("evidence_reference", "subject_principal_id"):
            _identifier(name, getattr(self, name))
        if type(self.certificate_fingerprint_sha256) is not str or not _FINGERPRINT.fullmatch(
            self.certificate_fingerprint_sha256
        ):
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_CERTIFICATE_FINGERPRINT_INVALID"
            )
        for name in (
            "legal_entity_reference", "enrollment_requester_principal_id",
            "reviewer_principal_id", "required_scope",
        ):
            value = getattr(self, name)
            if value is not None:
                _identifier(name, value)
        object.__setattr__(self, "evaluated_at", _instant("evaluated_at", self.evaluated_at))


@dataclass(frozen=True, slots=True)
class InstitutionalSignerSourceEvidence:
    """Untrusted source response envelope; never a verified signer result."""

    evidence_kind: str
    evidence_reference: str
    tenant_id: str
    source_system_id: str
    source_record_id: str
    source_revision: str
    subject_principal_id: str
    certificate_fingerprint_sha256: str
    evidence_fingerprint_sha256: str
    status: str
    valid_from: datetime
    valid_until: datetime | None
    revoked: bool
    observed_at: datetime
    response_signature_reference: str
    legal_entity_reference: str | None = None
    enrollment_requester_principal_id: str | None = None
    reviewer_principal_id: str | None = None
    authority_scope: str | None = None

    def __post_init__(self) -> None:
        if self.evidence_kind not in EVIDENCE_KINDS:
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_EVIDENCE_KIND_INVALID"
            )
        for name in (
            "evidence_reference", "source_system_id", "source_record_id",
            "source_revision", "subject_principal_id", "response_signature_reference",
        ):
            _identifier(name, getattr(self, name))
        if self.tenant_id != TENANT_ID:
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_TENANT_SCOPE_INVALID"
            )
        for name in ("certificate_fingerprint_sha256", "evidence_fingerprint_sha256"):
            value = getattr(self, name)
            if type(value) is not str or not _FINGERPRINT.fullmatch(value):
                raise InstitutionalSignerSourceAdapterError(
                    f"INSTITUTIONAL_SIGNER_SOURCE_{name.upper()}_INVALID"
                )
        for name in (
            "legal_entity_reference", "enrollment_requester_principal_id",
            "reviewer_principal_id", "authority_scope",
        ):
            value = getattr(self, name)
            if value is not None:
                _identifier(name, value)
        if type(self.status) is not str or not self.status or len(self.status) > 64:
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_STATUS_INVALID"
            )
        if type(self.revoked) is not bool:
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_REVOCATION_FLAG_INVALID"
            )
        valid_from = _instant("valid_from", self.valid_from)
        valid_until = (
            _instant("valid_until", self.valid_until)
            if self.valid_until is not None else None
        )
        if valid_until is not None and valid_until <= valid_from:
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_VALIDITY_INTERVAL_INVALID"
            )
        object.__setattr__(self, "valid_from", valid_from)
        object.__setattr__(self, "valid_until", valid_until)
        object.__setattr__(self, "observed_at", _instant("observed_at", self.observed_at))


@runtime_checkable
class InstitutionalSignerEvidenceSourceAdapter(Protocol):
    """Read-only provider connector. Implementations must bound I/O and fail closed."""

    source_system_id: str
    supported_evidence_kind: str

    def read_evidence(
        self, *, lookup: InstitutionalSignerSourceLookup
    ) -> InstitutionalSignerSourceEvidence:
        """Read one exact record; must not create or mutate authority records."""
        ...


@runtime_checkable
class InstitutionalSignerSourceResponseAuthenticator(Protocol):
    """Independent trust layer for provider identity, signatures and response binding."""

    def authenticate_response(
        self, *, expected_source_system_id: str,
        lookup: InstitutionalSignerSourceLookup,
        response: InstitutionalSignerSourceEvidence,
    ) -> None:
        """Raise unless source identity, signature and exact lookup scope validate."""
        ...


@runtime_checkable
class InstitutionalSignerSourceAdapterSet(Protocol):
    """Three independently governed evidence channels used by the verifier."""

    def read_identity_proofing(
        self, *, lookup: InstitutionalSignerSourceLookup
    ) -> InstitutionalSignerSourceEvidence: ...

    def read_signatory_mandate(
        self, *, lookup: InstitutionalSignerSourceLookup
    ) -> InstitutionalSignerSourceEvidence: ...

    def read_independent_approval(
        self, *, lookup: InstitutionalSignerSourceLookup
    ) -> InstitutionalSignerSourceEvidence: ...


class UnavailableInstitutionalSignerSourceAdapterSet:
    """Default-deny source set until providers and governance are approved."""

    def _unavailable(self, kind: str) -> InstitutionalSignerSourceEvidence:
        raise InstitutionalSignerSourceAdapterError(
            f"INSTITUTIONAL_SIGNER_SOURCE_{kind}_AUTHORITY_UNAVAILABLE"
        )

    def read_identity_proofing(
        self, *, lookup: InstitutionalSignerSourceLookup
    ) -> InstitutionalSignerSourceEvidence:
        del lookup
        return self._unavailable("IDENTITY_PROOFING")

    def read_signatory_mandate(
        self, *, lookup: InstitutionalSignerSourceLookup
    ) -> InstitutionalSignerSourceEvidence:
        del lookup
        return self._unavailable("SIGNATORY_MANDATE")

    def read_independent_approval(
        self, *, lookup: InstitutionalSignerSourceLookup
    ) -> InstitutionalSignerSourceEvidence:
        del lookup
        return self._unavailable("INDEPENDENT_APPROVAL")


__all__ = [
    "EVIDENCE_KINDS",
    "InstitutionalSignerSourceAdapterError",
    "InstitutionalSignerSourceLookup",
    "InstitutionalSignerSourceEvidence",
    "InstitutionalSignerEvidenceSourceAdapter",
    "InstitutionalSignerSourceResponseAuthenticator",
    "InstitutionalSignerSourceAdapterSet",
    "UnavailableInstitutionalSignerSourceAdapterSet",
]
