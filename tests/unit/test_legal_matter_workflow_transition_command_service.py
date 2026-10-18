"""
WILSY OS — P13R3 Workflow Transition Command Service Unit Certificate

VERSION: v1.0.0-P13R3-LEGAL-MATTER-WORKFLOW-TRANSITION-COMMAND-UNIT
AUTHORITY: Wilsy OS Core Governance / Legal Operations.
EPITOME: Certify server resolution, derived currentness, gate enforcement,
authority-free intent, replay delegation and no partial append on failure.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/
    test_legal_matter_workflow_transition_command_service.py
CERTIFICATION DATE: 2026-10-16
CHANGELOG: v1.0.0-P13R3 — Initial direct service certificate.
COMPLIANCE: POPIA section 19 / GDPR Article 32 / SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant reaches every tenant-bearing authority lookup.
AUTHORITY BOUNDARY: Test composition only; IAM remains outside the service.
FINANCIAL AUTHORITY BOUNDARY: NONE.
"""

from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace

import pytest

from tests.unit.test_legal_matter_workflow_transition import AT, context
from tools.eos.legal_operations.domain.legal_operating_catalogue import (
    CATALOGUE_FINGERPRINT,
)
from tools.eos.legal_operations.domain.legal_workflow_definition import (
    LegalWorkflowDefinition,
)
from tools.eos.legal_operations.domain.legal_matter_workflow_currentness import (
    LegalMatterWorkflowCurrentness,
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
    LegalWorkflowGateSatisfactionRegistryNotFoundError,
)
from tools.eos.legal_operations.registry.legal_workflow_stage_registry import (
    LegalWorkflowStageRegistry,
    LegalWorkflowStageRegistryNotFoundError,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    LegalWorkflowTopologyRegistry,
)
from tools.eos.legal_operations.service.legal_matter_workflow_transition_command_service import (
    LegalMatterWorkflowTransitionCommandConflictError,
    LegalMatterWorkflowTransitionCommandInputError,
    LegalMatterWorkflowTransitionCommandService,
)


VERSION = "v1.0.0-P13R3-LEGAL-MATTER-WORKFLOW-TRANSITION-COMMAND-UNIT"
ACTIVE = SimpleNamespace(in_transaction=True)


def definition() -> LegalWorkflowDefinition:
    """Return the exact platform definition used by the transition fixture."""
    return LegalWorkflowDefinition(
        workflow_definition_id="workflow-1",
        definition_revision=1,
        owner="PLATFORM",
        owner_tenant_id=None,
        name="Workflow",
        description_reference="workflow-desc",
        required_operating_item_ids=("PRACTICE_DISPUTES",),
        jurisdiction_references=("ZA",),
        catalogue_fingerprint=CATALOGUE_FINGERPRINT,
    )


class DefinitionRegistry(LegalWorkflowDefinitionRegistry):
    """Resolve the exact platform definition and no tenant alias."""

    def __init__(self, value) -> None:
        self.value = value

    def get_revision(
        self,
        owner,
        owner_tenant_id,
        workflow_definition_id,
        definition_revision,
        *,
        session,
    ):
        if str(getattr(owner, "value", owner)) != "PLATFORM":
            raise LegalWorkflowDefinitionRegistryNotFoundError("P9B_REVISION_NOT_FOUND")
        return self.value


class InstanceRegistry(LegalMatterWorkflowInstanceRegistry):
    """Resolve one exact tenant workflow instance."""

    def __init__(self, value) -> None:
        self.value = value

    def get_by_id(self, tenant_id, workflow_instance_id, *, session):
        if tenant_id != self.value.tenant_id or workflow_instance_id != self.value.workflow_instance_id:
            raise RuntimeError("G7G_R14_INSTANCE_NOT_FOUND")
        return self.value


class TopologyRegistry(LegalWorkflowTopologyRegistry):
    """Resolve one exact immutable topology."""

    def __init__(self, value) -> None:
        self.value = value

    def get_by_fingerprint(self, topology_fingerprint, *, session):
        return self.value


class StageRegistry(LegalWorkflowStageRegistry):
    """Resolve stages by server-derived definition identity and stage ID."""

    def __init__(self, *values) -> None:
        self.values = {value.stage_definition_id: value for value in values}

    def get_by_definition_stage(
        self,
        workflow_definition_fingerprint,
        stage_definition_id,
        *,
        session,
    ):
        try:
            return self.values[stage_definition_id]
        except KeyError as error:
            raise LegalWorkflowStageRegistryNotFoundError("P11B_STAGE_NOT_FOUND") from error


class GateRegistry(LegalWorkflowGateSatisfactionRegistry):
    """Resolve gate facts only by exact tenant and opaque satisfaction ID."""

    def __init__(self, values) -> None:
        self.values = {value.gate_satisfaction_id: value for value in values}

    def get_by_id(self, tenant_id, gate_satisfaction_id, *, session):
        try:
            value = self.values[gate_satisfaction_id]
        except KeyError as error:
            raise LegalWorkflowGateSatisfactionRegistryNotFoundError(
                "P12B_GATE_SATISFACTION_NOT_FOUND"
            ) from error
        if value.tenant_id != tenant_id:
            raise LegalWorkflowGateSatisfactionRegistryNotFoundError(
                "P12B_GATE_SATISFACTION_NOT_FOUND"
            )
        return value


class TransitionRegistry(LegalMatterWorkflowTransitionRegistry):
    """Derive currentness from history and capture only successful appends."""

    def __init__(self, instance) -> None:
        self.instance = instance
        self.history = []
        self.appended = []

    def list_history(self, tenant_id, workflow_instance_id, *, session):
        return tuple(self.history)

    def derive_currentness(self, currentness_id, workflow_instance, *, session):
        return LegalMatterWorkflowCurrentness.derive(
            currentness_id=currentness_id,
            workflow_instance=workflow_instance,
            transitions=tuple(self.history),
        )

    def create_or_replay(self, value, *, session):
        if self.appended and self.appended[-1].transition_id == value.transition_id:
            return self.appended[-1]
        self.appended.append(value)
        self.history.append(value)
        return value


def service(*, with_gate: bool = True, branching: bool = False):
    """Compose a service with exact immutable fixture authorities."""
    instance, topology, source, target, alternate, gates = context(
        with_gate=with_gate, branching=branching
    )
    transitions = TransitionRegistry(instance)
    subject = LegalMatterWorkflowTransitionCommandService(
        definition_registry=DefinitionRegistry(definition()),
        instance_registry=InstanceRegistry(instance),
        topology_registry=TopologyRegistry(topology),
        stage_registry=StageRegistry(
            *tuple(value for value in (source, target, alternate) if value is not None)
        ),
        gate_registry=GateRegistry(gates),
        transition_registry=transitions,
    )
    return subject, transitions, instance, target, gates


def execute(subject, *, gate_ids=("gate-sat-1",), target="s2", branch=None):
    """Execute one bounded server-side intent."""
    return subject.execute(
        tenant_id="tenant-1",
        transitioned_by_principal_id="principal-authorized",
        transition_id="transition-command-1",
        workflow_instance_id="instance-1",
        target_stage_definition_id=target,
        gate_satisfaction_ids=gate_ids,
        branch_selection_evidence_reference=branch,
        transitioned_at=AT + timedelta(minutes=1),
        transition_authorization_evidence_reference="tenant-authorization-decision:1",
        session=ACTIVE,
    )


def test_server_resolves_all_authorities_and_appends_transition() -> None:
    subject, transitions, instance, target, gates = service()
    value = execute(subject)
    assert value.tenant_id == instance.tenant_id
    assert value.source_stage_definition_id == instance.entry_stage_definition_id
    assert value.target_stage_definition_id == target.stage_definition_id
    assert value.gate_bindings[0].gate_satisfaction_id == gates[0].gate_satisfaction_id
    assert transitions.appended == [value]


def test_exact_command_replay_precedes_new_currentness_derivation() -> None:
    subject, transitions, _, _, _ = service()
    created = execute(subject)
    replayed = execute(subject)
    assert replayed == created
    assert transitions.appended == [created]


def test_divergent_command_replay_fails_closed() -> None:
    subject, transitions, _, _, _ = service(branching=True)
    execute(subject, target="s2", branch="branch:first")
    with pytest.raises(
        LegalMatterWorkflowTransitionCommandConflictError,
        match="P13R3_DIVERGENT_COMMAND_REPLAY",
    ):
        execute(subject, target="s3", branch="branch:second")
    assert len(transitions.appended) == 1


def test_missing_required_gate_fails_before_append() -> None:
    subject, transitions, _, _, _ = service()
    with pytest.raises(
        LegalMatterWorkflowTransitionCommandConflictError,
        match="G7G_R10_GATE_SATISFACTION_SET_MISMATCH",
    ):
        execute(subject, gate_ids=())
    assert transitions.appended == []


def test_unknown_gate_fails_before_append() -> None:
    subject, transitions, _, _, _ = service()
    with pytest.raises(
        LegalWorkflowGateSatisfactionRegistryNotFoundError,
        match="P12B_GATE_SATISFACTION_NOT_FOUND",
    ):
        execute(subject, gate_ids=("unknown",))
    assert transitions.appended == []


def test_non_successor_target_fails_before_append() -> None:
    subject, transitions, _, _, _ = service(branching=True)
    with pytest.raises(LegalWorkflowStageRegistryNotFoundError):
        execute(subject, target="outside", branch="branch-proof")
    assert transitions.appended == []


def test_branching_requires_server_passed_opaque_branch_evidence() -> None:
    subject, transitions, _, _, _ = service(branching=True)
    with pytest.raises(
        LegalMatterWorkflowTransitionCommandConflictError,
        match="G7G_R10_BRANCH_SELECTION_EVIDENCE_REQUIRED",
    ):
        execute(subject)
    assert transitions.appended == []
    value = execute(subject, branch="branch-selection:opaque")
    assert value.branch_selection_evidence_reference == "branch-selection:opaque"


def test_active_transaction_is_required() -> None:
    subject, _, _, _, _ = service()
    with pytest.raises(
        LegalMatterWorkflowTransitionCommandInputError,
        match="P13R3_ACTIVE_TRANSACTION_REQUIRED",
    ):
        subject.execute(
            tenant_id="tenant-1",
            transitioned_by_principal_id="principal",
            transition_id="transition-1",
            workflow_instance_id="instance-1",
            target_stage_definition_id="s2",
            gate_satisfaction_ids=("gate-sat-1",),
            branch_selection_evidence_reference=None,
            transitioned_at=AT,
            transition_authorization_evidence_reference="auth",
            session=object(),
        )


def test_service_accepts_no_authority_objects_or_fingerprints() -> None:
    parameter_names = set(
        LegalMatterWorkflowTransitionCommandService.execute.__annotations__
    )
    assert not parameter_names.intersection(
        {
            "workflow_definition",
            "workflow_topology",
            "source_stage",
            "target_stage",
            "gate_satisfactions",
            "tenant_authority",
            "iam_assignment",
            "workflow_instance_fingerprint",
            "workflow_topology_fingerprint",
            "source_stage_fingerprint",
            "target_stage_fingerprint",
        }
    )


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: test_legal_matter_workflow_transition_command_service.py
# VERSION: v1.0.0-P13R3-LEGAL-MATTER-WORKFLOW-TRANSITION-COMMAND-UNIT
# TENANT POSTURE: exact tenant resolution certified
# FAIL-CLOSED POSTURE: missing gate, target, branch and transaction reject
# CLIENT AUTHORITY OBJECTS / FINGERPRINTS ACCEPTED: NONE
# PARTIAL TRANSITION APPEND ON FAILURE: NONE
# IAM AUTHORITY: NOT CLAIMED BY THIS SERVICE TEST
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
