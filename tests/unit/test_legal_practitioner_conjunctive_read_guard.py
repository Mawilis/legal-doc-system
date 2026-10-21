"""P9-R105-P4G-P6-R3C conjunctive documentary denial certificate."""
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.legal_operations.service import (
    legal_practitioner_conjunctive_read_guard as guard,
)
from tools.eos.legal_operations.service.legal_practitioner_ethical_wall_read_barrier import (
    EthicalWallReadBarrierState as WallState,
)
from tools.eos.legal_operations.domain.legal_practitioner_matter_access_currentness import (
    LegalPractitionerMatterAccessCurrentnessState as AccessState,
)

NOW = datetime(2026, 10, 19, 18, tzinfo=timezone.utc)


class Session:
    in_transaction = True


def exercise(
    monkeypatch: pytest.MonkeyPatch,
    *,
    wall_state: WallState = WallState.DENY_UNVERIFIED,
    access_state: AccessState = AccessState.ALLOW_UNVERIFIED,
    error_at: str | None = None,
    session: Any = None,
) -> tuple[guard.ConjunctiveReadGuardResult, list[Any]]:
    events: list[Any] = []
    active_session = Session() if session is None else session

    def wall(**kw: Any) -> Any:
        events.append(("wall", kw))
        if error_at == "wall":
            raise RuntimeError("wall unavailable")
        return SimpleNamespace(
            state=wall_state,
            currentness=SimpleNamespace(
                decisive_restriction_fingerprints=("a" * 128,)
            ),
        )

    def history(**kw: Any) -> Any:
        events.append(("history", kw))
        if error_at == "history":
            raise RuntimeError("history unavailable")
        return ()

    def project(**kw: Any) -> Any:
        events.append(("project", kw))
        if error_at == "project":
            raise RuntimeError("projection unavailable")
        return SimpleNamespace(
            state=access_state,
            decisive_fingerprints=("b" * 128,),
        )

    monkeypatch.setattr(
        guard, "inspect_practitioner_ethical_wall_read_barrier", wall
    )
    monkeypatch.setattr(
        guard, "read_practitioner_matter_access_history", history
    )
    monkeypatch.setattr(
        guard, "project_legal_practitioner_matter_access_currentness",
        project,
    )

    result = guard.inspect_conjunctive_practitioner_read_guard(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        practitioner_principal_id="principal-1",
        wall_collection=object(),
        practitioner_access_collection=object(),
        session=active_session,
        server_clock=lambda: NOW,
    )
    return result, events


def test_restriction_preempts_access_history(monkeypatch):
    result, events = exercise(
        monkeypatch, wall_state=WallState.DENY_RESTRICTED
    )
    assert result.state is guard.ConjunctiveReadGuardState.DENY_WALL
    assert result.wall_fingerprints == ("a" * 128,)
    assert [event[0] for event in events] == ["wall"]
    assert not result.permits_content


@pytest.mark.parametrize("state", [
    AccessState.DENY_BLOCKED,
    AccessState.AMBIGUOUS_BLOCKED,
    AccessState.CORRUPT_BLOCKED,
])
def test_documentary_denial_blocks(monkeypatch, state):
    result, events = exercise(monkeypatch, access_state=state)
    assert result.state is (
        guard.ConjunctiveReadGuardState.DENY_DOCUMENTARY_ACCESS
    )
    assert [event[0] for event in events] == [
        "wall", "history", "project"
    ]
    assert not result.authorized


@pytest.mark.parametrize("state", [
    AccessState.ALLOW_UNVERIFIED,
    AccessState.NO_APPLICABLE_EVIDENCE,
])
def test_unverified_never_becomes_authorized(monkeypatch, state):
    result, events = exercise(monkeypatch, access_state=state)
    assert result.state is guard.ConjunctiveReadGuardState.DENY_UNVERIFIED
    assert not result.authorized and not result.permits_content
    wall, history, projector = [entry[1] for entry in events]
    assert wall["session"] is history["session"]
    assert wall["evaluation_time"] == projector["evaluation_time"] == NOW
    assert wall["tenant_id"] == history["tenant_id"] == "tenant-1"
    assert wall["practitioner_principal_id"] == (
        history["practitioner_principal_id"]
    )


@pytest.mark.parametrize("failure", ["wall", "history", "project"])
def test_unavailable_dependency_never_grants(monkeypatch, failure):
    result, _ = exercise(monkeypatch, error_at=failure)
    assert result.state is guard.ConjunctiveReadGuardState.DENY_UNAVAILABLE
    assert not result.permits_content


def test_missing_transaction_never_calls_evidence(monkeypatch):
    events: list[Any] = []
    monkeypatch.setattr(
        guard, "inspect_practitioner_ethical_wall_read_barrier",
        lambda **kw: events.append(kw),
    )
    result = guard.inspect_conjunctive_practitioner_read_guard(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        practitioner_principal_id="principal-1",
        wall_collection=object(),
        practitioner_access_collection=object(),
        session=None,
        server_clock=lambda: NOW,
    )
    assert result.state is guard.ConjunctiveReadGuardState.DENY_UNAVAILABLE
    assert events == []


def test_naive_clock_denies_before_read(monkeypatch):
    monkeypatch.setattr(
        guard, "inspect_practitioner_ethical_wall_read_barrier",
        lambda **kw: pytest.fail("read should not occur"),
    )
    result = guard.inspect_conjunctive_practitioner_read_guard(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        practitioner_principal_id="principal-1",
        wall_collection=object(),
        practitioner_access_collection=object(),
        session=Session(),
        server_clock=lambda: datetime(2026, 10, 19),
    )
    assert result.state is guard.ConjunctiveReadGuardState.DENY_UNAVAILABLE


def test_wall_corruption_does_not_check_documentary_allow(monkeypatch):
    result, events = exercise(
        monkeypatch, wall_state=WallState.DENY_UNAVAILABLE
    )
    assert result.state is guard.ConjunctiveReadGuardState.DENY_UNAVAILABLE
    assert [event[0] for event in events] == ["wall"]


def test_no_content_or_waiver_interface():
    for name in (
        "allow_content", "grant_access", "read_document",
        "waive", "lift", "execute_workflow", "ai_retrieve",
    ):
        assert not hasattr(guard, name)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P6-R3C
# END OF WILSY OS SOVEREIGN ARTIFACT
