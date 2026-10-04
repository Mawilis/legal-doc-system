"""Direct certificate for the sovereign HR business-role catalog."""

from __future__ import annotations

import ast
import pathlib

from tools.eos.auth import hr_business_role_catalog as catalog


EXPECTED_ROLES = frozenset({
    "tenant_attendance_administrator",
    "tenant_benefits_administrator",
    "tenant_benefits_director",
    "tenant_benefits_manager",
    "tenant_benefits_specialist",
    "tenant_calibration_facilitator",
    "tenant_chief_people_officer",
    "tenant_chro",
    "tenant_compensation_analyst",
    "tenant_compensation_director",
    "tenant_compensation_manager",
    "tenant_compensation_specialist",
    "tenant_contingent_workforce_manager",
    "tenant_contractor_administrator",
    "tenant_country_hr_director",
    "tenant_department_manager",
    "tenant_deputy_hr_director",
    "tenant_disciplinary_case_manager",
    "tenant_disciplinary_outcome_approver",
    "tenant_employee",
    "tenant_employee_relations_director",
    "tenant_employee_relations_manager",
    "tenant_employee_relations_specialist",
    "tenant_employment_compliance_specialist",
    "tenant_executive_manager",
    "tenant_external_hr_auditor",
    "tenant_global_mobility_manager",
    "tenant_global_mobility_specialist",
    "tenant_grievance_manager",
    "tenant_head_of_people",
    "tenant_health_safety_director",
    "tenant_health_safety_manager",
    "tenant_health_safety_officer",
    "tenant_hiring_manager",
    "tenant_hr_administrator",
    "tenant_hr_analyst",
    "tenant_hr_auditor",
    "tenant_hr_business_partner",
    "tenant_hr_compliance_director",
    "tenant_hr_compliance_manager",
    "tenant_hr_compliance_officer",
    "tenant_hr_data_analyst",
    "tenant_hr_data_steward",
    "tenant_hr_director",
    "tenant_hr_generalist",
    "tenant_hr_investigator",
    "tenant_hr_manager",
    "tenant_hr_specialist",
    "tenant_hris_administrator",
    "tenant_hris_director",
    "tenant_hris_manager",
    "tenant_immigration_administrator",
    "tenant_instructor",
    "tenant_interviewer",
    "tenant_labour_relations_manager",
    "tenant_labour_relations_specialist",
    "tenant_learning_administrator",
    "tenant_learning_development_director",
    "tenant_learning_development_manager",
    "tenant_leave_administrator",
    "tenant_leave_approver",
    "tenant_leave_manager",
    "tenant_line_manager",
    "tenant_occupational_health_administrator",
    "tenant_offboarding_administrator",
    "tenant_onboarding_coordinator",
    "tenant_onboarding_manager",
    "tenant_organisation_design_administrator",
    "tenant_organisation_design_manager",
    "tenant_payroll_administrator",
    "tenant_payroll_auditor",
    "tenant_payroll_director",
    "tenant_payroll_manager",
    "tenant_payroll_processor",
    "tenant_payroll_reviewer",
    "tenant_people_privacy_officer",
    "tenant_performance_director",
    "tenant_performance_manager",
    "tenant_performance_specialist",
    "tenant_personnel_administrator",
    "tenant_position_administrator",
    "tenant_recruiter",
    "tenant_recruiting_coordinator",
    "tenant_regional_hr_director",
    "tenant_sourcer",
    "tenant_succession_planner",
    "tenant_talent_acquisition_director",
    "tenant_talent_acquisition_manager",
    "tenant_talent_management_director",
    "tenant_talent_manager",
    "tenant_talent_specialist",
    "tenant_team_lead",
    "tenant_time_administrator",
    "tenant_time_attendance_manager",
    "tenant_trainer",
    "tenant_vp_people",
    "tenant_wellbeing_coordinator",
    "tenant_wellbeing_manager",
    "tenant_workforce_analyst",
    "tenant_workforce_planning_director",
    "tenant_workforce_planning_manager",
})


def test_catalog_contains_exact_101_roles() -> None:
    assert len(EXPECTED_ROLES) == 101
    assert catalog.ALL_HR_BUSINESS_ROLES == EXPECTED_ROLES


def test_every_role_is_unique_and_tenant_scoped() -> None:
    assert len(catalog.ALL_HR_BUSINESS_ROLES) == len(
        set(catalog.ALL_HR_BUSINESS_ROLES)
    )

    assert all(
        role.startswith("tenant_")
        for role in catalog.ALL_HR_BUSINESS_ROLES
    )


def test_role_families_partition_the_catalog_exactly() -> None:
    members = set()

    for family, roles in catalog.HR_ROLE_FAMILIES.items():
        assert family
        assert roles
        assert members.isdisjoint(roles)
        members.update(roles)

    assert members == EXPECTED_ROLES


def test_employee_relations_formal_write_candidates_are_exact() -> None:
    assert (
        catalog.EMPLOYEE_RELATION_FORMAL_WRITE_ROLE_CANDIDATES
        == frozenset({
            "tenant_hr_director",
            "tenant_hr_manager",
            "tenant_employee_relations_director",
            "tenant_employee_relations_manager",
            "tenant_employee_relations_specialist",
        })
    )


def test_report_only_candidates_do_not_overlap_formal_write() -> None:
    assert catalog.EMPLOYEE_RELATION_REPORT_ONLY_ROLE_CANDIDATES == frozenset({
        "tenant_hr_business_partner",
        "tenant_hr_generalist",
        "tenant_line_manager",
        "tenant_department_manager",
    })

    assert (
        catalog.EMPLOYEE_RELATION_FORMAL_WRITE_ROLE_CANDIDATES
        .isdisjoint(
            catalog.EMPLOYEE_RELATION_REPORT_ONLY_ROLE_CANDIDATES
        )
    )


def test_payroll_roles_do_not_imply_financial_execution() -> None:
    assert catalog.PAYROLL_ROLE_CANDIDATES

    assert all(
        "payroll" in role
        for role in catalog.PAYROLL_ROLE_CANDIDATES
    )

    assert catalog.PAYROLL_FINANCIAL_EXECUTION_AUTHORITY is False


def test_catalog_exposes_no_permission_or_authorization_functions() -> None:
    source_path = pathlib.Path(catalog.__file__ or "")

    tree = ast.parse(
        source_path.read_text(
            encoding="utf-8",
        )
    )

    functions = {
        node.name
        for node in ast.walk(tree)
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    }

    forbidden = {
        "authorize",
        "grant",
        "revoke",
        "assign",
        "permission_metadata",
        "authorize_tenant_operation",
    }

    assert functions.isdisjoint(
        forbidden
    )


def test_catalog_contains_no_permission_literals() -> None:
    source = pathlib.Path(
        catalog.__file__ or ""
    ).read_text(
        encoding="utf-8",
    )

    forbidden_fragments = (
        "hr:employee_relation:write",
        "permission_id",
        "ROLE_PERMISSIONS_MAP",
        "_BINDINGS",
        "ELIGIBLE",
    )

    assert all(
        fragment not in source
        for fragment in forbidden_fragments
    )
