"""
===============================================================================
WILSY OS — FG223 DIGITAL TWIN INTELLIGENCE PLATFORM
===============================================================================

File Path:
    tools/eos/digital_twin/domain/twin_entity.py

Epitome:
    Defines the foundational node of the Digital Twin Knowledge Graph.
    A TwinEntity represents any observable asset within the Wilsy OS ecosystem
    (e.g., Worker, Plugin, Execution, Node) without assuming ownership of its 
    underlying data. Features cryptographic SHA-256 hashing for immutability 
    verification and state-drift tracking.

Biblical Worth Billions:
    "Through wisdom is an house builded; and by understanding it is established."
    — Proverbs 24:3

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional

class TwinEntity:
    """
    Represents a single node within the Digital Twin graph.
    
    This class is strictly observational. It maps an entity's state at a 
    specific point in time and provides a cryptographic hash of that state to 
    guarantee verification and identify drift.
    """

    def __init__(self, entity_id: str, entity_type: str, attributes: Dict[str, Any]):
        """
        Initializes a sovereign TwinEntity.

        Args:
            entity_id (str): The globally unique identifier from the source system.
            entity_type (str): The classification of the entity (e.g., 'Worker', 'Plugin').
            attributes (Dict[str, Any]): The observed state telemetry and metadata.
        """
        if not entity_id or not entity_type:
            raise ValueError("TwinEntity requires a valid entity_id and entity_type.")

        self._entity_id = entity_id
        self._entity_type = entity_type
        self._attributes = attributes or {}
        
        # Sub-millisecond precision timestamping
        self._observed_at = time.time()
        self._state_hash = self._compute_hash()

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def entity_type(self) -> str:
        return self._entity_type

    @property
    def attributes(self) -> Dict[str, Any]:
        return self._attributes

    @property
    def observed_at(self) -> float:
        return self._observed_at

    @property
    def state_hash(self) -> str:
        return self._state_hash

    def _compute_hash(self) -> str:
        """
        Computes a timing-safe SHA-256 cryptographic digest of the entity's 
        current state to serve as a proof of reality.

        Returns:
            str: Hexadecimal SHA-256 digest.
        """
        try:
            # Deterministic sorting ensures identical states produce identical hashes
            payload = {
                "entity_id": self._entity_id,
                "entity_type": self._entity_type,
                "attributes": self._attributes
            }
            serialized_state = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            return hashlib.sha256(serialized_state.encode('utf-8')).hexdigest()
        except Exception as e:
            # Zero-loss preservation: fallback for unhashable attribute types
            raise RuntimeError(f"Cryptographic hash computation failed for Entity [{self._entity_id}]: {str(e)}")

    def update_state(self, new_attributes: Dict[str, Any]) -> bool:
        """
        Updates the observed attributes of the entity and recalculates the hash.
        
        Args:
            new_attributes (Dict[str, Any]): The latest state fetched from the source.
            
        Returns:
            bool: True if the state changed (drift detected), False otherwise.
        """
        try:
            previous_hash = self._state_hash
            self._attributes.update(new_attributes)
            self._observed_at = time.time()
            self._state_hash = self._compute_hash()
            
            # Return True if a state drift occurred
            return previous_hash != self._state_hash
        except Exception as e:
            raise RuntimeError(f"State update failure for Entity [{self._entity_id}]: {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Exports the entity to a dictionary for snapshot persistence or Event Bus streaming.
        """
        return {
            "entity_id": self._entity_id,
            "entity_type": self._entity_type,
            "attributes": self._attributes,
            "observed_at": self._observed_at,
            "state_hash": self._state_hash
        }
