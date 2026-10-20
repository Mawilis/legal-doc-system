"""
WILSY OS — IMMUTABLE ENGINEERING MERKLE PROOF RECORD
VERSION: 1.0.0-EMP-P7
AUTHORITY: Engineering Kernel evidence domain.
EPITOME: Immutable, verifiable evidence identity and Merkle inclusion metadata.
ABSOLUTE CANONICAL PATH: tools/eos/kernel/engineering_merkle_proof_record.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: 1.0.0-EMP-P7 — Immutable proof-record V1 contract.
COMPLIANCE: EK-001, EK-002, EK-003, EK-006, EK-007.
SECURITY: SHA3-256 provenance, exact schema, fail-closed hydration.
TENANT BOUNDARY: Explicit institution_id; never inferred from ambient state.
AUTHORITY BOUNDARY: No database, signing, release approval, or anchoring.
FINANCIAL AUTHORITY BOUNDARY: None.

The provenance hash authenticates internal data consistency only.
It is not a digital signature or an institutional anchoring receipt.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Any, Mapping

from tools.eos.kernel.engineering_merkle_proof import (
    canonical_json_bytes,
    leaf_hash,
    verify_inclusion_proof,
)

SCHEMA = "WILSY-ENGINEERING-MERKLE-PROOF-RECORD/V1"
_HEX64 = re.compile(r"[0-9a-f]{64}", re.ASCII)
_GIT40 = re.compile(r"[0-9a-f]{40}", re.ASCII)
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", re.ASCII)

_FIELDS = frozenset({
    "schema", "institution_id", "release_id", "evidence_id",
    "git_head", "evidence_digest", "leaf_commitment",
    "leaf_index", "leaf_count", "proof", "merkle_root",
    "provenance_hash",
})


def _identifier(name: str, value: object) -> str:
    """Validate an explicit, canonical institutional evidence identifier."""
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise ValueError("INVALID_" + name.upper())
    return value


def _hex(name: str, value: object, pattern: re.Pattern[str]) -> str:
    """Require exact lowercase hexadecimal digest representation."""
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise ValueError("INVALID_" + name.upper())
    return value


def _shape(index: object, count: object) -> tuple[int, int]:
    """Validate integer Merkle position and positive leaf count."""
    if (
        type(index) is not int
        or type(count) is not int
        or count < 1
        or not 0 <= index < count
    ):
        raise ValueError("INVALID_MERKLE_POSITION")
    return index, count


def _proof(values: object) -> tuple[str, ...]:
    """Validate an immutable ordered vector of canonical sibling digests."""
    if not isinstance(values, (tuple, list)):
        raise TypeError("INVALID_PROOF_CONTAINER")
    if type(values) not in (tuple, list):
        raise TypeError("INVALID_PROOF_CONTAINER")
    return tuple(_hex("sibling", v, _HEX64) for v in values)


def _path_root(
    leaf: str,
    index: int,
    count: int,
    siblings: tuple[str, ...],
) -> str:
    """Reconstruct the declared V1 tree path without raw evidence bytes."""
    from tools.eos.kernel.engineering_merkle_proof import parent_hash

    current = leaf
    position = index
    width = count
    offset = 0

    while width > 1:
        if offset >= len(siblings):
            raise ValueError("INCLUSION_PROOF_TOO_SHORT")
        sibling = siblings[offset]

        if position % 2 == 0:
            if position + 1 >= width and sibling != current:
                raise ValueError("INVALID_ODD_TAIL_DUPLICATION")
            current = parent_hash(current, sibling)
        else:
            current = parent_hash(sibling, current)

        position //= 2
        width = (width + 1) // 2
        offset += 1

    if offset != len(siblings):
        raise ValueError("INCLUSION_PROOF_TOO_LONG")
    return current


@dataclass(frozen=True, slots=True)
class EngineeringMerkleProofRecord:
    """Immutable consistency-verified engineering evidence claim.

    No authority is granted to register, approve, or anchor this record.
    """

    schema: str
    institution_id: str
    release_id: str
    evidence_id: str
    git_head: str
    evidence_digest: str
    leaf_commitment: str
    leaf_index: int
    leaf_count: int
    proof: tuple[str, ...]
    merkle_root: str
    provenance_hash: str

    def __post_init__(self) -> None:
        """Fail closed on invalid or altered persisted record state."""
        if self.schema != SCHEMA:
            raise ValueError("INVALID_RECORD_SCHEMA")
        for name in ("institution_id", "release_id", "evidence_id"):
            _identifier(name, getattr(self, name))
        _hex("git_head", self.git_head, _GIT40)
        _hex("evidence_digest", self.evidence_digest, _HEX64)
        _hex("leaf_commitment", self.leaf_commitment, _HEX64)
        _hex("merkle_root", self.merkle_root, _HEX64)
        _hex("provenance_hash", self.provenance_hash, _HEX64)
        index, count = _shape(self.leaf_index, self.leaf_count)
        if type(self.proof) is not tuple:
            raise TypeError("PROOF_MUST_BE_IMMUTABLE")
        siblings = _proof(self.proof)
        if _path_root(
            self.leaf_commitment, index, count, siblings
        ) != self.merkle_root:
            raise ValueError("MERKLE_ROOT_MISMATCH")
        if self.provenance_hash != self.expected_provenance_hash():
            raise ValueError("PROVENANCE_HASH_MISMATCH")

    def semantic_payload(self) -> dict[str, Any]:
        """Return the complete versioned semantic payload excluding its hash."""
        return {
            "schema": self.schema,
            "institution_id": self.institution_id,
            "release_id": self.release_id,
            "evidence_id": self.evidence_id,
            "git_head": self.git_head,
            "evidence_digest": self.evidence_digest,
            "leaf_commitment": self.leaf_commitment,
            "leaf_index": self.leaf_index,
            "leaf_count": self.leaf_count,
            "proof": list(self.proof),
            "merkle_root": self.merkle_root,
        }

    def expected_provenance_hash(self) -> str:
        """Compute versioned SHA3-256 semantic record identity."""
        return hashlib.sha3_256(
            b"WILSY:ENGINEERING:PROOF-RECORD:V1\x00"
            + canonical_json_bytes(self.semantic_payload())
        ).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Serialize the exact immutable record without adding authority claims."""
        return {
            **self.semantic_payload(),
            "provenance_hash": self.provenance_hash,
        }

    @classmethod
    def create(
        cls,
        *,
        institution_id: str,
        release_id: str,
        evidence_id: str,
        git_head: str,
        evidence: bytes,
        leaf_index: int,
        leaf_count: int,
        proof: tuple[str, ...] | list[str],
        merkle_root: str,
    ) -> EngineeringMerkleProofRecord:
        """Construct only if supplied evidence verifies against the Merkle root."""
        if type(evidence) is not bytes:
            raise TypeError("IMMUTABLE_EVIDENCE_BYTES_REQUIRED")
        index, count = _shape(leaf_index, leaf_count)
        siblings = _proof(proof)
        if not verify_inclusion_proof(
            evidence, index, count, siblings, merkle_root
        ):
            raise ValueError("INVALID_EVIDENCE_INCLUSION")

        payload = {
            "schema": SCHEMA,
            "institution_id": _identifier("institution_id", institution_id),
            "release_id": _identifier("release_id", release_id),
            "evidence_id": _identifier("evidence_id", evidence_id),
            "git_head": _hex("git_head", git_head, _GIT40),
            "evidence_digest": hashlib.sha3_256(evidence).hexdigest(),
            "leaf_commitment": leaf_hash(evidence),
            "leaf_index": index,
            "leaf_count": count,
            "proof": siblings,
            "merkle_root": _hex("merkle_root", merkle_root, _HEX64),
        }
        semantic = {
            **payload,
            "proof": list(siblings),
        }
        digest = hashlib.sha3_256(
            b"WILSY:ENGINEERING:PROOF-RECORD:V1\x00"
            + canonical_json_bytes(semantic)
        ).hexdigest()
        return cls(**payload, provenance_hash=digest)

    @classmethod
    def from_dict(
        cls,
        document: Mapping[str, Any],
    ) -> EngineeringMerkleProofRecord:
        """Hydrate strictly; reject missing, extra, or forged persisted fields."""
        if type(document) is not dict:
            raise TypeError("EXACT_DOCUMENT_REQUIRED")
        if set(document) != _FIELDS:
            raise ValueError("INVALID_PROOF_RECORD_FIELD_SET")
        data = dict(document)
        if type(data["proof"]) is not list:
            raise TypeError("CANONICAL_PERSISTED_PROOF_LIST_REQUIRED")
        data["proof"] = _proof(data["proof"])
        return cls(**data)

    def verify(self, evidence: bytes) -> bool:
        """Verify raw evidence matches this immutable Merkle proof claim."""
        try:
            return (
                type(evidence) is bytes
                and hashlib.sha3_256(evidence).hexdigest()
                    == self.evidence_digest
                and leaf_hash(evidence) == self.leaf_commitment
                and verify_inclusion_proof(
                    evidence, self.leaf_index, self.leaf_count,
                    self.proof, self.merkle_root,
                )
                and self.expected_provenance_hash()
                    == self.provenance_hash
            )
        except (TypeError, ValueError):
            return False


# ARTIFACT: IMMUTABLE ENGINEERING MERKLE PROOF RECORD
# VERSION: 1.0.0-EMP-P7
# AUTHORITY BOUNDARY: PURE DOMAIN; NO REGISTRATION OR ANCHORING
# TENANT POSTURE: EXPLICIT INSTITUTIONAL IDENTITY
# FAIL-CLOSED POSTURE: STRICT HYDRATION AND INCLUSION VALIDATION
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
