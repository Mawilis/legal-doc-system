"""TITLE: WILSY OS Legal Workflow Topology Domain.

VERSION: v1.0.1-G7G-R4-LEGAL-WORKFLOW-TOPOLOGY

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

EPITOME:
    Certify the structural graph of one exact immutable Legal workflow
    definition revision.

    The topology proves stage membership, successor integrity, exactly one
    entry stage, at least one terminal stage, entry reachability, and terminal
    reachability.

    Cycles are permitted only when every stage participating in or reachable
    through the cycle can still reach at least one terminal stage.

    This artifact owns structural workflow configuration only. It does not
    create runtime workflow state, execute automation, create work, select
    branches, establish legal events, grant IAM authority, assign principals,
    establish supervision, or create financial authority.

COLLABORATION:
    LegalWorkflowDefinition owns the immutable workflow header.
    LegalWorkflowStage owns immutable local stage configuration.
    This domain validates the whole stage graph.

RUNTIME BOUNDARY:
    A future LegalMatterWorkflowInstance pins one certified topology.
    Runtime stage progression remains separate.

LEGAL-TRUTH BOUNDARY:
    Reachability and stage progression are process facts only.
    Canonical Legal domains remain exclusive owners of Legal-event truth.

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
from tools.eos.legal_operations.domain.legal_workflow_stage import (
    LegalWorkflowStage,
)


VERSION: Final[str] = (
    "v1.0.1-G7G-R4-LEGAL-WORKFLOW-TOPOLOGY"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-WORKFLOW-TOPOLOGY/V1"
)


class LegalWorkflowTopologyError(ValueError):
    """Stable fail-closed workflow-topology validation failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise LegalWorkflowTopologyError(code)


def _text(
    name: str,
    value: object,
    *,
    limit: int = 160,
) -> str:
    if not isinstance(value, str):
        _fail(f"G7G_R4_{name.upper()}_INVALID")

    normalized = value.strip()

    if (
        not normalized
        or normalized != value
        or len(normalized) > limit
    ):
        _fail(f"G7G_R4_{name.upper()}_INVALID")

    return normalized


def _revision(value: object) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        _fail(
            "G7G_R4_DEFINITION_REVISION_INVALID"
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
            f"G7G_R4_{name.upper()}_INVALID"
        )

    try:
        int(value, 16)
    except ValueError as error:
        raise LegalWorkflowTopologyError(
            f"G7G_R4_{name.upper()}_INVALID"
        ) from error

    return value


@dataclass(frozen=True, slots=True)
class LegalWorkflowTopologyStage:
    """Minimal immutable stage snapshot required for graph certification."""

    stage_definition_id: str
    stage_fingerprint: str
    is_entry_stage: bool
    is_terminal_stage: bool
    successor_stage_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        stage_id = _text(
            "stage_definition_id",
            self.stage_definition_id,
        )

        stage_fingerprint = _fingerprint(
            "stage_fingerprint",
            self.stage_fingerprint,
        )

        if not isinstance(
            self.is_entry_stage,
            bool,
        ):
            _fail(
                "G7G_R4_IS_ENTRY_STAGE_INVALID"
            )

        if not isinstance(
            self.is_terminal_stage,
            bool,
        ):
            _fail(
                "G7G_R4_IS_TERMINAL_STAGE_INVALID"
            )

        if not isinstance(
            self.successor_stage_ids,
            tuple,
        ):
            _fail(
                "G7G_R4_SUCCESSOR_STAGE_IDS_INVALID"
            )

        successors: list[str] = []
        seen: set[str] = set()

        for raw in self.successor_stage_ids:
            successor = _text(
                "successor_stage_id",
                raw,
            )

            if successor in seen:
                _fail(
                    "G7G_R4_SUCCESSOR_STAGE_ID_DUPLICATE"
                )

            if successor == stage_id:
                _fail(
                    "G7G_R4_SELF_SUCCESSOR_INVALID"
                )

            seen.add(successor)
            successors.append(successor)

        if self.is_terminal_stage:
            if successors:
                _fail(
                    "G7G_R4_TERMINAL_STAGE_HAS_SUCCESSOR"
                )
        elif not successors:
            _fail(
                "G7G_R4_NON_TERMINAL_STAGE_REQUIRES_SUCCESSOR"
            )

        object.__setattr__(
            self,
            "stage_definition_id",
            stage_id,
        )
        object.__setattr__(
            self,
            "stage_fingerprint",
            stage_fingerprint,
        )
        object.__setattr__(
            self,
            "successor_stage_ids",
            tuple(successors),
        )

    @classmethod
    def from_stage(
        cls,
        stage: LegalWorkflowStage,
    ) -> "LegalWorkflowTopologyStage":
        return cls(
            stage_definition_id=
                stage.stage_definition_id,
            stage_fingerprint=
                stage.fingerprint,
            is_entry_stage=
                stage.is_entry_stage,
            is_terminal_stage=
                stage.is_terminal_stage,
            successor_stage_ids=
                stage.successor_stage_ids,
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "stage_definition_id":
                self.stage_definition_id,
            "stage_fingerprint":
                self.stage_fingerprint,
            "is_entry_stage":
                self.is_entry_stage,
            "is_terminal_stage":
                self.is_terminal_stage,
            "successor_stage_ids":
                list(self.successor_stage_ids),
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalWorkflowTopologyStage":
        if not isinstance(value, dict):
            _fail(
                "G7G_R4_STAGE_PAYLOAD_INVALID"
            )

        required = {
            "stage_definition_id",
            "stage_fingerprint",
            "is_entry_stage",
            "is_terminal_stage",
            "successor_stage_ids",
        }

        if set(value) != required:
            _fail(
                "G7G_R4_STAGE_PAYLOAD_SCHEMA_INVALID"
            )

        raw_successors = value[
            "successor_stage_ids"
        ]

        if not isinstance(
            raw_successors,
            list,
        ):
            _fail(
                "G7G_R4_SUCCESSOR_STAGE_IDS_INVALID"
            )

        successors: list[str] = []

        for raw in raw_successors:
            if not isinstance(raw, str):
                _fail(
                    "G7G_R4_SUCCESSOR_STAGE_IDS_INVALID"
                )
            successors.append(raw)

        return cls(
            stage_definition_id=value[
                "stage_definition_id"
            ],
            stage_fingerprint=value[
                "stage_fingerprint"
            ],
            is_entry_stage=value[
                "is_entry_stage"
            ],
            is_terminal_stage=value[
                "is_terminal_stage"
            ],
            successor_stage_ids=tuple(
                successors
            ),
        )


@dataclass(frozen=True, slots=True)
class LegalWorkflowTopology:
    """Whole-graph certificate for one exact workflow definition revision."""

    workflow_definition_id: str
    definition_revision: int
    workflow_definition_fingerprint: str

    stages: tuple[
        LegalWorkflowTopologyStage,
        ...
    ]

    schema: str = SCHEMA
    workflow_topology_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        definition_id = _text(
            "workflow_definition_id",
            self.workflow_definition_id,
        )

        revision = _revision(
            self.definition_revision
        )

        definition_fingerprint = _fingerprint(
            "workflow_definition_fingerprint",
            self.workflow_definition_fingerprint,
        )

        if not isinstance(self.stages, tuple):
            _fail("G7G_R4_STAGES_INVALID")

        if not self.stages:
            _fail("G7G_R4_STAGES_REQUIRED")

        stage_map: dict[
            str,
            LegalWorkflowTopologyStage,
        ] = {}

        for stage in self.stages:
            if not isinstance(
                stage,
                LegalWorkflowTopologyStage,
            ):
                _fail(
                    "G7G_R4_STAGE_INVALID"
                )

            if (
                stage.stage_definition_id
                in stage_map
            ):
                _fail(
                    "G7G_R4_STAGE_ID_DUPLICATE"
                )

            stage_map[
                stage.stage_definition_id
            ] = stage

        entry_ids = tuple(
            stage.stage_definition_id
            for stage in self.stages
            if stage.is_entry_stage
        )

        if len(entry_ids) != 1:
            _fail(
                "G7G_R4_EXACTLY_ONE_ENTRY_REQUIRED"
            )

        terminal_ids = {
            stage.stage_definition_id
            for stage in self.stages
            if stage.is_terminal_stage
        }

        if not terminal_ids:
            _fail(
                "G7G_R4_TERMINAL_STAGE_REQUIRED"
            )

        all_ids = set(stage_map)

        for stage in self.stages:
            for successor in (
                stage.successor_stage_ids
            ):
                if successor not in all_ids:
                    _fail(
                        "G7G_R4_DANGLING_SUCCESSOR"
                    )

        entry = entry_ids[0]

        reachable: set[str] = set()
        stack = [entry]

        while stack:
            current = stack.pop()

            if current in reachable:
                continue

            reachable.add(current)

            stack.extend(
                stage_map[
                    current
                ].successor_stage_ids
            )

        if reachable != all_ids:
            _fail(
                "G7G_R4_ORPHAN_STAGE"
            )

        reverse: dict[str, set[str]] = {
            stage_id: set()
            for stage_id in all_ids
        }

        for stage in self.stages:
            for successor in (
                stage.successor_stage_ids
            ):
                reverse[successor].add(
                    stage.stage_definition_id
                )

        can_reach_terminal: set[str] = set()
        terminal_stack = list(
            terminal_ids
        )

        while terminal_stack:
            current = terminal_stack.pop()

            if current in can_reach_terminal:
                continue

            can_reach_terminal.add(
                current
            )

            terminal_stack.extend(
                reverse[current]
            )

        if can_reach_terminal != all_ids:
            _fail(
                "G7G_R4_NON_TERMINATING_STAGE_REGION"
            )

        if (
            self.schema != SCHEMA
            or self.workflow_topology_version
            != VERSION
        ):
            _fail(
                "G7G_R4_IDENTITY_INVALID"
            )

        canonical_stages = tuple(
            sorted(
                self.stages,
                key=lambda stage:
                    stage.stage_definition_id,
            )
        )

        object.__setattr__(
            self,
            "workflow_definition_id",
            definition_id,
        )
        object.__setattr__(
            self,
            "definition_revision",
            revision,
        )
        object.__setattr__(
            self,
            "workflow_definition_fingerprint",
            definition_fingerprint,
        )
        object.__setattr__(
            self,
            "stages",
            canonical_stages,
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
                    "G7G_R4_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    @classmethod
    def from_definition_and_stages(
        cls,
        *,
        workflow_definition:
            LegalWorkflowDefinition,
        stages: tuple[
            LegalWorkflowStage,
            ...
        ],
    ) -> "LegalWorkflowTopology":
        """Certify stages against one exact workflow definition revision."""
        if not stages:
            _fail(
                "G7G_R4_STAGES_REQUIRED"
            )

        topology_stages: list[
            LegalWorkflowTopologyStage
        ] = []

        for stage in stages:
            if (
                stage.workflow_definition_id
                != workflow_definition.workflow_definition_id
                or stage.definition_revision
                != workflow_definition.definition_revision
                or not hmac.compare_digest(
                    stage.workflow_definition_fingerprint,
                    workflow_definition.fingerprint,
                )
            ):
                _fail(
                    "G7G_R4_STAGE_DEFINITION_BINDING_MISMATCH"
                )

            topology_stages.append(
                LegalWorkflowTopologyStage.from_stage(
                    stage
                )
            )

        return cls(
            workflow_definition_id=
                workflow_definition.workflow_definition_id,
            definition_revision=
                workflow_definition.definition_revision,
            workflow_definition_fingerprint=
                workflow_definition.fingerprint,
            stages=tuple(
                topology_stages
            ),
        )

    @property
    def entry_stage_definition_id(
        self,
    ) -> str:
        for stage in self.stages:
            if stage.is_entry_stage:
                return stage.stage_definition_id

        raise AssertionError(
            "validated topology lost entry stage"
        )

    @property
    def terminal_stage_definition_ids(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            stage.stage_definition_id
            for stage in self.stages
            if stage.is_terminal_stage
        )

    def semantic_dict(
        self,
    ) -> dict[str, object]:
        return {
            "schema":
                self.schema,
            "workflow_topology_version":
                self.workflow_topology_version,
            "workflow_definition_id":
                self.workflow_definition_id,
            "definition_revision":
                self.definition_revision,
            "workflow_definition_fingerprint":
                self.workflow_definition_fingerprint,
            "stages": [
                stage.to_dict()
                for stage in self.stages
            ],
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
    ) -> "LegalWorkflowTopology":
        if not isinstance(value, dict):
            _fail(
                "G7G_R4_PAYLOAD_INVALID"
            )

        required = {
            "schema",
            "workflow_topology_version",
            "workflow_definition_id",
            "definition_revision",
            "workflow_definition_fingerprint",
            "stages",
            "fingerprint",
        }

        if set(value) != required:
            _fail(
                "G7G_R4_PAYLOAD_SCHEMA_INVALID"
            )

        raw_stages = value["stages"]

        if not isinstance(raw_stages, list):
            _fail(
                "G7G_R4_STAGES_INVALID"
            )

        parsed_stages: list[
            LegalWorkflowTopologyStage
        ] = []

        for raw_stage in raw_stages:
            parsed_stages.append(
                LegalWorkflowTopologyStage.from_dict(
                    raw_stage
                )
            )

        return cls(
            schema=value["schema"],
            workflow_topology_version=value[
                "workflow_topology_version"
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
            stages=tuple(parsed_stages),
            fingerprint=value["fingerprint"],
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalWorkflowTopology",
    "LegalWorkflowTopologyError",
    "LegalWorkflowTopologyStage",
]

# ARTIFACT: legal_workflow_topology.py
# VERSION: v1.0.1-G7G-R4-LEGAL-WORKFLOW-TOPOLOGY
# AUTHORITY BOUNDARY: immutable structural workflow graph certificate only
# RUNTIME INSTANCE AUTHORITY: NONE
# LEGAL EVENT AUTHORITY: NONE
# IAM AUTHORITY: NONE
# WORK GENERATION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# TENANT POSTURE: exact tenant correlation; cross-tenant inference prohibited
# FAIL-CLOSED POSTURE: malformed, incomplete, or divergent evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
