"""
TITLE: WILSY OS CRM Sales Business Role Catalog
VERSION: v1.0.0-CRM-SALES-BUSINESS-ROLE-CATALOG

AUTHORITY:
    Immutable canonical CRM sales business-role vocabulary only.

EPITOME:
    Defines the researched professional role taxonomy used by sovereign CRM
    authorization policy while preserving strict separation between business
    eligibility, IAM permission, tenant membership, entitlement, record scope,
    sensitivity, workflow state, AI and execution authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/crm_sales_business_role_catalog.py

RESEARCH BASIS:
    Apollo:
        Separates ownership changes, assignment targets, bulk import, merge,
        export and stage administration from general persona identity.

    Salesforce:
        Separates business role from record ownership, hierarchy, sharing,
        teams and territories.

    HubSpot:
        Separates own/team/all record access from object-operation permission
        and treats explicit sharing as an additional record relationship.

    Dynamics 365 Sales:
        Distinguishes primary selling roles from functional sales roles such
        as forecasting and sequence administration.

    WILSY OS:
        - HR business-role catalogue provides the immutable family precedent.
        - RecordScopeEvidence owns relationship scope independently.
        - Tenant business-role authority owns assignment/currentness evidence.
        - Permission namespace and tenant authorization own effective
          operation authorization.

ROLE FAMILIES:
    PRIMARY_SELLERS
    SALES_LEADERSHIP
    SALES_OPERATIONS
    FUNCTIONAL_SALES
    REVENUE_ASSURANCE

AUTHORITY BOUNDARY:
    Catalogue membership establishes professional business-role vocabulary
    only. It does not authenticate a principal, prove tenant membership,
    assign a business role, grant a permission, establish entitlement,
    create record scope, bypass sensitivity or authorize a command.

RECORD-SCOPE BOUNDARY:
    A seller, manager, executive, RevOps operator or auditor never receives
    OWN, ASSIGNED, TEAM, REPORTING_LINE, TERRITORY, BUSINESS_UNIT or TENANT
    record scope merely because the role appears in this catalogue.
    Separately certified RecordScopeEvidence remains mandatory.

EMPLOYMENT-TITLE BOUNDARY:
    Human-readable employment titles and browser/client role tokens are
    presentation/profile facts only and never establish server authority.

GENERIC-TENANT-ROLE BOUNDARY:
    tenant_owner, tenant_admin, tenant_manager and tenant_auditor remain
    platform governance roles. They are deliberately not CRM sales personas.

CUSTOMER-SUCCESS BOUNDARY:
    Customer Success, renewal, retention and expansion roles are deliberately
    excluded pending their own lifecycle and authority research.

COMMERCIAL-MANAGER BOUNDARY:
    "Commercial Manager" is deliberately excluded because the existing UI
    token is too semantically broad to canonize without its own authority
    contract.

AI BOUNDARY:
    This catalogue grants no AI execution, scoring, inference, recommendation
    or autonomous-action authority.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.

MUTATION BOUNDARY:
    Pure frozen catalogue constants only. No persistence, HTTP, authorization
    execution, role assignment, lifecycle transition or workflow mutation.

CHANGELOG:
    2026-10-07 v1.0.0 establishes the researched canonical CRM sales
    business-role families.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Final, Mapping


CRM_SALES_BUSINESS_ROLE_CATALOG_VERSION: Final[str] = (
    "v1.0.0-CRM-SALES-BUSINESS-ROLE-CATALOG"
)


CRM_PRIMARY_SELLER_ROLES: Final[frozenset[str]] = frozenset({
    "tenant_crm_sdr",
    "tenant_crm_bdr",
    "tenant_crm_sales_rep",
    "tenant_crm_sales_consultant",
    "tenant_crm_account_executive",
    "tenant_crm_account_manager",
})


CRM_SALES_LEADERSHIP_ROLES: Final[frozenset[str]] = frozenset({
    "tenant_crm_team_lead",
    "tenant_crm_sales_manager",
    "tenant_crm_sales_director",
    "tenant_crm_vp_sales",
    "tenant_crm_chief_revenue_officer",
})


CRM_SALES_OPERATIONS_ROLES: Final[frozenset[str]] = frozenset({
    "tenant_crm_revops",
    "tenant_crm_sales_operations",
    "tenant_crm_manager",
})


CRM_FUNCTIONAL_SALES_ROLES: Final[frozenset[str]] = frozenset({
    "tenant_crm_forecast_manager",
    "tenant_crm_sequence_manager",
    "tenant_crm_sales_enablement",
})


CRM_REVENUE_ASSURANCE_ROLES: Final[frozenset[str]] = frozenset({
    "tenant_crm_auditor",
    "tenant_crm_revenue_analyst",
})


_CRM_SALES_ROLE_FAMILIES: Final[
    dict[str, frozenset[str]]
] = {
    "PRIMARY_SELLERS":
        CRM_PRIMARY_SELLER_ROLES,
    "SALES_LEADERSHIP":
        CRM_SALES_LEADERSHIP_ROLES,
    "SALES_OPERATIONS":
        CRM_SALES_OPERATIONS_ROLES,
    "FUNCTIONAL_SALES":
        CRM_FUNCTIONAL_SALES_ROLES,
    "REVENUE_ASSURANCE":
        CRM_REVENUE_ASSURANCE_ROLES,
}


CRM_SALES_ROLE_FAMILIES: Final[
    Mapping[str, frozenset[str]]
] = MappingProxyType(
    _CRM_SALES_ROLE_FAMILIES
)


ALL_CRM_SALES_BUSINESS_ROLES: Final[
    frozenset[str]
] = frozenset(
    role
    for roles in CRM_SALES_ROLE_FAMILIES.values()
    for role in roles
)


__all__ = [
    "CRM_SALES_BUSINESS_ROLE_CATALOG_VERSION",
    "CRM_SALES_ROLE_FAMILIES",
    "ALL_CRM_SALES_BUSINESS_ROLES",
    "CRM_PRIMARY_SELLER_ROLES",
    "CRM_SALES_LEADERSHIP_ROLES",
    "CRM_SALES_OPERATIONS_ROLES",
    "CRM_FUNCTIONAL_SALES_ROLES",
    "CRM_REVENUE_ASSURANCE_ROLES",
]

# ARTIFACT: crm_sales_business_role_catalog.py
# VERSION: v1.0.0-CRM-SALES-BUSINESS-ROLE-CATALOG
# AUTHORITY BOUNDARY: immutable business-role vocabulary only
# RECORD-SCOPE BOUNDARY: roles never manufacture record relationship scope
# TENANT POSTURE: canonical tenant_crm_* professional role identifiers only
# CUSTOMER SUCCESS: excluded pending separate research
# AI AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
