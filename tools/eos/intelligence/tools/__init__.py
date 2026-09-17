"""WILSY OS C1C server-owned AI tool package.

TITLE: Governed AI Tools
VERSION: v1.0.0-C1C-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Exposes only server-registered, immutable read-only tool metadata.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/tools/__init__.py
COLLABORATION / OWNERSHIP: C1C registry owns membership; adapters execute
                            canonical domain reads.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1C-R1 establishes the server-owned tool namespace.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No provider or caller registration.
TENANT BOUNDARY: Tool execution receives server-authenticated tenant context.
AUTHORITY BOUNDARY: Read-only legal projection composition.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Unknown or malformed tool contracts reject.
"""
from .registry import ServerOwnedAIToolRegistry, RegisteredAITool

__all__ = ["ServerOwnedAIToolRegistry", "RegisteredAITool"]

# ARTIFACT: tools/__init__.py
# VERSION: v1.0.0-C1C-R1
# AUTHORITY BOUNDARY: server-owned read-only tool namespace
# FAIL-CLOSED POSTURE: no dynamic registration
# END OF WILSY OS SOVEREIGN ARTIFACT
