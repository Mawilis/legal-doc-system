"""
TITLE: WILSY OS CRM Sales Business Role Catalog Direct Certificate
VERSION: v1.0.0-P0-CRM-SALES-BUSINESS-ROLE-CATALOG-CERT

AUTHORITY:
    Test-first contract for the canonical CRM sales business-role vocabulary.

EPITOME:
    Freezes the researched sales persona taxonomy used by sovereign CRM
    authorization policy while preserving strict separation between business
    eligibility, IAM permission, tenant membership, entitlement, record scope,
    sensitivity, workflow state and execution authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_crm_sales_business_role_catalog.py

RESEARCH BASIS:
    - Apollo permission profiles and ownership/assignment controls.
    - Salesforce role hierarchy, sharing, teams and territories.
    - HubSpot ownership/share/seat separation.
    - Dynamics Sales primary and functional sales roles.
    - WILSY CRM presentation vocabulary.
    - WILSY HR immutable role-family catalogue precedent.
    - WILSY tenant business-role authority.
    - WILSY shared RecordScopeEvidence domain.

SECURITY DOCTRINE:
    A CRM business role describes professional eligibility only.
    It does not authenticate, prove tenant membership, grant IAM permission,
    grant record scope, establish entitlement, bypass sensitivity, create
    pipeline state, execute workflows, authorize AI or authorize finance.

RECORD-SCOPE BOUNDARY:
    Seller, manager, executive, RevOps and auditor labels never manufacture
    OWN, TEAM, REPORTING_LINE, TERRITORY, BUSINESS_UNIT or TENANT scope.
    Those relationships require separately certified RecordScopeEvidence.

GENERIC-TENANT-ROLE BOUNDARY:
    tenant_owner, tenant_admin, tenant_manager and tenant_auditor remain
    platform-governance roles and are not canonical CRM sales personas.

CUSTOMER-SUCCESS BOUNDARY:
    Customer Success roles remain outside this catalogue pending their own
    lifecycle, account-stewardship and authority research.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.

CHANGELOG:
    2026-10-07 v1.0.0 freezes the researched CRM sales role taxonomy.
"""

from __future__ import annotations

from types import MappingProxyType

import pytest

import tools.eos.auth.crm_sales_business_role_catalog as catalog


EXPECTED_VERSION = (
    "v1.0.0-CRM-SALES-BUSINESS-ROLE-CATALOG"
)

EXPECTED_PRIMARY_SELLERS = frozenset({
    "tenant_crm_sdr",
    "tenant_crm_bdr",
    "tenant_crm_sales_rep",
    "tenant_crm_sales_consultant",
    "tenant_crm_account_executive",
    "tenant_crm_account_manager",
})

EXPECTED_LEADERSHIP = frozenset({
    "tenant_crm_team_lead",
    "tenant_crm_sales_manager",
    "tenant_crm_sales_director",
    "tenant_crm_vp_sales",
    "tenant_crm_chief_revenue_officer",
})

EXPECTED_OPERATIONS = frozenset({
    "tenant_crm_revops",
    "tenant_crm_sales_operations",
    "tenant_crm_manager",
})

EXPECTED_FUNCTIONAL = frozenset({
    "tenant_crm_forecast_manager",
    "tenant_crm_sequence_manager",
    "tenant_crm_sales_enablement",
})

EXPECTED_ASSURANCE = frozenset({
    "tenant_crm_auditor",
    "tenant_crm_revenue_analyst",
})

EXPECTED_FAMILIES = {
    "PRIMARY_SELLERS": EXPECTED_PRIMARY_SELLERS,
    "SALES_LEADERSHIP": EXPECTED_LEADERSHIP,
    "SALES_OPERATIONS": EXPECTED_OPERATIONS,
    "FUNCTIONAL_SALES": EXPECTED_FUNCTIONAL,
    "REVENUE_ASSURANCE": EXPECTED_ASSURANCE,
}

EXPECTED_ROLES = frozenset(
    role
    for roles in EXPECTED_FAMILIES.values()
    for role in roles
)


def test_version_is_exact() -> None:
    assert (
        catalog.CRM_SALES_BUSINESS_ROLE_CATALOG_VERSION
        == EXPECTED_VERSION
    )


def test_role_families_are_mapping_proxy() -> None:
    assert isinstance(
        catalog.CRM_SALES_ROLE_FAMILIES,
        MappingProxyType,
    )


def test_role_family_names_are_closed_and_exact() -> None:
    assert (
        set(catalog.CRM_SALES_ROLE_FAMILIES)
        == set(EXPECTED_FAMILIES)
    )


@pytest.mark.parametrize(
    ("family", "expected_roles"),
    tuple(EXPECTED_FAMILIES.items()),
)
def test_each_family_is_exact_and_immutable(
    family: str,
    expected_roles: frozenset[str],
) -> None:
    actual = catalog.CRM_SALES_ROLE_FAMILIES[
        family
    ]

    assert isinstance(actual, frozenset)
    assert actual == expected_roles


def test_all_roles_are_exact() -> None:
    assert len(EXPECTED_ROLES) == 19
    assert (
        catalog.ALL_CRM_SALES_BUSINESS_ROLES
        == EXPECTED_ROLES
    )


def test_every_role_is_unique_across_families() -> None:
    flattened = [
        role
        for roles in catalog.CRM_SALES_ROLE_FAMILIES.values()
        for role in roles
    ]

    assert len(flattened) == len(set(flattened))
    assert len(flattened) == 19


def test_every_role_is_canonical_tenant_crm_role() -> None:
    for role in catalog.ALL_CRM_SALES_BUSINESS_ROLES:
        assert role.startswith("tenant_crm_")
        assert role == role.strip()
        assert role == role.lower()
        assert " " not in role


@pytest.mark.parametrize(
    "role",
    (
        "tenant_owner",
        "tenant_admin",
        "tenant_manager",
        "tenant_auditor",
    ),
)
def test_generic_platform_roles_are_not_sales_personas(
    role: str,
) -> None:
    assert (
        role
        not in catalog.ALL_CRM_SALES_BUSINESS_ROLES
    )


@pytest.mark.parametrize(
    "role",
    (
        "owner",
        "admin",
        "manager",
        "auditor",
        "founder",
        "ceo",
        "super_admin",
        "workspace_admin",
        "crm_admin",
    ),
)
def test_client_or_platform_role_tokens_are_not_canonical_business_roles(
    role: str,
) -> None:
    assert (
        role
        not in catalog.ALL_CRM_SALES_BUSINESS_ROLES
    )


@pytest.mark.parametrize(
    "role",
    (
        "sales_rep",
        "sales_consultant",
        "account_executive",
        "sales_manager",
        "crm_manager",
        "revops",
        "team_lead",
    ),
)
def test_unscoped_ui_tokens_are_not_server_business_role_ids(
    role: str,
) -> None:
    assert (
        role
        not in catalog.ALL_CRM_SALES_BUSINESS_ROLES
    )


@pytest.mark.parametrize(
    "forbidden",
    (
        "commercial_manager",
        "tenant_crm_commercial_manager",
        "tenant_crm_founder",
        "tenant_crm_ceo",
        "tenant_crm_owner",
        "tenant_crm_admin",
    ),
)
def test_ambiguous_or_platform_personas_are_not_admitted(
    forbidden: str,
) -> None:
    assert (
        forbidden
        not in catalog.ALL_CRM_SALES_BUSINESS_ROLES
    )


def test_customer_success_is_deliberately_not_admitted() -> None:
    forbidden = {
        role
        for role in catalog.ALL_CRM_SALES_BUSINESS_ROLES
        if (
            "customer_success" in role
            or "renewal" in role
            or "retention" in role
        )
    }

    assert forbidden == set()


def test_hr_legal_and_finance_roles_are_not_admitted() -> None:
    for role in catalog.ALL_CRM_SALES_BUSINESS_ROLES:
        assert "tenant_hr_" not in role
        assert "tenant_legal_" not in role
        assert "billing" not in role
        assert "finance" not in role
        assert "payroll" not in role


def test_primary_seller_family_does_not_imply_leadership() -> None:
    assert (
        EXPECTED_PRIMARY_SELLERS
        .isdisjoint(EXPECTED_LEADERSHIP)
    )


def test_operations_family_is_distinct_from_sales_leadership() -> None:
    assert (
        EXPECTED_OPERATIONS
        .isdisjoint(EXPECTED_LEADERSHIP)
    )


def test_assurance_family_is_distinct_from_mutating_personas() -> None:
    assert (
        EXPECTED_ASSURANCE
        .isdisjoint(EXPECTED_PRIMARY_SELLERS)
    )
    assert (
        EXPECTED_ASSURANCE
        .isdisjoint(EXPECTED_LEADERSHIP)
    )
    assert (
        EXPECTED_ASSURANCE
        .isdisjoint(EXPECTED_OPERATIONS)
    )


def test_functional_roles_do_not_silently_become_leadership() -> None:
    assert (
        EXPECTED_FUNCTIONAL
        .isdisjoint(EXPECTED_LEADERSHIP)
    )


def test_catalog_contains_no_permission_mapping() -> None:
    forbidden_exports = {
        "PERMISSIONS",
        "ROLE_PERMISSIONS",
        "AUTHORIZATION_ROLES",
        "ELIGIBILITY",
        "OPERATION_PERMISSIONS",
    }

    assert forbidden_exports.isdisjoint(
        set(dir(catalog))
    )


def test_catalog_contains_no_record_scope_mapping() -> None:
    forbidden_exports = {
        "ROLE_SCOPES",
        "RECORD_SCOPES",
        "DEFAULT_SCOPE",
        "TENANT_SCOPE_ROLES",
        "TEAM_SCOPE_ROLES",
        "TERRITORY_SCOPE_ROLES",
    }

    assert forbidden_exports.isdisjoint(
        set(dir(catalog))
    )


def test_catalog_contains_no_entitlement_or_seat_authority() -> None:
    forbidden_exports = {
        "ENTITLEMENTS",
        "ROLE_ENTITLEMENTS",
        "SEATS",
        "SEAT_TYPES",
        "QUOTAS",
    }

    assert forbidden_exports.isdisjoint(
        set(dir(catalog))
    )


def test_catalog_contains_no_pipeline_or_stage_authority() -> None:
    forbidden_exports = {
        "PIPELINES",
        "PIPELINE_STAGES",
        "ROLE_PIPELINE_ACCESS",
        "STAGE_TRANSITIONS",
    }

    assert forbidden_exports.isdisjoint(
        set(dir(catalog))
    )


def test_catalog_contains_no_ai_or_financial_execution_authority() -> None:
    forbidden_exports = {
        "AI_AUTHORITY",
        "AI_PERMISSIONS",
        "PAYMENT_AUTHORITY",
        "SETTLEMENT_AUTHORITY",
        "FINANCIAL_EXECUTION",
    }

    assert forbidden_exports.isdisjoint(
        set(dir(catalog))
    )


def test_catalog_exports_only_frozen_role_truth() -> None:
    assert isinstance(
        catalog.ALL_CRM_SALES_BUSINESS_ROLES,
        frozenset,
    )

    for value in (
        catalog.CRM_PRIMARY_SELLER_ROLES,
        catalog.CRM_SALES_LEADERSHIP_ROLES,
        catalog.CRM_SALES_OPERATIONS_ROLES,
        catalog.CRM_FUNCTIONAL_SALES_ROLES,
        catalog.CRM_REVENUE_ASSURANCE_ROLES,
    ):
        assert isinstance(value, frozenset)


def test_named_family_exports_match_mapping() -> None:
    assert (
        catalog.CRM_PRIMARY_SELLER_ROLES
        == EXPECTED_PRIMARY_SELLERS
    )
    assert (
        catalog.CRM_SALES_LEADERSHIP_ROLES
        == EXPECTED_LEADERSHIP
    )
    assert (
        catalog.CRM_SALES_OPERATIONS_ROLES
        == EXPECTED_OPERATIONS
    )
    assert (
        catalog.CRM_FUNCTIONAL_SALES_ROLES
        == EXPECTED_FUNCTIONAL
    )
    assert (
        catalog.CRM_REVENUE_ASSURANCE_ROLES
        == EXPECTED_ASSURANCE
    )


# ARTIFACT: test_crm_sales_business_role_catalog.py
# VERSION: v1.0.0-P0-CRM-SALES-BUSINESS-ROLE-CATALOG-CERT
# AUTHORITY BOUNDARY: business-role vocabulary only; no authorization grant
# RECORD-SCOPE BOUNDARY: role family never manufactures relationship scope
# TENANT POSTURE: canonical tenant_crm_* role identifiers only
# CUSTOMER SUCCESS: excluded pending separate research
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
