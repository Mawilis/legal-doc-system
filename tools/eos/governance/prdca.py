"""Wilsy PRDCA core: signed platform and deployment certificates.

TITLE: Platform Registration and Deployment Certification Authority Core
VERSION: v1.0.1-M11-R8-R3B-P8-P3D-P5-R8-P3KR1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Stateless, fail-closed issuance and verification of signed PRC, DCC,
         deployment-evidence, and descriptor-binding certificate envelopes.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/prdca.py
COLLABORATION / OWNERSHIP: PRDCA governance authority; physical deployment evidence
                            and ledger persistence are separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.1-M11-R8-R3B-P8-P3D-P5-R8-P3KR1 hardens strict base64url
           signature decoding while preserving the injected Ed25519 boundary.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No secrets, clients, network, Mongo, KMS, or provider access.
TENANT BOUNDARY: Platform governance evidence only; no tenant authorization.
AUTHORITY BOUNDARY: Verifies deployment evidence but never creates deployment truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Unknown fields, identifiers, keys, signatures, statuses,
                          campaigns, bindings, and noncanonical bytes reject.
"""
from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import PurePosixPath
from pathlib import Path
import re
import unicodedata
from types import MappingProxyType
from typing import Any, Callable, ClassVar, Mapping, Protocol, Sequence, cast

from tools.eos.saas.billing.tenant_inbound_provider_credential_metadata_source_registry import (
    TenantInboundCredentialMetadataSourceDescriptor,
    TenantInboundCredentialMetadataSourceRegistrationProvenance,
    compute_entry_fingerprint,
)


PRDCA_OWNER = "WILSY_PLATFORM_REGISTRATION_AND_DEPLOYMENT_CERTIFICATION_AUTHORITY"
PRDCA_ALIAS = "WILSY_PRDCA"
SIGNED_ENVELOPE_SCHEMA = "WILSY-PRDCA-SIGNED-ENVELOPE/V1"
PRC_SCHEMA = "WILSY-PLATFORM-REGISTRATION-CERTIFICATE/V1"
DCC_SCHEMA = "WILSY-DEPLOYMENT-CERTIFICATION-CERTIFICATE/V1"
RECEIPT_SCHEMA = "WILSY-PRDCA-DESCRIPTOR-VERIFICATION-RECEIPT/V1"
DEPLOYMENT_EVIDENCE_SCHEMA = "WILSY-AUTHENTICATED-RUNTIME-DEPLOYMENT-EVIDENCE/V1"
DEPLOYMENT_EVIDENCE_ENVELOPE_SCHEMA = (
    "WILSY-AUTHENTICATED-RUNTIME-DEPLOYMENT-EVIDENCE-ENVELOPE/V1"
)
DEPLOYMENT_EVIDENCE_AUTHORITY = "WILSY_AUTHENTICATED_RUNTIME_DEPLOYMENT_EVIDENCE_AUTHORITY"
DEPLOYMENT_EVIDENCE_PRODUCER = "WILSY_AUTHENTICATED_RUNTIME_DEPLOYMENT_EVIDENCE_PRODUCER"
SIGNATURE_ALGORITHM = "Ed25519"
SIGNATURE_ENCODING = "base64url_without_padding"
ID_ALGORITHM = "SHA3-512"
ID_FORMAT = "lowercase_128_hex"
CERTIFICATE_STATUS_ACTIVE = "ACTIVE"
VERIFICATION_STATUS_VERIFIED = "VERIFIED"

_PRDCA_KEY_ID = re.compile(r"^prdca-key:[a-z0-9][a-z0-9._-]{0,63}$")
_DIGEST = re.compile(r"^[0-9a-f]{128}$")
_TOKEN = re.compile(r"^[^\s/\\]{1,256}$")
_IMPLEMENTATION = re.compile(r"^impl:[^\s/\\]{1,240}$")
_ENVELOPE_FIELDS = (
    "envelope_schema",
    "artifact_type",
    "artifact_id",
    "payload_schema",
    "payload",
    "campaign_identity",
    "issuer_authority",
    "authority_key_id",
    "signature_algorithm",
    "signature",
    "issued_at",
    "status",
)
_EVIDENCE_ENVELOPE_FIELDS = (
    "envelope_schema",
    "evidence_type",
    "evidence_id",
    "payload_schema",
    "payload",
    "producer_authority",
    "attestation_key_id",
    "signature_algorithm",
    "signature",
    "status",
)
_PRC_FIELDS = (
    "schema",
    "source_identity",
    "source_contract_version",
    "implementation_identity",
    "capability_class",
    "campaign_identity",
    "issuer_authority",
    "authority_key_id",
)
_DCC_FIELDS = (
    "schema",
    "platform_registration_id",
    "artifact_path",
    "artifact_version",
    "artifact_sha3_512",
    "campaign_identity",
    "environment",
    "issuer_authority",
    "authority_key_id",
)
_RECEIPT_FIELDS = (
    "schema",
    "platform_registration_id",
    "deployment_certification_id",
    "entry_fingerprint",
    "verification_status",
    "verifier_authority",
    "authority_key_id",
)
_EVIDENCE_FIELDS = (
    "artifact_path",
    "artifact_version",
    "artifact_sha3_512",
    "environment",
    "deployment_identity",
    "deployment_event_identity",
    "deployment_observed_at",
    "campaign_identity",
    "producer_authority",
    "deployment_status",
)


class PRDCAError(ValueError):
    """Base fail-closed PRDCA error."""


class PRDCAUnknownFieldError(PRDCAError):
    """A mapping contains an unknown or missing field."""


class PRDCASchemaError(PRDCAError):
    """A typed certificate schema is invalid."""


class PRDCACanonicalizationError(PRDCAError):
    """A value cannot be represented by the canonical byte contract."""


class PRDCAIdentifierMismatchError(PRDCAError):
    """A derived identifier does not match the supplied identifier."""


class PRDCASignatureVerificationError(PRDCAError):
    """A signature, key, or attestation cannot be verified."""


class PRDCAUnknownAuthorityKeyError(PRDCASignatureVerificationError):
    """The exact requested authority key is unavailable."""


class PRDCAArtifactConflictError(PRDCAError):
    """A certificate conflicts with an existing immutable artifact identity."""


class PRDCATransactionOwnershipError(PRDCAError):
    """Persistence was attempted without the caller-owned transaction boundary."""


class PRDCASigner(Protocol):
    """Injected private signer; implementations must produce Ed25519 bytes."""

    def sign(self, message: bytes) -> bytes: ...


class PRDCAKeyResolver(Protocol):
    """Injected exact-key resolver for Ed25519 verification."""

    def resolve(self, authority_key_id: str) -> Callable[[bytes, bytes], bool]: ...


class PRDCACertificateLedger(Protocol):
    """Inert caller-owned persistence boundary; no storage is implemented here."""

    def append_batch(
        self, batch: "PRDCACertificateBatch", session: "CallerOwnedTransaction"
    ) -> None: ...


class CallerOwnedTransaction(Protocol):
    """Marker protocol for an already-active caller transaction."""

    @property
    def active(self) -> bool: ...


class _Clock(Protocol):
    def now(self) -> datetime: ...


class _SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


def _text(name: str, value: object, *, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value:
        raise PRDCACanonicalizationError(f"M11P3K_INVALID_{name.upper()}")
    normalized = unicodedata.normalize("NFC", value)
    if any(unicodedata.category(char).startswith("C") for char in normalized):
        raise PRDCACanonicalizationError(f"M11P3K_NONCANONICAL_{name.upper()}")
    if pattern is not None and pattern.fullmatch(normalized) is None:
        raise PRDCACanonicalizationError(f"M11P3K_INVALID_{name.upper()}")
    return normalized


def _key_id(value: object) -> str:
    return _text("authority_key_id", value, pattern=_PRDCA_KEY_ID)


def _digest(value: object, name: str) -> str:
    return _text(name, value, pattern=_DIGEST)


def _timestamp(value: object) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise PRDCACanonicalizationError("M11P3K_UTC_TIMESTAMP_REQUIRED")
    instant = value.astimezone(timezone.utc)
    return instant.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _canonicalize(value: object) -> object:
    if isinstance(value, str):
        normalized = unicodedata.normalize("NFC", value)
        if any(unicodedata.category(char).startswith("C") for char in normalized):
            raise PRDCACanonicalizationError("M11P3K_CONTROL_CHARACTER")
        return normalized
    if isinstance(value, Mapping):
        return {str(key): _canonicalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if value is None or isinstance(value, (bool, int, float)):
        if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
            raise PRDCACanonicalizationError("M11P3K_NONFINITE_NUMBER")
        return value
    raise PRDCACanonicalizationError("M11P3K_UNSUPPORTED_CANONICAL_VALUE")


def _canonical_bytes(value: Mapping[str, object], fields: Sequence[str]) -> bytes:
    if tuple(value) != tuple(fields):
        raise PRDCAUnknownFieldError("M11P3K_FIELD_ORDER_OR_SCHEMA_MISMATCH")
    normalized = _canonicalize(value)
    try:
        encoded = json.dumps(
            normalized,
            ensure_ascii=False,
            sort_keys=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise PRDCACanonicalizationError("M11P3K_CANONICAL_JSON_FAILURE") from exc
    if encoded != encoded.rstrip() or encoded.endswith(b"\n"):
        raise PRDCACanonicalizationError("M11P3K_TRAILING_WHITESPACE")
    return encoded


def _id(value: Mapping[str, object], fields: Sequence[str]) -> str:
    return hashlib.sha3_512(_canonical_bytes(value, fields)).hexdigest()


def _b64(value: bytes) -> str:
    return urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _unb64(value: object) -> bytes:
    if not isinstance(value, str) or not value or re.fullmatch(r"[A-Za-z0-9_-]+", value) is None:
        raise PRDCASignatureVerificationError("M11P3K_INVALID_SIGNATURE_ENCODING")
    try:
        decoded = urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except Exception as exc:
        raise PRDCASignatureVerificationError("M11P3K_INVALID_SIGNATURE_ENCODING") from exc
    if _b64(decoded) != value or len(decoded) != 64:
        raise PRDCASignatureVerificationError("M11P3K_INVALID_SIGNATURE_ENCODING")
    return decoded


def _verify_with(resolver: PRDCAKeyResolver, key_id: str, message: bytes, signature: bytes) -> None:
    try:
        verifier = resolver.resolve(key_id)
    except Exception as exc:
        raise PRDCAUnknownAuthorityKeyError("M11P3K_UNKNOWN_AUTHORITY_KEY") from exc
    try:
        valid = bool(verifier(message, signature))
    except Exception as exc:
        raise PRDCASignatureVerificationError("M11P3K_SIGNATURE_VERIFICATION_FAILURE") from exc
    if not valid:
        raise PRDCASignatureVerificationError("M11P3K_INVALID_SIGNATURE")


def _sign(signer: PRDCASigner, message: bytes) -> str:
    try:
        signature = signer.sign(message)
    except Exception as exc:
        raise PRDCASignatureVerificationError("M11P3K_SIGNATURE_CREATION_FAILURE") from exc
    if not isinstance(signature, bytes) or len(signature) != 64:
        raise PRDCASignatureVerificationError("M11P3K_INVALID_SIGNER_OUTPUT")
    return _b64(signature)


def _validate_relative_path(value: object) -> str:
    path = _text("artifact_path", value)
    if "\\" in path or path.startswith("/"):
        raise PRDCACanonicalizationError("M11P3K_INVALID_ARTIFACT_PATH")
    parsed = PurePosixPath(path)
    if not path or path in (".", "..") or any(part in ("", ".", "..") for part in parsed.parts):
        raise PRDCACanonicalizationError("M11P3K_INVALID_ARTIFACT_PATH")
    return path


def _mapping_proxy(value: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class PlatformRegistrationCertificateEnvelope:
    envelope_schema: str
    artifact_type: str
    artifact_id: str
    payload_schema: str
    payload: Mapping[str, object]
    campaign_identity: str
    issuer_authority: str
    authority_key_id: str
    signature_algorithm: str
    signature: str
    issued_at: str
    status: str

    _FIELDS: ClassVar[tuple[str, ...]] = _ENVELOPE_FIELDS

    def to_dict(self) -> dict[str, object]:
        return {field: getattr(self, field) for field in self._FIELDS}


@dataclass(frozen=True, slots=True)
class DeploymentCertificationCertificateEnvelope:
    envelope_schema: str
    artifact_type: str
    artifact_id: str
    payload_schema: str
    payload: Mapping[str, object]
    campaign_identity: str
    issuer_authority: str
    authority_key_id: str
    signature_algorithm: str
    signature: str
    issued_at: str
    status: str

    _FIELDS: ClassVar[tuple[str, ...]] = _ENVELOPE_FIELDS

    def to_dict(self) -> dict[str, object]:
        return {field: getattr(self, field) for field in self._FIELDS}


@dataclass(frozen=True, slots=True)
class DescriptorVerificationReceiptEnvelope:
    envelope_schema: str
    artifact_type: str
    artifact_id: str
    payload_schema: str
    payload: Mapping[str, object]
    campaign_identity: str
    issuer_authority: str
    authority_key_id: str
    signature_algorithm: str
    signature: str
    issued_at: str
    status: str

    _FIELDS: ClassVar[tuple[str, ...]] = _ENVELOPE_FIELDS

    def to_dict(self) -> dict[str, object]:
        return {field: getattr(self, field) for field in self._FIELDS}


@dataclass(frozen=True, slots=True)
class AuthenticatedRuntimeDeploymentEvidencePayload:
    artifact_path: str
    artifact_version: str
    artifact_sha3_512: str
    environment: str
    deployment_identity: str
    deployment_event_identity: str
    deployment_observed_at: str
    campaign_identity: str
    producer_authority: str
    deployment_status: str

    _FIELDS: ClassVar[tuple[str, ...]] = _EVIDENCE_FIELDS

    def to_dict(self) -> dict[str, object]:
        return {field: getattr(self, field) for field in self._FIELDS}


@dataclass(frozen=True, slots=True)
class AuthenticatedRuntimeDeploymentEvidence:
    envelope_schema: str
    evidence_type: str
    evidence_id: str
    payload_schema: str
    payload: Mapping[str, object]
    producer_authority: str
    attestation_key_id: str
    signature_algorithm: str
    signature: str
    status: str

    _FIELDS: ClassVar[tuple[str, ...]] = _EVIDENCE_ENVELOPE_FIELDS

    def to_dict(self) -> dict[str, object]:
        return {field: getattr(self, field) for field in self._FIELDS}


@dataclass(frozen=True, slots=True)
class PRDCACertificateBatch:
    platform_registration: PlatformRegistrationCertificateEnvelope
    deployment_certification: DeploymentCertificationCertificateEnvelope
    descriptor_receipt: DescriptorVerificationReceiptEnvelope


def _envelope_signing_view(envelope: Mapping[str, object]) -> dict[str, object]:
    return {field: envelope[field] for field in _ENVELOPE_FIELDS if field != "signature"}


def _evidence_signing_view(envelope: Mapping[str, object]) -> dict[str, object]:
    return {field: envelope[field] for field in _EVIDENCE_ENVELOPE_FIELDS if field != "signature"}


def _make_envelope(
    *,
    artifact_type: str,
    artifact_id: str,
    payload_schema: str,
    payload: Mapping[str, object],
    campaign_identity: str,
    authority_key_id: str,
    signer: PRDCASigner,
    clock: _Clock,
) -> dict[str, object]:
    base: dict[str, object] = {
        "envelope_schema": SIGNED_ENVELOPE_SCHEMA,
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "payload_schema": payload_schema,
        "payload": dict(payload),
        "campaign_identity": campaign_identity,
        "issuer_authority": PRDCA_OWNER,
        "authority_key_id": authority_key_id,
        "signature_algorithm": SIGNATURE_ALGORITHM,
        "signature": "pending",
        "issued_at": _timestamp(clock.now()),
        "status": CERTIFICATE_STATUS_ACTIVE,
    }
    base["signature"] = _sign(signer, _canonical_bytes(_envelope_signing_view(base), tuple(field for field in _ENVELOPE_FIELDS if field != "signature")))
    return base


def _make_evidence_envelope(
    *, payload: Mapping[str, object], evidence_id: str, attestation_key_id: str,
    signature: str, status: str,
) -> AuthenticatedRuntimeDeploymentEvidence:
    envelope = {
        "envelope_schema": DEPLOYMENT_EVIDENCE_ENVELOPE_SCHEMA,
        "evidence_type": "AuthenticatedRuntimeDeploymentEvidence",
        "evidence_id": evidence_id,
        "payload_schema": DEPLOYMENT_EVIDENCE_SCHEMA,
        "payload": dict(payload),
        "producer_authority": DEPLOYMENT_EVIDENCE_PRODUCER,
        "attestation_key_id": attestation_key_id,
        "signature_algorithm": SIGNATURE_ALGORITHM,
        "signature": signature,
        "status": status,
    }
    return AuthenticatedRuntimeDeploymentEvidence(
        envelope_schema=cast(str, envelope["envelope_schema"]),
        evidence_type=cast(str, envelope["evidence_type"]),
        evidence_id=evidence_id,
        payload_schema=DEPLOYMENT_EVIDENCE_SCHEMA,
        payload=_mapping_proxy(cast(Mapping[str, object], envelope["payload"])),
        producer_authority=DEPLOYMENT_EVIDENCE_PRODUCER,
        attestation_key_id=attestation_key_id,
        signature_algorithm=SIGNATURE_ALGORITHM,
        signature=signature,
        status=status,
    )


class PRDCAAuthority:
    """Stateless PRDCA issuer/verifier with injected cryptographic boundaries."""

    def __init__(
        self,
        *,
        signer: PRDCASigner,
        key_resolver: PRDCAKeyResolver,
        deployment_evidence_key_resolver: PRDCAKeyResolver,
        clock: _Clock | None = None,
        ledger: PRDCACertificateLedger | None = None,
        artifact_root: str | Path | None = None,
    ) -> None:
        self._signer = signer
        self._key_resolver = key_resolver
        self._evidence_keys = deployment_evidence_key_resolver
        self._clock = clock or _SystemClock()
        self._ledger = ledger
        self._artifact_root = Path(artifact_root or Path.cwd()).resolve()

    def issue_platform_registration_certificate(
        self, *, source_identity: str, source_contract_version: str,
        implementation_identity: str, capability_class: str,
        campaign_identity: str, authority_key_id: str,
    ) -> PlatformRegistrationCertificateEnvelope:
        key_id = _key_id(authority_key_id)
        payload = {
            "schema": PRC_SCHEMA,
            "source_identity": _text("source_identity", source_identity, pattern=_TOKEN),
            "source_contract_version": _text("source_contract_version", source_contract_version, pattern=_TOKEN),
            "implementation_identity": _text("implementation_identity", implementation_identity, pattern=_IMPLEMENTATION),
            "capability_class": _text("capability_class", capability_class, pattern=_TOKEN),
            "campaign_identity": _text("campaign_identity", campaign_identity, pattern=_TOKEN),
            "issuer_authority": PRDCA_OWNER,
            "authority_key_id": key_id,
        }
        artifact_id = _id(payload, _PRC_FIELDS)
        envelope = _make_envelope(
            artifact_type="PLATFORM_REGISTRATION_CERTIFICATE",
            artifact_id=artifact_id,
            payload_schema=PRC_SCHEMA,
            payload=payload,
            campaign_identity=_text("campaign_identity", campaign_identity, pattern=_TOKEN),
            authority_key_id=key_id,
            signer=self._signer,
            clock=self._clock,
        )
        return PlatformRegistrationCertificateEnvelope(
            **cast(dict[str, Any], {field: envelope[field] for field in _ENVELOPE_FIELDS if field != "payload"}),
            payload=_mapping_proxy(cast(Mapping[str, object], envelope["payload"])),
        )

    def verify_platform_registration_certificate(
        self, certificate: PlatformRegistrationCertificateEnvelope,
    ) -> None:
        _verify_prdca_envelope(certificate.to_dict(), PRC_SCHEMA, "PLATFORM_REGISTRATION_CERTIFICATE", _PRC_FIELDS, self._key_resolver)

    def issue_deployment_certification_certificate(
        self, *, platform_registration: PlatformRegistrationCertificateEnvelope,
        deployment_evidence: AuthenticatedRuntimeDeploymentEvidence,
        campaign_identity: str, authority_key_id: str,
    ) -> DeploymentCertificationCertificateEnvelope:
        self.verify_platform_registration_certificate(platform_registration)
        evidence = self.verify_deployment_evidence(deployment_evidence)
        artifact_path = _validate_relative_path(evidence["artifact_path"])
        artifact_file = (self._artifact_root / artifact_path).resolve()
        try:
            artifact_file.relative_to(self._artifact_root)
            actual_digest = hashlib.sha3_512(artifact_file.read_bytes()).hexdigest()
        except (OSError, ValueError) as exc:
            raise PRDCAIdentifierMismatchError("M11P3K_ARTIFACT_BYTES_UNAVAILABLE") from exc
        if actual_digest != evidence["artifact_sha3_512"]:
            raise PRDCAIdentifierMismatchError("M11P3K_ARTIFACT_DIGEST_MISMATCH")
        key_id = _key_id(authority_key_id)
        campaign = _text("campaign_identity", campaign_identity, pattern=_TOKEN)
        if campaign != platform_registration.campaign_identity:
            raise PRDCAIdentifierMismatchError("M11P3K_CAMPAIGN_MISMATCH")
        payload = {
            "schema": DCC_SCHEMA,
            "platform_registration_id": platform_registration.artifact_id,
            "artifact_path": artifact_path,
            "artifact_version": evidence["artifact_version"],
            "artifact_sha3_512": evidence["artifact_sha3_512"],
            "campaign_identity": campaign,
            "environment": evidence["environment"],
            "issuer_authority": PRDCA_OWNER,
            "authority_key_id": key_id,
        }
        artifact_id = _id(payload, _DCC_FIELDS)
        envelope = _make_envelope(
            artifact_type="DEPLOYMENT_CERTIFICATION_CERTIFICATE",
            artifact_id=artifact_id,
            payload_schema=DCC_SCHEMA,
            payload=payload,
            campaign_identity=campaign,
            authority_key_id=key_id,
            signer=self._signer,
            clock=self._clock,
        )
        return DeploymentCertificationCertificateEnvelope(
            **cast(dict[str, Any], {field: envelope[field] for field in _ENVELOPE_FIELDS if field != "payload"}),
            payload=_mapping_proxy(cast(Mapping[str, object], envelope["payload"])),
        )

    def verify_deployment_evidence(
        self, evidence: AuthenticatedRuntimeDeploymentEvidence,
    ) -> Mapping[str, object]:
        if not isinstance(evidence, AuthenticatedRuntimeDeploymentEvidence):
            raise PRDCASignatureVerificationError("M11P3K_EVIDENCE_REQUIRED")
        raw = evidence.to_dict()
        if tuple(raw) != _EVIDENCE_ENVELOPE_FIELDS:
            raise PRDCAUnknownFieldError("M11P3K_EVIDENCE_ENVELOPE_SCHEMA")
        if evidence.envelope_schema != DEPLOYMENT_EVIDENCE_ENVELOPE_SCHEMA or evidence.payload_schema != DEPLOYMENT_EVIDENCE_SCHEMA:
            raise PRDCASchemaError("M11P3K_EVIDENCE_SCHEMA_MISMATCH")
        if evidence.evidence_type != "AuthenticatedRuntimeDeploymentEvidence" or evidence.producer_authority != DEPLOYMENT_EVIDENCE_PRODUCER:
            raise PRDCASignatureVerificationError("M11P3K_UNKNOWN_EVIDENCE_PRODUCER")
        if evidence.signature_algorithm != SIGNATURE_ALGORITHM or evidence.status != CERTIFICATE_STATUS_ACTIVE:
            raise PRDCASignatureVerificationError("M11P3K_INVALID_EVIDENCE_ENVELOPE")
        payload = dict(evidence.payload)
        if tuple(payload) != _EVIDENCE_FIELDS:
            raise PRDCAUnknownFieldError("M11P3K_EVIDENCE_PAYLOAD_SCHEMA")
        if payload["producer_authority"] != evidence.producer_authority or payload["deployment_status"] != "SUCCEEDED":
            raise PRDCASignatureVerificationError("M11P3K_EVIDENCE_STATUS_OR_PRODUCER_INVALID")
        _validate_relative_path(payload["artifact_path"])
        _text("artifact_version", payload["artifact_version"], pattern=_TOKEN)
        _digest(payload["artifact_sha3_512"], "artifact_sha3_512")
        for name in ("environment", "deployment_identity", "deployment_event_identity", "campaign_identity"):
            _text(name, payload[name], pattern=_TOKEN)
        _text("deployment_observed_at", payload["deployment_observed_at"], pattern=re.compile(r"^\d{4}-\d{2}-\d{2}T.*Z$"))
        expected = _id(payload, _EVIDENCE_FIELDS)
        if expected != evidence.evidence_id:
            raise PRDCAIdentifierMismatchError("M11P3K_EVIDENCE_ID_MISMATCH")
        _verify_with(self._evidence_keys, _key_id(evidence.attestation_key_id), _canonical_bytes(_evidence_signing_view(raw), tuple(field for field in _EVIDENCE_ENVELOPE_FIELDS if field != "signature")), _unb64(evidence.signature))
        return MappingProxyType(payload)

    def verify_descriptor_binding(
        self, *, platform_registration: PlatformRegistrationCertificateEnvelope,
        deployment_certification: DeploymentCertificationCertificateEnvelope,
        descriptor: TenantInboundCredentialMetadataSourceDescriptor,
    ) -> DescriptorVerificationReceiptEnvelope:
        self.verify_platform_registration_certificate(platform_registration)
        _verify_prdca_envelope(deployment_certification.to_dict(), DCC_SCHEMA, "DEPLOYMENT_CERTIFICATION_CERTIFICATE", _DCC_FIELDS, self._key_resolver)
        dcc = deployment_certification.payload
        prc = platform_registration.payload
        if dcc["platform_registration_id"] != platform_registration.artifact_id:
            raise PRDCAIdentifierMismatchError("M11P3K_DCC_PRC_LINK_MISMATCH")
        for field in ("source_identity", "source_contract_version", "implementation_identity", "capability_class"):
            if descriptor_value := getattr(descriptor, field, None):
                if prc[field] != descriptor_value:
                    raise PRDCAIdentifierMismatchError("M11P3K_DESCRIPTOR_SEMANTIC_MISMATCH")
        provenance = descriptor.registration_provenance
        if isinstance(provenance, Mapping):
            provenance = TenantInboundCredentialMetadataSourceRegistrationProvenance.from_mapping(provenance)
        if provenance.platform_registration_id != platform_registration.artifact_id or provenance.deployment_certification_id != deployment_certification.artifact_id:
            raise PRDCAIdentifierMismatchError("M11P3K_DESCRIPTOR_PROVENANCE_MISMATCH")
        computed = compute_entry_fingerprint(
            descriptor.source_identity,
            descriptor.source_contract_version,
            descriptor.implementation_identity,
            descriptor.capability_class,
            provenance,
        )
        if computed != descriptor.entry_fingerprint:
            raise PRDCAIdentifierMismatchError("M11P3K_DESCRIPTOR_FINGERPRINT_MISMATCH")
        key_id = _key_id(platform_registration.authority_key_id)
        payload = {
            "schema": RECEIPT_SCHEMA,
            "platform_registration_id": platform_registration.artifact_id,
            "deployment_certification_id": deployment_certification.artifact_id,
            "entry_fingerprint": computed,
            "verification_status": VERIFICATION_STATUS_VERIFIED,
            "verifier_authority": PRDCA_OWNER,
            "authority_key_id": key_id,
        }
        envelope = _make_envelope(
            artifact_type="DESCRIPTOR_VERIFICATION_RECEIPT",
            artifact_id=_id(payload, _RECEIPT_FIELDS),
            payload_schema=RECEIPT_SCHEMA,
            payload=payload,
            campaign_identity=platform_registration.campaign_identity,
            authority_key_id=key_id,
            signer=self._signer,
            clock=self._clock,
        )
        return DescriptorVerificationReceiptEnvelope(
            **cast(dict[str, Any], {field: envelope[field] for field in _ENVELOPE_FIELDS if field != "payload"}),
            payload=_mapping_proxy(cast(Mapping[str, object], envelope["payload"])),
        )

    def persist_certificate_batch(
        self, *, batch: PRDCACertificateBatch, session: CallerOwnedTransaction,
    ) -> None:
        if self._ledger is None or not getattr(session, "active", False):
            raise PRDCATransactionOwnershipError("M11P3K_CALLER_TRANSACTION_REQUIRED")
        self._ledger.append_batch(batch, session)


def _verify_prdca_envelope(
    raw: Mapping[str, object], payload_schema: str, artifact_type: str,
    id_fields: Sequence[str], resolver: PRDCAKeyResolver,
) -> None:
    if tuple(raw) != _ENVELOPE_FIELDS:
        raise PRDCAUnknownFieldError("M11P3K_ENVELOPE_SCHEMA")
    if raw["envelope_schema"] != SIGNED_ENVELOPE_SCHEMA or raw["artifact_type"] != artifact_type or raw["payload_schema"] != payload_schema:
        raise PRDCASchemaError("M11P3K_ENVELOPE_SCHEMA_MISMATCH")
    if raw["issuer_authority"] != PRDCA_OWNER or raw["signature_algorithm"] != SIGNATURE_ALGORITHM or raw["status"] != CERTIFICATE_STATUS_ACTIVE:
        raise PRDCASignatureVerificationError("M11P3K_ENVELOPE_AUTHORITY_MISMATCH")
    payload = raw["payload"]
    if not isinstance(payload, Mapping) or tuple(payload) != tuple(id_fields):
        raise PRDCAUnknownFieldError("M11P3K_PAYLOAD_SCHEMA")
    expected = _id(payload, id_fields)
    if expected != raw["artifact_id"]:
        raise PRDCAIdentifierMismatchError("M11P3K_ARTIFACT_ID_MISMATCH")
    if payload.get("issuer_authority") != PRDCA_OWNER or payload.get("authority_key_id") != raw["authority_key_id"]:
        raise PRDCAIdentifierMismatchError("M11P3K_PAYLOAD_AUTHORITY_MISMATCH")
    _verify_with(
        resolver,
        _key_id(raw["authority_key_id"]),
        _canonical_bytes(_envelope_signing_view(raw), tuple(field for field in _ENVELOPE_FIELDS if field != "signature")),
        _unb64(raw["signature"]),
    )


__all__ = [
    "AuthenticatedRuntimeDeploymentEvidence",
    "AuthenticatedRuntimeDeploymentEvidencePayload",
    "CallerOwnedTransaction",
    "DCC_SCHEMA",
    "DEPLOYMENT_EVIDENCE_AUTHORITY",
    "DEPLOYMENT_EVIDENCE_ENVELOPE_SCHEMA",
    "DEPLOYMENT_EVIDENCE_PRODUCER",
    "DEPLOYMENT_EVIDENCE_SCHEMA",
    "DescriptorVerificationReceiptEnvelope",
    "DeploymentCertificationCertificateEnvelope",
    "ID_ALGORITHM",
    "PRC_SCHEMA",
    "PRDCAArtifactConflictError",
    "PRDCAAuthority",
    "PRDCAError",
    "PRDCAKeyResolver",
    "PRDCACanonicalizationError",
    "PRDCACertificateBatch",
    "PRDCAIdentifierMismatchError",
    "PRDCASignatureVerificationError",
    "PRDCAUnknownAuthorityKeyError",
    "PRDCAUnknownFieldError",
    "PRDCACertificateLedger",
    "PRDCATransactionOwnershipError",
    "PlatformRegistrationCertificateEnvelope",
    "RECEIPT_SCHEMA",
    "SIGNED_ENVELOPE_SCHEMA",
]


# ARTIFACT: prdca.py
# VERSION: v1.0.1-M11-R8-R3B-P8-P3D-P5-R8-P3KR1
# AUTHORITY BOUNDARY: stateless PRDCA certificate issuance and verification only
# TENANT POSTURE: platform governance scope; no tenant authorization
# FAIL-CLOSED POSTURE: malformed, unsigned, divergent, or unknown artifacts reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
