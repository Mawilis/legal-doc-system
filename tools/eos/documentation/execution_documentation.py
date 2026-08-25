"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/execution_documentation.py
===============================================================================
Epitome:
    Automated execution runtime cataloger for Wilsy OS. Captures and documents
    ExecutionContext lifecycles, scheduler allocations, worker threads, execution
    plans, execution results, failure traces, and retry topologies.

Biblical Worth Billions:
    "The steps of a good man are ordered by the Lord: and he delighteth in his way."
    — Psalm 37:23

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/execution_documentation.py
===============================================================================
"""

from typing import Dict, List, Any, Optional
from tools.eos.documentation.documentation_contract import (
    DocumentationEntity,
    EntityKind,
    InterfaceSpec,
    VerificationStatus,
)


class ExecutionDocumentationGenerator:
    """
    Specialized documentation builder for tracking execution telemetry, scheduler
    plans, worker allocations, and runtime failure diagnostics in Wilsy OS.
    """

    @staticmethod
    def generate_execution_entity(
        urn: str,
        execution_id: str,
        plan_name: str,
        worker_id: str,
        status: str,
        duration_ms: float,
        retries: int = 0,
        failure_reason: Optional[str] = None,
        version: str = "2.0.0",
    ) -> DocumentationEntity:
        """
        Constructs a DocumentationEntity representing an ExecutionContext runtime telemetry record.

        Args:
            urn: Target unique documentation URN.
            execution_id: Unique execution context tracking ID.
            plan_name: Name of the executed orchestrator plan or workflow.
            worker_id: Target worker thread or process assigned.
            status: Runtime execution result status (e.g. 'SUCCESS', 'FAILED', 'RETRYING').
            duration_ms: Execution duration in milliseconds.
            retries: Number of retry attempts executed.
            failure_reason: Optional exception string or stack trace snippet.
            version: Target version string.

        Returns:
            Validated DocumentationEntity contract instance.
        """
        interface = InterfaceSpec(
            name=f"ExecutePlan::{plan_name}",
            description=f"Execution Plan run on worker {worker_id}",
            parameters={"execution_id": "str", "worker_id": "str"},
            return_type="ExecutionResult",
            is_async=True,
        )

        metadata = {
            "execution_id": execution_id,
            "plan_name": plan_name,
            "worker_id": worker_id,
            "status": status,
            "duration_ms": duration_ms,
            "retries": retries,
            "failure_reason": failure_reason or "N/A",
        }

        return DocumentationEntity(
            urn=urn,
            kind=EntityKind.KERNEL,
            title=f"Execution Telemetry: {plan_name} [{execution_id}]",
            purpose=f"Runtime telemetry trace for plan '{plan_name}' executed by {worker_id}",
            module_path="tools/eos/kernel/execution_context",
            version=version,
            architecture_summary=f"ExecutionContext runtime record for ID {execution_id} (Status: {status}, Latency: {duration_ms}ms)",
            lifecycle_stage="PRODUCTION",
            interfaces=[interface],
            metadata=metadata,
            verification_status=VerificationStatus.VERIFIED if status == "SUCCESS" else VerificationStatus.EXPERIMENTAL,
        )

    @staticmethod
    def generate_execution_summary(entities: List[DocumentationEntity]) -> Dict[str, Any]:
        """
        Aggregates execution telemetry entities into a runtime summary report.

        Args:
            entities: List of registered DocumentationEntity contracts.

        Returns:
            Dictionary compiling execution telemetry metrics.
        """
        summary: Dict[str, Any] = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_retries": 0,
            "avg_duration_ms": 0.0,
            "executions": [],
        }

        total_duration = 0.0

        for entity in entities:
            meta = entity.metadata
            if "execution_id" not in meta:
                continue

            summary["total_executions"] += 1
            duration = float(meta.get("duration_ms", 0.0))
            total_duration += duration
            summary["total_retries"] += int(meta.get("retries", 0))

            status = meta.get("status", "UNKNOWN")
            if status == "SUCCESS":
                summary["successful_executions"] += 1
            else:
                summary["failed_executions"] += 1

            summary["executions"].append({
                "urn": entity.urn,
                "execution_id": meta.get("execution_id"),
                "plan_name": meta.get("plan_name"),
                "worker_id": meta.get("worker_id"),
                "status": status,
                "duration_ms": duration,
                "retries": meta.get("retries"),
            })

        if summary["total_executions"] > 0:
            summary["avg_duration_ms"] = round(total_duration / summary["total_executions"], 4)

        return summary
