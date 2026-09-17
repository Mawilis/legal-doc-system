"""WILSY OS C1C immutable server-owned AI tool registry."""
from __future__ import annotations

"""TITLE: Server-Owned AI Tool Registry
VERSION: v1.0.0-C1C-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Binds immutable tool contracts to trusted server adapters; model
         output and HTTP callers cannot register or alter membership.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/tools/registry.py
COLLABORATION / OWNERSHIP: C1C orchestration consumes this registry; legal
                            adapters remain canonical read implementations.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1C-R1 adds duplicate/malformed/unknown fail-closed gates.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No network, provider, secret, or caller registration.
TENANT BOUNDARY: Adapter invocation is explicitly scoped by orchestrator.
AUTHORITY BOUNDARY: Tool membership metadata only; read-only execution binding.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Registry is immutable after construction.
"""
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable
from tools.eos.intelligence.domain.ai_tool_orchestration import AIToolContract, ToolRiskClass, AIToolOrchestrationError


class AIToolRegistryError(ValueError):
    """Stable server registry error."""


@dataclass(frozen=True, slots=True)
class RegisteredAITool:
    """Contract plus trusted adapter callable, never exposed to model JSON."""
    contract: AIToolContract
    adapter: Callable[..., Any]

    def __post_init__(self) -> None:
        if not isinstance(self.contract, AIToolContract) or self.contract.risk_class is not ToolRiskClass.READ_ONLY or not callable(self.adapter):
            raise AIToolRegistryError("C1C_TOOL_REGISTRATION_INVALID")


class ServerOwnedAIToolRegistry:
    """Immutable allowlist built once by the application composition root."""

    __slots__ = ("_tools", "_sealed")

    def __init__(self, registrations: tuple[RegisteredAITool, ...] = ()) -> None:
        if not isinstance(registrations, tuple):
            raise AIToolRegistryError("C1C_REGISTRY_INPUT_INVALID")
        values: dict[str, RegisteredAITool] = {}
        for item in registrations:
            if not isinstance(item, RegisteredAITool) or item.contract.identity in values:
                raise AIToolRegistryError("C1C_DUPLICATE_TOOL")
            values[item.contract.identity] = item
        self._tools = MappingProxyType(values)
        self._sealed = True

    @property
    def contracts(self) -> tuple[AIToolContract, ...]:
        """Return an immutable ordered contract snapshot."""
        return tuple(item.contract for item in self._tools.values())

    def get(self, identity: str) -> RegisteredAITool:
        """Return one known tool or fail closed."""
        try:
            return self._tools[identity]
        except (KeyError, TypeError) as error:
            raise AIToolRegistryError("C1C_TOOL_UNKNOWN") from error

    def contains(self, identity: str) -> bool:
        """Check membership without exposing adapter internals."""
        return isinstance(identity, str) and identity in self._tools

    def register(self, *_args: Any, **_kwargs: Any) -> None:
        """Reject runtime mutation; server composition is the sole owner."""
        raise AIToolRegistryError("C1C_DYNAMIC_REGISTRATION_FORBIDDEN")


__all__ = ["AIToolRegistryError", "RegisteredAITool", "ServerOwnedAIToolRegistry"]

# ARTIFACT: registry.py
# VERSION: v1.0.0-C1C-R1
# AUTHORITY BOUNDARY: immutable server-owned read-only tool membership
# FAIL-CLOSED POSTURE: duplicates, unknowns and dynamic registration reject
# END OF WILSY OS SOVEREIGN ARTIFACT
