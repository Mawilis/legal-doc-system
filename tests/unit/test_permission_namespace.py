"""TITLE: WILSY OS Permission Namespace Canon Certification.
VERSION: v1.19.0-L8-7C1-CLIENT-VISIBILITY-WRITE-IAM-CERT
AUTHORITY: Certification of immutable permission vocabulary semantics only.
EPITOME: Proves bounded namespaces, fail-closed metadata, deterministic policy
bytes, and exact own-tenant subscription/plan/WILSY AI capacity,
billing-intelligence evidence-read, and field-service outcome/return command
semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_permission_namespace.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-23.
CHANGELOG:
    2026-09-23 v1.19.0-L8-7C1-CLIENT-VISIBILITY-WRITE-IAM-CERT
    certifies legal_operations:client_visibility:write as one exact canonical
    TENANT permission for bounded future client-to-matter grant/revoke
    provisioning only. It requires separately proven membership, is non-cross-
    tenant, non-financial and non-self-authorizing, and raises canon cardinality
    to exactly 60 canonical permissions / 63 total rows.
    2026-09-23 v1.18.1-L8-6C-DEPUTY-PERSONAL-QUEUE-IAM-CERT
    corrects the direct-certificate cardinality after the already-certified
    legal_operations:deputy_queue:read addition: the permission canon now
    contains exactly 59 canonical permissions and 62 total rows. Production
    permission semantics and authorization behavior are unchanged.
    2026-09-23 v1.18.0-L8-6C-DEPUTY-PERSONAL-QUEUE-IAM-CERT
    certifies legal_operations:deputy_queue:read as one exact canonical TENANT
    permission for binding-scoped personal active-work projection only, with
    membership required, no cross-tenant capability, no financial execution,
    and no self-authorizing behavior.
    2026-09-23 v1.17.0-L8-6A-SHERIFF-QUEUE-READ-IAM-CERT
    certifies legal_operations:queue:read as one exact canonical TENANT
    permission with non-cross-tenant, non-financial, non-self-authorizing
    metadata and no deputy-personalization authority.
    2026-09-23 v1.16.0-L8-3-LEGAL-OPERATIONS-RECEIPT-IAM-CERT
    certifies legal_operations:receipt:write as one exact canonical TENANT
    permission with non-cross-tenant, non-financial, non-self-authorizing
    metadata and malformed-alias rejection.
    2026-09-23 v1.15.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-IAM-CERT certifies
    the dedicated own-tenant legal_operations:directory:write permission,
    exact non-financial/non-self-authorizing metadata, and fail-closed aliases.
    2026-09-17 v1.14.0-C1E-R1 certifies the dedicated legal-advisory
    generate/read permissions and exact tenant-only metadata.
    2026-09-15 v1.12.0-L7B-WILSY-AI-LEGAL-TOOL-PERMISSION-CERT certifies
    the dedicated tenant-scoped gateway read permission and its non-financial,
    non-self-authorizing metadata.
    2026-09-15 v1.11.0-L7B-LEGAL-OPERATIONS-COMMAND-PERMISSION-CERT certifies
    the attempt-outcome and return-write command permissions, yielding exactly
    50 canonical permissions and 53 total rows while preserving prior
    own-tenant evidence-read metadata and fail-closed alias rejection.
    2026-09-13 v1.8.0-M13-P6D-WILSY-AI-CAPACITY-READ-CERT certifies the
    canonical own-tenant WILSY AI usage-capacity evidence read permission,
    including its membership and non-financial metadata and alias rejection.
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
TENANT BOUNDARY: Permission metadata never proves membership; subscription,
plan, WILSY AI capacity-read, and billing-intelligence evidence-read
permissions require separately proven exact ACTIVE tenant membership.
AUTHORITY BOUNDARY: Tests policy metadata, not assignment or authorization.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
import json

import pytest

VERSION = "v1.19.0-L8-7C1-CLIENT-VISIBILITY-WRITE-IAM-CERT"

from tools.eos.auth.permission_namespace import PermissionDisposition, VERSION as POLICY_VERSION, canonical_permissions, classify_legacy_permission, permission_metadata

def test_runtime_version_source_is_canonical() -> None:
    assert POLICY_VERSION == "v1.23.0-L8-7C1-CLIENT-VISIBILITY-WRITE-IAM"


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
        "wilsy_ai:usage_capacity:read",
        "billing_intelligence:evidence:read",
        "wilsy_ai:legal_tool:read",
        "wilsy_ai:legal_services:execute",
        "wilsy_ai:legal_advisory:generate",
        "wilsy_ai:legal_advisory:read",
        "legal_operations:instruction:read",
        "legal_operations:instruction:write",
        "legal_operations:directory:write",
        "legal_operations:receipt:write",
        "legal_operations:queue:read",
        "legal_operations:deputy_queue:read",
        "legal_operations:client_visibility:write",
        "legal_operations:allocation:read",
        "legal_operations:allocation:write",
        "legal_operations:attempt:read",
        "legal_operations:attempt:write",
        "legal_operations:attempt_outcome:write",
        "legal_operations:return:read",
        "legal_operations:return:write",
        "legal_operations:billing:read",
        "legal_operations:invoice:read",
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
    ) == 60

    assert len(rows) == 63

    for permission_id in tenant:
        metadata = permission_metadata(
            permission_id
        )

        assert metadata.namespace == "TENANT"
        assert metadata.tenant_membership_required is True
        assert metadata.cross_tenant_capable is False
        assert metadata.financial_execution_capable is False
        assert metadata.authorizes_by_itself is False

    gateway = permission_metadata("wilsy_ai:legal_tool:read")
    assert gateway.namespace == "TENANT"
    assert gateway.scope_kind == "TENANT"
    assert gateway.tenant_membership_required is True
    assert gateway.cross_tenant_capable is False
    assert gateway.financial_execution_capable is False
    assert gateway.authorizes_by_itself is False
    assert gateway.disposition is PermissionDisposition.CANONICAL

    legal_services = permission_metadata("wilsy_ai:legal_services:execute")
    assert legal_services.namespace == "TENANT"
    assert legal_services.scope_kind == "TENANT"
    assert legal_services.tenant_membership_required is True
    assert legal_services.cross_tenant_capable is False
    assert legal_services.financial_execution_capable is False
    assert legal_services.authorizes_by_itself is False
    assert legal_services.disposition is PermissionDisposition.CANONICAL

    wilsy_ai_capacity = permission_metadata("wilsy_ai:usage_capacity:read")
    assert wilsy_ai_capacity.namespace == "TENANT"
    assert wilsy_ai_capacity.scope_kind == "TENANT"
    assert wilsy_ai_capacity.business_capability == "read own-tenant WILSY AI usage-capacity evidence"
    assert wilsy_ai_capacity.tenant_membership_required is True
    assert wilsy_ai_capacity.system_assignment_required is False
    assert wilsy_ai_capacity.cross_tenant_capable is False
    assert wilsy_ai_capacity.financial_execution_capable is False
    assert wilsy_ai_capacity.authorizes_by_itself is False
    assert wilsy_ai_capacity.disposition is PermissionDisposition.CANONICAL

    billing_intelligence = permission_metadata(
        "billing_intelligence:evidence:read"
    )
    assert billing_intelligence.namespace == "TENANT"
    assert billing_intelligence.scope_kind == "TENANT"
    assert billing_intelligence.business_capability == "read own-tenant canonical billing-intelligence evidence"
    assert billing_intelligence.tenant_membership_required is True
    assert billing_intelligence.system_assignment_required is False
    assert billing_intelligence.cross_tenant_capable is False
    assert billing_intelligence.financial_execution_capable is False
    assert billing_intelligence.authorizes_by_itself is False
    assert billing_intelligence.disposition is PermissionDisposition.CANONICAL

    queue_read = permission_metadata("legal_operations:queue:read")
    assert queue_read.namespace == "TENANT"
    assert queue_read.scope_kind == "TENANT"
    assert queue_read.business_capability == "read own-tenant certified sheriff operational queues"
    assert queue_read.tenant_membership_required is True
    assert queue_read.cross_tenant_capable is False
    assert queue_read.financial_execution_capable is False
    assert queue_read.authorizes_by_itself is False
    assert queue_read.disposition is PermissionDisposition.CANONICAL

    deputy_queue_read = permission_metadata("legal_operations:deputy_queue:read")
    assert deputy_queue_read.namespace == "TENANT"
    assert deputy_queue_read.scope_kind == "TENANT"
    assert (
        deputy_queue_read.business_capability
        == "read binding-scoped own active service-attempt work"
    )
    assert deputy_queue_read.tenant_membership_required is True
    assert deputy_queue_read.cross_tenant_capable is False
    assert deputy_queue_read.financial_execution_capable is False
    assert deputy_queue_read.authorizes_by_itself is False
    assert deputy_queue_read.disposition is PermissionDisposition.CANONICAL

    client_visibility_write = permission_metadata(
        "legal_operations:client_visibility:write"
    )
    assert client_visibility_write.namespace == "TENANT"
    assert client_visibility_write.scope_kind == "TENANT"
    assert (
        client_visibility_write.business_capability
        == "provision explicit own-tenant legal-client matter visibility"
    )
    assert client_visibility_write.tenant_membership_required is True
    assert client_visibility_write.system_assignment_required is False
    assert client_visibility_write.cross_tenant_capable is False
    assert client_visibility_write.financial_execution_capable is False
    assert client_visibility_write.authorizes_by_itself is False
    assert client_visibility_write.disposition is PermissionDisposition.CANONICAL

    command_permissions = {
        "legal_operations:directory:write":
            "provision own-tenant process-service directory identities",
        "legal_operations:receipt:write":
            "accept own-tenant instructions and record sheriff-office receipt",
        "legal_operations:attempt_outcome:write":
            "record own-tenant terminal service-attempt outcomes",
        "legal_operations:return:write":
            "generate own-tenant returns of service",
    }
    for permission_id, capability in command_permissions.items():
        metadata = permission_metadata(permission_id)
        assert metadata.namespace == "TENANT"
        assert metadata.scope_kind == "TENANT"
        assert metadata.tenant_membership_required is True
        assert metadata.cross_tenant_capable is False
        assert metadata.financial_execution_capable is False
        assert metadata.authorizes_by_itself is False
        assert metadata.disposition is PermissionDisposition.CANONICAL
        assert metadata.business_capability == capability

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
        "wilsy_ai:*",
        "wilsy_ai:usage_capacity:*",
        "WILSY_AI:USAGE_CAPACITY:READ",
        " wilsy_ai:usage_capacity:read",
        "wilsy_ai:usage_capacity:read ",
        "wilsy_ai:usage_capacity:READ",
        "billing_intelligence:*",
        "billing_intelligence:evidence:*",
        "BILLING_INTELLIGENCE:EVIDENCE:READ",
        " billing_intelligence:evidence:read",
        "billing_intelligence:evidence:read ",
        "billing_intelligence:evidence:READ",
        "billing_intelligence:evidence",
        "legal_operations:directory:*",
        "legal_operations:directory:write ",
        " legal_operations:directory:write",
        "LEGAL_OPERATIONS:DIRECTORY:WRITE",
        "legal_operations:receipt:*",
        "legal_operations:receipt",
        "LEGAL_OPERATIONS:RECEIPT:WRITE",
        " legal_operations:receipt:write",
        "legal_operations:receipt:write ",
        "legal_operations:client_visibility:*",
        "legal_operations:client_visibility",
        "LEGAL_OPERATIONS:CLIENT_VISIBILITY:WRITE",
        " legal_operations:client_visibility:write",
        "legal_operations:client_visibility:write ",
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
# VERSION: v1.19.0-L8-7C1-CLIENT-VISIBILITY-WRITE-IAM-CERT
# AUTHORITY BOUNDARY: permission semantic certification only
# TENANT POSTURE: client-visibility and other tenant permissions remain policy; exact ACTIVE membership remains separately governed
# FAIL-CLOSED POSTURE: unknown and malformed values deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT