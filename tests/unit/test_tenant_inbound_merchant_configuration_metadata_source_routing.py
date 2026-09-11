"""Wilsy OS direct certificate for merchant credential-metadata-source routing.

TITLE: Tenant Inbound Merchant Configuration Metadata Source Routing Certificate
VERSION: v1.0.0-M11-R8-P3D-P5-R8-P4-CREDENTIAL-METADATA-SOURCE-ROUTING-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Host-free proof that explicit metadata-source routing is typed, fingerprinted, strictly hydrated, and never inferred.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_merchant_configuration_metadata_source_routing.py
CERTIFICATION / UPDATE DATE: 2026-09-11
AUTHORITY BOUNDARY: Routing provenance only; no source resolution, credential retrieval, checkout, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement truth.
FAIL-CLOSED DECLARATION: Missing serialized routing, malformed routes, forged fingerprints, and absent required routing reject.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone

import pytest

from tools.eos.saas.domain.tenant_inbound_merchant_configuration import (
    InboundMerchantProviderId,
    TenantInboundCredentialMetadataSourceRouting,
    TenantInboundMerchantConfiguration,
    TenantInboundMerchantConfigurationError,
)

STAMP = datetime(2026, 9, 11, tzinfo=timezone.utc)


def route(source: str = "source-a", contract: str = "v1") -> TenantInboundCredentialMetadataSourceRouting:
    return TenantInboundCredentialMetadataSourceRouting(source, contract)


def config(**changes: object) -> TenantInboundMerchantConfiguration:
    values: dict[str, object] = {
        "merchant_configuration_id": "config-1",
        "tenant_id": "tenant-a",
        "provider_id": InboundMerchantProviderId.PAYFAST,
        "merchant_account_id": "merchant-account-1",
        "merchant_configuration_version": 1,
        "non_secret_provider_options": {"mode": "sandbox", "currency": "ZAR"},
        "credential_secret_reference": "vault://tenant-a/payfast/primary",
        "created_at": STAMP,
        "credential_metadata_source_routing": route(),
    }
    values.update(changes)
    return TenantInboundMerchantConfiguration(**values)  # type: ignore[arg-type]


def test_route_is_typed_exact_and_immutable() -> None:
    value = route()
    assert value.to_dict() == {"source_identity": "source-a", "source_contract_version": "v1"}
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        value.source_identity = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"source_identity": ""},
        {"source_identity": " source-a"},
        {"source_contract_version": ""},
        {"source_contract_version": "v1 "},
    ],
)
def test_route_rejects_malformed_tokens(kwargs: dict[str, str]) -> None:
    values = {"source_identity": "source-a", "source_contract_version": "v1"}
    values.update(kwargs)
    with pytest.raises(TenantInboundMerchantConfigurationError):
        TenantInboundCredentialMetadataSourceRouting(**values)


def test_route_participates_in_configuration_fingerprint() -> None:
    first = config(credential_metadata_source_routing=route("source-a", "v1"))
    second = config(credential_metadata_source_routing=route("source-b", "v1"))
    third = config(credential_metadata_source_routing=route("source-a", "v2"))
    assert first.fingerprint != second.fingerprint != third.fingerprint


def test_secret_reference_and_route_are_separate() -> None:
    value = config()
    routing = value.require_credential_metadata_source_routing()
    assert "credential_secret_reference" not in routing.to_dict()
    assert "vault://" not in str(routing.to_dict())


def test_no_route_is_explicit_but_non_authorizing() -> None:
    value = config(credential_metadata_source_routing=None)
    assert value.to_dict()["credential_metadata_source_routing"] is None
    with pytest.raises(TenantInboundMerchantConfigurationError, match="M11R8_CREDENTIAL_METADATA_SOURCE_ROUTING_REQUIRED"):
        value.require_credential_metadata_source_routing()


def test_untyped_route_is_rejected_without_coercion() -> None:
    with pytest.raises(TenantInboundMerchantConfigurationError, match="M11R8_INVALID_CREDENTIAL_METADATA_SOURCE_ROUTING"):
        config(credential_metadata_source_routing={"source_identity": "source-a", "source_contract_version": "v1"})


def test_round_trip_preserves_route_and_fingerprint() -> None:
    value = config()
    hydrated = TenantInboundMerchantConfiguration.from_dict(value.to_dict())
    assert hydrated == value
    assert hydrated.fingerprint == value.fingerprint


def test_missing_legacy_route_field_never_backfills() -> None:
    payload = config().to_dict()
    payload.pop("credential_metadata_source_routing")
    with pytest.raises(TenantInboundMerchantConfigurationError, match="M11R8_INVALID_CONFIGURATION_SCHEMA"):
        TenantInboundMerchantConfiguration.from_dict(payload)


def test_forged_route_without_recomputed_fingerprint_rejects() -> None:
    payload = config().to_dict()
    payload["credential_metadata_source_routing"] = {"source_identity": "source-b", "source_contract_version": "v1"}
    with pytest.raises(TenantInboundMerchantConfigurationError, match="M11R8_CONFIGURATION_FINGERPRINT_MISMATCH"):
        TenantInboundMerchantConfiguration.from_dict(payload)


# ARTIFACT: test_tenant_inbound_merchant_configuration_metadata_source_routing.py
# VERSION: v1.0.0-M11-R8-P3D-P5-R8-P4-CREDENTIAL-METADATA-SOURCE-ROUTING-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
