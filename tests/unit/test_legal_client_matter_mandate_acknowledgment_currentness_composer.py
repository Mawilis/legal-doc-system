"""Direct certificate for the L9B10-P3 acknowledgment currentness composer.

TITLE: WILSY OS Legal Client Matter Mandate Acknowledgment Currentness Composer Certificate
VERSION: v1.0.0-L9B10-P3-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS-COMPOSER-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove caller-owned transaction reads, exact lineage correlation,
         effective-time decision selection, conflict blocking and zero writes.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_acknowledgment_currentness_composer.py
COLLABORATION / OWNERSHIP: Synthetic direct certificate; registries and the
                            immutable projection remain canonical authorities.
CERTIFICATION / UPDATE DATE: 2026-09-27
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TRANSACTION BOUNDARY: Recording registry fakes only; no Mongo or network.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    LegalClientMatterMandateAcknowledgment,
    LegalClientMatterMandateAcknowledgmentDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment_currentness import (
    LegalClientMatterMandateAcknowledgmentCurrentnessState,
)
from tools.eos.legal_operations.orchestration import (
    legal_client_matter_mandate_acknowledgment_currentness_composer as composer_module,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_acknowledgment_currentness_composer import (
    LegalClientMatterMandateAcknowledgmentCurrentnessComposer,
    LegalClientMatterMandateAcknowledgmentCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_mandate_acknowledgment_registry as acknowledgment_registry,
    legal_client_matter_mandate_grant_registry as grant_registry,
)
from tests.unit.test_legal_client_matter_mandate_grant import grant


BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9b4"
GRANT_ID = "client-grant-l9b10"


class RecordingSession:
    """Minimal active caller transaction with no lifecycle methods."""

    in_transaction = True


def acknowledgment(
    source: Any,
    *,
    decision: LegalClientMatterMandateAcknowledgmentDecision,
    acknowledgment_id: str,
    effective_from: datetime,
    occurred_at: datetime | None = None,
) -> LegalClientMatterMandateAcknowledgment:
    """Create synthetic acknowledgment evidence for one exact grant."""
    return LegalClientMatterMandateAcknowledgment.from_client_grant(
        client_grant=source,
        acknowledgment_id=acknowledgment_id,
        decision=decision,
        decision_actor_principal_id="principal-l9b10",
        authorization_evidence_reference="auth:l9b10",
        authorization_evidence_fingerprint="a" * 128,
        source_evidence_reference="source:l9b10",
        source_evidence_fingerprint="b" * 128,
        occurred_at=occurred_at or effective_from,
        effective_from=effective_from,
        idempotency_key=f"idem:{acknowledgment_id}",
    )


def install_sources(
    monkeypatch: pytest.MonkeyPatch,
    *,
    source: Any,
    history: tuple[Any, ...] = (),
    sessions: list[Any] | None = None,
    grant_error: BaseException | None = None,
    history_error: BaseException | None = None,
) -> None:
    """Install recording grant/history seams and preserve the exact session."""
    observed = sessions if sessions is not None else []

    def read_grant(tenant_id: str, grant_id: str, collection: Any, *, session: Any) -> Any:
        observed.append(session)
        if grant_error is not None:
            raise grant_error
        return source

    def read_history(
        tenant_id: str,
        grant_id: str,
        collection: Any,
        *,
        session: Any,
        limit: int = 500,
    ) -> tuple[Any, ...]:
        observed.append(session)
        if history_error is not None:
            raise history_error
        return history

    monkeypatch.setattr(grant_registry, "get_grant", read_grant)
    monkeypatch.setattr(
        acknowledgment_registry,
        "list_acknowledgments_for_grant",
        read_history,
    )


def build_composer() -> LegalClientMatterMandateAcknowledgmentCurrentnessComposer:
    """Use isolated collection sentinels; monkeypatched seams prevent Mongo."""
    return LegalClientMatterMandateAcknowledgmentCurrentnessComposer(
        grant_collection=object(), acknowledgment_collection=object()
    )


def compose(
    composer: LegalClientMatterMandateAcknowledgmentCurrentnessComposer,
    session: Any,
    *,
    at: datetime = BASE + timedelta(hours=3),
    source: Any | None = None,
    history: tuple[Any, ...] = (),
    monkeypatch: pytest.MonkeyPatch | None = None,
) -> Any:
    """Call the public composition boundary after installing synthetic sources."""
    if monkeypatch is not None:
        install_sources(monkeypatch, source=source or grant(), history=history)
    return composer.compose_currentness(TENANT, GRANT_ID, at, session)


def expect_code(code: str, operation: Any) -> None:
    """Assert one stable fail-closed code without exposing evidence."""
    with pytest.raises(LegalClientMatterMandateAcknowledgmentCurrentnessComposerError) as raised:
        operation()
    assert raised.value.code == code
    assert str(raised.value) == code


def test_missing_or_inactive_session_rejected_before_any_read(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: list[Any] = []
    install_sources(monkeypatch, source=grant(), sessions=observed)
    value = build_composer()
    expect_code(
        "L9B10_P3_ACTIVE_TRANSACTION_REQUIRED",
        lambda: value.compose_currentness(TENANT, GRANT_ID, BASE, None),
    )
    expect_code(
        "L9B10_P3_ACTIVE_TRANSACTION_REQUIRED",
        lambda: value.compose_currentness(TENANT, GRANT_ID, BASE, type("S", (), {"in_transaction": False})()),
    )
    assert observed == []


def test_no_history_and_future_only_history_return_no_decision(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant(client_grant_id=GRANT_ID)
    future = acknowledgment(
        source,
        decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED,
        acknowledgment_id="future",
        effective_from=BASE + timedelta(days=1),
    )
    for history in ((), (future,)):
        install_sources(monkeypatch, source=source, history=history)
        result = build_composer().compose_currentness(TENANT, GRANT_ID, BASE, RecordingSession())
        assert result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.NO_DECISION
        assert result.decisive_acknowledgment_ids == ()


@pytest.mark.parametrize(
    ("decision", "state"),
    [
        (LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED),
        (LegalClientMatterMandateAcknowledgmentDecision.DECLINED, LegalClientMatterMandateAcknowledgmentCurrentnessState.DECLINED),
        (LegalClientMatterMandateAcknowledgmentDecision.REQUIRES_REVIEW, LegalClientMatterMandateAcknowledgmentCurrentnessState.REQUIRES_REVIEW),
    ],
)
def test_single_decisions_map_to_published_states(monkeypatch: pytest.MonkeyPatch, decision: Any, state: Any) -> None:
    source = grant(client_grant_id=GRANT_ID)
    value = acknowledgment(source, decision=decision, acknowledgment_id="single", effective_from=BASE)
    install_sources(monkeypatch, source=source, history=(value,))
    result = build_composer().compose_currentness(TENANT, GRANT_ID, BASE, RecordingSession())
    assert result.state is state
    assert result.is_acknowledged is (state is LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED)


def test_later_effective_decision_supersedes_earlier(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant(client_grant_id=GRANT_ID)
    earlier = acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.DECLINED, acknowledgment_id="earlier", effective_from=BASE)
    later = acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, acknowledgment_id="later", effective_from=BASE + timedelta(hours=1))
    install_sources(monkeypatch, source=source, history=(later, earlier))
    result = build_composer().compose_currentness(TENANT, GRANT_ID, BASE + timedelta(hours=2), RecordingSession())
    assert result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED
    assert result.decisive_acknowledgment_ids == ("later",)


def test_later_declined_and_review_are_current(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant(client_grant_id=GRANT_ID)
    earlier = acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, acknowledgment_id="earlier", effective_from=BASE)
    for decision, expected in (
        (LegalClientMatterMandateAcknowledgmentDecision.DECLINED, LegalClientMatterMandateAcknowledgmentCurrentnessState.DECLINED),
        (LegalClientMatterMandateAcknowledgmentDecision.REQUIRES_REVIEW, LegalClientMatterMandateAcknowledgmentCurrentnessState.REQUIRES_REVIEW),
    ):
        later = acknowledgment(source, decision=decision, acknowledgment_id=f"later-{decision.value}", effective_from=BASE + timedelta(hours=1))
        install_sources(monkeypatch, source=source, history=(earlier, later))
        result = build_composer().compose_currentness(TENANT, GRANT_ID, BASE + timedelta(hours=2), RecordingSession())
        assert result.state is expected


@pytest.mark.parametrize(
    "decision",
    [
        LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED,
        LegalClientMatterMandateAcknowledgmentDecision.DECLINED,
        LegalClientMatterMandateAcknowledgmentDecision.REQUIRES_REVIEW,
    ],
)
def test_same_effective_identical_decisions_are_not_ambiguous(monkeypatch: pytest.MonkeyPatch, decision: Any) -> None:
    source = grant(client_grant_id=GRANT_ID)
    first = acknowledgment(source, decision=decision, acknowledgment_id="first", effective_from=BASE)
    second = acknowledgment(source, decision=decision, acknowledgment_id="second", effective_from=BASE, occurred_at=BASE - timedelta(seconds=1))
    install_sources(monkeypatch, source=source, history=(second, first))
    result = build_composer().compose_currentness(TENANT, GRANT_ID, BASE + timedelta(hours=1), RecordingSession())
    assert result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState(decision.value)
    assert set(result.decisive_acknowledgment_ids) == {"first", "second"}


@pytest.mark.parametrize(
    "decisions",
    [
        (LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, LegalClientMatterMandateAcknowledgmentDecision.DECLINED),
        (LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, LegalClientMatterMandateAcknowledgmentDecision.REQUIRES_REVIEW),
        (LegalClientMatterMandateAcknowledgmentDecision.DECLINED, LegalClientMatterMandateAcknowledgmentDecision.REQUIRES_REVIEW),
        (LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, LegalClientMatterMandateAcknowledgmentDecision.DECLINED, LegalClientMatterMandateAcknowledgmentDecision.REQUIRES_REVIEW),
    ],
)
def test_same_effective_conflicts_are_ambiguous(monkeypatch: pytest.MonkeyPatch, decisions: tuple[Any, ...]) -> None:
    source = grant(client_grant_id=GRANT_ID)
    history = tuple(acknowledgment(source, decision=decision, acknowledgment_id=f"decision-{index}", effective_from=BASE) for index, decision in enumerate(decisions))
    install_sources(monkeypatch, source=source, history=tuple(reversed(history)))
    result = build_composer().compose_currentness(TENANT, GRANT_ID, BASE, RecordingSession())
    assert result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.AMBIGUOUS
    assert set(result.decisive_decisions) == {decision.value for decision in decisions}


def test_insertion_order_fingerprint_order_and_occurred_at_do_not_grant_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant(client_grant_id=GRANT_ID)
    declined = acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.DECLINED, acknowledgment_id="z-last", effective_from=BASE, occurred_at=BASE - timedelta(days=1))
    acknowledged = acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, acknowledgment_id="a-first", effective_from=BASE, occurred_at=BASE - timedelta(days=2))
    install_sources(monkeypatch, source=source, history=(declined, acknowledged))
    first = build_composer().compose_currentness(TENANT, GRANT_ID, BASE, RecordingSession())
    install_sources(monkeypatch, source=source, history=(acknowledged, declined))
    second = build_composer().compose_currentness(TENANT, GRANT_ID, BASE, RecordingSession())
    assert first.state is second.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.AMBIGUOUS


def test_future_conflict_is_excluded(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant(client_grant_id=GRANT_ID)
    current = acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, acknowledgment_id="current", effective_from=BASE)
    future = acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.DECLINED, acknowledgment_id="future", effective_from=BASE + timedelta(days=1))
    install_sources(monkeypatch, source=source, history=(future, current))
    result = build_composer().compose_currentness(TENANT, GRANT_ID, BASE, RecordingSession())
    assert result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED
    assert result.acknowledgment_evidence_fingerprints == (current.fingerprint,)


def test_correlated_history_mismatch_returns_corrupt_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant(client_grant_id=GRANT_ID)
    other = grant(client_grant_id="other-grant")
    invalid = acknowledgment(other, decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, acknowledgment_id="wrong-lineage", effective_from=BASE)
    install_sources(monkeypatch, source=source, history=(invalid,))
    result = build_composer().compose_currentness(TENANT, GRANT_ID, BASE, RecordingSession())
    assert result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.CORRUPT_BLOCKED
    assert result.is_usable is False


def test_tenant_mismatch_is_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant(client_grant_id=GRANT_ID)
    invalid = acknowledgment(
        source,
        decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED,
        acknowledgment_id="wrong-tenant",
        effective_from=BASE,
    )
    object.__setattr__(invalid, "tenant_id", "tenant-other")
    install_sources(monkeypatch, source=source, history=(invalid,))
    result = build_composer().compose_currentness(TENANT, GRANT_ID, BASE, RecordingSession())
    assert result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.CORRUPT_BLOCKED
    assert result.is_usable is False


def test_malformed_registry_error_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant(client_grant_id=GRANT_ID)
    install_sources(
        monkeypatch,
        source=source,
        history_error=acknowledgment_registry.LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError("bad"),
    )
    expect_code(
        "L9B10_P3_ACKNOWLEDGMENT_HISTORY_READ_FAILED",
        lambda: build_composer().compose_currentness(TENANT, GRANT_ID, BASE, RecordingSession()),
    )


def test_aware_time_required_and_exact_session_propagated(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant(client_grant_id=GRANT_ID)
    sessions: list[Any] = []
    install_sources(monkeypatch, source=source, history=(), sessions=sessions)
    transaction = RecordingSession()
    result = build_composer().compose_currentness(TENANT, GRANT_ID, BASE, transaction)
    assert result.evaluation_time == BASE
    assert sessions == [transaction, transaction]
    expect_code(
        "L9B10_P3_EVALUATION_TIME_INVALID",
        lambda: build_composer().compose_currentness(TENANT, GRANT_ID, BASE.replace(tzinfo=None), transaction),
    )


def test_transaction_remains_caller_owned_and_no_downstream_reads_or_writes(monkeypatch: pytest.MonkeyPatch) -> None:
    source = grant(client_grant_id=GRANT_ID)
    install_sources(monkeypatch, source=source, history=())
    transaction = RecordingSession()
    result = build_composer().compose_currentness(TENANT, GRANT_ID, BASE, transaction)
    assert result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.NO_DECISION
    assert not hasattr(transaction, "start_transaction")
    assert not hasattr(transaction, "commit_transaction")
    assert not hasattr(transaction, "abort_transaction")


def test_projection_is_deterministic_and_composer_has_no_forbidden_authorities() -> None:
    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_mandate_acknowledgment_currentness_composer.py").read_text()
    tree = ast.parse(source)
    imported = {node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)}
    imported.update(node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    assert not any(name.startswith(("pymongo", "motor", "httpx", "requests")) for name in imported)
    assert "legal_client_matter_mandate_grant_currentness_composer" not in source
    assert "LegalClientMatterMandate" in source
    assert "TODO" not in source
    assert "FIXME" not in source


def test_certificate_and_production_artifact_have_sovereign_markers() -> None:
    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_mandate_acknowledgment_currentness_composer.py").read_text()
    assert "VERSION: v1.0.0-L9B10-P3-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS-COMPOSER" in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source


# END OF WILSY OS SOVEREIGN TEST CERTIFICATE
