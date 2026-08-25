"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Runtime Execution Framework - Runtime Execution Plan Contract (FG149C).
    Serves as the pure runtime execution contract consumed by the Scheduler.
    Adapts registry topological descriptors into an ordered tuple of Task models.

Biblical Scale & Architecture:
    Institutional-grade immutable execution plan. Zero scheduling logic inside.
    Psalms 119:105 - "Your word is a lamp for my feet, a light on my path."

Collaboration & Maintenance:
    - [Architecture]: Decoupled runtime contract isolating tasks from scheduling dispatch.
    - Consumed by: Scheduler (FG149D).
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from tools.eos.registry.execution_plan import ExecutionPlan as RegistryExecutionPlan
from tools.eos.runtime.task import Task

logger = logging.getLogger("WilsyRuntimeExecutionPlan")


@dataclass(frozen=True)
class ExecutionPlan:
    """
    Immutable runtime execution contract passed directly to the Scheduler.
    Binds ordered tasks, global execution run ID, creation timestamp, and cryptographic checksum.
    """

    execution_id: str
    ordered_tasks: Tuple[Task, ...]
    checksum: str
    created_at: str

    # [FUNCTION EXPLANATION]: Factory constructor computing SHA-256 integrity checksum over task signatures.
    @classmethod
    def create(
        cls,
        ordered_tasks: Tuple[Task, ...],
        execution_id: str,
        created_at: Optional[str] = None,
    ) -> ExecutionPlan:
        """
        Factory method constructing a frozen runtime ExecutionPlan instance.

        Args:
            ordered_tasks (Tuple[Task, ...]): Topologically ordered tasks.
            execution_id (str): Global execution run correlation ID.
            created_at (Optional[str]): ISO 8601 creation timestamp override.

        Returns:
            ExecutionPlan: Immutable runtime execution plan with SHA-256 checksum.
        """
        now_utc = created_at or datetime.now(timezone.utc).isoformat()
        checksum = cls.compute_checksum(execution_id, ordered_tasks, now_utc)

        return cls(
            execution_id=execution_id,
            ordered_tasks=ordered_tasks,
            checksum=checksum,
            created_at=now_utc,
        )

    # [FUNCTION EXPLANATION]: Adapter method converting an FG148 Registry ExecutionPlan into an FG149 Runtime Plan.
    @classmethod
    def from_registry_plan(
        cls,
        registry_plan: RegistryExecutionPlan,
    ) -> ExecutionPlan:
        """
        Adapts an FG148 Registry ExecutionPlan into an FG149 Runtime ExecutionPlan.

        Args:
            registry_plan (RegistryExecutionPlan): Resolved registry plan containing engine descriptors.

        Returns:
            ExecutionPlan: Converted runtime execution plan containing Task instances.
        """
        tasks = tuple(
            Task.create(
                engine_descriptor=desc,
                execution_id=registry_plan.execution_id,
                priority=getattr(desc, "priority", 100),
            )
            for desc in registry_plan.ordered_descriptors
        )

        return cls.create(
            ordered_tasks=tasks,
            execution_id=registry_plan.execution_id,
            created_at=registry_plan.created_at,
        )

    # [FUNCTION EXPLANATION]: Computes SHA-256 cryptographic checksum over plan identifiers and task sequence.
    @staticmethod
    def compute_checksum(
        execution_id: str,
        ordered_tasks: Tuple[Task, ...],
        created_at: str,
    ) -> str:
        """
        Computes SHA-256 hash over execution parameters and task signatures.

        Returns:
            str: Hexadecimal SHA-256 hash string.
        """
        payload = {
            "execution_id": execution_id,
            "created_at": created_at,
            "task_ids": [t.task_id for t in ordered_tasks],
            "engine_ids": [t.engine_id for t in ordered_tasks],
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    # [FUNCTION EXPLANATION]: Cryptographic validation verifying runtime plan integrity.
    def verify_integrity(self) -> bool:
        """
        Verifies that the execution plan's checksum matches its current internal state.

        Returns:
            bool: True if cryptographic checksum is valid, False otherwise.
        """
        recalculated = self.compute_checksum(self.execution_id, self.ordered_tasks, self.created_at)
        return self.checksum == recalculated

    @property
    def total_tasks(self) -> int:
        """Returns the total number of tasks bound to this execution plan."""
        return len(self.ordered_tasks)

    # [FUNCTION EXPLANATION]: Serializes runtime plan metadata for audit trails and logging.
    def to_dict(self) -> Dict[str, Any]:
        """Serializes execution plan state into a JSON-compatible dictionary."""
        return {
            "execution_id": self.execution_id,
            "created_at": self.created_at,
            "total_tasks": self.total_tasks,
            "checksum": self.checksum,
            "integrity_valid": self.verify_integrity(),
            "ordered_tasks": [task.to_dict() for task in self.ordered_tasks],
        }
