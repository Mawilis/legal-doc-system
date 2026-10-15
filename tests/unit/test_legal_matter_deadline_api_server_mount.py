"""Direct mount certificate for the canonical api_server deadline router.

TITLE: Wilsy OS Legal Matter Deadline API Server Mount Certificate
VERSION: v1.0.2-LEGAL-OPS-COMPLETION-D3B2B-DEADLINE-API-SERVER-MOUNT-CERT
AUTHORITY: Wilsy OS Core Governance / application-composition certification.
EPITOME: Prove api_server.py mounts the certified D3B1 deadline router exactly
         once under /api without changing router-owned authority or truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_matter_deadline_api_server_mount.py
COLLABORATION / OWNERSHIP: Certificate owns only effective-route composition observations.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: 2026-10-15 v1.0.2-LEGAL-OPS-COMPLETION-D3B2B-DEADLINE-API-SERVER-MOUNT-CERT removes one accidental duplicate historical-lineage assertion without changing the certified api_server composition contract.
PREVIOUS CHANGELOG: 2026-10-15 v1.0.1-LEGAL-OPS-COMPLETION-D3B2B-DEADLINE-API-SERVER-MOUNT-CERT removes the obsolete requirement that the shared api_server composition root remain permanently frozen at its historical v1.9.0-D3B2B-MATTER-DEADLINE-ROUTER-MOUNT; current runtime/header/seal alignment and historical deadline lineage are certified independently.
2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D3B2B-DEADLINE-API-SERVER-MOUNT-CERT establishes exact POST/list/detail mount evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No request execution, customer data, credentials, or secrets.
TENANT BOUNDARY: Mounting grants no scope; D3B1 durable tenant authorization remains mandatory.
AUTHORITY BOUNDARY: Application composition only; D1/D2/D3A/D3B1 remain canonical.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing, duplicate, widened, or double-prefixed routes fail certification.
"""
from __future__ import annotations

from fastapi.routing import APIRoute, _iter_routes_with_context

import tools.eos.api.api_server as api_server
from tools.eos.api.legal_matter_deadline_router import router as deadline_router


VERSION = "v1.0.2-LEGAL-OPS-COMPLETION-D3B2B-DEADLINE-API-SERVER-MOUNT-CERT"
HISTORICAL_VERSION = "v1.9.0-D3B2B-MATTER-DEADLINE-ROUTER-MOUNT"


def _effective_routes() -> list[tuple[str, tuple[str, ...]]]:
    """Return effective deadline routes including included-router prefixes."""
    result: list[tuple[str, tuple[str, ...]]] = []
    for route, context in _iter_routes_with_context(api_server.app.routes):
        if not isinstance(route, APIRoute):
            continue
        path = context.path if context is not None else route.path
        methods = context.methods if context is not None else (route.methods or set())
        if not path.startswith("/api/legal-operations/matters/"):
            continue
        if "/deadlines" not in path:
            continue
        result.append((path, tuple(sorted(methods))))
    return sorted(result)


def test_api_server_mounts_deadline_router_exactly_once() -> None:
    assert deadline_router.prefix == "/legal-operations"
    assert _effective_routes() == sorted(
        [
            ("/api/legal-operations/matters/{case_matter_id}/deadlines", ("GET",)),
            ("/api/legal-operations/matters/{case_matter_id}/deadlines", ("POST",)),
            ("/api/legal-operations/matters/{case_matter_id}/deadlines/{deadline_id}", ("GET",)),
        ]
    )


def test_api_server_source_has_exact_import_mount_and_no_authority_copy() -> None:
    path = api_server.__file__
    assert path is not None
    source = open(path, encoding="utf-8").read()
    assert source.count(
        "from tools.eos.api.legal_matter_deadline_router import router as legal_matter_deadline_router"
    ) == 1
    assert source.count(
        'app.include_router(legal_matter_deadline_router, prefix="/api")'
    ) == 1
    assert "/api/api/legal-operations" not in source
    for forbidden in (
        "legal_operations:matter_deadline:read",
        "legal_operations:matter_deadline:write",
        "legal_matter_deadline_read",
        "legal_matter_deadline_write",
    ):
        assert forbidden not in source


def test_api_server_version_surfaces_are_aligned() -> None:
    """Certify current api_server alignment and preserved deadline lineage."""
    historical = HISTORICAL_VERSION
    current = api_server.VERSION

    assert isinstance(current, str)
    assert current
    assert current.strip() == current

    path = api_server.__file__
    assert path is not None

    source = open(
        path,
        encoding="utf-8",
    ).read()

    assert f"    {current}" in source
    assert f'VERSION = "{current}"' in source
    assert f"# VERSION: {current}" in source

    assert historical in source


# ARTIFACT: test_legal_matter_deadline_api_server_mount.py
# VERSION: v1.0.2-LEGAL-OPS-COMPLETION-D3B2B-DEADLINE-API-SERVER-MOUNT-CERT
# AUTHORITY BOUNDARY: api_server.py composition evidence only
# TENANT POSTURE: mount-only evidence; D3B1 durable authorization remains authoritative
# FAIL-CLOSED POSTURE: missing, duplicate, widened, or double-/api routes fail
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
