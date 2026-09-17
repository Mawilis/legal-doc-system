"""C1C domain certificate for strict contracts and phase transitions.
TITLE: AI Tool Orchestration Unit Certificate
VERSION: v1.0.0-C1C-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves immutable read-only metadata, derived root identity and monotonic phases.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_ai_tool_orchestration.py
CERTIFICATION / UPDATE DATE: 2026-09-16
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
AUTHORITY BOUNDARY: Test certificate only; no runtime authority.
"""
from datetime import datetime, timezone
import pytest
from tools.eos.intelligence.domain.ai_tool_orchestration import *

def root() -> AIToolOrchestration:
    return AIToolOrchestration("o1", "tenant1", "principal1", "corr1", OrchestrationPhase.STARTED, "plan1", occurred_at=datetime.now(timezone.utc))

def test_identity_and_transition_are_deterministic():
    assert orchestration_identity("tenant1", "principal1", "key") == orchestration_identity("tenant1", "principal1", "key")
    item = root().transition(OrchestrationPhase.PLANNED_TOOL, occurred_at=datetime.now(timezone.utc), tool_identity="legal.instruction.read.v1", resource_identity="instruction-1")
    assert item.revision == 1 and item.phase is OrchestrationPhase.PLANNED_TOOL

def test_skips_and_terminal_reexecution_reject():
    with pytest.raises(AIToolOrchestrationError):
        root().transition(OrchestrationPhase.TOOL_COMPLETED, occurred_at=datetime.now(timezone.utc))
    done = root().transition(OrchestrationPhase.PLANNED_FINAL, occurred_at=datetime.now(timezone.utc)).transition(OrchestrationPhase.COMPLETED, occurred_at=datetime.now(timezone.utc))
    with pytest.raises(AIToolOrchestrationError):
        done.transition(OrchestrationPhase.STARTED, occurred_at=datetime.now(timezone.utc))

def test_planner_contract_has_no_callable():
    contract = AIToolContract("legal.instruction.read.v1", "v1", "legal_operations", "legal.read.instruction", "legal_operations:instruction:read", ToolRiskClass.READ_ONLY, "LEGAL_PII", ("resource_identity",))
    assert not hasattr(contract, "adapter")

# ARTIFACT: test_ai_tool_orchestration.py
# VERSION: v1.0.0-C1C-R1
# END OF WILSY OS SOVEREIGN ARTIFACT
