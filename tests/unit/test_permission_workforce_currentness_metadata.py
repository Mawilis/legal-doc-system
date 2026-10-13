"""Certificate for explicit workforce-currentness permission metadata."""

from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    permission_metadata,
)


WORKFORCE_REQUIRED = (
    "hr:employee_relation:write",
    "hr:document:standard_employment:write",
    "hr:document:standard_employment:read",
    "hr:document:employee_relations_restricted:write",
    "hr:document:employee_relations_restricted:read",
    "hr:document:performance_restricted:write",
    "hr:document:performance_restricted:read",
    "hr:document:highly_sensitive_health:write",
    "hr:document:highly_sensitive_health:read",
    "hr:document:highly_sensitive_identity:write",
    "hr:document:highly_sensitive_identity:read",
    "hr:document:separation_restricted:write",
    "hr:document:separation_restricted:read",
    "hr:document:general:write",
    "hr:document:general:read",
)

NON_WORKFORCE_CONTROLS = (
    "legal_operations:client_matter:read",
    "legal_operations:client_acceptance:write",
    "subscription:read",
    "subscription:manage",
    "tenant_branding:read",
    "tenant_branding:profile:manage",
    "tenant_branding:asset:manage",
    "platform_billing:provider_policy:admin",
    "platform_billing:release",
    "inbound_provider_policy:author",
    "inbound_provider_policy:activate",
    "inbound_provider_policy:deactivate",
    "inbound_provider_policy:emergency_disable",
)


def test_workforce_required_permissions_are_explicit() -> None:
    for permission_id in WORKFORCE_REQUIRED:
        metadata = permission_metadata(
            permission_id
        )

        assert (
            metadata.disposition
            is PermissionDisposition.CANONICAL
        )
        assert metadata.namespace == "TENANT"
        assert metadata.tenant_membership_required is True
        assert metadata.workforce_currentness_required is True
        assert metadata.cross_tenant_capable is False
        assert metadata.financial_execution_capable is False


def test_external_commercial_and_provider_controls_remain_non_workforce() -> None:
    for permission_id in NON_WORKFORCE_CONTROLS:
        metadata = permission_metadata(
            permission_id
        )

        assert (
            metadata.disposition
            is PermissionDisposition.CANONICAL
        )
        assert metadata.workforce_currentness_required is False


def test_workforce_metadata_is_not_authority() -> None:
    metadata = permission_metadata(
        "hr:employee_relation:write"
    )

    assert metadata.authorizes_by_itself is False


def test_workforce_flag_does_not_imply_system_authority() -> None:
    metadata = permission_metadata(
        "hr:employee_relation:write"
    )

    assert metadata.system_assignment_required is False
