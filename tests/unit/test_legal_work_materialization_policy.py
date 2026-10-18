"""
WILSY OS — Legal Workflow Work-Materialization Policy Domain Certificate

TITLE: Legal Workflow Work-Materialization Policy Domain Certificate
VERSION: v1.0.0-P14-P7A-WORK-MATERIALIZATION-POLICY-RED-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME:
    Test-first contract for immutable workflow-to-operational-work policy.

    The policy describes WHAT work a certified workflow transition may
    materialize. It does not decide WHO performs that work and does not
    create IAM, professional, legal-event, notification-delivery, AI,
    assignment, supervision, billing, payment, settlement, or financial
    authority.

COMPETITIVE BASELINE:
    - phase/stage-triggered operational work;
    - multiple work templates per stage;
    - explicit dependency-template references;
    - operational relative-due rules;
    - deterministic stage re-entry materialization identity;
    - explicit materialization conditions;
    - immutable provenance and fail-closed authority separation exceeding
      ordinary task-automation semantics.

TENANT BOUNDARY:
    Exact non-pseudo tenant identity is mandatory.

FAIL-CLOSED DECLARATION:
    Malformed identity, drifted fingerprints, invalid due configuration,
    duplicate template/dependency/condition references, self-dependency,
    cross-policy ambiguity, or forbidden authority-bearing fields reject.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive for financial execution.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import timedelta

import pytest

from tools.eos.legal_operations.domain.legal_work_materialization_policy import (
    SCHEMA,
    VERSION,
    LegalOperationalDueRule,
    LegalWorkMaterializationPolicy,
    LegalWorkMaterializationPolicyError,
    LegalWorkMaterializationTemplate,
)


FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


def _template(
    *,
    template_id: str = "template-file-reply",
    title: str = "Prepare replying affidavit",
    due_rule: LegalOperationalDueRule | str = (
        LegalOperationalDueRule.TRANSITION_OFFSET
    ),
    due_offset_seconds: int | None = 172800,
    dependency_template_ids: tuple[str, ...] = (),
    condition_references: tuple[str, ...] = (),
) -> LegalWorkMaterializationTemplate:
    return LegalWorkMaterializationTemplate(
        work_template_id=template_id,
        title=title,
        due_rule=due_rule,
        due_offset_seconds=due_offset_seconds,
        dependency_template_ids=dependency_template_ids,
        condition_references=condition_references,
    )


def _policy(
    *,
    tenant_id: str = "tenant-law",
    policy_id: str = "policy-litigation-filing",
    policy_revision: int = 1,
    workflow_definition_id: str = "workflow-litigation",
    workflow_definition_fingerprint: str = FP_A,
    target_stage_definition_id: str = "stage-filing",
    target_stage_fingerprint: str = FP_B,
    templates: tuple[LegalWorkMaterializationTemplate, ...] | None = None,
    supersedes_fingerprint: str | None = None,
) -> LegalWorkMaterializationPolicy:
    return LegalWorkMaterializationPolicy(
        tenant_id=tenant_id,
        policy_id=policy_id,
        policy_revision=policy_revision,
        workflow_definition_id=workflow_definition_id,
        workflow_definition_fingerprint=workflow_definition_fingerprint,
        target_stage_definition_id=target_stage_definition_id,
        target_stage_fingerprint=target_stage_fingerprint,
        templates=templates or (_template(),),
        supersedes_fingerprint=supersedes_fingerprint,
    )


def test_version_schema_and_immutable_identity_are_exact() -> None:
    value = _policy()

    assert VERSION == (
        "v1.0.0-P14-P7-WORK-MATERIALIZATION-POLICY"
    )
    assert SCHEMA == (
        "WILSY-LEGAL-WORK-MATERIALIZATION-POLICY/V1"
    )
    assert value.tenant_id == "tenant-law"
    assert value.policy_id == "policy-litigation-filing"
    assert value.policy_revision == 1
    assert value.workflow_definition_id == "workflow-litigation"
    assert value.target_stage_definition_id == "stage-filing"
    assert len(value.fingerprint) == 128
    assert value.fingerprint == value.fingerprint.lower()

    with pytest.raises(FrozenInstanceError):
        value.policy_revision = 2  # type: ignore[misc]


def test_exact_round_trip_preserves_fingerprint_and_semantics() -> None:
    original = _policy(
        templates=(
            _template(
                template_id="template-draft",
                title="Draft filing",
            ),
            _template(
                template_id="template-review",
                title="Review filing",
                due_rule=LegalOperationalDueRule.NONE,
                due_offset_seconds=None,
                dependency_template_ids=("template-draft",),
                condition_references=("condition:review-required",),
            ),
        ),
    )

    restored = LegalWorkMaterializationPolicy.from_dict(
        original.to_dict()
    )

    assert restored == original
    assert restored.fingerprint == original.fingerprint
    assert restored.semantic_dict() == original.semantic_dict()


@pytest.mark.parametrize(
    "tenant_id",
    (
        "",
        " tenant-law",
        "tenant-law ",
        "default",
        "global",
        "root",
        "*",
    ),
)
def test_tenant_scope_is_exact_and_pseudo_tenants_reject(
    tenant_id: str,
) -> None:
    with pytest.raises(LegalWorkMaterializationPolicyError):
        _policy(tenant_id=tenant_id)


def test_policy_revision_is_positive_integer_not_boolean() -> None:
    for revision in (0, -1, True, False, 1.5, "1"):
        with pytest.raises(LegalWorkMaterializationPolicyError):
            _policy(policy_revision=revision)  # type: ignore[arg-type]


def test_fingerprint_lineage_is_exact_lowercase_sha3_512() -> None:
    value = _policy()

    assert value.workflow_definition_fingerprint == FP_A
    assert value.target_stage_fingerprint == FP_B

    with pytest.raises(LegalWorkMaterializationPolicyError):
        _policy(workflow_definition_fingerprint=FP_A.upper())

    with pytest.raises(LegalWorkMaterializationPolicyError):
        _policy(target_stage_fingerprint="b" * 127)

    with pytest.raises(LegalWorkMaterializationPolicyError):
        _policy(supersedes_fingerprint="g" * 128)


def test_one_policy_can_materialize_multiple_ordered_templates() -> None:
    first = _template(
        template_id="template-prepare",
        title="Prepare filing",
    )
    second = _template(
        template_id="template-review",
        title="Review filing",
        dependency_template_ids=("template-prepare",),
    )

    value = _policy(templates=(first, second))

    assert tuple(
        item.work_template_id
        for item in value.templates
    ) == (
        "template-prepare",
        "template-review",
    )


def test_template_identity_must_be_unique_within_policy() -> None:
    template = _template()

    with pytest.raises(
        LegalWorkMaterializationPolicyError,
        match="DUPLICATE",
    ):
        _policy(templates=(template, template))


def test_dependencies_must_reference_templates_in_same_policy() -> None:
    with pytest.raises(
        LegalWorkMaterializationPolicyError,
        match="DEPEND",
    ):
        _policy(
            templates=(
                _template(
                    template_id="template-review",
                    dependency_template_ids=("template-missing",),
                ),
            ),
        )


def test_self_dependency_rejects() -> None:
    with pytest.raises(
        LegalWorkMaterializationPolicyError,
        match="DEPEND",
    ):
        _policy(
            templates=(
                _template(
                    template_id="template-review",
                    dependency_template_ids=("template-review",),
                ),
            ),
        )


def test_dependency_cycle_rejects_fail_closed() -> None:
    with pytest.raises(
        LegalWorkMaterializationPolicyError,
        match="DEPEND",
    ):
        _policy(
            templates=(
                _template(
                    template_id="template-a",
                    dependency_template_ids=("template-b",),
                ),
                _template(
                    template_id="template-b",
                    dependency_template_ids=("template-a",),
                ),
            ),
        )


def test_transition_offset_due_rule_requires_positive_offset() -> None:
    valid = _template(
        due_rule=LegalOperationalDueRule.TRANSITION_OFFSET,
        due_offset_seconds=3600,
    )
    assert valid.due_offset_seconds == 3600

    for value in (None, 0, -1, True, 1.5, "3600"):
        with pytest.raises(
            LegalWorkMaterializationPolicyError,
            match="DUE",
        ):
            _template(
                due_rule=LegalOperationalDueRule.TRANSITION_OFFSET,
                due_offset_seconds=value,  # type: ignore[arg-type]
            )


def test_no_due_rule_forbids_offset() -> None:
    value = _template(
        due_rule=LegalOperationalDueRule.NONE,
        due_offset_seconds=None,
    )

    assert value.due_offset_seconds is None

    with pytest.raises(
        LegalWorkMaterializationPolicyError,
        match="DUE",
    ):
        _template(
            due_rule=LegalOperationalDueRule.NONE,
            due_offset_seconds=3600,
        )


def test_due_rule_is_operational_not_legal_deadline_calculation() -> None:
    value = _template(
        due_rule=LegalOperationalDueRule.TRANSITION_OFFSET,
        due_offset_seconds=int(
            timedelta(hours=12).total_seconds()
        ),
    )

    payload = value.to_dict()

    forbidden = {
        "jurisdiction_reference",
        "legal_deadline_id",
        "legal_period_rule",
        "court_rule",
        "calendar_authority",
        "ai_inferred_due_at",
    }

    assert forbidden.isdisjoint(payload)


def test_policy_contains_no_assignment_or_supervision_authority() -> None:
    payload = _policy().to_dict()

    forbidden = {
        "assignee_principal_id",
        "assigned_by_principal_id",
        "assignment_policy",
        "supervisor_principal_id",
        "supervisee_principal_id",
        "supervision_binding_id",
    }

    assert forbidden.isdisjoint(payload)


def test_policy_contains_no_iam_professional_financial_or_delivery_authority() -> None:
    payload = _policy().to_dict()

    forbidden = {
        "permission",
        "permissions",
        "role",
        "professional_qualification",
        "practising_authority",
        "notification_recipient",
        "notification_channel",
        "delivery_authority",
        "payment_state",
        "settlement_state",
        "invoice_id",
        "billing_authority",
    }

    assert forbidden.isdisjoint(payload)


def test_policy_contains_no_ai_execution_authority() -> None:
    payload = _policy().to_dict()

    forbidden = {
        "ai_provider",
        "ai_model",
        "ai_execute",
        "agent_execute",
        "tool_invocation",
        "autonomous_execution",
    }

    assert forbidden.isdisjoint(payload)


def test_conditions_are_opaque_references_not_browser_or_ai_truth() -> None:
    template = _template(
        condition_references=(
            "condition:gate-reviewed",
            "condition:matter-state-current",
        )
    )

    assert template.condition_references == (
        "condition:gate-reviewed",
        "condition:matter-state-current",
    )

    for invalid in (
        ("condition:x", "condition:x"),
        ("",),
        (" condition:x",),
    ):
        with pytest.raises(
            LegalWorkMaterializationPolicyError,
            match="CONDITION",
        ):
            _template(
                condition_references=invalid,
            )


def test_semantic_drift_changes_policy_fingerprint() -> None:
    baseline = _policy()

    changed_title = _policy(
        templates=(
            _template(
                title="Prepare amended replying affidavit",
            ),
        ),
    )
    changed_due = _policy(
        templates=(
            _template(
                due_offset_seconds=86400,
            ),
        ),
    )
    changed_stage = _policy(
        target_stage_definition_id="stage-hearing",
        target_stage_fingerprint=FP_C,
    )

    assert baseline.fingerprint != changed_title.fingerprint
    assert baseline.fingerprint != changed_due.fingerprint
    assert baseline.fingerprint != changed_stage.fingerprint


def test_hydration_rejects_missing_extra_or_corrupt_truth() -> None:
    payload = _policy().to_dict()

    missing = dict(payload)
    missing.pop("policy_id")

    with pytest.raises(
        LegalWorkMaterializationPolicyError,
        match="SCHEMA",
    ):
        LegalWorkMaterializationPolicy.from_dict(missing)

    extra = dict(payload)
    extra["unexpected"] = True

    with pytest.raises(
        LegalWorkMaterializationPolicyError,
        match="SCHEMA",
    ):
        LegalWorkMaterializationPolicy.from_dict(extra)

    corrupt = dict(payload)
    corrupt["fingerprint"] = "0" * 128

    with pytest.raises(
        LegalWorkMaterializationPolicyError,
        match="FINGERPRINT",
    ):
        LegalWorkMaterializationPolicy.from_dict(corrupt)


def test_competitive_capability_contract_is_explicit_without_authority_collapse() -> None:
    """
    Filevine/Actionstep-class mechanics are represented structurally:
    stage-triggered multi-work materialization, dependency relationships and
    relative operational due rules.

    WILSY differentiators remain mandatory:
    immutable provenance, deterministic replay material, strict tenant scope,
    and separation from assignment/supervision/IAM/legal-deadline/AI/finance.
    """
    value = _policy(
        templates=(
            _template(
                template_id="template-intake",
                title="Prepare evidence bundle",
                due_offset_seconds=14400,
                condition_references=("condition:evidence-required",),
            ),
            _template(
                template_id="template-review",
                title="Review evidence bundle",
                due_offset_seconds=28800,
                dependency_template_ids=("template-intake",),
                condition_references=("condition:review-required",),
            ),
        )
    )

    assert len(value.templates) == 2
    assert value.templates[1].dependency_template_ids == (
        "template-intake",
    )
    assert value.templates[1].due_offset_seconds == 28800


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_materialization_policy.py
# VERSION: v1.0.0-P14-P7A-WORK-MATERIALIZATION-POLICY-RED-CERT
# AUTHORITY BOUNDARY: domain contract certificate only
# COMPETITIVE BASELINE: phase work, dependencies, relative operational due rules
# ASSIGNMENT AUTHORITY: NONE
# SUPERVISION AUTHORITY: NONE
# IAM / PROFESSIONAL AUTHORITY: NONE
# LEGAL-DEADLINE AUTHORITY: NONE
# NOTIFICATION-DELIVERY AUTHORITY: NONE
# AI EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
