"""C1B-R19A reasoning HTTP composition coherence certificate.

TITLE: WILSY AI Authenticated Reasoning HTTP Composition Certificate
VERSION: v1.1.0-C1B-R19A
AUTHORITY: Wilsy OS Core Governance
EPITOME: Retire the obsolete unreachable-endpoint assertion while proving the
         single authenticated reasoning route and server-owned provider seam.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_reasoning_endpoint_unreachable.py
COLLABORATION / OWNERSHIP: Certifies tools/eos/api/wilsy_ai_reasoning_router.py
                            and its composition in tools/eos/api/server.py.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.1.0-C1B-R19A replaces the pre-R19 unreachable certificate with
           a narrow route-composition and alternate-surface certificate;
           v1.0.0-C1B-R2 certified the pre-R19 unreachable posture.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: The certificate checks composition only and never
                             executes a provider or exposes request data.
TENANT BOUNDARY: Runtime tenant scope remains owned by the authenticated
                 reasoning router dependency.
AUTHORITY BOUNDARY: HTTP composition certificate only; no reasoning, legal,
                    service, invoice, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Missing canonical composition or an alternate route
                         fails certification.
"""
from pathlib import Path


ROUTER_PATH = Path("tools/eos/api/wilsy_ai_reasoning_router.py")
SERVER_PATH = Path("tools/eos/api/server.py")
PROVIDER_BINDING_PATH = Path("tools/eos/intelligence/domain/ai_model_provider_binding.py")


def test_authenticated_reasoning_composition_replaces_stale_unreachable_assertion() -> None:
    """Prove the one authorized reasoning POST surface is composed exactly once."""
    router = ROUTER_PATH.read_text(encoding="utf-8")
    server = SERVER_PATH.read_text(encoding="utf-8")

    assert ROUTER_PATH.is_file()
    assert server.count("from .wilsy_ai_reasoning_router import router as wilsy_ai_reasoning_router") == 1
    assert server.count('app.include_router(wilsy_ai_reasoning_router, prefix="/api")') == 1
    assert router.count('router = APIRouter(prefix="/wilsy-ai"') == 1
    assert router.count('@router.post("/reasoning")') == 1
    assert "/wilsy-ai/reasoning/invoke" not in router
    assert "/wilsy-ai/reasoning/invoke" not in server


def test_server_owned_provider_binding_has_no_direct_execution_transport() -> None:
    """Preserve provider-neutral ownership by rejecting direct HTTP transports."""
    source = PROVIDER_BINDING_PATH.read_text(encoding="utf-8")
    assert "requests." not in source
    assert "httpx" not in source


# ARTIFACT: test_wilsy_ai_reasoning_endpoint_unreachable.py
# VERSION: v1.1.0-C1B-R19A
# AUTHORITY BOUNDARY: authenticated reasoning HTTP composition certificate only
# TENANT POSTURE: runtime authorization remains router-owned and tenant-scoped
# FAIL-CLOSED POSTURE: missing canonical route or alternate route fails
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
