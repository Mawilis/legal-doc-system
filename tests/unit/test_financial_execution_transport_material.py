"""Unit certification for canonical financial transport material.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TRANSPORT-MATERIAL-UNIT-CERT
AUTHORITY: semantic pre-transport authority only; no wire, provider, truth, or settlement authority.
EPITOME: Proves deterministic reconstruction of secret-free material before provider I/O.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution_transport_material.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
CERTIFICATION DATE: 2026-08-28
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: synthetic opaque references only; no credentials or payloads.
TENANT BOUNDARY: all semantic identities remain explicit and immutable.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS owns execution truth; execution is not settlement.
CHANGELOG: v1.0.0 certifies canonical JSON, SHA3-512 fingerprints, lineage, and fail-closed validation.
"""
from __future__ import annotations

import hashlib
import inspect
import json

import pytest

from tools.eos.kennel.domain.financial_execution_transport_material import (
    FinancialExecutionTransportMaterial,
    FinancialExecutionTransportMaterialError,
)


FP_A = "a" * 128
FP_B = "b" * 128


def material(**changes: object) -> FinancialExecutionTransportMaterial:
    values: dict[str, object] = {
        "tenant_id": "tenant-1",
        "execution_command_id": "command-1",
        "execution_attempt_id": "attempt-1",
        "provider_name": "PAYSHAP",
        "transport_correlation_id": "wilsy-correlation-1",
        "amount_minor": 12500,
        "currency": "ZAR",
        "payment_destination_reference": "destination-ref-1",
        "destination_fingerprint": FP_A,
        "provider_metadata_reference": "metadata-ref-1",
        "provider_configuration_reference": "config-ref-1",
        "provider_configuration_fingerprint": FP_B,
    }
    values.update(changes)
    return FinancialExecutionTransportMaterial(**values)  # type: ignore[arg-type]


def test_valid_material_preserves_all_explicit_fields() -> None:
    value = material()
    assert value.tenant_id == "tenant-1"
    assert value.execution_command_id == "command-1"
    assert value.execution_attempt_id == "attempt-1"
    assert value.provider_name == "PAYSHAP"
    assert value.transport_correlation_id == "wilsy-correlation-1"
    assert value.amount_minor == 12500
    assert value.currency == "ZAR"
    assert value.payment_destination_reference == "destination-ref-1"
    assert value.destination_fingerprint == FP_A
    assert value.provider_metadata_reference == "metadata-ref-1"
    assert value.provider_configuration_reference == "config-ref-1"
    assert value.provider_configuration_fingerprint == FP_B
    assert value.execution_command_id != value.execution_attempt_id


def test_canonical_payload_is_sorted_compact_and_explicit() -> None:
    value = material()
    payload = value.canonical_payload()
    expected = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    assert value.canonical_bytes() == expected
    assert list(payload) == sorted(payload)
    assert b" " not in value.canonical_bytes()


def test_optional_none_values_are_explicit_nulls() -> None:
    value = material(destination_fingerprint=None, provider_metadata_reference=None, provider_configuration_reference=None, provider_configuration_fingerprint=None)
    payload = value.canonical_payload()
    for key in ("destination_fingerprint", "provider_metadata_reference", "provider_configuration_reference", "provider_configuration_fingerprint"):
        assert key in payload and payload[key] is None
        assert f'"{key}":null'.encode() in value.canonical_bytes()


def test_sha3_512_and_exact_replay_are_deterministic() -> None:
    first = material()
    second = material()
    independent = hashlib.sha3_512(first.canonical_bytes()).hexdigest()
    assert first == second
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.fingerprint == second.fingerprint == independent
    assert len(first.fingerprint) == 128
    assert first.fingerprint == first.fingerprint.lower()
    assert all(char in "0123456789abcdef" for char in first.fingerprint)


@pytest.mark.parametrize(
    "field,value",
    [
        ("tenant_id", "tenant-2"), ("execution_command_id", "command-2"),
        ("execution_attempt_id", "attempt-2"), ("provider_name", "ZAPPER"),
        ("transport_correlation_id", "wilsy-correlation-2"), ("amount_minor", 12501),
        ("currency", "USD"), ("payment_destination_reference", "destination-ref-2"),
        ("destination_fingerprint", FP_B), ("provider_metadata_reference", "metadata-ref-2"),
        ("provider_configuration_reference", "config-ref-2"),
        ("provider_configuration_fingerprint", "c" * 128),
    ],
)
def test_each_semantic_field_changes_bytes_and_fingerprint(field: str, value: object) -> None:
    changed = material(**{field: value})
    assert changed.canonical_bytes() != material().canonical_bytes()
    assert changed.fingerprint != material().fingerprint


@pytest.mark.parametrize("field", ["destination_fingerprint", "provider_metadata_reference", "provider_configuration_reference", "provider_configuration_fingerprint"])
def test_optional_none_differs_from_bound_value(field: str) -> None:
    none_value = material(**{field: None})
    assert none_value.fingerprint != material().fingerprint


@pytest.mark.parametrize("field", ["tenant_id", "execution_command_id", "execution_attempt_id", "provider_name", "transport_correlation_id", "payment_destination_reference"])
def test_required_opaque_fields_fail_closed(field: str) -> None:
    with pytest.raises(FinancialExecutionTransportMaterialError):
        material(**{field: " "})


@pytest.mark.parametrize("value", [0, -1, True, 1.5, "100"])
def test_amount_requires_positive_integer_minor_units(value: object) -> None:
    with pytest.raises(FinancialExecutionTransportMaterialError):
        material(amount_minor=value)


@pytest.mark.parametrize("value", ["zar", "ZA", "ZARR", "12R", ""])
def test_currency_requires_uppercase_three_letters(value: str) -> None:
    with pytest.raises(FinancialExecutionTransportMaterialError):
        material(currency=value)


@pytest.mark.parametrize("field", ["destination_fingerprint", "provider_configuration_fingerprint"])
@pytest.mark.parametrize("value", ["x", "A" * 128, "g" * 128])
def test_digest_fields_require_lowercase_sha3_512_hex(field: str, value: str) -> None:
    with pytest.raises(FinancialExecutionTransportMaterialError):
        material(**{field: value})


@pytest.mark.parametrize("field", ["payment_destination_reference", "provider_metadata_reference", "provider_configuration_reference"])
def test_secret_like_references_fail_closed(field: str) -> None:
    with pytest.raises(FinancialExecutionTransportMaterialError):
        material(**{field: "synthetic-api-key-credential"})


def test_identity_collapse_fails_closed_and_object_is_immutable() -> None:
    with pytest.raises(FinancialExecutionTransportMaterialError):
        material(execution_attempt_id="command-1")
    value = material()
    with pytest.raises(AttributeError):
        value.amount_minor = 1  # type: ignore[misc]
    assert value.fingerprint == value.fingerprint


def test_public_surface_excludes_time_outcome_secret_and_idempotency_authority() -> None:
    fields = set(inspect.signature(FinancialExecutionTransportMaterial).parameters)
    forbidden = {"created_at", "claimed_at", "recorded_at", "observed_at", "provider_occurred_at", "executed_at", "settled_at", "provider_request_reference", "provider_execution_reference", "provider_evidence_reference", "observation_status", "api_key", "access_token", "password", "private_key", "idempotency_key"}
    assert not fields.intersection(forbidden)
    assert not hasattr(material(), "send")


# ARTIFACT: test_financial_execution_transport_material.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TRANSPORT-MATERIAL-UNIT-CERT
# AUTHORITY BOUNDARY: tests certify semantic material only; transport evidence and provider I/O remain separate.
# TENANT POSTURE: tenant, command, attempt, destination, and correlation identities remain explicit.
# FAIL-CLOSED POSTURE: malformed semantics, fingerprints, secrets, and authority collisions are rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; execution is not settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
