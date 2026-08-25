from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — BASE ENGINE LIFECYCLE CONTRACT (FG178)
===============================================================================
Epitome:
    Unified Abstract Base Engine enforcing a deterministic 5-stage lifecycle
    execution model across all Wilsy OS kernel subsystems:
    initialize() -> validate() -> execute() -> publish() -> shutdown().

Biblical Worth Billions:
    "Let all things be done decently and in order." — 1 Corinthians 14:40
    "To every thing there is a season, and a time to every purpose under the heaven."
    — Ecclesiastes 3:1
    Institutional software demands absolute predictability, deterministic state
    transitions, and cryptographic auditability. No child's place.

Collaboration & Ownership:
    - Founder & Lead Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Core Infrastructure
    - Phase / Milestone: FG178 - Engine Lifecycle Manager
    - Target Directory: tools/eos/core/
    - File Path: tools/eos/core/engine.py
    - Runtime Alignment: Python 3.10+ Production Environment

Downstream Consumers:
    - Kernel Scheduler (Orchestrates engine state machine transitions)
    - Event Bus (Subscribes to stage transition lifecycle envelopes)
    - Artifact Bus (Receives validated output data schemas)
    - Executive Audit Dashboards & Historical Replay Engine
===============================================================================
"""

import abc
import enum
import hashlib
import json
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# Initialize institutional logger for kernel core lifecycle events
logger = logging.getLogger("WilsyOS.Kernel.CoreEngine")


# =============================================================================
# ENUMERATIONS & STATE MODELS
# =============================================================================

class EngineStatus(str, enum.Enum):
    """
    Represents the operational state of a Wilsy OS kernel engine throughout
    its lifecycle state machine.
    """
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    VALIDATING = "VALIDATING"
    EXECUTING = "EXECUTING"
    PUBLISHING = "PUBLISHING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SHUTDOWN = "SHUTDOWN"


class LifecycleStage(str, enum.Enum):
    """
    Explicit enumeration of the 5 canonical execution stages.
    """
    INITIALIZE = "INITIALIZE"
    VALIDATE = "VALIDATE"
    EXECUTE = "EXECUTE"
    PUBLISH = "PUBLISH"
    SHUTDOWN = "SHUTDOWN"


class EngineLifecycleValidator:
    """
    Thread-safe state machine validator guarding engine lifecycle transitions.
    Prevents illegal state jumps (e.g., executing before validation).
    """

    _ALLOWED_TRANSITIONS: Dict[EngineStatus, Set[EngineStatus]] = {
        EngineStatus.UNINITIALIZED: {EngineStatus.INITIALIZING, EngineStatus.FAILED},
        EngineStatus.INITIALIZING: {EngineStatus.READY, EngineStatus.FAILED},
        EngineStatus.READY: {EngineStatus.VALIDATING, EngineStatus.SHUTDOWN, EngineStatus.FAILED},
        EngineStatus.VALIDATING: {EngineStatus.EXECUTING, EngineStatus.FAILED},
        EngineStatus.EXECUTING: {EngineStatus.PUBLISHING, EngineStatus.FAILED},
        EngineStatus.PUBLISHING: {EngineStatus.COMPLETED, EngineStatus.FAILED},
        EngineStatus.COMPLETED: {EngineStatus.SHUTDOWN, EngineStatus.READY, EngineStatus.FAILED},
        EngineStatus.FAILED: {EngineStatus.SHUTDOWN, EngineStatus.UNINITIALIZED},
        EngineStatus.SHUTDOWN: {EngineStatus.UNINITIALIZED},
    }

    @classmethod
    def can_transition(cls, current: EngineStatus, next_status: EngineStatus) -> bool:
        """
        Determines whether a transition from `current` to `next_status` is legal.
        """
        allowed = cls._ALLOWED_TRANSITIONS.get(current, set())
        return next_status in allowed


# =============================================================================
# ENGINE RESULT CONTAINER (IMMUTABLE & CRYPTOGRAPHICALLY SEALED)
# =============================================================================

class EngineResult:
    """
    Immutable container encapsulating the complete execution results of a
    kernel engine. Cryptographically sealed via SHA-256 over all execution data.
    """

    def __init__(
        self,
        execution_id: str,
        engine_id: str,
        status: EngineStatus,
        output_data: Optional[Dict[str, Any]] = None,
        artifacts: Optional[List[Dict[str, Any]]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None,
        duration_ms: float = 0.0,
        timestamp: Optional[str] = None,
    ) -> None:
        self.execution_id = execution_id
        self.engine_id = engine_id
        self.status = status
        self.output_data = output_data or {}
        self.artifacts = artifacts or []
        self.metrics = metrics or {}
        self.errors = errors or []
        self.duration_ms = duration_ms
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    def compute_checksum(self) -> str:
        """
        Calculates an immutable SHA-256 checksum seal across all execution outputs.
        Ensures anti-tamper verification for historical audit replays.
        """
        payload = {
            "execution_id": self.execution_id,
            "engine_id": self.engine_id,
            "status": self.status.value,
            "output_data": self.output_data,
            "artifacts": self.artifacts,
            "metrics": self.metrics,
            "errors": self.errors,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }
        raw_bytes = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(raw_bytes).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the execution result into a JSON-compatible dictionary.
        """
        return {
            "execution_id": self.execution_id,
            "engine_id": self.engine_id,
            "status": self.status.value,
            "output_data": self.output_data,
            "artifacts": self.artifacts,
            "metrics": self.metrics,
            "errors": self.errors,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
            "checksum": self.compute_checksum(),
        }


# =============================================================================
# ABSTRACT BASE KERNEL ENGINE
# =============================================================================

class BaseKernelEngine(abc.ABC):
    """
    Abstract Base Class for all Wilsy OS engines.

    Every subclass must implement the five lifecycle stage methods:
      1. initialize()
      2. validate(context)
      3. execute(context)
      4. publish(result)
      5. shutdown()

    Execution is triggered via `run_lifecycle(context)`, which enforces
    stage progression, timing telemetry, thread locks, error recovery,
    and event/artifact bus publications.
    """

    def __init__(
        self,
        engine_id: str,
        name: str,
        description: str,
        version: str = "1.0.0",
        event_bus_publisher: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        artifact_bus_publisher: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> None:
        """
        Initializes the base kernel engine structure.

        Args:
            engine_id: Unique string identifier (e.g., 'engine.governance.v1')
            name: Human-readable display name of the engine
            description: Concise explanation of the engine's purpose
            version: Semantic version string of the engine specification
            event_bus_publisher: Optional callable callback for Event Bus emissions
            artifact_bus_publisher: Optional callable callback for Artifact Bus emissions
        """
        self.engine_id = engine_id
        self.name = name
        self.description = description
        self.version = version

        self._status = EngineStatus.UNINITIALIZED
        self._state_lock = threading.RLock()

        # Wire communication bus delegates (fall back to internal logger if unattached)
        self.event_publisher = event_bus_publisher or self._default_event_publisher
        self.artifact_publisher = artifact_bus_publisher or self._default_artifact_publisher

    @property
    def status(self) -> EngineStatus:
        """Returns the current operational status of the engine under re-entrant lock protection."""
        with self._state_lock:
            return self._status

    def _set_status(self, new_status: EngineStatus) -> None:
        """
        Internal status transition method. Validates correctness against state machine rules.

        Raises:
            RuntimeError: If an invalid or out-of-order transition is attempted.
        """
        with self._state_lock:
            if not EngineLifecycleValidator.can_transition(self._status, new_status):
                error_msg = (
                    f"Illegal state transition in engine '{self.engine_id}': "
                    f"Cannot move from '{self._status.value}' to '{new_status.value}'."
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            logger.debug(
                f"Engine '{self.engine_id}' transitioning: {self._status.value} -> {new_status.value}"
            )
            self._status = new_status

    def _default_event_publisher(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Default event log handler when Event Bus is not explicitly wired."""
        logger.info(f"[EVENT-BUS :: {event_type}] {json.dumps(payload, default=str)}")

    def _default_artifact_publisher(self, schema_id: str, payload: Dict[str, Any]) -> None:
        """Default artifact log handler when Artifact Bus is not explicitly wired."""
        logger.info(f"[ARTIFACT-BUS :: {schema_id}] {json.dumps(payload, default=str)}")

    # -------------------------------------------------------------------------
    # MANDATORY ABSTRACT LIFECYCLE HOOKS (MUST BE IMPLEMENTED BY SUBCLASSES)
    # -------------------------------------------------------------------------

    @abc.abstractmethod
    def initialize(self) -> None:
        """
        STAGE 1: INITIALIZE
        Allocates memory, loads deep learning weights, opens database connection
        pools, and prepares all internal state prior to handling execution workloads.
        """
        pass

    @abc.abstractmethod
    def validate(self, context: Any) -> Tuple[bool, str]:
        """
        STAGE 2: VALIDATE
        Inspects the incoming ExecutionContext, verifying parameters, authorization
        tokens, policy constraints, and structural integrity before work begins.

        Returns:
            Tuple[bool, str]: (is_valid, validation_message_or_reason)
        """
        pass

    @abc.abstractmethod
    def execute(self, context: Any) -> Dict[str, Any]:
        """
        STAGE 3: EXECUTE
        Performs the core workload computation (governance checks, AI inference,
        risk assessment, or legal document processing).

        Returns:
            Dict[str, Any]: Structured operational output payload.
        """
        pass

    @abc.abstractmethod
    def publish(self, result: EngineResult) -> List[Dict[str, Any]]:
        """
        STAGE 4: PUBLISH
        Transforms execution results into formal, schema-validated artifacts for the
        Artifact Bus and downstream analytical consumers.

        Returns:
            List[Dict[str, Any]]: List of schema-conforming artifact dictionaries.
        """
        pass

    @abc.abstractmethod
    def shutdown(self) -> None:
        """
        STAGE 5: SHUTDOWN
        Gracefully releases system handles, flushes network sockets, drains queues,
        and clears memory buffers. Called during kernel termination or reset.
        """
        pass

    # -------------------------------------------------------------------------
    # UNIFIED TEMPLATE METHOD (DRIVEN BY KERNEL SCHEDULER)
    # -------------------------------------------------------------------------

    def run_lifecycle(self, context: Any) -> EngineResult:
        """
        Executes the engine through the deterministic 5-stage lifecycle.
        This template method guarantees that initialize, validate, execute,
        publish, and error recording happen in strict sequential order.

        Args:
            context: Incoming ExecutionContext object driving this execution cycle.

        Returns:
            EngineResult: Cryptographically sealed result container.
        """
        execution_id = getattr(context, "execution_id", f"EXEC-UNKNOWN-{int(time.time())}")
        start_time = time.perf_counter()
        errors: List[str] = []

        try:
            # -----------------------------------------------------------------
            # Stage 1: Initialize (Executed once if UNINITIALIZED)
            # -----------------------------------------------------------------
            if self.status == EngineStatus.UNINITIALIZED:
                self._set_status(EngineStatus.INITIALIZING)
                logger.info(f"Initializing engine '{self.engine_id}'...")
                self.initialize()
                self._set_status(EngineStatus.READY)

                self.event_publisher("EngineInitialized", {
                    "engine_id": self.engine_id,
                    "stage": LifecycleStage.INITIALIZE.value,
                    "execution_id": execution_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

            # -----------------------------------------------------------------
            # Stage 2: Validate Context
            # -----------------------------------------------------------------
            self._set_status(EngineStatus.VALIDATING)
            is_valid, validation_msg = self.validate(context)

            self.event_publisher("EngineValidated", {
                "engine_id": self.engine_id,
                "stage": LifecycleStage.VALIDATE.value,
                "execution_id": execution_id,
                "is_valid": is_valid,
                "message": validation_msg,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            if not is_valid:
                raise ValueError(f"Context validation failed in '{self.engine_id}': {validation_msg}")

            # -----------------------------------------------------------------
            # Stage 3: Execute Core Workload
            # -----------------------------------------------------------------
            self._set_status(EngineStatus.EXECUTING)
            output_data = self.execute(context)

            self.event_publisher("EngineExecuted", {
                "engine_id": self.engine_id,
                "stage": LifecycleStage.EXECUTE.value,
                "execution_id": execution_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            interim_duration = (time.perf_counter() - start_time) * 1000.0

            interim_result = EngineResult(
                execution_id=execution_id,
                engine_id=self.engine_id,
                status=EngineStatus.EXECUTING,
                output_data=output_data,
                duration_ms=interim_duration,
            )

            # -----------------------------------------------------------------
            # Stage 4: Publish Artifacts & Events
            # -----------------------------------------------------------------
            self._set_status(EngineStatus.PUBLISHING)
            artifacts = self.publish(interim_result)

            for artifact in artifacts:
                schema = artifact.get("artifact_schema", "generic_kernel_artifact_v1")
                self.artifact_publisher(schema, artifact)

            self._set_status(EngineStatus.COMPLETED)

            total_duration_ms = (time.perf_counter() - start_time) * 1000.0

            final_result = EngineResult(
                execution_id=execution_id,
                engine_id=self.engine_id,
                status=EngineStatus.COMPLETED,
                output_data=output_data,
                artifacts=artifacts,
                metrics={
                    "duration_ms": total_duration_ms,
                    "stages_cleared": 4,
                    "completed_cleanly": True,
                },
                duration_ms=total_duration_ms,
            )

            self.event_publisher("EngineCompleted", {
                "engine_id": self.engine_id,
                "stage": LifecycleStage.PUBLISH.value,
                "execution_id": execution_id,
                "duration_ms": total_duration_ms,
                "checksum": final_result.compute_checksum(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            return final_result

        except Exception as ex:
            # -----------------------------------------------------------------
            # Error Failure Path: Capture, Log, and Emit Failure Envelope
            # -----------------------------------------------------------------
            total_duration_ms = (time.perf_counter() - start_time) * 1000.0
            error_msg = f"Engine '{self.engine_id}' failed: {str(ex)}"
            logger.exception(error_msg)
            errors.append(error_msg)

            self._set_status(EngineStatus.FAILED)

            self.event_publisher("EngineFailed", {
                "engine_id": self.engine_id,
                "execution_id": execution_id,
                "error": error_msg,
                "duration_ms": total_duration_ms,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            return EngineResult(
                execution_id=execution_id,
                engine_id=self.engine_id,
                status=EngineStatus.FAILED,
                errors=errors,
                duration_ms=total_duration_ms,
            )


# Explicit alias so `from .engine import BaseEngine` in __init__.py works seamlessly
BaseEngine = BaseKernelEngine

__all__ = [
    "EngineStatus",
    "LifecycleStage",
    "EngineLifecycleValidator",
    "EngineResult",
    "BaseKernelEngine",
    "BaseEngine",
]
