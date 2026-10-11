"""Direct mount certificate for the canonical WilsyAPIServer deadline router.

TITLE: Wilsy OS Legal Matter Deadline Server Mount Certificate
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D3B2A-DEADLINE-SERVER-MOUNT-CERT
AUTHORITY: Wilsy OS Core Governance / application-composition certification.
EPITOME: Prove server.py mounts the certified D3B1 deadline router exactly once
         under /api without altering router-owned IAM, transaction, or truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_matter_deadline_server_mount.py
COLLABORATION / OWNERSHIP: Certificate owns only route-composition observations.
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D3B2A-DEADLINE-SERVER-MOUNT-CERT
           establishes exact effective POST/list/detail route evidence for server.py.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No request execution, customer data, or secrets.
TENANT BOUNDARY: Mounting creates no tenant authority; D3B1 durable IAM remains mandatory.
AUTHORITY BOUNDARY: Application composition only; D1/D2/D3A/D3B1 remain canonical.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing, duplicate, widened, or malformed routes fail certification.
"""
from __future__ import annotations

import tools.eos.api.server as server_api
from tools.eos.api.legal_matter_deadline_router import router as deadline_router


VERSION = "v1.0.0-LEGAL-OPS-COMPLETION-D3B2A-DEADLINE-SERVER-MOUNT-CERT"


def _effective_routes() -> list[tuple[str, tuple[str, ...]]]:
    """Return only effective APIRoutes for the deadline route family."""
    result: list[tuple[str, tuple[str, ...]]] = []
    for route in server_api.app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if not isinstance(path, str):
            continue
        if not path.startswith("/api/legal-operations/matters/"):
            continue
        if "/deadlines" not in path:
            continue
        if not isinstance(methods, set):
            continue
        result.append((path, tuple(sorted(methods))))
    return sorted(result)


def test_server_mounts_deadline_router_exactly_once_under_api() -> None:
    assert deadline_router.prefix == "/legal-operations"
    assert _effective_routes() == sorted(
        [
            (
                "/api/legal-operations/matters/{case_matter_id}/deadlines",
                ("GET",),
            ),
            (
                "/api/legal-operations/matters/{case_matter_id}/deadlines",
                ("POST",),
            ),
            (
                "/api/legal-operations/matters/{case_matter_id}/deadlines/{deadline_id}",
                ("GET",),
            ),
        ]
    )


def test_server_source_has_one_import_and_one_mount_without_double_api() -> None:
    path = server_api.__file__
    assert path is not None
    source = open(path, encoding="utf-8").read()
    assert source.count(
        "from .legal_matter_deadline_router import router as legal_matter_deadline_router"
    ) == 1
    assert source.count(
        'app.include_router(legal_matter_deadline_router, prefix="/api")'
    ) == 1
    assert "/api/api/legal-operations" not in source
    assert "legal_operations:matter_deadline:read" not in source
    assert "legal_operations:matter_deadline:write" not in source
    assert "legal_matter_deadline_read" not in source
    assert "legal_matter_deadline_write" not in source


def test_server_version_surfaces_are_aligned() -> None:
    expected = "v1.21.0-D3B2A-MATTER-DEADLINE-ROUTER-MOUNT"
    assert server_api.VERSION == expected
    path = server_api.__file__
    assert path is not None
    source = open(path, encoding="utf-8").read()
    assert f"VERSION: {expected}" in source
    assert f"# VERSION: {expected}" in source
    assert "2026-10-11" in source


# ARTIFACT: test_legal_matter_deadline_server_mount.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D3B2A-DEADLINE-SERVER-MOUNT-CERT
# AUTHORITY BOUNDARY: server.py route-composition evidence only
# TENANT POSTURE: mount-only observation; D3B1 durable authorization remains authoritative
# FAIL-CLOSED POSTURE: absent, duplicate, widened, or double-/api registration fails
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
