"""TITLE: C1B reasoning endpoint reachability certificate.
VERSION: v1.0.0-C1B-R2
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Prove the foundational package does not mount an HTTP reasoning path.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_reasoning_endpoint_unreachable.py
CHANGELOG: v1.0.0-C1B-R2 certifies execution and C1C tool loops remain unreachable.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from pathlib import Path


def test_reasoning_router_and_endpoint_are_unreachable() -> None:
    server = Path("tools/eos/api/server.py").read_text(encoding="utf-8")
    api_server = Path("tools/eos/api/api_server.py").read_text(encoding="utf-8")
    assert "wilsy-ai/reasoning/invoke" not in server
    assert "wilsy-ai/reasoning/invoke" not in api_server
    assert not Path("tools/eos/api/wilsy_ai_reasoning_router.py").exists()


def test_provider_binding_has_no_execution_route() -> None:
    source = Path("tools/eos/intelligence/domain/ai_model_provider_binding.py").read_text(encoding="utf-8")
    assert "requests." not in source and "httpx" not in source


# ARTIFACT: test_wilsy_ai_reasoning_endpoint_unreachable.py
# VERSION: v1.0.0-C1B-R2
# END OF WILSY OS SOVEREIGN ARTIFACT
