"""C1C service certificate proving delegation to frozen C1B authority."""
from tools.eos.intelligence.wilsy_ai_reasoning_service import WilsyAIReasoningService
from tools.eos.intelligence.wilsy_ai_reasoning_orchestrator import WilsyAIReasoningOrchestrator
from typing import Any, cast
import pytest

def test_service_rejects_non_c1b_orchestrator():
    with pytest.raises(Exception):
        WilsyAIReasoningService(cast(Any, object()))

# ARTIFACT: test_wilsy_ai_reasoning_service.py
# VERSION: v1.0.0-C1C-R1
# END OF WILSY OS SOVEREIGN ARTIFACT
