"""Direct certificate for the immutable P5 activation-domain facts.

TITLE: Tenant Inbound Provider Policy Activation Domain Tests
VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P5
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves closed activation event shapes, deterministic identity, and firewalls.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_provider_policy_activation.py
COLLABORATION / OWNERSHIP: Direct P5 domain certificate; no registry or orchestration ownership.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3C-P5 certifies immutable domain representation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
import inspect
import sys
from typing import Any, cast

import pytest

from tools.eos.saas.domain.tenant_inbound_merchant_configuration import InboundMerchantProviderId
from tools.eos.saas.domain.tenant_inbound_provider_policy import TenantInboundProviderPolicyScope
from tools.eos.saas.domain.tenant_inbound_provider_policy_activation import (
    ACTIVATION_EVENT_FINGERPRINT_SCHEMA,
    ACTIVATION_EVENT_FINGERPRINT_VERSION,
    TenantInboundProviderPolicyActivationError,
    TenantInboundProviderPolicyActivationEvent,
    TenantInboundProviderPolicyActivationEventKind,
    TenantInboundProviderPolicyReference,
)


VERSION = "v1.0.0-M11-R8-R3B-P8-P3C-P5"
CAMPAIGN_IDENTITY = "M11-R8-R3B-P8-P3C-P5"


NOW = datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc)


def _reference(**changes: object) -> TenantInboundProviderPolicyReference:
    values: dict[str, object] = {
        "provider_policy_id": "policy-1",
        "policy_version": 1,
        "policy_fingerprint": "a" * 128,
        "provider_id": InboundMerchantProviderId.PAYFAST,
        "merchant_configuration_id": "config-1",
        "merchant_configuration_version": 1,
        "merchant_configuration_fingerprint": "b" * 128,
    }
    values.update(changes)
    return TenantInboundProviderPolicyReference(**values)  # type: ignore[arg-type]


def _event(kind: object = TenantInboundProviderPolicyActivationEventKind.ACTIVATE, **changes: object) -> TenantInboundProviderPolicyActivationEvent:
    values: dict[str, object] = {
        "tenant_id": "tenant-1",
        "policy_scope": TenantInboundProviderPolicyScope.INBOUND_COLLECTION,
        "activation_event_id": "event-1",
        "activation_revision": 0,
        "event_kind": cast(Any, kind),
        "lifecycle_idempotency_key": "idem-1",
        "prior_active_policy": None,
        "target_active_policy": _reference(),
        "authorization_reference": "auth-1",
        "authorization_evidence_fingerprint": "c" * 128,
        "reason_reference": "reason-1",
        "occurred_at": NOW,
        "activation_event_fingerprint_version": ACTIVATION_EVENT_FINGERPRINT_VERSION,
    }
    if kind is TenantInboundProviderPolicyActivationEventKind.SUPERSEDE:
        values["prior_active_policy"] = _reference()
        values["target_active_policy"] = _reference(provider_policy_id="policy-2")
    elif kind in (TenantInboundProviderPolicyActivationEventKind.DEACTIVATE, TenantInboundProviderPolicyActivationEventKind.EMERGENCY_DISABLE):
        values["prior_active_policy"] = _reference()
        values["target_active_policy"] = None
    values.update(changes)
    return TenantInboundProviderPolicyActivationEvent(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("kind", list(TenantInboundProviderPolicyActivationEventKind))
def test_valid_event_kinds(kind: TenantInboundProviderPolicyActivationEventKind) -> None:
    event = _event(kind)
    assert event.event_kind is kind
    assert event.verify_fingerprint()


@pytest.mark.parametrize(
    ("kind", "changes"),
    [
        (TenantInboundProviderPolicyActivationEventKind.ACTIVATE, {"target_active_policy": None}),
        (TenantInboundProviderPolicyActivationEventKind.ACTIVATE, {"prior_active_policy": _reference()}),
        (TenantInboundProviderPolicyActivationEventKind.SUPERSEDE, {"prior_active_policy": None}),
        (TenantInboundProviderPolicyActivationEventKind.SUPERSEDE, {"target_active_policy": None}),
        (TenantInboundProviderPolicyActivationEventKind.SUPERSEDE, {"target_active_policy": _reference()}),
        (TenantInboundProviderPolicyActivationEventKind.DEACTIVATE, {"prior_active_policy": None}),
        (TenantInboundProviderPolicyActivationEventKind.DEACTIVATE, {"target_active_policy": _reference()}),
        (TenantInboundProviderPolicyActivationEventKind.EMERGENCY_DISABLE, {"prior_active_policy": None}),
        (TenantInboundProviderPolicyActivationEventKind.EMERGENCY_DISABLE, {"target_active_policy": _reference()}),
        (TenantInboundProviderPolicyActivationEventKind.ACTIVATE, {"reason_reference": ""}),
        (TenantInboundProviderPolicyActivationEventKind.SUPERSEDE, {"reason_reference": ""}),
        (TenantInboundProviderPolicyActivationEventKind.DEACTIVATE, {"reason_reference": ""}),
        (TenantInboundProviderPolicyActivationEventKind.EMERGENCY_DISABLE, {"reason_reference": ""}),
    ],
)
def test_transition_shape_and_reason_fail_closed(kind: TenantInboundProviderPolicyActivationEventKind, changes: dict[str, object]) -> None:
    with pytest.raises(TenantInboundProviderPolicyActivationError):
        _event(kind, **changes)


@pytest.mark.parametrize(
    "field",
    [
        "provider_policy_id", "policy_version", "policy_fingerprint", "provider_id",
        "merchant_configuration_id", "merchant_configuration_version", "merchant_configuration_fingerprint",
    ],
)
def test_policy_reference_fields_change_event_fingerprint(field: str) -> None:
    changed = {
        "provider_policy_id": "policy-2", "policy_version": 2, "policy_fingerprint": "d" * 128,
        "provider_id": InboundMerchantProviderId.PAYFAST, "merchant_configuration_id": "config-2",
        "merchant_configuration_version": 2, "merchant_configuration_fingerprint": "e" * 128,
    }[field]
    if field == "provider_id":
        # V1 has one representable provider; its serialized provider token is
        # still covered by strict schema rejection rather than a second enum member.
        payload = _reference().to_dict()
        payload["provider_id"] = "OTHER_PROVIDER"
        with pytest.raises(TenantInboundProviderPolicyActivationError):
            TenantInboundProviderPolicyReference.from_dict(payload)
        return
    altered = _reference(**{field: changed})
    assert altered != _reference()
    assert _event(target_active_policy=altered).fingerprint != _event().fingerprint


@pytest.mark.parametrize(
    "field",
    ["event_kind", "activation_revision", "lifecycle_idempotency_key", "authorization_reference", "authorization_evidence_fingerprint", "reason_reference", "occurred_at"],
)
def test_event_fields_change_fingerprint(field: str) -> None:
    values: dict[str, object] = {
        "event_kind": TenantInboundProviderPolicyActivationEventKind.DEACTIVATE,
        "activation_revision": 1,
        "lifecycle_idempotency_key": "idem-2",
        "authorization_reference": "auth-2",
        "authorization_evidence_fingerprint": "d" * 128,
        "reason_reference": "reason-2",
        "occurred_at": NOW.replace(second=1),
    }
    if field == "event_kind":
        changed_event = _event(
            TenantInboundProviderPolicyActivationEventKind.DEACTIVATE,
            prior_active_policy=_reference(),
            target_active_policy=None,
        )
    else:
        changed_event = _event(**{field: cast(object, values[field])})
    assert changed_event.fingerprint != _event().fingerprint


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tenant_id", ""), ("policy_scope", "OUTBOUND"), ("activation_event_id", ""),
        ("activation_revision", -1), ("lifecycle_idempotency_key", ""), ("event_kind", "UNKNOWN"),
        ("authorization_evidence_fingerprint", "bad"), ("occurred_at", datetime(2026, 9, 10, 10, 0)),
    ],
)
def test_malformed_event_fields_reject(field: str, value: object) -> None:
    with pytest.raises((TenantInboundProviderPolicyActivationError, ValueError)):
        _event(**{field: value})


@pytest.mark.parametrize("field", ["policy_fingerprint", "merchant_configuration_fingerprint"])
def test_malformed_reference_fingerprint_reject(field: str) -> None:
    with pytest.raises(TenantInboundProviderPolicyActivationError):
        _reference(**{field: "bad"})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("provider_policy_id", ""),
        ("policy_version", 0),
        ("policy_version", True),
        ("merchant_configuration_id", ""),
        ("merchant_configuration_version", 0),
        ("merchant_configuration_version", False),
        ("provider_id", "PAYFAST"),
        ("provider_id", None),
    ],
)
def test_malformed_reference_identity_reject(field: str, value: object) -> None:
    with pytest.raises((TenantInboundProviderPolicyActivationError, ValueError)):
        _reference(**{field: value})


def test_supplied_mismatched_event_fingerprint_rejects() -> None:
    with pytest.raises(TenantInboundProviderPolicyActivationError):
        _event(activation_event_fingerprint="f" * 128)


@pytest.mark.parametrize("extra", ["unexpected", "schema", "current_pointer", "latest_policy"])
def test_event_hydration_rejects_schema_drift(extra: str) -> None:
    payload = _event().to_dict()
    payload[extra] = "drift"
    with pytest.raises(TenantInboundProviderPolicyActivationError):
        TenantInboundProviderPolicyActivationEvent.from_dict(payload)


def test_reference_and_event_round_trip_is_strict_and_deterministic() -> None:
    event = _event()
    restored = TenantInboundProviderPolicyActivationEvent.from_dict(event.to_dict())
    assert restored == event
    assert restored.fingerprint == event.fingerprint
    assert TenantInboundProviderPolicyReference.from_dict(_reference().to_dict()) == _reference()
    assert ACTIVATION_EVENT_FINGERPRINT_SCHEMA.endswith("/V1")


def test_frozen_immutability() -> None:
    with pytest.raises(FrozenInstanceError):
        _event().tenant_id = "other"  # type: ignore[misc]


def test_supercede_allows_version_or_policy_id_change() -> None:
    assert _event(
        TenantInboundProviderPolicyActivationEventKind.SUPERSEDE,
        prior_active_policy=_reference(),
        target_active_policy=_reference(policy_version=2),
    ).target_active_policy != _event(
        TenantInboundProviderPolicyActivationEventKind.SUPERSEDE,
        prior_active_policy=_reference(),
        target_active_policy=_reference(provider_policy_id="policy-2"),
    ).target_active_policy


def test_forbidden_security_and_authority_fields_absent() -> None:
    event_fields = set(TenantInboundProviderPolicyActivationEvent.__dataclass_fields__)
    reference_fields = set(TenantInboundProviderPolicyReference.__dataclass_fields__)
    forbidden = {"credential_security_fact", "credential_safe", "current_secret_version", "raw_secret", "kms_result", "binding_eligibility", "checkout_eligibility", "current_pointer", "current_policy", "latest_policy"}
    assert not event_fields & forbidden
    assert not reference_fields & forbidden


def test_domain_has_no_persistence_authorization_or_clock_ownership() -> None:
    source = inspect.getsource(sys.modules[TenantInboundProviderPolicyActivationEvent.__module__])
    assert "MongoClient" not in source
    assert "start_transaction" not in source
    assert "authorization_decision" not in source
    assert "datetime.now" not in source


def test_no_commercial_or_financial_dependencies() -> None:
    source = inspect.getsource(sys.modules[TenantInboundProviderPolicyActivationEvent.__module__])
    assert "ClientInvoice" not in source
    assert "receivable" not in source.lower()
    assert "financial_execution" not in source.lower()


def test_event_serialization_excludes_mutable_current_pointer() -> None:
    payload = _event().to_dict()
    assert "current_pointer" not in payload
    assert "current_policy" not in payload
    assert payload["prior_active_policy"] is None


# ARTIFACT: test_tenant_inbound_provider_policy_activation.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P5
# AUTHORITY BOUNDARY: direct immutable-domain certificate only; no persistence or orchestration.
# FAIL-CLOSED POSTURE: every required malformed shape and forbidden authority field is tested.
# END OF WILSY OS SOVEREIGN ARTIFACT
