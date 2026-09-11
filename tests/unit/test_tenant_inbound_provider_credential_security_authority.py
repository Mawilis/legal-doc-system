"""WILSY OS direct certificate for the credential-security domain fact.

TITLE: Tenant Inbound Provider Credential Security Authority Tests
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove the closed provider-neutral credential-security value object,
         strict validity and fingerprint semantics, and all authority firewalls.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_provider_credential_security_authority.py
COLLABORATION / OWNERSHIP: Direct P2 domain certificate; registry, issuance,
                            current-pointer, binding, and provider owners remain deferred.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P2 certifies the four-state immutable
           credential-security authority domain contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque references only; no secret,
                             network, database, KMS, provider, or financial activity.
TENANT BOUNDARY: Fixtures bind one explicit tenant and configuration identity.
AUTHORITY BOUNDARY: Domain evidence only; no currentness, binding, checkout,
                    authorization lookup, or persistence authority.
FAIL-CLOSED DECLARATION: Invalid schema, identity, state, time, or digest rejects.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import inspect
from typing import Any, cast

import pytest

from tools.eos.saas.domain import tenant_inbound_provider_credential_security_authority as authority_module
from tools.eos.saas.domain.tenant_inbound_provider_credential_security_authority import (
    HASH_ALGORITHM,
    SECURITY_FINGERPRINT_SCHEMA,
    SECURITY_FINGERPRINT_VERSION,
    TenantInboundProviderCredentialSecurityAuthority,
    TenantInboundProviderCredentialSecurityAuthorityError,
    TenantInboundProviderCredentialSecurityState,
    is_valid_at,
)


AT = datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc)
END = AT + timedelta(hours=1)
CONFIGURATION_FINGERPRINT = "a" * 128
AUTHORIZATION_EVIDENCE_FINGERPRINT = "b" * 128


def _authority(**changes: object) -> TenantInboundProviderCredentialSecurityAuthority:
    """Build one valid synthetic authority for isolated direct assertions."""
    values: dict[str, object] = {
        "tenant_id": "tenant-security-a",
        "provider_id": "PAYFAST",
        "merchant_configuration_id": "merchant-config-a",
        "merchant_configuration_version": 1,
        "merchant_configuration_fingerprint": CONFIGURATION_FINGERPRINT,
        "credential_reference": "secret-ref://tenant-security-a/config-a/v1",
        "credential_version": "v1",
        "security_state": TenantInboundProviderCredentialSecurityState.ELIGIBLE,
        "security_revision": 0,
        "valid_from": AT,
        "valid_until": END,
        "evaluated_at": AT,
        "authorization_decision_id": "tenant-authorization-decision:credential-security-a",
        "authorization_evidence_fingerprint": AUTHORIZATION_EVIDENCE_FINGERPRINT,
    }
    values.update(changes)
    return TenantInboundProviderCredentialSecurityAuthority(
        **cast(dict[str, Any], values)
    )


@pytest.mark.parametrize(
    "state",
    list(TenantInboundProviderCredentialSecurityState),
)
def test_all_four_authorized_states_construct(state: TenantInboundProviderCredentialSecurityState) -> None:
    value = _authority(security_state=state)
    assert value.security_state is state
    assert value.security_fingerprint is not None


def test_fact_is_immutable_and_contains_no_current_pointer() -> None:
    value = _authority()
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        value.security_state = TenantInboundProviderCredentialSecurityState.REVOKED  # type: ignore[misc]
    fields = set(TenantInboundProviderCredentialSecurityAuthority.__dataclass_fields__)
    assert "is_current" not in fields
    assert "latest" not in fields
    assert "current_pointer" not in fields
    assert "raw_secret" not in fields
    assert "decrypted_secret" not in fields
    assert "plaintext_secret_hash" not in fields


def test_exact_fields_round_trip_and_provider_neutrality() -> None:
    value = _authority(provider_id="FUTURE_PROVIDER")
    restored = TenantInboundProviderCredentialSecurityAuthority.from_dict(value.to_dict())
    assert restored == value
    assert value.to_persisted() == value.to_dict()
    assert set(value.to_dict()) == {
        "tenant_id", "provider_id", "merchant_configuration_id",
        "merchant_configuration_version", "merchant_configuration_fingerprint",
        "credential_reference", "credential_version", "security_state",
        "security_revision", "valid_from", "valid_until", "evaluated_at",
        "authorization_decision_id", "authorization_evidence_fingerprint",
        "security_fingerprint_version", "security_fingerprint",
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tenant_id", ""),
        ("provider_id", ""),
        ("merchant_configuration_id", ""),
        ("merchant_configuration_version", 0),
        ("merchant_configuration_version", True),
        ("merchant_configuration_fingerprint", ""),
        ("credential_reference", ""),
        ("credential_version", ""),
        ("authorization_decision_id", ""),
        ("authorization_evidence_fingerprint", ""),
        ("tenant_id", "   "),
        ("provider_id", "  "),
        ("merchant_configuration_id", "\t"),
    ],
)
def test_blank_and_whitespace_identity_rejected(field: str, value: object) -> None:
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityError):
        _authority(**{field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("merchant_configuration_version", -1),
        ("merchant_configuration_version", False),
        ("security_revision", -1),
        ("security_revision", True),
        ("security_revision", "0"),
        ("security_state", "UNKNOWN"),
        ("security_fingerprint_version", "v2"),
    ],
)
def test_invalid_numeric_state_and_version_values_rejected(field: str, value: object) -> None:
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityError):
        _authority(**{field: value})


@pytest.mark.parametrize(
    "field",
    ["valid_from", "valid_until", "evaluated_at"],
)
def test_naive_time_rejected(field: str) -> None:
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityError):
        _authority(**{field: datetime(2026, 9, 10, 10, 0)})


def test_non_utc_time_rejected() -> None:
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityError):
        _authority(valid_from=AT.replace(tzinfo=timezone(timedelta(hours=2))))


@pytest.mark.parametrize(
    ("valid_from", "valid_until", "evaluated_at"),
    [
        (AT, AT, AT),
        (END, AT, AT),
        (AT, END, AT - timedelta(seconds=1)),
        (AT, END, END),
    ],
)
def test_validity_interval_and_evaluated_relation_fail_closed(
    valid_from: datetime, valid_until: datetime, evaluated_at: datetime
) -> None:
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityError):
        _authority(valid_from=valid_from, valid_until=valid_until, evaluated_at=evaluated_at)


def test_pure_half_open_validity_predicate() -> None:
    value = _authority(evaluated_at=AT + timedelta(minutes=1))
    assert value.is_valid_at(AT)
    assert value.is_valid_at(END - timedelta(microseconds=1))
    assert is_valid_at(AT, END, AT)
    assert not value.is_valid_at(END)
    assert not value.is_valid_at(AT - timedelta(microseconds=1))
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityError):
        value.is_valid_at(datetime(2026, 9, 10, 10, 0))


def test_eligible_is_historical_label_only() -> None:
    value = _authority()
    assert value.is_eligible
    assert value.security_state is TenantInboundProviderCredentialSecurityState.ELIGIBLE
    assert not hasattr(value, "current_pointer")
    assert not hasattr(value, "bind")


@pytest.mark.parametrize(
    ("field", "changed"),
    [
        ("tenant_id", "tenant-security-b"),
        ("provider_id", "OTHER_PROVIDER"),
        ("merchant_configuration_id", "merchant-config-b"),
        ("merchant_configuration_version", 2),
        ("merchant_configuration_fingerprint", "c" * 128),
        ("credential_reference", "secret-ref://tenant-security-a/config-a/v2"),
        ("credential_version", "v2"),
        ("security_state", TenantInboundProviderCredentialSecurityState.COMPROMISED),
        ("security_revision", 1),
        ("valid_from", AT + timedelta(seconds=1)),
        ("valid_until", END + timedelta(seconds=1)),
        ("evaluated_at", AT + timedelta(seconds=1)),
        ("authorization_decision_id", "tenant-authorization-decision:credential-security-b"),
        ("authorization_evidence_fingerprint", "d" * 128),
    ],
)
def test_every_authority_field_changes_fingerprint(field: str, changed: object) -> None:
    first = _authority(evaluated_at=AT + timedelta(minutes=1))
    second = replace(first, security_fingerprint=None, **{field: changed})
    assert second.fingerprint != first.fingerprint


def test_fingerprint_is_deterministic_and_sha3_512() -> None:
    first = _authority()
    second = _authority()
    assert first.fingerprint == second.fingerprint
    assert first.verify_fingerprint()
    assert first.verify_fingerprint(first.fingerprint)
    assert len(first.fingerprint) == 128
    assert first.fingerprint == first.fingerprint.lower()
    assert HASH_ALGORITHM == "SHA3-512"
    assert SECURITY_FINGERPRINT_VERSION == "v1"
    assert SECURITY_FINGERPRINT_SCHEMA == "WILSY-TENANT-INBOUND-PROVIDER-CREDENTIAL-SECURITY/V1"


def test_malformed_mismatched_and_unknown_fingerprint_rejected() -> None:
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityError):
        _authority(security_fingerprint="not-a-fingerprint")
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityError):
        _authority(security_fingerprint="0" * 128)
    payload = _authority().to_dict()
    payload["security_fingerprint_version"] = "v2"
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityError):
        TenantInboundProviderCredentialSecurityAuthority.from_dict(payload)


@pytest.mark.parametrize("missing", ["tenant_id", "security_state", "security_fingerprint"])
def test_strict_hydration_rejects_missing_fields(missing: str) -> None:
    payload = _authority().to_dict()
    del payload[missing]
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityError):
        TenantInboundProviderCredentialSecurityAuthority.from_dict(payload)


def test_strict_hydration_rejects_unknown_fields() -> None:
    payload = _authority().to_dict()
    payload["current_pointer"] = "forbidden"
    with pytest.raises(TenantInboundProviderCredentialSecurityAuthorityError):
        TenantInboundProviderCredentialSecurityAuthority.from_dict(payload)


def test_credential_reference_is_opaque_and_bounded_in_repr() -> None:
    value = _authority()
    rendered = repr(value)
    assert "[REDACTED_REFERENCE]" in rendered
    assert value.credential_reference not in rendered
    assert value.authorization_evidence_fingerprint in rendered
    assert "raw_secret" not in rendered.lower()
    assert "decrypted_secret" not in rendered.lower()


def test_non_eligible_states_are_historical_only() -> None:
    for state in (
        TenantInboundProviderCredentialSecurityState.COMPROMISED,
        TenantInboundProviderCredentialSecurityState.REVOKED,
        TenantInboundProviderCredentialSecurityState.ROTATED,
    ):
        value = _authority(security_state=state)
        assert not value.is_eligible
        assert value.security_state is state


def test_domain_has_no_runtime_or_persistence_dependencies() -> None:
    source = inspect.getsource(authority_module)
    assert "MongoClient" not in source
    assert "pymongo" not in source
    assert "socket" not in source
    assert "requests" not in source
    assert "resolve_secret" not in source
    assert "os.environ" not in source


def test_authorization_provenance_is_stored_but_not_reauthorized() -> None:
    value = _authority()
    serialized = value.to_dict()
    decision_id = serialized["authorization_decision_id"]
    assert isinstance(decision_id, str)
    assert decision_id.startswith("tenant-authorization-decision:")
    assert serialized["authorization_evidence_fingerprint"] == AUTHORIZATION_EVIDENCE_FINGERPRINT
    assert not hasattr(value, "authorize")
    assert not hasattr(value, "current_privilege")


# ARTIFACT: test_tenant_inbound_provider_credential_security_authority.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P2
# AUTHORITY BOUNDARY: direct immutable domain certificate only; no registry or issuance.
# TENANT POSTURE: every fixture is explicitly tenant and configuration scoped.
# FAIL-CLOSED POSTURE: malformed identities, state, time, schema, or digest reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no financial mutation.
# END OF WILSY OS SOVEREIGN ARTIFACT
