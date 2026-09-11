"""Direct certificate for the immutable credential-metadata source registry.

TITLE: Tenant Inbound Provider Credential Metadata Source Registry Tests
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exact descriptor identity, canonical SHA3-512 evidence, and
         fail-closed immutable source resolution without external side effects.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_provider_credential_metadata_source_registry.py
COLLABORATION / OWNERSHIP: Direct P5-R8-P3 source-registry certificate owner;
                            merchant configuration and runtime adapter tests
                            remain separate owners.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3-CERT covers the 23 required identity,
           canonicalization, lookup, immutability, and import-firewall cases.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque descriptors only; no secret,
                             provider, KMS, network, Mongo, or client activity.
TENANT BOUNDARY: Registry entries are platform-scoped; tenant route authority
                 is intentionally absent and remains issuance-owned.
AUTHORITY BOUNDARY: Tests prove registration resolution, never tenant
                    authorization, runtime authentication, or payment authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Any schema, identity, provenance, digest, lookup, or
                          mutation violation must reject.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields
import importlib
import inspect
from typing import Mapping, cast

import pytest

from tools.eos.saas.billing.tenant_inbound_provider_credential_metadata_source_registry import (
    CAPABILITY_CLASS_CREDENTIAL_METADATA,
    ENTRY_FINGERPRINT_SCHEMA,
    TenantInboundCredentialMetadataSourceContractVersionUnknownError,
    TenantInboundCredentialMetadataSourceDescriptor,
    TenantInboundCredentialMetadataSourceDescriptorError,
    TenantInboundCredentialMetadataSourceDuplicateRegistrationError,
    TenantInboundCredentialMetadataSourceFingerprintMismatchError,
    TenantInboundCredentialMetadataSourceRegistrationProvenance,
    TenantInboundCredentialMetadataSourceRegistry,
    TenantInboundCredentialMetadataSourceUnknownError,
    compute_entry_fingerprint,
)


def _provenance(**changes: object) -> TenantInboundCredentialMetadataSourceRegistrationProvenance:
    """Build valid synthetic platform provenance with no sensitive material."""
    values: dict[str, object] = {
        "platform_registration_id": "platform-registration-1",
        "deployment_certification_id": "deployment-certification-1",
    }
    values.update(changes)
    return TenantInboundCredentialMetadataSourceRegistrationProvenance(
        platform_registration_id=cast(str, values["platform_registration_id"]),
        deployment_certification_id=cast(str, values["deployment_certification_id"]),
    )


def _descriptor(**changes: object) -> TenantInboundCredentialMetadataSourceDescriptor:
    """Build one valid immutable descriptor."""
    values: dict[str, object] = {
        "source_identity": "source-alpha",
        "source_contract_version": "v1",
        "implementation_identity": "impl:credential-metadata-alpha",
        "capability_class": CAPABILITY_CLASS_CREDENTIAL_METADATA,
        "registration_provenance": _provenance(),
    }
    values.update(changes)
    return TenantInboundCredentialMetadataSourceDescriptor.create(
        source_identity=cast(str, values["source_identity"]),
        source_contract_version=cast(str, values["source_contract_version"]),
        implementation_identity=cast(str, values["implementation_identity"]),
        capability_class=cast(str, values["capability_class"]),
        registration_provenance=cast(
            TenantInboundCredentialMetadataSourceRegistrationProvenance,
            values["registration_provenance"],
        ),
    )


def test_exact_six_field_descriptor_contract_and_registration_identity() -> None:
    assert [item.name for item in fields(TenantInboundCredentialMetadataSourceDescriptor)] == [
        "source_identity",
        "source_contract_version",
        "implementation_identity",
        "capability_class",
        "registration_provenance",
        "entry_fingerprint",
    ]
    value = _descriptor()
    assert (value.source_identity, value.source_contract_version) == ("source-alpha", "v1")
    assert set(value.to_dict()) == set(TenantInboundCredentialMetadataSourceDescriptor._FIELDS)


def test_strict_field_validation_and_caller_fingerprint_rejection() -> None:
    with pytest.raises(TenantInboundCredentialMetadataSourceDescriptorError):
        _descriptor(source_identity=" source-alpha ")
    with pytest.raises(TenantInboundCredentialMetadataSourceDescriptorError):
        TenantInboundCredentialMetadataSourceDescriptor(
            source_identity="source-alpha",
            source_contract_version="v1",
            implementation_identity="impl:credential-metadata-alpha",
            capability_class=CAPABILITY_CLASS_CREDENTIAL_METADATA,
            registration_provenance=_provenance(),
            entry_fingerprint="0" * 128,
        )
    payload = _descriptor().to_dict()
    payload["entry_fingerprint"] = "0" * 128
    with pytest.raises(TenantInboundCredentialMetadataSourceFingerprintMismatchError):
        TenantInboundCredentialMetadataSourceDescriptor.from_dict(payload)


def test_unknown_descriptor_fields_are_rejected() -> None:
    payload = _descriptor().to_dict()
    payload["unexpected"] = "nope"
    with pytest.raises(TenantInboundCredentialMetadataSourceDescriptorError):
        TenantInboundCredentialMetadataSourceDescriptor.from_dict(payload)


def test_registration_provenance_is_exact_and_validated() -> None:
    value = _descriptor()
    provenance = cast(
        TenantInboundCredentialMetadataSourceRegistrationProvenance,
        value.registration_provenance,
    )
    assert provenance.to_dict() == {
        "platform_registration_id": "platform-registration-1",
        "deployment_certification_id": "deployment-certification-1",
    }
    with pytest.raises(TenantInboundCredentialMetadataSourceDescriptorError):
        _descriptor(registration_provenance={"platform_registration_id": "only"})


def test_capability_class_is_closed() -> None:
    with pytest.raises(TenantInboundCredentialMetadataSourceDescriptorError):
        _descriptor(capability_class="payment_provider")


def test_implementation_identity_is_typed_opaque_and_not_import_path() -> None:
    with pytest.raises(TenantInboundCredentialMetadataSourceDescriptorError):
        _descriptor(implementation_identity="tools.eos.secret.Client")
    with pytest.raises(TenantInboundCredentialMetadataSourceDescriptorError):
        _descriptor(implementation_identity="impl:../secret")


def test_canonical_nfc_normalization_is_applied() -> None:
    decomposed = "source-e\u0301"
    composed = "source-é"
    assert _descriptor(source_identity=decomposed).source_identity == composed


def test_canonical_byte_serialization_has_frozen_schema_and_no_whitespace() -> None:
    value = _descriptor()
    raw = value.canonical_bytes()
    assert raw.startswith(b'{"schema":"' + ENTRY_FINGERPRINT_SCHEMA.encode() + b'"')
    assert b" " not in raw
    assert b"\n" not in raw
    assert not raw.endswith(b"\n")


def test_non_ascii_utf8_serialization_is_deterministic() -> None:
    first = _descriptor(source_identity="source-é")
    second = _descriptor(source_identity="source-e\u0301")
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.entry_fingerprint == second.entry_fingerprint


def test_outer_canonical_key_order_is_exact() -> None:
    assert list(_descriptor().canonical_payload()) == [
        "schema",
        "source_identity",
        "source_contract_version",
        "implementation_identity",
        "capability_class",
        "registration_provenance",
    ]


def test_nested_provenance_key_order_is_exact() -> None:
    provenance = cast(Mapping[str, object], _descriptor().canonical_payload()["registration_provenance"])
    assert list(provenance) == [
        "platform_registration_id",
        "deployment_certification_id",
    ]


def test_sha3_512_fingerprint_is_lowercase_128_hex() -> None:
    value = _descriptor()
    assert value.entry_fingerprint is not None
    assert len(value.entry_fingerprint) == 128
    assert value.entry_fingerprint == value.entry_fingerprint.lower()
    assert all(char in "0123456789abcdef" for char in value.entry_fingerprint)


def test_every_fingerprint_bearing_field_is_in_canonical_payload() -> None:
    value = _descriptor()
    payload = value.canonical_payload()
    assert set(payload) == {
        "schema",
        "source_identity",
        "source_contract_version",
        "implementation_identity",
        "capability_class",
        "registration_provenance",
    }
    assert "entry_fingerprint" not in payload


def test_fingerprint_recomputation_is_deterministic() -> None:
    value = _descriptor()
    assert value.verify_fingerprint()
    assert value.entry_fingerprint == compute_entry_fingerprint(
        value.source_identity,
        value.source_contract_version,
        value.implementation_identity,
        value.capability_class,
        value.registration_provenance,
    )


def test_registration_provenance_mutation_changes_fingerprint() -> None:
    assert _descriptor().entry_fingerprint != _descriptor(
        registration_provenance=_provenance(platform_registration_id="platform-registration-2")
    ).entry_fingerprint


def test_implementation_identity_mutation_changes_fingerprint() -> None:
    assert _descriptor().entry_fingerprint != _descriptor(
        implementation_identity="impl:credential-metadata-beta"
    ).entry_fingerprint


def test_contract_version_mutation_changes_fingerprint() -> None:
    assert _descriptor().entry_fingerprint != _descriptor(
        source_contract_version="v2"
    ).entry_fingerprint


def test_exact_two_field_lookup_returns_immutable_descriptor() -> None:
    value = _descriptor()
    registry = TenantInboundCredentialMetadataSourceRegistry.from_descriptors((value,))
    assert registry.resolve("source-alpha", "v1") == value
    assert registry.lookup("source-alpha", "v1") == value
    assert registry.descriptors() == (value,)


def test_unknown_source_identity_fails_closed() -> None:
    registry = TenantInboundCredentialMetadataSourceRegistry.from_descriptors((_descriptor(),))
    with pytest.raises(TenantInboundCredentialMetadataSourceUnknownError):
        registry.resolve("source-missing", "v1")


def test_unknown_contract_version_fails_closed() -> None:
    registry = TenantInboundCredentialMetadataSourceRegistry.from_descriptors((_descriptor(),))
    with pytest.raises(TenantInboundCredentialMetadataSourceContractVersionUnknownError):
        registry.resolve("source-alpha", "v2")


def test_latest_contract_version_is_never_auto_selected() -> None:
    registry = TenantInboundCredentialMetadataSourceRegistry.from_descriptors(
        (_descriptor(source_contract_version="v1"), _descriptor(source_contract_version="v2"))
    )
    with pytest.raises(TenantInboundCredentialMetadataSourceContractVersionUnknownError):
        registry.resolve("source-alpha", "v3")
    assert registry.resolve("source-alpha", "v1").source_contract_version == "v1"


def test_descriptor_and_registry_are_immutable_and_duplicate_keys_reject() -> None:
    value = _descriptor()
    with pytest.raises((FrozenInstanceError, AttributeError)):
        value.source_identity = "changed"  # type: ignore[misc]
    registry = TenantInboundCredentialMetadataSourceRegistry.from_descriptors((value,))
    with pytest.raises(AttributeError):
        registry._entries = {}  # type: ignore[misc]
    with pytest.raises(TenantInboundCredentialMetadataSourceDuplicateRegistrationError):
        TenantInboundCredentialMetadataSourceRegistry.from_descriptors((value, value))


def test_import_side_effect_firewall_has_no_external_runtime_access() -> None:
    module = importlib.import_module(
        "tools.eos.saas.billing.tenant_inbound_provider_credential_metadata_source_registry"
    )
    tree = ast.parse(inspect.getsource(module))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert imported <= {"dataclasses", "hashlib", "hmac", "json", "re", "unicodedata", "types", "typing"}
    assert not hasattr(module.TenantInboundCredentialMetadataSourceRegistry, "register")
    assert not hasattr(module.TenantInboundCredentialMetadataSourceRegistry, "unregister")


# ARTIFACT: test_tenant_inbound_provider_credential_metadata_source_registry.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3-CERT
# AUTHORITY BOUNDARY: direct source-registry contract only
# TENANT POSTURE: platform registration is not tenant route authorization
# FAIL-CLOSED POSTURE: every required identity and integrity violation rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
