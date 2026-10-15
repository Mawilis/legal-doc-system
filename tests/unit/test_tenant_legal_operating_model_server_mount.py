"""Tenant Legal Operating Model WilsyAPIServer mount certificate."""
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
        == "v1.25.0-CX26-R3-LEGAL-OPERATING-MODEL-ROUTER-MOUNT"
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
# VERSION: v1.0.0-CX26-R3-WILSY-API-SERVER-MOUNT-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
