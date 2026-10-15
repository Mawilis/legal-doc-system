"""TITLE: WILSY OS Tenant Legal Workflow Activation Domain.

VERSION: v1.0.1-G7G-R5-TENANT-LEGAL-WORKFLOW-ACTIVATION

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

EPITOME:
    Preserve one immutable tenant decision to activate one exact certified
    Legal workflow definition/topology against one exact Tenant Legal Operating
    Model revision.

    Activation establishes tenant workflow configuration only.

    It does not establish subscription ownership, product entitlement, IAM,
    principal assignment, professional authority, supervision, runtime workflow
    state, Legal-event truth, work generation, billing, payment, settlement or
    financial-execution authority.

TENANT OPERATING-MODEL BINDING:
    The activation binds one exact TenantLegalOperatingModel identity, revision
    and fingerprint.

    Every workflow required_operating_item_id must already appear in the bound
    operating model's activated_item_ids.

WORKFLOW BINDING:
    The activation binds one exact LegalWorkflowDefinition identity, revision
    and fingerprint and one exact certified LegalWorkflowTopology fingerprint.

    Workflow topology must itself bind the same definition revision.

OWNERSHIP:
    PLATFORM workflow definitions may be activated by any exact tenant after
    future orchestration validates commercial eligibility and other issuance
    conditions.

    TENANT workflow definitions may only be activated by their exact owner
    tenant.

COMMERCIAL BOUNDARY:
    commercial_eligibility_evidence_reference preserves an opaque reference to
    evidence that future orchestration validated before issuance.

    This domain does not interpret Plan, Subscription, Product Entitlement,
    price, quota or billing truth.

CURRENTNESS:
    No activation self-declares current. Immutable revision/effective chronology
    and supersession evidence will later allow the registry/orchestration layer
    to derive current activation.

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
    LegalWorkflowDefinitionOwner,
)
from tools.eos.legal_operations.domain.legal_workflow_topology import (
    LegalWorkflowTopology,
)
from tools.eos.legal_operations.domain.tenant_legal_operating_model import (
    TenantLegalOperatingModel,
)


VERSION: Final[str] = (
    "v1.0.1-G7G-R5-TENANT-LEGAL-WORKFLOW-ACTIVATION"
)
SCHEMA: Final[str] = (
    "WILSY-TENANT-LEGAL-WORKFLOW-ACTIVATION/V1"
)


class TenantLegalWorkflowActivationError(ValueError):
    """Stable fail-closed tenant workflow-activation failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise TenantLegalWorkflowActivationError(code)


def _text(
    name: str,
    value: object,
    *,
    limit: int = 320,
) -> str:
    if not isinstance(value, str):
        _fail(
            f"G7G_R5_{name.upper()}_INVALID"
        )

    normalized = value.strip()

    if (
        not normalized
        or normalized != value
        or len(normalized) > limit
    ):
        _fail(
            f"G7G_R5_{name.upper()}_INVALID"
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
        _fail("G7G_R5_TENANT_REQUIRED")

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
            f"G7G_R5_{name.upper()}_INVALID"
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
            f"G7G_R5_{name.upper()}_INVALID"
        )

    return value.astimezone(timezone.utc)


def _optional_text(
    name: str,
    value: object,
    *,
    limit: int = 320,
) -> str | None:
    if value is None:
        return None

    return _text(
        name,
        value,
        limit=limit,
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
            f"G7G_R5_{name.upper()}_INVALID"
        )

    try:
        int(value, 16)
    except ValueError as error:
        raise TenantLegalWorkflowActivationError(
            f"G7G_R5_{name.upper()}_INVALID"
        ) from error

    return value


@dataclass(frozen=True, slots=True)
class TenantLegalWorkflowActivation:
    """One immutable tenant workflow-activation revision."""

    activation_id: str
    tenant_id: str
    activation_revision: int

    operating_model_id: str
    operating_model_revision: int
    operating_model_fingerprint: str

    workflow_definition_id: str
    workflow_definition_revision: int
    workflow_definition_fingerprint: str
    workflow_topology_fingerprint: str

    commercial_eligibility_evidence_reference: str
    activation_reason_reference: str

    effective_from: datetime

    supersedes_activation_id: str | None = None

    schema: str = SCHEMA
    activation_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        activation_id = _text(
            "activation_id",
            self.activation_id,
            limit=160,
        )

        tenant_id = _tenant(
            self.tenant_id
        )

        activation_revision = _positive_int(
            "activation_revision",
            self.activation_revision,
        )

        operating_model_id = _text(
            "operating_model_id",
            self.operating_model_id,
            limit=160,
        )

        operating_model_revision = _positive_int(
            "operating_model_revision",
            self.operating_model_revision,
        )

        operating_model_fingerprint = _fingerprint(
            "operating_model_fingerprint",
            self.operating_model_fingerprint,
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

        commercial_reference = _text(
            "commercial_eligibility_evidence_reference",
            self.commercial_eligibility_evidence_reference,
        )

        reason_reference = _text(
            "activation_reason_reference",
            self.activation_reason_reference,
        )

        effective_from = _timestamp(
            "effective_from",
            self.effective_from,
        )

        supersedes = _optional_text(
            "supersedes_activation_id",
            self.supersedes_activation_id,
            limit=160,
        )

        if (
            supersedes is not None
            and hmac.compare_digest(
                supersedes,
                activation_id,
            )
        ):
            _fail(
                "G7G_R5_SELF_SUPERSESSION_INVALID"
            )

        if (
            self.schema != SCHEMA
            or self.activation_version
            != VERSION
        ):
            _fail(
                "G7G_R5_IDENTITY_INVALID"
            )

        object.__setattr__(
            self,
            "activation_id",
            activation_id,
        )
        object.__setattr__(
            self,
            "tenant_id",
            tenant_id,
        )
        object.__setattr__(
            self,
            "activation_revision",
            activation_revision,
        )
        object.__setattr__(
            self,
            "operating_model_id",
            operating_model_id,
        )
        object.__setattr__(
            self,
            "operating_model_revision",
            operating_model_revision,
        )
        object.__setattr__(
            self,
            "operating_model_fingerprint",
            operating_model_fingerprint,
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
            "commercial_eligibility_evidence_reference",
            commercial_reference,
        )
        object.__setattr__(
            self,
            "activation_reason_reference",
            reason_reference,
        )
        object.__setattr__(
            self,
            "effective_from",
            effective_from,
        )
        object.__setattr__(
            self,
            "supersedes_activation_id",
            supersedes,
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
                    "G7G_R5_FINGERPRINT_MISMATCH"
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
        activation_id: str,
        activation_revision: int,
        operating_model: TenantLegalOperatingModel,
        workflow_definition: LegalWorkflowDefinition,
        workflow_topology: LegalWorkflowTopology,
        commercial_eligibility_evidence_reference: str,
        activation_reason_reference: str,
        effective_from: datetime,
        supersedes_activation_id: str | None = None,
    ) -> "TenantLegalWorkflowActivation":
        """Bind exact configuration evidence without manufacturing authority."""
        tenant_id = operating_model.tenant_id

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
                "G7G_R5_TOPOLOGY_DEFINITION_BINDING_MISMATCH"
            )

        owner = LegalWorkflowDefinitionOwner(
            workflow_definition.owner
        )

        if (
            owner is LegalWorkflowDefinitionOwner.TENANT
            and workflow_definition.owner_tenant_id
            != tenant_id
        ):
            _fail(
                "G7G_R5_TENANT_WORKFLOW_OWNER_MISMATCH"
            )

        activated = set(
            operating_model.activated_item_ids
        )

        required = set(
            workflow_definition.required_operating_item_ids
        )

        if not required.issubset(
            activated
        ):
            _fail(
                "G7G_R5_OPERATING_MODEL_CAPABILITY_MISMATCH"
            )

        return cls(
            activation_id=activation_id,
            tenant_id=tenant_id,
            activation_revision=activation_revision,
            operating_model_id=
                operating_model.operating_model_id,
            operating_model_revision=
                operating_model.revision,
            operating_model_fingerprint=
                operating_model.fingerprint,
            workflow_definition_id=
                workflow_definition.workflow_definition_id,
            workflow_definition_revision=
                workflow_definition.definition_revision,
            workflow_definition_fingerprint=
                workflow_definition.fingerprint,
            workflow_topology_fingerprint=
                workflow_topology.fingerprint,
            commercial_eligibility_evidence_reference=
                commercial_eligibility_evidence_reference,
            activation_reason_reference=
                activation_reason_reference,
            effective_from=effective_from,
            supersedes_activation_id=
                supersedes_activation_id,
        )

    def semantic_dict(
        self,
    ) -> dict[str, object]:
        return {
            "schema":
                self.schema,
            "activation_version":
                self.activation_version,
            "activation_id":
                self.activation_id,
            "tenant_id":
                self.tenant_id,
            "activation_revision":
                self.activation_revision,
            "operating_model_id":
                self.operating_model_id,
            "operating_model_revision":
                self.operating_model_revision,
            "operating_model_fingerprint":
                self.operating_model_fingerprint,
            "workflow_definition_id":
                self.workflow_definition_id,
            "workflow_definition_revision":
                self.workflow_definition_revision,
            "workflow_definition_fingerprint":
                self.workflow_definition_fingerprint,
            "workflow_topology_fingerprint":
                self.workflow_topology_fingerprint,
            "commercial_eligibility_evidence_reference":
                self.commercial_eligibility_evidence_reference,
            "activation_reason_reference":
                self.activation_reason_reference,
            "effective_from":
                self.effective_from.isoformat(),
            "supersedes_activation_id":
                self.supersedes_activation_id,
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
    ) -> "TenantLegalWorkflowActivation":
        if not isinstance(value, dict):
            _fail(
                "G7G_R5_PAYLOAD_INVALID"
            )

        required = {
            "schema",
            "activation_version",
            "activation_id",
            "tenant_id",
            "activation_revision",
            "operating_model_id",
            "operating_model_revision",
            "operating_model_fingerprint",
            "workflow_definition_id",
            "workflow_definition_revision",
            "workflow_definition_fingerprint",
            "workflow_topology_fingerprint",
            "commercial_eligibility_evidence_reference",
            "activation_reason_reference",
            "effective_from",
            "supersedes_activation_id",
            "fingerprint",
        }

        if set(value) != required:
            _fail(
                "G7G_R5_PAYLOAD_SCHEMA_INVALID"
            )

        raw_effective = value[
            "effective_from"
        ]

        if not isinstance(
            raw_effective,
            str,
        ):
            _fail(
                "G7G_R5_EFFECTIVE_FROM_INVALID"
            )

        try:
            effective_from = datetime.fromisoformat(
                raw_effective
            )
        except ValueError as error:
            raise TenantLegalWorkflowActivationError(
                "G7G_R5_EFFECTIVE_FROM_INVALID"
            ) from error

        return cls(
            schema=value["schema"],
            activation_version=value[
                "activation_version"
            ],
            activation_id=value[
                "activation_id"
            ],
            tenant_id=value[
                "tenant_id"
            ],
            activation_revision=value[
                "activation_revision"
            ],
            operating_model_id=value[
                "operating_model_id"
            ],
            operating_model_revision=value[
                "operating_model_revision"
            ],
            operating_model_fingerprint=value[
                "operating_model_fingerprint"
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
            commercial_eligibility_evidence_reference=value[
                "commercial_eligibility_evidence_reference"
            ],
            activation_reason_reference=value[
                "activation_reason_reference"
            ],
            effective_from=effective_from,
            supersedes_activation_id=value[
                "supersedes_activation_id"
            ],
            fingerprint=value[
                "fingerprint"
            ],
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "TenantLegalWorkflowActivation",
    "TenantLegalWorkflowActivationError",
]

# ARTIFACT: tenant_legal_workflow_activation.py
# VERSION: v1.0.1-G7G-R5-TENANT-LEGAL-WORKFLOW-ACTIVATION
# AUTHORITY BOUNDARY: immutable tenant workflow configuration evidence only
# SUBSCRIPTION AUTHORITY: NONE
# ENTITLEMENT AUTHORITY: NONE
# IAM AUTHORITY: NONE
# WORKFLOW INSTANCE AUTHORITY: NONE
# WORK GENERATION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# TENANT POSTURE: exact tenant correlation; cross-tenant inference prohibited
# FAIL-CLOSED POSTURE: malformed, incomplete, or divergent evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
