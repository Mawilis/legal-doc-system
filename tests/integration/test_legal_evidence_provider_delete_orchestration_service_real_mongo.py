"""Real-Mongo orchestration certificate for Legal Evidence provider deletion.

TITLE: Legal Evidence Provider Delete Orchestration Real-Mongo Certificate
VERSION: v1.1.0-L10A2R-A3-P4-P6D6-PROVIDER-DELETE-ORCHESTRATION-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME:
    Certify the complete provider-delete orchestration boundary across genuine
    cleanup authorization, genuine cleanup command, five real Mongo registries,
    a deterministic provider adapter, execution-fence concurrency, durable
    restart replay and unknown-commit fresh readback.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_evidence_provider_delete_orchestration_service_real_mongo.py
COLLABORATION / OWNERSHIP:
    Python EOS Legal Operations / Legal Evidence.
CERTIFICATION / UPDATE DATE: 2026-10-03
CHANGELOG:
    v1.1.0-L10A2R-A3-P4-P6D6-PROVIDER-DELETE-ORCHESTRATION-REAL-MONGO-CERT
    adds explicit real-Mongo certificates for evidence/uncertainty coexistence,
    divergent and failed unknown-commit readback, post-provider evidence
    persistence failure, and nested uncertainty-persistence failure.
    v1.0.0 establishes the P6D6 end-to-end real-Mongo certificate.
COMPLIANCE:
    WILSY OS Sovereign Governance Contract v1.2.0; real Mongo durability,
    exact tenant isolation, deterministic concurrency and fail-closed evidence.
SECURITY / PRIVACY POSTURE:
    Every durable lookup and write is exact tenant scoped. No external provider
    credential or provider network call is used.
TENANT BOUNDARY:
    Authorization, command, claim, execution evidence and uncertainty remain
    exact tenant-scoped durable truth.
AUTHORITY BOUNDARY:
    Seeds upstream authority only through certified domain factories and tests
    orchestration consumption. This certificate grants no cleanup authority,
    retry authority, reconciliation execution authority or physical-absence truth.
FINANCIAL AUTHORITY BOUNDARY:
    No billing, payment, settlement or financial execution authority.
    Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from threading import Event, Lock, Thread
from typing import Any, Callable
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.client_session import ClientSession

import tests.unit.test_legal_evidence_provider_cleanup_authorization as auth_cert
import tests.unit.test_legal_evidence_provider_cleanup_command as command_cert
from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_uncertainty import (
    open_legal_evidence_provider_delete_execution_uncertainty,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_cleanup_authorization_registry import (
    COLLECTION as AUTH_COLLECTION,
    LegalEvidenceProviderCleanupAuthorizationRegistry,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_cleanup_command_registry import (
    COLLECTION as COMMAND_COLLECTION,
    LegalEvidenceProviderCleanupCommandRegistry,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_delete_execution_claim_registry import (
    COLLECTION as CLAIM_COLLECTION,
    LegalEvidenceProviderDeleteExecutionClaimRegistry,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_delete_execution_evidence_registry import (
    COLLECTION as EVIDENCE_COLLECTION,
    LegalEvidenceProviderDeleteExecutionEvidenceRegistry,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_delete_execution_uncertainty_registry import (
    COLLECTION as UNCERTAINTY_COLLECTION,
    LegalEvidenceProviderDeleteExecutionUncertaintyRegistry,
)
from tools.eos.legal_operations.service.legal_evidence_provider_delete_orchestration_service import (
    VERSION as SERVICE_VERSION,
    LegalEvidenceProviderDeleteOrchestrationError,
    LegalEvidenceProviderDeleteOrchestrationService,
)
from tools.eos.legal_operations.service.legal_evidence_s3_provider_delete_adapter import (
    LegalEvidenceS3ProviderDeleteExecutionEvidence,
)


URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS&directConnection=true"
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
EXPECTED_SERVICE_VERSION = (
    "v1.3.0-L10A2R-A3-P4-P6D5-"
    "PROVIDER-DELETE-ORCHESTRATION"
)
TENANT = auth_cert.TENANT
BASE_TIME = datetime(
    2026,
    10,
    2,
    22,
    0,
    0,
    tzinfo=timezone.utc,
)


class _Clock:
    """Deterministic monotonic UTC clock for one orchestration instance."""

    def __init__(self) -> None:
        self._index = 0

    def __call__(self) -> datetime:
        self._index += 1
        return BASE_TIME + timedelta(
            seconds=self._index
        )


class _FixedClock:
    """Return one fixed UTC value for deterministic competing claim identity."""

    def __call__(self) -> datetime:
        return BASE_TIME


class _Ids:
    """Deterministic per-service identity factory."""

    def __init__(
        self,
        suffix: str,
    ) -> None:
        self._suffix = suffix

    def __call__(
        self,
        kind: str,
    ) -> str:
        return f"{kind}-p6d6-{self._suffix}"


class _SessionTracker:
    """Thread-safe observation of genuine ClientSession transaction scope."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._active: set[int] = set()
        self._commit_count = 0

    def started(
        self,
        session: ClientSession,
    ) -> None:
        with self._lock:
            self._active.add(id(session))

    def closed(
        self,
        session: ClientSession,
    ) -> None:
        with self._lock:
            self._active.discard(id(session))

    def next_commit(self) -> int:
        with self._lock:
            self._commit_count += 1
            return self._commit_count

    def has_active_transaction(self) -> bool:
        with self._lock:
            return bool(self._active)


class _Provider:
    """Deterministic provider capability with no network or Mongo authority."""

    def __init__(
        self,
        tracker: _SessionTracker,
    ) -> None:
        self._tracker = tracker
        self.calls = 0
        self.requests: list[Any] = []

    def execute_delete(
        self,
        request: Any,
    ) -> LegalEvidenceS3ProviderDeleteExecutionEvidence:
        if self._tracker.has_active_transaction():
            raise AssertionError(
                "PROVIDER_CALLED_INSIDE_TRANSACTION"
            )

        self.calls += 1
        self.requests.append(request)

        return LegalEvidenceS3ProviderDeleteExecutionEvidence(
            provider_name=request.provider_name,
            storage_reference=request.storage_reference,
            object_version_reference=
                request.object_version_reference,
            delete_marker=None,
            delete_marker_version_reference=None,
        )


class _UnknownCommitError(RuntimeError):
    """Deterministic Mongo-compatible unknown commit acknowledgement."""

    def has_error_label(
        self,
        label: str,
    ) -> bool:
        return (
            label
            == "UnknownTransactionCommitResult"
        )


class _EvidenceRegistryFaultBoundary:
    """Bound one injected evidence-registry failure to certificate execution."""

    def __init__(
        self,
        delegate: Any,
        *,
        mode: str,
    ) -> None:
        self._delegate = delegate
        self._mode = mode
        self._expected: Any = None

    def __getattr__(self, name: str) -> Any:
        return getattr(self._delegate, name)

    def get_by_command_id(self, **kwargs: Any) -> Any:
        if self._expected is None:
            return self._delegate.get_by_command_id(**kwargs)
        if self._mode == "READBACK_FAILED":
            raise RuntimeError("certificate-readback-failure")
        if self._mode == "READBACK_DIVERGENT":
            return replace(
                self._expected,
                executed_at=(
                    self._expected.executed_at
                    + timedelta(microseconds=1)
                ),
                fingerprint="",
            )
        return self._delegate.get_by_command_id(**kwargs)

    def create_or_replay(self, value: Any, **kwargs: Any) -> Any:
        self._expected = value
        if self._mode == "PERSISTENCE_FAILED":
            raise RuntimeError("certificate-evidence-persistence-failure")
        return self._delegate.create_or_replay(value, **kwargs)


class _UncertaintyRegistryFaultBoundary:
    """Bound one uncertainty write failure while preserving genuine reads."""

    def __init__(self, delegate: Any) -> None:
        self._delegate = delegate

    def __getattr__(self, name: str) -> Any:
        return getattr(self._delegate, name)

    def create_or_replay(self, _value: Any, **_kwargs: Any) -> Any:
        raise RuntimeError("certificate-uncertainty-persistence-failure")


def _install_session_instrumentation(
    *,
    monkeypatch: pytest.MonkeyPatch,
    tracker: _SessionTracker,
    commit_outcome: str | None = None,
) -> None:
    """Instrument genuine ClientSession methods without replacing session type."""

    original_start = ClientSession.start_transaction
    original_commit = ClientSession.commit_transaction
    original_abort = ClientSession.abort_transaction

    def patched_start(
        session: ClientSession,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        result = original_start(
            session,
            *args,
            **kwargs,
        )
        tracker.started(session)
        return result

    def patched_commit(
        session: ClientSession,
    ) -> None:
        ordinal = tracker.next_commit()

        try:
            if (
                commit_outcome is not None
                and ordinal == 3
            ):
                if commit_outcome == "COMMITTED":
                    original_commit(session)
                elif commit_outcome == "ABSENT":
                    original_abort(session)
                else:
                    raise AssertionError(
                        commit_outcome
                    )

                raise _UnknownCommitError(
                    "unknown-commit-result"
                )

            original_commit(session)

        finally:
            tracker.closed(session)

    def patched_abort(
        session: ClientSession,
    ) -> None:
        try:
            original_abort(session)
        finally:
            tracker.closed(session)

    monkeypatch.setattr(
        ClientSession,
        "start_transaction",
        patched_start,
    )
    monkeypatch.setattr(
        ClientSession,
        "commit_transaction",
        patched_commit,
    )
    monkeypatch.setattr(
        ClientSession,
        "abort_transaction",
        patched_abort,
    )


class _SlowAfterPreflightService(
    LegalEvidenceProviderDeleteOrchestrationService
):
    """Pause one worker after stale preflight and before claim acquisition."""

    def __init__(
        self,
        *,
        preflight_done: Event,
        release: Event,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._preflight_done_event = preflight_done
        self._release_event = release

    def _preflight(
        self,
        *,
        tenant_id: str,
        command_id: str,
    ):
        result = super()._preflight(
            tenant_id=tenant_id,
            command_id=command_id,
        )
        self._preflight_done_event.set()

        if not self._release_event.wait(
            timeout=10,
        ):
            raise AssertionError(
                "P6D6_SLOW_WORKER_RELEASE_TIMEOUT"
            )

        return result


@pytest.fixture()
def mongo_context() -> Any:
    """Create one disposable real-Mongo database with all five registries."""

    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5_000,
        connectTimeoutMS=5_000,
        retryWrites=True,
    )

    hello = client.admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello["isWritablePrimary"] is True

    db_name = (
        "wilsy_p6d6_"
        + uuid4().hex[:20]
    )
    db = client[db_name]

    auth = (
        LegalEvidenceProviderCleanupAuthorizationRegistry(
            db[AUTH_COLLECTION]
        )
    )
    command = (
        LegalEvidenceProviderCleanupCommandRegistry(
            db[COMMAND_COLLECTION]
        )
    )
    claim = (
        LegalEvidenceProviderDeleteExecutionClaimRegistry(
            db[CLAIM_COLLECTION]
        )
    )
    evidence = (
        LegalEvidenceProviderDeleteExecutionEvidenceRegistry(
            db[EVIDENCE_COLLECTION]
        )
    )
    uncertainty = (
        LegalEvidenceProviderDeleteExecutionUncertaintyRegistry(
            db[UNCERTAINTY_COLLECTION]
        )
    )

    for registry in (
        auth,
        command,
        claim,
        evidence,
        uncertainty,
    ):
        registry.ensure_indexes()

    try:
        yield (
            client,
            db,
            auth,
            command,
            claim,
            evidence,
            uncertainty,
        )
    finally:
        client.drop_database(db_name)
        client.close()


def _seed_authority(
    *,
    client: MongoClient[Any],
    auth_registry: Any,
    command_registry: Any,
    suffix: str,
) -> tuple[Any, Any]:
    """Persist genuine certified cleanup authorization and command."""

    authorization = auth_cert._authorize(
        authorization_id=(
            f"cleanup-authorization-p6d6-{suffix}"
        ),
        authorized_at=auth_cert.AUTHORIZED_AT,
        reason_reference=(
            f"cleanup-authorization-reason-p6d6-{suffix}"
        ),
    )

    issued_at = max(
        command_cert.ISSUED_AT,
        authorization.authorized_at
        + timedelta(minutes=1),
    )

    command = command_cert._issue(
        cleanup=authorization,
        command_id=(
            f"cleanup-command-p6d6-{suffix}"
        ),
        issued_at=issued_at,
        reason_reference=(
            f"cleanup-command-reason-p6d6-{suffix}"
        ),
    )

    with client.start_session() as session:
        session.start_transaction()

        auth_registry.create_or_replay(
            authorization,
            session=session,
        )
        command_registry.create_or_replay(
            command,
            session=session,
        )

        session.commit_transaction()

    return authorization, command


def _service(
    *,
    client: Any,
    command_registry: Any,
    auth_registry: Any,
    claim_registry: Any,
    evidence_registry: Any,
    uncertainty_registry: Any,
    provider: Any,
    suffix: str,
    clock: Callable[[], datetime] | None = None,
) -> LegalEvidenceProviderDeleteOrchestrationService:
    """Construct the production service against five real durable registries."""

    return LegalEvidenceProviderDeleteOrchestrationService(
        client=client,
        command_registry=command_registry,
        cleanup_authorization_registry=
            auth_registry,
        claim_registry=claim_registry,
        execution_evidence_registry=
            evidence_registry,
        uncertainty_registry=
            uncertainty_registry,
        provider_adapter=provider,
        clock=clock or _Clock(),
        id_factory=_Ids(suffix),
    )


def _count(
    db: Any,
    collection: str,
    *,
    command_id: str,
) -> int:
    return db[collection].count_documents(
        {"command_id": command_id}
    )


def test_version_and_real_mongo_topology(
    mongo_context: Any,
) -> None:
    client, _, *_ = mongo_context
    hello = client.admin.command("hello")

    assert SERVICE_VERSION == EXPECTED_SERVICE_VERSION
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello["isWritablePrimary"] is True


def test_real_happy_path_claim_before_provider_and_restart_replay(
    mongo_context: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        client,
        db,
        auth,
        command_registry,
        claim,
        evidence,
        uncertainty,
    ) = mongo_context

    _, command = _seed_authority(
        client=client,
        auth_registry=auth,
        command_registry=command_registry,
        suffix="happy",
    )

    tracker = _SessionTracker()
    _install_session_instrumentation(
        monkeypatch=monkeypatch,
        tracker=tracker,
    )
    provider = _Provider(tracker)

    service = _service(
        client=client,
        command_registry=command_registry,
        auth_registry=auth,
        claim_registry=claim,
        evidence_registry=evidence,
        uncertainty_registry=uncertainty,
        provider=provider,
        suffix="happy",
    )

    result = service.execute(
        tenant_id=command.tenant_id,
        command_id=command.command_id,
    )

    assert provider.calls == 1
    assert result.command_id == command.command_id
    assert _count(
        db,
        CLAIM_COLLECTION,
        command_id=command.command_id,
    ) == 1
    assert _count(
        db,
        EVIDENCE_COLLECTION,
        command_id=command.command_id,
    ) == 1
    assert _count(
        db,
        UNCERTAINTY_COLLECTION,
        command_id=command.command_id,
    ) == 0

    # Restart the service/registries over the same committed Mongo state.
    restarted_provider = _Provider(tracker)
    restarted = _service(
        client=client,
        command_registry=(
            LegalEvidenceProviderCleanupCommandRegistry(
                db[COMMAND_COLLECTION]
            )
        ),
        auth_registry=(
            LegalEvidenceProviderCleanupAuthorizationRegistry(
                db[AUTH_COLLECTION]
            )
        ),
        claim_registry=(
            LegalEvidenceProviderDeleteExecutionClaimRegistry(
                db[CLAIM_COLLECTION]
            )
        ),
        evidence_registry=(
            LegalEvidenceProviderDeleteExecutionEvidenceRegistry(
                db[EVIDENCE_COLLECTION]
            )
        ),
        uncertainty_registry=(
            LegalEvidenceProviderDeleteExecutionUncertaintyRegistry(
                db[UNCERTAINTY_COLLECTION]
            )
        ),
        provider=restarted_provider,
        suffix="restart",
    )

    replay = restarted.execute(
        tenant_id=command.tenant_id,
        command_id=command.command_id,
    )

    assert replay == result
    assert restarted_provider.calls == 0


def test_real_provider_failure_leaves_claim_and_blocks_retry(
    mongo_context: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        client,
        db,
        auth,
        command_registry,
        claim,
        evidence,
        uncertainty,
    ) = mongo_context

    _, command = _seed_authority(
        client=client,
        auth_registry=auth,
        command_registry=command_registry,
        suffix="provider-failure",
    )

    tracker = _SessionTracker()
    _install_session_instrumentation(
        monkeypatch=monkeypatch,
        tracker=tracker,
    )

    class _FailingProvider(_Provider):
        def execute_delete(self, request: Any) -> Any:
            super().execute_delete(request)
            raise RuntimeError("provider-failure")

    provider = _FailingProvider(tracker)

    service = _service(
        client=client,
        command_registry=command_registry,
        auth_registry=auth,
        claim_registry=claim,
        evidence_registry=evidence,
        uncertainty_registry=uncertainty,
        provider=provider,
        suffix="provider-failure",
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match=(
            "PROVIDER_EXECUTION_FAILED_"
            "RECONCILIATION_REQUIRED"
        ),
    ):
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert provider.calls == 1
    assert _count(
        db,
        CLAIM_COLLECTION,
        command_id=command.command_id,
    ) == 1
    assert _count(
        db,
        EVIDENCE_COLLECTION,
        command_id=command.command_id,
    ) == 0
    assert _count(
        db,
        UNCERTAINTY_COLLECTION,
        command_id=command.command_id,
    ) == 0

    second_provider = _Provider(tracker)
    second = _service(
        client=client,
        command_registry=command_registry,
        auth_registry=auth,
        claim_registry=claim,
        evidence_registry=evidence,
        uncertainty_registry=uncertainty,
        provider=second_provider,
        suffix="provider-failure-second",
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="PREEXISTING_CLAIM_REQUIRES_RECONCILIATION",
    ):
        second.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert second_provider.calls == 0


def test_real_stale_preflight_concurrency_allows_one_provider_call(
    mongo_context: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        client,
        db,
        auth,
        command_registry,
        claim,
        evidence,
        uncertainty,
    ) = mongo_context

    _, command = _seed_authority(
        client=client,
        auth_registry=auth,
        command_registry=command_registry,
        suffix="race",
    )

    tracker = _SessionTracker()
    _install_session_instrumentation(
        monkeypatch=monkeypatch,
        tracker=tracker,
    )
    provider = _Provider(tracker)

    preflight_done = Event()
    release = Event()

    shared_ids = _Ids("race-shared")
    fixed_clock = _FixedClock()

    slow = _SlowAfterPreflightService(
        preflight_done=preflight_done,
        release=release,
        client=client,
        command_registry=command_registry,
        cleanup_authorization_registry=auth,
        claim_registry=claim,
        execution_evidence_registry=evidence,
        uncertainty_registry=uncertainty,
        provider_adapter=provider,
        clock=fixed_clock,
        id_factory=shared_ids,
    )

    fast = LegalEvidenceProviderDeleteOrchestrationService(
        client=client,
        command_registry=command_registry,
        cleanup_authorization_registry=auth,
        claim_registry=claim,
        execution_evidence_registry=evidence,
        uncertainty_registry=uncertainty,
        provider_adapter=provider,
        clock=fixed_clock,
        id_factory=shared_ids,
    )

    slow_result: list[Any] = []
    fast_result: list[Any] = []

    def run_slow() -> None:
        try:
            slow_result.append(
                slow.execute(
                    tenant_id=command.tenant_id,
                    command_id=command.command_id,
                )
            )
        except Exception as error:
            slow_result.append(error)

    def run_fast() -> None:
        try:
            fast_result.append(
                fast.execute(
                    tenant_id=command.tenant_id,
                    command_id=command.command_id,
                )
            )
        except Exception as error:
            fast_result.append(error)

    slow_thread = Thread(
        target=run_slow,
        daemon=True,
    )
    slow_thread.start()

    assert preflight_done.wait(timeout=10)

    fast_thread = Thread(
        target=run_fast,
        daemon=True,
    )
    fast_thread.start()
    fast_thread.join(timeout=10)

    assert not fast_thread.is_alive()
    assert len(fast_result) == 1
    assert not isinstance(
        fast_result[0],
        Exception,
    )
    assert provider.calls == 1

    release.set()
    slow_thread.join(timeout=10)

    assert not slow_thread.is_alive()
    assert len(slow_result) == 1
    assert isinstance(
        slow_result[0],
        LegalEvidenceProviderDeleteOrchestrationError,
    )
    assert (
        slow_result[0].code
        == (
            "L10A2R_A3_P4_P6D5_"
            "CLAIM_FENCE_NOT_ACQUIRED"
        )
    )
    assert (
        slow_result[0].reconciliation_required
        is True
    )

    assert provider.calls == 1
    assert _count(
        db,
        CLAIM_COLLECTION,
        command_id=command.command_id,
    ) == 1
    assert _count(
        db,
        EVIDENCE_COLLECTION,
        command_id=command.command_id,
    ) == 1
    assert _count(
        db,
        UNCERTAINTY_COLLECTION,
        command_id=command.command_id,
    ) == 0


def test_real_unknown_commit_exact_readback_reconciles_without_uncertainty(
    mongo_context: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        client,
        db,
        auth,
        command_registry,
        claim,
        evidence,
        uncertainty,
    ) = mongo_context

    _, command = _seed_authority(
        client=client,
        auth_registry=auth,
        command_registry=command_registry,
        suffix="unknown-exact",
    )

    tracker = _SessionTracker()
    _install_session_instrumentation(
        monkeypatch=monkeypatch,
        tracker=tracker,
        commit_outcome="COMMITTED",
    )
    provider = _Provider(tracker)

    service = _service(
        client=client,
        command_registry=command_registry,
        auth_registry=auth,
        claim_registry=claim,
        evidence_registry=evidence,
        uncertainty_registry=uncertainty,
        provider=provider,
        suffix="unknown-exact",
    )

    result = service.execute(
        tenant_id=command.tenant_id,
        command_id=command.command_id,
    )

    assert provider.calls == 1
    assert result.command_id == command.command_id
    assert _count(
        db,
        EVIDENCE_COLLECTION,
        command_id=command.command_id,
    ) == 1
    assert _count(
        db,
        UNCERTAINTY_COLLECTION,
        command_id=command.command_id,
    ) == 0


def test_real_unknown_commit_absent_records_uncertainty_after_readback(
    mongo_context: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        client,
        db,
        auth,
        command_registry,
        claim,
        evidence,
        uncertainty,
    ) = mongo_context

    _, command = _seed_authority(
        client=client,
        auth_registry=auth,
        command_registry=command_registry,
        suffix="unknown-absent",
    )

    tracker = _SessionTracker()
    _install_session_instrumentation(
        monkeypatch=monkeypatch,
        tracker=tracker,
        commit_outcome="ABSENT",
    )
    provider = _Provider(tracker)

    service = _service(
        client=client,
        command_registry=command_registry,
        auth_registry=auth,
        claim_registry=claim,
        evidence_registry=evidence,
        uncertainty_registry=uncertainty,
        provider=provider,
        suffix="unknown-absent",
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="UNKNOWN_COMMIT_READBACK_ABSENT",
    ) as captured:
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert captured.value.reconciliation_required is True
    assert provider.calls == 1
    assert _count(
        db,
        EVIDENCE_COLLECTION,
        command_id=command.command_id,
    ) == 0
    assert _count(
        db,
        UNCERTAINTY_COLLECTION,
        command_id=command.command_id,
    ) == 1


def test_real_evidence_uncertainty_coexistence_fails_closed(
    mongo_context: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        client,
        db,
        auth,
        command_registry,
        claim,
        evidence,
        uncertainty,
    ) = mongo_context
    _, command = _seed_authority(
        client=client,
        auth_registry=auth,
        command_registry=command_registry,
        suffix="coexistence",
    )
    tracker = _SessionTracker()
    _install_session_instrumentation(
        monkeypatch=monkeypatch,
        tracker=tracker,
    )
    initial_provider = _Provider(tracker)
    execution_evidence = _service(
        client=client,
        command_registry=command_registry,
        auth_registry=auth,
        claim_registry=claim,
        evidence_registry=evidence,
        uncertainty_registry=uncertainty,
        provider=initial_provider,
        suffix="coexistence-initial",
    ).execute(
        tenant_id=command.tenant_id,
        command_id=command.command_id,
    )
    unresolved = open_legal_evidence_provider_delete_execution_uncertainty(
        uncertainty_id="uncertainty-p6d6-coexistence",
        command=command,
        execution_evidence=execution_evidence,
        uncertainty_recorded_at=(
            execution_evidence.executed_at
            + timedelta(seconds=1)
        ),
    )
    with client.start_session() as session:
        session.start_transaction()
        uncertainty.create_or_replay(unresolved, session=session)
        session.commit_transaction()

    restarted_provider = _Provider(tracker)
    restarted = _service(
        client=client,
        command_registry=command_registry,
        auth_registry=auth,
        claim_registry=claim,
        evidence_registry=evidence,
        uncertainty_registry=uncertainty,
        provider=restarted_provider,
        suffix="coexistence-restart",
    )
    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="RECONCILIATION_REQUIRED",
    ) as captured:
        restarted.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert captured.value.reconciliation_required is True
    assert initial_provider.calls == 1
    assert restarted_provider.calls == 0
    assert _count(db, EVIDENCE_COLLECTION, command_id=command.command_id) == 1
    assert _count(db, UNCERTAINTY_COLLECTION, command_id=command.command_id) == 1


def _assert_real_unknown_commit_readback_classification_fails_closed(
    mongo_context: Any,
    monkeypatch: pytest.MonkeyPatch,
    *,
    mode: str,
    expected_code: str,
) -> None:
    (
        client,
        db,
        auth,
        command_registry,
        claim,
        evidence,
        uncertainty,
    ) = mongo_context
    _, command = _seed_authority(
        client=client,
        auth_registry=auth,
        command_registry=command_registry,
        suffix=mode.casefold(),
    )
    tracker = _SessionTracker()
    _install_session_instrumentation(
        monkeypatch=monkeypatch,
        tracker=tracker,
        commit_outcome="COMMITTED",
    )
    provider = _Provider(tracker)
    bounded_evidence = _EvidenceRegistryFaultBoundary(
        evidence,
        mode=mode,
    )
    service = _service(
        client=client,
        command_registry=command_registry,
        auth_registry=auth,
        claim_registry=claim,
        evidence_registry=bounded_evidence,
        uncertainty_registry=uncertainty,
        provider=provider,
        suffix=mode.casefold(),
    )
    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match=expected_code,
    ) as captured:
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert captured.value.reconciliation_required is True
    assert provider.calls == 1
    assert _count(db, CLAIM_COLLECTION, command_id=command.command_id) == 1
    assert _count(db, UNCERTAINTY_COLLECTION, command_id=command.command_id) == 0


def test_real_unknown_commit_divergent_readback_fails_closed(
    mongo_context: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _assert_real_unknown_commit_readback_classification_fails_closed(
        mongo_context,
        monkeypatch,
        mode="READBACK_DIVERGENT",
        expected_code="UNKNOWN_COMMIT_READBACK_DIVERGENT",
    )


def test_real_unknown_commit_readback_failure_fails_closed(
    mongo_context: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _assert_real_unknown_commit_readback_classification_fails_closed(
        mongo_context,
        monkeypatch,
        mode="READBACK_FAILED",
        expected_code="UNKNOWN_COMMIT_READBACK_FAILED",
    )


def test_real_post_provider_persistence_failure_records_uncertainty(
    mongo_context: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        client,
        db,
        auth,
        command_registry,
        claim,
        evidence,
        uncertainty,
    ) = mongo_context
    _, command = _seed_authority(
        client=client,
        auth_registry=auth,
        command_registry=command_registry,
        suffix="persistence-failure",
    )
    tracker = _SessionTracker()
    _install_session_instrumentation(monkeypatch=monkeypatch, tracker=tracker)
    provider = _Provider(tracker)
    service = _service(
        client=client,
        command_registry=command_registry,
        auth_registry=auth,
        claim_registry=claim,
        evidence_registry=_EvidenceRegistryFaultBoundary(
            evidence,
            mode="PERSISTENCE_FAILED",
        ),
        uncertainty_registry=uncertainty,
        provider=provider,
        suffix="persistence-failure",
    )
    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="POST_PROVIDER_PERSISTENCE_UNCERTAIN",
    ) as captured:
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert captured.value.reconciliation_required is True
    assert provider.calls == 1
    assert _count(db, CLAIM_COLLECTION, command_id=command.command_id) == 1
    assert _count(db, EVIDENCE_COLLECTION, command_id=command.command_id) == 0
    assert _count(db, UNCERTAINTY_COLLECTION, command_id=command.command_id) == 1


def test_real_uncertainty_persistence_failure_fails_closed(
    mongo_context: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        client,
        db,
        auth,
        command_registry,
        claim,
        evidence,
        uncertainty,
    ) = mongo_context
    _, command = _seed_authority(
        client=client,
        auth_registry=auth,
        command_registry=command_registry,
        suffix="uncertainty-failure",
    )
    tracker = _SessionTracker()
    _install_session_instrumentation(monkeypatch=monkeypatch, tracker=tracker)
    provider = _Provider(tracker)
    service = _service(
        client=client,
        command_registry=command_registry,
        auth_registry=auth,
        claim_registry=claim,
        evidence_registry=_EvidenceRegistryFaultBoundary(
            evidence,
            mode="PERSISTENCE_FAILED",
        ),
        uncertainty_registry=_UncertaintyRegistryFaultBoundary(uncertainty),
        provider=provider,
        suffix="uncertainty-failure",
    )
    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="UNCERTAINTY_PERSISTENCE_FAILED",
    ) as captured:
        service.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )

    assert captured.value.reconciliation_required is True
    assert provider.calls == 1
    assert _count(db, CLAIM_COLLECTION, command_id=command.command_id) == 1
    assert _count(db, EVIDENCE_COLLECTION, command_id=command.command_id) == 0
    assert _count(db, UNCERTAINTY_COLLECTION, command_id=command.command_id) == 0

    restarted_provider = _Provider(tracker)
    restarted = _service(
        client=client,
        command_registry=command_registry,
        auth_registry=auth,
        claim_registry=claim,
        evidence_registry=evidence,
        uncertainty_registry=uncertainty,
        provider=restarted_provider,
        suffix="uncertainty-failure-restart",
    )
    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="PREEXISTING_CLAIM_REQUIRES_RECONCILIATION",
    ):
        restarted.execute(
            tenant_id=command.tenant_id,
            command_id=command.command_id,
        )
    assert restarted_provider.calls == 0


def test_real_cross_tenant_request_is_absent_and_never_calls_provider(
    mongo_context: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (
        client,
        _db,
        auth,
        command_registry,
        claim,
        evidence,
        uncertainty,
    ) = mongo_context

    _, command = _seed_authority(
        client=client,
        auth_registry=auth,
        command_registry=command_registry,
        suffix="tenant",
    )

    tracker = _SessionTracker()
    _install_session_instrumentation(
        monkeypatch=monkeypatch,
        tracker=tracker,
    )
    provider = _Provider(tracker)

    service = _service(
        client=client,
        command_registry=command_registry,
        auth_registry=auth,
        claim_registry=claim,
        evidence_registry=evidence,
        uncertainty_registry=uncertainty,
        provider=provider,
        suffix="tenant",
    )

    with pytest.raises(
        LegalEvidenceProviderDeleteOrchestrationError,
        match="COMMAND_NOT_FOUND",
    ):
        service.execute(
            tenant_id=f"{command.tenant_id}-other",
            command_id=command.command_id,
        )

    assert provider.calls == 0


def test_certificate_has_no_retry_release_or_physical_absence_authority() -> None:
    """Certificate must not enlarge provider or reconciliation authority."""

    public = {
        name
        for name in dir(
            LegalEvidenceProviderDeleteOrchestrationService
        )
        if not name.startswith("_")
    }

    assert {
        "retry",
        "retry_delete",
        "release_claim",
        "prove_absence",
        "reconcile",
    }.isdisjoint(public)


# ARTIFACT: test_legal_evidence_provider_delete_orchestration_service_real_mongo.py
# VERSION: v1.1.0-L10A2R-A3-P4-P6D6-PROVIDER-DELETE-ORCHESTRATION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: consumes certified cleanup authorization/command; no provider retry, reconciliation execution, lifecycle, IAM, billing, payment, settlement or financial authority
# TENANT POSTURE: exact tenant-scoped authorization, command, claim, execution-evidence and uncertainty durability
# TRANSACTION POSTURE: provider execution is outside Mongo transaction scope; durable phases use separate transactions; unknown evidence commit uses fresh readback
# FAIL-CLOSED POSTURE: claims, ambiguity, divergence and tenant mismatch block automatic provider re-execution
# PROVIDER POSTURE: deterministic fake provider only; no live AWS request and no physical-absence inference
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
