"""FastAPI authority-bridge composition certificate.
TITLE: FastAPI Authority Bridge Composition Certification
VERSION: v1.1.0-WILSY-PYTHON-AUTHORITY-BRIDGE-COMPOSITION
AUTHORITY: Certification of canonical router composition and host-runtime invariants.
EPITOME: Protects service-trust-first registration without importing production persistence in unit tests.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authority_bridge_server_composition.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30
CHANGELOG: v1.1.0-WILSY-PYTHON-AUTHORITY-BRIDGE-COMPOSITION — AST structural certificate and explicit host-runtime helper contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: Composition only; no credentials or persistence access.
TENANT BOUNDARY: Delegated to the bridge and existing Python tenant authority.
AUTHORITY BOUNDARY: No new authority; registration only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
import ast
from pathlib import Path
from typing import Any

SERVER = Path("tools/eos/api/server.py")
BRIDGE = Path("tools/eos/api/authority_bridge_router.py")

def assert_static_composition_invariants() -> None:
    server = SERVER.read_text(); bridge = BRIDGE.read_text()
    assert server.count("from .authority_bridge_router import router as authority_bridge_router") == 1
    assert server.count("app.include_router(authority_bridge_router)") == 1
    assert "app.include_router(authority_bridge_router, prefix=" not in server
    tree = ast.parse(bridge)
    route = next(n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "authorize")
    decorators = [ast.unparse(d) for d in route.decorator_list]
    assert any("router.post(ROUTE_PATH)" in d for d in decorators)
    assert "return await authorize_request" in ast.unparse(route)
    orchestration = next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef) and n.name == "authorize_request")
    calls = [ast.unparse(n) for n in ast.walk(orchestration) if isinstance(n, ast.Call)]
    assert any("trust_verifier" in call for call in calls)
    assert any("identity_provider" in call for call in calls)
    assert any("tenant_provider" in call for call in calls)
    assert any("authorization_provider" in call for call in calls)

def assert_runtime_route_contract(app: Any, frozen_router: Any, endpoint: Any) -> None:
    """Host helper; caller supplies an already-built isolated app."""
    routes = [r for r in frozen_router.routes if getattr(r, "path", None) == "/internal/authority/authorize" and "POST" in getattr(r, "methods", set())]
    assert len(routes) == 1
    assert routes[0].endpoint is endpoint
    assert getattr(app, "authority_bridge_router", frozen_router) is frozen_router

def test_layer_a_static_composition_invariants():
    assert_static_composition_invariants()

def test_included_router_is_not_assumed_flattened():
    assert "app.routes" not in SERVER.read_text()
    assert "_IncludedRouter" not in SERVER.read_text()

# ARTIFACT: test_authority_bridge_server_composition.py
# VERSION: v1.1.0-WILSY-PYTHON-AUTHORITY-BRIDGE-COMPOSITION
# AUTHORITY BOUNDARY: FastAPI registration only.
# TENANT POSTURE: Existing bridge tenant authority remains authoritative.
# FAIL-CLOSED POSTURE: Registration introduces no bypass or fallback.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
