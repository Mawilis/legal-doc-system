"""
===============================================================================
WILSY OS — FG223 DIGITAL TWIN INTELLIGENCE PLATFORM
===============================================================================

File Path:
    tools/eos/digital_twin/domain/twin_relationship.py

Epitome:
    Defines the directed relationship edge connecting TwinEntity nodes within the 
    Digital Twin Knowledge Graph. Captures semantic dependencies (e.g., CONTAINS, 
    EXECUTES, DEPENDS_ON, PRODUCES) with cryptographic hash integrity and state 
    drift detection capabilities.

Biblical Worth Billions:
    "That their hearts might be comforted, being knit together in love, and unto 
    all riches of the full assurance of understanding..."
    — Colossians 2:2

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional


class TwinRelationship:
    """
    Represents a directed relationship edge between two TwinEntity instances.
    
    Observational in nature; connects a source entity to a target entity via
    a strictly typed predicate verb alongside arbitrary metadata telemetry.
    """

    def __init__(
        self,
        relationship_id: str,
        source_id: str,
        target_id: str,
        predicate: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a sovereign TwinRelationship edge.

        Args:
            relationship_id (str): Unique identifier for the relationship edge.
            source_id (str): The origin TwinEntity identifier.
            target_id (str): The destination TwinEntity identifier.
            predicate (str): The semantic verb (e.g., 'DEPENDS_ON', 'EXECUTES').
            attributes (Optional[Dict[str, Any]]): Contextual relationship metadata.
        """
        if not relationship_id or not source_id or not target_id or not predicate:
            raise ValueError(
                "TwinRelationship requires relationship_id, source_id, target_id, and predicate."
            )

        self._relationship_id = relationship_id
        self._source_id = source_id
        self._target_id = target_id
        self._predicate = predicate.upper()
        self._attributes = attributes or {}
        self._created_at = time.time()
        self._relationship_hash = self._compute_hash()

    @property
    def relationship_id(self) -> str:
        return self._relationship_id

    @property
    def source_id(self) -> str:
        return self._source_id

    @property
    def target_id(self) -> str:
        return self._target_id

    @property
    def predicate(self) -> str:
        return self._predicate

    @property
    def attributes(self) -> Dict[str, Any]:
        return self._attributes

    @property
    def created_at(self) -> float:
        return self._created_at

    @property
    def relationship_hash(self) -> str:
        return self._relationship_hash

    def _compute_hash(self) -> str:
        """
        Computes a deterministic SHA-256 digest of the edge state for cryptographic attestation.

        Returns:
            str: Hexadecimal SHA-256 digest.
        """
        try:
            payload = {
                "relationship_id": self._relationship_id,
                "source_id": self._source_id,
                "target_id": self._target_id,
                "predicate": self._predicate,
                "attributes": self._attributes
            }
            serialized = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        except Exception as e:
            raise RuntimeError(f"Cryptographic calculation failed for Relationship [{self._relationship_id}]: {str(e)}")

    def update_attributes(self, new_attributes: Dict[str, Any]) -> bool:
        """
        Updates edge metadata and recalculates the cryptographic hash to detect drift.

        Args:
            new_attributes (Dict[str, Any]): Updated key-value metadata.

        Returns:
            bool: True if state drift occurred (hash changed), False otherwise.
        """
        try:
            previous_hash = self._relationship_hash
            self._attributes.update(new_attributes)
            self._relationship_hash = self._compute_hash()
            return previous_hash != self._relationship_hash
        except Exception as e:
            raise RuntimeError(f"Attribute update failure for Relationship [{self._relationship_id}]: {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Exports the relationship edge to a dictionary representation.
        """
        return {
            "relationship_id": self._relationship_id,
            "source_id": self._source_id,
            "target_id": self._target_id,
            "predicate": self._predicate,
            "attributes": self._attributes,
            "created_at": self._created_at,
            "relationship_hash": self._relationship_hash
        }
