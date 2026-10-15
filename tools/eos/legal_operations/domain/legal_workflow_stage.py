"""TITLE: WILSY OS Legal Workflow Stage Definition Domain.

VERSION: v1.0.1-G7G-R3-LEGAL-WORKFLOW-STAGE

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

EPITOME:
    Preserve one immutable stage node belonging to one exact immutable Legal
    workflow-definition revision.

    A stage may identify successor stages and opaque references to work
    requirements, completion gates and automation configuration.

    This value does not create workflow-instance state, work items,
    assignments, supervision, legal events, IAM authority or automation
    execution authority.

WORKFLOW BINDING:
    workflow_definition_id, definition_revision and
    workflow_definition_fingerprint bind this node to one exact immutable
    LegalWorkflowDefinition revision.

TOPOLOGY BOUNDARY:
    This artifact validates only local node invariants.

    It does not prove whole-workflow graph validity, reachability, single-entry
    topology, terminal reachability, branch convergence, or cycle policy.
    Those require a future graph/topology certificate over all stages.

STAGE BOUNDARY:
    is_entry_stage and is_terminal_stage describe workflow configuration only.

    Terminal stages cannot declare successors.
    Non-terminal stages must declare at least one successor.
    A stage cannot directly succeed itself.

WORK REQUIREMENT BOUNDARY:
    work_requirement_references are opaque configuration references.
    They do not create LegalWorkItem records.

COMPLETION-GATE BOUNDARY:
    completion_gate_references identify future gate definitions.
    Gates must later evaluate canonical server-side evidence.
    This value never creates or satisfies legal evidence.

AUTOMATION BOUNDARY:
    automation_references are configuration references only.
    They grant no operation authority and execute nothing.

ASSIGNMENT / SUPERVISION:
    No assignee, supervisor, role or permission is embedded.

COMMERCIAL BOUNDARY:
    No plan, subscription, entitlement, price or quota authority.

FINANCIAL AUTHORITY:
    None. Kennel EOS remains exclusive financial execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha3_512
import hmac
import json
from typing import Final, NoReturn

from tools.eos.legal_operations.domain.legal_workflow_definition import (
    LegalWorkflowDefinition,
)


VERSION: Final[str] = (
    "v1.0.1-G7G-R3-LEGAL-WORKFLOW-STAGE"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-WORKFLOW-STAGE/V1"
)


class LegalWorkflowStageError(ValueError):
    """Stable fail-closed workflow-stage definition failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise LegalWorkflowStageError(code)


def _text(
    name: str,
    value: object,
    *,
    limit: int = 320,
) -> str:
    if not isinstance(value, str):
        _fail(
            f"G7G_R3_{name.upper()}_INVALID"
        )

    normalized = value.strip()

    if (
        not normalized
        or normalized != value
        or len(normalized) > limit
    ):
        _fail(
            f"G7G_R3_{name.upper()}_INVALID"
        )

    return normalized


def _revision(
    value: object,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        _fail(
            "G7G_R3_DEFINITION_REVISION_INVALID"
        )

    return value


def _boolean(
    name: str,
    value: object,
) -> bool:
    if not isinstance(value, bool):
        _fail(
            f"G7G_R3_{name.upper()}_INVALID"
        )

    return value


def _fingerprint(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 128
        or value.lower() != value
    ):
        _fail(
            f"G7G_R3_{name.upper()}_INVALID"
        )

    try:
        int(value, 16)
    except ValueError as error:
        raise LegalWorkflowStageError(
            f"G7G_R3_{name.upper()}_INVALID"
        ) from error

    return value


def _references(
    name: str,
    value: object,
    *,
    limit: int = 240,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        _fail(
            f"G7G_R3_{name.upper()}_INVALID"
        )

    result: list[str] = []
    seen: set[str] = set()

    for raw in value:
        reference = _text(
            name.removesuffix("s"),
            raw,
            limit=limit,
        )

        if reference in seen:
            _fail(
                f"G7G_R3_{name.upper()}_DUPLICATE"
            )

        seen.add(reference)
        result.append(reference)

    return tuple(result)


@dataclass(frozen=True, slots=True)
class LegalWorkflowStage:
    """One immutable stage node for one exact workflow-definition revision."""

    workflow_definition_id: str
    definition_revision: int
    workflow_definition_fingerprint: str

    stage_definition_id: str
    name: str
    description_reference: str

    is_entry_stage: bool
    is_terminal_stage: bool

    successor_stage_ids: tuple[str, ...]
    work_requirement_references: tuple[str, ...]
    completion_gate_references: tuple[str, ...]
    automation_references: tuple[str, ...]

    schema: str = SCHEMA
    workflow_stage_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        workflow_definition_id = _text(
            "workflow_definition_id",
            self.workflow_definition_id,
            limit=160,
        )

        definition_revision = _revision(
            self.definition_revision
        )

        definition_fingerprint = _fingerprint(
            "workflow_definition_fingerprint",
            self.workflow_definition_fingerprint,
        )

        stage_definition_id = _text(
            "stage_definition_id",
            self.stage_definition_id,
            limit=160,
        )

        name = _text(
            "name",
            self.name,
            limit=240,
        )

        description_reference = _text(
            "description_reference",
            self.description_reference,
            limit=320,
        )

        is_entry_stage = _boolean(
            "is_entry_stage",
            self.is_entry_stage,
        )

        is_terminal_stage = _boolean(
            "is_terminal_stage",
            self.is_terminal_stage,
        )

        successor_stage_ids = _references(
            "successor_stage_ids",
            self.successor_stage_ids,
            limit=160,
        )

        if stage_definition_id in successor_stage_ids:
            _fail(
                "G7G_R3_SELF_SUCCESSOR_INVALID"
            )

        if is_terminal_stage:
            if successor_stage_ids:
                _fail(
                    "G7G_R3_TERMINAL_STAGE_HAS_SUCCESSOR"
                )
        elif not successor_stage_ids:
            _fail(
                "G7G_R3_NON_TERMINAL_STAGE_REQUIRES_SUCCESSOR"
            )

        work_requirements = _references(
            "work_requirement_references",
            self.work_requirement_references,
        )

        completion_gates = _references(
            "completion_gate_references",
            self.completion_gate_references,
        )

        automation_references = _references(
            "automation_references",
            self.automation_references,
        )

        if (
            self.schema != SCHEMA
            or self.workflow_stage_version
            != VERSION
        ):
            _fail(
                "G7G_R3_IDENTITY_INVALID"
            )

        object.__setattr__(
            self,
            "workflow_definition_id",
            workflow_definition_id,
        )
        object.__setattr__(
            self,
            "definition_revision",
            definition_revision,
        )
        object.__setattr__(
            self,
            "workflow_definition_fingerprint",
            definition_fingerprint,
        )
        object.__setattr__(
            self,
            "stage_definition_id",
            stage_definition_id,
        )
        object.__setattr__(
            self,
            "name",
            name,
        )
        object.__setattr__(
            self,
            "description_reference",
            description_reference,
        )
        object.__setattr__(
            self,
            "is_entry_stage",
            is_entry_stage,
        )
        object.__setattr__(
            self,
            "is_terminal_stage",
            is_terminal_stage,
        )
        object.__setattr__(
            self,
            "successor_stage_ids",
            successor_stage_ids,
        )
        object.__setattr__(
            self,
            "work_requirement_references",
            work_requirements,
        )
        object.__setattr__(
            self,
            "completion_gate_references",
            completion_gates,
        )
        object.__setattr__(
            self,
            "automation_references",
            automation_references,
        )

        digest = self._compute_fingerprint()

        if self.fingerprint:
            supplied = _fingerprint(
                "fingerprint",
                self.fingerprint,
            )

            if not hmac.compare_digest(
                supplied,
                digest,
            ):
                _fail(
                    "G7G_R3_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    @classmethod
    def from_workflow_definition(
        cls,
        *,
        workflow_definition: LegalWorkflowDefinition,
        stage_definition_id: str,
        name: str,
        description_reference: str,
        is_entry_stage: bool,
        is_terminal_stage: bool,
        successor_stage_ids: tuple[str, ...],
        work_requirement_references: tuple[str, ...],
        completion_gate_references: tuple[str, ...],
        automation_references: tuple[str, ...],
    ) -> "LegalWorkflowStage":
        """Bind one stage to exact immutable workflow-definition evidence."""
        return cls(
            workflow_definition_id=
                workflow_definition.workflow_definition_id,
            definition_revision=
                workflow_definition.definition_revision,
            workflow_definition_fingerprint=
                workflow_definition.fingerprint,
            stage_definition_id=
                stage_definition_id,
            name=
                name,
            description_reference=
                description_reference,
            is_entry_stage=
                is_entry_stage,
            is_terminal_stage=
                is_terminal_stage,
            successor_stage_ids=
                successor_stage_ids,
            work_requirement_references=
                work_requirement_references,
            completion_gate_references=
                completion_gate_references,
            automation_references=
                automation_references,
        )

    def semantic_dict(
        self,
    ) -> dict[str, object]:
        return {
            "schema":
                self.schema,
            "workflow_stage_version":
                self.workflow_stage_version,
            "workflow_definition_id":
                self.workflow_definition_id,
            "definition_revision":
                self.definition_revision,
            "workflow_definition_fingerprint":
                self.workflow_definition_fingerprint,
            "stage_definition_id":
                self.stage_definition_id,
            "name":
                self.name,
            "description_reference":
                self.description_reference,
            "is_entry_stage":
                self.is_entry_stage,
            "is_terminal_stage":
                self.is_terminal_stage,
            "successor_stage_ids":
                list(
                    self.successor_stage_ids
                ),
            "work_requirement_references":
                list(
                    self.work_requirement_references
                ),
            "completion_gate_references":
                list(
                    self.completion_gate_references
                ),
            "automation_references":
                list(
                    self.automation_references
                ),
        }

    def _compute_fingerprint(
        self,
    ) -> str:
        canonical = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        return sha3_512(
            canonical.encode("utf-8")
        ).hexdigest()

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            **self.semantic_dict(),
            "fingerprint":
                self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalWorkflowStage":
        if not isinstance(value, dict):
            _fail(
                "G7G_R3_PAYLOAD_INVALID"
            )

        required = {
            "schema",
            "workflow_stage_version",
            "workflow_definition_id",
            "definition_revision",
            "workflow_definition_fingerprint",
            "stage_definition_id",
            "name",
            "description_reference",
            "is_entry_stage",
            "is_terminal_stage",
            "successor_stage_ids",
            "work_requirement_references",
            "completion_gate_references",
            "automation_references",
            "fingerprint",
        }

        if set(value) != required:
            _fail(
                "G7G_R3_PAYLOAD_SCHEMA_INVALID"
            )

        sequence_fields = (
            "successor_stage_ids",
            "work_requirement_references",
            "completion_gate_references",
            "automation_references",
        )

        converted: dict[str, tuple[str, ...]] = {}

        for field in sequence_fields:
            raw = value[field]

            if not isinstance(raw, list):
                _fail(
                    f"G7G_R3_{field.upper()}_INVALID"
                )

            parsed: list[str] = []

            for item in raw:
                if not isinstance(item, str):
                    _fail(
                        f"G7G_R3_{field.upper()}_INVALID"
                    )

                parsed.append(item)

            converted[field] = tuple(parsed)

        return cls(
            schema=value["schema"],
            workflow_stage_version=value[
                "workflow_stage_version"
            ],
            workflow_definition_id=value[
                "workflow_definition_id"
            ],
            definition_revision=value[
                "definition_revision"
            ],
            workflow_definition_fingerprint=value[
                "workflow_definition_fingerprint"
            ],
            stage_definition_id=value[
                "stage_definition_id"
            ],
            name=value["name"],
            description_reference=value[
                "description_reference"
            ],
            is_entry_stage=value[
                "is_entry_stage"
            ],
            is_terminal_stage=value[
                "is_terminal_stage"
            ],
            successor_stage_ids=tuple(
                converted["successor_stage_ids"]
            ),
            work_requirement_references=tuple(
                converted[
                    "work_requirement_references"
                ]
            ),
            completion_gate_references=tuple(
                converted[
                    "completion_gate_references"
                ]
            ),
            automation_references=tuple(
                converted[
                    "automation_references"
                ]
            ),
            fingerprint=value["fingerprint"],
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalWorkflowStage",
    "LegalWorkflowStageError",
]

# ARTIFACT: legal_workflow_stage.py
# VERSION: v1.0.1-G7G-R3-LEGAL-WORKFLOW-STAGE
# AUTHORITY BOUNDARY: immutable local workflow-stage configuration only
# WHOLE-GRAPH AUTHORITY: NONE
# WORK GENERATION AUTHORITY: NONE
# AUTOMATION EXECUTION AUTHORITY: NONE
# LEGAL EVENT AUTHORITY: NONE
# IAM AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# TENANT POSTURE: exact tenant correlation; cross-tenant inference prohibited
# FAIL-CLOSED POSTURE: malformed, incomplete, or divergent evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
