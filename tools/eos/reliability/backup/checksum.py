"""
===============================================================================
WILSY OS — CRYPTOGRAPHIC BACKUP CHECKSUM & MERKLE ROOT ENGINE
===============================================================================

File Path:
    tools/eos/reliability/backup/checksum.py

Epitome:
    Computes SHA3-256 digests and Merkle root proofs for immutable backup 
    manifest verification and artifact integrity assurance.

Biblical Worth Billions:
    "Prove all things; hold fast that which is good."
    — 1 Thessalonians 5:21

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import hashlib
import json
from typing import List, Dict, Any

class BackupChecksumEngine:
    """Provides cryptographic hashing and Merkle root generation for platform backups."""

    @staticmethod
    def compute_sha3(data: Dict[str, Any]) -> str:
        """Computes a SHA3-256 checksum for a structured data dictionary."""
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha3_256(serialized.encode('utf-8')).hexdigest()

    @staticmethod
    def compute_merkle_root(artifacts: List[str]) -> str:
        """Computes a Merkle tree root hash across a list of artifact checksums."""
        if not artifacts:
            return hashlib.sha3_256(b"EMPTY_BACKUP_MANIFEST").hexdigest()

        current_level = list(artifacts)
        while len(current_level) > 1:
            if len(current_level) % 2 != 0:
                current_level.append(current_level[-1])
            
            next_level = []
            for i in range(0, len(current_level), 2):
                combined = current_level[i] + current_level[i+1]
                parent = hashlib.sha3_256(combined.encode('utf-8')).hexdigest()
                next_level.append(parent)
            current_level = next_level

        return current_level[0]
