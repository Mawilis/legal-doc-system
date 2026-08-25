"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/export_engine.py
===============================================================================
Epitome:
    Multi-format export engine for FG210 documentation entities. Converts
    in-memory DocumentationEntity contracts into institutional Markdown docs,
    structured JSON catalogs, and self-contained HTML blueprints.

Biblical Worth Billions:
    "And the Lord answered me, and said, Write the vision, and make it plain
     upon tables, that he may run that readeth it." — Habakkuk 2:2

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/export_engine.py
===============================================================================
"""

import json
from typing import List, Dict, Any
from tools.eos.documentation.documentation_contract import DocumentationEntity


class DocumentationExportEngine:
    """
    Renders registered documentation entities into Markdown, JSON, and HTML formats.
    """

    @staticmethod
    def export_to_json(entities: List[DocumentationEntity], indent: int = 2) -> str:
        """
        Exports a list of DocumentationEntity instances into a JSON string.

        Args:
            entities: Registered documentation entities.
            indent: Formatting indentation spaces.

        Returns:
            JSON formatted string.
        """
        payload = [entity.to_dict() for entity in entities]
        return json.dumps(payload, indent=indent, default=str)

    @staticmethod
    def export_to_markdown(entities: List[DocumentationEntity]) -> str:
        """
        Renders a comprehensive Markdown documentation manual for all provided entities.

        Args:
            entities: Registered documentation entities.

        Returns:
            Formatted Markdown document string.
        """
        md_lines: List[str] = [
            "# Wilsy OS — Institutional Architecture & System Documentation",
            "**Sovereign Operating System | FG210 Documentation Engine**",
            "",
            "---",
            "",
        ]

        for entity in entities:
            md_lines.extend([
                f"## {entity.title}",
                f"- **URN:** `{entity.urn}`",
                f"- **Kind:** `{entity.kind.value}`",
                f"- **Module Path:** `{entity.module_path}`",
                f"- **Version:** `{entity.version}`",
                f"- **Lifecycle Stage:** `{entity.lifecycle_stage}`",
                f"- **Verification Status:** `{entity.verification_status.value}`",
                "",
                "### Purpose",
                f"{entity.purpose}",
                "",
                "### Architecture Summary",
                f"{entity.architecture_summary}",
                "",
            ])

            if entity.interfaces:
                md_lines.append("### Interfaces")
                for iface in entity.interfaces:
                    async_str = " (Async)" if iface.is_async else ""
                    md_lines.append(f"- **`{iface.name}`**{async_str}: {iface.description}")
                    md_lines.append(f"  - Return Type: `{iface.return_type}`")
                md_lines.append("")

            if entity.events:
                md_lines.append("### Event Contracts")
                for evt in entity.events:
                    md_lines.append(f"- **Event:** `{evt.event_name}`")
                    md_lines.append(f"  - Publisher: `{evt.publisher}` | Subscriber: `{evt.subscriber}`")
                md_lines.append("")

            if entity.dependencies:
                md_lines.append("### Dependencies")
                for dep in entity.dependencies:
                    md_lines.append(f"- `{dep}`")
                md_lines.append("")

            md_lines.append("---")
            md_lines.append("")

        return "\n".join(md_lines)

    @staticmethod
    def export_to_html(entities: List[DocumentationEntity]) -> str:
        """
        Renders an institutional HTML status report containing all system entities.

        Args:
            entities: Registered documentation entities.

        Returns:
            Self-contained HTML string.
        """
        body_content = ""
        for entity in entities:
            body_content += f"""
            <div class="card">
                <h2>{entity.title}</h2>
                <p><strong>URN:</strong> <code>{entity.urn}</code> | <strong>Version:</strong> {entity.version}</p>
                <p><strong>Kind:</strong> {entity.kind.value} | <strong>Status:</strong> {entity.verification_status.value}</p>
                <p><strong>Module:</strong> <code>{entity.module_path}</code></p>
                <hr/>
                <p><strong>Purpose:</strong> {entity.purpose}</p>
                <p><strong>Architecture:</strong> {entity.architecture_summary}</p>
            </div>
            """

        html_str = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Wilsy OS — Institutional Documentation</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; }}
        h1 {{ color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 0.5rem; }}
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }}
        code {{ background: #0f172a; color: #38bdf8; padding: 0.2rem 0.4rem; border-radius: 4px; }}
        hr {{ border: 0; border-top: 1px solid #334155; margin: 1rem 0; }}
    </style>
</head>
<body>
    <h1>Wilsy OS — Architecture Catalog</h1>
    {body_content}
</body>
</html>"""
        return html_str
