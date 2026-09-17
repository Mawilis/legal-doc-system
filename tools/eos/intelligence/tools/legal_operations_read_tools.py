"""WILSY OS C1C adapter bindings for the seven canonical legal read tools.

TITLE: Legal Operations Read Tool Bindings
VERSION: v1.0.0-C1C-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Reuses L7B contracts, LegalAIReadAdapter and invocation evidence;
         this module creates no legal collection or lifecycle authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/tools/legal_operations_read_tools.py
COLLABORATION / OWNERSHIP: L7B remains canonical adapter/evidence authority;
                            C1C registry owns server membership only.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1C-R1 maps exactly seven read-only legal contracts.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Results are transient; only L7B evidence refs persist.
TENANT BOUNDARY: Caller context is passed unchanged to L7B canonical reads.
AUTHORITY BOUNDARY: Legal read projection composition only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Unknown contracts and malformed projections reject.
"""
from __future__ import annotations

import asyncio
import inspect
from typing import Any, Mapping
from tools.eos.intelligence.domain.ai_tool_orchestration import AIToolContract, ToolRiskClass
from tools.eos.intelligence.domain.legal_ai_gateway import TOOL_CONTRACTS
from tools.eos.intelligence.domain.legal_ai_read_adapter import LegalAIReadAdapter, LegalAIReadAdapterError


def _contract(identity: str, source: Any) -> AIToolContract:
    return AIToolContract(identity=identity, version=source.version, domain="legal_operations",
                          capability=source.capability, underlying_permission=source.underlying_permission,
                          risk_class=ToolRiskClass.READ_ONLY, pii_class=source.pii_class,
                          argument_names=("resource_identity",))


TOOL_CONTRACTS_C1C: tuple[AIToolContract, ...] = tuple(_contract(identity, source) for identity, source in TOOL_CONTRACTS.items())
# Explicit C1C alias; values are immutable contract snapshots, not callables.
LEGAL_READ_TOOL_CONTRACTS = TOOL_CONTRACTS_C1C


class LegalOperationsReadToolAdapter:
    """Invoke the existing async L7B adapter without duplicating hydration."""

    __slots__ = ("_adapter",)

    def __init__(self, adapter: LegalAIReadAdapter | None = None) -> None:
        self._adapter = adapter or LegalAIReadAdapter()

    def read(self, *, contract: AIToolContract, resource_identity: str, context: Any, collections: Mapping[str, Any]) -> dict[str, object]:
        """Read one canonical projection, bridging async adapter on sync workers."""
        source = TOOL_CONTRACTS.get(contract.identity)
        if source is None or not isinstance(resource_identity, str) or not resource_identity.strip():
            raise LegalAIReadAdapterError("C1C_LEGAL_TOOL_INPUT_INVALID")
        result = self._adapter.read(contract=source, resource_identity=resource_identity, context=context, collections=collections)
        if inspect.isawaitable(result):
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                result = asyncio.run(result)
            else:
                raise LegalAIReadAdapterError("C1C_SYNC_WORKER_REQUIRED")
        if not isinstance(result, dict):
            raise LegalAIReadAdapterError("C1C_LEGAL_TOOL_RESULT_INVALID")
        return result


def build_legal_read_registrations(adapter: LegalOperationsReadToolAdapter | None = None) -> tuple[Any, ...]:
    """Return exactly seven server-owned read registrations."""
    from .registry import RegisteredAITool
    bound = adapter or LegalOperationsReadToolAdapter()
    return tuple(RegisteredAITool(contract=item, adapter=bound.read) for item in TOOL_CONTRACTS_C1C)


__all__ = ["TOOL_CONTRACTS_C1C", "LEGAL_READ_TOOL_CONTRACTS", "LegalOperationsReadToolAdapter", "build_legal_read_registrations"]

# ARTIFACT: legal_operations_read_tools.py
# VERSION: v1.0.0-C1C-R1
# AUTHORITY BOUNDARY: canonical L7B legal read adapter composition
# TENANT POSTURE: explicit authenticated context passed to L7B
# FAIL-CLOSED POSTURE: exactly seven read-only tools
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
