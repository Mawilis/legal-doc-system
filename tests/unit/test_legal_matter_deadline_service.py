"""D3A legal-matter deadline service unit certificate.

TITLE: Wilsy OS Legal Matter Deadline Service Unit Certificate
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D3A-DEADLINE-SERVICE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify matter correlation, D1/D2 composition, session propagation, replay and authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system-legal-deadline-engine/tests/unit/test_legal_matter_deadline_service.py
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D3A-DEADLINE-SERVICE-CERT establishes direct service evidence.
TENANT BOUNDARY: Exact tenant/matter correlation precedes writes.
AUTHORITY BOUNDARY: Service composition only; no IAM, legal-rule or execution truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Matter, transaction, D1 and D2 failures reject.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import inspect
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_matter_deadline import LegalMatterDeadline, LegalMatterDeadlineTemporalPosture
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry.legal_matter_deadline_registry import LegalMatterDeadlineRegistryConflictError, LegalMatterDeadlineRegistryNotFoundError
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistryError
from tools.eos.legal_operations.service import legal_matter_deadline_service as service

NOW = datetime(2026, 10, 11, 8, 0, tzinfo=timezone.utc)


class Session:
    in_transaction = True


def matter(tenant: str = "tenant-a") -> CaseMatter:
    return CaseMatter(tenant_id=tenant, case_matter_id="matter-1", matter_reference="MAT-1", opened_at=NOW, evidence_reference="matter:1")


def command(**changes: object) -> dict[str, object]:
    values: dict[str, object] = {"tenant_id": "tenant-a", "case_matter_id": "matter-1", "deadline_id": "deadline-1", "deadline_kind": "FILING", "title": "Deadline", "due_at": NOW + timedelta(days=7), "source_type": "COURT_ORDER", "source_reference": "evidence:order", "source_evidence_fingerprint": "a" * 128, "jurisdiction_reference": "jurisdiction:court", "created_at": NOW, "matter_collection": object(), "deadline_collection": object(), "session": Session()}
    values.update(changes); return values


def install(monkeypatch: pytest.MonkeyPatch, *, history: tuple[CaseMatter, ...] | None = None) -> list[tuple[str, object]]:
    calls: list[tuple[str, object]] = []
    def get_history(tenant: str, entity_type: str, identity: str, collection: Any, *, session: Any):
        calls.append(("matter", session)); return history if history is not None else (matter(tenant),)
    def persist(value: LegalMatterDeadline, collection: Any, *, session: Any):
        calls.append(("persist", session)); return value
    monkeypatch.setattr(service.LegalOperationsLifecycleRegistry, "get_entity_history", staticmethod(get_history))
    monkeypatch.setattr(service.LegalMatterDeadlineRegistry, "persist_deadline", staticmethod(persist))
    return calls


def test_valid_command_correlates_matter_then_constructs_d1_and_persists_d2(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = install(monkeypatch); args = command(); value = service.record_legal_matter_deadline(**args)  # type: ignore[arg-type]
    assert type(value) is LegalMatterDeadline and value.tenant_id == "tenant-a"
    assert [name for name, _ in calls] == ["matter", "persist"]
    assert calls[0][1] is args["session"] is calls[1][1]


@pytest.mark.parametrize("history", ((), (matter("tenant-b"),)))
def test_absent_and_foreign_matter_are_same_bounded_failure(monkeypatch: pytest.MonkeyPatch, history: tuple[CaseMatter, ...]) -> None:
    calls = install(monkeypatch, history=history)
    with pytest.raises(service.LegalMatterDeadlineServiceError) as captured: service.record_legal_matter_deadline(**command())  # type: ignore[arg-type]
    assert captured.value.code == "DEADLINE_MATTER_NOT_AVAILABLE"
    assert [name for name, _ in calls] == ["matter"]


def test_matter_repository_failure_is_stable_and_precedes_deadline_write(monkeypatch: pytest.MonkeyPatch) -> None:
    persisted = False

    def fail_history(*args: object, **kwargs: object) -> tuple[CaseMatter, ...]:
        raise LegalOperationsLifecycleRegistryError("repository unavailable")

    def persist(*args: object, **kwargs: object) -> LegalMatterDeadline:
        nonlocal persisted
        persisted = True
        raise AssertionError("deadline persistence must not run")

    monkeypatch.setattr(service.LegalOperationsLifecycleRegistry, "get_entity_history", staticmethod(fail_history))
    monkeypatch.setattr(service.LegalMatterDeadlineRegistry, "persist_deadline", staticmethod(persist))
    with pytest.raises(service.LegalMatterDeadlineServiceError) as captured:
        service.record_legal_matter_deadline(**command())  # type: ignore[arg-type]
    assert captured.value.code == "DEADLINE_MATTER_PERSISTENCE_FAILURE"
    assert persisted is False


def test_transaction_and_d1_validation_fail_before_persistence(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = install(monkeypatch)
    with pytest.raises(service.LegalMatterDeadlineServiceError, match="DEADLINE_TRANSACTION_REQUIRED"): service.record_legal_matter_deadline(**command(session=None))  # type: ignore[arg-type]
    with pytest.raises(service.LegalMatterDeadlineServiceError, match="DEADLINE_INVALID"): service.record_legal_matter_deadline(**command(source_evidence_fingerprint="bad"))  # type: ignore[arg-type]
    with pytest.raises(service.LegalMatterDeadlineServiceError, match="DEADLINE_INVALID"): service.record_legal_matter_deadline(**command(due_at=datetime(2026, 10, 12)))  # type: ignore[arg-type]
    assert [name for name, _ in calls] == ["matter", "matter"]


def test_replay_conflict_reads_and_temporal_posture_delegate(monkeypatch: pytest.MonkeyPatch) -> None:
    install(monkeypatch); value = service.record_legal_matter_deadline(**command())  # type: ignore[arg-type]
    monkeypatch.setattr(service.LegalMatterDeadlineRegistry, "get_deadline", staticmethod(lambda *a, **k: value))
    monkeypatch.setattr(service.LegalMatterDeadlineRegistry, "list_matter_deadlines", staticmethod(lambda *a, **k: (value,)))
    assert service.get_legal_matter_deadline(tenant_id="tenant-a", deadline_id="deadline-1", deadline_collection=object(), session=Session()) == value
    assert service.list_legal_matter_deadlines(tenant_id="tenant-a", case_matter_id="matter-1", deadline_collection=object(), session=Session()) == (value,)
    assert service.observe_legal_matter_deadline(value, at=value.due_at + timedelta(seconds=1)) is LegalMatterDeadlineTemporalPosture.OVERDUE
    monkeypatch.setattr(service.LegalMatterDeadlineRegistry, "get_deadline", staticmethod(lambda *a, **k: (_ for _ in ()).throw(LegalMatterDeadlineRegistryNotFoundError())))
    with pytest.raises(service.LegalMatterDeadlineServiceError, match="DEADLINE_NOT_AVAILABLE"): service.get_legal_matter_deadline(tenant_id="tenant-b", deadline_id="deadline-1", deadline_collection=object(), session=Session())
    monkeypatch.setattr(service.LegalMatterDeadlineRegistry, "persist_deadline", staticmethod(lambda *a, **k: (_ for _ in ()).throw(LegalMatterDeadlineRegistryConflictError())))
    with pytest.raises(service.LegalMatterDeadlineServiceError, match="DEADLINE_CONFLICT"): service.record_legal_matter_deadline(**command())  # type: ignore[arg-type]


def test_supersession_does_not_mutate_prior_and_service_owns_no_forbidden_authority(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = install(monkeypatch); value = service.record_legal_matter_deadline(**command(deadline_id="deadline-2", supersedes_deadline_id="deadline-1"))  # type: ignore[arg-type]
    assert value.supersedes_deadline_id == "deadline-1" and [name for name, _ in calls] == ["matter", "persist"]
    source = inspect.getsource(service)
    for token in ("MongoClient(", "start_transaction(", "commit_transaction(", "abort_transaction(", "timedelta(", "calculate_due_at(", "is_holiday(", "add_business_days(", "ai_generated", "payment_authority"):
        assert token not in source


# ARTIFACT: test_legal_matter_deadline_service.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D3A-DEADLINE-SERVICE-CERT
# AUTHORITY BOUNDARY: direct matter-correlation and D1/D2 composition certificate only
# TENANT POSTURE: exact tenant/matter correlation precedes persistence
# FAIL-CLOSED POSTURE: transaction, matter, validation, conflict and persistence failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
