"""Direct certificate for pure workforce admission policy."""

from datetime import datetime, timezone
from types import MappingProxyType

import pytest

from tools.eos.auth.permission_namespace import (
    permission_metadata,
)
from tools.eos.auth.workforce_admission_policy import (
    WorkforceAdmissionDisposition,
    WorkforceAdmissionPolicyError,
    evaluate_workforce_admission,
)
from tools.eos.auth.workforce_authorization_currentness import (
    TenantPrincipalWorkforceCurrentness,
)


AT = datetime(
    2026,
    10,
    13,
    8,
    0,
    tzinfo=timezone.utc,
)


def _projection(
    *active_relationship_ids: str,
) -> TenantPrincipalWorkforceCurrentness:
    return TenantPrincipalWorkforceCurrentness(
        tenant_id="tenant-w3d",
        principal_id="principal-w3d",
        observed_at=AT,
        relationship_currentness=MappingProxyType({}),
        active_relationship_ids=tuple(
            active_relationship_ids
        ),
    )


def test_non_workforce_permission_skips_currentness() -> None:
    metadata = permission_metadata(
        "legal_operations:client_matter:read"
    )

    result = evaluate_workforce_admission(
        metadata,
        None,
    )

    assert (
        result
        is WorkforceAdmissionDisposition.NOT_REQUIRED
    )


def test_workforce_required_permission_without_projection_is_not_current() -> None:
    metadata = permission_metadata(
        "hr:employee_relation:write"
    )

    result = evaluate_workforce_admission(
        metadata,
        None,
    )

    assert (
        result
        is WorkforceAdmissionDisposition.NOT_CURRENT
    )


def test_workforce_required_permission_without_active_relationship_is_not_current() -> None:
    metadata = permission_metadata(
        "hr:employee_relation:write"
    )

    result = evaluate_workforce_admission(
        metadata,
        _projection(),
    )

    assert (
        result
        is WorkforceAdmissionDisposition.NOT_CURRENT
    )


def test_one_active_relationship_satisfies_currentness_prerequisite() -> None:
    metadata = permission_metadata(
        "hr:employee_relation:write"
    )

    result = evaluate_workforce_admission(
        metadata,
        _projection("relationship-a"),
    )

    assert (
        result
        is WorkforceAdmissionDisposition.SATISFIED
    )


def test_multiple_active_relationships_are_not_ambiguous_authority() -> None:
    metadata = permission_metadata(
        "hr:employee_relation:write"
    )

    result = evaluate_workforce_admission(
        metadata,
        _projection(
            "relationship-a",
            "relationship-b",
        ),
    )

    assert (
        result
        is WorkforceAdmissionDisposition.SATISFIED
    )


def test_non_workforce_permission_rejects_injected_workforce_projection() -> None:
    metadata = permission_metadata(
        "legal_operations:client_matter:read"
    )

    with pytest.raises(
        WorkforceAdmissionPolicyError,
        match="UNEXPECTED_WORKFORCE_CURRENTNESS",
    ):
        evaluate_workforce_admission(
            metadata,
            _projection("relationship-a"),
        )


def test_invalid_metadata_rejects() -> None:
    with pytest.raises(
        WorkforceAdmissionPolicyError,
        match="PERMISSION_METADATA_INVALID",
    ):
        evaluate_workforce_admission(
            object(),  # type: ignore[arg-type]
            None,
        )


def test_client_commercial_branding_provider_controls_are_not_workforce_required() -> None:
    controls = (
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

    for permission_id in controls:
        assert (
            evaluate_workforce_admission(
                permission_metadata(permission_id),
                None,
            )
            is WorkforceAdmissionDisposition.NOT_REQUIRED
        )


def test_policy_does_not_expose_authorization_surface() -> None:
    import tools.eos.auth.workforce_admission_policy as module

    assert not hasattr(module, "authorize")
    assert not hasattr(module, "grant")
    assert not hasattr(module, "assign")
