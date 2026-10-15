"""Tenant Legal Operating Model api_server.app mount certificate."""
from __future__ import annotations

from pathlib import Path

from fastapi.routing import APIRoute, _iter_routes_with_context

from tools.eos.api import api_server


PATH = "/api/legal/operating-model"


def _pairs() -> list[tuple[str, str]]:
    """Return effective TOM routes including included-router prefixes."""
    result: list[tuple[str, str]] = []

    for route, context in _iter_routes_with_context(
        api_server.app.routes
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


def test_api_server_app_mount_is_exact() -> None:
    assert _pairs() == [
        ("GET", PATH),
        ("POST", PATH),
    ]


def test_api_server_mount_source_occurs_once() -> None:
    source = Path(
        api_server.__file__
    ).read_text(
        encoding="utf-8"
    )

    assert source.count(
        "from tools.eos.api.tenant_legal_operating_model_router "
        "import router as tenant_legal_operating_model_router"
    ) == 1

    assert source.count(
        'app.include_router('
        'tenant_legal_operating_model_router, prefix="/api")'
    ) == 1


def test_api_server_version_and_financial_boundary() -> None:
    assert (
        api_server.VERSION
        == "v1.11.0-CX26-R3-LEGAL-OPERATING-MODEL-ROUTER-MOUNT"
    )

    source = Path(
        api_server.__file__
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "FINANCIAL AUTHORITY BOUNDARY"
        in source
    )
    assert "Kennel EOS" in source


# ARTIFACT: test_tenant_legal_operating_model_api_server_mount.py
# VERSION: v1.0.0-CX26-R3-API-SERVER-MOUNT-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
