"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/documentation_generator.py
===============================================================================
Epitome:
    Core generation engine that transforms registered DocumentationEntity metadata
    into human-readable and machine-parseable documentation formats. Ensures
    that no documentation is ever handwritten after component registration.

Biblical Worth Billions:
    "Ready writer, speaking of the things which I have made touching the king."
    — Psalm 45:1

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/documentation_generator.py
===============================================================================
"""

from typing import Dict, Any, List
from tools.eos.documentation.documentation_contract import DocumentationEntity, EntityKind


class DocumentationGenerator:
    """
    Converts raw DocumentationEntity contracts into canonical structured Markdown
    and text documentation blocks adhering to the Wilsy OS institutional schema.
    """

    @staticmethod
    def generate_markdown(entity: DocumentationEntity) -> str:
        """
        Generates a standard institutional Markdown document from a DocumentationEntity.

        Args:
            entity: Validated DocumentationEntity contract.

        Returns:
            Formatted Markdown string.
        """
        md: List[str] = []

        # Header & Metadata
        md.append(f"# {entity.title}")
        md.append(f"**URN:** `{entity.urn}`  ")
        md.append(f"**Kind:** `{entity.kind.value}` | **Version:** `{entity.version}` | **Status:** `{entity.verification_status.value}`  ")
        md.append(f"**Module Path:** `{entity.module_path}`  ")
        md.append(f"**Lifecycle Stage:** `{entity.lifecycle_stage}`\n")

        md.append("---")
        md.append("## Purpose & Executive Summary\n")
        md.append(f"{entity.purpose}\n")

        md.append("## Architecture Summary\n")
        md.append(f"{entity.architecture_summary}\n")

        # Dependencies
        if entity.dependencies:
            md.append("## Dependencies\n")
            for dep in entity.dependencies:
                md.append(f"- `{dep}`")
            md.append("")

        # Interfaces
        if entity.interfaces:
            md.append("## Public Interfaces & Methods\n")
            md.append("| Name | Description | Return Type | Async |")
            md.append("| :--- | :--- | :--- | :--- |")
            for iface in entity.interfaces:
                async_str = "Yes" if iface.is_async else "No"
                desc = iface.description.replace("\n", " ")
                md.append(f"| `{iface.name}` | {desc} | `{iface.return_type}` | {async_str} |")
            md.append("")

        # Events
        if entity.events:
            md.append("## Sovereign Events\n")
            md.append("| Event Name | Publisher | Subscriber | Stage |")
            md.append("| :--- | :--- | :--- | :--- |")
            for evt in entity.events:
                md.append(f"| `{evt.event_name}` | `{evt.publisher}` | `{evt.subscriber}` | `{evt.lifecycle_stage}` |")
            md.append("")

        # Artifacts
        if entity.artifacts:
            md.append("## Output Artifacts\n")
            md.append("| Artifact Type | Producer | Consumer | Retention |")
            md.append("| :--- | :--- | :--- | :--- |")
            for art in entity.artifacts:
                md.append(f"| `{art.artifact_type}` | `{art.producer}` | `{art.consumer}` | `{art.retention_policy}` |")
            md.append("")

        # Governance
        if entity.governance_rules:
            md.append("## Governance & Enforcement Rules\n")
            md.append("| Policy ID | Title | Rule | Level |")
            md.append("| :--- | :--- | :--- | :--- |")
            for gov in entity.governance_rules:
                md.append(f"| `{gov.policy_id}` | {gov.title} | {gov.approval_rule} | `{gov.enforcement_level}` |")
            md.append("")

        # Examples
        if entity.examples:
            md.append("## Execution Examples\n")
            for ex in entity.examples:
                md.append(f"```python\n{ex}\n```\n")

        # Related Modules
        if entity.related_modules:
            md.append("## Related Modules\n")
            for rel in entity.related_modules:
                md.append(f"- `{rel}`")
            md.append("")

        md.append("---")
        md.append("*Generated automatically by Wilsy OS FG210 Institutional Documentation Engine.*")

        return "\n".join(md)
