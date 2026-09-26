"""TITLE: WILSY OS Permission Namespace Semantic Canon.
VERSION: v1.26.0-L9A3-CLIENT-ACCEPTANCE-IAM
AUTHORITY: Immutable permission vocabulary and scope metadata only.
EPITOME: Extends the canonical TENANT permission vocabulary with dedicated
inbound-collection, merchant-configuration, provider-policy, WILSY AI,
billing-intelligence, Legal Operations lifecycle/client visibility, and explicit
human conflict-review capability semantics without granting tenant-wide matter
enumeration, reviewer identity, legal determination, waiver, engagement,
representation, cross-tenant authority, or financial execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/permission_namespace.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-26.
CHANGELOG:
    2026-09-26 v1.26.0-L9A3-CLIENT-ACCEPTANCE-IAM adds the dedicated own-tenant
    legal_operations:client_acceptance:write permission for server-composed
    client-acceptance evidence. It remains membership-gated, non-cross-tenant,
    non-financial and non-self-authorizing; it does not prove engagement,
    representation, Court, payment, execution or settlement authority.
    2026-09-23 v1.25.0-L8-8I-CONFLICT-REVIEW-IAM adds the dedicated own-tenant
    legal_operations:client_matter:read permission vocabulary for a future
    explicitly-bound LEGAL_CLIENT matter projection only. The permission is
    membership-gated, non-cross-tenant, non-financial and non-self-authorizing;
    it does not grant tenant-wide matter enumeration, internal instruction or
    sheriff/deputy queue visibility, service/return evidence, billing, payment,
    execution, settlement, or visibility provisioning authority.
    2026-09-23 v1.23.0-L8-7C1-CLIENT-VISIBILITY-WRITE-IAM adds the dedicated own-tenant
    legal_operations:client_visibility:write permission vocabulary for future
    L8-7 client-to-matter visibility grant/revoke provisioning. The permission
    is membership-gated, non-cross-tenant, non-financial and non-self-
    authorizing; it does not itself prove actor role, target LEGAL_CLIENT IAM,
    CaseMatter scope, current ACTIVE visibility, client reads, service, billing,
    payment, execution or settlement authority.
    2026-09-23 v1.22.0-L8-6C-DEPUTY-PERSONAL-QUEUE-IAM adds the dedicated own-tenant
    legal_operations:deputy_queue:read permission for an authenticated deputy's
    binding-scoped personal active-work projection only. It is non-cross-tenant,
    non-financial, non-self-authorizing, and does not grant sheriff tenant-wide
    queue visibility, lifecycle mutation, service completion, return, billing,
    payment, AI, execution, or settlement authority.
    2026-09-23 v1.21.0-L8-6A-SHERIFF-QUEUE-READ-IAM adds the dedicated own-tenant
    legal_operations:queue:read permission for authenticated sheriff cockpit
    projection only; it is non-cross-tenant, non-financial, and does not
    authorize queue mutation, deputy impersonation, or personal-queue scope.
    2026-09-23 v1.20.0-L8-3-LEGAL-OPERATIONS-RECEIPT-IAM adds one dedicated
    own-tenant acceptance/office-receipt permission. It remains membership-
    gated, non-cross-tenant, non-financial, and non-self-authorizing; receipt
    authority remains distinct from allocation and service.
    2026-09-23 v1.19.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-IAM adds one
    dedicated own-tenant process-service directory provisioning permission;
    metadata remains membership-gated, non-cross-tenant, non-financial, and
    non-self-authorizing.
    2026-09-17 v1.18.0-C1E-R1 adds dedicated legal-advisory generate/read
    permissions without legal execution, provider, or financial authority.
    2026-09-17 v1.17.0-C1C-R1 adds the dedicated own-tenant legal-services
    execution permission for the governed C1C orchestration route.
    2026-09-16 v1.16.0-C1B-R2 adds the dedicated own-tenant reasoning
    execution permission; it grants no provider, model, financial, or
    cross-tenant authority.
    2026-09-15 v1.15.0-L7B-WILSY-AI-LEGAL-TOOL adds the dedicated own-tenant
    Legal Tool Gateway read permission; it remains non-financial and
    non-cross-tenant.
    2026-09-15 v1.14.0-L7B-LEGAL-OPERATIONS-IAM adds authenticated field-service
    command vocabulary for attempt outcomes and return generation without
    granting typed subject authority or financial execution.
    2026-09-15 v1.13.0-L7A-LEGAL-OPERATIONS-IAM adds explicit own-tenant
    Legal Operations read/write vocabulary without granting authority alone.
    2026-09-13 v1.12.0-M14-P1-BILLING-INTELLIGENCE-EVIDENCE-READ adds the
    canonical own-tenant billing-intelligence evidence read permission; it
    remains membership-gated, non-cross-tenant, non-financial, and
    non-self-authorizing.
    2026-09-13 v1.11.0-M13-P6D-WILSY-AI-CAPACITY-READ adds the canonical
    own-tenant WILSY AI usage-capacity evidence read permission; it remains
    membership-gated, non-cross-tenant, non-financial, and non-self-authorizing.
    2026-09-10 v1.10.0-M11-R8-R3B-P8-P3D-P4A adds four dedicated
    tenant inbound provider credential-security permissions; all remain
    own-tenant, non-financial, and non-self-authorizing.
    2026-09-09 v1.9.0-M11-R8-R3B-P8-P3B-I2-R3 adds the explicit
    inbound merchant-configuration remediation permission for the future
    COMPROMISED-to-DISABLED authority; no lifecycle or secret authority is
    granted.
    2026-09-09 v1.8.0-M11-R8-R3B-P8-P3A adds the seven dedicated
    tenant inbound merchant-configuration and provider-policy permissions;
    all remain explicit, own-tenant, non-financial and non-self-authorizing.
    2026-09-09 v1.7.0-M11-R8-R3B-P6A adds the exact
    inbound_collection:authorization:create tenant privilege; it remains
    provider-neutral, non-financial, and non-self-authorizing.
    2026-09-04 runtime VERSION is the canonical policy provenance source for
    trusted authorization-evidence capture; no policy semantics changed.
    2026-09-04 v1.4.0-PLATFORM-BILLING-RELEASE-PERMISSION adds the
    tenant-scoped platform_billing:release capability without execution authority.
    2026-09-03 v1.3.0-PLAN-PERMISSION-CANON adds plan:read and plan:manage
    as explicit own-tenant, membership-required, non-cross-tenant,
    non-financial canonical permissions.
    v1.2.0-SUBSCRIPTION-PERMISSION-CANON added subscription:read and
    subscription:manage as explicit own-tenant, membership-required,
    non-cross-tenant, non-financial canonical permissions.
    v1.1.0-PERMISSION-NAMESPACE-CANON added the bounded TENANT vocabulary.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Metadata never authenticates, authorizes, proves
membership, trusts transport projections, or grants execution.
TENANT BOUNDARY: Subscription, plan, WILSY AI usage-capacity, and
billing-intelligence evidence read permissions require separately proven ACTIVE
membership in the exact selected tenant and never permit cross-tenant access.
AUTHORITY BOUNDARY: Owns permission vocabulary semantics only. WILSY AI
capacity and billing-intelligence evidence remain read-only projections;
current role assignment and final authorization remain separate authorities.
FINANCIAL AUTHORITY BOUNDARY: Subscription, plan, WILSY AI capacity, and
billing-intelligence evidence permissions cannot approve, release, execute,
collect, or settle funds.
Kennel EOS remains exclusive.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from json import dumps
from types import MappingProxyType
from typing import Final


VERSION = "v1.26.0-L9A3-CLIENT-ACCEPTANCE-IAM"


class PermissionDisposition(StrEnum):
    """Closed permission-canon disposition vocabulary."""

    CANONICAL = "CANONICAL"
    LEGACY_ONLY = "LEGACY_ONLY"
    DEPRECATED = "DEPRECATED"
    BLOCKED_AMBIGUOUS = "BLOCKED_AMBIGUOUS"


@dataclass(frozen=True, slots=True)
class PermissionMetadata:
    """Immutable semantic metadata for one permission identifier."""

    permission_id: str
    namespace: str
    scope_kind: str
    business_capability: str
    tenant_membership_required: bool
    system_assignment_required: bool
    cross_tenant_capable: bool
    financial_execution_capable: bool
    deprecated_or_legacy: bool
    authorizes_by_itself: bool
    disposition: PermissionDisposition


def _meta(
    permission_id: str,
    namespace: str,
    scope: str,
    capability: str,
    *,
    tenant: bool = False,
    system: bool = False,
    disposition: PermissionDisposition = PermissionDisposition.CANONICAL,
) -> PermissionMetadata:
    """Construct immutable metadata without creating authority."""
    return PermissionMetadata(
        permission_id=permission_id,
        namespace=namespace,
        scope_kind=scope,
        business_capability=capability,
        tenant_membership_required=tenant,
        system_assignment_required=system,
        cross_tenant_capable=False,
        financial_execution_capable=False,
        deprecated_or_legacy=(
            disposition is not PermissionDisposition.CANONICAL
        ),
        authorizes_by_itself=False,
        disposition=disposition,
    )


_PERMISSIONS: Final = MappingProxyType(
    {
        "kernel:read": _meta(
            "kernel:read",
            "SYSTEM",
            "SYSTEM",
            "read kernel state",
            system=True,
        ),
        "kernel:write": _meta(
            "kernel:write",
            "SYSTEM",
            "SYSTEM",
            "write kernel state",
            system=True,
        ),
        "governance:evaluate": _meta(
            "governance:evaluate",
            "SYSTEM",
            "SYSTEM",
            "evaluate governance",
            system=True,
        ),
        "governance:read": _meta(
            "governance:read",
            "SYSTEM",
            "SYSTEM",
            "read governance evidence",
            system=True,
        ),
        "artifacts:read": _meta(
            "artifacts:read",
            "TENANT",
            "TENANT",
            "read artifacts",
            tenant=True,
        ),
        "artifacts:write": _meta(
            "artifacts:write",
            "SERVICE",
            "SERVICE",
            "write service artifacts",
        ),
        "events:publish": _meta(
            "events:publish",
            "SERVICE",
            "SERVICE",
            "publish service events",
        ),
        "audit:read": _meta(
            "audit:read",
            "TENANT",
            "TENANT",
            "read tenant audit evidence",
            tenant=True,
        ),
        "tenant:profile:read": _meta(
            "tenant:profile:read",
            "TENANT",
            "TENANT",
            "read bounded tenant profile",
            tenant=True,
        ),
        "tenant:profile:write": _meta(
            "tenant:profile:write",
            "TENANT",
            "TENANT",
            "write bounded tenant profile",
            tenant=True,
        ),
        "tenant:lifecycle:archive": _meta(
            "tenant:lifecycle:archive",
            "TENANT",
            "TENANT",
            "archive own tenant",
            tenant=True,
        ),
        "tenant:membership:read": _meta(
            "tenant:membership:read",
            "TENANT",
            "TENANT",
            "read tenant membership",
            tenant=True,
        ),
        "tenant:membership:write": _meta(
            "tenant:membership:write",
            "TENANT",
            "TENANT",
            "administer tenant membership",
            tenant=True,
        ),
        "tenant:role_assignment:read": _meta(
            "tenant:role_assignment:read",
            "TENANT",
            "TENANT",
            "read tenant role assignments",
            tenant=True,
        ),
        "tenant:role_assignment:write": _meta(
            "tenant:role_assignment:write",
            "TENANT",
            "TENANT",
            "administer tenant role assignments",
            tenant=True,
        ),
        "tenant:business_role:read": _meta(
            "tenant:business_role:read",
            "TENANT",
            "TENANT",
            "read tenant business-role authority",
            tenant=True,
            system=True,
        ),
        "tenant:business_role:write": _meta(
            "tenant:business_role:write",
            "TENANT",
            "TENANT",
            "change tenant business-role authority",
            tenant=True,
            system=True,
        ),
        "subscription:read": _meta(
            "subscription:read",
            "TENANT",
            "TENANT",
            "read own-tenant subscription commercial truth",
            tenant=True,
        ),
        "subscription:manage": _meta(
            "subscription:manage",
            "TENANT",
            "TENANT",
            "manage own-tenant subscription lifecycle truth",
            tenant=True,
        ),
        "plan:read": _meta(
            "plan:read",
            "TENANT",
            "TENANT",
            "read own-tenant plan catalogue commercial truth",
            tenant=True,
        ),
        "plan:manage": _meta(
            "plan:manage",
            "TENANT",
            "TENANT",
            "manage own-tenant plan catalogue lifecycle truth",
            tenant=True,
        ),
        "wilsy_ai:usage_capacity:read": _meta(
            "wilsy_ai:usage_capacity:read",
            "TENANT",
            "TENANT",
            "read own-tenant WILSY AI usage-capacity evidence",
            tenant=True,
        ),
        "wilsy_ai:legal_tool:read": _meta(
            "wilsy_ai:legal_tool:read",
            "TENANT",
            "TENANT",
            "invoke own-tenant WILSY AI Legal Tool Gateway reads",
            tenant=True,
        ),
        "wilsy_ai:reasoning:execute": _meta(
            "wilsy_ai:reasoning:execute", "TENANT", "TENANT",
            "execute authenticated WILSY AI reasoning admission",
            tenant=True,
        ),
        "wilsy_ai:legal_services:execute": _meta(
            "wilsy_ai:legal_services:execute", "TENANT", "TENANT",
            "execute authenticated own-tenant WILSY AI Legal Services orchestration",
            tenant=True,
        ),
        "wilsy_ai:legal_advisory:generate": _meta(
            "wilsy_ai:legal_advisory:generate", "TENANT", "TENANT",
            "generate own-tenant evidence-backed legal advisory", tenant=True,
        ),
        "wilsy_ai:legal_advisory:read": _meta(
            "wilsy_ai:legal_advisory:read", "TENANT", "TENANT",
            "read own-tenant evidence-backed legal advisory", tenant=True,
        ),
        "billing_intelligence:evidence:read": _meta(
            "billing_intelligence:evidence:read",
            "TENANT",
            "TENANT",
            "read own-tenant canonical billing-intelligence evidence",
            tenant=True,
        ),
        "legal_operations:instruction:read": _meta(
            "legal_operations:instruction:read", "TENANT", "TENANT",
            "read own-tenant legal instructions", tenant=True,
        ),
        "legal_operations:instruction:write": _meta(
            "legal_operations:instruction:write", "TENANT", "TENANT",
            "operate own-tenant legal instructions", tenant=True,
        ),
        "legal_operations:directory:write": _meta(
            "legal_operations:directory:write", "TENANT", "TENANT",
            "provision own-tenant process-service directory identities", tenant=True,
        ),
        "legal_operations:receipt:write": _meta(
            "legal_operations:receipt:write", "TENANT", "TENANT",
            "accept own-tenant instructions and record sheriff-office receipt", tenant=True,
        ),
        "legal_operations:queue:read": _meta(
            "legal_operations:queue:read", "TENANT", "TENANT",
            "read own-tenant certified sheriff operational queues", tenant=True,
        ),
        "legal_operations:deputy_queue:read": _meta(
            "legal_operations:deputy_queue:read", "TENANT", "TENANT",
            "read binding-scoped own active service-attempt work", tenant=True,
        ),
        "legal_operations:client_visibility:write": _meta(
            "legal_operations:client_visibility:write", "TENANT", "TENANT",
            "provision explicit own-tenant legal-client matter visibility",
            tenant=True,
        ),
        "legal_operations:client_matter:read": _meta(
            "legal_operations:client_matter:read", "TENANT", "TENANT",
            "read explicitly-bound own legal-client matters",
            tenant=True,
        ),
        "legal_operations:client_acceptance:write": _meta(
            "legal_operations:client_acceptance:write", "TENANT", "TENANT",
            "issue bounded own-tenant client-acceptance evidence", tenant=True,
        ),
        "legal_operations:conflict_review:write": _meta(
            "legal_operations:conflict_review:write", "TENANT", "TENANT",
            "record authorized own-tenant human conflict-review determinations",
            tenant=True,
        ),
        "legal_operations:allocation:read": _meta(
            "legal_operations:allocation:read", "TENANT", "TENANT",
            "read own-tenant process allocations", tenant=True,
        ),
        "legal_operations:allocation:write": _meta(
            "legal_operations:allocation:write", "TENANT", "TENANT",
            "operate own-tenant process allocations", tenant=True,
        ),
        "legal_operations:attempt:read": _meta(
            "legal_operations:attempt:read", "TENANT", "TENANT",
            "read own-tenant service attempts", tenant=True,
        ),
        "legal_operations:attempt:write": _meta(
            "legal_operations:attempt:write", "TENANT", "TENANT",
            "operate own-tenant service attempts", tenant=True,
        ),
        "legal_operations:attempt_outcome:write": _meta(
            "legal_operations:attempt_outcome:write", "TENANT", "TENANT",
            "record own-tenant terminal service-attempt outcomes", tenant=True,
        ),
        "legal_operations:return:read": _meta(
            "legal_operations:return:read", "TENANT", "TENANT",
            "read own-tenant returns of service", tenant=True,
        ),
        "legal_operations:return:write": _meta(
            "legal_operations:return:write", "TENANT", "TENANT",
            "generate own-tenant returns of service", tenant=True,
        ),
        "legal_operations:billing:read": _meta(
            "legal_operations:billing:read", "TENANT", "TENANT",
            "read own-tenant legal billing evidence", tenant=True,
        ),
        "legal_operations:invoice:read": _meta(
            "legal_operations:invoice:read", "TENANT", "TENANT",
            "read own-tenant legal invoice evidence", tenant=True,
        ),
        "platform_billing:provider_policy:admin": _meta(
            "platform_billing:provider_policy:admin",
            "TENANT",
            "TENANT",
            "administer platform billing provider policy lifecycle",
            tenant=True,
        ),
        "accounts_payable:provider_policy:admin": _meta(
            "accounts_payable:provider_policy:admin",
            "TENANT",
            "ACCOUNTS_PAYABLE",
            "administer accounts-payable provider policy",
            tenant=True,
        ),
        "platform_billing:release": _meta(
            "platform_billing:release",
            "TENANT",
            "TENANT",
            "authorize platform billing release",
            tenant=True,
        ),
        "inbound_collection:authorization:create": _meta(
            "inbound_collection:authorization:create",
            "TENANT",
            "TENANT",
            "request inbound collection authorization creation",
            tenant=True,
        ),
        "inbound_merchant_configuration:register": _meta(
            "inbound_merchant_configuration:register",
            "TENANT",
            "TENANT",
            "register inbound merchant configuration identity",
            tenant=True,
        ),
        "inbound_merchant_configuration:lifecycle": _meta(
            "inbound_merchant_configuration:lifecycle",
            "TENANT",
            "TENANT",
            "transition inbound merchant configuration lifecycle",
            tenant=True,
        ),
        "inbound_merchant_configuration:security": _meta(
            "inbound_merchant_configuration:security",
            "TENANT",
            "TENANT",
            "contain compromised inbound merchant configuration",
            tenant=True,
        ),
        "inbound_merchant_configuration:remediate": _meta(
            "inbound_merchant_configuration:remediate",
            "TENANT",
            "TENANT",
            "remediate compromised inbound merchant configuration",
            tenant=True,
        ),
        "inbound_provider_credential_security:eligibility_issue": _meta(
            "inbound_provider_credential_security:eligibility_issue",
            "TENANT",
            "TENANT",
            "issue credential-security eligibility evidence",
            tenant=True,
        ),
        "inbound_provider_credential_security:revoke": _meta(
            "inbound_provider_credential_security:revoke",
            "TENANT",
            "TENANT",
            "revoke credential-security eligibility evidence",
            tenant=True,
        ),
        "inbound_provider_credential_security:compromise": _meta(
            "inbound_provider_credential_security:compromise",
            "TENANT",
            "TENANT",
            "record credential-security compromise evidence",
            tenant=True,
        ),
        "inbound_provider_credential_security:rotate": _meta(
            "inbound_provider_credential_security:rotate",
            "TENANT",
            "TENANT",
            "record credential-security rotation evidence",
            tenant=True,
        ),
        "inbound_provider_policy:author": _meta(
            "inbound_provider_policy:author",
            "TENANT",
            "TENANT",
            "author inbound provider policy revisions",
            tenant=True,
        ),
        "inbound_provider_policy:activate": _meta(
            "inbound_provider_policy:activate",
            "TENANT",
            "TENANT",
            "activate inbound provider policy",
            tenant=True,
        ),
        "inbound_provider_policy:deactivate": _meta(
            "inbound_provider_policy:deactivate",
            "TENANT",
            "TENANT",
            "deactivate inbound provider policy",
            tenant=True,
        ),
        "inbound_provider_policy:emergency_disable": _meta(
            "inbound_provider_policy:emergency_disable",
            "TENANT",
            "TENANT",
            "emergency-disable inbound provider policy",
            tenant=True,
        ),
        "execution:trigger": _meta(
            "execution:trigger",
            "SYSTEM",
            "UNSAFE_MULTI_NAMESPACE",
            "trigger non-financial execution",
            disposition=PermissionDisposition.BLOCKED_AMBIGUOUS,
        ),
        "tenant:manage": _meta(
            "tenant:manage",
            "TENANT",
            "UNRESOLVED",
            "tenant administration (scope unresolved)",
            tenant=True,
            disposition=PermissionDisposition.BLOCKED_AMBIGUOUS,
        ),
        "admin:all": _meta(
            "admin:all",
            "SYSTEM",
            "LEGACY",
            "legacy administrative label",
            system=True,
            disposition=PermissionDisposition.LEGACY_ONLY,
        ),
    }
)


def permission_metadata(
    permission_id: str,
) -> PermissionMetadata:
    """Return exact immutable metadata; malformed and unknown values deny."""
    if (
        not isinstance(permission_id, str)
        or not permission_id
        or permission_id != permission_id.strip()
    ):
        raise ValueError("UNKNOWN_PERMISSION")

    try:
        return _PERMISSIONS[permission_id]
    except KeyError as error:
        raise ValueError(
            "UNKNOWN_PERMISSION"
        ) from error


def canonical_permissions() -> bytes:
    """Serialize the immutable permission canon deterministically."""
    rows = [
        {
            "permission_id": value.permission_id,
            "namespace": value.namespace,
            "scope_kind": value.scope_kind,
            "business_capability": value.business_capability,
            "tenant_membership_required":
                value.tenant_membership_required,
            "system_assignment_required":
                value.system_assignment_required,
            "cross_tenant_capable":
                value.cross_tenant_capable,
            "financial_execution_capable":
                value.financial_execution_capable,
            "deprecated_or_legacy":
                value.deprecated_or_legacy,
            "authorizes_by_itself":
                value.authorizes_by_itself,
            "disposition":
                value.disposition.value,
        }
        for value in _PERMISSIONS.values()
    ]

    return dumps(
        rows,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")


def classify_legacy_permission(
    permission_id: object,
) -> PermissionDisposition | None:
    """Classify known noncanonical permissions without authorizing."""
    if (
        not isinstance(permission_id, str)
        or not permission_id
        or permission_id != permission_id.strip()
    ):
        return None

    try:
        return permission_metadata(
            permission_id
        ).disposition
    except ValueError:
        return None


__all__ = [
    "PermissionDisposition",
    "PermissionMetadata",
    "VERSION",
    "permission_metadata",
    "canonical_permissions",
    "classify_legacy_permission",
]

# ARTIFACT: tools/eos/auth/permission_namespace.py
# VERSION: v1.26.0-L9A3-CLIENT-ACCEPTANCE-IAM
# AUTHORITY BOUNDARY: canonical permission vocabulary semantics only; no possession or authorization authority
# TENANT POSTURE: conflict-review, client-matter, client-visibility and other tenant permissions require separately proven exact ACTIVE tenant membership
# FAIL-CLOSED POSTURE: unknown, malformed, ambiguous and legacy values never manufacture authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
