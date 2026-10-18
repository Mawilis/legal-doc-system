"""
TITLE:
    WILSY OS P14-R20R11 Legal Work Completion Permission Namespace
    RED Certificate

VERSION:
    v1.0.0-P14-R20R11-WORK-COMPLETION-PERMISSION-RED

AUTHORITY:
    Wilsy OS Core Governance / Python EOS IAM

EPITOME:
    Freeze the exact canonical permission-vocabulary contract required before
    any Legal Work completion operation, business-role eligibility, static role
    grant, command authority, or completion service may exist.

TENANT BOUNDARY:
    Exact own-tenant TENANT permission metadata only.

AUTHORITY BOUNDARY:
    Permission vocabulary semantics only. This certificate creates no permission
    possession, role grant, business-role eligibility, operation binding,
    assignment authority, completion authority, workflow authority, persistence,
    financial execution, or settlement authority.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive.
"""

from __future__ import annotations

import pytest

from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    canonical_permissions,
    permission_metadata,
)


PERMISSION = "legal_operations:work_item:complete"


def test_completion_permission_is_canonical_exact_own_tenant_and_nonfinancial() -> None:
    metadata = permission_metadata(
        PERMISSION
    )

    assert (
        metadata.permission_id
        == PERMISSION
    )
    assert (
        metadata.disposition
        is PermissionDisposition.CANONICAL
    )
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"

    assert (
        metadata.business_capability
        == (
            "request bounded own-tenant Legal work-item "
            "completion admission"
        )
    )

    assert (
        metadata.tenant_membership_required
        is True
    )
    assert (
        metadata.system_assignment_required
        is False
    )
    assert (
        metadata.cross_tenant_capable
        is False
    )
    assert (
        metadata.financial_execution_capable
        is False
    )
    assert (
        metadata.authorizes_by_itself
        is False
    )


def test_completion_permission_does_not_silently_reuse_work_item_write() -> None:
    assert (
        PERMISSION
        != "legal_operations:work_item:write"
    )

    write_metadata = permission_metadata(
        "legal_operations:work_item:write"
    )

    completion_metadata = permission_metadata(
        PERMISSION
    )

    assert (
        completion_metadata.permission_id
        != write_metadata.permission_id
    )


@pytest.mark.parametrize(
    "value",
    (
        "legal_operations:work_item:complete ",
        " legal_operations:work_item:complete",
        "LEGAL_OPERATIONS:WORK_ITEM:COMPLETE",
        "legal_operations:work_item:*",
        "legal_operations:work_item",
        "work_item:complete",
        "legal_operations:work_item:completed",
    ),
)
def test_alias_case_whitespace_and_wildcard_variants_fail_closed(
    value: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="UNKNOWN_PERMISSION",
    ):
        permission_metadata(
            value
        )


def test_permission_vocabulary_remains_non_self_authorizing() -> None:
    metadata = permission_metadata(
        PERMISSION
    )

    assert (
        metadata.authorizes_by_itself
        is False
    )

    field_names = set(
        metadata.__dataclass_fields__
    )

    forbidden_authority_fields = {
        "authorization_role",
        "business_role",
        "role_grant",
        "role_assignment",
        "assignee_principal_id",
        "supervisor_principal_id",
        "completion_authorized",
        "completion_event_id",
    }

    assert forbidden_authority_fields.isdisjoint(
        field_names
    )


def test_serialized_permission_canon_contains_exact_completion_permission_once() -> None:
    raw = canonical_permissions()

    assert isinstance(raw, bytes)

    token = (
        b'"permission_id":'
        b'"legal_operations:work_item:complete"'
    )

    assert raw.count(token) == 1


def test_completion_permission_metadata_contains_no_completion_execution_claim() -> None:
    metadata = permission_metadata(
        PERMISSION
    )

    raw = {
        "permission_id": metadata.permission_id,
        "namespace": metadata.namespace,
        "scope_kind": metadata.scope_kind,
        "business_capability": metadata.business_capability,
        "tenant_membership_required":
            metadata.tenant_membership_required,
        "system_assignment_required":
            metadata.system_assignment_required,
        "cross_tenant_capable":
            metadata.cross_tenant_capable,
        "financial_execution_capable":
            metadata.financial_execution_capable,
        "authorizes_by_itself":
            metadata.authorizes_by_itself,
        "disposition": metadata.disposition.value,
    }

    forbidden = {
        "completion_authorized",
        "completion_event_id",
        "assignee_principal_id",
        "supervisor_principal_id",
        "dependency_satisfied",
        "workflow_released",
        "payment_id",
        "settlement_id",
    }

    assert forbidden.isdisjoint(
        raw
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_completion_permission_namespace.py
# VERSION: v1.0.0-P14-R20R11-WORK-COMPLETION-PERMISSION-RED
# PERMISSION: legal_operations:work_item:complete
# OWN-TENANT MEMBERSHIP REQUIRED: YES
# CROSS-TENANT AUTHORITY: NO
# AUTHORIZES BY ITSELF: NO
# STATIC ROLE GRANT AUTHORITY: NONE
# BUSINESS-ROLE ELIGIBILITY AUTHORITY: NONE
# OPERATION BINDING AUTHORITY: NONE
# ASSIGNMENT AUTHORITY: NONE
# COMPLETION COMMAND AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
