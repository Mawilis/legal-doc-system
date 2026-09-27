"""Direct certificate for the L9C5 currentness composer.

TITLE: WILSY OS Legal Client Matter Conflict Disposition Currentness Composer Certificate
VERSION: v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS-COMPOSER-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify one exact registry history read, caller-session propagation,
         explicit-time propagation and pure projection delegation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_conflict_disposition_currentness_composer.py
COLLABORATION / OWNERSHIP: The disposition registry and currentness domain
                            remain the only authorities exercised here.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS-COMPOSER-CERT covers
           active caller transactions, exact five-dimensional scope, one read,
           pure delegation, fail-closed mapping and forbidden-authority audit.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TRANSACTION BOUNDARY: Recording fakes only; no Mongo or network.
FAIL-CLOSED DECLARATION: Missing/inactive transactions and registry failures
                         never become a currentness result.
"""
from __future__ import annotations

import ast
from dataclasses import replace
from datetime import timedelta, timezone
from pathlib import Path

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition import (
    LegalClientMatterConflictDispositionType,
)
from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition_currentness import (
    LegalClientMatterConflictDispositionCurrentnessState,
)
from tools.eos.legal_operations.orchestration import (
    legal_client_matter_conflict_disposition_currentness_composer as composer_module,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_conflict_disposition_currentness_composer import (
    VERSION,
    LegalClientMatterConflictDispositionCurrentnessComposer,
    LegalClientMatterConflictDispositionCurrentnessComposerError,
)
from tests.unit.test_legal_client_matter_conflict_disposition import BASE, TENANT, bundle


MATTER = "matter-l9b2"
SOURCE = bundle()[0]
MATTER_FP = SOURCE.matter_fingerprint
PARTY = SOURCE.client_party_id
SUBJECT = SOURCE.subject_identity_fingerprint
AT = BASE + timedelta(hours=1)


class Session:
    """Recording active caller transaction with forbidden lifecycle methods."""

    def __init__(self, active: bool = True) -> None:
        self.active = active
        self.starts = 0
        self.commits = 0
        self.aborts = 0

    def in_transaction(self) -> bool:
        return self.active

    def start_transaction(self) -> None:
        self.starts += 1

    def commit_transaction(self) -> None:
        self.commits += 1

    def abort_transaction(self) -> None:
        self.aborts += 1


def value(*, state=LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED, effective=None, suffix="a"):
    source = bundle(disposition=state)[0]
    return replace(
        source,
        disposition_id=f"disposition-l9c5-composer-{suffix}",
        idempotency_key=f"idempotency:l9c5:composer:{suffix}",
        occurred_at=(effective - timedelta(minutes=1) if effective else source.occurred_at),
        effective_from=effective or source.effective_from,
        fingerprint="",
    )


def make_composer(monkeypatch, history):
    calls = []

    def read(*args, **kwargs):
        calls.append((args, kwargs))
        return tuple(history)

    monkeypatch.setattr(composer_module.disposition_registry, "list_dispositions_for_context", read)
    return LegalClientMatterConflictDispositionCurrentnessComposer(disposition_collection=object()), calls


def compose(composer, session, **changes):
    values = {
        "tenant_id": TENANT,
        "case_matter_id": MATTER,
        "matter_fingerprint": MATTER_FP,
        "client_party_id": PARTY,
        "subject_identity_fingerprint": SUBJECT,
        "evaluation_time": AT,
    }
    values.update(changes)
    return composer.compose_currentness(**values, session=session)


def test_version_and_exact_scope_read_with_same_session(monkeypatch):
    source = value()
    composer, calls = make_composer(monkeypatch, [source])
    session = Session()
    result = compose(composer, session)
    assert VERSION == "v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS-COMPOSER"
    assert result.state is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[0:5] == (TENANT, MATTER, MATTER_FP, PARTY, SUBJECT)
    assert kwargs["session"] is session
    assert result.is_engagement_permitted


def test_empty_history_and_all_three_states(monkeypatch):
    composer, _ = make_composer(monkeypatch, [])
    assert compose(composer, Session()).state is LegalClientMatterConflictDispositionCurrentnessState.NO_DISPOSITION
    for state in LegalClientMatterConflictDispositionType:
        composer, _ = make_composer(monkeypatch, [value(state=state, suffix=state.value)])
        result = compose(composer, Session())
        assert result.state is LegalClientMatterConflictDispositionCurrentnessState(state.value)
        assert result.is_engagement_permitted is (state is LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED)


def test_projection_owns_latest_future_and_ambiguity_semantics(monkeypatch):
    earlier = value(effective=BASE + timedelta(minutes=10), suffix="earlier")
    later = value(state=LegalClientMatterConflictDispositionType.ENGAGEMENT_PROHIBITED, effective=BASE + timedelta(minutes=20), suffix="later")
    future = value(state=LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED, effective=AT + timedelta(days=1), suffix="future")
    composer, _ = make_composer(monkeypatch, [future, later, earlier])
    result = compose(composer, Session())
    assert result.state is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PROHIBITED
    same_time = value(state=LegalClientMatterConflictDispositionType.ENGAGEMENT_UNRESOLVED, effective=later.effective_from, suffix="conflict")
    composer, _ = make_composer(monkeypatch, [later, same_time])
    assert compose(composer, Session()).state is LegalClientMatterConflictDispositionCurrentnessState.AMBIGUOUS


def test_time_is_passed_exactly_after_aware_normalization(monkeypatch):
    composer, calls = make_composer(monkeypatch, [value()])
    provided = AT.replace(tzinfo=timezone(timedelta(hours=2)))
    result = compose(composer, Session(), evaluation_time=provided)
    assert result.evaluation_time == provided.astimezone(timezone.utc)
    assert len(calls) == 1


@pytest.mark.parametrize("session", [None, Session(False)])
def test_missing_or_inactive_transaction_fails_closed(monkeypatch, session):
    composer, calls = make_composer(monkeypatch, [value()])
    with pytest.raises(LegalClientMatterConflictDispositionCurrentnessComposerError) as raised:
        compose(composer, session)
    assert raised.value.code == "L9C5_P2_ACTIVE_TRANSACTION_REQUIRED"
    assert calls == []


def test_invalid_time_and_scope_are_rejected_without_read(monkeypatch):
    composer, calls = make_composer(monkeypatch, [value()])
    with pytest.raises(LegalClientMatterConflictDispositionCurrentnessComposerError):
        compose(composer, Session(), evaluation_time=AT.replace(tzinfo=None))
    with pytest.raises(LegalClientMatterConflictDispositionCurrentnessComposerError):
        compose(composer, Session(), tenant_id=" tenant-l9c5")
    assert calls == []


def test_registry_corruption_or_unavailability_maps_non_sensitive(monkeypatch):
    def broken(*_args, **_kwargs):
        raise composer_module.disposition_registry.LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError("L9C3_PERSISTED_RECORD_INVALID")

    monkeypatch.setattr(composer_module.disposition_registry, "list_dispositions_for_context", broken)
    composer = LegalClientMatterConflictDispositionCurrentnessComposer(disposition_collection=object())
    with pytest.raises(LegalClientMatterConflictDispositionCurrentnessComposerError) as raised:
        compose(composer, Session())
    assert raised.value.code == "L9C5_P2_HISTORY_READ_FAILED"
    assert "L9C3" not in str(raised.value)


def test_no_transaction_lifecycle_no_writes_and_exact_return_type(monkeypatch):
    composer, _ = make_composer(monkeypatch, [value()])
    session = Session()
    result = compose(composer, session)
    assert type(result).__name__ == "LegalClientMatterConflictDispositionCurrentness"
    assert session.starts == session.commits == session.aborts == 0


def test_functional_boundary_and_deterministic_fingerprint(monkeypatch):
    composer, _ = make_composer(monkeypatch, [value()])
    session = Session()
    first = compose(composer, session)
    second = compose(composer, Session())
    assert first.fingerprint == second.fingerprint and len(first.fingerprint) == 128


def test_negative_import_and_no_duplicated_currentness_authority():
    path = Path("tools/eos/legal_operations/orchestration/legal_client_matter_conflict_disposition_currentness_composer.py")
    module = ast.parse(path.read_text())
    imported = {node.module for node in ast.walk(module) if isinstance(node, ast.ImportFrom) and node.module}
    text = path.read_text()
    forbidden = ("screening_registry", "review_registry", "client_acceptance", "mandate", "engagement", "representation", "court", "pymongo", "mongo", "jwt")
    assert all(token not in " ".join(imported) for token in forbidden)
    assert "datetime.now" not in text and "utcnow" not in text
    assert "max(" not in text and "AMBIGUOUS" not in text.split("project_legal_client_matter_conflict_disposition_currentness", 1)[0]


# ARTIFACT: test_legal_client_matter_conflict_disposition_currentness_composer.py
# VERSION: v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS-COMPOSER-CERT
# AUTHORITY BOUNDARY: direct read-only composer certificate only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
