"""TITLE: Accounts Payable Provider Selection Decision Certificate.
VERSION: v1.0.0-M11-P5-R1B-AP2D-R1.
AUTHORITY: Direct unit certification of the AP2D immutable domain fact.
EPITOME: Proves authority-slot identity, divergence, validation, and immutability.
ABSOLUTE CANONICAL PATH: tests/unit/test_accounts_payable_provider_selection_decision.py
COLLABORATION / OWNERSHIP: Kennel EOS AP2D domain certification.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 certifies deterministic AP selection identity and fingerprint behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Synthetic tenant-scoped evidence only.
AUTHORITY BOUNDARY: Certificate evidence only; no database, selection orchestration, or execution.
"""
from dataclasses import FrozenInstanceError
from typing import Any, cast

import pytest

from tools.eos.kennel.domain.accounts_payable_provider_selection_decision import (
    AccountsPayableProviderSelectionDecision,
    AccountsPayableProviderSelectionDecisionError,
)


FINGERPRINT_A = "a" * 128
FINGERPRINT_B = "b" * 128
FINGERPRINT_C = "c" * 128


def make_decision(**overrides: object) -> AccountsPayableProviderSelectionDecision:
    """Build synthetic values only; authority validation remains production-owned."""
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "execution_request_id": "request-a",
        "execution_request_fingerprint": FINGERPRINT_A,
        "runtime_binding_id": "binding-a",
        "runtime_binding_revision": 1,
        "runtime_binding_fingerprint": FINGERPRINT_B,
        "provider_policy_id": "policy-a",
        "provider_policy_revision": 1,
        "provider_policy_fingerprint": FINGERPRINT_C,
        "selected_provider": "PAYSHAP",
    }
    values.update(overrides)
    return AccountsPayableProviderSelectionDecision(**cast(Any, values))


def test_canonical_decision_constructs() -> None:
    value = make_decision()
    assert value.selected_provider == "PAYSHAP"
    assert len(value.selection_decision_id) == 128
    assert len(value.selection_decision_fingerprint) == 128


def test_selection_decision_id_is_deterministic() -> None:
    value = make_decision()
    assert value.selection_decision_id == value.derive_selection_decision_id()


def test_decision_fingerprint_is_deterministic() -> None:
    value = make_decision()
    assert value.selection_decision_fingerprint == value.derive_fingerprint()


def test_same_slot_same_provider_is_exact_reconstruction() -> None:
    first = make_decision()
    second = make_decision()
    assert first.selection_decision_id == second.selection_decision_id
    assert first.selection_decision_fingerprint == second.selection_decision_fingerprint
    assert first == second


def test_same_slot_different_provider_has_same_id_and_divergent_fingerprint() -> None:
    first = make_decision(selected_provider="PAYSHAP")
    second = make_decision(selected_provider="CARD")
    assert first.selection_decision_id == second.selection_decision_id
    assert first.selection_decision_fingerprint != second.selection_decision_fingerprint


def test_tenant_change_alters_id_and_fingerprint() -> None:
    base = make_decision()
    changed = make_decision(tenant_id="tenant-b")
    assert base.selection_decision_id != changed.selection_decision_id
    assert base.selection_decision_fingerprint != changed.selection_decision_fingerprint


def test_request_provenance_change_alters_id_and_fingerprint() -> None:
    base = make_decision()
    changed = make_decision(execution_request_fingerprint="d" * 128)
    assert base.selection_decision_id != changed.selection_decision_id
    assert base.selection_decision_fingerprint != changed.selection_decision_fingerprint


def test_runtime_binding_provenance_change_alters_id_and_fingerprint() -> None:
    base = make_decision()
    changed = make_decision(runtime_binding_revision=2)
    assert base.selection_decision_id != changed.selection_decision_id
    assert base.selection_decision_fingerprint != changed.selection_decision_fingerprint


def test_policy_provenance_change_alters_id_and_fingerprint() -> None:
    base = make_decision()
    changed = make_decision(provider_policy_id="policy-b")
    assert base.selection_decision_id != changed.selection_decision_id
    assert base.selection_decision_fingerprint != changed.selection_decision_fingerprint


def test_invalid_tenant_rejects() -> None:
    with pytest.raises(AccountsPayableProviderSelectionDecisionError):
        make_decision(tenant_id=" ")


@pytest.mark.parametrize("field,value", [("execution_request_id", ""), ("execution_request_fingerprint", "invalid")])
def test_invalid_request_identity_rejects(field: str, value: object) -> None:
    with pytest.raises(AccountsPayableProviderSelectionDecisionError):
        make_decision(**{field: value})


@pytest.mark.parametrize("field,value", [("runtime_binding_id", ""), ("runtime_binding_revision", 0), ("runtime_binding_fingerprint", "invalid")])
def test_invalid_runtime_binding_identity_rejects(field: str, value: object) -> None:
    with pytest.raises(AccountsPayableProviderSelectionDecisionError):
        make_decision(**{field: value})


@pytest.mark.parametrize("field,value", [("provider_policy_id", ""), ("provider_policy_revision", 0), ("provider_policy_fingerprint", "invalid")])
def test_invalid_policy_identity_rejects(field: str, value: object) -> None:
    with pytest.raises(AccountsPayableProviderSelectionDecisionError):
        make_decision(**{field: value})


def test_empty_selected_provider_rejects() -> None:
    with pytest.raises(AccountsPayableProviderSelectionDecisionError):
        make_decision(selected_provider="")


def test_wrong_supplied_decision_id_rejects() -> None:
    persisted = make_decision().to_persisted()
    persisted["selection_decision_id"] = "f" * 128
    with pytest.raises(AccountsPayableProviderSelectionDecisionError):
        AccountsPayableProviderSelectionDecision.from_persisted(persisted)


def test_wrong_supplied_decision_fingerprint_rejects() -> None:
    persisted = make_decision().to_persisted()
    persisted["selection_decision_fingerprint"] = "f" * 128
    with pytest.raises(AccountsPayableProviderSelectionDecisionError):
        AccountsPayableProviderSelectionDecision.from_persisted(persisted)


def test_decision_is_immutable() -> None:
    value = make_decision()
    with pytest.raises(FrozenInstanceError):
        value.selected_provider = "CARD"  # type: ignore[misc]


def test_persisted_round_trip_preserves_identity_and_fingerprint() -> None:
    value = make_decision()
    restored = AccountsPayableProviderSelectionDecision.from_persisted(value.to_persisted())
    assert restored == value
    assert restored.to_persisted() == value.to_persisted()


def test_authority_slot_excludes_selected_provider() -> None:
    first = make_decision(selected_provider="PAYSHAP")
    second = make_decision(selected_provider="CARD")
    assert "selected_provider" not in first.authority_slot_payload()
    assert first.authority_slot_payload() == second.authority_slot_payload()


def test_decision_payload_includes_selected_provider() -> None:
    value = make_decision()
    assert value.decision_payload()["selected_provider"] == "PAYSHAP"


# ARTIFACT: test_accounts_payable_provider_selection_decision.py
# VERSION: v1.0.0-M11-P5-R1B-AP2D-R1
# AUTHORITY BOUNDARY: direct AP selection-domain certificate only
# TENANT POSTURE: synthetic tenant-scoped fixtures; no persistence
# FAIL-CLOSED POSTURE: malformed and divergent immutable facts reject
# END OF WILSY OS SOVEREIGN ARTIFACT
