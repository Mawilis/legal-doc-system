"""
WILSY OS — ENGINEERING MERKLE CHECKPOINT HISTORY DOMAIN
VERSION: 1.0.0-EMP-P16
AUTHORITY: Engineering Kernel deterministic history verification.
EPITOME: Immutable, domain-separated, prefix-verifiable checkpoints.
ABSOLUTE CANONICAL PATH: tools/eos/kernel/engineering_merkle_checkpoint.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: 1.0.0-EMP-P16 — Initial complete-history checkpoint domain.
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-007.
SECURITY: Exact schema, append-only prefix validation and hash integrity.
TENANT BOUNDARY: Explicit institution_id and log_id.
AUTHORITY BOUNDARY: Pure computation; no signatures or trusted anchors.
FINANCIAL AUTHORITY BOUNDARY: None.

V1 commits to the full ordered leaf-commitment vector. This enables
independent whole-history prefix verification, but is not a compact
Merkle consistency proof. Hashes do not establish trusted authorship.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Any, Mapping

from tools.eos.kernel.engineering_merkle_proof import (
    canonical_json_bytes,
    leaf_hash,
    merkle_root,
    parent_hash,
)

SCHEMA = "WILSY-ENGINEERING-MERKLE-CHECKPOINT/V1"
_PREFIX = b"WILSY:ENGINEERING:CHECKPOINT:V1\x00"
_EMPTY = b"WILSY:ENGINEERING:MERKLE:EMPTY:V1\x00"
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", re.ASCII)
_HEX = re.compile(r"[0-9a-f]{64}", re.ASCII)
_FIELDS = frozenset({
    "schema", "institution_id", "log_id", "leaf_count",
    "leaf_commitments", "merkle_root", "previous_checkpoint_hash",
    "checkpoint_hash",
})


def _identifier(name: str, value: object) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise ValueError("INVALID_" + name.upper())
    return value


def _hex(name: str, value: object) -> str:
    if type(value) is not str or _HEX.fullmatch(value) is None:
        raise ValueError("INVALID_" + name.upper())
    return value


def _root_from_commitments(commitments: tuple[str, ...]) -> str:
    if not commitments:
        return hashlib.sha3_256(_EMPTY).hexdigest()
    level = list(commitments)
    while len(level) > 1:
        next_level: list[str] = []
        for index in range(0, len(level), 2):
            left = level[index]
            right = level[index + 1] if index + 1 < len(level) else left
            next_level.append(parent_hash(left, right))
        level = next_level
    return level[0]


@dataclass(frozen=True, slots=True)
class EngineeringMerkleCheckpoint:
    schema: str
    institution_id: str
    log_id: str
    leaf_count: int
    leaf_commitments: tuple[str, ...]
    merkle_root: str
    previous_checkpoint_hash: str | None
    checkpoint_hash: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise ValueError("INVALID_CHECKPOINT_SCHEMA")
        _identifier("institution_id", self.institution_id)
        _identifier("log_id", self.log_id)
        if type(self.leaf_count) is not int or self.leaf_count < 0:
            raise ValueError("INVALID_LEAF_COUNT")
        if type(self.leaf_commitments) is not tuple:
            raise TypeError("IMMUTABLE_LEAF_COMMITMENTS_REQUIRED")
        for commitment in self.leaf_commitments:
            _hex("leaf_commitment", commitment)
        if self.leaf_count != len(self.leaf_commitments):
            raise ValueError("CHECKPOINT_LEAF_COUNT_MISMATCH")
        _hex("merkle_root", self.merkle_root)
        _hex("checkpoint_hash", self.checkpoint_hash)
        if self.previous_checkpoint_hash is not None:
            _hex("previous_checkpoint_hash", self.previous_checkpoint_hash)
        if _root_from_commitments(self.leaf_commitments) != self.merkle_root:
            raise ValueError("CHECKPOINT_ROOT_MISMATCH")
        if self.checkpoint_hash != self.expected_hash():
            raise ValueError("CHECKPOINT_PROVENANCE_MISMATCH")

    def semantic_payload(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "institution_id": self.institution_id,
            "log_id": self.log_id,
            "leaf_count": self.leaf_count,
            "leaf_commitments": list(self.leaf_commitments),
            "merkle_root": self.merkle_root,
            "previous_checkpoint_hash": self.previous_checkpoint_hash,
        }

    def expected_hash(self) -> str:
        return hashlib.sha3_256(
            _PREFIX + canonical_json_bytes(self.semantic_payload())
        ).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.semantic_payload(),
            "checkpoint_hash": self.checkpoint_hash,
        }

    @classmethod
    def create(
        cls,
        *,
        institution_id: str,
        log_id: str,
        events: list[bytes],
        previous_checkpoint: EngineeringMerkleCheckpoint | None = None,
    ) -> EngineeringMerkleCheckpoint:
        institution = _identifier("institution_id", institution_id)
        log = _identifier("log_id", log_id)
        if type(events) is not list:
            raise TypeError("EVENT_LIST_REQUIRED")
        if previous_checkpoint is not None:
            if type(previous_checkpoint) is not cls:
                raise TypeError("EXACT_PREVIOUS_CHECKPOINT_REQUIRED")
            if (
                previous_checkpoint.institution_id != institution
                or previous_checkpoint.log_id != log
            ):
                raise ValueError("CROSS_SCOPE_CHECKPOINT_LINK")
        commitments = tuple(leaf_hash(event) for event in events)
        count = len(commitments)

        if previous_checkpoint is not None:
            # Revalidate predecessor integrity at the admission boundary.
            # No caller may manufacture a valid extension from a rewritten
            # history or a forged predecessor commitment.
            if (
                previous_checkpoint.expected_hash()
                != previous_checkpoint.checkpoint_hash
                or _root_from_commitments(
                    previous_checkpoint.leaf_commitments
                ) != previous_checkpoint.merkle_root
            ):
                raise ValueError("INVALID_PREDECESSOR_CHECKPOINT")

            if count <= previous_checkpoint.leaf_count:
                raise ValueError("CHECKPOINT_EXTENSION_MUST_GROW")

            if (
                commitments[:previous_checkpoint.leaf_count]
                != previous_checkpoint.leaf_commitments
            ):
                raise ValueError("CHECKPOINT_HISTORY_PREFIX_MISMATCH")

        root = merkle_root(events)
        previous_hash = (
            previous_checkpoint.checkpoint_hash
            if previous_checkpoint is not None else None
        )
        semantic = {
            "schema": SCHEMA,
            "institution_id": institution,
            "log_id": log,
            "leaf_count": count,
            "leaf_commitments": list(commitments),
            "merkle_root": root,
            "previous_checkpoint_hash": previous_hash,
        }
        checkpoint_hash = hashlib.sha3_256(
            _PREFIX + canonical_json_bytes(semantic)
        ).hexdigest()
        return cls(
            schema=SCHEMA,
            institution_id=institution,
            log_id=log,
            leaf_count=count,
            leaf_commitments=commitments,
            merkle_root=root,
            previous_checkpoint_hash=previous_hash,
            checkpoint_hash=checkpoint_hash,
        )

    @classmethod
    def from_dict(
        cls, document: Mapping[str, Any]
    ) -> EngineeringMerkleCheckpoint:
        if type(document) is not dict:
            raise TypeError("EXACT_CHECKPOINT_DOCUMENT_REQUIRED")
        if set(document) != _FIELDS:
            raise ValueError("INVALID_CHECKPOINT_FIELD_SET")
        data = dict(document)
        if type(data["leaf_commitments"]) is not list:
            raise TypeError("CANONICAL_PERSISTED_COMMITMENTS_REQUIRED")
        data["leaf_commitments"] = tuple(data["leaf_commitments"])
        return cls(**data)


def verify_checkpoint_extension(
    old: EngineeringMerkleCheckpoint,
    new: EngineeringMerkleCheckpoint,
    old_events: list[bytes],
    new_events: list[bytes],
) -> bool:
    """Check complete-history prefix consistency without trusted signing."""
    try:
        if type(old) is not EngineeringMerkleCheckpoint:
            return False
        if type(new) is not EngineeringMerkleCheckpoint:
            return False
        if type(old_events) is not list or type(new_events) is not list:
            return False
        if (
            old.institution_id != new.institution_id
            or old.log_id != new.log_id
            or new.previous_checkpoint_hash != old.checkpoint_hash
            or new.leaf_count <= old.leaf_count
            or len(old_events) != old.leaf_count
            or len(new_events) != new.leaf_count
            or new_events[:len(old_events)] != old_events
        ):
            return False
        old_commitments = tuple(leaf_hash(item) for item in old_events)
        new_commitments = tuple(leaf_hash(item) for item in new_events)
        return (
            old_commitments == old.leaf_commitments
            and new_commitments == new.leaf_commitments
            and new_commitments[:old.leaf_count] == old_commitments
            and merkle_root(old_events) == old.merkle_root
            and merkle_root(new_events) == new.merkle_root
            and old.expected_hash() == old.checkpoint_hash
            and new.expected_hash() == new.checkpoint_hash
        )
    except (TypeError, ValueError, OverflowError):
        return False


# ARTIFACT: ENGINEERING MERKLE CHECKPOINT HISTORY DOMAIN
# VERSION: 1.0.0-EMP-P16
# AUTHORITY BOUNDARY: HISTORY CONSISTENCY, NOT TRUSTED ANCHORING
# TENANT POSTURE: EXPLICIT INSTITUTION AND LOG SCOPE
# FAIL-CLOSED POSTURE: REORDER, SUBSTITUTION, ROOT FORGERY REJECTED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
