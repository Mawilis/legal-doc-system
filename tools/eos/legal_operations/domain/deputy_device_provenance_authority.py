"""Dedicated Deputy browser-device proof-of-possession authority.

TITLE: WILSY OS Deputy Device Provenance Authority
VERSION: v1.0.0-L8-6G-DEPUTY-DEVICE-PROVENANCE
AUTHORITY: Python EOS Legal Operations identity-evidence boundary.
EPITOME: Verify one short-lived, server-issued challenge signed by a Deputy-owned
         P-256 browser key, bound to the authenticated principal, canonical
         Deputy binding, exact tenant and current authentication session.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/deputy_device_provenance_authority.py
COLLABORATION / OWNERSHIP: IAM owns authentication/session currentness; P1 owns
                            Deputy identity; L8-6B owns principal-to-Deputy
                            binding; this module verifies browser key possession;
                            registry owns challenge consumption and lifecycle.
CERTIFICATION / UPDATE DATE: 2026-10-30
CHANGELOG: v1.0.0 establishes P-256 ECDSA proof-of-possession challenge and
           immutable secret-free device provenance. Hardware attestation and
           operating-system permission are explicitly not claimed.
COMPLIANCE: Privacy-by-design controls; no legal-compliance finding is made.
SECURITY / PRIVACY POSTURE: Public key only; no private key, bearer, token,
                             location, permission, or biometric material.
TENANT BOUNDARY: Tenant, principal, Deputy and office derive from the canonical
                 DeputyPrincipalBinding; caller supplies only the active session
                 reference and public-key material.
AUTHORITY BOUNDARY: Proves possession of a browser-held P-256 private key at
                    one challenge time. It is not hardware attestation, trusted
                    device certification, OS permission proof, IAM, role,
                    membership, service or Return of Service authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Pure cryptographic domain value; registry must consume
                      each challenge exactly once in caller-owned transaction.
FAIL-CLOSED DECLARATION: Exact P-256 key, canonical challenge, 32-byte nonce,
                         bounded UTC window and valid ECDSA signature required.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
from typing import Any, Final, NoReturn, cast

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

from tools.eos.legal_operations.domain.deputy_principal_binding import (
    DeputyPrincipalBinding,
)

VERSION: Final[str] = "v1.0.0-L8-6G-DEPUTY-DEVICE-PROVENANCE"
SCHEMA: Final[str] = "WILSY-LEGAL-OPERATIONS-DEPUTY-DEVICE-PROVENANCE/V1"
CHALLENGE_PURPOSE: Final[str] = "DEPUTY_DEVICE_ENROLLMENT_PROOF"
SIGNATURE_ALGORITHM: Final[str] = "ECDSA_P256_SHA256_WEBCRYPTO_P1363"
MAX_CHALLENGE_LIFETIME: Final[timedelta] = timedelta(minutes=5)
_NONCE_BYTES: Final[int] = 32
_SIGNATURE_BYTES: Final[int] = 64
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,191}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_B64URL = re.compile(r"^[A-Za-z0-9_-]+$")


class DeputyDeviceProvenanceAuthorityError(ValueError):
    """Stable fail-closed Deputy device proof error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = DeputyDeviceProvenanceAuthorityError(code)
    if cause is None:
        raise error
    raise error from cause


def _identifier(name: str, value: object) -> str:
    if not isinstance(value, str) or _ID.fullmatch(value) is None:
        _fail(f"L8_6G_{name.upper()}_INVALID")
    return value


def _utc(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(f"L8_6G_{name.upper()}_INVALID")
    return value.astimezone(timezone.utc)


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(name: str, value: object) -> bytes:
    if not isinstance(value, str) or not value or _B64URL.fullmatch(value) is None:
        _fail(f"L8_6G_{name.upper()}_INVALID")
    try:
        return base64.b64decode(
            value + "=" * (-len(value) % 4),
            altchars=b"-_",
            validate=True,
        )
    except (ValueError, TypeError) as error:
        _fail(f"L8_6G_{name.upper()}_INVALID", error)


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _public_key(public_key_der: bytes) -> ec.EllipticCurvePublicKey:
    try:
        key = serialization.load_der_public_key(public_key_der)
    except (TypeError, ValueError) as error:
        _fail("L8_6G_PUBLIC_KEY_INVALID", error)
    if (
        not isinstance(key, ec.EllipticCurvePublicKey)
        or not isinstance(key.curve, ec.SECP256R1)
    ):
        _fail("L8_6G_P256_PUBLIC_KEY_REQUIRED")
    canonical = key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    if canonical != public_key_der:
        _fail("L8_6G_PUBLIC_KEY_NOT_CANONICAL")
    return key


def _challenge_payload(
    *,
    challenge_id: str,
    tenant_id: str,
    principal_id: str,
    deputy_id: str,
    sheriff_office_id: str,
    session_reference: str,
    device_id: str,
    public_key_spki: str,
    public_key_fingerprint: str,
    nonce: str,
    issued_at: datetime,
    expires_at: datetime,
) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "purpose": CHALLENGE_PURPOSE,
        "algorithm": SIGNATURE_ALGORITHM,
        "challenge_id": challenge_id,
        "tenant_id": tenant_id,
        "principal_id": principal_id,
        "deputy_id": deputy_id,
        "sheriff_office_id": sheriff_office_id,
        "session_reference": session_reference,
        "device_id": device_id,
        "public_key_spki": public_key_spki,
        "public_key_fingerprint": public_key_fingerprint,
        "nonce": nonce,
        "issued_at": issued_at.isoformat(timespec="microseconds"),
        "expires_at": expires_at.isoformat(timespec="microseconds"),
    }


@dataclass(frozen=True, slots=True, init=False)
class DeputyDeviceProvenanceChallenge:
    """Server-issued challenge bound to one authenticated Deputy browser key.

    Challenge construction is factory-only. A persistence/orchestration layer
    must issue the nonce, persist this exact challenge, and atomically consume
    it once before accepting a proof. This value alone does not prevent replay.
    """

    challenge_id: str
    tenant_id: str
    principal_id: str
    deputy_id: str
    sheriff_office_id: str
    session_reference: str
    device_id: str
    public_key_spki: str
    public_key_fingerprint: str
    nonce: str
    issued_at: datetime
    expires_at: datetime

    def __init__(self, *args: object, **kwargs: object) -> None:
        _fail("L8_6G_CHALLENGE_FACTORY_REQUIRED")

    @classmethod
    def issue(
        cls,
        *,
        binding: DeputyPrincipalBinding,
        session_reference: str,
        challenge_id: str,
        public_key_spki_der: bytes,
        nonce: bytes,
        issued_at: datetime,
        expires_at: datetime,
    ) -> "DeputyDeviceProvenanceChallenge":
        """Create one canonical challenge from an exact Deputy binding.

        Caller must already have admitted current authentication, current tenant
        IAM, current Deputy binding, and current session. The registry must
        persist the challenge and enforce single-use consumption.
        """
        if type(binding) is not DeputyPrincipalBinding:
            _fail("L8_6G_DEPUTY_BINDING_REQUIRED")
        try:
            binding.to_dict()
        except Exception as error:
            _fail("L8_6G_DEPUTY_BINDING_INVALID", error)
        session = _identifier("session_reference", session_reference)
        challenge = _identifier("challenge_id", challenge_id)
        if not isinstance(public_key_spki_der, bytes):
            _fail("L8_6G_PUBLIC_KEY_INVALID")
        key = _public_key(public_key_spki_der)
        canonical_key = key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        key_fingerprint = hashlib.sha3_512(canonical_key).hexdigest()
        device_id = f"deputy-device:{key_fingerprint}"
        nonce_value = nonce if isinstance(nonce, bytes) else b""
        if len(nonce_value) != _NONCE_BYTES:
            _fail("L8_6G_NONCE_INVALID")
        start, end = _utc("issued_at", issued_at), _utc("expires_at", expires_at)
        if end <= start or end - start > MAX_CHALLENGE_LIFETIME:
            _fail("L8_6G_CHALLENGE_WINDOW_INVALID")
        value = cast(Any, object.__new__(cls))
        for name, item in {
            "challenge_id": challenge,
            "tenant_id": binding.tenant_id,
            "principal_id": binding.principal_id,
            "deputy_id": binding.deputy_id,
            "sheriff_office_id": binding.sheriff_office_id,
            "session_reference": session,
            "device_id": device_id,
            "public_key_spki": _b64encode(canonical_key),
            "public_key_fingerprint": key_fingerprint,
            "nonce": _b64encode(nonce_value),
            "issued_at": start,
            "expires_at": end,
        }.items():
            object.__setattr__(value, name, item)
        value._validate()
        return cast("DeputyDeviceProvenanceChallenge", value)

    def _validate(self) -> None:
        """Revalidate all challenge bindings and cryptographic material."""
        for name in (
            "challenge_id", "tenant_id", "principal_id", "deputy_id",
            "sheriff_office_id", "session_reference",
        ):
            _identifier(name, getattr(self, name))
        public_key = _b64decode("public_key_spki", self.public_key_spki)
        key = _public_key(public_key)
        fingerprint = hashlib.sha3_512(
            key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        ).hexdigest()
        if fingerprint != self.public_key_fingerprint or self.device_id != f"deputy-device:{fingerprint}":
            _fail("L8_6G_PUBLIC_KEY_BINDING_INVALID")
        if len(_b64decode("nonce", self.nonce)) != _NONCE_BYTES:
            _fail("L8_6G_NONCE_INVALID")
        start, end = _utc("issued_at", self.issued_at), _utc("expires_at", self.expires_at)
        if end <= start or end - start > MAX_CHALLENGE_LIFETIME:
            _fail("L8_6G_CHALLENGE_WINDOW_INVALID")

    def signed_payload(self) -> bytes:
        """Return the exact UTF-8 bytes the browser must sign using WebCrypto."""
        self._validate()
        payload = _challenge_payload(
            challenge_id=self.challenge_id,
            tenant_id=self.tenant_id,
            principal_id=self.principal_id,
            deputy_id=self.deputy_id,
            sheriff_office_id=self.sheriff_office_id,
            session_reference=self.session_reference,
            device_id=self.device_id,
            public_key_spki=self.public_key_spki,
            public_key_fingerprint=self.public_key_fingerprint,
            nonce=self.nonce,
            issued_at=self.issued_at,
            expires_at=self.expires_at,
        )
        return json.dumps(
            payload,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact non-secret challenge record."""
        self._validate()
        payload = json.loads(self.signed_payload().decode("utf-8"))
        payload["challenge_fingerprint"] = _digest(payload)
        return payload


@dataclass(frozen=True, slots=True, init=False)
class DeputyDeviceProvenance:
    """Immutable proof that one browser-held P-256 key signed one live challenge.

    This establishes proof-of-possession only. It does not claim a hardware-
    backed key, genuine physical device, OS permission, location integrity,
    ongoing device control, or current lifecycle status; the registry owns
    currentness, revocation, and replay protection.
    """

    tenant_id: str
    principal_id: str
    deputy_id: str
    sheriff_office_id: str
    session_reference: str
    device_id: str
    public_key_spki: str
    public_key_fingerprint: str
    challenge_id: str
    challenge_fingerprint: str
    verified_at: datetime
    signature_fingerprint: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        _fail("L8_6G_PROVENANCE_FACTORY_REQUIRED")

    @classmethod
    def verify(
        cls,
        *,
        challenge: DeputyDeviceProvenanceChallenge,
        signature_p1363: bytes,
        verified_at: datetime,
    ) -> "DeputyDeviceProvenance":
        """Verify WebCrypto P-256 ECDSA signature over the exact live challenge.

        The registry must separately prove that this challenge is persisted,
        unexpired, belongs to the current session and has not been consumed.
        """
        if type(challenge) is not DeputyDeviceProvenanceChallenge:
            _fail("L8_6G_CHALLENGE_REQUIRED")
        challenge._validate()
        observed = _utc("verified_at", verified_at)
        if observed < challenge.issued_at or observed > challenge.expires_at:
            _fail("L8_6G_CHALLENGE_EXPIRED")
        if not isinstance(signature_p1363, bytes) or len(signature_p1363) != _SIGNATURE_BYTES:
            _fail("L8_6G_SIGNATURE_INVALID")
        r = int.from_bytes(signature_p1363[:32], "big")
        s = int.from_bytes(signature_p1363[32:], "big")
        if r <= 0 or s <= 0:
            _fail("L8_6G_SIGNATURE_INVALID")
        public_key = _public_key(_b64decode("public_key_spki", challenge.public_key_spki))
        try:
            public_key.verify(
                encode_dss_signature(r, s),
                challenge.signed_payload(),
                ec.ECDSA(hashes.SHA256()),
            )
        except InvalidSignature as error:
            _fail("L8_6G_SIGNATURE_VERIFICATION_FAILED", error)
        signature_fingerprint = hashlib.sha3_512(signature_p1363).hexdigest()
        challenge_fingerprint = str(challenge.to_dict()["challenge_fingerprint"])
        value = cast(Any, object.__new__(cls))
        for name, item in {
            "tenant_id": challenge.tenant_id,
            "principal_id": challenge.principal_id,
            "deputy_id": challenge.deputy_id,
            "sheriff_office_id": challenge.sheriff_office_id,
            "session_reference": challenge.session_reference,
            "device_id": challenge.device_id,
            "public_key_spki": challenge.public_key_spki,
            "public_key_fingerprint": challenge.public_key_fingerprint,
            "challenge_id": challenge.challenge_id,
            "challenge_fingerprint": challenge_fingerprint,
            "verified_at": observed,
            "signature_fingerprint": signature_fingerprint,
        }.items():
            object.__setattr__(value, name, item)
        value._validate()
        return cast("DeputyDeviceProvenance", value)

    def _validate(self) -> None:
        """Revalidate immutable proof shape without claiming currentness."""
        for name in (
            "tenant_id", "principal_id", "deputy_id", "sheriff_office_id",
            "session_reference", "challenge_id",
        ):
            _identifier(name, getattr(self, name))
        key = _public_key(_b64decode("public_key_spki", self.public_key_spki))
        fingerprint = hashlib.sha3_512(
            key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        ).hexdigest()
        if fingerprint != self.public_key_fingerprint or self.device_id != f"deputy-device:{fingerprint}":
            _fail("L8_6G_PROVENANCE_KEY_BINDING_INVALID")
        for name in ("challenge_fingerprint", "signature_fingerprint"):
            if not isinstance(getattr(self, name), str) or _SHA3.fullmatch(getattr(self, name)) is None:
                _fail(f"L8_6G_{name.upper()}_INVALID")
        _utc("verified_at", self.verified_at)

    @property
    def fingerprint(self) -> str:
        """Return SHA3-512 identity over all immutable provenance fields."""
        self._validate()
        return _digest(self.to_dict())

    def to_dict(self) -> dict[str, object]:
        """Serialize secret-free immutable provenance for strict persistence."""
        self._validate()
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "entity_type": "DeputyDeviceProvenance",
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "deputy_id": self.deputy_id,
            "sheriff_office_id": self.sheriff_office_id,
            "session_reference": self.session_reference,
            "device_id": self.device_id,
            "public_key_spki": self.public_key_spki,
            "public_key_fingerprint": self.public_key_fingerprint,
            "challenge_id": self.challenge_id,
            "challenge_fingerprint": self.challenge_fingerprint,
            "verified_at": self.verified_at.isoformat(timespec="microseconds"),
            "signature_fingerprint": self.signature_fingerprint,
        }


__all__ = [
    "VERSION",
    "SCHEMA",
    "CHALLENGE_PURPOSE",
    "SIGNATURE_ALGORITHM",
    "MAX_CHALLENGE_LIFETIME",
    "DeputyDeviceProvenanceAuthorityError",
    "DeputyDeviceProvenanceChallenge",
    "DeputyDeviceProvenance",
]


# ARTIFACT: tools/eos/legal_operations/domain/deputy_device_provenance_authority.py
# VERSION: v1.0.0-L8-6G-DEPUTY-DEVICE-PROVENANCE
# AUTHORITY BOUNDARY: Browser P-256 key proof-of-possession only; no hardware attestation,
#                     OS permission, IAM, service, or Return of Service authority.
# TENANT POSTURE: Exact canonical tenant/principal/Deputy/office binding.
# REPLAY POSTURE: Registry must atomically consume each persisted challenge once.
# FAIL-CLOSED POSTURE: Invalid key, challenge, window, nonce or signature rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
