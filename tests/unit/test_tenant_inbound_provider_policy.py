"""WILSY OS tenant inbound provider-policy direct certificate.

TITLE: Tenant Inbound Provider Policy Direct Certificate
VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P1
AUTHORITY: Wilsy OS Core Governance; immutable policy-domain evidence only.
EPITOME: Prove strict construction, deterministic identity, configuration
         snapshot binding, and security/financial boundary separation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_provider_policy.py
COLLABORATION / OWNERSHIP: Direct certificate for the SaaS provider-policy
                            domain; registry and lifecycle owners are deferred.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3C-P1 certifies the immutable V1 inbound
           collection policy contract and its SHA3-512 identity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only;
                             no raw secrets, credentials, KMS, or transport.
TENANT BOUNDARY: Every fixture is explicitly tenant scoped and binds one exact
                 merchant-configuration identity.
AUTHORITY BOUNDARY: This certificate covers immutable policy facts only; it does
                    not authorize generic operations or runtime activation.
FINANCIAL AUTHORITY BOUNDARY: No ClientInvoice, receivable, payment, settlement,
                              checkout, or Kennel execution behavior.
FAIL-CLOSED DECLARATION: Invalid schema, enum, timestamp, provenance, provider,
                          or digest data must reject.
"""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest

from tools.eos.saas.domain.tenant_inbound_merchant_configuration import InboundMerchantProviderId
from tools.eos.saas.domain.tenant_inbound_provider_policy import (
    POLICY_FINGERPRINT_VERSION,
    PolicyScope,
    TenantInboundProviderPolicy,
    TenantInboundProviderPolicyError,
    TenantInboundProviderPolicyScope,
)


_AT = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
_CONFIGURATION_FINGERPRINT = "a" * 128
_AUTH_EVIDENCE_FINGERPRINT = "b" * 128


def _policy(**overrides: object) -> TenantInboundProviderPolicy:
    """Build one valid synthetic PAYFAST policy for isolated direct assertions."""
    values: dict[str, object] = {
        "tenant_id": "tenant-policy-a",
        "provider_policy_id": "provider-policy-a",
        "policy_version": 1,
        "policy_scope": TenantInboundProviderPolicyScope.INBOUND_COLLECTION,
        "provider_id": InboundMerchantProviderId.PAYFAST,
        "merchant_configuration_id": "merchant-config-a",
        "merchant_configuration_version": 1,
        "merchant_configuration_fingerprint": _CONFIGURATION_FINGERPRINT,
        "authoring_authorization_reference": "tenant-authorization-decision:policy-create-a",
        "authoring_authorization_evidence_fingerprint": _AUTH_EVIDENCE_FINGERPRINT,
        "created_at": _AT,
    }
    values.update(overrides)
    return TenantInboundProviderPolicy(**cast(dict[str, Any], values))


def test_valid_payfast_policy_is_immutable_and_exactly_scoped() -> None:
    policy = _policy()
    assert policy.policy_scope is PolicyScope.INBOUND_COLLECTION
    assert policy.provider_id is InboundMerchantProviderId.PAYFAST
    assert policy.policy_fingerprint is not None and len(policy.policy_fingerprint) == 128
    assert policy.to_dict()["policy_fingerprint_version"] == POLICY_FINGERPRINT_VERSION
    with pytest.raises((AttributeError, TypeError)):
        policy.tenant_id = "other"  # type: ignore[misc]


def test_identical_policy_has_deterministic_fingerprint_and_round_trip() -> None:
    first = _policy()
    second = _policy()
    assert first.policy_fingerprint == second.policy_fingerprint
    assert first.to_dict() == second.to_dict()
    assert TenantInboundProviderPolicy.from_dict(first.to_dict()) == first
    assert first.to_persisted() == first.to_dict()
    assert first.verify_fingerprint()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tenant_id", "tenant-policy-b"),
        ("provider_policy_id", "provider-policy-b"),
        ("policy_version", 2),
        ("merchant_configuration_id", "merchant-config-b"),
        ("merchant_configuration_version", 2),
        ("merchant_configuration_fingerprint", "c" * 128),
        ("authoring_authorization_reference", "tenant-authorization-decision:policy-create-b"),
        ("authoring_authorization_evidence_fingerprint", "d" * 128),
        ("created_at", _AT + timedelta(seconds=1)),
    ],
)
def test_every_immutable_authority_field_changes_policy_fingerprint(field: str, value: object) -> None:
    first = _policy()
    second = replace(first, policy_fingerprint=None, **{field: value})
    assert second.policy_fingerprint != first.policy_fingerprint


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tenant_id", ""),
        ("provider_policy_id", ""),
        ("policy_version", 0),
        ("policy_version", True),
        ("merchant_configuration_id", ""),
        ("merchant_configuration_version", 0),
        ("merchant_configuration_version", True),
        ("merchant_configuration_fingerprint", "not-a-sha3"),
        ("authoring_authorization_reference", ""),
        ("authoring_authorization_evidence_fingerprint", "not-a-sha3"),
        ("created_at", datetime(2026, 9, 9, 12, 0)),
        ("created_at", _AT.replace(tzinfo=timezone(timedelta(hours=2)))),
        ("policy_fingerprint_version", "v2"),
        ("policy_scope", "WRONG_SCOPE"),
        ("provider_id", "PAYSHAP"),
        ("provider_id", "UNSUPPORTED_PROVIDER"),
    ],
)
def test_strict_construction_rejects_invalid_policy_values(field: str, value: object) -> None:
    with pytest.raises(TenantInboundProviderPolicyError):
        _policy(**{field: value})


def test_supplied_mismatched_fingerprint_and_corrupt_schema_fail_closed() -> None:
    policy = _policy()
    with pytest.raises(TenantInboundProviderPolicyError, match="FINGERPRINT"):
        replace(policy, policy_fingerprint="0" * 128)
    payload = policy.to_dict()
    payload["unexpected"] = True
    with pytest.raises(TenantInboundProviderPolicyError, match="SCHEMA"):
        TenantInboundProviderPolicy.from_dict(payload)
    missing = policy.to_dict()
    del missing["provider_id"]
    with pytest.raises(TenantInboundProviderPolicyError, match="SCHEMA"):
        TenantInboundProviderPolicy.from_dict(missing)


def test_configuration_snapshot_and_authoring_provenance_are_in_policy_identity() -> None:
    policy = _policy()
    serialized = policy.to_dict()
    assert serialized["tenant_id"] == "tenant-policy-a"
    assert serialized["merchant_configuration_id"] == "merchant-config-a"
    assert serialized["merchant_configuration_version"] == 1
    assert serialized["merchant_configuration_fingerprint"] == _CONFIGURATION_FINGERPRINT
    authorization_reference = serialized["authoring_authorization_reference"]
    assert isinstance(authorization_reference, str)
    assert authorization_reference.startswith("tenant-authorization-decision:")
    assert serialized["authoring_authorization_evidence_fingerprint"] == _AUTH_EVIDENCE_FINGERPRINT
    assert policy.verify_fingerprint(policy.policy_fingerprint)


def test_policy_has_no_currentness_secret_payment_or_runtime_authority_fields() -> None:
    fields = set(TenantInboundProviderPolicy.__dataclass_fields__)
    serialized = set(_policy().to_dict())
    forbidden = {
        "active", "enabled", "disabled", "deactivated", "emergency_disabled",
        "current_pointer", "current_secret_version", "secret_version", "raw_secret",
        "credential_bytes", "payment_state", "settlement_state", "routing_authority",
    }
    assert fields.isdisjoint(forbidden)
    assert serialized.isdisjoint(forbidden)
    assert not hasattr(_policy(), "activate")
    assert not hasattr(_policy(), "bind_provider")
    assert not hasattr(_policy(), "checkout")


def test_policy_v1_boundaries_are_explicit_and_provider_neutral() -> None:
    assert TenantInboundProviderPolicyScope.INBOUND_COLLECTION.value == "INBOUND_COLLECTION"
    assert InboundMerchantProviderId.PAYFAST.value == "PAYFAST"
    assert not hasattr(InboundMerchantProviderId, "PAYSHAP")
    assert "ClientInvoice" not in TenantInboundProviderPolicy.__module__
    assert "CommercialReceivable" not in TenantInboundProviderPolicy.__module__


# ARTIFACT: test_tenant_inbound_provider_policy.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P1
# AUTHORITY BOUNDARY: immutable policy-domain certificate only; no registry or activation.
# TENANT POSTURE: exact tenant/configuration identity is asserted in every fixture.
# FAIL-CLOSED POSTURE: malformed, unsupported, non-UTC, corrupt, or out-of-scope facts reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no financial mutation.
# END OF WILSY OS SOVEREIGN ARTIFACT
