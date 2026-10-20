"""
WILSY OS — ENGINEERING MERKLE CHECKPOINT WITNESS VERIFICATION
VERSION: 1.0.0-EMP-P31
AUTHORITY: Verify separately authenticated witness receipts.
EPITOME: Independent Ed25519 checkpoint witness validation.
ABSOLUTE CANONICAL PATH: tools/eos/kernel/engineering_merkle_checkpoint_witness.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-007.
SECURITY: Strict base64url, key identity, scope, provenance and validity.
TENANT BOUNDARY: Exact institution and log.
AUTHORITY BOUNDARY: Public verification only; no witness issuance or anchoring.
FINANCIAL AUTHORITY: None.

A verified signature is not proof of external receipt delivery or offsite
retention. Those require independently established operational evidence.
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

DOMAIN = b"WILSY:ENGINEERING:MERKLE:WITNESS:V1\x00"
PROVENANCE = "WILSY_ENGINEERING_WITNESS_TRUST/V1"
KEY_PREFIX = "engineering-witness-key:"
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", re.ASCII)
_HEX32 = re.compile(r"[0-9a-f]{32}", re.ASCII)
_HEX64 = re.compile(r"[0-9a-f]{64}", re.ASCII)
_BASE64URL = re.compile(r"[A-Za-z0-9_-]+", re.ASCII)


class EngineeringCheckpointWitnessError(ValueError):
    """One witness trust, receipt or signature check failed."""


def _identifier(value: object, name: str) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise EngineeringCheckpointWitnessError(
            "INVALID_" + name.upper()
        )
    return value


def _timestamp(value: object) -> datetime:
    if (
        type(value) is not datetime
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise EngineeringCheckpointWitnessError(
            "WITNESS_UTC_TIMESTAMP_REQUIRED"
        )
    return value.astimezone(timezone.utc)


def _decode(value: object, length: int) -> bytes:
    if type(value) is not str or _BASE64URL.fullmatch(value) is None:
        raise EngineeringCheckpointWitnessError(
            "WITNESS_BASE64URL_INVALID"
        )
    try:
        raw = base64.urlsafe_b64decode(
            value + "=" * (-len(value) % 4)
        )
    except (ValueError, binascii.Error) as exc:
        raise EngineeringCheckpointWitnessError(
            "WITNESS_BASE64URL_INVALID"
        ) from exc
    if (
        len(raw) != length
        or base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
        != value
    ):
        raise EngineeringCheckpointWitnessError(
            "WITNESS_BASE64URL_INVALID"
        )
    return raw


def _key_id(value: object) -> str:
    if (
        type(value) is not str
        or not value.startswith(KEY_PREFIX)
        or _HEX32.fullmatch(value[len(KEY_PREFIX):]) is None
    ):
        raise EngineeringCheckpointWitnessError(
            "WITNESS_KEY_ID_INVALID"
        )
    return value


@dataclass(frozen=True, slots=True)
class EngineeringCheckpointWitnessKey:
    witness_id: str
    key_id: str
    public_key_base64url: str
    valid_from: datetime
    valid_until: datetime
    status: str
    provenance: str

    def __post_init__(self) -> None:
        _identifier(self.witness_id, "witness_id")
        _key_id(self.key_id)
        raw = _decode(self.public_key_base64url, 32)
        if (
            self.key_id
            != KEY_PREFIX + hashlib.sha3_512(raw).hexdigest()[:32]
        ):
            raise EngineeringCheckpointWitnessError(
                "WITNESS_KEY_DERIVATION_INVALID"
            )
        try:
            Ed25519PublicKey.from_public_bytes(raw)
        except (TypeError, ValueError) as exc:
            raise EngineeringCheckpointWitnessError(
                "WITNESS_PUBLIC_KEY_INVALID"
            ) from exc
        start = _timestamp(self.valid_from)
        end = _timestamp(self.valid_until)
        if end <= start:
            raise EngineeringCheckpointWitnessError(
                "WITNESS_KEY_WINDOW_INVALID"
            )
        if (
            type(self.status) is not str
            or self.status not in ("ACTIVE", "REVOKED", "RETIRED")
        ):
            raise EngineeringCheckpointWitnessError(
                "WITNESS_KEY_STATUS_INVALID"
            )
        if self.provenance != PROVENANCE:
            raise EngineeringCheckpointWitnessError(
                "WITNESS_PROVENANCE_INVALID"
            )
        object.__setattr__(self, "valid_from", start)
        object.__setattr__(self, "valid_until", end)


@dataclass(frozen=True, slots=True)
class EngineeringCheckpointWitnessTrust:
    trusted_keys: tuple[EngineeringCheckpointWitnessKey, ...]

    def __post_init__(self) -> None:
        if (
            type(self.trusted_keys) is not tuple
            or any(
                type(key) is not EngineeringCheckpointWitnessKey
                for key in self.trusted_keys
            )
            or len({key.key_id for key in self.trusted_keys})
            != len(self.trusted_keys)
            or len({key.witness_id for key in self.trusted_keys})
            != len(self.trusted_keys)
        ):
            raise EngineeringCheckpointWitnessError(
                "WITNESS_TRUST_ROOT_INVALID"
            )

    def resolve(
        self, key_id: str
    ) -> EngineeringCheckpointWitnessKey:
        for key in self.trusted_keys:
            if key.key_id == key_id:
                return key
        raise EngineeringCheckpointWitnessError(
            "WITNESS_UNKNOWN_KEY"
        )


@dataclass(frozen=True, slots=True)
class EngineeringCheckpointWitnessReceipt:
    institution_id: str
    log_id: str
    checkpoint_hash: str
    leaf_count: int
    witness_id: str
    key_id: str
    observed_at: datetime
    signature_base64url: str

    def __post_init__(self) -> None:
        _identifier(self.institution_id, "institution_id")
        _identifier(self.log_id, "log_id")
        _identifier(self.witness_id, "witness_id")
        _key_id(self.key_id)
        if (
            type(self.checkpoint_hash) is not str
            or _HEX64.fullmatch(self.checkpoint_hash) is None
        ):
            raise EngineeringCheckpointWitnessError(
                "WITNESS_CHECKPOINT_HASH_INVALID"
            )
        if type(self.leaf_count) is not int or self.leaf_count < 0:
            raise EngineeringCheckpointWitnessError(
                "WITNESS_LEAF_COUNT_INVALID"
            )
        observed = _timestamp(self.observed_at)
        _decode(self.signature_base64url, 64)
        object.__setattr__(self, "observed_at", observed)


def witness_receipt_message(
    receipt: EngineeringCheckpointWitnessReceipt,
) -> bytes:
    if type(receipt) is not EngineeringCheckpointWitnessReceipt:
        raise EngineeringCheckpointWitnessError(
            "EXACT_WITNESS_RECEIPT_REQUIRED"
        )
    payload = {
        "schema": "WILSY-ENGINEERING-CHECKPOINT-WITNESS/V1",
        "institution_id": receipt.institution_id,
        "log_id": receipt.log_id,
        "checkpoint_hash": receipt.checkpoint_hash,
        "leaf_count": receipt.leaf_count,
        "witness_id": receipt.witness_id,
        "key_id": receipt.key_id,
        "observed_at": receipt.observed_at.isoformat(),
    }
    return DOMAIN + json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def verify_checkpoint_witness_receipt(
    *,
    checkpoint: EngineeringMerkleCheckpoint,
    receipt: EngineeringCheckpointWitnessReceipt,
    trust: EngineeringCheckpointWitnessTrust,
    verified_at: datetime,
) -> bool:
    if (
        type(checkpoint) is not EngineeringMerkleCheckpoint
        or type(receipt) is not EngineeringCheckpointWitnessReceipt
        or type(trust) is not EngineeringCheckpointWitnessTrust
    ):
        raise EngineeringCheckpointWitnessError(
            "WITNESS_VERIFICATION_INPUT_INVALID"
        )
    observed = _timestamp(verified_at)

    try:
        EngineeringMerkleCheckpoint.from_dict(checkpoint.to_dict())
    except (TypeError, ValueError, KeyError) as exc:
        raise EngineeringCheckpointWitnessError(
            "WITNESSED_CHECKPOINT_INVALID"
        ) from exc

    if (
        receipt.institution_id != checkpoint.institution_id
        or receipt.log_id != checkpoint.log_id
        or receipt.checkpoint_hash != checkpoint.checkpoint_hash
        or receipt.leaf_count != checkpoint.leaf_count
    ):
        raise EngineeringCheckpointWitnessError(
            "WITNESS_CHECKPOINT_MISMATCH"
        )

    key = trust.resolve(receipt.key_id)
    if (
        key.witness_id != receipt.witness_id
        or key.status != "ACTIVE"
        or key.provenance != PROVENANCE
    ):
        raise EngineeringCheckpointWitnessError(
            "WITNESS_KEY_NOT_AUTHORIZED"
        )
    if not (
        key.valid_from <= receipt.observed_at < key.valid_until
        and key.valid_from <= observed < key.valid_until
        and receipt.observed_at <= observed
    ):
        raise EngineeringCheckpointWitnessError(
            "WITNESS_KEY_NOT_CURRENT"
        )

    public_bytes = _decode(key.public_key_base64url, 32)
    signature_bytes = _decode(receipt.signature_base64url, 64)
    message = witness_receipt_message(receipt)

    try:
        Ed25519PublicKey.from_public_bytes(public_bytes).verify(
            signature_bytes,
            message,
        )
    except (InvalidSignature, TypeError, ValueError) as exc:
        raise EngineeringCheckpointWitnessError(
            "WITNESS_SIGNATURE_INVALID"
        ) from exc

    return True


# ARTIFACT: ENGINEERING MERKLE CHECKPOINT WITNESS VERIFIER
# VERSION: 1.0.0-EMP-P31
# AUTHORITY: PUBLIC KEY VERIFICATION ONLY
# PRODUCTION KEY OR WITNESS ISSUANCE: NONE
# OFFSITE DELIVERY / EXTERNAL PUBLICATION: NOT CERTIFIED
# END OF WILSY OS SOVEREIGN ARTIFACT
