"""Governed source-adapter contracts for institutional signer evidence.

This module defines the boundary between external authorities and the EOS
institutional signer verifier. Provider responses are untrusted until an
independent source-response authenticator validates their origin and integrity.
No concrete provider or positive verifier is configured here.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import json
import re
from typing import Final, Mapping, Protocol, runtime_checkable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

TENANT_ID: Final[str] = "WILSYTENANT-4CD2FZ4O"
EVIDENCE_KINDS: Final[frozenset[str]] = frozenset({
    "IDENTITY_PROOFING",
    "SIGNATORY_MANDATE",
    "INDEPENDENT_APPROVAL",
})
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}\Z")
_FINGERPRINT = re.compile(r"[0-9a-f]{64}\Z")


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
        try:
            signature = base64.b64decode(self.response_signature_base64, validate=True)
        except (ValueError, TypeError):
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_SIGNATURE_ENCODING_INVALID"
            ) from None
        if len(signature) != 64:
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_SIGNATURE_LENGTH_INVALID"
            )
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
    response_signing_key_id: str
    response_signature_base64: str
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
            "response_signing_key_id",
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


def _canonical_source_response_payload(
    response: InstitutionalSignerSourceEvidence,
) -> bytes:
    """Canonical bytes signed by an institutional source response key."""
    payload = {
        "authority_scope": response.authority_scope,
        "certificate_fingerprint_sha256": response.certificate_fingerprint_sha256,
        "evidence_fingerprint_sha256": response.evidence_fingerprint_sha256,
        "evidence_kind": response.evidence_kind,
        "evidence_reference": response.evidence_reference,
        "enrollment_requester_principal_id": response.enrollment_requester_principal_id,
        "legal_entity_reference": response.legal_entity_reference,
        "observed_at": response.observed_at.isoformat(),
        "response_signature_reference": response.response_signature_reference,
        "response_signing_key_id": response.response_signing_key_id,
        "reviewer_principal_id": response.reviewer_principal_id,
        "revoked": response.revoked,
        "source_record_id": response.source_record_id,
        "source_revision": response.source_revision,
        "source_system_id": response.source_system_id,
        "status": response.status,
        "subject_principal_id": response.subject_principal_id,
        "tenant_id": response.tenant_id,
        "valid_from": response.valid_from.isoformat(),
        "valid_until": response.valid_until.isoformat() if response.valid_until else None,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


class Ed25519InstitutionalSignerSourceResponseAuthenticator:
    """Verify source responses against explicitly pinned, source-bound Ed25519 keys.

    Key provisioning, rotation and revocation are external governance responsibilities.
    Empty trust configuration denies every response.
    """

    def __init__(self, trusted_public_keys: Mapping[tuple[str, str], bytes]) -> None:
        self._trusted_public_keys: dict[tuple[str, str], Ed25519PublicKey] = {}
        for (source_system_id, key_id), raw_key in trusted_public_keys.items():
            source_id = _identifier("source_system_id", source_system_id)
            trusted_key_id = _identifier("response_signing_key_id", key_id)
            if type(raw_key) is not bytes or len(raw_key) != 32:
                raise InstitutionalSignerSourceAdapterError(
                    "INSTITUTIONAL_SIGNER_SOURCE_TRUSTED_KEY_INVALID"
                )
            self._trusted_public_keys[(source_id, trusted_key_id)] = Ed25519PublicKey.from_public_bytes(raw_key)

    def authenticate_response(
        self, *, expected_source_system_id: str,
        lookup: InstitutionalSignerSourceLookup,
        response: InstitutionalSignerSourceEvidence,
    ) -> None:
        del lookup  # Exact request/response field binding is enforced by the caller.
        key = self._trusted_public_keys.get((expected_source_system_id, response.response_signing_key_id))
        if key is None or response.source_system_id != expected_source_system_id:
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_SIGNING_KEY_UNTRUSTED"
            )
        try:
            key.verify(base64.b64decode(response.response_signature_base64, validate=True), _canonical_source_response_payload(response))
        except (InvalidSignature, ValueError):
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_RESPONSE_SIGNATURE_INVALID"
            ) from None


def read_authenticated_source_evidence(
    *,
    adapter: InstitutionalSignerEvidenceSourceAdapter,
    authenticator: InstitutionalSignerSourceResponseAuthenticator,
    lookup: InstitutionalSignerSourceLookup,
) -> InstitutionalSignerSourceEvidence:
    """Read one source record and authenticate its response and exact scope.

    Negative status/revocation/expiry are intentionally returned intact so the
    verifier can persist a NOT_CURRENT observation. This function authenticates
    origin and binding; it does not turn a source response into legal authority.
    """
    expected_kind = lookup.evidence_kind
    source_system_id = _identifier("source_system_id", adapter.source_system_id)
    if adapter.supported_evidence_kind != expected_kind:
        raise InstitutionalSignerSourceAdapterError(
            "INSTITUTIONAL_SIGNER_SOURCE_ADAPTER_EVIDENCE_KIND_MISMATCH"
        )
    response = adapter.read_evidence(lookup=lookup)
    if type(response) is not InstitutionalSignerSourceEvidence:
        raise InstitutionalSignerSourceAdapterError(
            "INSTITUTIONAL_SIGNER_SOURCE_RESPONSE_TYPE_INVALID"
        )
    authenticator.authenticate_response(
        expected_source_system_id=source_system_id,
        lookup=lookup,
        response=response,
    )
    if response.source_system_id != source_system_id:
        raise InstitutionalSignerSourceAdapterError(
            "INSTITUTIONAL_SIGNER_SOURCE_SYSTEM_MISMATCH"
        )
    expected_bindings = {
        "evidence_kind": lookup.evidence_kind,
        "evidence_reference": lookup.evidence_reference,
        "tenant_id": lookup.tenant_id,
        "subject_principal_id": lookup.subject_principal_id,
        "certificate_fingerprint_sha256": lookup.certificate_fingerprint_sha256,
        "legal_entity_reference": lookup.legal_entity_reference,
        "enrollment_requester_principal_id": lookup.enrollment_requester_principal_id,
        "reviewer_principal_id": lookup.reviewer_principal_id,
        "authority_scope": lookup.required_scope,
    }
    for field, expected in expected_bindings.items():
        if getattr(response, field) != expected:
            raise InstitutionalSignerSourceAdapterError(
                f"INSTITUTIONAL_SIGNER_SOURCE_{field.upper()}_MISMATCH"
            )
    return response


class AuthenticatedInstitutionalSignerSourceAdapterSet:
    """Compose three separately configured, authenticated read-only source adapters.

    This returns untrusted source envelopes after cryptographic origin and exact
    scope checks. It does not construct any opaque verifier-issued success result.
    """

    def __init__(
        self, *,
        identity_proofing: InstitutionalSignerEvidenceSourceAdapter,
        signatory_mandate: InstitutionalSignerEvidenceSourceAdapter,
        independent_approval: InstitutionalSignerEvidenceSourceAdapter,
        authenticator: InstitutionalSignerSourceResponseAuthenticator,
    ) -> None:
        adapters = {
            "IDENTITY_PROOFING": identity_proofing,
            "SIGNATORY_MANDATE": signatory_mandate,
            "INDEPENDENT_APPROVAL": independent_approval,
        }
        if len({id(adapter) for adapter in adapters.values()}) != len(adapters):
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_ADAPTERS_MUST_BE_DISTINCT"
            )
        for kind, adapter in adapters.items():
            if adapter.supported_evidence_kind != kind:
                raise InstitutionalSignerSourceAdapterError(
                    "INSTITUTIONAL_SIGNER_SOURCE_ADAPTER_EVIDENCE_KIND_MISMATCH"
                )
        self._adapters = adapters
        self._authenticator = authenticator

    def _read(self, *, kind: str, lookup: InstitutionalSignerSourceLookup) -> InstitutionalSignerSourceEvidence:
        if lookup.evidence_kind != kind:
            raise InstitutionalSignerSourceAdapterError(
                "INSTITUTIONAL_SIGNER_SOURCE_EVIDENCE_KIND_INVALID"
            )
        return read_authenticated_source_evidence(
            adapter=self._adapters[kind], authenticator=self._authenticator, lookup=lookup
        )

    def read_identity_proofing(self, *, lookup: InstitutionalSignerSourceLookup) -> InstitutionalSignerSourceEvidence:
        return self._read(kind="IDENTITY_PROOFING", lookup=lookup)

    def read_signatory_mandate(self, *, lookup: InstitutionalSignerSourceLookup) -> InstitutionalSignerSourceEvidence:
        return self._read(kind="SIGNATORY_MANDATE", lookup=lookup)

    def read_independent_approval(self, *, lookup: InstitutionalSignerSourceLookup) -> InstitutionalSignerSourceEvidence:
        return self._read(kind="INDEPENDENT_APPROVAL", lookup=lookup)


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
    "Ed25519InstitutionalSignerSourceResponseAuthenticator",
    "InstitutionalSignerSourceAdapterSet",
    "UnavailableInstitutionalSignerSourceAdapterSet",
    "AuthenticatedInstitutionalSignerSourceAdapterSet",
    "read_authenticated_source_evidence",
]
