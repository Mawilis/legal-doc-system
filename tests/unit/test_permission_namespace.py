"""TITLE: WILSY OS Permission Namespace Canon Certification.
VERSION: v1.7.0-M11-R8-R3B-P8-P3D-P4A-CERT
AUTHORITY: Certification of immutable permission vocabulary semantics only.
EPITOME: Proves bounded namespaces, fail-closed metadata, deterministic policy
bytes, and exact own-tenant subscription/plan permission semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_permission_namespace.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-09.
CHANGELOG:
    2026-09-10 v1.7.0-M11-R8-R3B-P8-P3D-P4A-CERT certifies four
    credential-security permissions in the canonical TENANT namespace.
    2026-09-09 v1.6.0-M11-R8-R3B-P8-P3B-I2-R3-CERT certifies the dedicated
    remediation permission alongside the seven existing inbound
    merchant-configuration/provider-policy permissions.
    2026-09-09 v1.5.0-M11-R8-R3B-P8-P3A-CERT certifies seven dedicated inbound
    merchant-configuration/provider-policy permissions and their non-financial
    tenant metadata.
    2026-09-09 v1.4.0-M11-R8-R3B-P6A-CERT certifies the dedicated inbound
    collection authorization-request permission and its non-financial metadata.
    2026-09-03 v1.2.1-PLAN-PERMISSION-NAMESPACE-CERT corrects the direct-certificate
    cardinality expectation against the already-certified subscription-era
    baseline: adding plan:read and plan:manage yields 19 canonical
    permissions and 22 total permission rows. Production permission
    semantics and role grants are unchanged by this certificate-only repair.
    2026-09-03 v1.2.0-PLAN-PERMISSION-NAMESPACE-CERT certifies plan:read
    and plan:manage as exact canonical TENANT permissions while preserving
    subscription permission semantics and fail-closed wildcard/alias rejection.
    2026-08-30 v1.1.1-PERMISSION-NAMESPACE-CERT added explicit wildcard,
    alias, and hard-delete absence coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: No credentials, JWT authority projections,
persistence, or financial execution are processed.
TENANT BOUNDARY: Permission metadata never proves membership; subscription and
plan permissions require separately proven exact ACTIVE tenant membership.
AUTHORITY BOUNDARY: Tests policy metadata, not assignment or authorization.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
import json

import pytest

VERSION = "v1.7.0-M11-R8-R3B-P8-P3D-P4A-CERT"

from tools.eos.auth.permission_namespace import PermissionDisposition, VERSION as POLICY_VERSION, canonical_permissions, classify_legacy_permission, permission_metadata

def test_runtime_version_source_is_canonical() -> None:
    assert POLICY_VERSION == "v1.10.0-M11-R8-R3B-P8-P3D-P4A"


def test_permission_canon_properties() -> None:
    """Canonical tenant permissions remain explicit, bounded and non-financial."""
    rows = json.loads(
        canonical_permissions()
    )

    tenant = {
        "audit:read",
        "tenant:profile:read",
        "tenant:profile:write",
        "tenant:lifecycle:archive",
        "tenant:membership:read",
        "tenant:membership:write",
        "tenant:role_assignment:read",
        "tenant:role_assignment:write",
        "subscription:read",
        "subscription:manage",
        "plan:read",
        "plan:manage",
        "platform_billing:release",
        "inbound_collection:authorization:create",
        "inbound_merchant_configuration:register",
        "inbound_merchant_configuration:lifecycle",
        "inbound_merchant_configuration:security",
        "inbound_merchant_configuration:remediate",
        "inbound_provider_credential_security:eligibility_issue",
        "inbound_provider_credential_security:revoke",
        "inbound_provider_credential_security:compromise",
        "inbound_provider_credential_security:rotate",
        "inbound_provider_policy:author",
        "inbound_provider_policy:activate",
        "inbound_provider_policy:deactivate",
        "inbound_provider_policy:emergency_disable",
    }

    assert tenant <= {
        row["permission_id"]
        for row in rows
    }

    assert len(
        [
            row
            for row in rows
            if row["disposition"] == "CANONICAL"
        ]
    ) == 37

    assert len(rows) == 40

    for permission_id in tenant:
        metadata = permission_metadata(
            permission_id
        )

        assert metadata.namespace == "TENANT"
        assert metadata.tenant_membership_required is True
        assert metadata.cross_tenant_capable is False
        assert metadata.financial_execution_capable is False
        assert metadata.authorizes_by_itself is False

    release = permission_metadata("platform_billing:release")
    assert release.business_capability == "authorize platform billing release"

    inbound = permission_metadata("inbound_collection:authorization:create")
    assert inbound.namespace == "TENANT"
    assert inbound.scope_kind == "TENANT"
    assert inbound.business_capability == "request inbound collection authorization creation"
    assert inbound.tenant_membership_required is True
    assert inbound.cross_tenant_capable is False
    assert inbound.financial_execution_capable is False
    assert inbound.authorizes_by_itself is False

    expected_capabilities = {
        "inbound_merchant_configuration:register": "register inbound merchant configuration identity",
        "inbound_merchant_configuration:lifecycle": "transition inbound merchant configuration lifecycle",
        "inbound_merchant_configuration:security": "contain compromised inbound merchant configuration",
        "inbound_merchant_configuration:remediate": "remediate compromised inbound merchant configuration",
        "inbound_provider_credential_security:eligibility_issue": "issue credential-security eligibility evidence",
        "inbound_provider_credential_security:revoke": "revoke credential-security eligibility evidence",
        "inbound_provider_credential_security:compromise": "record credential-security compromise evidence",
        "inbound_provider_credential_security:rotate": "record credential-security rotation evidence",
        "inbound_provider_policy:author": "author inbound provider policy revisions",
        "inbound_provider_policy:activate": "activate inbound provider policy",
        "inbound_provider_policy:deactivate": "deactivate inbound provider policy",
        "inbound_provider_policy:emergency_disable": "emergency-disable inbound provider policy",
    }
    for permission_id, capability in expected_capabilities.items():
        metadata = permission_metadata(permission_id)
        assert metadata.business_capability == capability
        assert metadata.namespace == "TENANT"
        assert metadata.scope_kind == "TENANT"
        assert metadata.tenant_membership_required is True
        assert metadata.cross_tenant_capable is False
        assert metadata.financial_execution_capable is False
        assert metadata.authorizes_by_itself is False

    plan_read = permission_metadata(
        "plan:read"
    )

    plan_manage = permission_metadata(
        "plan:manage"
    )

    assert (
        plan_read.business_capability
        == "read own-tenant plan catalogue commercial truth"
    )

    assert (
        plan_manage.business_capability
        == "manage own-tenant plan catalogue lifecycle truth"
    )

    assert permission_metadata(
        "execution:trigger"
    ).disposition is PermissionDisposition.BLOCKED_AMBIGUOUS

    assert permission_metadata(
        "admin:all"
    ).disposition is PermissionDisposition.LEGACY_ONLY

    assert permission_metadata(
        "tenant:manage"
    ).disposition is PermissionDisposition.BLOCKED_AMBIGUOUS

    assert permission_metadata(
        "artifacts:write"
    ).namespace == "SERVICE"

    assert permission_metadata(
        "events:publish"
    ).namespace == "SERVICE"

    assert permission_metadata(
        "kernel:read"
    ).system_assignment_required is True

    assert permission_metadata(
        "kernel:write"
    ).tenant_membership_required is False

    assert permission_metadata(
        "artifacts:read"
    ).tenant_membership_required is True

    assert permission_metadata(
        "governance:read"
    ).namespace == "SYSTEM"

    assert classify_legacy_permission(
        "admin:all"
    ) is PermissionDisposition.LEGACY_ONLY

    assert classify_legacy_permission(
        "execution:trigger"
    ) is PermissionDisposition.BLOCKED_AMBIGUOUS

    assert classify_legacy_permission(
        "tenant:manage"
    ) is PermissionDisposition.BLOCKED_AMBIGUOUS

    assert classify_legacy_permission(
        "unknown"
    ) is None

    assert classify_legacy_permission(
        " admin:all "
    ) is None

    assert classify_legacy_permission(
        None
    ) is None

    invalid = (
        "tenant:*",
        "tenant:all",
        "tenant:admin",
        "tenant:lifecycle:*",
        "tenant:membership:*",
        "tenant:role_assignment:*",
        "manage:tenant",
        "TENANT:PROFILE:READ",
        " tenant:profile:read",
        "tenant:profile:read ",
        "tenant:lifecycle:delete",
        "subscription:*",
        "subscription",
        "plan:*",
        "plan:all",
        "plan",
        "PLAN:READ",
        " plan:read",
        "plan:read ",
        "inbound_merchant_configuration:*",
        "inbound_merchant_configuration:remediate ",
        "inbound_merchant_configuration:remediation",
        "inbound_provider_credential_security:*",
        "inbound_provider_credential_security:all",
        "inbound_provider_credential_security:ELIGIBILITY_ISSUE",
    )

    for value in invalid:
        with pytest.raises(
            ValueError
        ):
            permission_metadata(
                value
            )

    assert not any(
        "delete"
        in row["permission_id"]
        for row in rows
    )

    assert canonical_permissions() == canonical_permissions()
    assert isinstance(
        canonical_permissions(),
        bytes,
    )


def test_credential_security_permissions_are_exact_tenant_permissions() -> None:
    permissions = {
        "inbound_provider_credential_security:eligibility_issue",
        "inbound_provider_credential_security:revoke",
        "inbound_provider_credential_security:compromise",
        "inbound_provider_credential_security:rotate",
    }
    assert len(permissions) == 4
    for permission_id in permissions:
        metadata = permission_metadata(permission_id)
        assert metadata.namespace == "TENANT"
        assert metadata.scope_kind == "TENANT"
        assert metadata.tenant_membership_required is True
        assert metadata.cross_tenant_capable is False
        assert metadata.financial_execution_capable is False
        assert metadata.authorizes_by_itself is False
    assert permission_metadata("inbound_provider_credential_security:eligibility_issue").business_capability == "issue credential-security eligibility evidence"
    assert permission_metadata("inbound_provider_credential_security:revoke").business_capability == "revoke credential-security eligibility evidence"
    assert permission_metadata("inbound_provider_credential_security:compromise").business_capability == "record credential-security compromise evidence"
    assert permission_metadata("inbound_provider_credential_security:rotate").business_capability == "record credential-security rotation evidence"
    for value in (
        "inbound_provider_credential_security:unknown",
        "inbound_provider_credential_security:*",
        " inbound_provider_credential_security:rotate",
        "inbound_provider_credential_security:rotate ",
    ):
        with pytest.raises(ValueError):
            permission_metadata(value)

    with pytest.raises(
        ValueError
    ):
        permission_metadata(
            "unknown"
        )

    with pytest.raises(
        ValueError
    ):
        permission_metadata(
            " "
        )

    with pytest.raises(
        (
            AttributeError,
            TypeError,
        )
    ):
        permission_metadata(
            "audit:read"
        ).permission_id = "x"  # type: ignore[misc]

    assert (
        permission_metadata(
            "execution:trigger"
        ).business_capability
        != "financial execution"
    )

    assert permission_metadata(
        "admin:all"
    ).deprecated_or_legacy is True

    assert (
        permission_metadata(
            "tenant:membership:write"
        ).permission_id
        != permission_metadata(
            "tenant:role_assignment:write"
        ).permission_id
    )



def test_no_domain_profile_permissions():
    assert all(permission_metadata(row["permission_id"]).namespace not in {"DOMAIN", "PROFILE"} for row in json.loads(canonical_permissions()))


# ARTIFACT: test_permission_namespace.py
# VERSION: v1.7.0-M11-R8-R3B-P8-P3D-P4A-CERT
# AUTHORITY BOUNDARY: permission semantic certification only
# TENANT POSTURE: subscription/plan grants remain policy; exact ACTIVE membership remains separately governed
# FAIL-CLOSED POSTURE: unknown and malformed values deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
