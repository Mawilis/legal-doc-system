"""WILSY OS Tenant Legal Operating Model Server Mount Certificate.
TITLE: Tenant Legal Operating Model Server Mount Certificate
VERSION: v1.0.1-CX26-R3-SERVER-V1.43-ALIGNMENT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Verifies the canonical tenant legal operating-model route mount and
         current server version without creating legal or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_legal_operating_model_server_mount.py
COLLABORATION / OWNERSHIP: Python EOS API composition and tenant legal operating-model owners.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: v1.0.1-CX26-R3-SERVER-V1.43-ALIGNMENT completes the sovereign header and end seal and pins the mount certificate to the current v1.43 server; route assertions are unchanged.
CHANGELOG: v1.0.0-CX26-R3-WILSY-API-SERVER-MOUNT-CERT established exact route and source-mount assertions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Static route composition inspection only; no tenant records are accessed.
TENANT BOUNDARY: The certificate grants no tenant access or operating-model authority.
AUTHORITY BOUNDARY: Route mount evidence only; Python EOS remains the sole authorization source.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution and settlement.
"""
from __future__ import annotations

from pathlib import Path

from fastapi.routing import APIRoute, _iter_routes_with_context

from tools.eos.api import server as server_api


PATH = "/api/legal/operating-model"


def _pairs() -> list[tuple[str, str]]:
    """Return effective TOM routes including included-router prefixes."""
    result: list[tuple[str, str]] = []

    for route, context in _iter_routes_with_context(
        server_api.app.routes
    ):
        if not isinstance(route, APIRoute):
            continue

        path = (
            context.path
            if context is not None
            else route.path
        )
        methods = (
            context.methods
            if context is not None
            else (route.methods or set())
        )

        if path != PATH:
            continue

        result.extend(
            (method, path)
            for method in methods
        )

    return sorted(result)


def test_canonical_wilsy_api_server_mount_is_exact() -> None:
    assert _pairs() == [
        ("GET", PATH),
        ("POST", PATH),
    ]


def test_canonical_mount_source_occurs_once() -> None:
    source = Path(
        server_api.__file__
    ).read_text(
        encoding="utf-8"
    )

    assert source.count(
        "from .tenant_legal_operating_model_router "
        "import router as tenant_legal_operating_model_router"
    ) == 1

    assert source.count(
        'app.include_router('
        'tenant_legal_operating_model_router, prefix="/api")'
    ) == 1


def test_canonical_server_version_and_financial_boundary() -> None:
    assert (
        server_api.VERSION
        == "v1.43.0-AUTHENTICATED-LEGACY-QR-ROUTER-MOUNT"
    )

    source = Path(
        server_api.__file__
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "FINANCIAL AUTHORITY BOUNDARY"
        in source
    )
    assert "Kennel EOS" in source


# ARTIFACT: test_tenant_legal_operating_model_server_mount.py
# VERSION: v1.0.1-CX26-R3-SERVER-V1.43-ALIGNMENT
# AUTHORITY BOUNDARY: Route mount evidence only; Python EOS owns authorization.
# TENANT POSTURE: No tenant access or operating-model authority is created.
# FAIL-CLOSED POSTURE: Missing, duplicate, or mismatched route/version fails.
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
