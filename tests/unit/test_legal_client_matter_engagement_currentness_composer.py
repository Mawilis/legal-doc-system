"""Direct certificate for L9C11-P4 Engagement currentness composition.

TITLE: WILSY OS L9C11-P4 Engagement Currentness Composer Certificate
VERSION: v1.0.0-L9C11-P4-ENGAGEMENT-CURRENTNESS-COMPOSER-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove one caller-transaction-bound history read and unchanged
         delegation to the certified P3 Engagement currentness projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_engagement_currentness_composer.py
COLLABORATION / OWNERSHIP: Certificate for the L9C11-P4 pure composer only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P4 certificate covers session/transaction ownership,
           exact registry call shape, P3 state pass-through, corruption,
           ordering, future and multiplicity behavior, and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identities and fingerprints only.
TENANT BOUNDARY: Exact five-field lineage is asserted at the registry seam.
AUTHORITY BOUNDARY: Read-only composition; no current pointer or downstream authority.
FINANCIAL AUTHORITY BOUNDARY: No billing, payment, settlement or execution.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import inspect
from pathlib import Path
from typing import Any, cast, get_type_hints

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    LegalClientMatterEngagement,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement_currentness import (
    LegalClientMatterEngagementCurrentness,
    LegalClientMatterEngagementCurrentnessState,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_engagement_registry as engagement_registry,
)
from tools.eos.legal_operations.orchestration import (
    legal_client_matter_engagement_currentness_composer as composer_module,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_engagement_currentness_composer import (
    VERSION,
    LegalClientMatterEngagementCurrentnessComposer,
    LegalClientMatterEngagementCurrentnessComposerError,
    compose_currentness,
)


HEX = "a" * 128
WHEN = datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc)


class _Session:
    in_transaction = True


class _InactiveSession:
    in_transaction = False


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


def _composer() -> LegalClientMatterEngagementCurrentnessComposer:
    return LegalClientMatterEngagementCurrentnessComposer(
        engagement_collection=object()
    )


def _install_reader(monkeypatch: pytest.MonkeyPatch, history: object) -> list[tuple[tuple[object, ...], dict[str, object]]]:
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def reader(*args: object, **kwargs: object) -> object:
        calls.append((args, kwargs))
        return history

    monkeypatch.setattr(engagement_registry, "list_engagements_for_context", reader)
    return calls


def _compose(
    monkeypatch: pytest.MonkeyPatch,
    history: object,
    *,
    evaluated_at: datetime = WHEN + timedelta(hours=1),
    session: object | None = None,
) -> tuple[LegalClientMatterEngagementCurrentness, list[tuple[tuple[object, ...], dict[str, object]]]]:
    calls = _install_reader(monkeypatch, history)
    value = _composer().compose_currentness(
        "tenant-a",
        "matter-1",
        HEX,
        "party-1",
        HEX,
        evaluated_at,
        _Session() if session is None else session,
    )
    return value, calls


def test_version_and_callable_identity_are_explicit() -> None:
    assert VERSION == "v1.0.0-L9C11-P4-ENGAGEMENT-CURRENTNESS-COMPOSER"
    assert callable(compose_currentness)
    assert callable(LegalClientMatterEngagementCurrentnessComposer.compose_currentness)


def test_missing_and_inactive_sessions_are_rejected_before_registry_read(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _install_reader(monkeypatch, ())
    for session in (None, _InactiveSession()):
        with pytest.raises(LegalClientMatterEngagementCurrentnessComposerError) as error:
            _composer().compose_currentness("tenant-a", "matter-1", HEX, "party-1", HEX, WHEN, session)
        assert error.value.code == "L9C11_P4_ACTIVE_TRANSACTION_REQUIRED"
    assert calls == []


def test_active_session_is_required_and_collection_is_explicit() -> None:
    with pytest.raises(LegalClientMatterEngagementCurrentnessComposerError) as error:
        LegalClientMatterEngagementCurrentnessComposer(engagement_collection=None)
    assert error.value.code == "L9C11_P4_COLLECTION_REQUIRED"


def test_exactly_one_registry_read_and_exact_session_lineage_propagation(monkeypatch: pytest.MonkeyPatch) -> None:
    session = _Session()
    history = (_engagement(),)
    value, calls = _compose(monkeypatch, history, session=session)
    assert value.state is LegalClientMatterEngagementCurrentnessState.CURRENT
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[:5] == ("tenant-a", "matter-1", HEX, "party-1", HEX)
    assert kwargs == {"session": session}


def test_p3_receives_exact_history_and_evaluation_time(monkeypatch: pytest.MonkeyPatch) -> None:
    session = _Session()
    history = (_engagement(),)
    calls = _install_reader(monkeypatch, history)
    projection_calls: list[dict[str, object]] = []
    expected = object()

    def projection(**kwargs: object) -> object:
        projection_calls.append(kwargs)
        return expected

    monkeypatch.setattr(composer_module, "project_legal_client_matter_engagement_currentness", projection)
    result = _composer().compose_currentness("tenant-a", "matter-1", HEX, "party-1", HEX, WHEN, session)
    assert result is expected
    assert len(calls) == 1
    assert len(projection_calls) == 1
    assert projection_calls[0]["engagements"] is history
    assert projection_calls[0]["evaluated_at"] == WHEN
    assert projection_calls[0]["tenant_id"] == "tenant-a"
    assert projection_calls[0]["case_matter_id"] == "matter-1"


def test_empty_history_passes_through_to_no_engagement(monkeypatch: pytest.MonkeyPatch) -> None:
    value, _ = _compose(monkeypatch, ())
    assert value.state is LegalClientMatterEngagementCurrentnessState.NO_ENGAGEMENT


def test_future_only_history_passes_through_to_no_engagement(monkeypatch: pytest.MonkeyPatch) -> None:
    future = _engagement(effective_from=WHEN + timedelta(days=2))
    value, _ = _compose(monkeypatch, (future,), evaluated_at=WHEN + timedelta(days=1))
    assert value.state is LegalClientMatterEngagementCurrentnessState.NO_ENGAGEMENT


def test_single_eligible_history_is_current_with_exact_decisive_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    engagement = _engagement()
    value, _ = _compose(monkeypatch, (engagement,))
    assert value.state is LegalClientMatterEngagementCurrentnessState.CURRENT
    assert value.decisive_engagement_id == engagement.engagement_id
    assert value.decisive_engagement_fingerprint == engagement.fingerprint
    assert value.decisive_effective_from == engagement.effective_from


def test_exact_duplicate_history_remains_current_without_composer_normalization(monkeypatch: pytest.MonkeyPatch) -> None:
    engagement = _engagement()
    value, _ = _compose(monkeypatch, (engagement, engagement))
    assert value.state is LegalClientMatterEngagementCurrentnessState.CURRENT
    assert value.normalized_engagement_count == 1


def test_two_same_effective_distinct_rows_are_ambiguous(monkeypatch: pytest.MonkeyPatch) -> None:
    first = _engagement()
    second = _engagement(engagement_id="engagement-2", firm_decision_id="firm-decision-2", idempotency_key="idempotency:engagement-2")
    value, _ = _compose(monkeypatch, (first, second))
    assert value.state is LegalClientMatterEngagementCurrentnessState.AMBIGUOUS
    assert value.decisive_engagement_id is None


def test_later_distinct_eligible_row_is_ambiguous_not_latest_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    first = _engagement()
    later = _engagement(engagement_id="engagement-later", firm_decision_id="firm-decision-later", effective_from=WHEN + timedelta(hours=2), idempotency_key="idempotency:engagement-later")
    value, _ = _compose(monkeypatch, (later, first), evaluated_at=WHEN + timedelta(hours=3))
    assert value.state is LegalClientMatterEngagementCurrentnessState.AMBIGUOUS


def test_reversed_registry_history_has_identical_projection(monkeypatch: pytest.MonkeyPatch) -> None:
    first = _engagement()
    second = _engagement(engagement_id="engagement-2", firm_decision_id="firm-decision-2", idempotency_key="idempotency:engagement-2")
    forward, _ = _compose(monkeypatch, (first, second))
    reverse, _ = _compose(monkeypatch, (second, first))
    assert forward.to_dict() == reverse.to_dict()


def test_registry_hydration_error_fails_closed_without_no_engagement_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    def reader(*args: object, **kwargs: object) -> object:
        raise engagement_registry.LegalClientMatterEngagementRegistryPersistedRecordInvalidError("corrupt")

    monkeypatch.setattr(engagement_registry, "list_engagements_for_context", reader)
    with pytest.raises(LegalClientMatterEngagementCurrentnessComposerError) as error:
        _composer().compose_currentness("tenant-a", "matter-1", HEX, "party-1", HEX, WHEN, _Session())
    assert error.value.code == "L9C11_P4_HISTORY_READ_FAILED"


def test_p3_corrupt_blocked_state_passes_through(monkeypatch: pytest.MonkeyPatch) -> None:
    corrupt_candidate = _engagement(tenant_id="tenant-b")
    value, _ = _compose(monkeypatch, (corrupt_candidate,))
    assert value.state is LegalClientMatterEngagementCurrentnessState.CORRUPT_BLOCKED


def test_projection_failure_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_reader(monkeypatch, ())

    def projection(**kwargs: object) -> object:
        raise ValueError("raw projection detail")

    monkeypatch.setattr(composer_module, "project_legal_client_matter_engagement_currentness", projection)
    with pytest.raises(LegalClientMatterEngagementCurrentnessComposerError) as error:
        _composer().compose_currentness("tenant-a", "matter-1", HEX, "party-1", HEX, WHEN, _Session())
    assert error.value.code == "L9C11_P4_PROJECTION_FAILED"
    assert "raw projection detail" not in str(error.value)


def test_input_immutability_and_no_transaction_lifecycle(monkeypatch: pytest.MonkeyPatch) -> None:
    history = [_engagement()]
    session = _Session()
    before = tuple(history)
    value, _ = _compose(monkeypatch, tuple(history), session=session)
    assert tuple(history) == before
    assert value.state is LegalClientMatterEngagementCurrentnessState.CURRENT
    assert not hasattr(session, "start_transaction")
    assert not hasattr(session, "commit_transaction")
    assert not hasattr(session, "abort_transaction")


def test_static_authority_surface_excludes_selection_persistence_and_downstream_domains() -> None:
    source = Path(
        "/Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_engagement_currentness_composer.py"
    ).read_text(encoding="utf-8")
    assert "list_engagements_for_context" in source
    assert "max(" not in source
    assert "sorted(" not in source
    assert "MongoClient" not in source
    assert "pymongo" not in source
    assert "representation_authority" not in source
    assert "TODO" not in source and "FIXME" not in source
    assert "transaction.start" not in source
    assert "commit_transaction" not in source
    assert "abort_transaction" not in source


def test_public_surface_returns_the_certified_p3_type_and_has_no_transport_authority() -> None:
    annotations = get_type_hints(
        LegalClientMatterEngagementCurrentnessComposer.compose_currentness,
    )
    assert annotations["return"] is LegalClientMatterEngagementCurrentness
    source = inspect.getsource(LegalClientMatterEngagementCurrentnessComposer)
    assert "HTTP" not in source
    assert "Court" not in source
    assert "finance" not in source.lower()
