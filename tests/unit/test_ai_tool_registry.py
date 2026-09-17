"""C1C server-owned registry certificate."""
from tools.eos.intelligence.domain.ai_tool_orchestration import AIToolContract, ToolRiskClass
from tools.eos.intelligence.tools.registry import RegisteredAITool, ServerOwnedAIToolRegistry, AIToolRegistryError
import pytest

def registration(identity="legal.instruction.read.v1"):
    return RegisteredAITool(AIToolContract(identity, "v1", "legal_operations", "legal.read.instruction", "legal_operations:instruction:read", ToolRiskClass.READ_ONLY, "LEGAL_PII", ("resource_identity",)), lambda **_: {"state": "ALLOCATED"})

def test_registry_is_exact_and_immutable():
    registry = ServerOwnedAIToolRegistry((registration(),))
    assert registry.contains("legal.instruction.read.v1")
    with pytest.raises(AIToolRegistryError, match="UNKNOWN"):
        registry.get("unknown")
    with pytest.raises(AIToolRegistryError, match="DYNAMIC"):
        registry.register(registration("other"))

def test_duplicates_reject():
    with pytest.raises(AIToolRegistryError, match="DUPLICATE"):
        ServerOwnedAIToolRegistry((registration(), registration()))

# ARTIFACT: test_ai_tool_registry.py
# VERSION: v1.0.0-C1C-R1
# END OF WILSY OS SOVEREIGN ARTIFACT
