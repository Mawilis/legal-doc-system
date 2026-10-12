"""Direct mount certificate for Legal Storefront public-intent admission.

TITLE: Wilsy OS Legal Storefront Public Intent Server Mount Certificate
VERSION: v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-SERVER-MOUNT-CERT
AUTHORITY: Wilsy OS Core Governance / application-composition certification.
EPITOME: Prove server.py mounts the directly and Real-Mongo-certified L8-9C
         public-intent router exactly once under /api and bootstraps the L8-9B
         durable-intent plus L8-9C0 ephemeral rate-limit indexes without
         copying Storefront, tenant, AI, Legal lifecycle or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_storefront_public_intent_server_mount.py
COLLABORATION / OWNERSHIP: Certificate owns only application-composition and
                            infrastructure-bootstrap observations.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-SERVER-MOUNT-CERT
           establishes the exact effective POST route, one canonical /api mount,
           current server-version alignment, and both required Storefront index
           bootstrap registrations.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Composition evidence only; no customer payload,
                             secret, raw rate subject, model request or credential.
TENANT BOUNDARY: Explicitly pre-tenant. Mounting creates no tenant authority.
AUTHORITY BOUNDARY: server.py composes already-certified L8-9A/L8-9B/L8-9C0/
                    L8-9C authorities and creates no independent business truth.
AI AUTHORITY BOUNDARY: No WILSY AI inference, entitlement, tool or gateway
                       authority is added by this composition certificate.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing, duplicate, widened, double-/api, unbootstrapped
                         or version-inconsistent composition fails certification.
"""

from __future__ import annotations

from fastapi.routing import APIRoute, _iter_routes_with_context

import tools.eos.api.server as server_api
from tools.eos.api.legal_storefront_public_intent_router import (
    router as legal_storefront_public_intent_router,
)


VERSION = (
    "v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-SERVER-MOUNT-CERT"
)

EXPECTED_SERVER_VERSION = (
    "v1.24.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-ROUTER-MOUNT"
)

EXPECTED_PATH = "/api/legal-storefront/public-intents"


def _effective_routes() -> list[tuple[str, tuple[str, ...]]]:
    """Flatten the canonical FastAPI graph and return Storefront intent routes."""
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

        if path != EXPECTED_PATH:
            continue

        result.append((path, tuple(sorted(methods))))

    return sorted(result)


def _server_source() -> str:
    """Return the canonical composition-root source for structural assertions."""
    path = server_api.__file__
    assert path is not None
    return open(path, encoding="utf-8").read()


def test_server_mounts_public_intent_router_exactly_once_under_api() -> None:
    """Certify one effective anonymous POST route at the canonical API path."""
    assert legal_storefront_public_intent_router.prefix == "/legal-storefront"

    assert _effective_routes() == [
        (
            EXPECTED_PATH,
            ("POST",),
        )
    ]


def test_server_source_has_exactly_one_import_and_one_api_mount() -> None:
    """Certify one router import/mount and reject accidental double-/api wiring."""
    source = _server_source()

    assert source.count(
        "from .legal_storefront_public_intent_router import ("
    ) == 1

    assert source.count(
        "router as legal_storefront_public_intent_router,"
    ) == 1

    assert source.count(
        "app.include_router(\n"
        "            legal_storefront_public_intent_router,\n"
        '            prefix="/api",\n'
        "        )"
    ) == 1

    assert "/api/api/legal-storefront" not in source


def test_server_bootstraps_both_storefront_index_contracts_once() -> None:
    """Certify infrastructure bootstrap for durable intent and rate evidence."""
    source = _server_source()

    assert source.count(
        "LegalStorefrontPublicIntentRegistry.ensure_indexes("
    ) == 1

    assert source.count(
        "database[LEGAL_STOREFRONT_PUBLIC_INTENT_COLLECTION]"
    ) == 1

    assert source.count(
        "LegalStorefrontPublicIntentRateLimit.ensure_indexes("
    ) == 1

    assert source.count(
        "LEGAL_STOREFRONT_PUBLIC_INTENT_RATE_LIMIT_COLLECTION"
    ) == 2

    assert source.count(
        "COLLECTION as LEGAL_STOREFRONT_PUBLIC_INTENT_COLLECTION"
    ) == 1

    assert source.count(
        "COLLECTION as LEGAL_STOREFRONT_PUBLIC_INTENT_RATE_LIMIT_COLLECTION"
    ) == 1


def test_server_version_surfaces_are_exactly_aligned() -> None:
    """Certify v1.24 runtime, sovereign header and end-seal alignment."""
    assert server_api.VERSION == EXPECTED_SERVER_VERSION

    source = _server_source()

    assert f"VERSION: {EXPECTED_SERVER_VERSION}" in source
    assert f'VERSION = "{EXPECTED_SERVER_VERSION}"' in source
    assert f"# VERSION: {EXPECTED_SERVER_VERSION}" in source

    assert source.count(EXPECTED_SERVER_VERSION) == 4


def test_server_composition_does_not_copy_storefront_authority() -> None:
    """Certify Storefront composition seams contain no copied business truth."""
    source = _server_source()

    import_start = source.index(
        "from .legal_storefront_public_intent_router import ("
    )
    import_end = source.index(
        "from .wilsy_ai_legal_gateway_router",
        import_start,
    )
    import_seam = source[import_start:import_end]

    bootstrap_start = source.index(
        "LegalStorefrontPublicIntentRegistry.ensure_indexes("
    )
    bootstrap_end = source.index(
        "if provider is not None and database is not None and client is not None:",
        bootstrap_start,
    )
    bootstrap_seam = source[bootstrap_start:bootstrap_end]

    mount_start = source.index(
        "app.include_router(\n"
        "            legal_storefront_public_intent_router,"
    )
    mount_end = source.index(
        "app.include_router(wilsy_ai_legal_gateway_router",
        mount_start,
    )
    mount_seam = source[mount_start:mount_end]

    storefront_composition = (
        import_seam
        + bootstrap_seam
        + mount_seam
    )

    for forbidden in (
        'contact_email":',
        'organization_name":',
        'industry":',
        'region":',
        "hashlib.sha3_512(",
        "WILSY-LSI-",
        "create_or_replay(intent",
        "subject_digest=",
        "L8_9C_RATE_LIMITED",
        "L8_9C_PERSISTENCE_UNAVAILABLE",
        "legal_storefront_public_intent_write",
        "tenant_id =",
        "principal_id =",
        "subscription_id =",
        "entitlement_id =",
        "payment_id =",
        "settlement_id =",
    ):
        assert forbidden not in storefront_composition


def test_storefront_mount_does_not_widen_method_or_route_surface() -> None:
    """Certify composition exposes exactly one POST Storefront intent route."""
    routes = _effective_routes()

    assert len(routes) == 1
    assert routes[0][0] == EXPECTED_PATH
    assert routes[0][1] == ("POST",)


# ARTIFACT: test_legal_storefront_public_intent_server_mount.py
# VERSION: v1.0.0-L8-9C-LEGAL-STOREFRONT-PUBLIC-INTENT-SERVER-MOUNT-CERT
# AUTHORITY BOUNDARY: canonical server composition and bootstrap evidence only
# TENANT POSTURE: explicitly pre-tenant; no tenant authority created by mount
# AI POSTURE: no WILSY AI invocation, inference, entitlement or authority
# FAIL-CLOSED POSTURE: absent, duplicate, widened or unbootstrapped composition fails
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
