"""
WILSY OS — ENGINEERING MERKLE CHECKPOINT AUTHENTICATION
VERSION: 1.0.0-EMP-P27
AUTHORITY: Public-key-only checkpoint signature verification.
EPITOME: Independent scope-bound Ed25519 authentication.
ABSOLUTE CANONICAL PATH: tools/eos/kernel/engineering_merkle_checkpoint_authentication.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: P27 verification domain, immutable trust descriptors and signatures.
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-007.
SECURITY: Domain separation, strict key identity and canonical encoding.
TENANT BOUNDARY: Institution and evidence log exact binding.
TRUST AUTHORITY: Injected trusted public keys only; no source-owned production keys.
SIGNING AUTHORITY: None.
FINANCIAL EXECUTION AUTHORITY: None.
"""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from tools.eos.kernel.engineering_merkle_checkpoint import (
    EngineeringMerkleCheckpoint,
)

DOMAIN = b"WILSY:ENGINEERING:MERKLE:CHECKPOINT:AUTH:V1\x00"
PROVENANCE = "WILSY_ENGINEERING_CHECKPOINT_TRUST/V1"
KEY_PREFIX = "engineering-checkpoint-key:"
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", re.ASCII)
_HEX = re.compile(r"[a-f0-9]{32}", re.ASCII)
_SIGNATURE_CHARS = re.compile(r"[A-Za-z0-9_-]{86}", re.ASCII)
_PUBLIC_CHARS = re.compile(r"[A-Za-z0-9_-]{43}", re.ASCII)


class EngineeringCheckpointAuthenticationError(ValueError):
    """Exact checkpoint signature or trust check failed."""


def _identifier(value: object, name: str) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise EngineeringCheckpointAuthenticationError(
            "INVALID_" + name.upper()
        )
    return value


def _timestamp(value: object) -> datetime:
    if (
        type(value) is not datetime
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise EngineeringCheckpointAuthenticationError(
            "UTC_TIMESTAMP_REQUIRED"
        )
    return value.astimezone(timezone.utc)


def _decode(value: object, size: int, pattern: re.Pattern[str]) -> bytes:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise EngineeringCheckpointAuthenticationError(
            "INVALID_BASE64URL_ENCODING"
        )
    try:
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, binascii.Error) as exc:
        raise EngineeringCheckpointAuthenticationError(
            "INVALID_BASE64URL_ENCODING"
        ) from exc
    if (
        len(raw) != size
        or base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
        != value
    ):
        raise EngineeringCheckpointAuthenticationError(
            "INVALID_BASE64URL_ENCODING"
        )
    return raw


@dataclass(frozen=True, slots=True)
class EngineeringCheckpointTrustedKey:
    key_id: str
    public_key_base64url: str
    institution_id: str
    log_id: str
    valid_from: datetime
    valid_until: datetime
    status: str
    provenance: str

    def __post_init__(self) -> None:
        _identifier(self.institution_id, "institution_id")
        _identifier(self.log_id, "log_id")
        raw = _decode(self.public_key_base64url, 32, _PUBLIC_CHARS)
        if (
            type(self.key_id) is not str
            or not self.key_id.startswith(KEY_PREFIX)
            or _HEX.fullmatch(self.key_id[len(KEY_PREFIX):]) is None
            or self.key_id
            != KEY_PREFIX + hashlib.sha3_512(raw).hexdigest()[:32]
        ):
            raise EngineeringCheckpointAuthenticationError(
                "KEY_IDENTITY_INVALID"
            )
        try:
            Ed25519PublicKey.from_public_bytes(raw)
        except (TypeError, ValueError) as exc:
            raise EngineeringCheckpointAuthenticationError(
                "PUBLIC_KEY_INVALID"
            ) from exc
        start = _timestamp(self.valid_from)
        end = _timestamp(self.valid_until)
        if end <= start:
            raise EngineeringCheckpointAuthenticationError(
                "KEY_WINDOW_INVALID"
            )
        if self.status not in ("ACTIVE", "REVOKED", "RETIRED"):
            raise EngineeringCheckpointAuthenticationError(
                "KEY_STATUS_INVALID"
            )
        if self.provenance != PROVENANCE:
            raise EngineeringCheckpointAuthenticationError(
                "TRUST_PROVENANCE_INVALID"
            )
        object.__setattr__(self, "valid_from", start)
        object.__setattr__(self, "valid_until", end)


@dataclass(frozen=True, slots=True)
class EngineeringCheckpointTrustRoot:
    trusted_keys: tuple[EngineeringCheckpointTrustedKey, ...]

    def __post_init__(self) -> None:
        if (
            type(self.trusted_keys) is not tuple
            or any(
                type(key) is not EngineeringCheckpointTrustedKey
                for key in self.trusted_keys
            )
            or len({key.key_id for key in self.trusted_keys})
            != len(self.trusted_keys)
        ):
            raise EngineeringCheckpointAuthenticationError(
                "TRUST_ROOT_INVALID"
            )

    def resolve(
        self, key_id: str
    ) -> EngineeringCheckpointTrustedKey:
        for key in self.trusted_keys:
            if key.key_id == key_id:
                return key
        raise EngineeringCheckpointAuthenticationError(
            "UNKNOWN_CHECKPOINT_KEY"
        )


@dataclass(frozen=True, slots=True)
class EngineeringCheckpointSignature:
    checkpoint_hash: str
    institution_id: str
    log_id: str
    key_id: str
    signature_base64url: str

    def __post_init__(self) -> None:
        _identifier(self.institution_id, "institution_id")
        _identifier(self.log_id, "log_id")
        if (
            type(self.checkpoint_hash) is not str
            or re.fullmatch(r"[a-f0-9]{64}", self.checkpoint_hash) is None
        ):
            raise EngineeringCheckpointAuthenticationError(
                "CHECKPOINT_HASH_INVALID"
            )
        if (
            type(self.key_id) is not str
            or not self.key_id.startswith(KEY_PREFIX)
            or _HEX.fullmatch(self.key_id[len(KEY_PREFIX):]) is None
        ):
            raise EngineeringCheckpointAuthenticationError(
                "KEY_ID_INVALID"
            )
        _decode(self.signature_base64url, 64, _SIGNATURE_CHARS)


def checkpoint_signature_message(
    checkpoint: EngineeringMerkleCheckpoint,
) -> bytes:
    if type(checkpoint) is not EngineeringMerkleCheckpoint:
        raise EngineeringCheckpointAuthenticationError(
            "EXACT_CHECKPOINT_REQUIRED"
        )
    if (
        checkpoint.expected_hash() != checkpoint.checkpoint_hash
    ):
        raise EngineeringCheckpointAuthenticationError(
            "CHECKPOINT_INTEGRITY_INVALID"
        )
    payload = {
        "checkpoint_hash": checkpoint.checkpoint_hash,
        "institution_id": checkpoint.institution_id,
        "log_id": checkpoint.log_id,
        "schema": "WILSY-ENGINEERING-CHECKPOINT-SIGNATURE/V1",
    }
    return DOMAIN + json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")


def verify_checkpoint_signature(
    *,
    checkpoint: EngineeringMerkleCheckpoint,
    signature: EngineeringCheckpointSignature,
    trust_root: EngineeringCheckpointTrustRoot,
    verified_at: datetime,
) -> bool:
    if (
        type(signature) is not EngineeringCheckpointSignature
        or type(trust_root) is not EngineeringCheckpointTrustRoot
    ):
        raise EngineeringCheckpointAuthenticationError(
            "VERIFICATION_INPUT_INVALID"
        )
    observed = _timestamp(verified_at)
    message = checkpoint_signature_message(checkpoint)
    if (
        checkpoint.checkpoint_hash != signature.checkpoint_hash
        or checkpoint.institution_id != signature.institution_id
        or checkpoint.log_id != signature.log_id
    ):
        raise EngineeringCheckpointAuthenticationError(
            "SIGNATURE_CHECKPOINT_SCOPE_MISMATCH"
        )
    key = trust_root.resolve(signature.key_id)
    if (
        key.institution_id != checkpoint.institution_id
        or key.log_id != checkpoint.log_id
        or key.status != "ACTIVE"
        or key.provenance != PROVENANCE
    ):
        raise EngineeringCheckpointAuthenticationError(
            "KEY_NOT_AUTHORIZED_FOR_CHECKPOINT"
        )
    if not key.valid_from <= observed < key.valid_until:
        raise EngineeringCheckpointAuthenticationError(
            "TRUST_KEY_NOT_CURRENT"
        )
    public_bytes = _decode(
        key.public_key_base64url, 32, _PUBLIC_CHARS
    )
    signature_bytes = _decode(
        signature.signature_base64url, 64, _SIGNATURE_CHARS
    )
    try:
        Ed25519PublicKey.from_public_bytes(public_bytes).verify(
            signature_bytes, message
        )
    except (InvalidSignature, TypeError, ValueError) as exc:
        raise EngineeringCheckpointAuthenticationError(
            "CHECKPOINT_SIGNATURE_INVALID"
        ) from exc
    return True


# ARTIFACT: ENGINEERING MERKLE CHECKPOINT AUTHENTICATION
# VERSION: 1.0.0-EMP-P27
# AUTHORITY: PUBLIC-KEY-ONLY VERIFICATION
# PRIVATE KEY AND SIGNING AUTHORITY: NONE
# EXTERNAL ANCHORING AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
