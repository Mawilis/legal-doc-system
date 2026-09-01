"""Canonical asynchronous worker registry for the runtime scheduler.

TITLE: WILSY Runtime Worker Registry
VERSION: v1.0.0-WILSY-RUNTIME-WORKER-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Validates and routes explicit async worker objects without manufacturing execution truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/runtime/worker_registry.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.0 establishes the structural async execute worker-object contract, removes stale raw-callable dispatch, rejects invalid or duplicate registration, fails closed for non-WorkerResultDTO and task-identity mismatches, preserves unknown-worker and worker-exception FAILED results and valid matching statuses, and adds no tenant, authentication, KEXEC, persistence, transaction, or financial authority.
COMPLIANCE: Explicit local orchestration; POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Stable failure reasons do not include payloads or worker representations.
TENANT BOUNDARY: No tenant lookup, synthesis, membership, or authorization; engine names and task IDs are routing evidence only.
AUTHORITY BOUNDARY: Local worker routing and result-shape validation only; no authentication, authorization, or KEXEC authority.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import inspect
import logging
import time
from typing import Any, Dict, Optional, Protocol

from .worker_result import WorkerExecutionStatusEnum, WorkerResultDTO

logger = logging.getLogger("WilsyOS.Runtime.WorkerRegistry")
VERSION = "v1.0.0-WILSY-RUNTIME-WORKER-REGISTRY"


class WorkerRegistrationError(ValueError):
    """Raised when a worker configuration is not a valid runtime registration."""


class DuplicateWorkerRegistrationError(WorkerRegistrationError):
    """Raised when an engine routing key is already registered."""


class EngineWorkerProtocol(Protocol):
    """Structural contract for canonical asynchronous worker objects."""

    async def execute(self, task_id: str, payload: dict[str, Any]) -> WorkerResultDTO:
        """Execute one task and return its canonical result DTO."""
        ...


class EngineWorkerRegistry:
    """Register and dispatch validated async worker objects.

    Registration mutates only this in-memory routing table. Workers must expose
    an async ``execute`` method; raw callables and ``process_task``-only objects
    are not accepted. Dispatch preserves valid result DTOs, while unknown
    workers, worker exceptions, invalid result types, and identity mismatches
    become fail-closed FAILED DTOs. Tenant and financial authority remain
    outside this orchestration component.
    """

    def __init__(self) -> None:
        self._workers: Dict[str, EngineWorkerProtocol] = {}

    def register_worker(self, engine_name_or_worker: Any, worker: Optional[EngineWorkerProtocol] = None) -> None:
        """Register a worker by explicit or inferred nonblank engine name.

        Duplicate keys, invalid names, and workers without an async callable
        ``execute`` method raise :class:`WorkerRegistrationError` without
        mutating the registry.
        """
        if worker is None:
            target_worker = engine_name_or_worker
            engine_name = getattr(target_worker, "engine_name", None)
        else:
            engine_name = engine_name_or_worker
            target_worker = worker
        if not isinstance(engine_name, str) or not engine_name.strip():
            raise WorkerRegistrationError("ENGINE_NAME_REQUIRED")
        normalized_name = engine_name.strip()
        execute = getattr(target_worker, "execute", None)
        if not callable(execute) or not inspect.iscoroutinefunction(execute):
            raise WorkerRegistrationError("ASYNC_EXECUTE_WORKER_REQUIRED")
        if normalized_name in self._workers:
            raise DuplicateWorkerRegistrationError("DUPLICATE_ENGINE_NAME")
        self._workers[normalized_name] = target_worker

    async def dispatch_task(self, engine_name: str, task_id: str, payload: dict[str, Any]) -> WorkerResultDTO:
        """Dispatch one task and return a canonical, identity-checked result."""
        worker = self._workers.get(engine_name)
        if worker is None:
            return self._failed(task_id, f"No worker registered for engine '{engine_name}'")
        start_time = time.perf_counter()
        try:
            result = await worker.execute(task_id, payload)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            if not isinstance(result, WorkerResultDTO):
                return self._failed(task_id, "INVALID_WORKER_RESULT_TYPE")
            if result.task_id != task_id:
                return self._failed(task_id, "WORKER_RESULT_TASK_ID_MISMATCH")
            return result
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.exception("Worker execution failed for engine [%s]", engine_name)
            return WorkerResultDTO(task_id=task_id, status=WorkerExecutionStatusEnum.FAILED, execution_duration_ms=duration_ms, output={}, error_details=str(exc))

    @staticmethod
    def _failed(task_id: str, reason: str) -> WorkerResultDTO:
        """Create a non-success result with only stable failure evidence."""
        return WorkerResultDTO(task_id=task_id, status=WorkerExecutionStatusEnum.FAILED, execution_duration_ms=0.0, output={}, error_details=reason)


# ARTIFACT: worker_registry.py
# VERSION: v1.0.0-WILSY-RUNTIME-WORKER-REGISTRY
# AUTHORITY BOUNDARY: local worker routing and result validation only.
# TENANT POSTURE: no tenant synthesis, lookup, or authorization.
# FAIL-CLOSED POSTURE: invalid registration and invalid result evidence are rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
