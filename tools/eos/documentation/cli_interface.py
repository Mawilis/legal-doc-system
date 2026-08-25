"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/cli_interface.py
===============================================================================
Epitome:
    Command-Line Interface (CLI) harness for FG210 Documentation Engine.
    Provides terminal entrypoints for searching, querying URNs, building
    compliance audit reports, and exporting system documentation.

Biblical Worth Billions:
    "Write the vision, and make it plain upon tables, that he may run that
     readeth it." — Habakkuk 2:2

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/cli_interface.py
===============================================================================
"""

import sys
import argparse
from typing import List
from tools.eos.documentation.registry import DocumentationRegistry
from tools.eos.documentation.search_index import DocumentationSearchIndex
from tools.eos.documentation.export_engine import DocumentationExportEngine
from tools.eos.documentation.verification_documentation import (
    VerificationDocumentationGenerator,
)


class DocumentationCLI:
    """
    Terminal CLI controller for querying, exporting, and auditing documentation entities.
    """

    def __init__(self) -> None:
        self.registry = DocumentationRegistry()

    def run(self, args: List[str]) -> int:
        """
        Parses CLI arguments and dispatches command actions.

        Args:
            args: Raw CLI argument tokens.

        Returns:
            Exit code integer (0 for success, non-zero for failure).
        """
        parser = argparse.ArgumentParser(
            description="Wilsy OS — FG210 Institutional Documentation Engine CLI"
        )
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Command: list
        subparsers.add_parser("list", help="List all registered documentation entities")

        # Command: search
        search_parser = subparsers.add_parser("search", help="Search documentation entities")
        search_parser.add_argument("query", type=str, help="Search query string")

        # Command: export
        export_parser = subparsers.add_parser("export", help="Export documentation manual")
        export_parser.add_argument(
            "--format",
            type=str,
            choices=["json", "markdown", "html"],
            default="markdown",
            help="Export format (default: markdown)",
        )

        # Command: audit
        subparsers.add_parser("audit", help="Run institutional verification audit report")

        parsed = parser.parse_args(args)

        if parsed.command == "list":
            entities = self.registry.list_all()
            print(f"Registered Entities ({len(entities)}):")
            for e in entities:
                print(f"  - [{e.kind.value}] {e.urn} -> {e.title}")
            return 0

        elif parsed.command == "search":
            search_index = DocumentationSearchIndex(self.registry.list_all())
            hits = search_index.search(parsed.query)
            print(f"Search Results for '{parsed.query}' ({len(hits)} matches):")
            for h in hits:
                print(f"  - [{h['score']}] {h['urn']} ({h['title']})")
            return 0

        elif parsed.command == "export":
            entities = self.registry.list_all()
            if parsed.format == "json":
                print(DocumentationExportEngine.export_to_json(entities))
            elif parsed.format == "html":
                print(DocumentationExportEngine.export_to_html(entities))
            else:
                print(DocumentationExportEngine.export_to_markdown(entities))
            return 0

        elif parsed.command == "audit":
            entities = self.registry.list_all()
            report = VerificationDocumentationGenerator.generate_verification_audit_report(
                entities
            )
            print(f"Institutional Audit Report:")
            print(f"  - Total Entities: {report['total_entities']}")
            print(f"  - Verified: {report['verified_count']}")
            print(f"  - Compliance: {report['compliance_percentage']}%")
            return 0

        else:
            parser.print_help()
            return 1


def main() -> None:
    cli = DocumentationCLI()
    sys.exit(cli.run(sys.argv[1:]))


if __name__ == "__main__":
    main()
