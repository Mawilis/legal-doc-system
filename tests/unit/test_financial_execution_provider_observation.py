# -*- coding: utf-8 -*-
"""Unit certification for the provider-neutral observation contract."""
from datetime import datetime, timezone
from typing import Any
import pytest
from tools.eos.kennel.domain.financial_execution_provider_observation import *

NOW=datetime(2026,1,1,tzinfo=timezone.utc)
def obs(**kw: Any) -> FinancialExecutionProviderObservation:
    v: dict[str, Any]=dict(observation_id="obs",tenant_id="t",execution_attempt_id="attempt",provider_name="P",observation_status=ObservationStatus.PENDING,observed_at=NOW)
    v.update(kw); return FinancialExecutionProviderObservation(**v)

def test_valid_pending_and_authenticated_terminals():
    assert obs().observation_status is ObservationStatus.PENDING
    assert obs(observation_id="o2",observation_status=ObservationStatus.EXECUTED,provider_evidence_reference="e",evidence_strength=EvidenceStrength.AUTHENTICATED,provider_occurred_at=NOW).fingerprint
    assert obs(observation_id="o3",observation_status=ObservationStatus.FAILED,provider_evidence_reference="e",evidence_strength=EvidenceStrength.AUTHENTICATED)
    assert obs(observation_id="o4",observation_status=ObservationStatus.UNKNOWN)
    assert obs(observation_id="o5",observation_status=ObservationStatus.CONFLICT,evidence_strength=EvidenceStrength.CONFLICTING)

@pytest.mark.parametrize("field",["tenant_id","execution_attempt_id","provider_name","observation_id"])
def test_required_identity(field):
    with pytest.raises(ObservationError): obs(**{field:" "})

def test_time_and_enum_validation():
    with pytest.raises(ObservationError): obs(observed_at=datetime.now())
    with pytest.raises(ObservationError): obs(provider_occurred_at=datetime.now())
    with pytest.raises(ObservationError): obs(correlation_fingerprint="bad")
    with pytest.raises(ObservationError): obs(observation_id="x",observation_status="PENDING")

def test_optional_occurrence_and_transport():
    assert obs(provider_occurred_at=None,transport_disposition=TransportDisposition.AMBIGUOUS)

def test_determinism_and_material_fields():
    a=obs(provider_request_reference="r",provider_evidence_reference="e",provider_occurred_at=NOW,evidence_strength=EvidenceStrength.AUTHENTICATED); b=obs(provider_request_reference="r",provider_evidence_reference="e",provider_occurred_at=NOW,evidence_strength=EvidenceStrength.AUTHENTICATED)
    assert a.to_dict()==b.to_dict() and a.fingerprint==b.fingerprint
    assert a.fingerprint != obs(observation_id="x",provider_request_reference="r",provider_evidence_reference="e",provider_occurred_at=NOW,evidence_strength=EvidenceStrength.AUTHENTICATED).fingerprint
    assert a.fingerprint != obs(provider_request_reference="r",provider_evidence_reference="z",provider_occurred_at=NOW,evidence_strength=EvidenceStrength.AUTHENTICATED).fingerprint
    assert a.fingerprint != obs(provider_request_reference="r",provider_evidence_reference="e",provider_occurred_at=datetime(2026,1,2,tzinfo=timezone.utc),evidence_strength=EvidenceStrength.AUTHENTICATED).fingerprint

def test_immutable_and_truth_boundary():
    a=obs()
    with pytest.raises(AttributeError): setattr(a,"observation_status",ObservationStatus.FAILED)
    assert "SETTLED" not in [x.value for x in ObservationStatus]; assert not hasattr(a,"finalize"); assert "payload" not in a.to_dict()
