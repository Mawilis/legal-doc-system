"""WILSY OS direct certificate for credential-material metadata.

TITLE: Tenant Inbound Provider Credential Material Metadata Tests
VERSION: v1.1.0-M11-R8-R3B-P8-P3D-P5-R4D-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove the immutable provider-neutral metadata value and its typed
         observation boundary without claiming external or durable authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_provider_credential_material_metadata.py
COLLABORATION / OWNERSHIP: Direct P5-R3 domain certificate; registry, adapter,
                            security-evidence, and issuance owners remain deferred.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.1.0-M11-R8-R3B-P8-P3D-P5-R4D-CERT covers the preserved P5-R3
           cases plus generation-identity and re-observation semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque references only; no secret,
                             network, database, KMS, provider, or financial activity.
TENANT BOUNDARY: Fixtures carry explicit tenant and merchant-configuration correlation.
AUTHORITY BOUNDARY: Direct tests prove value shape and integrity only.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, checkout, or Kennel execution.
FAIL-CLOSED DECLARATION: Schema drift, invalid identity, timestamp, provenance,
                          secret-shaped fields, and digest mismatch reject.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timezone
import ast
import hashlib
import json
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.saas.domain.tenant_inbound_provider_credential_material_metadata import (
    CAMPAIGN_IDENTITY,
    HASH_ALGORITHM,
    MAX_CREDENTIAL_VERSION_LENGTH,
    METADATA_FINGERPRINT_SCHEMA,
    METADATA_FINGERPRINT_VERSION,
    TenantInboundProviderCredentialMaterialMetadata,
    TenantInboundProviderCredentialMaterialMetadataError,
    TenantInboundProviderCredentialMaterialObservation,
    VERSION,
)


AT = datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc)
CONFIGURATION_FINGERPRINT = "a" * 128


def _observation(**changes: object) -> TenantInboundProviderCredentialMaterialObservation:
    """Build one valid synthetic observation with no secret material."""
    values: dict[str, object] = {
        "credential_reference": "secret-ref://tenant-a/config-a/v1",
        "credential_version": "generation-1",
        "metadata_source_identity": "metadata-adapter-a",
        "metadata_source_version": "adapter-contract-v1",
        "version_provenance_reference": "source-observation-a",
        "observed_at": AT,
    }
    values.update(changes)
    return TenantInboundProviderCredentialMaterialObservation(
        **cast(dict[str, Any], values)
    )


def _metadata(**changes: object) -> TenantInboundProviderCredentialMaterialMetadata:
    """Build one valid synthetic metadata value with explicit tenant scope."""
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "provider_id": "provider-a",
        "merchant_configuration_id": "config-a",
        "merchant_configuration_version": 1,
        "merchant_configuration_fingerprint": CONFIGURATION_FINGERPRINT,
        "credential_reference": "secret-ref://tenant-a/config-a/v1",
        "credential_version": "generation-1",
        "observed_at": AT,
        "metadata_source_identity": "metadata-adapter-a",
        "metadata_source_version": "adapter-contract-v1",
        "version_provenance_reference": "source-observation-a",
    }
    values.update(changes)
    return TenantInboundProviderCredentialMaterialMetadata(
        **cast(dict[str, Any], values)
    )


def test_valid_minimal_metadata_value_is_structurally_valid() -> None:
    value = _metadata()
    assert value.tenant_id == "tenant-a"
    assert value.credential_version == "generation-1"
    assert value.metadata_fingerprint is not None


def test_metadata_has_exact_thirteen_field_contract() -> None:
    assert [item.name for item in fields(TenantInboundProviderCredentialMaterialMetadata)] == [
        "tenant_id",
        "provider_id",
        "merchant_configuration_id",
        "merchant_configuration_version",
        "merchant_configuration_fingerprint",
        "credential_reference",
        "credential_version",
        "observed_at",
        "metadata_source_identity",
        "metadata_source_version",
        "version_provenance_reference",
        "metadata_fingerprint_version",
        "metadata_fingerprint",
    ]
    assert len(fields(TenantInboundProviderCredentialMaterialMetadata)) == 13
    assert set(_metadata().to_dict()) == {
        item.name for item in fields(TenantInboundProviderCredentialMaterialMetadata)
    }


def test_observation_has_exact_six_field_contract() -> None:
    assert [item.name for item in fields(TenantInboundProviderCredentialMaterialObservation)] == [
        "credential_reference",
        "credential_version",
        "metadata_source_identity",
        "metadata_source_version",
        "version_provenance_reference",
        "observed_at",
    ]
    assert len(fields(TenantInboundProviderCredentialMaterialObservation)) == 6
    assert set(_observation().to_dict()) == {
        item.name for item in fields(TenantInboundProviderCredentialMaterialObservation)
    }


def test_opaque_credential_version_is_structurally_accepted() -> None:
    assert _metadata(credential_version="opaque-provider-generation-α").credential_version == "opaque-provider-generation-α"


@pytest.mark.parametrize("version", ["", "   ", " generation-1 "])
def test_blank_or_surrounding_whitespace_version_is_rejected(version: str) -> None:
    with pytest.raises(TenantInboundProviderCredentialMaterialMetadataError, match="CREDENTIAL_VERSION"):
        _metadata(credential_version=version)


def test_overlong_credential_version_is_rejected() -> None:
    with pytest.raises(TenantInboundProviderCredentialMaterialMetadataError, match="CREDENTIAL_VERSION"):
        _metadata(credential_version="v" * (MAX_CREDENTIAL_VERSION_LENGTH + 1))


def test_credential_version_is_not_configuration_version_or_security_revision() -> None:
    value = _metadata(merchant_configuration_version=2, credential_version="2")
    assert value.credential_version == "2"
    assert "security_revision" not in value.to_dict()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("credential_reference", ""),
        ("merchant_configuration_fingerprint", "not-a-fingerprint"),
        ("metadata_source_identity", ""),
        ("metadata_source_version", ""),
        ("version_provenance_reference", ""),
    ],
)
def test_required_reference_configuration_and_provenance_fields_reject_blank_or_bad_values(field: str, value: object) -> None:
    with pytest.raises(TenantInboundProviderCredentialMaterialMetadataError):
        _metadata(**{field: value})


def test_aware_utc_observation_is_accepted() -> None:
    assert _metadata(observed_at=AT).observed_at == AT


def test_naive_observation_is_rejected() -> None:
    with pytest.raises(TenantInboundProviderCredentialMaterialMetadataError, match="OBSERVED_AT"):
        _metadata(observed_at=datetime(2026, 9, 10, 10, 0))


def test_non_utc_observation_is_rejected() -> None:
    from datetime import timedelta, timezone as tz

    with pytest.raises(TenantInboundProviderCredentialMaterialMetadataError, match="NON_UTC"):
        _metadata(observed_at=AT.replace(tzinfo=tz(timedelta(hours=2))))


def test_metadata_fingerprint_is_deterministic_and_round_trips() -> None:
    first = _metadata()
    second = _metadata()
    assert first.metadata_fingerprint == second.metadata_fingerprint
    assert first.to_dict() == second.to_dict()
    assert TenantInboundProviderCredentialMaterialMetadata.from_dict(first.to_dict()) == first
    assert first.to_persisted() == first.to_dict()
    assert first.verify_fingerprint()


def test_observed_at_is_descriptive_and_excluded_from_generation_fingerprint() -> None:
    later = _metadata(observed_at=AT.replace(minute=1))
    assert later.observed_at != _metadata().observed_at
    assert later.fingerprint == _metadata().fingerprint
    assert later.same_generation(_metadata())
    assert later != _metadata()


def test_observed_at_does_not_create_a_new_generation_identity() -> None:
    first = _metadata(observed_at=AT)
    later = _metadata(observed_at=AT.replace(second=1))
    assert first.generation_identity() == later.generation_identity()
    assert first.same_generation(later)
    assert first.fingerprint == later.fingerprint


def test_different_generation_identity_fields_change_fingerprint_and_identity() -> None:
    value = _metadata()
    changes: dict[str, object] = {
        "tenant_id": "tenant-b",
        "provider_id": "provider-b",
        "merchant_configuration_id": "config-b",
        "merchant_configuration_version": 2,
        "merchant_configuration_fingerprint": "b" * 128,
        "credential_reference": "secret-ref://tenant-a/config-a/v2",
        "credential_version": "generation-2",
        "metadata_source_identity": "metadata-adapter-b",
        "metadata_source_version": "adapter-contract-v2",
        "version_provenance_reference": "source-observation-b",
    }
    for field_name, changed in changes.items():
        altered = replace(value, metadata_fingerprint=None, **{field_name: changed})
        assert altered.fingerprint != value.fingerprint, field_name
        assert not altered.same_generation(value), field_name


def test_old_timestamp_bound_fingerprint_is_rejected() -> None:
    value = _metadata()
    legacy_payload = {
        "tenant_id": value.tenant_id,
        "provider_id": value.provider_id,
        "merchant_configuration_id": value.merchant_configuration_id,
        "merchant_configuration_version": value.merchant_configuration_version,
        "merchant_configuration_fingerprint": value.merchant_configuration_fingerprint,
        "credential_reference": value.credential_reference,
        "credential_version": value.credential_version,
        "observed_at": value.observed_at.isoformat(),
        "metadata_source_identity": value.metadata_source_identity,
        "metadata_source_version": value.metadata_source_version,
        "version_provenance_reference": value.version_provenance_reference,
        "metadata_fingerprint_version": value.metadata_fingerprint_version,
    }
    old_fingerprint = hashlib.sha3_512(
        json.dumps(legacy_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert old_fingerprint != value.fingerprint
    with pytest.raises(TenantInboundProviderCredentialMaterialMetadataError, match="FINGERPRINT"):
        _metadata(metadata_fingerprint=old_fingerprint)


def test_metadata_fingerprint_schema_and_version_are_exact() -> None:
    value = _metadata()
    assert VERSION == "v1.1.0-M11-R8-R3B-P8-P3D-P5-R4D"
    assert CAMPAIGN_IDENTITY == "M11-R8-R3B-P8-P3D-P5-R4D"
    assert value.metadata_fingerprint_version == METADATA_FINGERPRINT_VERSION == "v1"
    assert METADATA_FINGERPRINT_SCHEMA == "WILSY-TENANT-INBOUND-PROVIDER-CREDENTIAL-MATERIAL-METADATA/V1"
    assert HASH_ALGORITHM == "SHA3-512"
    assert value.metadata_fingerprint is not None and len(value.metadata_fingerprint) == 128


def test_supplied_matching_fingerprint_is_validation_only() -> None:
    value = _metadata()
    rebuilt = _metadata(metadata_fingerprint=value.fingerprint)
    assert rebuilt == value
    assert rebuilt.verify_fingerprint(value.fingerprint)


def test_supplied_divergent_fingerprint_is_rejected() -> None:
    with pytest.raises(TenantInboundProviderCredentialMaterialMetadataError, match="FINGERPRINT"):
        _metadata(metadata_fingerprint="0" * 128)


def test_metadata_and_observation_are_immutable() -> None:
    value = _metadata()
    observation = _observation()
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        value.tenant_id = "tenant-b"  # type: ignore[misc]
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        observation.credential_version = "generation-2"  # type: ignore[misc]


def test_secret_and_runtime_authority_fields_are_absent() -> None:
    forbidden = {
        "raw_secret", "decrypted_secret", "secret_hash", "secret_bytes",
        "metadata_fact_id", "currentness", "current", "current_pointer",
        "security_eligibility", "compromised", "revoked", "rotation_authorized",
        "idempotency_key", "security_revision", "cas", "payment_state",
        "settlement_state", "checkout", "binding",
    }
    assert forbidden.isdisjoint(set(_metadata().__dataclass_fields__))
    assert forbidden.isdisjoint(set(_metadata().to_dict()))
    assert forbidden.isdisjoint(set(_observation().__dataclass_fields__))


def test_provider_neutrality_is_structural() -> None:
    assert _metadata(provider_id="provider-neutral").provider_id == "provider-neutral"
    assert "PAYFAST" not in TenantInboundProviderCredentialMaterialMetadata.__module__
    assert "STRIPE" not in TenantInboundProviderCredentialMaterialMetadata.__module__


def test_no_currentness_or_metadata_id_is_claimed() -> None:
    assert not hasattr(_metadata(), "currentness")
    assert not hasattr(_metadata(), "metadata_fact_id")
    assert not hasattr(_metadata(), "is_current")


def test_no_registry_database_cas_or_idempotency_behavior_exists() -> None:
    value = _metadata()
    for name in ("persist", "save", "create", "ensure_indexes", "get_current", "cas", "idempotency_key"):
        assert not hasattr(value, name)


def test_fingerprint_integrity_does_not_claim_external_source_authentication() -> None:
    value = _metadata()
    assert value.verify_fingerprint()
    assert "authenticated" not in repr(value).lower()
    assert "verified" not in repr(value).lower()


def test_raw_configuration_correlation_does_not_prove_configuration_existence() -> None:
    value = _metadata(merchant_configuration_id="unregistered-config")
    assert value.merchant_configuration_id == "unregistered-config"
    assert value.merchant_configuration_fingerprint == CONFIGURATION_FINGERPRINT


def test_bare_opaque_version_does_not_prove_version_authority() -> None:
    value = _metadata(credential_version="caller-asserted-generation")
    assert value.credential_version == "caller-asserted-generation"
    assert not hasattr(value, "authenticated")


def test_observation_is_not_durable_authority() -> None:
    observation = _observation()
    assert not hasattr(observation, "metadata_fact_id")
    assert not hasattr(observation, "persist")
    assert not hasattr(observation, "is_current")


def test_security_binding_and_financial_claims_are_absent() -> None:
    value = _metadata()
    for name in (
        "is_eligible", "is_compromised", "is_revoked", "is_rotated",
        "bind_provider", "checkout", "mark_paid", "settle",
    ):
        assert not hasattr(value, name)


def test_every_semantic_field_changes_fingerprint() -> None:
    value = _metadata()
    changes: dict[str, object] = {
        "tenant_id": "tenant-b",
        "provider_id": "provider-b",
        "merchant_configuration_id": "config-b",
        "merchant_configuration_version": 2,
        "merchant_configuration_fingerprint": "b" * 128,
        "credential_reference": "secret-ref://tenant-a/config-a/v2",
        "credential_version": "generation-2",
        "metadata_source_identity": "metadata-adapter-b",
        "metadata_source_version": "adapter-contract-v2",
        "version_provenance_reference": "source-observation-b",
    }
    for field_name, changed in changes.items():
        altered = replace(value, metadata_fingerprint=None, **{field_name: changed})
        assert altered.fingerprint != value.fingerprint, field_name


def test_observation_round_trip_is_strict() -> None:
    observation = _observation()
    assert TenantInboundProviderCredentialMaterialObservation.from_dict(observation.to_dict()) == observation
    malformed = observation.to_dict()
    malformed["unexpected"] = "drift"
    with pytest.raises(TenantInboundProviderCredentialMaterialMetadataError, match="OBSERVATION_SCHEMA"):
        TenantInboundProviderCredentialMaterialObservation.from_dict(malformed)


def test_metadata_round_trip_rejects_unknown_and_missing_fields() -> None:
    payload = _metadata().to_dict()
    payload["unexpected"] = "drift"
    with pytest.raises(TenantInboundProviderCredentialMaterialMetadataError, match="METADATA_SCHEMA"):
        TenantInboundProviderCredentialMaterialMetadata.from_dict(payload)
    missing = _metadata().to_dict()
    del missing["credential_version"]
    with pytest.raises(TenantInboundProviderCredentialMaterialMetadataError, match="METADATA_SCHEMA"):
        TenantInboundProviderCredentialMaterialMetadata.from_dict(missing)


def test_import_surface_is_stdlib_only_and_has_no_side_effect_capabilities() -> None:
    source_path = (
        Path(__file__).resolve().parents[2]
        / "tools/eos/saas/domain/tenant_inbound_provider_credential_material_metadata.py"
    )
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    imported_roots = {
        (node.module or "").split(".")[0]
        for node in imports
        if isinstance(node, ast.ImportFrom)
    }
    imported_roots.update(alias.name.split(".")[0] for node in imports if isinstance(node, ast.Import) for alias in node.names)
    assert imported_roots <= {"__future__", "dataclasses", "datetime", "hashlib", "json", "re", "typing"}
    assert all(token not in source for token in ("pymongo", "boto3", "requests", "secret_manager", "kms"))


# ARTIFACT: test_tenant_inbound_provider_credential_material_metadata.py
# VERSION: v1.1.0-M11-R8-R3B-P8-P3D-P5-R4D-CERT
# AUTHORITY BOUNDARY: direct structural/value certificate only.
# FAIL-CLOSED POSTURE: invalid shape, provenance fields, timestamps, or digests reject.
# END OF WILSY OS SOVEREIGN ARTIFACT
