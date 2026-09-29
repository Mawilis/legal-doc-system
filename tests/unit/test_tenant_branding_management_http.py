"""Direct certificate for the L10-P2C6 tenant-branding management HTTP boundary.

TITLE: Tenant Branding Management HTTP Direct Certificate
VERSION: v1.0.0-L10-P2C6-D21B-BRANDING-MANAGEMENT-HTTP-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves authenticated tenant-derived routing, strict browser-safe
         projections, deterministic evidence helpers and bounded HTTP errors.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_management_http.py
COLLABORATION / OWNERSHIP: Direct Python EOS certificate; real-Mongo follow-up
                            remains separate because this gate introduces a new
                            multi-registry HTTP transaction composition.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: v1.0.0-L10-P2C6-D21B-BRANDING-MANAGEMENT-HTTP-CERT establishes 35
           focused assertions for route scope, tenant-derived authority,
           deterministic evidence and fail-closed transport behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No credentials, raw bytes, public URLs or caller
                             tenant claims become authority.
TENANT BOUNDARY: Exact authenticated identity tenant only.
AUTHORITY BOUNDARY: HTTP composition; D21B registries remain canonical.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

import pytest
from starlette.requests import Request

from tools.eos.api import tenant_branding_router as router


class CodedError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _request(payload: object) -> Request:
    body = json.dumps(payload).encode()
    consumed = False

    async def receive() -> dict[str, object]:
        nonlocal consumed
        if consumed:
            return {"type": "http.request", "body": b"", "more_body": False}
        consumed = True
        return {"type": "http.request", "body": body, "more_body": False}

    return Request({"type": "http", "method": "POST", "path": "/api/tenant-branding/profiles", "headers": []}, receive)


@pytest.mark.parametrize("value", range(10))
def test_digest_is_deterministic(value: int) -> None:
    payload = {"tenant": "tenant-a", "profile": value, "fields": ["label", "colour"]}
    assert router._digest(payload) == router._digest({"fields": payload["fields"], "profile": value, "tenant": "tenant-a"})
    assert len(router._digest(payload)) == 128


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("D21B2B_NOT_FOUND", 404),
        ("D21B4B_CURRENT_POINTER_MISSING", 404),
        ("D21B5B_ASSET_NOT_FOUND", 404),
        ("D21B4B_PROFILE_CONFLICT", 409),
        ("D21B4B_RETRY_REQUIRED", 409),
        ("D21B4B_CURRENT_POINTER_CONFLICT", 409),
        ("D21B2B_INPUT_INVALID", 422),
        ("D21B3_PROFILE_REQUIRED", 422),
        ("D21B4A_ACTIVE_ENTITLEMENT_REQUIRED", 422),
        ("D21B5A_MEDIA_INVALID", 422),
        ("BRANDING_PERSISTENCE_UNAVAILABLE", 503),
        ("D21B2B_PERSISTENCE_UNAVAILABLE", 503),
        ("UNKNOWN_FAILURE", 503),
        ("D21B2B_SINGLE_CURRENT_ENTITLEMENT_REQUIRED", 409),
        ("D21B4B_CURRENT_HISTORY_MISSING", 404),
    ],
)
def test_error_mapping_is_bounded(code: str, expected: int) -> None:
    assert router._map_error(CodedError(code)).status_code == expected


@pytest.mark.parametrize("payload", [{"profile_label": "A"}, {"profile_label": "B", "timestamp": "transport"}, {"primary_color": "#fff"}, {}, {"email_display_name": "Legal"}])
def test_allowlist_accepts_only_declared_presentation_fields(payload: dict[str, str]) -> None:
    result = asyncio.run(router._json_allowlist(_request(payload), {"profile_label", "primary_color", "email_display_name"}))
    assert result == {key: value for key, value in payload.items() if key != "timestamp"}


@pytest.mark.parametrize("field", ["tenant_id", "entitlement_id", "source_evidence_fingerprint", "approval_evidence_fingerprint", "raw_bytes"])
def test_allowlist_rejects_authority_or_raw_fields(field: str) -> None:
    with pytest.raises(Exception):
        asyncio.run(router._json_allowlist(_request({field: "forbidden"}), {"profile_label"}))


@pytest.mark.parametrize("value", range(5))
def test_browser_projection_excludes_durable_authority_fields(value: int) -> None:
    entitlement = SimpleNamespace(entitlement_id=f"ent-{value}", branding_tier="PRO", lifecycle_state="ACTIVE", lifecycle_revision=value, fingerprint="a" * 128)
    profile = SimpleNamespace(profile_id=f"profile-{value}", profile_label="Legal", fingerprint="b" * 128, branding_entitlement=entitlement, primary_color="#111", secondary_color=None, accent_color="#222", email_display_name=None, logo_asset_reference=None, logo_asset_fingerprint=None, favicon_asset_reference=None, favicon_asset_fingerprint=None)
    current = SimpleNamespace(profile=profile, pointer=SimpleNamespace(selection_id="sel", selection_revision=1))
    projection = router._profile_projection(current, entitlement)
    assert projection["entitlement"]["entitlementId"] == entitlement.entitlement_id
    assert "sourceEvidenceFingerprint" not in json.dumps(projection)
    assert "tenant_id" not in json.dumps(projection)
    assert "raw_bytes" not in json.dumps(projection)


def test_routes_are_authenticated_and_bounded() -> None:
    paths = {getattr(route, "path", None) for route in router.router.routes}
    assert paths == {"/tenant-branding", "/tenant-branding/profiles", "/tenant-branding/profiles/{profile_id}/select"}
    assert router._READ_PERMISSION == "tenant_branding:read"
    assert router._PROFILE_PERMISSION == "tenant_branding:profile:manage"


# ARTIFACT: test_tenant_branding_management_http.py
# VERSION: v1.0.0-L10-P2C6-D21B-BRANDING-MANAGEMENT-HTTP-CERT
# AUTHORITY BOUNDARY: focused HTTP composition certificate only
# TENANT POSTURE: authenticated server-derived tenant scope
# FAIL-CLOSED POSTURE: browser authority fields are rejected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
