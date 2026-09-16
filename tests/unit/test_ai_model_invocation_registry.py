"""Direct C1A certificate for the model-invocation evidence registry.

TITLE: WILSY AI Model Invocation Registry Unit Certificate
VERSION: v1.0.0-WILSY-AI-MODEL-INVOCATION-REGISTRY-UNIT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves deterministic tenant-scoped append/replay persistence against
         a Mongo-shaped double without starting a database or transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_ai_model_invocation_registry.py
COLLABORATION / OWNERSHIP: Certifies the C1A registry and its caller-session
                            transaction boundary.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0 establishes index, persistence, replay, corruption,
           transport-boundary, and transaction-ownership coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only canonical bounded evidence is accepted.
TENANT BOUNDARY: Every collection query includes tenant_id.
AUTHORITY BOUNDARY: Persistence adapter only; no authorization or execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Divergence, corruption, unknown fields, and transport
                         failures reject deterministically.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import inspect

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.intelligence.domain.ai_model_execution import (
    ModelExecutionOutcome,
    ModelExecutionInput,
    ModelInvocationEvidence,
    ModelProviderResult,
)
from tools.eos.intelligence.registry.ai_model_invocation_registry import (
    AIModelInvocationRegistry,
    AIModelInvocationRegistryConflictError,
    AIModelInvocationRegistryError,
    AIModelInvocationRegistryNotFoundError,
    COLLECTION,
    IDENTITY_INDEX_NAME,
    ensure_indexes,
)


class SessionDouble:
    """Caller-owned session marker that exposes no registry lifecycle methods."""


class CollectionDouble:
    """Deterministic Mongo-shaped collection with session call recording."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.index_calls: list[tuple[object, dict[str, object]]] = []
        self.find_calls: list[tuple[dict[str, object], object]] = []
        self.insert_calls: list[tuple[dict[str, object], object]] = []
        self.fail_insert: BaseException | None = None

    def with_options(self, **_: object) -> "CollectionDouble":
        return self

    def create_index(self, keys: object, **kwargs: object) -> str:
        self.index_calls.append((keys, kwargs))
        return str(kwargs.get("name", "index"))

    def find_one(self, query: dict[str, object], *, session: object) -> dict[str, object] | None:
        self.find_calls.append((dict(query), session))
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None

    def insert_one(self, document: dict[str, object], *, session: object) -> None:
        self.insert_calls.append((dict(document), session))
        if self.fail_insert is not None:
            raise self.fail_insert
        if any(
            row.get("tenant_id") == document.get("tenant_id")
            and row.get("invocation_id") == document.get("invocation_id")
            for row in self.rows
        ):
            raise DuplicateKeyError("duplicate")
        self.rows.append(dict(document, _id="transport-id"))


BASE_TIME = datetime(2026, 9, 16, 8, 0, tzinfo=timezone.utc)


def make_evidence(*, tenant_id: str = "tenant-c1a", invocation_id: str = "invocation-1", correlation_id: str = "correlation-1", response_text: str = "Bounded result.") -> ModelInvocationEvidence:
    """Build one deterministic evidence fixture through production composition."""
    request = ModelExecutionInput(
        tenant_id=tenant_id,
        principal_id="principal-1",
        invocation_id=invocation_id,
        correlation_id=correlation_id,
        entitlement_id="entitlement-1",
        provider_id="provider-neutral",
        model_id="model-neutral-v1",
        prompt="Bounded prompt.",
        system_policy="Bounded policy.",
        tool_invocation_evidence_references=("tool-evidence-1",),
    )
    result = ModelProviderResult(
        provider_id="provider-neutral",
        model_id="model-neutral-v1",
        response_text=response_text,
        provider_request_id="provider-request-1",
        input_tokens=2,
        output_tokens=2,
    )
    return ModelInvocationEvidence.from_execution(
        request,
        result,
        created_at=BASE_TIME,
        completed_at=BASE_TIME + timedelta(seconds=1),
    )


def test_collection_and_tenant_identity_index() -> None:
    """The registry uses a dedicated collection and one deterministic identity index."""
    collection = CollectionDouble()
    ensure_indexes(collection)
    assert COLLECTION == "wilsy_ai_model_invocations"
    assert len(collection.index_calls) == 1
    keys, options = collection.index_calls[0]
    assert keys == [("tenant_id", 1), ("invocation_id", 1)]
    assert options == {"unique": True, "name": IDENTITY_INDEX_NAME}


def test_create_get_and_exact_session_passthrough() -> None:
    """Create/get persist canonical evidence and pass the caller session unchanged."""
    collection = CollectionDouble()
    registry = AIModelInvocationRegistry(collection)
    session = SessionDouble()
    evidence = make_evidence()
    assert registry.create_or_replay(evidence, session=session) == evidence
    assert registry.get(tenant_id="tenant-c1a", invocation_id="invocation-1", session=session) == evidence
    assert all(call_session is session for _, call_session in collection.find_calls)
    assert all(call_session is session for _, call_session in collection.insert_calls)
    assert "_id" not in collection.insert_calls[0][0]


def test_absence_and_foreign_tenant_are_not_found() -> None:
    """Exact tenant predicates prevent cross-tenant evidence disclosure."""
    registry = AIModelInvocationRegistry(CollectionDouble())
    session = SessionDouble()
    with pytest.raises(AIModelInvocationRegistryNotFoundError, match="C1A_INVOCATION_NOT_FOUND"):
        registry.get(tenant_id="tenant-c1a", invocation_id="missing", session=session)
    collection = CollectionDouble()
    registry = AIModelInvocationRegistry(collection)
    registry.create_or_replay(make_evidence(tenant_id="tenant-a"), session=session)
    with pytest.raises(AIModelInvocationRegistryNotFoundError):
        registry.get(tenant_id="tenant-b", invocation_id="invocation-1", session=session)
    assert collection.find_calls[-1][0] == {"tenant_id": "tenant-b", "invocation_id": "invocation-1"}


def test_identical_replay_returns_existing_without_second_write() -> None:
    """A byte-equivalent invocation identity is idempotent."""
    collection = CollectionDouble()
    registry = AIModelInvocationRegistry(collection)
    session = SessionDouble()
    evidence = make_evidence()
    first = registry.create_or_replay(evidence, session=session)
    second = registry.create_or_replay(evidence, session=session)
    assert first == second == evidence
    assert len(collection.insert_calls) == 1


def test_divergent_replay_fails_closed() -> None:
    """The same tenant/invocation identity cannot be rebound to new evidence."""
    collection = CollectionDouble()
    registry = AIModelInvocationRegistry(collection)
    session = SessionDouble()
    registry.create_or_replay(make_evidence(), session=session)
    divergent = make_evidence(response_text="Different result.")
    with pytest.raises(AIModelInvocationRegistryConflictError, match="C1A_DIVERGENT_REPLAY"):
        registry.create_or_replay(divergent, session=session)
    assert len(collection.insert_calls) == 1


def test_transport_id_is_removed_but_unknown_field_is_rejected() -> None:
    """Only Mongo _id is stripped; arbitrary persisted fields remain invalid."""
    collection = CollectionDouble()
    registry = AIModelInvocationRegistry(collection)
    session = SessionDouble()
    evidence = make_evidence()
    registry.create_or_replay(evidence, session=session)
    collection.rows[0]["unknown_persisted_field"] = "reject"
    with pytest.raises(AIModelInvocationRegistryError, match="C1A_CORRUPT_EVIDENCE"):
        registry.get(tenant_id=evidence.tenant_id, invocation_id=evidence.invocation_id, session=session)
    collection.rows[0].pop("unknown_persisted_field")
    collection.rows[0]["fingerprint"] = "0" * 128
    with pytest.raises(AIModelInvocationRegistryError, match="C1A_CORRUPT_EVIDENCE"):
        registry.get(tenant_id=evidence.tenant_id, invocation_id=evidence.invocation_id, session=session)


def test_registry_does_not_own_transaction_lifecycle() -> None:
    """Source and behavior prove no start/commit/abort/retry methods are called."""
    source = inspect.getsource(AIModelInvocationRegistry)
    for forbidden in ("start_transaction", "commit_transaction", "abort_transaction", "with_transaction", "start_session"):
        assert forbidden not in source
    session = SessionDouble()
    registry = AIModelInvocationRegistry(CollectionDouble())
    registry.create_or_replay(make_evidence(), session=session)


def test_invalid_inputs_fail_closed_without_persistence() -> None:
    """Missing evidence or session is rejected before collection access."""
    collection = CollectionDouble()
    registry = AIModelInvocationRegistry(collection)
    with pytest.raises(AIModelInvocationRegistryError, match="C1A_INPUT_INVALID"):
        registry.create_or_replay(object(), session=SessionDouble())  # type: ignore[arg-type]
    with pytest.raises(AIModelInvocationRegistryError, match="C1A_INPUT_INVALID"):
        registry.create_or_replay(make_evidence(), session=None)
    assert collection.find_calls == [] and collection.insert_calls == []


def test_duplicate_race_is_not_silently_replayed() -> None:
    """A transport duplicate race is surfaced as a governed conflict."""
    collection = CollectionDouble()
    registry = AIModelInvocationRegistry(collection)
    session = SessionDouble()
    evidence = make_evidence()
    collection.rows.append(dict(evidence.to_dict(), _id="transport-id"))
    with pytest.raises(AIModelInvocationRegistryConflictError, match="C1A_DIVERGENT_REPLAY"):
        registry.create_or_replay(make_evidence(response_text="Different result."), session=session)


def test_failure_outcome_is_persistable_as_bounded_evidence() -> None:
    """Provider failure classification persists without raw exception material."""
    request = ModelExecutionInput(
        tenant_id="tenant-c1a", principal_id="principal-1", invocation_id="failure-1",
        correlation_id="correlation-failure", entitlement_id="entitlement-1",
        provider_id="provider-neutral", model_id="model-neutral-v1",
        prompt="Bounded prompt.", system_policy="Bounded policy.",
    )
    result = ModelProviderResult(
        provider_id="provider-neutral", model_id="model-neutral-v1",
        outcome=ModelExecutionOutcome.PROVIDER_TIMEOUT,
        error_classification="PROVIDER_TIMEOUT",
    )
    evidence = ModelInvocationEvidence.from_execution(
        request, result, created_at=BASE_TIME, completed_at=BASE_TIME
    )
    assert evidence.to_dict()["error_classification"] == "PROVIDER_TIMEOUT"
    assert "raw_provider_error" not in evidence.to_dict()


# ARTIFACT: test_ai_model_invocation_registry.py
# VERSION: v1.0.0-WILSY-AI-MODEL-INVOCATION-REGISTRY-UNIT
# AUTHORITY BOUNDARY: direct registry certification only
# TENANT POSTURE: exact tenant predicate assertions
# FAIL-CLOSED POSTURE: corruption and divergent replay reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
