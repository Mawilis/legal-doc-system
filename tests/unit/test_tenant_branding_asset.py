"""Direct certificate for D21B5A tenant branding asset evidence.

TITLE: Tenant Branding Asset Direct Certificate
VERSION: v1.0.0-D21B5A-TENANT-BRANDING-ASSET-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove tenant-bound asset references, safe media policy, bounded content,
         SHA3-512 byte identity, immutable metadata and authority firewalls.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_branding_asset.py
COLLABORATION / OWNERSHIP: Evidence-only certificate for D21B5A; persistence and
                            runtime resolution remain separate later gates.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B5A-TENANT-BRANDING-ASSET-CERT establishes direct evidence
           for LOGO/FAVICON kinds, tenant namespace binding, raster/icon MIME
           allowlisting, SVG rejection, 2 MiB maximum, deterministic content and
           metadata fingerprints, strict hydration and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic bytes/identities only; no URLs, files,
                             provider credentials or browser state.
TENANT BOUNDARY: Every asset reference is exact-tenant namespaced.
AUTHORITY BOUNDARY: Asset evidence only; no profile approval/presentation/IAM.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
import hashlib
import re

import pytest

from tools.eos.saas.domain.tenant_branding_asset import (
    MAX_ASSET_BYTES,
    SAFE_MEDIA_TYPES,
    TenantBrandingAsset,
    TenantBrandingAssetError,
    TenantBrandingAssetKind,
    content_fingerprint,
    register_tenant_branding_asset,
)


NOW = datetime(2026, 9, 25, 17, 0, tzinfo=timezone.utc)
FP = "a" * 128
PNG = b"\x89PNG\r\n\x1a\n" + b"brand-image-payload"


def asset(**changes: object) -> TenantBrandingAsset:
    """Return one valid immutable synthetic logo asset."""
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "asset_reference": "asset:tenant-a:logo:primary",
        "asset_kind": TenantBrandingAssetKind.LOGO,
        "media_type": "image/png",
        "content_length": len(PNG),
        "content_fingerprint": hashlib.sha3_512(PNG).hexdigest(),
        "source_evidence_reference": "brand-upload-1",
        "source_evidence_fingerprint": FP,
        "registered_at": NOW,
    }
    values.update(changes)
    return TenantBrandingAsset(**values)  # type: ignore[arg-type]


def test_factory_binds_exact_content_sha3_and_length() -> None:
    """Factory hashes supplied bytes and never stores raw content in metadata."""
    value = register_tenant_branding_asset(
        tenant_id="tenant-a",
        asset_reference="asset:tenant-a:logo:primary",
        asset_kind=TenantBrandingAssetKind.LOGO,
        media_type="image/png",
        content=PNG,
        source_evidence_reference="brand-upload-1",
        source_evidence_fingerprint=FP,
        registered_at=NOW,
    )
    assert value.content_fingerprint == hashlib.sha3_512(PNG).hexdigest()
    assert value.content_length == len(PNG)
    assert "content" not in value.to_dict()


@pytest.mark.parametrize("kind", list(TenantBrandingAssetKind))
def test_closed_asset_kinds_are_supported(kind: TenantBrandingAssetKind) -> None:
    """Both canonical runtime purposes have exact evidence values."""
    value = asset(asset_kind=kind)
    assert value.asset_kind is kind


@pytest.mark.parametrize("media_type", sorted(SAFE_MEDIA_TYPES))
def test_safe_raster_and_icon_media_types_are_supported(media_type: str) -> None:
    """Only the explicit non-SVG image allowlist is admitted."""
    assert asset(media_type=media_type).media_type == media_type


@pytest.mark.parametrize(
    "media_type",
    ["image/svg+xml", "text/html", "text/css", "application/javascript", "image/gif"],
)
def test_svg_executable_and_unapproved_media_types_fail_closed(media_type: str) -> None:
    """Executable/active or unapproved image formats never become brand assets."""
    with pytest.raises(
        TenantBrandingAssetError,
        match="D21B5A_MEDIA_TYPE_UNSUPPORTED",
    ):
        asset(media_type=media_type)


@pytest.mark.parametrize(
    "tenant_id,asset_reference",
    [
        ("tenant-a", "asset:tenant-b:logo:primary"),
        ("tenant-a", "https://example.com/logo.png"),
        ("tenant-a", "/tmp/logo.png"),
        ("default", "asset:default:logo:primary"),
        ("*", "asset:*:logo:primary"),
    ],
)
def test_reference_must_be_exact_tenant_asset_namespace(
    tenant_id: str,
    asset_reference: str,
) -> None:
    """Foreign/raw-location/pseudo-tenant references reject."""
    with pytest.raises(TenantBrandingAssetError):
        asset(tenant_id=tenant_id, asset_reference=asset_reference)


def test_empty_nonbytes_and_oversize_content_fail_closed() -> None:
    """Content identity cannot be derived from absent or unbounded bytes."""
    with pytest.raises(
        TenantBrandingAssetError,
        match="D21B5A_CONTENT_LENGTH_INVALID",
    ):
        content_fingerprint(b"")
    with pytest.raises(
        TenantBrandingAssetError,
        match="D21B5A_CONTENT_BYTES_REQUIRED",
    ):
        content_fingerprint("not-bytes")  # type: ignore[arg-type]
    with pytest.raises(
        TenantBrandingAssetError,
        match="D21B5A_CONTENT_LENGTH_INVALID",
    ):
        content_fingerprint(b"x" * (MAX_ASSET_BYTES + 1))


def test_declared_content_length_and_fingerprint_are_strict() -> None:
    """Metadata cannot lie about byte length or fingerprint shape."""
    with pytest.raises(
        TenantBrandingAssetError,
        match="D21B5A_CONTENT_LENGTH_INVALID",
    ):
        asset(content_length=0)
    with pytest.raises(
        TenantBrandingAssetError,
        match="D21B5A_CONTENT_LENGTH_INVALID",
    ):
        asset(content_length=MAX_ASSET_BYTES + 1)
    with pytest.raises(TenantBrandingAssetError):
        asset(content_fingerprint="not-a-digest")


def test_source_evidence_and_registered_time_are_mandatory() -> None:
    """Registration evidence must be opaque, complete and timezone-aware."""
    with pytest.raises(TenantBrandingAssetError):
        asset(source_evidence_reference="")
    with pytest.raises(TenantBrandingAssetError):
        asset(source_evidence_fingerprint="bad")
    with pytest.raises(TenantBrandingAssetError):
        asset(registered_at=NOW.replace(tzinfo=None))


def test_metadata_fingerprint_is_deterministic_and_mutation_sensitive() -> None:
    """Exact semantic metadata has one lowercase SHA3-512 integrity seal."""
    first = asset()
    second = asset()
    assert first.fingerprint == second.fingerprint
    assert re.fullmatch(r"[0-9a-f]{128}", first.fingerprint)
    assert (
        replace(
            first,
            asset_reference="asset:tenant-a:logo:secondary",
            fingerprint="",
        ).fingerprint
        != first.fingerprint
    )


def test_strict_round_trip_unknown_missing_and_corrupt_payloads_fail_closed() -> None:
    """Hydration accepts exact schema and stored integrity only."""
    value = asset()
    payload = value.to_dict()
    assert TenantBrandingAsset.from_dict(payload) == value

    with pytest.raises(TenantBrandingAssetError, match="D21B5A_SCHEMA_INVALID"):
        TenantBrandingAsset.from_dict({**payload, "extra": "x"})

    missing = dict(payload)
    missing.pop("media_type")
    with pytest.raises(TenantBrandingAssetError, match="D21B5A_SCHEMA_INVALID"):
        TenantBrandingAsset.from_dict(missing)

    corrupt = dict(payload)
    corrupt["fingerprint"] = "f" * 128
    with pytest.raises(
        TenantBrandingAssetError,
        match="D21B5A_FINGERPRINT_MISMATCH",
    ):
        TenantBrandingAsset.from_dict(corrupt)


def test_immutability_and_authority_firewalls() -> None:
    """Asset evidence cannot mutate or acquire unrelated authorities."""
    value = asset()
    with pytest.raises((FrozenInstanceError, AttributeError)):
        value.tenant_id = "tenant-b"  # type: ignore[misc]

    forbidden = {
        "content",
        "bytes",
        "url",
        "path",
        "bucket",
        "storage_key",
        "profile_id",
        "current",
        "principal_id",
        "role",
        "permission",
        "price",
        "amount",
        "invoice",
        "payment",
        "execution",
        "settlement",
    }
    assert forbidden.isdisjoint(value.to_dict())


def test_factory_fingerprint_changes_with_exact_bytes() -> None:
    """Different bytes cannot share D21B5A content identity."""
    first = content_fingerprint(PNG)
    second = content_fingerprint(PNG + b"x")
    assert first != second


# ARTIFACT: test_tenant_branding_asset.py
# VERSION: v1.0.0-D21B5A-TENANT-BRANDING-ASSET-CERT
# AUTHORITY BOUNDARY: direct asset-evidence validation only; no persistence/profile/browser/IAM/financial authority
# TENANT POSTURE: synthetic tenant-bound asset namespaces only
# FAIL-CLOSED POSTURE: unsafe reference/media/content/evidence/schema corruption rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
