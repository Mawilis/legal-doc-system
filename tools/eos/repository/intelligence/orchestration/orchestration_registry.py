"""
===============================================================================
WILSY OS — FG231C ENTERPRISE NERVOUS SYSTEM [V1.0.0]
===============================================================================
Epitome:
    Sovereign orchestration registry defining workflow definitions, execution 
    stages, step bindings, and state transitions for Wilsy OS.

Biblical Worth Billions:
    "Let all things be done decently and in order." — 1 Corinthians 14:40

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Architecture Agent
    - File Path: tools/eos/repository/intelligence/orchestration/orchestration_registry.py
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional


class WorkflowStatus(str, Enum):
    """Workflow execution state definitions."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class WorkflowStep:
    """
    Represents a discrete step bound to a capability ID within an orchestration workflow.
    """
    step_id: str
    capability_id: str
    description: str
    timeout_ms: int = 5000
    retry_limit: int = 3
    required_for_success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Converts workflow step to serializable dictionary."""
        return asdict(self)


@dataclass
class WorkflowDefinition:
    """
    Sovereign definition of an orchestrated end-to-end execution flow.
    """
    workflow_id: str
    name: str
    purpose: str
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING

    def add_step(self, step: WorkflowStep) -> None:
        """Appends an execution step to the workflow pipeline."""
        self.steps.append(step)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes workflow definition to dictionary representation."""
        data = asdict(self)
        data["status"] = self.status.value if isinstance(self.status, WorkflowStatus) else str(self.status)
        data["steps"] = [step.to_dict() for step in self.steps]
        return data


@dataclass
class OrchestrationRegistryCatalog:
    """
    Master catalog index of all defined system orchestration workflows.
    """
    workflows: Dict[str, WorkflowDefinition] = field(default_factory=dict)

    def register_workflow(self, workflow: WorkflowDefinition) -> None:
        """Registers a workflow definition into the master orchestration index."""
        self.workflows[workflow.workflow_id] = workflow

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Retrieves a workflow by its unique identifier."""
        return self.workflows.get(workflow_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the entire orchestration catalog."""
        return {
            "total_workflows": len(self.workflows),
            "workflows": {k: v.to_dict() for k, v in self.workflows.items()},
        }