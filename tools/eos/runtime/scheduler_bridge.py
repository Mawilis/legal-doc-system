# -*- coding: utf-8 -*-
"""Canonical FG171C worker-event bridge.

TITLE: WILSY OS FG171C Worker Event Bridge
VERSION: v1.0.0-WILSY-FG171C-WORKER-EVENT-BRIDGE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Deterministically bridges canonical TASK_STARTED events to registered workers and publishes contract-valid completion, failure, and artifact events.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/runtime/scheduler_bridge.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder & Chief Architect); Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.0 establishes the first sovereign bridge contract, replaces stale event_id/payload assumptions with execution_id/metadata, uses deterministic async subscription and publication, emits canonical success/failure DTOs, and publishes artifact output through the canonical payload field.
COMPLIANCE: Explicit tenant-scoped event propagation; no persistence or transaction ownership; POPIA section 19, GDPR Article 32, and SOC 2 CC7.2 isolation posture.
SECURITY / PRIVACY POSTURE: Logs identifiers only; task and worker output mappings are deep-copied at orchestration boundaries to avoid bridge-induced mutation of upstream or sibling event payloads.
TENANT BOUNDARY: Accepts only explicitly tenant-scoped TASK_STARTED events; performs no tenant lookup, membership inference, cross-tenant substitution, or authorization.
AUTHORITY BOUNDARY: Owns event-to-worker orchestration only. Authentication, principal authority, tenant authorization, worker registration authority, request/correlation trust, and kernel KEXEC authority remain external.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial execution authority.

Epitome:
    WorkerEventBridge subscribes asynchronously to canonical TASK_STARTED
    events, validates their minimum execution/tenant/routing contract, dispatches
    an isolated payload through EngineWorkerRegistry, and emits exactly one
    terminal worker event:

        TASK_COMPLETED for SUCCESS
        TASK_FAILED for every non-success status

    Successful worker output may additionally produce ARTIFACT_PUBLISHED when
    artifact evidence is present.

    Scheduler task execution identity is preserved unchanged from
    TaskStartedEventDTO.execution_id. The bridge does not create or grant a
    higher-level Engineering Kernel KEXEC identity.

    The bridge does not authorize tenant membership. tenant_id is trusted only
    as already-authorized upstream scope evidence and is propagated unchanged
    after fail-closed structural validation.

Collaboration & Ownership:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    Engineering Collaboration: Wilsy OS Core Engineering
    File Path: tools/eos/runtime/scheduler_bridge.py
"""
from __future__ import annotations

from copy import deepcopy
import logging
import uuid
from typing import Any

from .scheduler_events import (
    ArtifactPublishedEventDTO,
    RuntimeEventBus,
    RuntimeEventTypeEnum,
    TaskCompletedEventDTO,
    TaskFailedEventDTO,
    TaskStartedEventDTO,
)
from .worker_registry import EngineWorkerRegistry
from .worker_result import WorkerExecutionStatusEnum

VERSION = "v1.0.0-WILSY-FG171C-WORKER-EVENT-BRIDGE"

logger = logging.getLogger("WilsyOS.Runtime.SchedulerBridge")

_FORBIDDEN_TENANT_REFERENCES = frozenset(
    {
        "unknown",
        "none",
        "null",
        "tenant-default",
    }
)


class WorkerEventBridge:
    """Bridge canonical scheduler events to the registered worker runtime.

    Authority:
        This component performs no authentication, tenant authorization,
        permission grant, worker-registration authority decision, or financial
        authorization.

    Tenant boundary:
        TASK_STARTED must contain a nonblank explicit tenant reference that is
        not a forbidden compatibility sentinel. The bridge never invents or
        substitutes tenant scope.

    Execution identity:
        execution_id and task_id must both be present and identical. The bridge
        preserves that task-scoped execution identity across terminal events.

    Mutation:
        TASK_STARTED metadata is deep-copied before worker dispatch. Worker
        output is independently deep-copied into each published downstream
        event so this bridge does not create shared mutable event payload state.

    Subscription:
        The handler is registered through RuntimeEventBus.subscribe_async(),
        making worker dispatch and downstream publication part of the awaited
        TASK_STARTED async dispatch path.

    Persistence and transactions:
        None. The bridge owns no persistence session, transaction, durable
        retry, idempotency record, or settlement state.

    Financial boundary:
        None. Kennel EOS remains the exclusive financial execution authority.
    """

    def __init__(
        self,
        event_bus: RuntimeEventBus,
        worker_registry: EngineWorkerRegistry,
    ) -> None:
        """Bind an explicit event bus and worker registry and subscribe once.

        Construction performs no worker execution, persistence operation,
        tenant lookup, or financial operation.
        """
        self.event_bus = event_bus
        self.worker_registry = worker_registry
        self._register_subscribers()
        logger.info(
            "FG171C WorkerEventBridge initialized with async TASK_STARTED subscription"
        )

    def _register_subscribers(self) -> None:
        """Register the TASK_STARTED handler on the deterministic async path."""
        self.event_bus.subscribe_async(
            RuntimeEventTypeEnum.TASK_STARTED,
            self._handle_task_started,
        )

    @staticmethod
    def _is_valid_task_started(event: TaskStartedEventDTO) -> bool:
        """Validate the minimum fail-closed bridge ingress contract.

        Validation proves only structural suitability for dispatch. It does not
        authenticate the producer or authorize tenant membership.
        """
        if event.event_type != RuntimeEventTypeEnum.TASK_STARTED.value:
            logger.error(
                "Rejecting TASK_STARTED bridge ingress with mismatched event_type [%s]",
                event.event_type,
            )
            return False

        if not event.execution_id.strip():
            logger.error("Rejecting TASK_STARTED bridge ingress without execution_id")
            return False

        if event.task_id is None or not event.task_id.strip():
            logger.error("Rejecting TASK_STARTED bridge ingress without task_id")
            return False

        if event.execution_id != event.task_id:
            logger.error(
                "Rejecting TASK_STARTED bridge ingress with execution/task identity mismatch"
            )
            return False

        if event.engine_name is None or not event.engine_name.strip():
            logger.error("Rejecting TASK_STARTED bridge ingress without engine_name")
            return False

        if event.tenant_id is None:
            logger.error("Rejecting TASK_STARTED bridge ingress without tenant_id")
            return False

        tenant_reference = event.tenant_id.strip()
        if (
            not tenant_reference
            or tenant_reference.casefold() in _FORBIDDEN_TENANT_REFERENCES
        ):
            logger.error(
                "Rejecting TASK_STARTED bridge ingress with invalid tenant reference"
            )
            return False

        return True

    async def _handle_task_started(self, event: Any) -> None:
        """Dispatch one valid TASK_STARTED event and publish its terminal events.

        Invalid or malformed ingress fails closed before worker dispatch.

        Success:
            Publishes one canonical TaskCompletedEventDTO. If the worker output
            contains artifact evidence, also publishes one canonical
            ArtifactPublishedEventDTO.

        Failure and cancellation:
            Publishes one canonical TaskFailedEventDTO and never publishes an
            artifact.

        Mutation boundary:
            Worker dispatch receives a deep copy of TASK_STARTED metadata.
            Completion, failure, and artifact event payload structures receive
            independent deep copies of worker output.

        Financial boundary:
            Worker orchestration is not approval, release authorization,
            execution, payment, or settlement.
        """
        if not isinstance(event, TaskStartedEventDTO):
            logger.warning(
                "WorkerEventBridge rejected unexpected event payload type [%s]",
                type(event).__name__,
            )
            return

        if not self._is_valid_task_started(event):
            return

        task_id = event.task_id
        engine_name = event.engine_name
        tenant_id = event.tenant_id

        assert task_id is not None
        assert engine_name is not None
        assert tenant_id is not None

        logger.info(
            "Bridge dispatching task [%s] on engine [%s] for tenant [%s]",
            task_id,
            engine_name,
            tenant_id,
        )

        worker_result = await self.worker_registry.dispatch_task(
            engine_name=engine_name,
            task_id=task_id,
            payload=deepcopy(event.metadata),
        )

        if worker_result.status == WorkerExecutionStatusEnum.SUCCESS:
            output_metadata = deepcopy(worker_result.output)

            completed_event = TaskCompletedEventDTO(
                execution_id=event.execution_id,
                event_type=RuntimeEventTypeEnum.TASK_COMPLETED.value,
                message=f"Task {task_id} completed",
                session_id=event.session_id,
                tenant_id=tenant_id,
                task_id=task_id,
                engine_name=engine_name,
                status=worker_result.status.value,
                execution_duration_ms=worker_result.execution_duration_ms,
                metadata=output_metadata,
            )

            await self.event_bus.publish_async(
                RuntimeEventTypeEnum.TASK_COMPLETED,
                completed_event,
            )

            if (
                "artifact_id" in worker_result.output
                or "artifact_type" in worker_result.output
                or worker_result.output.get("artifact") is True
            ):
                artifact_id = str(
                    worker_result.output.get("artifact_id")
                    or f"art-{uuid.uuid4().hex[:8]}"
                )
                artifact_type = str(
                    worker_result.output.get("artifact_type")
                    or f"{engine_name}_result"
                )

                artifact_event = ArtifactPublishedEventDTO(
                    artifact_id=artifact_id,
                    event_type=RuntimeEventTypeEnum.ARTIFACT_PUBLISHED.value,
                    message=f"Artifact {artifact_id} published",
                    session_id=event.session_id,
                    tenant_id=tenant_id,
                    source_task_id=task_id,
                    artifact_type=artifact_type,
                    payload=deepcopy(worker_result.output),
                )

                logger.info(
                    "Bridge publishing artifact [%s] for task [%s]",
                    artifact_id,
                    task_id,
                )

                await self.event_bus.publish_async(
                    RuntimeEventTypeEnum.ARTIFACT_PUBLISHED,
                    artifact_event,
                )

            return

        error_text = (
            worker_result.error_details
            or f"Worker execution ended with status {worker_result.status.value}"
        )

        failed_event = TaskFailedEventDTO(
            execution_id=event.execution_id,
            event_type=RuntimeEventTypeEnum.TASK_FAILED.value,
            message=f"Task {task_id} failed",
            session_id=event.session_id,
            tenant_id=tenant_id,
            task_id=task_id,
            engine_name=engine_name,
            error_details={
                "status": worker_result.status.value,
                "error": error_text,
                "execution_duration_ms": worker_result.execution_duration_ms,
                "output": deepcopy(worker_result.output),
            },
        )

        await self.event_bus.publish_async(
            RuntimeEventTypeEnum.TASK_FAILED,
            failed_event,
        )


__all__ = [
    "VERSION",
    "WorkerEventBridge",
]


# ARTIFACT: scheduler_bridge.py
# VERSION: v1.0.0-WILSY-FG171C-WORKER-EVENT-BRIDGE
# AUTHORITY BOUNDARY: event-to-worker orchestration only; authentication, tenant authorization, worker-registration authority, request/correlation trust, kernel KEXEC authority, and financial authority remain external
# TENANT POSTURE: explicit valid tenant-scoped TASK_STARTED required; no tenant synthesis, membership inference, authorization, or cross-tenant substitution
# FAIL-CLOSED POSTURE: malformed type, event type, execution/task identity, engine routing, or tenant scope is rejected before worker dispatch; every non-success worker result emits TASK_FAILED
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains the exclusive financial execution authority
# END OF WILSY OS SOVEREIGN ARTIFACT
