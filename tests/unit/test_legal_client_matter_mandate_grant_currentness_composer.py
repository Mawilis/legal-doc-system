"""Direct certificate for the read-only L9B9-P2 currentness composer.

TITLE: WILSY OS Legal Client Matter Mandate Grant Currentness Composer Certificate
VERSION: v1.0.0-L9B9-P2-CLIENT-MANDATE-GRANT-CURRENTNESS-COMPOSER-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove caller-owned transaction composition, consistent-session reads,
         formation windows, lifecycle terminal ambiguity, CaseMatter gating,
         strict corruption handling, and zero persistence of projections.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_grant_currentness_composer.py
COLLABORATION / OWNERSHIP: Synthetic direct certificate for L9B9-P2 only;
                            registries and the projection domain remain their
                            separate canonical authorities.
CERTIFICATION / UPDATE DATE: 2026-09-27
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TRANSACTION BOUNDARY: Recording fakes only; no Mongo or network.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant import (
    LegalClientMatterMandateGrant,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_currentness import (
    LegalClientMatterMandateGrantCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_lifecycle import (
    LegalClientMatterMandateGrantLifecycleEvent,
    LegalClientMatterMandateGrantLifecycleReason,
    record_legal_client_matter_mandate_grant_lifecycle,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatterState,
)
from tools.eos.legal_operations.orchestration import (
    legal_client_matter_mandate_grant_currentness_composer as composer_module,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_grant_currentness_composer import (
    LegalClientMatterMandateGrantCurrentnessComposer,
    LegalClientMatterMandateGrantCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_mandate_grant_lifecycle_registry as lifecycle_registry,
    legal_client_matter_mandate_grant_registry as grant_registry,
)
from tests.unit.test_legal_client_matter_mandate_grant import grant, matter


BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9b4"


class RecordingSession:
    """Minimal active caller transaction with no transaction lifecycle methods."""

    in_transaction = True


def lifecycle_event(
    source: LegalClientMatterMandateGrant,
    *,
    event: LegalClientMatterMandateGrantLifecycleEvent,
    event_id: str,
    effective_from: datetime,
    successor: LegalClientMatterMandateGrant | None = None,
) -> Any:
    """Create exact synthetic lifecycle evidence for one source grant."""
    return record_legal_client_matter_mandate_grant_lifecycle(
        client_grant=source,
        lifecycle_event_id=event_id,
        event=event,
        decision_actor_principal_id="principal-l9b9",
        authorization_evidence_reference="auth:l9b9",
        authorization_evidence_fingerprint="b" * 128,
        source_evidence_reference="source:l9b9",
        source_evidence_fingerprint="c" * 128,
        occurred_at=effective_from,
        effective_from=effective_from,
        idempotency_key=f"idem:{event_id}",
        reason=(
            LegalClientMatterMandateGrantLifecycleReason.CLIENT_WITHDRAWAL
            if event is LegalClientMatterMandateGrantLifecycleEvent.REVOKED
            else None
        ),
        successor_grant=successor,
    )


def install_sources(
    monkeypatch: pytest.MonkeyPatch,
    *,
    source: LegalClientMatterMandateGrant | None,
    events: tuple[Any, ...] = (),
    matter_value: Any | None = None,
    sessions: list[Any] | None = None,
) -> None:
    """Install recording registry seams; all reads receive the same session."""
    observed = sessions if sessions is not None else []

    def read_grant(tenant_id: str, grant_id: str, collection: Any, *, session: Any) -> Any:
        observed.append(session)
        if source is None:
            raise grant_registry.LegalClientMatterMandateGrantRegistryNotFoundError(
                "L9B7_GRANT_NOT_FOUND"
            )
        return source

    def read_events(
        tenant_id: str, grant_id: str, collection: Any, *, session: Any
    ) -> tuple[Any, ...]:
        observed.append(session)
        return events

    def read_matter(
        tenant_id: str, entity_type: str, entity_identity: str, collection: Any, *, session: Any
    ) -> tuple[Any, ...]:
        observed.append(session)
        return () if matter_value is None else (matter_value,)

    monkeypatch.setattr(grant_registry, "get_grant", read_grant)
    monkeypatch.setattr(lifecycle_registry, "list_events_for_grant", read_events)
    monkeypatch.setattr(
        composer_module.matter_registry.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        staticmethod(read_matter),
    )


def build_composer() -> LegalClientMatterMandateGrantCurrentnessComposer:
    """Use isolated sentinels; monkeypatched seams prevent database access."""
    return LegalClientMatterMandateGrantCurrentnessComposer(
        grant_collection=object(),
        lifecycle_collection=object(),
        matter_lifecycle_collection=object(),
    )


def compose(
    composer: LegalClientMatterMandateGrantCurrentnessComposer,
    session: Any,
    *,
    at: datetime = BASE + timedelta(hours=3),
    grant_id: str = "client-grant-l9b4",
) -> Any:
    """Call the public four-input composition boundary."""
    return composer.compose_currentness(TENANT, grant_id, at, session)


def expect_code(code: str, operation: Any) -> None:
    """Assert one stable composer error without exposing input values."""
    with pytest.raises(LegalClientMatterMandateGrantCurrentnessComposerError) as raised:
        operation()
    assert raised.value.code == code
    assert str(raised.value) == code


def test_missing_or_inactive_transaction_rejected_before_any_read(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: list[Any] = []
    install_sources(monkeypatch, source=grant(), sessions=observed)
    value = build_composer()
    expect_code("L9B9_P2_ACTIVE_TRANSACTION_REQUIRED", lambda: compose(value, None))
    expect_code("L9B9_P2_ACTIVE_TRANSACTION_REQUIRED", lambda: compose(value, type("S", (), {"in_transaction": False})()))
    assert observed == []


def test_absent_formation_is_truthful_and_does_not_read_other_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: list[Any] = []
    install_sources(monkeypatch, source=None, sessions=observed)
    value = compose(build_composer(), RecordingSession())
    assert value.state is LegalClientMatterMandateGrantCurrentnessState.FORMATION_ABSENT
    assert value.client_grant_fingerprint is None
    assert value.case_matter_id is None and value.client_party_id is None
    assert len(observed) == 1


def test_formation_window_is_resolved_before_lifecycle_or_matter_reads(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant()
    observed: list[Any] = []
    install_sources(monkeypatch, source=source, sessions=observed)
    before = compose(build_composer(), RecordingSession(), at=source.effective_from - timedelta(microseconds=1))
    assert before.state is LegalClientMatterMandateGrantCurrentnessState.NOT_YET_EFFECTIVE
    assert len(observed) == 1
    observed.clear()
    at_end = compose(build_composer(), RecordingSession(), at=source.effective_until)  # type: ignore[arg-type]
    assert at_end.state is LegalClientMatterMandateGrantCurrentnessState.EXPIRED
    observed.clear()
    after = compose(build_composer(), RecordingSession(), at=source.effective_until + timedelta(days=1))  # type: ignore[operator]
    assert after.state is LegalClientMatterMandateGrantCurrentnessState.EXPIRED
    assert len(observed) == 1


def test_open_matter_without_invalidator_is_current_and_uses_one_session(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant()
    sessions: list[Any] = []
    install_sources(monkeypatch, source=source, matter_value=matter(), sessions=sessions)
    transaction = RecordingSession()
    value = compose(build_composer(), transaction)
    assert value.state is LegalClientMatterMandateGrantCurrentnessState.CURRENT
    assert value.is_usable is True
    assert sessions and all(item is transaction for item in sessions)
    assert transaction.in_transaction is True


def test_future_lifecycle_is_excluded_and_terminal_events_are_projected(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant()
    future = lifecycle_event(
        source,
        event=LegalClientMatterMandateGrantLifecycleEvent.REVOKED,
        event_id="future",
        effective_from=BASE + timedelta(days=2),
    )
    install_sources(monkeypatch, source=source, events=(future,), matter_value=matter())
    value = compose(build_composer(), RecordingSession())
    assert value.state is LegalClientMatterMandateGrantCurrentnessState.CURRENT
    revoked = lifecycle_event(
        source,
        event=LegalClientMatterMandateGrantLifecycleEvent.REVOKED,
        event_id="revoked",
        effective_from=BASE + timedelta(hours=3),
    )
    install_sources(monkeypatch, source=source, events=(future, revoked), matter_value=matter())
    value = compose(build_composer(), RecordingSession())
    assert value.state is LegalClientMatterMandateGrantCurrentnessState.REVOKED

    successor = grant(
        client_grant_id="client-grant-l9b4-successor",
        occurred_at=BASE + timedelta(hours=3),
        effective_from=BASE + timedelta(hours=3),
        idempotency_key="successor-idem-l9b9",
    )
    superseded = lifecycle_event(
        source,
        event=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED,
        event_id="superseded",
        effective_from=BASE + timedelta(hours=3),
        successor=successor,
    )
    install_sources(monkeypatch, source=source, events=(superseded,), matter_value=matter())
    value = compose(build_composer(), RecordingSession())
    assert value.state is LegalClientMatterMandateGrantCurrentnessState.SUPERSEDED
    assert value.successor_client_grant_id == successor.client_grant_id
    assert value.is_current is False


def test_conflicting_terminal_history_is_ambiguous_without_ordering_tiebreak(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant()
    revoked = lifecycle_event(
        source,
        event=LegalClientMatterMandateGrantLifecycleEvent.REVOKED,
        event_id="revoked-conflict",
        effective_from=BASE + timedelta(hours=3),
    )
    successor_a = grant(client_grant_id="successor-a", idempotency_key="successor-a-idem")
    successor_b = grant(client_grant_id="successor-b", idempotency_key="successor-b-idem")
    superseded_a = lifecycle_event(
        source,
        event=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED,
        event_id="superseded-a",
        effective_from=BASE + timedelta(hours=3),
        successor=successor_a,
    )
    superseded_b = lifecycle_event(
        source,
        event=LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED,
        event_id="superseded-b",
        effective_from=BASE + timedelta(hours=3),
        successor=successor_b,
    )
    for events in ((superseded_a, superseded_b), (revoked, superseded_a)):
        install_sources(monkeypatch, source=source, events=tuple(reversed(events)), matter_value=matter())
        value = compose(build_composer(), RecordingSession())
        assert value.state is LegalClientMatterMandateGrantCurrentnessState.AMBIGUOUS
        assert len(value.decisive_lifecycle_evidence_fingerprints) == 2
        assert value.successor_client_grant_id is None


def test_closed_missing_or_mismatched_matter_is_not_current(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant()
    closed = matter().transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="matter-closed:l9b9",
        occurred_at=BASE + timedelta(days=1),
    )
    install_sources(monkeypatch, source=source, matter_value=closed)
    value = compose(build_composer(), RecordingSession())
    assert value.state is LegalClientMatterMandateGrantCurrentnessState.MATTER_CLOSED
    install_sources(monkeypatch, source=source, matter_value=None)
    value = compose(build_composer(), RecordingSession())
    assert value.state is LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED
    foreign = matter(tenant_id="tenant-other")
    install_sources(monkeypatch, source=source, matter_value=foreign)
    value = compose(build_composer(), RecordingSession())
    assert value.state is LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED


def test_scope_and_lifecycle_corruption_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant()
    foreign = grant(client_grant_id="foreign-grant")
    install_sources(monkeypatch, source=foreign, matter_value=matter())
    value = compose(build_composer(), RecordingSession())
    assert value.state is LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED
    revoked = lifecycle_event(
        source,
        event=LegalClientMatterMandateGrantLifecycleEvent.REVOKED,
        event_id="bad-correlation",
        effective_from=BASE + timedelta(hours=3),
    )
    object.__setattr__(revoked, "client_grant_fingerprint", "d" * 128)
    install_sources(monkeypatch, source=source, events=(revoked,), matter_value=matter())
    value = compose(build_composer(), RecordingSession())
    assert value.state is LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED


def test_invalid_time_is_rejected_and_fingerprints_are_exact_replays(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant()
    install_sources(monkeypatch, source=source, matter_value=matter())
    value = build_composer()
    expect_code("L9B9_P2_EVALUATION_TIME_INVALID", lambda: compose(value, RecordingSession(), at=BASE.replace(tzinfo=None)))
    first = compose(value, RecordingSession())
    second = compose(value, RecordingSession())
    assert first.fingerprint == second.fingerprint


def test_no_capacity_acknowledgment_mandate_or_engagement_authority_is_imported() -> None:
    path = Path("tools/eos/legal_operations/orchestration/legal_client_matter_mandate_grant_currentness_composer.py")
    tree = ast.parse(path.read_text())
    imports = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not any(
        token in module
        for module in imports
        for token in ("acting_capacity", "acknowledgment", "mandate_registry", "engagement", "fastapi", "pymongo")
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"insert_one", "update_one", "delete_one", "delete_many", "create_index"}
        for node in ast.walk(tree)
    )


# ARTIFACT: test_legal_client_matter_mandate_grant_currentness_composer.py
# VERSION: v1.0.0-L9B9-P2-CLIENT-MANDATE-GRANT-CURRENTNESS-COMPOSER-CERT
# RESULT: bounded synthetic unit certificate only; no Mongo writes
# END OF WILSY OS SOVEREIGN ARTIFACT
