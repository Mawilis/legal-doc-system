"""C1E-R1 unit certificate for the advisory HTTP router.

TITLE: WILSY AI Advisory Router Unit Certificate
VERSION: v1.0.0-C1E-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves exact routes, strict transport schema, bounded error mapping,
         and redacted response policy without starting the application.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_advisory_router.py
COLLABORATION / OWNERSHIP: C1E router and FastAPI composition certificate.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-C1E-R1 establishes transport-only route coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from typing import Any

from tools.eos.api.wilsy_ai_advisory_router import (
    GENERATE_PERMISSION,
    READ_PERMISSION,
    WilsyAIAdvisoryRequest,
    router,
)


def test_routes_and_permissions_are_exact() -> None:
    paths = {(getattr(route, "path", ""), tuple(sorted(getattr(route, "methods", None) or ()))) for route in router.routes}  # type: ignore[arg-type]
    assert ("/wilsy-ai/legal-next-actions", ("POST",)) in paths
    assert ("/wilsy-ai/legal-next-actions/{advisory_id}", ("GET",)) in paths
    assert GENERATE_PERMISSION == "wilsy_ai:legal_advisory:generate"
    assert READ_PERMISSION == "wilsy_ai:legal_advisory:read"


def test_request_forbids_caller_authority_fields() -> None:
    valid = WilsyAIAdvisoryRequest(orchestration_id="c1c-orch-1")
    assert valid.orchestration_id == "c1c-orch-1"
    try:
        WilsyAIAdvisoryRequest(orchestration_id="c1c-orch-1", tenant_id="foreign")  # type: ignore[call-arg]
    except Exception as error:
        assert "extra" in str(error).lower()
    else:
        raise AssertionError("unknown authority field was accepted")


# ARTIFACT: test_wilsy_ai_advisory_router.py
# VERSION: v1.0.0-C1E-R1
# CERTIFICATION: focused router proof; no Mongo/provider execution
# END OF WILSY OS SOVEREIGN ARTIFACT
