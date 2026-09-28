"""Direct certificate for the L9C9-P4 currentness composer.

TITLE: WILSY OS Legal Client Matter Engagement Firm Decision Currentness Composer Certificate
VERSION: v1.0.0-L9C9-P4-ENGAGEMENT-FIRM-DECISION-CURRENTNESS-COMPOSER-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify one exact registry history read, caller-session propagation,
         explicit-time propagation and unchanged P3 delegation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_engagement_firm_decision_currentness_composer.py
COLLABORATION / OWNERSHIP: The P1 registry and P3 pure projection remain the
                            only authorities exercised by this certificate.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C9-P4-ENGAGEMENT-FIRM-DECISION-CURRENTNESS-COMPOSER-CERT
           proves caller transactions, exact scope, one read, pass-through
           semantics, fail-closed mapping and forbidden-authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TRANSACTION BOUNDARY: Recording fakes only; no Mongo or network access.
FAIL-CLOSED DECLARATION: Missing/inactive transactions, registry failures and
                         projection failures never become a currentness result.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision import (
    LegalClientMatterEngagementFirmDecision,
    LegalClientMatterEngagementFirmDecisionType,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision_currentness import (
    LegalClientMatterEngagementFirmDecisionCurrentnessState,
    project_legal_client_matter_engagement_firm_decision_currentness,
)
from tools.eos.legal_operations.orchestration import (
    legal_client_matter_engagement_firm_decision_currentness_composer as composer_module,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_engagement_firm_decision_currentness_composer import (
    VERSION,
    LegalClientMatterEngagementFirmDecisionCurrentnessComposer,
    LegalClientMatterEngagementFirmDecisionCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_engagement_firm_decision_registry as decision_registry,
)


BASE = datetime(2026, 9, 28, 10, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9c9-p4"
MATTER = "matter-l9c9-p4"
PARTY = "party-l9c9-p4"
SUBJECT_FP = "b" * 128


SOURCE_MATTER = CaseMatter(
    tenant_id=TENANT,
    case_matter_id=MATTER,
    matter_reference="CASE-L9C9-P4",
    opened_at=BASE,
    evidence_reference="matter:l9c9:p4",
)
SOURCE_PARTY = register_legal_matter_party(
    matter=SOURCE_MATTER,
    party_id=PARTY,
    party_kind=LegalMatterPartyKind.ORGANIZATION,
    party_side=LegalMatterPartySide.CLIENT_SIDE,
    matter_role=LegalMatterPartyRole.CLIENT,
    subject_reference="client:subject-l9c9-p4",
    subject_identity_fingerprint=SUBJECT_FP,
    display_name="Synthetic client presentation",
    registered_at=BASE + timedelta(minutes=1),
    source_evidence_reference="party:l9c9:p4",
    source_evidence_fingerprint="e" * 128,
)
MATTER_FP = SOURCE_MATTER.fingerprint


class RecordingSession:
    """Active caller-owned transaction with lifecycle counters."""

    in_transaction = True

    def __init__(self) -> None:
        self.starts = 0
        self.commits = 0
        self.aborts = 0

    def start_transaction(self) -> None:
        self.starts += 1

    def commit_transaction(self) -> None:
        self.commits += 1

    def abort_transaction(self) -> None:
        self.aborts += 1


def decision(
    *,
    decision_id: str = "decision-l9c9-p4",
    state: LegalClientMatterEngagementFirmDecisionType = LegalClientMatterEngagementFirmDecisionType.ACCEPTED,
    effective_from: datetime | None = None,
) -> LegalClientMatterEngagementFirmDecision:
    """Build valid synthetic evidence for the exact requested lineage."""
    effective = effective_from or (BASE + timedelta(minutes=5))
    return LegalClientMatterEngagementFirmDecision.from_canonical(
        decision_id=decision_id,
        case_matter=SOURCE_MATTER,
        party=SOURCE_PARTY,
        decision=state,
        decision_actor_principal_id="principal:l9c9-p4",
        authorization_evidence_reference="iam:l9c9-p4",
        authorization_evidence_fingerprint="c" * 128,
        source_evidence_reference=f"source:{decision_id}",
        source_evidence_fingerprint="d" * 128,
        occurred_at=effective,
        effective_from=effective,
        idempotency_key=f"idempotency:{decision_id}",
    )


def build_composer(monkeypatch: pytest.MonkeyPatch, history: tuple[Any, ...] = ()) -> tuple[Any, list[tuple[tuple[Any, ...], dict[str, Any]]]]:
    """Install one recording registry seam and return its call log."""
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def read(*args: Any, **kwargs: Any) -> tuple[Any, ...]:
        calls.append((args, kwargs))
        return history

    monkeypatch.setattr(composer_module.decision_registry, "list_firm_decisions_for_context", read)
    return LegalClientMatterEngagementFirmDecisionCurrentnessComposer(decision_collection=object()), calls


def compose(composer: Any, session: Any, **changes: Any) -> Any:
    values: dict[str, Any] = {
        "tenant_id": TENANT,
        "case_matter_id": MATTER,
        "matter_fingerprint": MATTER_FP,
        "client_party_id": PARTY,
        "subject_identity_fingerprint": SUBJECT_FP,
        "evaluated_at": BASE + timedelta(hours=1),
    }
    values.update(changes)
    return composer.compose_currentness(**values, session=session)


def test_contract_scope_one_read_and_same_session(monkeypatch: pytest.MonkeyPatch) -> None:
    composer, calls = build_composer(monkeypatch, (decision(),))
    session = RecordingSession()
    result = compose(composer, session)
    assert VERSION == "v1.0.0-L9C9-P4-ENGAGEMENT-FIRM-DECISION-CURRENTNESS-COMPOSER"
    assert type(result).__name__ == "LegalClientMatterEngagementFirmDecisionCurrentness"
    assert result.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.ACCEPTED
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[:5] == (TENANT, MATTER, MATTER_FP, PARTY, SUBJECT_FP)
    assert kwargs["session"] is session
    assert session.starts == session.commits == session.aborts == 0


@pytest.mark.parametrize("session", [None, type("Inactive", (), {"in_transaction": False})()])
def test_active_transaction_required_before_read(monkeypatch: pytest.MonkeyPatch, session: Any) -> None:
    composer, calls = build_composer(monkeypatch, (decision(),))
    with pytest.raises(LegalClientMatterEngagementFirmDecisionCurrentnessComposerError) as raised:
        compose(composer, session)
    assert raised.value.code == "L9C9_P4_ACTIVE_TRANSACTION_REQUIRED"
    assert calls == []


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        (LegalClientMatterEngagementFirmDecisionType.ACCEPTED, LegalClientMatterEngagementFirmDecisionCurrentnessState.ACCEPTED),
        (LegalClientMatterEngagementFirmDecisionType.DECLINED, LegalClientMatterEngagementFirmDecisionCurrentnessState.DECLINED),
        (LegalClientMatterEngagementFirmDecisionType.REQUIRES_REVIEW, LegalClientMatterEngagementFirmDecisionCurrentnessState.REQUIRES_REVIEW),
    ],
)
def test_empty_and_state_passthrough(monkeypatch: pytest.MonkeyPatch, state: Any, expected: Any) -> None:
    empty, _ = build_composer(monkeypatch, ())
    assert compose(empty, RecordingSession()).state is LegalClientMatterEngagementFirmDecisionCurrentnessState.NO_DECISION
    value, _ = build_composer(monkeypatch, (decision(state=state),))
    assert compose(value, RecordingSession()).state is expected


def test_future_and_same_effective_semantics_are_owned_by_p3(monkeypatch: pytest.MonkeyPatch) -> None:
    future = decision(effective_from=BASE + timedelta(days=1))
    composer, _ = build_composer(monkeypatch, (future,))
    result = compose(composer, RecordingSession(), evaluated_at=BASE)
    direct = project_legal_client_matter_engagement_firm_decision_currentness(
        tenant_id=TENANT,
        case_matter_id=MATTER,
        matter_fingerprint=MATTER_FP,
        client_party_id=PARTY,
        subject_identity_fingerprint=SUBJECT_FP,
        evaluated_at=BASE,
        decisions=(future,),
    )
    assert result == direct
    assert result.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.NO_DECISION
    conflicting = decision(decision_id="decision-conflict", state=LegalClientMatterEngagementFirmDecisionType.DECLINED)
    composer, _ = build_composer(monkeypatch, (decision(), conflicting))
    assert compose(composer, RecordingSession()).state is LegalClientMatterEngagementFirmDecisionCurrentnessState.AMBIGUOUS


def test_later_acceptance_restoration_and_corrupt_passthrough(monkeypatch: pytest.MonkeyPatch) -> None:
    earlier = decision(state=LegalClientMatterEngagementFirmDecisionType.DECLINED)
    later = decision(decision_id="decision-later", state=LegalClientMatterEngagementFirmDecisionType.ACCEPTED, effective_from=BASE + timedelta(minutes=10))
    composer, _ = build_composer(monkeypatch, (later, earlier))
    assert compose(composer, RecordingSession()).state is LegalClientMatterEngagementFirmDecisionCurrentnessState.ACCEPTED
    invalid = cast(Any, object())
    composer, _ = build_composer(monkeypatch, (invalid,))
    assert compose(composer, RecordingSession()).state is LegalClientMatterEngagementFirmDecisionCurrentnessState.CORRUPT_BLOCKED


def test_time_is_explicit_and_normalized_without_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    composer, calls = build_composer(monkeypatch, (decision(),))
    provided = (BASE + timedelta(hours=1)).astimezone(timezone(timedelta(hours=2)))
    result = compose(composer, RecordingSession(), evaluated_at=provided)
    assert result.evaluation_time == provided.astimezone(timezone.utc)
    assert len(calls) == 1


def test_registry_and_projection_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(*_args: Any, **_kwargs: Any) -> Any:
        raise decision_registry.LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError("secret")

    monkeypatch.setattr(composer_module.decision_registry, "list_firm_decisions_for_context", broken)
    composer = LegalClientMatterEngagementFirmDecisionCurrentnessComposer(decision_collection=object())
    with pytest.raises(LegalClientMatterEngagementFirmDecisionCurrentnessComposerError) as raised:
        compose(composer, RecordingSession())
    assert raised.value.code == "L9C9_P4_HISTORY_READ_FAILED"
    assert "secret" not in str(raised.value)

    composer, _ = build_composer(monkeypatch, (decision(),))
    monkeypatch.setattr(composer_module, "project_legal_client_matter_engagement_firm_decision_currentness", lambda **_: (_ for _ in ()).throw(ValueError("secret")))
    with pytest.raises(LegalClientMatterEngagementFirmDecisionCurrentnessComposerError) as raised:
        compose(composer, RecordingSession())
    assert raised.value.code == "L9C9_P4_PROJECTION_FAILED"
    assert "secret" not in str(raised.value)


def test_history_object_and_inputs_are_not_mutated(monkeypatch: pytest.MonkeyPatch) -> None:
    history = (decision(),)
    composer, _ = build_composer(monkeypatch, history)
    inputs = {"tenant_id": TENANT, "case_matter_id": MATTER, "matter_fingerprint": MATTER_FP, "client_party_id": PARTY, "subject_identity_fingerprint": SUBJECT_FP}
    before = dict(inputs)
    compose(composer, RecordingSession(), **inputs)
    assert inputs == before and history == (history[0],)


def test_forbidden_authorities_and_duplicated_logic_absent() -> None:
    path = Path("tools/eos/legal_operations/orchestration/legal_client_matter_engagement_firm_decision_currentness_composer.py")
    tree = ast.parse(path.read_text())
    imported = " ".join(node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom))
    assert "legal_client_matter_engagement_firm_decision_currentness" in imported
    assert "legal_operations.registry" in imported
    text = path.read_text()
    forbidden_modules = ("principal_status", "conflict_currentness", "mandate_currentness", "representation", "court", "finance", "pymongo", "mongo")
    assert all(token not in imported.lower() for token in forbidden_modules)
    assert "legal_operations.registry" in imported
    assert "datetime.now" not in text and "utcnow" not in text
    assert "sorted(" not in text and "max(" not in text


# ARTIFACT: test_legal_client_matter_engagement_firm_decision_currentness_composer.py
# VERSION: v1.0.0-L9C9-P4-ENGAGEMENT-FIRM-DECISION-CURRENTNESS-COMPOSER-CERT
# AUTHORITY BOUNDARY: direct one-read composer certificate only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
