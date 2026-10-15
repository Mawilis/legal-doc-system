"""TITLE: WILSY OS Legal Workflow Gate Satisfaction Domain.

VERSION: v1.0.1-G7G-R9-LEGAL-WORKFLOW-GATE-SATISFACTION

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

EPITOME:
    Preserve one immutable positive workflow completion-gate satisfaction fact
    for one exact matter workflow instance and one exact source stage.

    The value proves only that future server-side orchestration evaluated one
    configured completion gate against exact canonical evidence fingerprints
    and admitted that gate as satisfied at one evaluation time.

    It does not create the underlying canonical evidence.

BINDING:
    Satisfaction binds:
      - exact tenant and case_matter_id,
      - exact LegalMatterWorkflowInstance identity/fingerprint,
      - exact workflow topology fingerprint,
      - exact source LegalWorkflowStage identity/fingerprint,
      - one gate_reference declared by that source stage,
      - one or more typed canonical evidence bindings.

CANONICAL EVIDENCE:
    Each evidence binding contains:
      evidence_kind,
      evidence_reference,
      evidence_fingerprint.

    evidence_kind and evidence_reference are opaque identifiers naming
    canonical upstream evidence. The fingerprint is exact lowercase SHA3-512
    integrity evidence.

    This domain does not interpret specialist Legal semantics.

POSITIVE-FACT MODEL:
    There is no SATISFIED/UNSATISFIED boolean or mutable status.

    Existence of a valid LegalWorkflowGateSatisfaction means that exact gate
    evaluation succeeded. Failed gate evaluation produces no satisfaction fact
    and therefore cannot be mistaken for positive evidence.

CURRENTNESS / TRANSITION:
    This artifact does not progress the workflow, choose branches, establish
    current stage, generate work, or complete a workflow.

AUTHORIZATION:
    evaluated_by_principal_id and evaluation_authorization_evidence_reference
    are audit provenance only. They do not create or persist IAM authority.

FINANCIAL AUTHORITY:
    None. Kennel EOS remains exclusive financial execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
import hmac
import json
from typing import Final, NoReturn

from tools.eos.legal_operations.domain.legal_matter_workflow_instance import (
    LegalMatterWorkflowInstance,
)
from tools.eos.legal_operations.domain.legal_workflow_stage import (
    LegalWorkflowStage,
)
from tools.eos.legal_operations.domain.legal_workflow_topology import (
    LegalWorkflowTopology,
)


VERSION: Final[str] = (
    "v1.0.1-G7G-R9-LEGAL-WORKFLOW-GATE-SATISFACTION"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-WORKFLOW-GATE-SATISFACTION/V1"
)


class LegalWorkflowGateSatisfactionError(ValueError):
    """Stable fail-closed workflow-gate satisfaction failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise LegalWorkflowGateSatisfactionError(code)


def _text(
    name: str,
    value: object,
    *,
    limit: int = 320,
) -> str:
    if not isinstance(value, str):
        _fail(
            f"G7G_R9_{name.upper()}_INVALID"
        )

    normalized = value.strip()

    if (
        not normalized
        or normalized != value
        or len(normalized) > limit
    ):
        _fail(
            f"G7G_R9_{name.upper()}_INVALID"
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
        _fail("G7G_R9_TENANT_REQUIRED")

    return tenant


def _timestamp(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            f"G7G_R9_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


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
            f"G7G_R9_{name.upper()}_INVALID"
        )

    try:
        int(value, 16)
    except ValueError as error:
        raise LegalWorkflowGateSatisfactionError(
            f"G7G_R9_{name.upper()}_INVALID"
        ) from error

    return value


@dataclass(frozen=True, slots=True)
class LegalWorkflowGateEvidence:
    """One exact canonical evidence binding used by a gate evaluation."""

    evidence_kind: str
    evidence_reference: str
    evidence_fingerprint: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "evidence_kind",
            _text(
                "evidence_kind",
                self.evidence_kind,
                limit=160,
            ),
        )

        object.__setattr__(
            self,
            "evidence_reference",
            _text(
                "evidence_reference",
                self.evidence_reference,
            ),
        )

        object.__setattr__(
            self,
            "evidence_fingerprint",
            _fingerprint(
                "evidence_fingerprint",
                self.evidence_fingerprint,
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "evidence_kind":
                self.evidence_kind,
            "evidence_reference":
                self.evidence_reference,
            "evidence_fingerprint":
                self.evidence_fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalWorkflowGateEvidence":
        if not isinstance(value, dict):
            _fail(
                "G7G_R9_EVIDENCE_PAYLOAD_INVALID"
            )

        required = {
            "evidence_kind",
            "evidence_reference",
            "evidence_fingerprint",
        }

        if set(value) != required:
            _fail(
                "G7G_R9_EVIDENCE_PAYLOAD_SCHEMA_INVALID"
            )

        return cls(
            evidence_kind=value[
                "evidence_kind"
            ],
            evidence_reference=value[
                "evidence_reference"
            ],
            evidence_fingerprint=value[
                "evidence_fingerprint"
            ],
        )


@dataclass(frozen=True, slots=True)
class LegalWorkflowGateSatisfaction:
    """One immutable positive gate-satisfaction fact."""

    gate_satisfaction_id: str

    tenant_id: str
    case_matter_id: str

    workflow_instance_id: str
    workflow_instance_fingerprint: str
    workflow_topology_fingerprint: str

    source_stage_definition_id: str
    source_stage_fingerprint: str

    gate_reference: str

    canonical_evidence: tuple[
        LegalWorkflowGateEvidence,
        ...
    ]

    evaluated_at: datetime
    evaluated_by_principal_id: str
    evaluation_authorization_evidence_reference: str

    schema: str = SCHEMA
    gate_satisfaction_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        satisfaction_id = _text(
            "gate_satisfaction_id",
            self.gate_satisfaction_id,
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

        source_stage_definition_id = _text(
            "source_stage_definition_id",
            self.source_stage_definition_id,
            limit=160,
        )

        source_stage_fingerprint = _fingerprint(
            "source_stage_fingerprint",
            self.source_stage_fingerprint,
        )

        gate_reference = _text(
            "gate_reference",
            self.gate_reference,
        )

        if not isinstance(
            self.canonical_evidence,
            tuple,
        ):
            _fail(
                "G7G_R9_CANONICAL_EVIDENCE_INVALID"
            )

        if not self.canonical_evidence:
            _fail(
                "G7G_R9_CANONICAL_EVIDENCE_REQUIRED"
            )

        evidence: list[
            LegalWorkflowGateEvidence
        ] = []

        seen: set[
            tuple[str, str, str]
        ] = set()

        for value in self.canonical_evidence:
            if not isinstance(
                value,
                LegalWorkflowGateEvidence,
            ):
                _fail(
                    "G7G_R9_CANONICAL_EVIDENCE_INVALID"
                )

            identity = (
                value.evidence_kind,
                value.evidence_reference,
                value.evidence_fingerprint,
            )

            if identity in seen:
                _fail(
                    "G7G_R9_CANONICAL_EVIDENCE_DUPLICATE"
                )

            seen.add(identity)
            evidence.append(value)

        canonical_evidence = tuple(
            sorted(
                evidence,
                key=lambda item: (
                    item.evidence_kind,
                    item.evidence_reference,
                    item.evidence_fingerprint,
                ),
            )
        )

        evaluated_at = _timestamp(
            "evaluated_at",
            self.evaluated_at,
        )

        evaluated_by_principal_id = _text(
            "evaluated_by_principal_id",
            self.evaluated_by_principal_id,
            limit=160,
        )

        authorization_reference = _text(
            "evaluation_authorization_evidence_reference",
            self.evaluation_authorization_evidence_reference,
        )

        if (
            self.schema != SCHEMA
            or self.gate_satisfaction_version
            != VERSION
        ):
            _fail(
                "G7G_R9_IDENTITY_INVALID"
            )

        object.__setattr__(
            self,
            "gate_satisfaction_id",
            satisfaction_id,
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
            "source_stage_definition_id",
            source_stage_definition_id,
        )
        object.__setattr__(
            self,
            "source_stage_fingerprint",
            source_stage_fingerprint,
        )
        object.__setattr__(
            self,
            "gate_reference",
            gate_reference,
        )
        object.__setattr__(
            self,
            "canonical_evidence",
            canonical_evidence,
        )
        object.__setattr__(
            self,
            "evaluated_at",
            evaluated_at,
        )
        object.__setattr__(
            self,
            "evaluated_by_principal_id",
            evaluated_by_principal_id,
        )
        object.__setattr__(
            self,
            "evaluation_authorization_evidence_reference",
            authorization_reference,
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
                    "G7G_R9_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    @classmethod
    def from_authorities(
        cls,
        *,
        gate_satisfaction_id: str,
        workflow_instance:
            LegalMatterWorkflowInstance,
        workflow_topology:
            LegalWorkflowTopology,
        source_stage:
            LegalWorkflowStage,
        gate_reference: str,
        canonical_evidence: tuple[
            LegalWorkflowGateEvidence,
            ...
        ],
        evaluated_at: datetime,
        evaluated_by_principal_id: str,
        evaluation_authorization_evidence_reference: str,
    ) -> "LegalWorkflowGateSatisfaction":
        """Bind one configured gate to exact canonical evidence."""
        if not hmac.compare_digest(
            workflow_instance.workflow_topology_fingerprint,
            workflow_topology.fingerprint,
        ):
            _fail(
                "G7G_R9_INSTANCE_TOPOLOGY_BINDING_MISMATCH"
            )

        if (
            source_stage.workflow_definition_id
            != workflow_topology.workflow_definition_id
            or source_stage.definition_revision
            != workflow_topology.definition_revision
            or not hmac.compare_digest(
                source_stage.workflow_definition_fingerprint,
                workflow_topology.workflow_definition_fingerprint,
            )
        ):
            _fail(
                "G7G_R9_STAGE_TOPOLOGY_BINDING_MISMATCH"
            )

        topology_stage = None

        for value in workflow_topology.stages:
            if (
                value.stage_definition_id
                == source_stage.stage_definition_id
            ):
                topology_stage = value
                break

        if topology_stage is None:
            _fail(
                "G7G_R9_STAGE_NOT_IN_TOPOLOGY"
            )

        if not hmac.compare_digest(
            topology_stage.stage_fingerprint,
            source_stage.fingerprint,
        ):
            _fail(
                "G7G_R9_STAGE_FINGERPRINT_MISMATCH"
            )

        normalized_gate = _text(
            "gate_reference",
            gate_reference,
        )

        if (
            normalized_gate
            not in source_stage.completion_gate_references
        ):
            _fail(
                "G7G_R9_GATE_NOT_CONFIGURED_ON_STAGE"
            )

        return cls(
            gate_satisfaction_id=
                gate_satisfaction_id,
            tenant_id=
                workflow_instance.tenant_id,
            case_matter_id=
                workflow_instance.case_matter_id,
            workflow_instance_id=
                workflow_instance.workflow_instance_id,
            workflow_instance_fingerprint=
                workflow_instance.fingerprint,
            workflow_topology_fingerprint=
                workflow_topology.fingerprint,
            source_stage_definition_id=
                source_stage.stage_definition_id,
            source_stage_fingerprint=
                source_stage.fingerprint,
            gate_reference=
                normalized_gate,
            canonical_evidence=
                canonical_evidence,
            evaluated_at=
                evaluated_at,
            evaluated_by_principal_id=
                evaluated_by_principal_id,
            evaluation_authorization_evidence_reference=
                evaluation_authorization_evidence_reference,
        )

    def semantic_dict(
        self,
    ) -> dict[str, object]:
        return {
            "schema":
                self.schema,
            "gate_satisfaction_version":
                self.gate_satisfaction_version,
            "gate_satisfaction_id":
                self.gate_satisfaction_id,
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
            "source_stage_definition_id":
                self.source_stage_definition_id,
            "source_stage_fingerprint":
                self.source_stage_fingerprint,
            "gate_reference":
                self.gate_reference,
            "canonical_evidence": [
                value.to_dict()
                for value in self.canonical_evidence
            ],
            "evaluated_at":
                self.evaluated_at.isoformat(),
            "evaluated_by_principal_id":
                self.evaluated_by_principal_id,
            "evaluation_authorization_evidence_reference":
                self.evaluation_authorization_evidence_reference,
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
    ) -> "LegalWorkflowGateSatisfaction":
        if not isinstance(value, dict):
            _fail(
                "G7G_R9_PAYLOAD_INVALID"
            )

        required = {
            "schema",
            "gate_satisfaction_version",
            "gate_satisfaction_id",
            "tenant_id",
            "case_matter_id",
            "workflow_instance_id",
            "workflow_instance_fingerprint",
            "workflow_topology_fingerprint",
            "source_stage_definition_id",
            "source_stage_fingerprint",
            "gate_reference",
            "canonical_evidence",
            "evaluated_at",
            "evaluated_by_principal_id",
            "evaluation_authorization_evidence_reference",
            "fingerprint",
        }

        if set(value) != required:
            _fail(
                "G7G_R9_PAYLOAD_SCHEMA_INVALID"
            )

        raw_evidence = value[
            "canonical_evidence"
        ]

        if not isinstance(
            raw_evidence,
            list,
        ):
            _fail(
                "G7G_R9_CANONICAL_EVIDENCE_INVALID"
            )

        parsed_evidence: list[
            LegalWorkflowGateEvidence
        ] = []

        for raw in raw_evidence:
            parsed_evidence.append(
                LegalWorkflowGateEvidence.from_dict(
                    raw
                )
            )

        raw_evaluated_at = value[
            "evaluated_at"
        ]

        if not isinstance(
            raw_evaluated_at,
            str,
        ):
            _fail(
                "G7G_R9_EVALUATED_AT_INVALID"
            )

        try:
            evaluated_at = datetime.fromisoformat(
                raw_evaluated_at
            )
        except ValueError as error:
            raise LegalWorkflowGateSatisfactionError(
                "G7G_R9_EVALUATED_AT_INVALID"
            ) from error

        return cls(
            schema=value["schema"],
            gate_satisfaction_version=value[
                "gate_satisfaction_version"
            ],
            gate_satisfaction_id=value[
                "gate_satisfaction_id"
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
            source_stage_definition_id=value[
                "source_stage_definition_id"
            ],
            source_stage_fingerprint=value[
                "source_stage_fingerprint"
            ],
            gate_reference=value[
                "gate_reference"
            ],
            canonical_evidence=tuple(
                parsed_evidence
            ),
            evaluated_at=
                evaluated_at,
            evaluated_by_principal_id=value[
                "evaluated_by_principal_id"
            ],
            evaluation_authorization_evidence_reference=value[
                "evaluation_authorization_evidence_reference"
            ],
            fingerprint=value[
                "fingerprint"
            ],
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalWorkflowGateEvidence",
    "LegalWorkflowGateSatisfaction",
    "LegalWorkflowGateSatisfactionError",
]

# ARTIFACT: legal_workflow_gate_satisfaction.py
# VERSION: v1.0.1-G7G-R9-LEGAL-WORKFLOW-GATE-SATISFACTION
# AUTHORITY BOUNDARY: immutable positive gate-evaluation evidence only
# CANONICAL LEGAL EVIDENCE CREATION: NONE
# TRANSITION AUTHORITY: NONE
# CURRENTNESS AUTHORITY: NONE
# WORK GENERATION AUTHORITY: NONE
# IAM AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# TENANT POSTURE: exact tenant correlation; cross-tenant inference prohibited
# FAIL-CLOSED POSTURE: malformed, incomplete, or divergent evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
