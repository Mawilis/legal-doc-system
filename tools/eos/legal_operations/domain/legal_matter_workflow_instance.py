"""TITLE: WILSY OS Legal Matter Workflow Instance Domain.

VERSION: v1.0.1-G7G-R6-LEGAL-MATTER-WORKFLOW-INSTANCE

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

EPITOME:
    Preserve the immutable start of one tenant Legal workflow instance for one
    exact case_matter_id.

    The instance start binds one exact TenantLegalWorkflowActivation, one exact
    LegalWorkflowDefinition revision, one exact certified LegalWorkflowTopology,
    and that topology's certified entry stage.

    This artifact creates no mutable current-stage state and owns no stage
    progression.

RUNTIME BOUNDARY:
    entry_stage_definition_id is the certified starting stage only.

    Future immutable transition evidence must separately prove progression from
    one stage to another. This domain does not contain current_stage_id, status,
    completion, terminal-state or transition authority.

MATTER BOUNDARY:
    case_matter_id is an exact correlation to canonical CaseMatter truth.
    This domain does not create or mutate matter state, matter authority,
    engagement, mandate, representation or any specialist Legal truth.

ACTIVATION BOUNDARY:
    Tenant workflow activation is configuration evidence only. Starting an
    instance does not create subscription, entitlement or IAM authority.

AUDIT:
    started_by_principal_id and start_authorization_evidence_reference record
    initiation audit evidence only. They are not reusable permission for later
    workflow or Legal commands.

WORK BOUNDARY:
    Instance creation does not create LegalWorkItem records, assignments,
    supervision bindings, deadlines, documents or automation executions.

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

from tools.eos.legal_operations.domain.legal_workflow_definition import (
    LegalWorkflowDefinition,
)
from tools.eos.legal_operations.domain.legal_workflow_topology import (
    LegalWorkflowTopology,
)
from tools.eos.legal_operations.domain.tenant_legal_workflow_activation import (
    TenantLegalWorkflowActivation,
)


VERSION: Final[str] = (
    "v1.0.1-G7G-R6-LEGAL-MATTER-WORKFLOW-INSTANCE"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-MATTER-WORKFLOW-INSTANCE/V1"
)


class LegalMatterWorkflowInstanceError(ValueError):
    """Stable fail-closed matter-workflow-instance start failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise LegalMatterWorkflowInstanceError(code)


def _text(
    name: str,
    value: object,
    *,
    limit: int = 320,
) -> str:
    if not isinstance(value, str):
        _fail(
            f"G7G_R6_{name.upper()}_INVALID"
        )

    normalized = value.strip()

    if (
        not normalized
        or normalized != value
        or len(normalized) > limit
    ):
        _fail(
            f"G7G_R6_{name.upper()}_INVALID"
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
        _fail("G7G_R6_TENANT_REQUIRED")

    return tenant


def _positive_int(
    name: str,
    value: object,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        _fail(
            f"G7G_R6_{name.upper()}_INVALID"
        )

    return value


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
            f"G7G_R6_{name.upper()}_INVALID"
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
            f"G7G_R6_{name.upper()}_INVALID"
        )

    try:
        int(value, 16)
    except ValueError as error:
        raise LegalMatterWorkflowInstanceError(
            f"G7G_R6_{name.upper()}_INVALID"
        ) from error

    return value


@dataclass(frozen=True, slots=True)
class LegalMatterWorkflowInstance:
    """Immutable initiation evidence for one matter workflow execution."""

    workflow_instance_id: str

    tenant_id: str
    case_matter_id: str

    activation_id: str
    activation_revision: int
    activation_fingerprint: str

    workflow_definition_id: str
    workflow_definition_revision: int
    workflow_definition_fingerprint: str
    workflow_topology_fingerprint: str

    entry_stage_definition_id: str

    started_at: datetime
    started_by_principal_id: str
    start_authorization_evidence_reference: str

    schema: str = SCHEMA
    workflow_instance_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        workflow_instance_id = _text(
            "workflow_instance_id",
            self.workflow_instance_id,
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

        activation_id = _text(
            "activation_id",
            self.activation_id,
            limit=160,
        )

        activation_revision = _positive_int(
            "activation_revision",
            self.activation_revision,
        )

        activation_fingerprint = _fingerprint(
            "activation_fingerprint",
            self.activation_fingerprint,
        )

        workflow_definition_id = _text(
            "workflow_definition_id",
            self.workflow_definition_id,
            limit=160,
        )

        workflow_definition_revision = _positive_int(
            "workflow_definition_revision",
            self.workflow_definition_revision,
        )

        workflow_definition_fingerprint = _fingerprint(
            "workflow_definition_fingerprint",
            self.workflow_definition_fingerprint,
        )

        workflow_topology_fingerprint = _fingerprint(
            "workflow_topology_fingerprint",
            self.workflow_topology_fingerprint,
        )

        entry_stage_definition_id = _text(
            "entry_stage_definition_id",
            self.entry_stage_definition_id,
            limit=160,
        )

        started_at = _timestamp(
            "started_at",
            self.started_at,
        )

        started_by_principal_id = _text(
            "started_by_principal_id",
            self.started_by_principal_id,
            limit=160,
        )

        start_authorization_reference = _text(
            "start_authorization_evidence_reference",
            self.start_authorization_evidence_reference,
        )

        if (
            self.schema != SCHEMA
            or self.workflow_instance_version
            != VERSION
        ):
            _fail(
                "G7G_R6_IDENTITY_INVALID"
            )

        object.__setattr__(
            self,
            "workflow_instance_id",
            workflow_instance_id,
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
            "activation_id",
            activation_id,
        )
        object.__setattr__(
            self,
            "activation_revision",
            activation_revision,
        )
        object.__setattr__(
            self,
            "activation_fingerprint",
            activation_fingerprint,
        )
        object.__setattr__(
            self,
            "workflow_definition_id",
            workflow_definition_id,
        )
        object.__setattr__(
            self,
            "workflow_definition_revision",
            workflow_definition_revision,
        )
        object.__setattr__(
            self,
            "workflow_definition_fingerprint",
            workflow_definition_fingerprint,
        )
        object.__setattr__(
            self,
            "workflow_topology_fingerprint",
            workflow_topology_fingerprint,
        )
        object.__setattr__(
            self,
            "entry_stage_definition_id",
            entry_stage_definition_id,
        )
        object.__setattr__(
            self,
            "started_at",
            started_at,
        )
        object.__setattr__(
            self,
            "started_by_principal_id",
            started_by_principal_id,
        )
        object.__setattr__(
            self,
            "start_authorization_evidence_reference",
            start_authorization_reference,
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
                    "G7G_R6_FINGERPRINT_MISMATCH"
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
        workflow_instance_id: str,
        case_matter_id: str,
        activation: TenantLegalWorkflowActivation,
        workflow_definition: LegalWorkflowDefinition,
        workflow_topology: LegalWorkflowTopology,
        started_at: datetime,
        started_by_principal_id: str,
        start_authorization_evidence_reference: str,
    ) -> "LegalMatterWorkflowInstance":
        """Bind one exact activation/topology to one matter without progressing."""
        if (
            activation.workflow_definition_id
            != workflow_definition.workflow_definition_id
            or activation.workflow_definition_revision
            != workflow_definition.definition_revision
            or not hmac.compare_digest(
                activation.workflow_definition_fingerprint,
                workflow_definition.fingerprint,
            )
        ):
            _fail(
                "G7G_R6_ACTIVATION_DEFINITION_BINDING_MISMATCH"
            )

        if (
            workflow_topology.workflow_definition_id
            != workflow_definition.workflow_definition_id
            or workflow_topology.definition_revision
            != workflow_definition.definition_revision
            or not hmac.compare_digest(
                workflow_topology.workflow_definition_fingerprint,
                workflow_definition.fingerprint,
            )
        ):
            _fail(
                "G7G_R6_TOPOLOGY_DEFINITION_BINDING_MISMATCH"
            )

        if not hmac.compare_digest(
            activation.workflow_topology_fingerprint,
            workflow_topology.fingerprint,
        ):
            _fail(
                "G7G_R6_ACTIVATION_TOPOLOGY_BINDING_MISMATCH"
            )

        return cls(
            workflow_instance_id=
                workflow_instance_id,
            tenant_id=
                activation.tenant_id,
            case_matter_id=
                case_matter_id,
            activation_id=
                activation.activation_id,
            activation_revision=
                activation.activation_revision,
            activation_fingerprint=
                activation.fingerprint,
            workflow_definition_id=
                workflow_definition.workflow_definition_id,
            workflow_definition_revision=
                workflow_definition.definition_revision,
            workflow_definition_fingerprint=
                workflow_definition.fingerprint,
            workflow_topology_fingerprint=
                workflow_topology.fingerprint,
            entry_stage_definition_id=
                workflow_topology.entry_stage_definition_id,
            started_at=
                started_at,
            started_by_principal_id=
                started_by_principal_id,
            start_authorization_evidence_reference=
                start_authorization_evidence_reference,
        )

    def semantic_dict(
        self,
    ) -> dict[str, object]:
        return {
            "schema":
                self.schema,
            "workflow_instance_version":
                self.workflow_instance_version,
            "workflow_instance_id":
                self.workflow_instance_id,
            "tenant_id":
                self.tenant_id,
            "case_matter_id":
                self.case_matter_id,
            "activation_id":
                self.activation_id,
            "activation_revision":
                self.activation_revision,
            "activation_fingerprint":
                self.activation_fingerprint,
            "workflow_definition_id":
                self.workflow_definition_id,
            "workflow_definition_revision":
                self.workflow_definition_revision,
            "workflow_definition_fingerprint":
                self.workflow_definition_fingerprint,
            "workflow_topology_fingerprint":
                self.workflow_topology_fingerprint,
            "entry_stage_definition_id":
                self.entry_stage_definition_id,
            "started_at":
                self.started_at.isoformat(),
            "started_by_principal_id":
                self.started_by_principal_id,
            "start_authorization_evidence_reference":
                self.start_authorization_evidence_reference,
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
    ) -> "LegalMatterWorkflowInstance":
        if not isinstance(value, dict):
            _fail(
                "G7G_R6_PAYLOAD_INVALID"
            )

        required = {
            "schema",
            "workflow_instance_version",
            "workflow_instance_id",
            "tenant_id",
            "case_matter_id",
            "activation_id",
            "activation_revision",
            "activation_fingerprint",
            "workflow_definition_id",
            "workflow_definition_revision",
            "workflow_definition_fingerprint",
            "workflow_topology_fingerprint",
            "entry_stage_definition_id",
            "started_at",
            "started_by_principal_id",
            "start_authorization_evidence_reference",
            "fingerprint",
        }

        if set(value) != required:
            _fail(
                "G7G_R6_PAYLOAD_SCHEMA_INVALID"
            )

        raw_started = value[
            "started_at"
        ]

        if not isinstance(
            raw_started,
            str,
        ):
            _fail(
                "G7G_R6_STARTED_AT_INVALID"
            )

        try:
            started_at = datetime.fromisoformat(
                raw_started
            )
        except ValueError as error:
            raise LegalMatterWorkflowInstanceError(
                "G7G_R6_STARTED_AT_INVALID"
            ) from error

        return cls(
            schema=value["schema"],
            workflow_instance_version=value[
                "workflow_instance_version"
            ],
            workflow_instance_id=value[
                "workflow_instance_id"
            ],
            tenant_id=value[
                "tenant_id"
            ],
            case_matter_id=value[
                "case_matter_id"
            ],
            activation_id=value[
                "activation_id"
            ],
            activation_revision=value[
                "activation_revision"
            ],
            activation_fingerprint=value[
                "activation_fingerprint"
            ],
            workflow_definition_id=value[
                "workflow_definition_id"
            ],
            workflow_definition_revision=value[
                "workflow_definition_revision"
            ],
            workflow_definition_fingerprint=value[
                "workflow_definition_fingerprint"
            ],
            workflow_topology_fingerprint=value[
                "workflow_topology_fingerprint"
            ],
            entry_stage_definition_id=value[
                "entry_stage_definition_id"
            ],
            started_at=
                started_at,
            started_by_principal_id=value[
                "started_by_principal_id"
            ],
            start_authorization_evidence_reference=value[
                "start_authorization_evidence_reference"
            ],
            fingerprint=value[
                "fingerprint"
            ],
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalMatterWorkflowInstance",
    "LegalMatterWorkflowInstanceError",
]

# ARTIFACT: legal_matter_workflow_instance.py
# VERSION: v1.0.1-G7G-R6-LEGAL-MATTER-WORKFLOW-INSTANCE
# AUTHORITY BOUNDARY: immutable workflow-instance start evidence only
# CURRENT-STAGE AUTHORITY: NONE
# PROGRESSION AUTHORITY: NONE
# WORK GENERATION AUTHORITY: NONE
# LEGAL EVENT AUTHORITY: NONE
# IAM AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# TENANT POSTURE: exact tenant correlation; cross-tenant inference prohibited
# FAIL-CLOSED POSTURE: malformed, incomplete, or divergent evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
