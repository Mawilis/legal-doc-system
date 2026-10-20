"""Direct certificate for the authorization-role revocation server mount.

TITLE: Authorization Role Revocation Server Mount Certificate
VERSION: v1.0.1-P1-R3E-SERVER-MOUNT-PRESERVATION-HARNESS-REPAIR
AUTHORITY: Wilsy OS Core Governance / sovereign API composition certification.
EPITOME: Prove the certified revocation router is imported and mounted exactly
         once without importing unrelated privileged-security bootstraps.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authorization_role_revocation_server_mount.py
COLLABORATION / OWNERSHIP: Certifies only server composition of the already
                            certified authorization-role revocation router.
CERTIFICATION / UPDATE DATE: 2026-10-18
CHANGELOG: v1.0.0-P1-R3E establishes exact import, mount, route, preservation,
           version-alignment, and privileged-bootstrap exclusion evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Static/runtime composition observation only.
TENANT BOUNDARY: Mounting creates no tenant authority; the router retains
                 authenticated RequireTenantAuthorization ownership.
AUTHORITY BOUNDARY: Server composition evidence only; no IAM or mutation truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing, duplicate, widened, or mixed-authority mounts fail.
"""
from __future__ import annotations

import re

from pathlib import Path

from fastapi.routing import APIRoute, _iter_routes_with_context

import tools.eos.api.server as server_api


VERSION = "v1.0.1-P1-R3E-SERVER-MOUNT-PRESERVATION-HARNESS-REPAIR"
SERVER = Path("tools/eos/api/server.py")
ROUTE = "/api/tenants/role-assignments/revocations"


def _effective_routes() -> list[tuple[str, tuple[str, ...]]]:
    """Return the exact mounted revocation route and methods."""
    result: list[tuple[str, tuple[str, ...]]] = []
    for route, context in _iter_routes_with_context(server_api.app.routes):
        if not isinstance(route, APIRoute):
            continue
        path = context.path if context is not None else route.path
        if path != ROUTE:
            continue
        methods = context.methods if context is not None else (route.methods or set())
        result.append((path, tuple(sorted(methods))))
    return result


def test_revocation_router_is_imported_and_mounted_exactly_once() -> None:
    """Certify one import, one /api mount, and no double-prefix route."""
    source = SERVER.read_text(encoding="utf-8")
    import_line = (
        "from .authorization_role_revocation_router import router as "
        "authorization_role_revocation_router"
    )
    mount_line = (
        'app.include_router(authorization_role_revocation_router, prefix="/api")'
    )
    assert source.count(import_line) == 1
    assert source.count(mount_line) == 1
    assert "/api/api/tenants/role-assignments/revocations" not in source
    assert _effective_routes() == [(ROUTE, ("POST",))]


def test_mount_preserves_composition_and_excludes_privileged_bootstrap() -> None:
    """Prove current-main mounts remain and unrelated security DDL stays absent."""
    source = SERVER.read_text(encoding="utf-8")
    preserved = (
        "legal_operations_router",
        "legal_operations_command_router",
        "legal_operations_billing_read_router",
        "legal_matter_deadline_router",
        "legal_client_acceptance_router",
        "legal_evidence_upload_router",
        "tenant_legal_operating_model_router",
        "legal_storefront_public_intent_router",
        "tenant_branding_router",
        "authority_bridge_router",
    )
    mounted = {
        match.group(1)
        for match in re.finditer(
            r"app\.include_router\(\s*([A-Za-z_][A-Za-z0-9_]*)",
            source,
            flags=re.MULTILINE,
        )
    }
    assert set(preserved).issubset(mounted)
    forbidden = (
        "PrivilegedFactorVerificationCurrentnessRegistry",
        "InternalServiceReplayRegistry.ensure_indexes",
        "InternalServiceWorkloadCredentialRegistry",
        "PrivilegedWorkloadTrustCurrentnessRegistry",
        "PrivilegedNoninteractiveSecurityProofRegistry",
        "PrivilegedSecurityAssuranceEvidenceRegistry",
    )
    revocation_source = Path(
        "tools/eos/api/authorization_role_revocation_router.py"
    ).read_text(encoding="utf-8")
    assert all(item not in revocation_source for item in forbidden)
    # This is the router's own authorized revocation-evidence
    # dependency, not a privileged security-index bootstrap.
    assert revocation_source.count(
        "AuthorizationRoleRevocationEvidenceRegistry("
    ) == 1
    assert "AuthorizationRoleRevocationEvidenceRegistry.ensure_indexes(" not in revocation_source
    # These are independently governed server-startup protections,
    # not authority delegated to the revocation HTTP router.
    required_startup_indexes = (
        "PrivilegedFactorVerificationCurrentnessRegistry(",
        "InternalServiceReplayRegistry.ensure_indexes(",
        "InternalServiceWorkloadCredentialRegistry(",
        "PrivilegedWorkloadTrustCurrentnessRegistry(",
        "PrivilegedNoninteractiveSecurityProofRegistry(",
        "PrivilegedSecurityAssuranceEvidenceRegistry(",
        "AuthorizationRoleRevocationEvidenceRegistry(",
    )
    for index_owner in required_startup_indexes:
        assert source.count(index_owner) == 1
    assert source.index(
        "AuthorizationRoleRevocationEvidenceRegistry("
    ) < source.index("DeputyPrincipalBindingRegistry.ensure_indexes(")


def test_server_version_and_authority_surfaces_are_aligned() -> None:
    """Certify one current version across header, runtime, changelog, and seal."""
    source = SERVER.read_text(encoding="utf-8")
    current = server_api.VERSION
    assert current == "v1.33.0-P12C-R4N-PRACTITIONER-BINDING-LIFECYCLE"
    assert f"VERSION: {current}" in source
    assert f'VERSION = "{current}"' in source
    assert f"# VERSION: {current}" in source
    assert "FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively" in source
    assert source.count(
        'app.include_router(authorization_role_revocation_router, prefix="/api")'
    ) == 1


# ARTIFACT: test_authorization_role_revocation_server_mount.py
# VERSION: v1.0.1-P1-R3E-SERVER-MOUNT-PRESERVATION-HARNESS-REPAIR
# AUTHORITY BOUNDARY: server composition verification only; no IAM or mutation authority
# TENANT POSTURE: mounted router retains authenticated tenant admission ownership
# FAIL-CLOSED POSTURE: absent, duplicate, widened, or mixed-authority mounts fail
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
