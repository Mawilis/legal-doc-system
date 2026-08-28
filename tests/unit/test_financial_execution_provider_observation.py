# -*- coding: utf-8 -*-
"""Unit certification for the immutable provider-neutral observation contract.

TITLE: Financial Execution Provider Observation Unit Certification
VERSION: v1.0.1-KENNEL-FINANCIAL-EXECUTION-PROVIDER-OBSERVATION-UNIT-CERT
PURPOSE: Certify validation, identity, deterministic evidence, and truth-boundary invariants.
CERTIFICATION AUTHORITY / SCOPE: Frozen provider-observation domain only.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
LAST UPDATED: 2026-08-28
COMPLIANCE: POPIA §19 | GDPR Art. 32 | SOC2 CC7.2
SECURITY / PRIVACY POSTURE: no raw payloads, credentials, settlement, or truth fields.
TENANT BOUNDARY: baseline observations use explicit tenant identity.
TRUTH BOUNDARY: provider observation is distinct from attempt, execution truth, and settlement.
CHANGELOG: v1.0.1 governance-only certification hardening; NO FINANCIAL SEMANTIC CHANGE.
"""
from datetime import datetime, timezone
from typing import Any
import pytest
from tools.eos.kennel.domain.financial_execution_provider_observation import EvidenceStrength, FinancialExecutionProviderObservation, ObservationError, ObservationStatus, TransportDisposition

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
NAIVE_NOW = datetime(2026, 1, 1)

def obs(**overrides: Any) -> FinancialExecutionProviderObservation:
    """Build a valid baseline observation without creating lifecycle or truth state."""
    values: dict[str, Any] = {"observation_id": "obs", "tenant_id": "t", "execution_attempt_id": "attempt", "provider_name": "P", "observation_status": ObservationStatus.PENDING, "observed_at": NOW}
    values.update(overrides)
    return FinancialExecutionProviderObservation(**values)

def test_valid_pending_and_authenticated_terminals() -> None:
    """Certify valid nonfinal, terminal-observation, unknown, and conflict values."""
    assert obs().observation_status is ObservationStatus.PENDING
    assert obs(observation_id="o2", observation_status=ObservationStatus.EXECUTED, provider_evidence_reference="e", evidence_strength=EvidenceStrength.AUTHENTICATED, provider_occurred_at=NOW).fingerprint
    assert obs(observation_id="o3", observation_status=ObservationStatus.FAILED, provider_evidence_reference="e", evidence_strength=EvidenceStrength.AUTHENTICATED)
    assert obs(observation_id="o4", observation_status=ObservationStatus.UNKNOWN)
    assert obs(observation_id="o5", observation_status=ObservationStatus.CONFLICT, evidence_strength=EvidenceStrength.CONFLICTING)

@pytest.mark.parametrize("field", ["tenant_id", "execution_attempt_id", "provider_name", "observation_id"])
def test_required_identity(field: str) -> None:
    """Certify fail-closed rejection of blank identities."""
    with pytest.raises(ObservationError): obs(**{field: " "})

def test_time_and_enum_validation() -> None:
    """Certify timezone and closed-vocabulary validation."""
    with pytest.raises(ObservationError): obs(observed_at=NAIVE_NOW)
    with pytest.raises(ObservationError): obs(provider_occurred_at=NAIVE_NOW)
    with pytest.raises(ObservationError): obs(correlation_fingerprint="bad")
    with pytest.raises(ObservationError): obs(observation_id="x", observation_status="PENDING")

def test_optional_occurrence_and_transport() -> None:
    """Certify optional occurrence and orthogonal transport ambiguity."""
    assert obs(provider_occurred_at=None, transport_disposition=TransportDisposition.AMBIGUOUS)

def test_determinism_and_material_fields() -> None:
    """Certify deterministic serialization and material fingerprint coverage."""
    a = obs(provider_request_reference="r", provider_evidence_reference="e", provider_occurred_at=NOW, evidence_strength=EvidenceStrength.AUTHENTICATED)
    b = obs(provider_request_reference="r", provider_evidence_reference="e", provider_occurred_at=NOW, evidence_strength=EvidenceStrength.AUTHENTICATED)
    assert a.to_dict() == b.to_dict()
    assert a.fingerprint == b.fingerprint
    assert a.fingerprint != obs(observation_id="x", provider_request_reference="r", provider_evidence_reference="e", provider_occurred_at=NOW, evidence_strength=EvidenceStrength.AUTHENTICATED).fingerprint
    assert a.fingerprint != obs(provider_request_reference="r", provider_evidence_reference="z", provider_occurred_at=NOW, evidence_strength=EvidenceStrength.AUTHENTICATED).fingerprint
    assert a.fingerprint != obs(provider_request_reference="r", provider_evidence_reference="e", provider_occurred_at=datetime(2026, 1, 2, tzinfo=timezone.utc), evidence_strength=EvidenceStrength.AUTHENTICATED).fingerprint

def test_immutable_and_truth_boundary() -> None:
    """Certify immutability and separation from final truth and settlement."""
    value = obs()
    with pytest.raises(AttributeError): setattr(value, "observation_status", ObservationStatus.FAILED)
    assert "SETTLED" not in [item.value for item in ObservationStatus]
    assert not hasattr(value, "finalize")
    assert "payload" not in value.to_dict()

# ARTIFACT: test_financial_execution_provider_observation.py
# VERSION: v1.0.1-KENNEL-FINANCIAL-EXECUTION-PROVIDER-OBSERVATION-UNIT-CERT
# TENANT POSTURE: explicit tenant identity; no cross-tenant inference.
# FAIL-CLOSED POSTURE: invalid identity, timestamps, vocabulary, or fingerprints are rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution truth; observation tests own none.
# NO FINANCIAL SEMANTIC CHANGE: governance-only certification hardening.
# END OF WILSY OS SOVEREIGN ARTIFACT
