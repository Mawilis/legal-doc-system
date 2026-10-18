"""
TITLE: WILSY OS Legal Transition Work Materialization Service
VERSION: v1.1.0-P14-P18-TRANSITION-WORK-MATERIALIZER
AUTHORITY: Wilsy OS Core Governance / Legal Operations
EPITOME: Atomically derives immutable operational work from one persisted
transition and one server-selected immutable policy, then seals exact replay.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_transition_work_materialization_service.py
COLLABORATION / OWNERSHIP: workflow-instance and transition registries supply
source truth; policy supplies declarative work; work and receipt registries own
durability inside one caller-owned transaction.
CERTIFICATION DATE: 2026-10-16
CHANGELOG: v1.1.0 re-correlates replay receipt, policy and every work artifact
against exact persisted transition/instance truth; v1.0.0 introduced the
replay-first deterministic materializer.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: tenant-first exact reads; no PII logging.
TENANT BOUNDARY: every lookup and persisted artifact is exact-tenant scoped.
AUTHORITY BOUNDARY: operational work creation only; no assignment, supervision,
IAM, professional, notification, AI, condition interpretation or legal deadline.
FINANCIAL AUTHORITY BOUNDARY: none; Kennel EOS exclusively executes finance.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import hashlib
import hmac
import json
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.legal_transition_work_materialization_receipt import (
    LegalTransitionWorkMaterializationOutput,
    LegalTransitionWorkMaterializationReceipt,
)
from tools.eos.legal_operations.domain.legal_work_dependency_edge import (
    LegalWorkDependencyEdge,
)
from tools.eos.legal_operations.domain.legal_work_item import LegalWorkItem, LegalWorkItemStatus
from tools.eos.legal_operations.domain.legal_work_materialization_policy import (
    LegalOperationalDueRule,
    LegalWorkMaterializationPolicy,
    LegalWorkMaterializationTemplate,
)
from tools.eos.legal_operations.registry.legal_transition_work_materialization_receipt_registry import (
    LegalTransitionWorkMaterializationReceiptRegistryNotFoundError,
)

VERSION: Final[str] = "v1.2.0-P14-R10-TRANSITION-WORK-MATERIALIZER"
SOURCE_KIND: Final[str] = "LEGAL_TRANSITION_WORK_MATERIALIZATION"


class LegalTransitionWorkMaterializationServiceError(RuntimeError):
    """Base stable fail-closed materialization error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise LegalTransitionWorkMaterializationServiceError(code)


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 320:
        _fail(f"P14_P18_{name.upper()}_INVALID")
    return value


def _tx(session: object) -> object:
    marker = getattr(session, "in_transaction", None) if session is not None else None
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        raise LegalTransitionWorkMaterializationServiceError(
            "P14_P18_ACTIVE_TRANSACTION_REQUIRED"
        ) from error
    if active is not True:
        _fail("P14_P18_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _digest(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


def _derive_work(
    transition: Any,
    policy: LegalWorkMaterializationPolicy,
    template: LegalWorkMaterializationTemplate,
) -> LegalWorkItem:
    payload = {
        "tenant_id": transition.tenant_id,
        "case_matter_id": transition.case_matter_id,
        "transition_id": transition.transition_id,
        "transition_fingerprint": transition.fingerprint,
        "policy_id": policy.policy_id,
        "policy_revision": policy.policy_revision,
        "policy_fingerprint": policy.fingerprint,
        "work_template_id": template.work_template_id,
    }
    due_at = None
    if template.due_rule is LegalOperationalDueRule.TRANSITION_OFFSET:
        offset = template.due_offset_seconds
        if offset is None:
            _fail("P14_P18_DUE_OFFSET_REQUIRED")
        due_at = transition.transitioned_at + timedelta(seconds=offset)
    return LegalWorkItem(
        work_item_id=_digest(payload), tenant_id=transition.tenant_id,
        case_matter_id=transition.case_matter_id, title=template.title,
        source_kind=SOURCE_KIND, source_reference=transition.transition_id,
        source_evidence_fingerprint=_digest(payload), status=LegalWorkItemStatus.OPEN,
        created_at=transition.transitioned_at, due_at=due_at,
    )


@dataclass(frozen=True, slots=True)
class LegalTransitionWorkMaterializationResult:
    """Immutable bounded result without assignment or execution authority."""

    receipt: LegalTransitionWorkMaterializationReceipt | None
    work_items: tuple[LegalWorkItem, ...]
    replayed: bool
    no_policy: bool


class LegalTransitionWorkMaterializationService:
    """
    Create or exactly replay transition-derived operational work and edges.

    Work items, materialization receipt and runtime dependency edges all use
    the same caller-owned active transaction. Dependency edges express
    topology only; they do not satisfy dependencies, complete work, mutate a
    blocked state, assign work, notify, invoke AI or grant any authority.
    """

    def __init__(
        self,
        *,
        transition_registry: Any,
        workflow_instance_registry: Any,
        policy_registry: Any,
        work_item_registry: Any,
        receipt_registry: Any,
        dependency_registry: Any,
    ) -> None:
        dependencies = (
            transition_registry,
            workflow_instance_registry,
            policy_registry,
            work_item_registry,
            receipt_registry,
            dependency_registry,
        )

        if any(
            value is None
            for value in dependencies
        ):
            _fail(
                "P14_P18_REGISTRY_REQUIRED"
            )

        self._transitions = (
            transition_registry
        )
        self._instances = (
            workflow_instance_registry
        )
        self._policies = (
            policy_registry
        )
        self._work = (
            work_item_registry
        )
        self._receipts = (
            receipt_registry
        )
        self._dependencies = (
            dependency_registry
        )

    @staticmethod
    def _derive_dependency_edges(
        *,
        tenant_id: str,
        case_matter_id: str,
        receipt: LegalTransitionWorkMaterializationReceipt,
        policy: LegalWorkMaterializationPolicy,
        work_items: tuple[
            LegalWorkItem,
            ...,
        ],
    ) -> tuple[
        LegalWorkDependencyEdge,
        ...,
    ]:
        """
        Derive exact receipt-bound runtime edges from policy declarations.

        The policy domain has already certified template membership and DAG
        validity. This method maps those declared template dependencies onto
        the exact materialized work identities and fingerprints.
        """
        if (
            len(policy.templates)
            != len(work_items)
        ):
            _fail(
                "P14_R10_DEPENDENCY_WORK_COUNT_MISMATCH"
            )

        work_by_template = {
            template.work_template_id:
                work
            for template, work in zip(
                policy.templates,
                work_items,
                strict=True,
            )
        }

        edges: list[
            LegalWorkDependencyEdge
        ] = []

        for successor_template in (
            policy.templates
        ):
            successor = work_by_template[
                successor_template.work_template_id
            ]

            for predecessor_template_id in (
                successor_template.dependency_template_ids
            ):
                predecessor = (
                    work_by_template.get(
                        predecessor_template_id
                    )
                )

                if predecessor is None:
                    _fail(
                        "P14_R10_DEPENDENCY_TEMPLATE_WORK_MISSING"
                    )

                edges.append(
                    LegalWorkDependencyEdge(
                        tenant_id=tenant_id,
                        case_matter_id=case_matter_id,
                        source_materialization_receipt_id=(
                            receipt.receipt_id
                        ),
                        source_materialization_receipt_fingerprint=(
                            receipt.fingerprint
                        ),
                        predecessor_work_item_id=(
                            predecessor.work_item_id
                        ),
                        predecessor_work_item_fingerprint=(
                            predecessor.fingerprint
                        ),
                        successor_work_item_id=(
                            successor.work_item_id
                        ),
                        successor_work_item_fingerprint=(
                            successor.fingerprint
                        ),
                    )
                )

        return tuple(
            sorted(
                edges,
                key=lambda edge: (
                    edge.predecessor_work_item_id,
                    edge.successor_work_item_id,
                    edge.dependency_edge_id,
                ),
            )
        )

    def materialize(
        self,
        tenant_id: str,
        workflow_instance_id: str,
        transition_id: str,
        *,
        session: object,
    ) -> LegalTransitionWorkMaterializationResult:
        """
        Materialize server-derived work inside one caller-owned transaction.

        Inputs are scope locators only. They grant no policy, work, assignment,
        supervision, IAM, notification, AI, deadline, dependency-satisfaction,
        completion, blocked-state or financial authority.
        """
        tx = _tx(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        instance_id = _text(
            "workflow_instance_id",
            workflow_instance_id,
        )
        transition_identity = _text(
            "transition_id",
            transition_id,
        )

        instance = self._instances.get_by_id(
            tenant,
            instance_id,
            session=tx,
        )

        if (
            instance.tenant_id != tenant
            or instance.workflow_instance_id
            != instance_id
        ):
            _fail(
                "P14_P18_INSTANCE_SCOPE_MISMATCH"
            )

        history = self._transitions.list_history(
            tenant,
            instance_id,
            session=tx,
        )

        transition = next(
            (
                value
                for value in history
                if value.transition_id
                == transition_identity
            ),
            None,
        )

        if transition is None:
            _fail(
                "P14_P18_TRANSITION_NOT_FOUND"
            )

        if (
            transition.tenant_id
            != tenant
            or transition.workflow_instance_id
            != instance_id
            or transition.case_matter_id
            != instance.case_matter_id
            or transition.workflow_instance_fingerprint
            != instance.fingerprint
            or transition.workflow_topology_fingerprint
            != instance.workflow_topology_fingerprint
        ):
            _fail(
                "P14_P18_TRANSITION_SCOPE_MISMATCH"
            )

        try:
            receipt = (
                self._receipts.get_by_transition_id(
                    tenant,
                    transition_identity,
                    session=tx,
                )
            )
        except (
            LegalTransitionWorkMaterializationReceiptRegistryNotFoundError
        ):
            receipt = None

        if receipt is not None:
            if (
                receipt.tenant_id
                != tenant
                or receipt.case_matter_id
                != transition.case_matter_id
                or receipt.transition_id
                != transition.transition_id
                or not hmac.compare_digest(
                    receipt.transition_fingerprint,
                    transition.fingerprint,
                )
                or receipt.workflow_definition_id
                != instance.workflow_definition_id
                or receipt.target_stage_definition_id
                != transition.target_stage_definition_id
            ):
                _fail(
                    "P14_P18_REPLAY_RECEIPT_SCOPE_MISMATCH"
                )

            policy = self._policies.get_revision(
                tenant,
                receipt.policy_id,
                receipt.policy_revision,
                session=tx,
            )

            if (
                policy.tenant_id
                != tenant
                or policy.policy_id
                != receipt.policy_id
                or policy.policy_revision
                != receipt.policy_revision
                or not hmac.compare_digest(
                    policy.fingerprint,
                    receipt.policy_fingerprint,
                )
                or policy.workflow_definition_id
                != instance.workflow_definition_id
                or policy.workflow_definition_fingerprint
                != instance.workflow_definition_fingerprint
                or policy.target_stage_definition_id
                != transition.target_stage_definition_id
                or policy.target_stage_fingerprint
                != transition.target_stage_fingerprint
            ):
                _fail(
                    "P14_P18_REPLAY_POLICY_MISMATCH"
                )

            if (
                len(receipt.outputs)
                != len(policy.templates)
            ):
                _fail(
                    "P14_P18_REPLAY_OUTPUT_COUNT_MISMATCH"
                )

            works: list[
                LegalWorkItem
            ] = []

            for template, output in zip(
                policy.templates,
                receipt.outputs,
                strict=True,
            ):
                expected = _derive_work(
                    transition,
                    policy,
                    template,
                )

                if (
                    output.work_item_id
                    != expected.work_item_id
                ):
                    _fail(
                        "P14_P18_REPLAY_OUTPUT_ID_MISMATCH"
                    )

                durable = self._work.get_by_id(
                    tenant,
                    output.work_item_id,
                    session=tx,
                )

                if (
                    durable != expected
                    or not hmac.compare_digest(
                        durable.fingerprint,
                        output.work_item_fingerprint,
                    )
                ):
                    _fail(
                        "P14_P18_REPLAY_WORK_MISMATCH"
                    )

                works.append(
                    durable
                )

            replay_work = tuple(
                works
            )

            expected_edges = (
                self._derive_dependency_edges(
                    tenant_id=tenant,
                    case_matter_id=(
                        transition.case_matter_id
                    ),
                    receipt=receipt,
                    policy=policy,
                    work_items=replay_work,
                )
            )

            durable_edges = (
                self._dependencies.list_by_receipt(
                    tenant,
                    receipt.receipt_id,
                    session=tx,
                )
            )

            if (
                durable_edges
                != expected_edges
            ):
                _fail(
                    "P14_R10_REPLAY_DEPENDENCY_EDGE_MISMATCH"
                )

            return (
                LegalTransitionWorkMaterializationResult(
                    receipt=receipt,
                    work_items=replay_work,
                    replayed=True,
                    no_policy=False,
                )
            )

        rows = (
            self._policies.list_workflow_stage(
                tenant,
                instance.workflow_definition_id,
                transition.target_stage_definition_id,
                session=tx,
            )
        )

        families = {
            value.policy_id
            for value in rows
        }

        if not families:
            return (
                LegalTransitionWorkMaterializationResult(
                    receipt=None,
                    work_items=(),
                    replayed=False,
                    no_policy=True,
                )
            )

        if len(families) != 1:
            _fail(
                "P14_P18_AMBIGUOUS_POLICY_FAMILIES"
            )

        policy = max(
            rows,
            key=lambda value:
                value.policy_revision,
        )

        if (
            policy.tenant_id
            != tenant
            or policy.workflow_definition_id
            != instance.workflow_definition_id
            or policy.workflow_definition_fingerprint
            != instance.workflow_definition_fingerprint
            or policy.target_stage_definition_id
            != transition.target_stage_definition_id
            or policy.target_stage_fingerprint
            != transition.target_stage_fingerprint
        ):
            _fail(
                "P14_P18_POLICY_SCOPE_MISMATCH"
            )

        if any(
            template.condition_references
            for template in policy.templates
        ):
            _fail(
                "P14_P18_CONDITION_RESOLVER_ABSENT"
            )

        persisted = tuple(
            self._work.create_or_replay(
                _derive_work(
                    transition,
                    policy,
                    template,
                ),
                session=tx,
            )
            for template in policy.templates
        )

        receipt_value = (
            LegalTransitionWorkMaterializationReceipt(
                tenant_id=tenant,
                case_matter_id=(
                    transition.case_matter_id
                ),
                transition_id=(
                    transition.transition_id
                ),
                transition_fingerprint=(
                    transition.fingerprint
                ),
                workflow_definition_id=(
                    instance.workflow_definition_id
                ),
                target_stage_definition_id=(
                    transition.target_stage_definition_id
                ),
                policy_id=policy.policy_id,
                policy_revision=(
                    policy.policy_revision
                ),
                policy_fingerprint=(
                    policy.fingerprint
                ),
                outputs=tuple(
                    LegalTransitionWorkMaterializationOutput(
                        work_item_id=(
                            value.work_item_id
                        ),
                        work_item_fingerprint=(
                            value.fingerprint
                        ),
                    )
                    for value in persisted
                ),
                materialized_at=(
                    transition.transitioned_at
                ),
            )
        )

        durable_receipt = (
            self._receipts.create_or_replay(
                receipt_value,
                session=tx,
            )
        )

        expected_edges = (
            self._derive_dependency_edges(
                tenant_id=tenant,
                case_matter_id=(
                    transition.case_matter_id
                ),
                receipt=durable_receipt,
                policy=policy,
                work_items=persisted,
            )
        )

        durable_edges = tuple(
            sorted(
                (
                    self._dependencies.create_or_replay(
                        edge,
                        session=tx,
                    )
                    for edge in expected_edges
                ),
                key=lambda edge: (
                    edge.predecessor_work_item_id,
                    edge.successor_work_item_id,
                    edge.dependency_edge_id,
                ),
            )
        )

        if (
            durable_edges
            != expected_edges
        ):
            _fail(
                "P14_R10_DEPENDENCY_EDGE_PERSISTENCE_MISMATCH"
            )

        return (
            LegalTransitionWorkMaterializationResult(
                receipt=durable_receipt,
                work_items=persisted,
                replayed=False,
                no_policy=False,
            )
        )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_transition_work_materialization_service.py
# VERSION: v1.2.0-P14-R10-TRANSITION-WORK-MATERIALIZER
# AUTHORITY BOUNDARY: deterministic operational work creation only
# TENANT POSTURE: exact tenant scope / fail closed
# FAIL-CLOSED POSTURE: ambiguity, unresolved conditions, misbinding and corruption reject
# ASSIGNMENT / SUPERVISION / IAM / NOTIFICATION / AI AUTHORITY: NONE
# LEGAL-DEADLINE AUTHORITY: NONE; due_at is operational only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
