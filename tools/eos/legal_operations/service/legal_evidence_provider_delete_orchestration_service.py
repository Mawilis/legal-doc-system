"""WILSY OS — Legal Evidence Provider Delete Orchestration Service.

TITLE: Legal Evidence Provider Delete Orchestration Service
VERSION: v1.3.0-L10A2R-A3-P4-P6D5-PROVIDER-DELETE-ORCHESTRATION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME:
    Fail-closed tenant-scoped orchestration of one already-authorized provider
    delete through a durable pre-provider claim, provider execution outside
    Mongo transaction scope, immutable execution evidence, and durable
    uncertainty whenever post-provider persistence cannot be certified.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_provider_delete_orchestration_service.py
COLLABORATION / OWNERSHIP:
    Python EOS Legal Operations owns orchestration truth. Provider adapters own
    external capability only; Mongo registries own durable evidence only.
CERTIFICATION OR UPDATE DATE: 2026-10-03
CHANGELOG:
    v1.3.0-L10A2R-A3-P4-P6D5-PROVIDER-DELETE-ORCHESTRATION
    - Requires the exact certified
      LegalEvidenceS3ProviderDeleteExecutionEvidence result type immediately
      after provider I/O and before canonical durable execution-evidence
      construction.
    - Duck-typed, forged, or otherwise uncertified provider results fail closed
      with reconciliation required; the already-durable pre-provider claim
      survives, no execution evidence is written, no uncertainty is fabricated,
      and no retry authority is granted.
    - Preserves provider call count, transaction boundaries, tenant binding,
      claim-fence semantics, unknown-commit reconciliation, no-retry posture,
      persisted schemas, public service API, and Kennel financial boundary.
    v1.2.0-L10A2R-A3-P4-P6D5-PROVIDER-DELETE-ORCHESTRATION
    - Distinguishes Mongo UnknownTransactionCommitResult from ordinary
      post-provider execution-evidence persistence failure.
    - Performs a fresh tenant-scoped transactional execution-evidence
      readback before any uncertainty write after an ambiguous commit.
    - Exact durable evidence reconciles success; absence permits bounded
      uncertainty only after readback; divergent or unreadable durable
      state fails closed without fabricated provider success.
    - Preserves v1.1.0 claim-fence ownership, no provider retry, persisted
      schemas, tenant boundary and Kennel financial authority boundary.
    v1.1.0-L10A2R-A3-P4-P6D5-PROVIDER-DELETE-ORCHESTRATION
    - Repairs provider-delete execution-fence ownership under concurrent
      stale-preflight exact-claim replay. A fresh claim read now occurs
      inside the claim transaction immediately before insertion; any
      already-durable claim blocks provider execution for that invocation.
    - Preserves claim registry schema/API, tenant scope, provider adapter,
      execution-evidence schema, uncertainty schema, and no-retry posture.
    v1.1.0-L10A2R-A3-P4-P6D5-PROVIDER-DELETE-ORCHESTRATION
    - Sovereign structural certification of the previously runtime-certified
      P6D5 orchestration.
    - Added complete institutional header, public API authority documentation,
      and mandatory sovereign end seal.
    - Runtime control flow, tenant binding, transaction ordering, provider-call
      ordering, retry posture, and evidence semantics intentionally unchanged.
COMPLIANCE:
    WILSY OS Sovereign Governance Contract v1.2.0; fail-closed evidence,
    transaction, idempotency, tenant-isolation, and certification posture.
SECURITY / PRIVACY POSTURE:
    Exact tenant-scoped durable reads/writes; provider I/O outside Mongo
    transactions; surviving claims/uncertainty block automatic re-execution;
    no physical-absence inference from provider acceptance.
TENANT BOUNDARY:
    All command, authorization, claim, execution-evidence and uncertainty
    persistence remains explicitly tenant scoped; cross-tenant inference is
    prohibited.
AUTHORITY BOUNDARY:
    Consumes certified cleanup command and authorization evidence. The service
    does not create cleanup authority, retry authority, reconciliation
    authority, lifecycle authority, IAM authority, or physical-absence truth.
FINANCIAL AUTHORITY BOUNDARY:
    No billing, payment, settlement, or financial execution authority.
    Kennel EOS remains the exclusive financial execution authority.

ORDERING CONTRACT:
    1. Read exact durable command and cleanup authorization.
    2. Reject unresolved uncertainty.
    3. Return exact durable execution evidence without provider re-execution.
    4. Reject surviving claim without execution evidence.
    5. Acquire a fresh immutable pre-provider execution claim; any
       already-durable claim proves this invocation does not own the fence.
    6. Leave Mongo transaction scope.
    7. Execute provider delete exactly once.
    8. Construct immutable execution evidence.
    9. Persist execution evidence in a fresh Mongo transaction.
   10. Unknown commit acknowledgement requires fresh transactional readback.
   11. Exact durable evidence reconciles success; absence may record
       uncertainty only after readback; divergence fails closed.

SEMANTIC LOCKS:
    CLAIM != PROVIDER EXECUTED.
    PROVIDER EXECUTED != PHYSICAL ABSENCE.
    PROVIDER EXECUTED != SETTLED.
    UNCERTAINTY != RETRY AUTHORIZATION.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Final, NoReturn

from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_command import (
    LegalEvidenceProviderCleanupCommand,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_claim import (
    open_legal_evidence_provider_delete_execution_claim,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_evidence import (
    LegalEvidenceProviderDeleteExecutionEvidence,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_uncertainty import (
    open_legal_evidence_provider_delete_execution_uncertainty,
)
from tools.eos.legal_operations.service.legal_evidence_provider_delete_execution_port import (
    LegalEvidenceProviderDeleteExecutionRequest,
)

from tools.eos.legal_operations.service.legal_evidence_s3_provider_delete_adapter import (
    LegalEvidenceS3ProviderDeleteExecutionEvidence,
)


VERSION: Final[str] = (
    "v1.3.0-L10A2R-A3-P4-P6D5-"
    "PROVIDER-DELETE-ORCHESTRATION"
)

UNKNOWN_TRANSACTION_COMMIT_RESULT: Final[str] = (
    "UnknownTransactionCommitResult"
)


def _has_error_label(
    error: BaseException,
    label: str,
) -> bool:
    """Inspect bounded causal driver state without exposing provider text."""
    current: BaseException | None = error
    visited: set[int] = set()

    for _ in range(8):
        if current is None or id(current) in visited:
            return False

        visited.add(id(current))

        checker = getattr(
            current,
            "has_error_label",
            None,
        )

        if callable(checker):
            try:
                if bool(checker(label)):
                    return True
            except Exception:
                pass

        current = current.__cause__

    return False


class LegalEvidenceProviderDeleteOrchestrationError(RuntimeError):
    """Institutional fail-closed orchestration error.

    AUTHORITY:
        Carries bounded failure classification only. It grants no provider,
        cleanup, retry, reconciliation, absence, IAM, billing, payment,
        settlement, or financial execution authority.
    TENANT SCOPE:
        Does not disclose or infer cross-tenant state.
    MUTATION:
        None.
    IDEMPOTENCY:
        None; it represents one failed orchestration observation.
    TRANSACTION:
        Does not own Mongo sessions or transactions.
    FAIL-CLOSED:
        ``reconciliation_required`` is explicit and never implies success.
    FINANCIAL BOUNDARY:
        Kennel EOS remains the exclusive financial execution authority.
    """

    def __init__(
        self,
        code: str,
        *,
        reconciliation_required: bool = False,
    ) -> None:
        super().__init__(code)
        self.code = code
        self.reconciliation_required = reconciliation_required


def _fail(
    code: str,
    *,
    reconciliation_required: bool = False,
    cause: BaseException | None = None,
) -> NoReturn:
    error = LegalEvidenceProviderDeleteOrchestrationError(
        code,
        reconciliation_required=reconciliation_required,
    )
    if cause is None:
        raise error
    raise error from cause


def _utc(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        _fail("L10A2R_A3_P4_P6D5_CLOCK_INVALID")
    if value.utcoffset() is None:
        _fail("L10A2R_A3_P4_P6D5_CLOCK_INVALID")
    return value.astimezone(timezone.utc)


def _abort_if_active(session: Any) -> None:
    marker = getattr(session, "in_transaction", False)
    active = marker() if callable(marker) else bool(marker)
    if active:
        session.abort_transaction()


class LegalEvidenceProviderDeleteOrchestrationService:
    """Coordinate one tenant-scoped provider-delete execution boundary.

    AUTHORITY:
        Consumes existing cleanup command/authorization evidence and may invoke
        only the configured provider-delete adapter after this invocation
        acquires and commits a fresh durable execution claim. Exact replay
        of another invocation's claim is not execution-fence ownership.
        It creates no cleanup authority of its own.
    TENANT SCOPE:
        All command, authorization, claim, execution-evidence and uncertainty
        registry operations remain explicitly tenant scoped.
    MUTATION:
        Persists a pre-provider claim, then optionally execution evidence or
        uncertainty in separate caller-owned Mongo transactions.
    IDEMPOTENCY:
        Existing durable execution evidence is exact replay. Any already-
        durable claim, including an exact immutable replay, means this
        invocation did not acquire the execution fence and blocks another
        automatic provider call. Existing uncertainty also blocks execution.
    TRANSACTION:
        Provider I/O occurs only after the claim transaction has committed and
        outside every Mongo transaction. Evidence/uncertainty use fresh
        transactions.
    FAIL-CLOSED:
        Provider failure or post-provider persistence ambiguity never triggers
        an automatic provider retry and never proves physical absence.
    FINANCIAL BOUNDARY:
        This service has no billing, payment, settlement, or financial
        execution authority. Kennel EOS remains exclusive.
    """

    def __init__(
        self,
        *,
        client: Any,
        command_registry: Any,
        cleanup_authorization_registry: Any,
        claim_registry: Any,
        execution_evidence_registry: Any,
        uncertainty_registry: Any,
        provider_adapter: Any,
        clock: Callable[[], datetime],
        id_factory: Callable[[str], str],
    ) -> None:
        self._client = client
        self._command_registry = command_registry
        self._cleanup_authorization_registry = (
            cleanup_authorization_registry
        )
        self._claim_registry = claim_registry
        self._execution_evidence_registry = (
            execution_evidence_registry
        )
        self._uncertainty_registry = uncertainty_registry
        self._provider_adapter = provider_adapter
        self._clock = clock
        self._id_factory = id_factory

    @staticmethod
    def _request(
        command: LegalEvidenceProviderCleanupCommand,
    ) -> LegalEvidenceProviderDeleteExecutionRequest:
        return LegalEvidenceProviderDeleteExecutionRequest(
            command_id=command.command_id,
            command_fingerprint=command.fingerprint,
            tenant_id=command.tenant_id,
            provider_name=command.provider_name,
            storage_reference=command.storage_reference,
            object_version_reference=command.object_version_reference,
            cleanup_authorization_id=command.cleanup_authorization_id,
            cleanup_authorization_fingerprint=
                command.cleanup_authorization_fingerprint,
        )

    @staticmethod
    def _validate_authorization(
        command: LegalEvidenceProviderCleanupCommand,
        authorization: Any,
    ) -> None:
        checks = (
            ("tenant_id", command.tenant_id),
            (
                "authorization_id",
                command.cleanup_authorization_id,
            ),
            ("provider_name", command.provider_name),
            ("storage_reference", command.storage_reference),
            (
                "object_version_reference",
                command.object_version_reference,
            ),
            (
                "fingerprint",
                command.cleanup_authorization_fingerprint,
            ),
        )

        for name, expected in checks:
            if getattr(authorization, name, None) != expected:
                _fail(
                    "L10A2R_A3_P4_P6D5_"
                    "CLEANUP_AUTHORIZATION_MISMATCH"
                )

    def _preflight(
        self,
        *,
        tenant_id: str,
        command_id: str,
    ) -> tuple[
        LegalEvidenceProviderCleanupCommand,
        LegalEvidenceProviderDeleteExecutionEvidence | None,
    ]:
        with self._client.start_session() as session:
            session.start_transaction()
            try:
                command = self._command_registry.get_by_command_id(
                    tenant_id=tenant_id,
                    command_id=command_id,
                    session=session,
                )

                if command is None:
                    _fail(
                        "L10A2R_A3_P4_P6D5_COMMAND_NOT_FOUND"
                    )

                if (
                    type(command)
                    is not LegalEvidenceProviderCleanupCommand
                ):
                    _fail(
                        "L10A2R_A3_P4_P6D5_COMMAND_INVALID"
                    )

                authorization = (
                    self._cleanup_authorization_registry
                    .get_by_authorization_id(
                        tenant_id=tenant_id,
                        authorization_id=
                            command.cleanup_authorization_id,
                        session=session,
                    )
                )

                if authorization is None:
                    _fail(
                        "L10A2R_A3_P4_P6D5_"
                        "CLEANUP_AUTHORIZATION_NOT_FOUND"
                    )

                self._validate_authorization(
                    command,
                    authorization,
                )

                uncertainty = (
                    self._uncertainty_registry
                    .get_by_command_id(
                        tenant_id=tenant_id,
                        command_id=command_id,
                        session=session,
                    )
                )

                if uncertainty is not None:
                    _fail(
                        "L10A2R_A3_P4_P6D5_"
                        "RECONCILIATION_REQUIRED",
                        reconciliation_required=True,
                    )

                evidence = (
                    self._execution_evidence_registry
                    .get_by_command_id(
                        tenant_id=tenant_id,
                        command_id=command_id,
                        session=session,
                    )
                )

                if evidence is not None:
                    session.commit_transaction()
                    return command, evidence

                claim = self._claim_registry.get_by_command_id(
                    tenant_id=tenant_id,
                    command_id=command_id,
                    session=session,
                )

                if claim is not None:
                    _fail(
                        "L10A2R_A3_P4_P6D5_"
                        "PREEXISTING_CLAIM_REQUIRES_RECONCILIATION",
                        reconciliation_required=True,
                    )

                session.commit_transaction()
                return command, None

            except Exception:
                _abort_if_active(session)
                raise

    def _commit_claim(
        self,
        command: LegalEvidenceProviderCleanupCommand,
    ) -> None:
        claim = open_legal_evidence_provider_delete_execution_claim(
            claim_id=self._id_factory("claim"),
            command=command,
            claimed_at=_utc(self._clock()),
        )

        with self._client.start_session() as session:
            session.start_transaction()
            try:
                existing_claim = (
                    self._claim_registry.get_by_command_id(
                        tenant_id=command.tenant_id,
                        command_id=command.command_id,
                        session=session,
                    )
                )

                if existing_claim is not None:
                    _fail(
                        "L10A2R_A3_P4_P6D5_"
                        "CLAIM_FENCE_NOT_ACQUIRED",
                        reconciliation_required=True,
                    )

                self._claim_registry.create_or_replay(
                    claim,
                    session=session,
                )
                session.commit_transaction()
            except Exception as error:
                _abort_if_active(session)

                if (
                    isinstance(
                        error,
                        LegalEvidenceProviderDeleteOrchestrationError,
                    )
                    and error.code
                    == (
                        "L10A2R_A3_P4_P6D5_"
                        "CLAIM_FENCE_NOT_ACQUIRED"
                    )
                ):
                    raise

                _fail(
                    "L10A2R_A3_P4_P6D5_"
                    "CLAIM_PERSISTENCE_FAILED",
                    reconciliation_required=True,
                    cause=error,
                )

    def _fresh_execution_evidence_readback(
        self,
        *,
        expected: LegalEvidenceProviderDeleteExecutionEvidence,
    ) -> LegalEvidenceProviderDeleteExecutionEvidence | None:
        """Fresh-read execution evidence after unknown commit acknowledgement.

        AUTHORITY:
            Reconciles only the already-attempted execution-evidence commit.
            It grants no provider execution, retry or cleanup authority.
        TENANT SCOPE:
            Reads only ``expected.tenant_id`` and ``expected.command_id``.
        MUTATION:
            No durable mutation. The required fresh read transaction is aborted
            after the snapshot read rather than committed.
        IDEMPOTENCY:
            Only exact immutable execution evidence reconciles to success.
        TRANSACTION:
            Owns one fresh Mongo session and active read transaction because the
            execution-evidence registry requires transaction-bound lookups.
        FAIL-CLOSED:
            Read failure or durable divergence never becomes execution success
            and never creates uncertainty before classification completes.
        FINANCIAL BOUNDARY:
            No billing, payment, settlement or financial execution authority.
        """
        try:
            with self._client.start_session() as session:
                session.start_transaction()
                try:
                    observed = (
                        self._execution_evidence_registry
                        .get_by_command_id(
                            tenant_id=expected.tenant_id,
                            command_id=expected.command_id,
                            session=session,
                        )
                    )
                except Exception:
                    _abort_if_active(session)
                    raise

                _abort_if_active(session)

        except Exception as error:
            _fail(
                "L10A2R_A3_P4_P6D5_"
                "UNKNOWN_COMMIT_READBACK_FAILED",
                reconciliation_required=True,
                cause=error,
            )

        if observed is None:
            return None

        if (
            type(observed)
            is not LegalEvidenceProviderDeleteExecutionEvidence
            or observed != expected
            or observed.fingerprint != expected.fingerprint
        ):
            _fail(
                "L10A2R_A3_P4_P6D5_"
                "UNKNOWN_COMMIT_READBACK_DIVERGENT",
                reconciliation_required=True,
            )

        return observed

    def _persist_uncertainty(
        self,
        *,
        command: LegalEvidenceProviderCleanupCommand,
        execution_evidence:
            LegalEvidenceProviderDeleteExecutionEvidence,
    ) -> None:
        uncertainty = (
            open_legal_evidence_provider_delete_execution_uncertainty(
                uncertainty_id=self._id_factory("uncertainty"),
                command=command,
                execution_evidence=execution_evidence,
                uncertainty_recorded_at=_utc(self._clock()),
            )
        )

        with self._client.start_session() as session:
            session.start_transaction()
            try:
                self._uncertainty_registry.create_or_replay(
                    uncertainty,
                    session=session,
                )
                session.commit_transaction()
            except Exception as error:
                _abort_if_active(session)
                _fail(
                    "L10A2R_A3_P4_P6D5_"
                    "UNCERTAINTY_PERSISTENCE_FAILED",
                    reconciliation_required=True,
                    cause=error,
                )

    def execute(
        self,
        *,
        tenant_id: str,
        command_id: str,
    ) -> LegalEvidenceProviderDeleteExecutionEvidence:
        """Execute one exact tenant/command provider-delete orchestration.

        AUTHORITY:
            Requires pre-existing durable cleanup command and authorization.
        TENANT SCOPE:
            Every durable lookup and mutation uses the supplied exact tenant.
        MUTATION:
            Commits the pre-provider claim before provider I/O and persists
            execution evidence or uncertainty afterward.
        IDEMPOTENCY:
            Exact existing execution evidence returns without provider I/O.
            Existing unresolved claim or uncertainty blocks re-execution;
            exact claim replay never grants provider-execution ownership.
        TRANSACTION:
            Mongo transactions never span provider execution.
        FAIL-CLOSED:
            Unknown execution-evidence commit acknowledgement requires fresh
            exact durable readback before success or uncertainty; ambiguity
            never becomes automatic retry or physical-absence truth.
            After provider I/O, only the exact certified S3 provider-evidence
            domain type may cross into canonical durable execution evidence.
            Any other result requires reconciliation and cannot create durable
            execution evidence, uncertainty, retry authority, or absence truth.
        FINANCIAL BOUNDARY:
            No financial execution authority; Kennel EOS remains exclusive.
        """
        command, replay = self._preflight(
            tenant_id=tenant_id,
            command_id=command_id,
        )

        if replay is not None:
            return replay

        self._commit_claim(command)

        request = self._request(command)

        try:
            provider_evidence = (
                self._provider_adapter.execute_delete(request)
            )
        except Exception as error:
            _fail(
                "L10A2R_A3_P4_P6D5_"
                "PROVIDER_EXECUTION_FAILED_RECONCILIATION_REQUIRED",
                reconciliation_required=True,
                cause=error,
            )

        if (
            type(provider_evidence)
            is not LegalEvidenceS3ProviderDeleteExecutionEvidence
        ):
            _fail(
                "L10A2R_A3_P4_P6D5_"
                "PROVIDER_RESULT_INVALID_RECONCILIATION_REQUIRED",
                reconciliation_required=True,
            )

        execution_evidence = (
            LegalEvidenceProviderDeleteExecutionEvidence(
                execution_evidence_id=
                    self._id_factory("execution_evidence"),
                tenant_id=command.tenant_id,
                command_id=command.command_id,
                cleanup_authorization_id=
                    command.cleanup_authorization_id,
                provider_name=provider_evidence.provider_name,
                storage_reference=
                    provider_evidence.storage_reference,
                object_version_reference=
                    provider_evidence.object_version_reference,
                command_fingerprint=command.fingerprint,
                cleanup_authorization_fingerprint=
                    command.cleanup_authorization_fingerprint,
                delete_marker=provider_evidence.delete_marker,
                delete_marker_version_reference=
                    provider_evidence.delete_marker_version_reference,
                executed_at=_utc(self._clock()),
            )
        )

        try:
            with self._client.start_session() as session:
                session.start_transaction()
                try:
                    persisted = (
                        self._execution_evidence_registry
                        .create_or_replay(
                            execution_evidence,
                            session=session,
                        )
                    )
                    session.commit_transaction()
                except Exception as error:
                    if not _has_error_label(
                        error,
                        UNKNOWN_TRANSACTION_COMMIT_RESULT,
                    ):
                        _abort_if_active(session)
                    raise

        except Exception as persistence_error:
            if _has_error_label(
                persistence_error,
                UNKNOWN_TRANSACTION_COMMIT_RESULT,
            ):
                reconciled = (
                    self._fresh_execution_evidence_readback(
                        expected=execution_evidence,
                    )
                )

                if reconciled is not None:
                    return reconciled

                self._persist_uncertainty(
                    command=command,
                    execution_evidence=execution_evidence,
                )

                _fail(
                    "L10A2R_A3_P4_P6D5_"
                    "UNKNOWN_COMMIT_READBACK_ABSENT",
                    reconciliation_required=True,
                    cause=persistence_error,
                )

            self._persist_uncertainty(
                command=command,
                execution_evidence=execution_evidence,
            )

            _fail(
                "L10A2R_A3_P4_P6D5_"
                "POST_PROVIDER_PERSISTENCE_UNCERTAIN",
                reconciliation_required=True,
                cause=persistence_error,
            )

        return persisted


__all__ = [
    "VERSION",
    "LegalEvidenceProviderDeleteOrchestrationError",
    "LegalEvidenceProviderDeleteOrchestrationService",
]

# ARTIFACT: legal_evidence_provider_delete_orchestration_service.py
# VERSION: v1.3.0-L10A2R-A3-P4-P6D5-PROVIDER-DELETE-ORCHESTRATION
# AUTHORITY BOUNDARY: consumes certified cleanup authority; grants no new cleanup, retry, reconciliation, lifecycle, IAM, billing, payment, settlement, or financial authority
# TENANT POSTURE: exact tenant-scoped command, authorization, claim, execution-evidence, and uncertainty persistence
# TRANSACTION POSTURE: provider execution occurs outside Mongo transactions; durable phases use separate fresh transactions
# IDEMPOTENCY POSTURE: durable execution evidence replays exactly; any already-durable claim, including exact replay, blocks provider re-execution by that invocation
# FAIL-CLOSED POSTURE: provider/persistence ambiguity requires reconciliation and never proves physical absence
# UNKNOWN COMMIT POSTURE: execution-evidence UnknownTransactionCommitResult requires fresh transactional exact readback before uncertainty
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
