"""
===============================================================================
WILSY OS — FG223 DIGITAL TWIN INTELLIGENCE PLATFORM
===============================================================================

File Path:
    tools/eos/digital_twin/domain/twin_snapshot.py

Epitome:
    Defines the immutable state snapshot artifact for the Digital Twin Knowledge Graph.
    Captures complete point-in-time state of all entities and relationships across
    all observable subsystems, backed by cryptographic Merkle root hashes and SHA-256
    integrity digests for historical replay and audit verification.

Biblical Worth Billions:
    "Bind up the testimony, seal the law among my disciples."
    — Isaiah 8:16

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import hashlib
import json
import time
from typing import Dict, List, Any, Optional, Tuple


class TwinSnapshot:
    """
    An immutable point-in-time snapshot of the Digital Twin Knowledge Graph.
    """

    def __init__(
        self,
        snapshot_id: str,
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ):
        if not snapshot_id:
            raise ValueError("TwinSnapshot requires a valid snapshot_id.")

        self._snapshot_id = snapshot_id
        self._timestamp = time.time()
        self._entities = entities or []
        self._relationships = relationships or []
        self._metadata = metadata or {}

        self._snapshot_hash, self._merkle_root = self._compute_cryptographic_proofs()

    @property
    def snapshot_id(self) -> str:
        return self._snapshot_id

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def entities_count(self) -> int:
        return len(self._entities)

    @property
    def relationships_count(self) -> int:
        return len(self._relationships)

    @property
    def snapshot_hash(self) -> str:
        return self._snapshot_hash

    @property
    def merkle_root(self) -> str:
        return self._merkle_root

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata

    def _compute_cryptographic_proofs(self) -> Tuple[str, str]:
        try:
            entity_hashes = sorted([e.get("state_hash", "") for e in self._entities if "state_hash" in e])
            rel_hashes = sorted([r.get("relationship_hash", "") for r in self._relationships if "relationship_hash" in r])

            leaf_hashes = entity_hashes + rel_hashes
            if not leaf_hashes:
                empty_digest = hashlib.sha256(b"EMPTY_GRAPH_SNAPSHOT").hexdigest()
                return empty_digest, empty_digest

            current_level = leaf_hashes
            while len(current_level) > 1:
                if len(current_level) % 2 != 0:
                    current_level.append(current_level[-1])
                next_level = []
                for i in range(0, len(current_level), 2):
                    combined = (current_level[i] + current_level[i + 1]).encode('utf-8')
                    next_level.append(hashlib.sha256(combined).hexdigest())
                current_level = next_level

            merkle_root = current_level[0]

            payload = {
                "snapshot_id": self._snapshot_id,
                "entities_count": len(self._entities),
                "relationships_count": len(self._relationships),
                "merkle_root": merkle_root,
                "metadata": self._metadata
            }
            serialized = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            snapshot_hash = hashlib.sha256(serialized.encode('utf-8')).hexdigest()

            return snapshot_hash, merkle_root
        except Exception as e:
            raise RuntimeError(f"Cryptographic proof calculation failed for Snapshot [{self._snapshot_id}]: {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self._snapshot_id,
            "timestamp": self._timestamp,
            "entities_count": self.entities_count,
            "entity_count": self.entities_count,
            "relationships_count": self.relationships_count,
            "relationship_count": self.relationships_count,
            "entities": self._entities,
            "relationships": self._relationships,
            "metadata": self._metadata,
            "snapshot_hash": self._snapshot_hash,
            "sha3_hash": self._snapshot_hash,
            "merkle_root": self._merkle_root
        }
