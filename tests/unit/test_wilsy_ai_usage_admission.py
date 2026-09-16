"""TITLE: C1B usage admission direct certificate.
VERSION: v1.0.1-C1B-R3B
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certify immutable reservation states, replay, divergence, and held capacity.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_usage_admission.py
CHANGELOG: v1.0.1-C1B-R3B certifies persistence-boundary normalization of
           BSON-naive UTC datetimes without weakening domain invariants.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from datetime import datetime, timezone, timedelta
import pytest

from tools.eos.saas.domain.wilsy_ai_usage_admission import WilsyAIUsageAdmission, WilsyAIUsageAdmissionError, WilsyAIUsageAdmissionState
from tools.eos.saas.billing.wilsy_ai_usage_admission_registry import _hydrate


def admission(key: str = "k", ident: str = "a", tenant: str = "tenant-a") -> WilsyAIUsageAdmission:
    now = datetime(2026, 9, 16, tzinfo=timezone.utc)
    return WilsyAIUsageAdmission(tenant, ident, key, "ent-a", "WILSY_AI_REASONING", 1, "a" * 128, now, now + timedelta(days=1), created_at=now, updated_at=now)


def test_identity_fingerprint_round_trip_and_replay_shape() -> None:
    item = admission()
    assert WilsyAIUsageAdmission.from_dict(item.to_dict()) == item
    assert len(item.fingerprint) == 128
    with pytest.raises(WilsyAIUsageAdmissionError):
        WilsyAIUsageAdmission.from_dict({**item.to_dict(), "reserved_request_units": 2})


def test_registry_hydrates_bson_naive_utc_datetimes_without_weakening_domain() -> None:
    item = admission()
    persisted = item.to_dict()
    for field in ("window_start", "window_end", "created_at", "updated_at"):
        value = persisted[field]
        assert isinstance(value, datetime)
        persisted[field] = value.replace(tzinfo=None)
    hydrated = _hydrate({**persisted, "command_fingerprint": "command", "_id": "row"})
    assert hydrated == item
    for field in ("window_start", "window_end", "created_at", "updated_at"):
        value = getattr(hydrated, field)
        assert value.tzinfo is timezone.utc
        assert value == getattr(item, field)

    aware = _hydrate({**item.to_dict(), "command_fingerprint": "command", "_id": "row"})
    assert aware == item
    with pytest.raises(WilsyAIUsageAdmissionError):
        WilsyAIUsageAdmission.from_dict({**item.to_dict(), "window_start": item.window_start.replace(tzinfo=None)})


def test_states_hold_capacity_and_reconciliation_is_not_usage() -> None:
    item = admission()
    assert item.updated_at is not None
    claimed = item.transition(WilsyAIUsageAdmissionState.CLAIMED, occurred_at=item.updated_at, evidence_reference="claim")
    assert claimed.updated_at is not None
    uncertain = claimed.transition(WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED, occurred_at=claimed.updated_at, evidence_reference="uncertain")
    assert uncertain.updated_at is not None
    released = uncertain.transition(WilsyAIUsageAdmissionState.RELEASED, occurred_at=uncertain.updated_at, evidence_reference="release")
    assert claimed.state is WilsyAIUsageAdmissionState.CLAIMED
    assert uncertain.state is WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED
    assert released.state is WilsyAIUsageAdmissionState.RELEASED
    with pytest.raises(WilsyAIUsageAdmissionError):
        item.transition(WilsyAIUsageAdmissionState.COMPLETED, occurred_at=item.updated_at, evidence_reference="bad")


def test_tenant_and_chronology_fail_closed() -> None:
    with pytest.raises(WilsyAIUsageAdmissionError): admission(tenant="default")
    item = admission()
    assert item.created_at is not None and item.updated_at is not None
    with pytest.raises(WilsyAIUsageAdmissionError):
        item.transition(WilsyAIUsageAdmissionState.RELEASED, occurred_at=item.created_at - timedelta(seconds=1), evidence_reference="release")


# ARTIFACT: test_wilsy_ai_usage_admission.py
# VERSION: v1.0.1-C1B-R3B
# END OF WILSY OS SOVEREIGN ARTIFACT
