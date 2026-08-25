"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/architecture_documentation.py
===============================================================================
Epitome:
    Generates institutional architecture blueprints, subsystem maps, execution
    flow graphs, and dependency visualizers in Mermaid format directly from
    runtime metadata. Eliminates human drift in architecture diagrams.

Biblical Worth Billions:
    "According to all that I shew thee, after the pattern of the tabernacle,
     and the pattern of all the instruments thereof, even so shall ye make it."
    — Exodus 25:9

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/architecture_documentation.py
===============================================================================
"""

from typing import List, Dict, Any
from tools.eos.documentation.documentation_contract import DocumentationEntity, EntityKind


class ArchitectureDocumentationGenerator:
    """
    Generates structural architecture diagrams, subsystem relationship maps,
    and visual dependency graphs using standard Mermaid syntax.
    """

    @staticmethod
    def generate_mermaid_dependency_graph(entities: List[DocumentationEntity]) -> str:
        """
        Generates a Mermaid JS flowchart illustrating inter-subsystem dependencies.

        Args:
            entities: List of registered DocumentationEntity contracts.

        Returns:
            String containing formatted Mermaid syntax diagram.
        """
        lines: List[str] = ["graph TD", "    %% Wilsy OS Architecture Dependency Graph"]

        node_ids: Dict[str, str] = {}
        for idx, entity in enumerate(entities):
            clean_id = f"node_{idx}"
            node_ids[entity.urn] = clean_id
            lines.append(f'    {clean_id}["{entity.title}<br/><i>{entity.urn}</i>"]')

        for entity in entities:
            source_id = node_ids.get(entity.urn)
            if not source_id:
                continue

            for dep in entity.dependencies:
                target_id = node_ids.get(dep)
                if target_id:
                    lines.append(f"    {source_id} --> {target_id}")
                else:
                    ext_id = f"ext_{abs(hash(dep)) & 0xFFFFFF}"
                    lines.append(f'    {ext_id}["{dep}"]')
                    lines.append(f"    {source_id} -.-> {ext_id}")

        return "\n".join(lines)

    @staticmethod
    def generate_subsystem_map(entities: List[DocumentationEntity]) -> Dict[str, List[Dict[str, str]]]:
        """
        Groups documented entities by their EntityKind to form a structured subsystem catalog map.

        Args:
            entities: List of registered DocumentationEntity contracts.

        Returns:
            Dictionary mapping EntityKind values to lists of entity summary dicts.
        """
        subsystem_map: Dict[str, List[Dict[str, str]]] = {}

        for entity in entities:
            kind_key = entity.kind.value
            if kind_key not in subsystem_map:
                subsystem_map[kind_key] = []

            subsystem_map[kind_key].append({
                "urn": entity.urn,
                "title": entity.title,
                "module_path": entity.module_path,
                "version": entity.version,
                "status": entity.verification_status.value,
            })

        return subsystem_map
