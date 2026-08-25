"""
===============================================================================
WILSY OS — FG223 DIGITAL TWIN INTELLIGENCE PLATFORM
===============================================================================

File Path:
    tools/eos/digital_twin/domain/twin_state.py

Epitome:
    Encapsulates the synchronized in-memory topology state vector of the Digital
    Twin Knowledge Graph. Maintains living entity and relationship indexes,
    tracks architectural drift, and generates real-time state integrity metrics.

Biblical Worth Billions:
    "That which hath been is now; and that which is to be hath already been; 
    and God requireth that which is past."
    — Ecclesiastes 3:15

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import time
from typing import Dict, List, Optional, Set, Tuple, Any
from tools.eos.digital_twin.domain.twin_entity import TwinEntity
from tools.eos.digital_twin.domain.twin_relationship import TwinRelationship


class TwinState:
    """
    Maintains the active in-memory graph state across all Wilsy OS entities and edges.
    
    This class is observational and data-agnostic. It indexes entities by ID/type
    and relationships by ID/predicate/source/target for sub-millisecond query evaluation.
    """

    def __init__(self):
        """Initializes an empty TwinState container."""
        self._entities: Dict[str, TwinEntity] = {}
        self._relationships: Dict[str, TwinRelationship] = {}
        
        # Indexes for sub-millisecond O(1) query lookups
        self._entities_by_type: Dict[str, Set[str]] = {}
        self._relationships_by_source: Dict[str, Set[str]] = {}
        self._relationships_by_target: Dict[str, Set[str]] = {}
        self._relationships_by_predicate: Dict[str, Set[str]] = {}

        self._last_updated: float = time.time()
        self._drift_counter: int = 0

    @property
    def entity_count(self) -> int:
        return len(self._entities)

    @property
    def relationship_count(self) -> int:
        return len(self._relationships)

    @property
    def drift_count(self) -> int:
        return self._drift_counter

    @property
    def last_updated(self) -> float:
        return self._last_updated

    def upsert_entity(self, entity: TwinEntity) -> bool:
        """
        Registers or updates an entity in the living state.

        Args:
            entity (TwinEntity): The entity node to upsert.

        Returns:
            bool: True if an existing entity experienced state drift, False if new or unchanged.
        """
        if not isinstance(entity, TwinEntity):
            raise TypeError("upsert_entity requires a valid TwinEntity instance.")

        entity_id = entity.entity_id
        entity_type = entity.entity_type
        is_drift = False

        if entity_id in self._entities:
            existing = self._entities[entity_id]
            if existing.state_hash != entity.state_hash:
                is_drift = True
                self._drift_counter += 1
        else:
            # Index new entity type
            if entity_type not in self._entities_by_type:
                self._entities_by_type[entity_type] = set()
            self._entities_by_type[entity_type].add(entity_id)

        self._entities[entity_id] = entity
        self._last_updated = time.time()
        return is_drift

    def upsert_relationship(self, relationship: TwinRelationship) -> bool:
        """
        Registers or updates a relationship edge in the living state.

        Args:
            relationship (TwinRelationship): The relationship edge to upsert.

        Returns:
            bool: True if edge updated (drift), False if new or unchanged.
        """
        if not isinstance(relationship, TwinRelationship):
            raise TypeError("upsert_relationship requires a valid TwinRelationship instance.")

        rel_id = relationship.relationship_id
        src_id = relationship.source_id
        tgt_id = relationship.target_id
        predicate = relationship.predicate
        is_drift = False

        if rel_id in self._relationships:
            existing = self._relationships[rel_id]
            if existing.relationship_hash != relationship.relationship_hash:
                is_drift = True
                self._drift_counter += 1
        else:
            # Index edge endpoints and predicate
            if src_id not in self._relationships_by_source:
                self._relationships_by_source[src_id] = set()
            self._relationships_by_source[src_id].add(rel_id)

            if tgt_id not in self._relationships_by_target:
                self._relationships_by_target[tgt_id] = set()
            self._relationships_by_target[tgt_id].add(rel_id)

            if predicate not in self._relationships_by_predicate:
                self._relationships_by_predicate[predicate] = set()
            self._relationships_by_predicate[predicate].add(rel_id)

        self._relationships[rel_id] = relationship
        self._last_updated = time.time()
        return is_drift

    def get_entity(self, entity_id: str) -> Optional[TwinEntity]:
        return self._entities.get(entity_id)

    def get_relationship(self, relationship_id: str) -> Optional[TwinRelationship]:
        return self._relationships.get(relationship_id)

    def get_entities_by_type(self, entity_type: str) -> List[TwinEntity]:
        entity_ids = self._entities_by_type.get(entity_type, set())
        return [self._entities[eid] for eid in entity_ids if eid in self._entities]

    def get_outgoing_relationships(self, source_id: str) -> List[TwinRelationship]:
        rel_ids = self._relationships_by_source.get(source_id, set())
        return [self._relationships[rid] for rid in rel_ids if rid in self._relationships]

    def get_incoming_relationships(self, target_id: str) -> List[TwinRelationship]:
        rel_ids = self._relationships_by_target.get(target_id, set())
        return [self._relationships[rid] for rid in rel_ids if rid in self._relationships]

    def export_serialized_state(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Exports all entities and relationships as dictionaries for snapshot generation.
        """
        entities_serialized = [e.to_dict() for e in self._entities.values()]
        relationships_serialized = [r.to_dict() for r in self._relationships.values()]
        return entities_serialized, relationships_serialized
