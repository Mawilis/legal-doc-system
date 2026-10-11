"""Direct mount certificate for the canonical Legal Client Acceptance router.

TITLE: Wilsy OS Legal Client Acceptance Server Mount Certificate
VERSION: v1.0.0-LEGAL-CLIENT-ACCEPTANCE-SERVER-MOUNT-CERT
AUTHORITY: Wilsy OS Core Governance / application-composition certification.
EPITOME: Prove server.py mounts the directly certified Legal Client Acceptance
         router exactly once under /api without copying IAM, acceptance,
         transaction, engagement, representation, Court, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_acceptance_server_mount.py
COLLABORATION / OWNERSHIP: Certificate owns only route-composition observations.
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0-LEGAL-CLIENT-ACCEPTANCE-SERVER-MOUNT-CERT
           establishes exact server.py effective-route and source-mount evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No request execution, customer data, secrets, or PII.
TENANT BOUNDARY: Mounting creates no tenant authority; router-owned durable IAM remains mandatory.
AUTHORITY BOUNDARY: Application composition only; canonical Legal Client Acceptance remains authoritative.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing, duplicate, widened, malformed, or double-/api routes fail certification.
"""

from __future__ import annotations

from fastapi.routing import APIRoute, _iter_routes_with_context

import tools.eos.api.server as server_api
from tools.eos.api.legal_client_acceptance_router import (
    router as legal_client_acceptance_router,
)


VERSION = "v1.0.0-LEGAL-CLIENT-ACCEPTANCE-SERVER-MOUNT-CERT"
EXPECTED_SERVER_VERSION = "v1.22.0-LEGAL-CLIENT-ACCEPTANCE-ROUTER-MOUNT"


def _effective_routes() -> list[tuple[str, tuple[str, ...]]]:
    """Flatten effective Legal Client Acceptance routes under server.py."""

    result: list[tuple[str, tuple[str, ...]]] = []

    for route, context in _iter_routes_with_context(server_api.app.routes):
        if not isinstance(route, APIRoute):
            continue

        path = context.path if context is not None else route.path
        methods = (
            context.methods
            if context is not None
            else (route.methods or set())
        )

        if not path.startswith("/api/legal-operations/client/"):
            continue
        if "acceptance-context" not in path:
            continue

        result.append((path, tuple(sorted(methods))))

    return sorted(result)


def test_server_mounts_client_acceptance_router_exactly_once_under_api() -> None:
    """Certify the exact three effective client-context routes."""

    assert legal_client_acceptance_router.prefix == "/legal-operations/client"

    assert _effective_routes() == sorted(
        [
            (
                "/api/legal-operations/client/"
                "acceptance-contexts/{acceptance_context_id}/content",
                ("GET",),
            ),
            (
                "/api/legal-operations/client/"
                "matters/{case_matter_id}/acceptance-contexts",
                ("POST",),
            ),
            (
                "/api/legal-operations/client/"
                "acceptance-contexts/{acceptance_context_id}/acceptances",
                ("POST",),
            ),
        ]
    )


def test_server_source_has_exact_import_mount_and_no_authority_copy() -> None:
    """Certify one import, one /api mount, and no copied Legal authority."""

    path = server_api.__file__
    assert path is not None

    source = open(path, encoding="utf-8").read()

    assert source.count(
        "from .legal_client_acceptance_router "
        "import router as legal_client_acceptance_router"
    ) == 1

    assert source.count(
        'app.include_router(legal_client_acceptance_router, prefix="/api")'
    ) == 1

    assert "/api/api/legal-operations/client" not in source

    for forbidden in (
        "legal_operations:client_acceptance:write",
        "legal_client_acceptance_write",
        "acceptance_context_id =",
        "acceptance_scope =",
        "actor_principal_id =",
        "accepted_at =",
        "confirmed =",
    ):
        assert forbidden not in source


def test_server_version_surfaces_are_aligned() -> None:
    """Certify the exact composition-root version and sovereign seals."""

    assert server_api.VERSION == EXPECTED_SERVER_VERSION

    path = server_api.__file__
    assert path is not None

    source = open(path, encoding="utf-8").read()

    assert f"VERSION: {EXPECTED_SERVER_VERSION}" in source
    assert f'# VERSION: {EXPECTED_SERVER_VERSION}' in source
    assert (
        "v1.22.0-LEGAL-CLIENT-ACCEPTANCE-ROUTER-MOUNT"
        in source
    )
    assert "2026-10-11" in source


def test_server_mount_does_not_widen_router_contract() -> None:
    """Certify composition adds no extra Legal Client Acceptance routes."""

    routes = _effective_routes()

    assert len(routes) == 3
    assert {methods for _, methods in routes} == {("GET",), ("POST",)}
    assert all(path.startswith("/api/legal-operations/client/") for path, _ in routes)


# ARTIFACT: test_legal_client_acceptance_server_mount.py
# VERSION: v1.0.0-LEGAL-CLIENT-ACCEPTANCE-SERVER-MOUNT-CERT
# AUTHORITY BOUNDARY: server.py route-composition evidence only
# TENANT POSTURE: mount-only evidence; router-owned authorization remains authoritative
# FAIL-CLOSED POSTURE: absent, duplicate, widened, malformed, or double-/api routes fail
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
