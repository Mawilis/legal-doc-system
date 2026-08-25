"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/__init__.py
===============================================================================
Epitome:
    Core package initializer for the FG210 Documentation Engine.
    Exposes unified contract classes, generators, exporters, registry, and
    CLI harnesses for seamless integration across Wilsy OS.

Biblical Worth Billions:
    "For where two or three are gathered together in my name, there am I in
     the midst of them." — Matthew 18:20

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/__init__.py
===============================================================================
"""

from tools.eos.documentation.documentation_contract import (
    DocumentationEntity,
    EntityKind,
    VerificationStatus,
    InterfaceSpec,
    EventSpec,
)
from tools.eos.documentation.artifact_documentation import ArtifactDocumentationGenerator
from tools.eos.documentation.execution_documentation import ExecutionDocumentationGenerator
from tools.eos.documentation.verification_documentation import (
    VerificationDocumentationGenerator,
)
from tools.eos.documentation.export_engine import DocumentationExportEngine
from tools.eos.documentation.registry import DocumentationRegistry
from tools.eos.documentation.search_index import DocumentationSearchIndex
from tools.eos.documentation.diff_engine import DocumentationDiffEngine
from tools.eos.documentation.cli_interface import DocumentationCLI

__all__ = [
    "DocumentationEntity",
    "EntityKind",
    "VerificationStatus",
    "InterfaceSpec",
    "EventSpec",
    "ArtifactDocumentationGenerator",
    "ExecutionDocumentationGenerator",
    "VerificationDocumentationGenerator",
    "DocumentationExportEngine",
    "DocumentationRegistry",
    "DocumentationSearchIndex",
    "DocumentationDiffEngine",
    "DocumentationCLI",
]
