"""WILSY OS C1C reusable reasoning service.

TITLE: WILSY AI Reasoning Service
VERSION: v1.0.0-C1C-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Provides one composition seam for the frozen C1B claim/execute/
         finalize lifecycle so HTTP and tool orchestration cannot fork it.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/wilsy_ai_reasoning_service.py
COLLABORATION / OWNERSHIP: C1B remains execution/admission authority; C1C
                            delegates without changing provider semantics.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1C-R1 exposes a dependency-injected canonical C1B service.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Prompt/provider material remains transient.
TENANT BOUNDARY: Delegated C1B calls retain explicit tenant scope.
AUTHORITY BOUNDARY: Reasoning evidence only; no legal or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Missing C1B composition is unavailable, never synthetic.
"""
from __future__ import annotations

from typing import Any
from tools.eos.intelligence.wilsy_ai_reasoning_orchestrator import WilsyAIReasoningOrchestrator


class WilsyAIReasoningServiceError(RuntimeError):
    """Stable service composition failure."""


class WilsyAIReasoningService:
    """Small façade retaining C1B caller-transaction ownership."""

    __slots__ = ("_orchestrator",)

    def __init__(self, orchestrator: WilsyAIReasoningOrchestrator) -> None:
        if not all(callable(getattr(orchestrator, name, None)) for name in ("claim", "execute", "finalize")):
            raise WilsyAIReasoningServiceError("C1C_REASONING_ORCHESTRATOR_REQUIRED")
        self._orchestrator = orchestrator

    @property
    def orchestrator(self) -> WilsyAIReasoningOrchestrator:
        """Return the already-composed C1B authority."""
        return self._orchestrator

    def claim(self, **kwargs: Any) -> Any:
        """Delegate one C1B claim; caller owns transaction lifecycle."""
        return self._orchestrator.claim(**kwargs)

    def execute(self, permit: Any, **kwargs: Any) -> Any:
        """Delegate one provider execution outside transaction scope."""
        return self._orchestrator.execute(permit, **kwargs)

    def finalize(self, attempt: Any, **kwargs: Any) -> Any:
        """Delegate one C1B finalization under a fresh caller transaction."""
        return self._orchestrator.finalize(attempt, **kwargs)


__all__ = ["WilsyAIReasoningService", "WilsyAIReasoningServiceError"]

# ARTIFACT: wilsy_ai_reasoning_service.py
# VERSION: v1.0.0-C1C-R1
# AUTHORITY BOUNDARY: C1B reasoning composition only
# TENANT POSTURE: delegated explicit tenant scope
# FAIL-CLOSED POSTURE: no synthetic provider or usage state
# END OF WILSY OS SOVEREIGN ARTIFACT
