"""
WILSY OS — Legal Matter Workflow Transition Command Service

VERSION: v1.0.0-P13R3-LEGAL-MATTER-WORKFLOW-TRANSITION-COMMAND
AUTHORITY: Wilsy OS Core Governance / Legal Operations.
EPITOME: Resolve every durable workflow authority server-side and append one
immutable LegalMatterWorkflowTransition inside the caller-owned transaction.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/
    legal_matter_workflow_transition_command_service.py
COLLABORATION / OWNERSHIP:
    API transport supplies authenticated tenant/principal and intent only.
    Definition, instance, topology, stage, gate and transition registries own
    durable truth. The transition domain owns progression semantics.
CERTIFICATION / UPDATE DATE: 2026-10-16
CHANGELOG:
    v1.0.0-P13R3 — Establishes server-resolved immutable workflow-transition
    composition with derived currentness and exact gate resolution.
COMPLIANCE: POPIA section 19 / GDPR Article 32 / SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE:
    Every tenant-bearing read starts with authenticated tenant scope. No client
    authority object or authority fingerprint is accepted.
TENANT BOUNDARY: Cross-tenant absence remains ordinary not-found truth.
AUTHORITY BOUNDARY:
    This service composes already-authorized transition execution. IAM remains
    the API dependency's authority and its durable evidence issuer. The service
    grants no matter access, professional role, assignment, supervision, work,
    legal-status, commercial, AI, payment or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: NONE; Kennel EOS exclusively executes finance.
TRANSACTION BOUNDARY:
    One caller-owned already-active Mongo transaction covers all reads and the
    append. This service never starts, commits, aborts or retries it.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hmac
from typing import Final, NoReturn

from tools.eos.legal_operations.domain.legal_matter_workflow_transition import (
    LegalMatterWorkflowTransition,
    LegalMatterWorkflowTransitionError,
)
from tools.eos.legal_operations.domain.legal_workflow_definition import (
    LegalWorkflowDefinition,
    LegalWorkflowDefinitionOwner,
)
from tools.eos.legal_operations.registry.legal_matter_workflow_instance_registry import (
    LegalMatterWorkflowInstanceRegistry,
)
from tools.eos.legal_operations.registry.legal_matter_workflow_transition_registry import (
    LegalMatterWorkflowTransitionRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_definition_registry import (
    LegalWorkflowDefinitionRegistry,
    LegalWorkflowDefinitionRegistryNotFoundError,
)
from tools.eos.legal_operations.registry.legal_workflow_gate_satisfaction_registry import (
    LegalWorkflowGateSatisfactionRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_stage_registry import (
    LegalWorkflowStageRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    LegalWorkflowTopologyRegistry,
)


VERSION: Final[str] = (
    "v1.0.0-P13R3-LEGAL-MATTER-WORKFLOW-TRANSITION-COMMAND"
)


class LegalMatterWorkflowTransitionCommandServiceError(RuntimeError):
    """Stable fail-closed transition-composition error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalMatterWorkflowTransitionCommandInputError(
    LegalMatterWorkflowTransitionCommandServiceError
):
    """Server command input or service composition is malformed."""


class LegalMatterWorkflowTransitionCommandConflictError(
    LegalMatterWorkflowTransitionCommandServiceError
):
    """Resolved durable authorities conflict with the requested intent."""


def _raise(
    kind: type[LegalMatterWorkflowTransitionCommandServiceError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = kind(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object, *, limit: int = 320) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 32 for character in value)
    ):
        _raise(
            LegalMatterWorkflowTransitionCommandInputError,
            f"P13R3_{name.upper()}_INVALID",
        )
    return value


def _tenant(value: object) -> str:
    tenant_id = _text("tenant_id", value, limit=160)
    if tenant_id.casefold() in {
        "default",
        "global",
        "global_root",
        "root",
        "master",
        "*",
    }:
        _raise(
            LegalMatterWorkflowTransitionCommandInputError,
            "P13R3_TENANT_REQUIRED",
        )
    return tenant_id


def _moment(value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _raise(
            LegalMatterWorkflowTransitionCommandInputError,
            "P13R3_TRANSITIONED_AT_INVALID",
        )
    return value.astimezone(timezone.utc)


def _transaction(session: object) -> object:
    if session is None:
        _raise(
            LegalMatterWorkflowTransitionCommandInputError,
            "P13R3_ACTIVE_TRANSACTION_REQUIRED",
        )
    try:
        marker = getattr(session, "in_transaction")
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        _raise(
            LegalMatterWorkflowTransitionCommandInputError,
            "P13R3_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    if active is not True:
        _raise(
            LegalMatterWorkflowTransitionCommandInputError,
            "P13R3_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _gate_ids(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        _raise(
            LegalMatterWorkflowTransitionCommandInputError,
            "P13R3_GATE_SATISFACTION_IDS_INVALID",
        )
    normalized = tuple(
        _text("gate_satisfaction_id", item, limit=160)
        for item in value
    )
    if len(set(normalized)) != len(normalized):
        _raise(
            LegalMatterWorkflowTransitionCommandInputError,
            "P13R3_GATE_SATISFACTION_IDS_DUPLICATE",
        )
    return normalized


class LegalMatterWorkflowTransitionCommandService:
    """Resolve durable authorities and append one immutable transition fact."""

    def __init__(
        self,
        *,
        definition_registry: LegalWorkflowDefinitionRegistry,
        instance_registry: LegalMatterWorkflowInstanceRegistry,
        topology_registry: LegalWorkflowTopologyRegistry,
        stage_registry: LegalWorkflowStageRegistry,
        gate_registry: LegalWorkflowGateSatisfactionRegistry,
        transition_registry: LegalMatterWorkflowTransitionRegistry,
    ) -> None:
        requirements = (
            (definition_registry, LegalWorkflowDefinitionRegistry, "DEFINITION"),
            (instance_registry, LegalMatterWorkflowInstanceRegistry, "INSTANCE"),
            (topology_registry, LegalWorkflowTopologyRegistry, "TOPOLOGY"),
            (stage_registry, LegalWorkflowStageRegistry, "STAGE"),
            (gate_registry, LegalWorkflowGateSatisfactionRegistry, "GATE"),
            (transition_registry, LegalMatterWorkflowTransitionRegistry, "TRANSITION"),
        )
        for value, expected, label in requirements:
            if not isinstance(value, expected):
                _raise(
                    LegalMatterWorkflowTransitionCommandInputError,
                    f"P13R3_{label}_REGISTRY_REQUIRED",
                )
        self._definition_registry = definition_registry
        self._instance_registry = instance_registry
        self._topology_registry = topology_registry
        self._stage_registry = stage_registry
        self._gate_registry = gate_registry
        self._transition_registry = transition_registry

    def _definition(
        self,
        *,
        tenant_id: str,
        workflow_definition_id: str,
        definition_revision: int,
        expected_fingerprint: str,
        session: object,
    ) -> LegalWorkflowDefinition:
        candidates: list[LegalWorkflowDefinition] = []
        for owner, owner_tenant_id in (
            (LegalWorkflowDefinitionOwner.PLATFORM, None),
            (LegalWorkflowDefinitionOwner.TENANT, tenant_id),
        ):
            try:
                candidate = self._definition_registry.get_revision(
                    owner,
                    owner_tenant_id,
                    workflow_definition_id,
                    definition_revision,
                    session=session,
                )
            except LegalWorkflowDefinitionRegistryNotFoundError:
                continue
            if hmac.compare_digest(candidate.fingerprint, expected_fingerprint):
                candidates.append(candidate)
        if len(candidates) != 1:
            _raise(
                LegalMatterWorkflowTransitionCommandConflictError,
                "P13R3_DURABLE_DEFINITION_NOT_EXACT",
            )
        return candidates[0]

    def execute(
        self,
        *,
        tenant_id: str,
        transitioned_by_principal_id: str,
        transition_id: str,
        workflow_instance_id: str,
        target_stage_definition_id: str,
        gate_satisfaction_ids: tuple[str, ...],
        branch_selection_evidence_reference: str | None,
        transitioned_at: datetime,
        transition_authorization_evidence_reference: str,
        session: object,
    ) -> LegalMatterWorkflowTransition:
        """Resolve server authority and append/replay one transition.

        The caller must already have authenticated and authorized the exact
        tenant/principal, issued durable authorization evidence, and opened the
        transaction. Only intent IDs and optional branch evidence enter here.
        """
        tx = _transaction(session)
        tenant = _tenant(tenant_id)
        principal = _text(
            "transitioned_by_principal_id",
            transitioned_by_principal_id,
            limit=160,
        )
        transition_identity = _text("transition_id", transition_id, limit=160)
        instance_identity = _text(
            "workflow_instance_id", workflow_instance_id, limit=160
        )
        target_identity = _text(
            "target_stage_definition_id", target_stage_definition_id, limit=160
        )
        gate_ids = _gate_ids(gate_satisfaction_ids)
        branch_reference = (
            None
            if branch_selection_evidence_reference is None
            else _text(
                "branch_selection_evidence_reference",
                branch_selection_evidence_reference,
            )
        )
        at = _moment(transitioned_at)
        authorization_reference = _text(
            "transition_authorization_evidence_reference",
            transition_authorization_evidence_reference,
        )

        instance = self._instance_registry.get_by_id(
            tenant, instance_identity, session=tx
        )
        definition = self._definition(
            tenant_id=tenant,
            workflow_definition_id=instance.workflow_definition_id,
            definition_revision=instance.workflow_definition_revision,
            expected_fingerprint=instance.workflow_definition_fingerprint,
            session=tx,
        )
        topology = self._topology_registry.get_by_fingerprint(
            instance.workflow_topology_fingerprint,
            session=tx,
        )
        if (
            topology.workflow_definition_id != definition.workflow_definition_id
            or topology.definition_revision != definition.definition_revision
            or not hmac.compare_digest(
                topology.workflow_definition_fingerprint, definition.fingerprint
            )
        ):
            _raise(
                LegalMatterWorkflowTransitionCommandConflictError,
                "P13R3_DEFINITION_TOPOLOGY_BINDING_MISMATCH",
            )

        history = self._transition_registry.list_history(
            tenant, instance_identity, session=tx
        )
        replay = next(
            (
                value
                for value in history
                if value.transition_id == transition_identity
            ),
            None,
        )
        if replay is not None:
            requested_gate_ids = tuple(sorted(gate_ids))
            replay_gate_ids = tuple(
                sorted(
                    binding.gate_satisfaction_id
                    for binding in replay.gate_bindings
                )
            )
            if (
                replay.tenant_id != tenant
                or replay.workflow_instance_id != instance_identity
                or replay.target_stage_definition_id != target_identity
                or replay_gate_ids != requested_gate_ids
                or replay.branch_selection_evidence_reference != branch_reference
                or replay.transitioned_by_principal_id != principal
                or replay.transitioned_at != at
                or replay.transition_authorization_evidence_reference
                != authorization_reference
            ):
                _raise(
                    LegalMatterWorkflowTransitionCommandConflictError,
                    "P13R3_DIVERGENT_COMMAND_REPLAY",
                )
            return self._transition_registry.create_or_replay(
                replay,
                session=tx,
            )
        currentness = self._transition_registry.derive_currentness(
            f"transition-command:{transition_identity}",
            instance,
            session=tx,
        )
        source_stage = self._stage_registry.get_by_definition_stage(
            definition.fingerprint,
            currentness.current_stage_definition_id,
            session=tx,
        )
        target_stage = self._stage_registry.get_by_definition_stage(
            definition.fingerprint,
            target_identity,
            session=tx,
        )
        satisfactions = tuple(
            self._gate_registry.get_by_id(tenant, gate_id, session=tx)
            for gate_id in gate_ids
        )
        try:
            transition = LegalMatterWorkflowTransition.from_authorities(
                transition_id=transition_identity,
                workflow_instance=instance,
                workflow_topology=topology,
                source_stage=source_stage,
                target_stage=target_stage,
                gate_satisfactions=satisfactions,
                branch_selection_evidence_reference=branch_reference,
                transitioned_at=at,
                transitioned_by_principal_id=principal,
                transition_authorization_evidence_reference=authorization_reference,
                previous_transition=history[-1] if history else None,
            )
        except LegalMatterWorkflowTransitionError as error:
            _raise(
                LegalMatterWorkflowTransitionCommandConflictError,
                error.code,
                error,
            )
        return self._transition_registry.create_or_replay(transition, session=tx)


__all__ = [
    "VERSION",
    "LegalMatterWorkflowTransitionCommandConflictError",
    "LegalMatterWorkflowTransitionCommandInputError",
    "LegalMatterWorkflowTransitionCommandService",
    "LegalMatterWorkflowTransitionCommandServiceError",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_matter_workflow_transition_command_service.py
# VERSION: v1.0.0-P13R3-LEGAL-MATTER-WORKFLOW-TRANSITION-COMMAND
# AUTHORITY BOUNDARY: server resolution and immutable transition append only
# TENANT POSTURE: authenticated exact tenant on every tenant-bearing lookup
# FAIL-CLOSED POSTURE: missing, corrupt, stale, divergent authorities reject
# CALLER-OWNED ACTIVE TRANSACTION REQUIRED: YES
# CLIENT AUTHORITY OBJECTS / FINGERPRINTS ACCEPTED: NONE
# MUTABLE CURRENT-STAGE POINTER: NONE
# DEFINITION / TOPOLOGY / STAGE / GATE MUTATION: NONE
# IAM / PROFESSIONAL / WORK / LEGAL-STATUS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
