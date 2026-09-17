"""C1E-R1D unit certificate for exact replay ordering in the advisory service.

TITLE: WILSY AI Advisory Service Unit Certificate
VERSION: v1.0.1-C1E-R1D
AUTHORITY: Wilsy OS Core Governance
EPITOME: Verifies exact identity replay before supersession, changed-snapshot
         lineage, strict tenant composition, redaction, and fail-closed
         boundaries without Mongo, provider, or model calls.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_advisory_service.py
COLLABORATION / OWNERSHIP: C1E service certificate; R1 static/unit only.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.1-C1E-R1D certifies replay-before-supersession ordering,
           no-write exact replay, changed-snapshot succession, and corruption
           fail-closed behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.intelligence.domain.ai_tool_orchestration import OrchestrationPhase
from tools.eos.intelligence.registry.next_best_action_advisory_registry import (
    NextBestActionAdvisoryConflictError,
    NextBestActionAdvisoryRegistryError,
)
from tools.eos.intelligence.wilsy_ai_advisory_service import (
    AdvisoryServiceResult,
    WilsyAIAdvisoryService,
    WilsyAIAdvisoryServiceError,
)


TENANT = "tenant-r1d"
STAMP = datetime(2026, 9, 17, 8, 0, tzinfo=timezone.utc)


class _Session:
    """Minimal caller-owned transaction seam with observable lifecycle."""

    def __init__(self) -> None:
        self.starts = self.commits = self.aborts = self.ends = 0

    def start_transaction(self) -> None:
        self.starts += 1

    def commit_transaction(self) -> None:
        self.commits += 1

    def abort_transaction(self) -> None:
        self.aborts += 1

    def end_session(self) -> None:
        self.ends += 1


class _Candidate:
    """Bounded advisory double exposing only fields consumed by the service."""

    def __init__(self, source: str, supersedes: str | None) -> None:
        self.tenant_id = TENANT
        self.advisory_id = f"advisory-{source}"
        self.scope_ref = "orchestration-r1d"
        self.policy_id = "WILSY_AI_LEGAL_NEXT_BEST_ACTION_REVIEW_POLICY"
        self.policy_version = "v1"
        self.source_snapshot_fingerprint = source
        self.generated_at = "2026-09-17T08:00:00Z"
        self.supersedes_advisory_id = supersedes
        self.recommendation = SimpleNamespace(
            action_title="Review", rationale="Evidence only.",
            confidence_score=1.0, confidence_basis="Evidence", risk_level="MEDIUM",
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "tenant_id": self.tenant_id,
            "advisory_id": self.advisory_id,
            "scope_ref": self.scope_ref,
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "source_snapshot_fingerprint": self.source_snapshot_fingerprint,
            "generated_at": self.generated_at,
            "supersedes_advisory_id": self.supersedes_advisory_id,
        }


class _Adapter:
    """Adapter double that rejects the historical self-supersession ordering."""

    def __init__(self) -> None:
        self.calls: list[str | None] = []

    def build(self, **kwargs: Any) -> _Candidate:
        source = str(kwargs["result"]["snapshot"])
        supersedes = cast(str | None, kwargs.get("supersedes_advisory_id"))
        candidate_id = f"advisory-{source}"
        if supersedes == candidate_id:
            raise AssertionError("C1D_SELF_SUPERSESSION construction attempted")
        self.calls.append(supersedes)
        return _Candidate(source, supersedes)


class _Orchestrations:
    def __init__(self, roots: list[Any]) -> None:
        self.roots, self.calls = roots, 0

    def get(self, **_: Any) -> Any:
        root = self.roots[min(self.calls, len(self.roots) - 1)]
        self.calls += 1
        return root


class _Invocations:
    def __init__(self, values: dict[str, Any]) -> None:
        self.values, self.calls = values, 0

    def get(self, *, invocation_id: str, **_: Any) -> Any:
        self.calls += 1
        return self.values[invocation_id]


class _Reader:
    def __init__(self, snapshots: dict[str, str]) -> None:
        self.snapshots, self.calls = snapshots, 0

    def read(self, *, resource_identity: str, **_: Any) -> dict[str, object]:
        self.calls += 1
        return {"snapshot": self.snapshots[resource_identity]}


class _Authority:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, **_: Any) -> bool:
        self.calls += 1
        return True


class _Advisories:
    """Tenant-scoped immutable registry double with explicit replay errors."""

    def __init__(self) -> None:
        self.rows: dict[str, Any] = {}
        self.current: Any | None = None
        self.get_calls = self.current_calls = self.create_calls = 0
        self.corrupt = False

    def get(self, *, advisory_id: str, **_: Any) -> Any:
        self.get_calls += 1
        if self.corrupt:
            raise NextBestActionAdvisoryRegistryError("C1D_CORRUPT_ADVISORY")
        if advisory_id not in self.rows:
            raise NextBestActionAdvisoryRegistryError("C1D_NOT_FOUND")
        return self.rows[advisory_id]

    def get_current_by_scope(self, **_: Any) -> Any:
        self.current_calls += 1
        if self.current is None:
            raise NextBestActionAdvisoryRegistryError("C1D_CURRENT_NOT_FOUND")
        return self.current

    def create_or_replay(self, advisory: Any, **_: Any) -> Any:
        self.create_calls += 1
        prior = self.rows.get(advisory.advisory_id)
        if prior is not None:
            if prior.to_dict() != advisory.to_dict():
                raise NextBestActionAdvisoryConflictError("C1D_DIVERGENT_REPLAY")
            return prior
        self.rows[advisory.advisory_id] = advisory
        self.current = advisory
        return advisory


def _context() -> TenantAuthorizationContext:
    identity = SimpleNamespace(identity_id="principal-r1d", tenant_id=TENANT)
    return TenantAuthorizationContext(cast(Any, identity), TENANT, cast(Any, SimpleNamespace()))


def _root(invocation_id: str, resource: str = "attempt-r1d") -> Any:
    return SimpleNamespace(
        orchestration_id="orchestration-r1d", tenant_id=TENANT,
        phase=OrchestrationPhase.COMPLETED, outcome="TOOL_ASSISTED",
        tool_invocation_id=invocation_id, tool_identity="legal.attempt.read.v1",
        resource_identity=resource,
    )


def _invocation(invocation_id: str) -> Any:
    return SimpleNamespace(
        invocation_id=invocation_id, correlation_id="orchestration-r1d",
        tool_identity="legal.attempt.read.v1",
    )


def _service(orchestrations: Any, invocations: Any, advisories: _Advisories,
             reader: _Reader, authority: _Authority, adapter: _Adapter) -> WilsyAIAdvisoryService:
    return WilsyAIAdvisoryService(
        session_factory=_Session,
        orchestration_registry=orchestrations,
        invocation_registry=invocations,
        advisory_registry=advisories,
        legal_reader=reader,
        authority_checker=authority,
        adapter=adapter,
    )


def test_service_rejects_malformed_orchestration_without_opening_session() -> None:
    called = False

    def factory() -> object:
        nonlocal called
        called = True
        return object()

    service = WilsyAIAdvisoryService(session_factory=factory)
    with pytest.raises(WilsyAIAdvisoryServiceError, match="ORCHESTRATION_ID_INVALID"):
        import asyncio
        asyncio.run(service.generate(orchestration_id=" ", context=cast(Any, object())))
    assert called is False


def test_public_projection_contains_only_bounded_review_fields() -> None:
    advisory = SimpleNamespace(
        advisory_id="advisory-1",
        scope_ref="matter-1",
        generated_at="2026-09-17T00:00:00Z",
        recommendation=SimpleNamespace(
            action_title="Review", rationale="Review evidence.", confidence_score=1.0,
            confidence_basis="Evidence only.", risk_level="MEDIUM",
        ),
    )
    result = AdvisoryServiceResult(advisory, replay=False)  # type: ignore[arg-type]
    payload = result.to_public_dict()
    assert set(payload) == {"advisory_id", "scope_ref", "title", "rationale", "confidence_score", "confidence_basis", "risk_level", "generated_at", "status", "superseded_by_advisory_id"}
    assert not any(token in str(payload).lower() for token in ("fingerprint", "provider", "model", "prompt", "execution"))


def test_service_has_no_provider_or_financial_execution_surface() -> None:
    names = set(dir(WilsyAIAdvisoryService))
    assert not names.intersection({"execute", "approve", "pay", "settle", "release", "run_model"})


def test_exact_replay_is_resolved_before_current_supersession() -> None:
    """An unchanged source replays without a second write or self-successor."""
    root = _root("invocation-r1d")
    invocations = _Invocations({"invocation-r1d": _invocation("invocation-r1d")})
    orchestrations = _Orchestrations([root, root])
    advisories, reader, authority, adapter = _Advisories(), _Reader({"attempt-r1d": "snapshot-a"}), _Authority(), _Adapter()
    service = _service(orchestrations, invocations, advisories, reader, authority, adapter)

    first = asyncio.run(service.generate(orchestration_id=root.orchestration_id, context=_context(), generated_at=STAMP))
    replay = asyncio.run(service.generate(orchestration_id=root.orchestration_id, context=_context(), generated_at=STAMP))

    assert first.replay is False
    assert replay.replay is True and replay.advisory.to_dict() == first.advisory.to_dict()
    assert len(advisories.rows) == 1 and advisories.create_calls == 1
    assert advisories.current_calls == 1
    assert adapter.calls == [None, None]
    assert authority.calls == 4 and reader.calls == 4


def test_changed_snapshot_resolves_current_then_supersedes_it() -> None:
    """A genuinely changed source builds one successor over the prior current row."""
    first_root, second_root = _root("invocation-a"), _root("invocation-b")
    orchestrations = _Orchestrations([first_root, second_root])
    invocations = _Invocations({"invocation-a": _invocation("invocation-a"), "invocation-b": _invocation("invocation-b")})
    advisories, reader, authority, adapter = _Advisories(), _Reader({"attempt-r1d": "snapshot-a"}), _Authority(), _Adapter()
    service = _service(orchestrations, invocations, advisories, reader, authority, adapter)
    first = asyncio.run(service.generate(orchestration_id=first_root.orchestration_id, context=_context(), generated_at=STAMP))
    reader.snapshots["attempt-r1d"] = "snapshot-b"
    second = asyncio.run(service.generate(orchestration_id=second_root.orchestration_id, context=_context(), generated_at=STAMP))

    assert second.replay is False and len(advisories.rows) == 2
    assert second.advisory.supersedes_advisory_id == first.advisory.advisory_id
    assert adapter.calls == [None, None, first.advisory.advisory_id]
    assert advisories.current_calls == 2


def test_exact_lookup_corruption_fails_closed() -> None:
    """An exact-identity registry corruption error is never treated as a miss."""
    root = _root("invocation-r1d")
    invocations = _Invocations({"invocation-r1d": _invocation("invocation-r1d")})
    advisories, reader, authority, adapter = _Advisories(), _Reader({"attempt-r1d": "snapshot-a"}), _Authority(), _Adapter()
    advisories.corrupt = True
    service = _service(_Orchestrations([root]), invocations, advisories, reader, authority, adapter)

    with pytest.raises(WilsyAIAdvisoryServiceError, match="EVIDENCE_CORRUPT"):
        asyncio.run(service.generate(orchestration_id=root.orchestration_id, context=_context(), generated_at=STAMP))
    assert advisories.create_calls == 0 and advisories.current_calls == 0


# ARTIFACT: test_wilsy_ai_advisory_service.py
# VERSION: v1.0.1-C1E-R1D
# CERTIFICATION: focused service boundary proof; no Mongo/provider execution
# END OF WILSY OS SOVEREIGN ARTIFACT
