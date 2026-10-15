"""TITLE: WILSY OS Legal Matter Workflow Currentness Projection.

VERSION: v1.0.1-G7G-R11-LEGAL-MATTER-WORKFLOW-CURRENTNESS

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

EPITOME:
    Derive one deterministic immutable current workflow position from one exact
    LegalMatterWorkflowInstance plus a complete immutable transition history.

    This module owns no persistence, current pointer, registry mutation,
    transition execution, IAM, work generation, Legal-event truth, assignment,
    supervision, billing or financial execution.

DERIVATION:
    With no transitions:
        current stage = instance.entry_stage_definition_id

    With transitions:
        history must form one exact contiguous chain beginning at the instance
        entry stage.

        Sequence numbers must be exactly 1..N.

        The first transition must have no previous-transition fingerprint.

        Every later transition must bind the immediately previous transition
        fingerprint.

        Every later source stage must equal the immediately previous target
        stage.

        Transition timestamps must strictly increase.

        Every transition must bind the same exact tenant, case_matter_id,
        workflow instance identity/fingerprint and topology fingerprint.

        current stage = final valid transition target.

FAIL-CLOSED:
    Sequence gaps, duplicate sequence numbers, mixed scope, broken fingerprint
    chain, stage discontinuity, chronology drift, duplicate transition identity
    or malformed evidence reject rather than infer or repair currentness.

CURRENTNESS:
    This artifact is a derived projection only.

    It does not create progression and does not establish that the current stage
    is legally complete, professionally authorized, assigned, supervised or
    otherwise actionable.

FINANCIAL AUTHORITY:
    None. Kennel EOS remains exclusive financial execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha3_512
import hmac
import json
from typing import Final, NoReturn

from tools.eos.legal_operations.domain.legal_matter_workflow_instance import (
    LegalMatterWorkflowInstance,
)
from tools.eos.legal_operations.domain.legal_matter_workflow_transition import (
    LegalMatterWorkflowTransition,
)


VERSION: Final[str] = (
    "v1.0.1-G7G-R11-LEGAL-MATTER-WORKFLOW-CURRENTNESS"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-MATTER-WORKFLOW-CURRENTNESS/V1"
)


class LegalMatterWorkflowCurrentnessError(ValueError):
    """Stable fail-closed currentness derivation failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise LegalMatterWorkflowCurrentnessError(code)


def _text(
    name: str,
    value: object,
    *,
    limit: int = 320,
) -> str:
    if not isinstance(value, str):
        _fail(
            f"G7G_R11_{name.upper()}_INVALID"
        )

    normalized = value.strip()

    if (
        not normalized
        or normalized != value
        or len(normalized) > limit
    ):
        _fail(
            f"G7G_R11_{name.upper()}_INVALID"
        )

    return normalized


def _tenant(value: object) -> str:
    tenant = _text(
        "tenant_id",
        value,
        limit=160,
    )

    if tenant.casefold() in {
        "default",
        "global",
        "root",
        "*",
    }:
        _fail("G7G_R11_TENANT_REQUIRED")

    return tenant


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
            f"G7G_R11_{name.upper()}_INVALID"
        )

    try:
        int(value, 16)
    except ValueError as error:
        raise LegalMatterWorkflowCurrentnessError(
            f"G7G_R11_{name.upper()}_INVALID"
        ) from error

    return value


@dataclass(frozen=True, slots=True)
class LegalMatterWorkflowCurrentness:
    """Immutable deterministic currentness evidence for one workflow instance."""

    currentness_id: str

    tenant_id: str
    case_matter_id: str

    workflow_instance_id: str
    workflow_instance_fingerprint: str
    workflow_topology_fingerprint: str

    current_stage_definition_id: str

    transition_count: int
    head_transition_id: str | None
    head_transition_fingerprint: str | None

    schema: str = SCHEMA
    currentness_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        currentness_id = _text(
            "currentness_id",
            self.currentness_id,
            limit=160,
        )

        tenant_id = _tenant(
            self.tenant_id
        )

        case_matter_id = _text(
            "case_matter_id",
            self.case_matter_id,
            limit=160,
        )

        workflow_instance_id = _text(
            "workflow_instance_id",
            self.workflow_instance_id,
            limit=160,
        )

        workflow_instance_fingerprint = _fingerprint(
            "workflow_instance_fingerprint",
            self.workflow_instance_fingerprint,
        )

        workflow_topology_fingerprint = _fingerprint(
            "workflow_topology_fingerprint",
            self.workflow_topology_fingerprint,
        )

        current_stage_definition_id = _text(
            "current_stage_definition_id",
            self.current_stage_definition_id,
            limit=160,
        )

        if (
            isinstance(self.transition_count, bool)
            or not isinstance(self.transition_count, int)
            or self.transition_count < 0
        ):
            _fail(
                "G7G_R11_TRANSITION_COUNT_INVALID"
            )

        head_transition_id = self.head_transition_id
        head_transition_fingerprint = (
            self.head_transition_fingerprint
        )

        if self.transition_count == 0:
            if (
                head_transition_id is not None
                or head_transition_fingerprint is not None
            ):
                _fail(
                    "G7G_R11_EMPTY_HISTORY_HEAD_FORBIDDEN"
                )
        else:
            if head_transition_id is None:
                _fail(
                    "G7G_R11_HEAD_TRANSITION_ID_REQUIRED"
                )

            if head_transition_fingerprint is None:
                _fail(
                    "G7G_R11_HEAD_TRANSITION_FINGERPRINT_REQUIRED"
                )

            head_transition_id = _text(
                "head_transition_id",
                head_transition_id,
                limit=160,
            )

            head_transition_fingerprint = _fingerprint(
                "head_transition_fingerprint",
                head_transition_fingerprint,
            )

        if (
            self.schema != SCHEMA
            or self.currentness_version != VERSION
        ):
            _fail(
                "G7G_R11_IDENTITY_INVALID"
            )

        object.__setattr__(
            self,
            "currentness_id",
            currentness_id,
        )
        object.__setattr__(
            self,
            "tenant_id",
            tenant_id,
        )
        object.__setattr__(
            self,
            "case_matter_id",
            case_matter_id,
        )
        object.__setattr__(
            self,
            "workflow_instance_id",
            workflow_instance_id,
        )
        object.__setattr__(
            self,
            "workflow_instance_fingerprint",
            workflow_instance_fingerprint,
        )
        object.__setattr__(
            self,
            "workflow_topology_fingerprint",
            workflow_topology_fingerprint,
        )
        object.__setattr__(
            self,
            "current_stage_definition_id",
            current_stage_definition_id,
        )
        object.__setattr__(
            self,
            "head_transition_id",
            head_transition_id,
        )
        object.__setattr__(
            self,
            "head_transition_fingerprint",
            head_transition_fingerprint,
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
                    "G7G_R11_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    @classmethod
    def derive(
        cls,
        *,
        currentness_id: str,
        workflow_instance:
            LegalMatterWorkflowInstance,
        transitions: tuple[
            LegalMatterWorkflowTransition,
            ...
        ],
    ) -> "LegalMatterWorkflowCurrentness":
        """Derive exact current stage from one instance and complete history."""
        if not isinstance(
            transitions,
            tuple,
        ):
            _fail(
                "G7G_R11_TRANSITIONS_INVALID"
            )

        if not transitions:
            return cls(
                currentness_id=
                    currentness_id,
                tenant_id=
                    workflow_instance.tenant_id,
                case_matter_id=
                    workflow_instance.case_matter_id,
                workflow_instance_id=
                    workflow_instance.workflow_instance_id,
                workflow_instance_fingerprint=
                    workflow_instance.fingerprint,
                workflow_topology_fingerprint=
                    workflow_instance.workflow_topology_fingerprint,
                current_stage_definition_id=
                    workflow_instance.entry_stage_definition_id,
                transition_count=0,
                head_transition_id=None,
                head_transition_fingerprint=None,
            )

        ordered = tuple(
            sorted(
                transitions,
                key=lambda value:
                    value.sequence_number,
            )
        )

        seen_sequences: set[int] = set()
        seen_ids: set[str] = set()

        expected_source = (
            workflow_instance.entry_stage_definition_id
        )

        previous: (
            LegalMatterWorkflowTransition | None
        ) = None

        for index, transition in enumerate(
            ordered,
            1,
        ):
            if not isinstance(
                transition,
                LegalMatterWorkflowTransition,
            ):
                _fail(
                    "G7G_R11_TRANSITION_INVALID"
                )

            if (
                transition.sequence_number
                in seen_sequences
            ):
                _fail(
                    "G7G_R11_SEQUENCE_DUPLICATE"
                )

            seen_sequences.add(
                transition.sequence_number
            )

            if (
                transition.transition_id
                in seen_ids
            ):
                _fail(
                    "G7G_R11_TRANSITION_ID_DUPLICATE"
                )

            seen_ids.add(
                transition.transition_id
            )

            if transition.sequence_number != index:
                _fail(
                    "G7G_R11_SEQUENCE_GAP"
                )

            if (
                transition.tenant_id
                != workflow_instance.tenant_id
                or transition.case_matter_id
                != workflow_instance.case_matter_id
                or transition.workflow_instance_id
                != workflow_instance.workflow_instance_id
                or not hmac.compare_digest(
                    transition.workflow_instance_fingerprint,
                    workflow_instance.fingerprint,
                )
                or not hmac.compare_digest(
                    transition.workflow_topology_fingerprint,
                    workflow_instance.workflow_topology_fingerprint,
                )
            ):
                _fail(
                    "G7G_R11_TRANSITION_SCOPE_MISMATCH"
                )

            if (
                transition.source_stage_definition_id
                != expected_source
            ):
                _fail(
                    "G7G_R11_STAGE_CONTINUITY_INVALID"
                )

            if previous is None:
                if (
                    transition.previous_transition_fingerprint
                    is not None
                ):
                    _fail(
                        "G7G_R11_FIRST_PREVIOUS_FINGERPRINT_INVALID"
                    )
            else:
                if (
                    transition.previous_transition_fingerprint
                    is None
                    or not hmac.compare_digest(
                        transition.previous_transition_fingerprint,
                        previous.fingerprint,
                    )
                ):
                    _fail(
                        "G7G_R11_FINGERPRINT_CHAIN_INVALID"
                    )

                if (
                    previous.transitioned_at
                    >= transition.transitioned_at
                ):
                    _fail(
                        "G7G_R11_CHRONOLOGY_INVALID"
                    )

            expected_source = (
                transition.target_stage_definition_id
            )

            previous = transition

        if previous is None:
            raise AssertionError(
                "validated non-empty transition history lost head"
            )

        return cls(
            currentness_id=
                currentness_id,
            tenant_id=
                workflow_instance.tenant_id,
            case_matter_id=
                workflow_instance.case_matter_id,
            workflow_instance_id=
                workflow_instance.workflow_instance_id,
            workflow_instance_fingerprint=
                workflow_instance.fingerprint,
            workflow_topology_fingerprint=
                workflow_instance.workflow_topology_fingerprint,
            current_stage_definition_id=
                previous.target_stage_definition_id,
            transition_count=
                len(ordered),
            head_transition_id=
                previous.transition_id,
            head_transition_fingerprint=
                previous.fingerprint,
        )

    def semantic_dict(
        self,
    ) -> dict[str, object]:
        return {
            "schema":
                self.schema,
            "currentness_version":
                self.currentness_version,
            "currentness_id":
                self.currentness_id,
            "tenant_id":
                self.tenant_id,
            "case_matter_id":
                self.case_matter_id,
            "workflow_instance_id":
                self.workflow_instance_id,
            "workflow_instance_fingerprint":
                self.workflow_instance_fingerprint,
            "workflow_topology_fingerprint":
                self.workflow_topology_fingerprint,
            "current_stage_definition_id":
                self.current_stage_definition_id,
            "transition_count":
                self.transition_count,
            "head_transition_id":
                self.head_transition_id,
            "head_transition_fingerprint":
                self.head_transition_fingerprint,
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
    ) -> "LegalMatterWorkflowCurrentness":
        if not isinstance(value, dict):
            _fail(
                "G7G_R11_PAYLOAD_INVALID"
            )

        required = {
            "schema",
            "currentness_version",
            "currentness_id",
            "tenant_id",
            "case_matter_id",
            "workflow_instance_id",
            "workflow_instance_fingerprint",
            "workflow_topology_fingerprint",
            "current_stage_definition_id",
            "transition_count",
            "head_transition_id",
            "head_transition_fingerprint",
            "fingerprint",
        }

        if set(value) != required:
            _fail(
                "G7G_R11_PAYLOAD_SCHEMA_INVALID"
            )

        return cls(
            schema=value["schema"],
            currentness_version=value[
                "currentness_version"
            ],
            currentness_id=value[
                "currentness_id"
            ],
            tenant_id=value[
                "tenant_id"
            ],
            case_matter_id=value[
                "case_matter_id"
            ],
            workflow_instance_id=value[
                "workflow_instance_id"
            ],
            workflow_instance_fingerprint=value[
                "workflow_instance_fingerprint"
            ],
            workflow_topology_fingerprint=value[
                "workflow_topology_fingerprint"
            ],
            current_stage_definition_id=value[
                "current_stage_definition_id"
            ],
            transition_count=value[
                "transition_count"
            ],
            head_transition_id=value[
                "head_transition_id"
            ],
            head_transition_fingerprint=value[
                "head_transition_fingerprint"
            ],
            fingerprint=value[
                "fingerprint"
            ],
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalMatterWorkflowCurrentness",
    "LegalMatterWorkflowCurrentnessError",
]

# ARTIFACT: legal_matter_workflow_currentness.py
# VERSION: v1.0.1-G7G-R11-LEGAL-MATTER-WORKFLOW-CURRENTNESS
# AUTHORITY BOUNDARY: pure derived workflow currentness evidence only
# PERSISTENCE AUTHORITY: NONE
# PROGRESSION AUTHORITY: NONE
# WORK GENERATION AUTHORITY: NONE
# IAM AUTHORITY: NONE
# LEGAL EVENT AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# TENANT POSTURE: exact tenant correlation; cross-tenant inference prohibited
# FAIL-CLOSED POSTURE: malformed, incomplete, or divergent evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
