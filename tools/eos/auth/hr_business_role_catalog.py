"""Sovereign HR business-role vocabulary.

This module defines immutable HR/People business-role identifiers
only. It is deliberately NON-AUTHORIZING.

A role appearing here grants no permission, creates no membership,
creates no role assignment, and authorizes no operation.

Canonical authorization remains owned by:
  - tools.eos.auth.roles
  - tools.eos.auth.permission_namespace
  - tools.eos.auth.tenant_authority_policy
  - tools.eos.auth.tenant_authorization

Job title, department, manager relationship and employee metadata
remain business data and do not confer IAM authority.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Final


VERSION: Final[str] = (
    "v1.0.0-P0-C12E4B2-HR-BUSINESS-ROLE-CATALOG"
)


HR_ROLE_FAMILIES: Final = MappingProxyType({

    "EXECUTIVE_PEOPLE_LEADERSHIP": frozenset({
        "tenant_chief_people_officer",
        "tenant_chro",
        "tenant_vp_people",
        "tenant_head_of_people",
        "tenant_hr_director",
        "tenant_deputy_hr_director",
        "tenant_regional_hr_director",
        "tenant_country_hr_director",
    }),

    "CORE_HR": frozenset({
        "tenant_hr_manager",
        "tenant_hr_business_partner",
        "tenant_hr_generalist",
        "tenant_hr_specialist",
        "tenant_hr_administrator",
        "tenant_personnel_administrator",
    }),

    "EMPLOYEE_LABOUR_RELATIONS": frozenset({
        "tenant_employee_relations_director",
        "tenant_employee_relations_manager",
        "tenant_employee_relations_specialist",
        "tenant_labour_relations_manager",
        "tenant_labour_relations_specialist",
        "tenant_hr_investigator",
        "tenant_disciplinary_case_manager",
        "tenant_disciplinary_outcome_approver",
        "tenant_grievance_manager",
    }),

    "TALENT_ACQUISITION": frozenset({
        "tenant_talent_acquisition_director",
        "tenant_talent_acquisition_manager",
        "tenant_recruiter",
        "tenant_sourcer",
        "tenant_recruiting_coordinator",
        "tenant_hiring_manager",
        "tenant_interviewer",
    }),

    "ONBOARDING_OFFBOARDING_MOBILITY": frozenset({
        "tenant_onboarding_manager",
        "tenant_onboarding_coordinator",
        "tenant_offboarding_administrator",
        "tenant_global_mobility_manager",
        "tenant_global_mobility_specialist",
        "tenant_immigration_administrator",
    }),

    "PAYROLL": frozenset({
        "tenant_payroll_director",
        "tenant_payroll_manager",
        "tenant_payroll_administrator",
        "tenant_payroll_processor",
        "tenant_payroll_reviewer",
        "tenant_payroll_auditor",
    }),

    "COMPENSATION": frozenset({
        "tenant_compensation_director",
        "tenant_compensation_manager",
        "tenant_compensation_specialist",
        "tenant_compensation_analyst",
    }),

    "BENEFITS": frozenset({
        "tenant_benefits_director",
        "tenant_benefits_manager",
        "tenant_benefits_administrator",
        "tenant_benefits_specialist",
    }),

    "TIME_ATTENDANCE_LEAVE": frozenset({
        "tenant_time_attendance_manager",
        "tenant_time_administrator",
        "tenant_attendance_administrator",
        "tenant_leave_manager",
        "tenant_leave_administrator",
        "tenant_leave_approver",
    }),

    "PERFORMANCE_TALENT_SUCCESSION": frozenset({
        "tenant_performance_director",
        "tenant_performance_manager",
        "tenant_performance_specialist",
        "tenant_talent_management_director",
        "tenant_talent_manager",
        "tenant_talent_specialist",
        "tenant_succession_planner",
        "tenant_calibration_facilitator",
    }),

    "LEARNING_DEVELOPMENT": frozenset({
        "tenant_learning_development_director",
        "tenant_learning_development_manager",
        "tenant_learning_administrator",
        "tenant_trainer",
        "tenant_instructor",
    }),

    "WORKFORCE_ORGANISATION": frozenset({
        "tenant_workforce_planning_director",
        "tenant_workforce_planning_manager",
        "tenant_workforce_analyst",
        "tenant_position_administrator",
        "tenant_organisation_design_manager",
        "tenant_organisation_design_administrator",
    }),

    "HRIS_PEOPLE_DATA": frozenset({
        "tenant_hris_director",
        "tenant_hris_manager",
        "tenant_hris_administrator",
        "tenant_hr_data_steward",
        "tenant_hr_data_analyst",
    }),

    "COMPLIANCE_PRIVACY_AUDIT": frozenset({
        "tenant_hr_compliance_director",
        "tenant_hr_compliance_manager",
        "tenant_hr_compliance_officer",
        "tenant_hr_auditor",
        "tenant_external_hr_auditor",
        "tenant_people_privacy_officer",
        "tenant_employment_compliance_specialist",
    }),

    "HEALTH_SAFETY_WELLBEING": frozenset({
        "tenant_health_safety_director",
        "tenant_health_safety_manager",
        "tenant_health_safety_officer",
        "tenant_occupational_health_administrator",
        "tenant_wellbeing_manager",
        "tenant_wellbeing_coordinator",
    }),

    "CONTINGENT_WORKFORCE": frozenset({
        "tenant_contingent_workforce_manager",
        "tenant_contractor_administrator",
    }),

    "MANAGEMENT_HIERARCHY": frozenset({
        "tenant_executive_manager",
        "tenant_department_manager",
        "tenant_line_manager",
        "tenant_team_lead",
    }),

    "EMPLOYEE_SELF_SERVICE": frozenset({
        "tenant_employee",
    }),

    "GENERAL_HR_ASSURANCE": frozenset({
        "tenant_hr_analyst",
    }),
})


ALL_HR_BUSINESS_ROLES: Final[frozenset[str]] = frozenset(
    role
    for roles in HR_ROLE_FAMILIES.values()
    for role in roles
)


EMPLOYEE_RELATION_FORMAL_WRITE_ROLE_CANDIDATES: Final[
    frozenset[str]
] = frozenset({
    "tenant_hr_director",
    "tenant_hr_manager",
    "tenant_employee_relations_director",
    "tenant_employee_relations_manager",
    "tenant_employee_relations_specialist",
})


EMPLOYEE_RELATION_REPORT_ONLY_ROLE_CANDIDATES: Final[
    frozenset[str]
] = frozenset({
    "tenant_hr_business_partner",
    "tenant_hr_generalist",
    "tenant_line_manager",
    "tenant_department_manager",
})


PAYROLL_ROLE_CANDIDATES: Final[frozenset[str]] = (
    HR_ROLE_FAMILIES["PAYROLL"]
)


PAYROLL_FINANCIAL_EXECUTION_AUTHORITY: Final[bool] = False


__all__ = [
    "VERSION",
    "HR_ROLE_FAMILIES",
    "ALL_HR_BUSINESS_ROLES",
    "EMPLOYEE_RELATION_FORMAL_WRITE_ROLE_CANDIDATES",
    "EMPLOYEE_RELATION_REPORT_ONLY_ROLE_CANDIDATES",
    "PAYROLL_ROLE_CANDIDATES",
    "PAYROLL_FINANCIAL_EXECUTION_AUTHORITY",
]
