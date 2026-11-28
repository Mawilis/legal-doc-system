"""TITLE: WILSY OS Controlled Intelligence Dock Component Catalog
VERSION: v1.0.0
AUTHORITY: WILSY OS Core Governance; presentation contract only.
EPITOME: Validate a closed declarative work interface without executable model content.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/wilsy_dock_contract.py
COLLABORATION / OWNERSHIP: EOS reasoning router, Projects registry, React Dock.
CERTIFICATION / UPDATE DATE: 2026-11-25
CHANGELOG: v1.0.0 introduces source-bound briefs, actions and artifact components.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: Plain bounded text; no routes, scripts or tool execution.
TENANT BOUNDARY: Envelope coordinates must come from independently authorized EOS reads.
AUTHORITY BOUNDARY: Validation grants no permission; commands reauthorize in Projects.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively; no financial operations here.
"""
from __future__ import annotations

from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

VERSION = "v1.0.0"


class DockModel(BaseModel):
    """Reject coercion and extra fields; no storage, IAM or transaction ownership."""

    model_config = ConfigDict(extra="forbid", strict=True)


class WorkBinding(DockModel):
    """Source coordinates, never an authorization grant or historical work truth."""

    project_id: str = Field(pattern=r"^prj-[0-9a-f]{48}$")
    task_id: str = Field(pattern=r"^ptk-[0-9a-f]{48}$")
    revision: int = Field(ge=1)
    fingerprint: str = Field(pattern=r"^[0-9a-f]{128}$")
    participant_view: bool


class DockExecution(DockModel):
    """Closed client operation; the renderer chooses canonical routes locally."""

    operation: Literal["NAVIGATE_TASK", "REVIEW_EVIDENCE", "DRAFT_PLAN", "PROJECT_TASK_TRANSITION"]
    target_status: Literal["IN_PROGRESS", "DONE"] | None = None
    requires_confirmation: bool = False

    @model_validator(mode="after")
    def validate_command(self) -> DockExecution:
        """Deny disconnected or unconfirmed mutations, without executing one."""
        mutation = self.operation == "PROJECT_TASK_TRANSITION"
        if mutation != (self.target_status is not None) or (mutation and not self.requires_confirmation):
            raise ValueError("DOCK_EXECUTION_INVALID")
        return self


class DockAction(DockModel):
    """Revision-bound suggestion with source ordering and metadata-only correlation."""

    id: str = Field(min_length=1, max_length=100)
    component_id: str = Field(min_length=1, max_length=100)
    kind: Literal["DRAFT_PLAN", "OPEN_TASK", "REVIEW_EVIDENCE", "START_TASK", "COMPLETE_TASK"]
    source: WorkBinding
    outcome: str = Field(min_length=1, max_length=240)
    priority: int = Field(ge=0, le=3)
    availability: Literal["AVAILABLE"] = "AVAILABLE"
    verified_revision: int = Field(ge=1)
    execution: DockExecution
    correlation_id: str = Field(pattern=r"^[0-9a-f]{128}$")

    @model_validator(mode="after")
    def validate_binding(self) -> DockAction:
        """Reject revision, kind and operation confusion before UI rendering."""
        expected = {"DRAFT_PLAN": ("DRAFT_PLAN", None), "OPEN_TASK": ("NAVIGATE_TASK", None),
                    "REVIEW_EVIDENCE": ("REVIEW_EVIDENCE", None),
                    "START_TASK": ("PROJECT_TASK_TRANSITION", "IN_PROGRESS"),
                    "COMPLETE_TASK": ("PROJECT_TASK_TRANSITION", "DONE")}
        if self.verified_revision != self.source.revision or expected[self.kind] != (
            self.execution.operation, self.execution.target_status,
        ):
            raise ValueError("DOCK_ACTION_BINDING_INVALID")
        return self


class TaskBrief(DockModel):
    """Compact source facts; missing facts remain absent, never inferred by AI."""

    type: Literal["TaskBrief"] = "TaskBrief"
    id: str = Field(min_length=1, max_length=100)
    source: WorkBinding
    title: str = Field(min_length=1, max_length=180)
    purpose: str = Field(max_length=5000)
    status: Literal["TODO", "IN_PROGRESS", "BLOCKED", "DONE", "CANCELLED"]
    owner: str | None = Field(default=None, max_length=180)
    deadline: str | None = Field(default=None, max_length=40)
    dependencies: list[str] = Field(max_length=25)
    established: str = Field(min_length=1, max_length=500)
    blockers: list[str] = Field(max_length=25)
    next_action: str = Field(min_length=1, max_length=240)
    can_attach: bool


class ActionList(DockModel):
    """At most four source-authorized suggestions, each rechecked on execution."""

    type: Literal["ActionList"] = "ActionList"
    id: str = Field(min_length=1, max_length=100)
    actions: list[DockAction] = Field(max_length=4)


class Checklist(DockModel):
    """Unexecuted plain-text criteria; checking a box proves no source completion."""

    type: Literal["Checklist"] = "Checklist"
    id: str = Field(min_length=1, max_length=100)
    items: list[str] = Field(max_length=50)


class ArtifactFrame(DockModel):
    """Draft lifecycle description; only independent EOS readback proves attachment."""

    type: Literal["ArtifactFrame"] = "ArtifactFrame"
    id: str = Field(min_length=1, max_length=100)
    source: WorkBinding
    title: str = Field(min_length=1, max_length=180)
    state: Literal["DRAFT", "EDITING", "ATTACHING", "UNVERIFIED", "ATTACHED", "DISCARDED"]
    provenance: Literal["DETERMINISTIC_DRAFT", "GOVERNED_PROVIDER"]
    content: str = Field(max_length=12000)


class ApprovalCard(DockModel):
    """Decision locator only; the canonical approval workflow owns all decisions."""

    type: Literal["ApprovalCard"] = "ApprovalCard"
    id: str = Field(min_length=1, max_length=100)
    approval_id: str = Field(pattern=r"^par-[0-9a-f]{48}$")
    text: str = Field(min_length=1, max_length=1000)


class StatusBanner(DockModel):
    """Bounded nonsecret status, with no inferred command or settlement success."""

    type: Literal["StatusBanner"] = "StatusBanner"
    id: str = Field(min_length=1, max_length=100)
    state: Literal["PENDING", "UNVERIFIED", "VERIFIED", "DENIED", "UNAVAILABLE"]
    text: str = Field(min_length=1, max_length=1000)


class PlainText(DockModel):
    """Inert contextual text, never interpreted as HTML or an executable tool."""

    type: Literal["PlainText"] = "PlainText"
    id: str = Field(min_length=1, max_length=100)
    text: str = Field(max_length=6000)


DockComponent = Annotated[
    TaskBrief | ActionList | Checklist | ArtifactFrame | ApprovalCard | StatusBanner | PlainText,
    Field(discriminator="type"),
]


class DockEnvelope(DockModel):
    """Versioned exact-scope projection, validated before leaving Python EOS."""

    catalog: Literal["wilsy.dock.v1"] = "wilsy.dock.v1"
    tenant_id: str = Field(min_length=1, max_length=180)
    principal_id: str = Field(min_length=1, max_length=180)
    observed_at: str = Field(min_length=1, max_length=64)
    source: WorkBinding
    components: list[DockComponent] = Field(min_length=1, max_length=8)
    model_invoked: Literal[False] = False
    financial_execution: Literal[False] = False

    @model_validator(mode="after")
    def validate_components(self) -> DockEnvelope:
        """Reject duplicate identities or actions disconnected from current source."""
        ids = [item.id for item in self.components]
        if len(ids) != len(set(ids)):
            raise ValueError("DOCK_DUPLICATE_COMPONENT")
        actions: list[str] = []
        for component in self.components:
            if isinstance(component, (TaskBrief, ArtifactFrame)) and component.source != self.source:
                raise ValueError("DOCK_COMPONENT_SCOPE_INVALID")
            if isinstance(component, ActionList):
                for action in component.actions:
                    if action.component_id != component.id or action.source != self.source:
                        raise ValueError("DOCK_ACTION_SCOPE_INVALID")
                    actions.append(action.id)
        if len(actions) != len(set(actions)) or len(actions) > 4:
            raise ValueError("DOCK_ACTION_COUNT_INVALID")
        return self


# ARTIFACT: wilsy_dock_contract.py
# VERSION: v1.0.0
# AUTHORITY BOUNDARY: inert validated presentation; Projects owns commands
# TENANT POSTURE: exact authenticated source coordinates
# FAIL-CLOSED POSTURE: unknown components and disconnected actions rejected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
