"""Direct certificate for L9C11-P3 Engagement currentness.

TITLE: WILSY OS L9C11-P3 Engagement Currentness Certificate
VERSION: v1.0.0-L9C11-P3-ENGAGEMENT-CURRENTNESS-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove deterministic currentness math over immutable Engagement
         history without inventing lifecycle or supersession authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_engagement_currentness.py
COLLABORATION / OWNERSHIP: Certificate for the L9C11-P3 pure domain only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P3 certificate covers vocabulary, exact lineage,
           future exclusion, duplicate normalization, multiplicity ambiguity,
           corruption precedence, order independence and SHA3-512 integrity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only.
TENANT BOUNDARY: Exact tenant, matter, party and subject lineage is asserted.
AUTHORITY BOUNDARY: Pure currentness projection; no registry or lifecycle.
FINANCIAL AUTHORITY BOUNDARY: No billing, payment, settlement or execution.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import inspect
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    LegalClientMatterEngagement,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement_currentness import (
    CURRENTNESS_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterEngagementCurrentness,
    LegalClientMatterEngagementCurrentnessError,
    LegalClientMatterEngagementCurrentnessState,
    project_legal_client_matter_engagement_currentness,
)


HEX = "a" * 128
WHEN = datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc)


def _engagement(**overrides: object) -> LegalClientMatterEngagement:
    values: dict[str, object] = {
        "engagement_id": "engagement-1",
        "tenant_id": "tenant-a",
        "case_matter_id": "matter-1",
        "matter_fingerprint": HEX,
        "client_party_id": "party-1",
        "subject_reference": "client:subject-1",
        "subject_identity_fingerprint": HEX,
        "acting_capacity_id": "capacity-1",
        "acting_capacity_fingerprint": HEX,
        "client_acceptance_id": "acceptance-1",
        "client_acceptance_fingerprint": HEX,
        "instrument_id": "instrument-1",
        "version": "v1",
        "instrument_fingerprint": HEX,
        "content_fingerprint": HEX,
        "mandate_id": "mandate-1",
        "mandate_scope": "scope:limited",
        "mandate_fingerprint": HEX,
        "conflict_disposition_id": "conflict-1",
        "conflict_disposition_fingerprint": HEX,
        "firm_decision_id": "firm-decision-1",
        "decision_actor_principal_id": "principal-firm-1",
        "firm_decision_fingerprint": HEX,
        "authorization_evidence_reference": "evidence:authorization-1",
        "authorization_evidence_fingerprint": HEX,
        "source_evidence_reference": "evidence:formation-1",
        "source_evidence_fingerprint": HEX,
        "effective_from": WHEN + timedelta(minutes=1),
        "idempotency_key": "idempotency:engagement-1",
    }
    values.update(overrides)
    return LegalClientMatterEngagement(**cast(Any, values))


def _project(
    history: list[LegalClientMatterEngagement],
    *,
    evaluated_at: object = WHEN + timedelta(hours=1),
    **scope: object,
) -> LegalClientMatterEngagementCurrentness:
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "case_matter_id": "matter-1",
        "matter_fingerprint": HEX,
        "client_party_id": "party-1",
        "subject_identity_fingerprint": HEX,
        "evaluated_at": evaluated_at,
        "engagements": history,
    }
    values.update(scope)
    return project_legal_client_matter_engagement_currentness(**cast(Any, values))


def test_schema_vocabulary_and_exactly_one_positive_state() -> None:
    assert set(LegalClientMatterEngagementCurrentnessState) == {
        LegalClientMatterEngagementCurrentnessState.NO_ENGAGEMENT,
        LegalClientMatterEngagementCurrentnessState.CURRENT,
        LegalClientMatterEngagementCurrentnessState.AMBIGUOUS,
        LegalClientMatterEngagementCurrentnessState.CORRUPT_BLOCKED,
    }
    assert list(LegalClientMatterEngagementCurrentnessState).count(
        LegalClientMatterEngagementCurrentnessState.CURRENT
    ) == 1
    value = _project([_engagement()])
    assert value.schema == SCHEMA
    assert value.currentness_version == VERSION
    assert value.is_current is True
    assert value.is_usable is True


def test_empty_history_is_no_engagement() -> None:
    value = _project([])
    assert value.state is LegalClientMatterEngagementCurrentnessState.NO_ENGAGEMENT
    assert value.is_current is False
    assert value.decisive_engagement_id is None
    assert value.normalized_engagement_count == 0
    assert value.eligible_engagement_count == 0


def test_single_eligible_engagement_is_current_and_decisive() -> None:
    engagement = _engagement()
    value = _project([engagement])
    assert value.state is LegalClientMatterEngagementCurrentnessState.CURRENT
    assert value.decisive_engagement_id == engagement.engagement_id
    assert value.decisive_engagement_fingerprint == engagement.fingerprint
    assert value.decisive_effective_from == engagement.effective_from
    assert value.candidate_engagement_ids == (engagement.engagement_id,)


def test_future_only_history_is_not_current() -> None:
    future = _engagement(effective_from=WHEN + timedelta(days=2))
    value = _project([future], evaluated_at=WHEN + timedelta(days=1))
    assert value.state is LegalClientMatterEngagementCurrentnessState.NO_ENGAGEMENT
    assert value.normalized_engagement_count == 1
    assert value.eligible_engagement_count == 0


def test_eligible_plus_future_excludes_future_without_ambiguity() -> None:
    eligible = _engagement()
    future = _engagement(
        engagement_id="engagement-future",
        effective_from=WHEN + timedelta(days=2),
        idempotency_key="idempotency:engagement-future",
    )
    value = _project([future, eligible])
    assert value.state is LegalClientMatterEngagementCurrentnessState.CURRENT
    assert value.decisive_engagement_id == "engagement-1"
    assert value.normalized_engagement_count == 2
    assert value.eligible_engagement_count == 1


def test_exact_duplicate_history_is_a_noop() -> None:
    engagement = _engagement()
    value = _project([engagement, engagement])
    assert value.state is LegalClientMatterEngagementCurrentnessState.CURRENT
    assert value.normalized_engagement_count == 1
    assert value.eligible_engagement_count == 1


@pytest.mark.parametrize(
    "field",
    ["tenant_id", "case_matter_id", "matter_fingerprint", "client_party_id", "subject_identity_fingerprint"],
)
def test_wrong_lineage_candidate_is_corrupt_blocked(field: str) -> None:
    candidate = _engagement(**{field: "tenant-b" if field in {"tenant_id", "case_matter_id", "client_party_id"} else "b" * 128})
    value = _project([candidate])
    assert value.state is LegalClientMatterEngagementCurrentnessState.CORRUPT_BLOCKED
    assert value.is_current is False
    assert value.corruption_evidence_fingerprints


def test_same_effective_distinct_candidates_are_ambiguous() -> None:
    first = _engagement()
    second = _engagement(
        engagement_id="engagement-2",
        firm_decision_id="firm-decision-2",
        idempotency_key="idempotency:engagement-2",
    )
    value = _project([second, first])
    assert value.state is LegalClientMatterEngagementCurrentnessState.AMBIGUOUS
    assert value.decisive_engagement_id is None
    assert value.eligible_engagement_count == 2
    assert set(value.candidate_engagement_ids) == {"engagement-1", "engagement-2"}


def test_later_distinct_engagement_does_not_supersede_earlier_without_contract() -> None:
    first = _engagement()
    later = _engagement(
        engagement_id="engagement-later",
        effective_from=WHEN + timedelta(hours=2),
        firm_decision_id="firm-decision-later",
        idempotency_key="idempotency:engagement-later",
    )
    value = _project([first, later], evaluated_at=WHEN + timedelta(hours=3))
    assert value.state is LegalClientMatterEngagementCurrentnessState.AMBIGUOUS
    assert value.is_current is False


def test_history_order_does_not_change_projection() -> None:
    first = _engagement()
    second = _engagement(
        engagement_id="engagement-2",
        firm_decision_id="firm-decision-2",
        idempotency_key="idempotency:engagement-2",
    )
    assert _project([first, second]).to_dict() == _project([second, first]).to_dict()


def test_duplicate_id_with_divergent_payload_is_corrupt() -> None:
    first = _engagement()
    divergent = _engagement(
        engagement_id=first.engagement_id,
        firm_decision_id="firm-decision-divergent",
        idempotency_key="idempotency:engagement-divergent",
    )
    value = _project([first, divergent])
    assert value.state is LegalClientMatterEngagementCurrentnessState.CORRUPT_BLOCKED


def test_duplicate_fingerprint_with_divergent_payload_is_corrupt() -> None:
    first = _engagement()
    divergent = _engagement(
        engagement_id="engagement-divergent",
        firm_decision_id="firm-decision-divergent",
        idempotency_key="idempotency:engagement-divergent",
    )
    object.__setattr__(divergent, "fingerprint", first.fingerprint)
    value = _project([first, divergent])
    assert value.state is LegalClientMatterEngagementCurrentnessState.CORRUPT_BLOCKED


def test_malformed_candidate_is_corrupt_blocked() -> None:
    malformed = object.__new__(LegalClientMatterEngagement)
    object.__setattr__(malformed, "engagement_id", "bad")
    value = _project([cast(Any, malformed)])
    assert value.state is LegalClientMatterEngagementCurrentnessState.CORRUPT_BLOCKED


def test_naive_evaluation_time_is_rejected_without_a_hidden_clock() -> None:
    with pytest.raises(LegalClientMatterEngagementCurrentnessError):
        _project([_engagement()], evaluated_at=datetime(2026, 9, 28, 9, 0))


def test_repeatability_and_strict_round_trip_are_deterministic() -> None:
    value = _project([_engagement()])
    repeat = _project([_engagement()])
    assert value.to_dict() == repeat.to_dict()
    assert len(value.fingerprint) == 128
    assert LegalClientMatterEngagementCurrentness.from_dict(value.to_dict()) == value
    tampered = value.to_dict()
    tampered["state"] = "AMBIGUOUS"
    with pytest.raises(LegalClientMatterEngagementCurrentnessError):
        LegalClientMatterEngagementCurrentness.from_dict(tampered)


def test_projection_is_immutable_and_has_no_current_pointer_or_lifecycle() -> None:
    value = _project([_engagement()])
    assert set(value.to_dict()) == set(CURRENTNESS_FIELDS)
    with pytest.raises(FrozenInstanceError):
        value.state = "NO_ENGAGEMENT"  # type: ignore[misc]
    source = Path(
        "/Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_engagement_currentness.py"
    ).read_text(encoding="utf-8")
    assert "datetime.now" not in source
    assert "MongoClient" not in source
    assert "pymongo" not in source
    assert "TODO" not in source and "FIXME" not in source
    assert "Representation" in source and "formation" in source
    assert "current pointer" in source


def test_currentness_does_not_form_representation_court_or_finance_authority() -> None:
    source = inspect.getsource(LegalClientMatterEngagementCurrentness)
    assert "Representation" in source
    assert "Court" not in source
    assert "finance" not in source.lower()
