"""
TITLE: WILSY OS Shared Record Scope Authority Domain Direct Certificate
VERSION: v1.0.0-P0-RECORD-SCOPE-AUTHORITY-DOMAIN-CERT
AUTHORITY:
    Test-first contract for immutable, source-bound record-scope evidence.
EPITOME:
    Freezes the shared relationship-scope vocabulary used by CRM, HR,
    Legal Operations and future governed WILSY OS record domains without
    conflating relationship breadth with authorization or data sensitivity.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_record_scope_authority_domain.py

RESEARCH BASIS:
    - Apollo: ownership, assignment, import and record-operation controls.
    - Salesforce: ownership, hierarchy, teams, territories and sharing.
    - HubSpot: own/team/all record visibility.
    - WILSY Legal: explicit principal-to-record visibility evidence.
    - WILSY HR: restricted sensitivity remains independent of record scope.
    - WILSY tenant authorization: business-role eligibility is only one
      authorization conjunct and never an authorization grant.

SECURITY DOCTRINE:
    Relationship scope never authenticates a principal, proves membership,
    grants a permission, proves tenant entitlement, bypasses sensitivity,
    establishes an HR restricted-case grant or authorizes execution.

TENANT BOUNDARY:
    Principal tenant and record tenant must be identical explicit non-pseudo
    tenants before record-scope evidence may exist.

SENSITIVITY BOUNDARY:
    RESTRICTED is deliberately NOT a record-scope value. Existing HR
    EMPLOYEE_RELATIONS_RESTRICTED, PERFORMANCE_RESTRICTED and
    SEPARATION_RESTRICTED classifications remain separate authorization
    conjuncts.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.

AI BOUNDARY:
    No score, inference or AI recommendation may create record-scope evidence.

CHANGELOG:
    2026-10-06 v1.0.0 freezes the researched shared record-scope contract.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.auth.record_scope_authority import (
    RECORD_SCOPE_AUTHORITY_SCHEMA,
    RECORD_SCOPE_AUTHORITY_VERSION,
    RecordAccessBasis,
    RecordScope,
    RecordScopeEvidence,
    RecordScopeEvidenceError,
)


EXPECTED_VERSION = "v1.0.0-RECORD-SCOPE-AUTHORITY"
EXPECTED_SCHEMA = "WILSY-RECORD-SCOPE-AUTHORITY/V1"

TENANT = "WILSYTENANT-CRM-SCOPE-001"
PRINCIPAL = "principal-sales-001"
RESOURCE_TYPE = "crm.lead"
RESOURCE_ID = "WILSYCRM-LEAD-001"

SOURCE_REFERENCE = (
    "crm-lead:WILSYCRM-LEAD-001:owner:principal-sales-001"
)
SOURCE_FINGERPRINT = "a" * 128
ISSUED_AT = datetime(
    2026,
    10,
    6,
    21,
    0,
    tzinfo=timezone.utc,
)


def _evidence(**changes: Any) -> RecordScopeEvidence:
    values: dict[str, Any] = {
        "principal_tenant_id": TENANT,
        "record_tenant_id": TENANT,
        "principal_id": PRINCIPAL,
        "resource_type": RESOURCE_TYPE,
        "resource_id": RESOURCE_ID,
        "scope": RecordScope.OWN,
        "basis": RecordAccessBasis.RECORD_OWNER,
        "source_reference": SOURCE_REFERENCE,
        "source_revision": 7,
        "source_fingerprint": SOURCE_FINGERPRINT,
        "issued_at": ISSUED_AT,
    }

    values.update(changes)

    return RecordScopeEvidence.issue(**values)


def test_version_and_schema_are_exact() -> None:
    assert RECORD_SCOPE_AUTHORITY_VERSION == EXPECTED_VERSION
    assert RECORD_SCOPE_AUTHORITY_SCHEMA == EXPECTED_SCHEMA


def test_record_scope_vocabulary_is_closed_and_exact() -> None:
    assert tuple(scope.value for scope in RecordScope) == (
        "SELF",
        "OWN",
        "ASSIGNED",
        "SHARED",
        "TEAM",
        "REPORTING_LINE",
        "DEPARTMENT",
        "TERRITORY",
        "BUSINESS_UNIT",
        "TENANT",
    )


def test_restricted_is_not_a_record_scope() -> None:
    assert "RESTRICTED" not in {
        scope.value for scope in RecordScope
    }


def test_access_basis_vocabulary_is_closed_and_exact() -> None:
    assert tuple(basis.value for basis in RecordAccessBasis) == (
        "SUBJECT_SELF",
        "RECORD_OWNER",
        "EXPLICIT_ASSIGNMENT",
        "EXPLICIT_SHARE",
        "TEAM_MEMBERSHIP",
        "REPORTING_HIERARCHY",
        "DEPARTMENT_MEMBERSHIP",
        "TERRITORY_ASSIGNMENT",
        "BUSINESS_UNIT_MEMBERSHIP",
        "TENANT_ELEVATED_AUTHORITY",
    )


@pytest.mark.parametrize(
    ("basis", "scope"),
    (
        (
            RecordAccessBasis.SUBJECT_SELF,
            RecordScope.SELF,
        ),
        (
            RecordAccessBasis.RECORD_OWNER,
            RecordScope.OWN,
        ),
        (
            RecordAccessBasis.EXPLICIT_ASSIGNMENT,
            RecordScope.ASSIGNED,
        ),
        (
            RecordAccessBasis.EXPLICIT_SHARE,
            RecordScope.SHARED,
        ),
        (
            RecordAccessBasis.TEAM_MEMBERSHIP,
            RecordScope.TEAM,
        ),
        (
            RecordAccessBasis.REPORTING_HIERARCHY,
            RecordScope.REPORTING_LINE,
        ),
        (
            RecordAccessBasis.DEPARTMENT_MEMBERSHIP,
            RecordScope.DEPARTMENT,
        ),
        (
            RecordAccessBasis.TERRITORY_ASSIGNMENT,
            RecordScope.TERRITORY,
        ),
        (
            RecordAccessBasis.BUSINESS_UNIT_MEMBERSHIP,
            RecordScope.BUSINESS_UNIT,
        ),
        (
            RecordAccessBasis.TENANT_ELEVATED_AUTHORITY,
            RecordScope.TENANT,
        ),
    ),
)
def test_access_basis_maps_to_exact_scope(
    basis: RecordAccessBasis,
    scope: RecordScope,
) -> None:
    value = _evidence(
        basis=basis,
        scope=scope,
        source_reference=(
            f"authority:{basis.value.lower()}:source"
        ),
    )

    assert value.basis is basis
    assert value.scope is scope


@pytest.mark.parametrize(
    ("basis", "wrong_scope"),
    (
        (
            RecordAccessBasis.RECORD_OWNER,
            RecordScope.TENANT,
        ),
        (
            RecordAccessBasis.EXPLICIT_ASSIGNMENT,
            RecordScope.TEAM,
        ),
        (
            RecordAccessBasis.TEAM_MEMBERSHIP,
            RecordScope.OWN,
        ),
        (
            RecordAccessBasis.TENANT_ELEVATED_AUTHORITY,
            RecordScope.OWN,
        ),
    ),
)
def test_basis_scope_mismatch_fails_closed(
    basis: RecordAccessBasis,
    wrong_scope: RecordScope,
) -> None:
    with pytest.raises(
        RecordScopeEvidenceError,
        match="RECORD_SCOPE_BASIS_SCOPE_MISMATCH",
    ):
        _evidence(
            basis=basis,
            scope=wrong_scope,
        )


def test_evidence_is_immutable_and_fingerprinted() -> None:
    value = _evidence()

    assert value.tenant_id == TENANT
    assert value.principal_id == PRINCIPAL
    assert value.resource_type == RESOURCE_TYPE
    assert value.resource_id == RESOURCE_ID
    assert value.scope is RecordScope.OWN
    assert value.basis is RecordAccessBasis.RECORD_OWNER
    assert value.source_revision == 7
    assert value.source_fingerprint == SOURCE_FINGERPRINT
    assert value.issued_at == ISSUED_AT

    assert len(value.fingerprint) == 128
    assert set(value.fingerprint) <= set(
        "0123456789abcdef"
    )

    with pytest.raises(FrozenInstanceError):
        value.scope = RecordScope.TENANT  # type: ignore[misc]


@pytest.mark.parametrize(
    "tenant",
    (
        "",
        " ",
        " tenant-a",
        "tenant-a ",
        "default",
        "GLOBAL",
        "root",
        "*",
        "MASTER",
        "GLOBAL_ROOT",
        "SOVEREIGN_ROOT",
        "wilsy-sovereign-root",
    ),
)
def test_principal_tenant_fails_closed(
    tenant: str,
) -> None:
    with pytest.raises(RecordScopeEvidenceError):
        _evidence(
            principal_tenant_id=tenant,
            record_tenant_id=tenant,
        )


def test_cross_tenant_scope_is_impossible() -> None:
    with pytest.raises(
        RecordScopeEvidenceError,
        match="RECORD_SCOPE_CROSS_TENANT_FORBIDDEN",
    ):
        _evidence(
            principal_tenant_id="WILSYTENANT-A",
            record_tenant_id="WILSYTENANT-B",
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("principal_id", ""),
        ("principal_id", " principal-1"),
        ("resource_type", ""),
        ("resource_type", "crm.lead "),
        ("resource_id", ""),
        ("resource_id", " lead-1"),
        ("source_reference", ""),
        ("source_reference", " source-1"),
    ),
)
def test_identifiers_and_reference_are_exact(
    field_name: str,
    value: str,
) -> None:
    with pytest.raises(RecordScopeEvidenceError):
        _evidence(**{field_name: value})


@pytest.mark.parametrize(
    "revision",
    (
        True,
        False,
        -1,
        1.5,
        "1",
        None,
    ),
)
def test_source_revision_requires_nonnegative_integer(
    revision: object,
) -> None:
    with pytest.raises(RecordScopeEvidenceError):
        _evidence(
            source_revision=revision,
        )


@pytest.mark.parametrize(
    "fingerprint",
    (
        "",
        "a" * 127,
        "a" * 129,
        "A" * 128,
        "g" * 128,
    ),
)
def test_source_fingerprint_requires_lowercase_sha3_512_shape(
    fingerprint: str,
) -> None:
    with pytest.raises(RecordScopeEvidenceError):
        _evidence(
            source_fingerprint=fingerprint,
        )


@pytest.mark.parametrize(
    "issued_at",
    (
        datetime(2026, 10, 6, 21, 0),
        "not-a-time",
        None,
    ),
)
def test_issued_at_requires_aware_datetime(
    issued_at: object,
) -> None:
    with pytest.raises(RecordScopeEvidenceError):
        _evidence(
            issued_at=issued_at,
        )


def test_evidence_normalizes_aware_datetime_to_utc() -> None:
    value = _evidence()

    assert value.issued_at.tzinfo is timezone.utc


def test_scope_evidence_contains_no_permission_or_role_grant() -> None:
    names = {
        field.name
        for field in fields(RecordScopeEvidence)
    }

    forbidden = {
        "permission",
        "permissions",
        "authorization_role",
        "business_role",
        "role",
        "roles",
        "membership",
        "entitlement",
        "quota",
    }

    assert forbidden.isdisjoint(names)


def test_scope_evidence_contains_no_sensitivity_authority() -> None:
    names = {
        field.name
        for field in fields(RecordScopeEvidence)
    }

    forbidden = {
        "restricted",
        "sensitivity",
        "confidentiality",
        "legal_hold",
        "investigation_access",
        "employee_relations_access",
    }

    assert forbidden.isdisjoint(names)


def test_scope_evidence_contains_no_ai_or_financial_authority() -> None:
    names = {
        field.name
        for field in fields(RecordScopeEvidence)
    }

    forbidden = {
        "ai_score",
        "ai_recommendation",
        "intent_score",
        "payment_authority",
        "settlement_authority",
        "financial_execution",
        "invoice_id",
        "payment_id",
    }

    assert forbidden.isdisjoint(names)


def test_scope_evidence_contains_no_pipeline_or_domain_state() -> None:
    names = {
        field.name
        for field in fields(RecordScopeEvidence)
    }

    forbidden = {
        "lead_status",
        "deal_stage",
        "pipeline_stage",
        "employee_status",
        "disciplinary_status",
        "case_status",
    }

    assert forbidden.isdisjoint(names)


def test_scope_domain_exposes_no_authorization_execution_method() -> None:
    forbidden = {
        "authorize",
        "is_authorized",
        "grant_permission",
        "grant_role",
        "execute",
        "persist",
        "save",
        "insert",
        "update",
        "delete",
    }

    assert forbidden.isdisjoint(
        set(dir(RecordScopeEvidence))
    )


def test_round_trip_preserves_exact_scope_evidence() -> None:
    original = _evidence()

    hydrated = RecordScopeEvidence.from_dict(
        original.to_dict()
    )

    assert hydrated == original
    assert hydrated.fingerprint == original.fingerprint


@pytest.mark.parametrize(
    "mutation",
    (
        "missing",
        "extra",
        "fingerprint",
        "scope",
        "basis",
        "tenant",
    ),
)
def test_hydration_rejects_schema_or_evidence_corruption(
    mutation: str,
) -> None:
    payload = _evidence().to_dict()

    if mutation == "missing":
        payload.pop("resource_id")

    elif mutation == "extra":
        payload["unexpected_authority"] = "DENY"

    elif mutation == "fingerprint":
        payload["fingerprint"] = "b" * 128

    elif mutation == "scope":
        payload["scope"] = "TENANT"

    elif mutation == "basis":
        payload["basis"] = "TEAM_MEMBERSHIP"

    elif mutation == "tenant":
        payload["tenant_id"] = "WILSYTENANT-OTHER"

    with pytest.raises(RecordScopeEvidenceError):
        RecordScopeEvidence.from_dict(payload)


def test_fingerprint_changes_when_authority_coordinates_change() -> None:
    baseline = _evidence()

    changed_principal = _evidence(
        principal_id="principal-sales-002",
    )

    changed_resource = _evidence(
        resource_id="WILSYCRM-LEAD-002",
    )

    changed_scope = _evidence(
        scope=RecordScope.ASSIGNED,
        basis=RecordAccessBasis.EXPLICIT_ASSIGNMENT,
        source_reference="assignment:WILSYCRM-LEAD-001:principal-sales-001",
    )

    changed_source_revision = _evidence(
        source_revision=8,
    )

    assert baseline.fingerprint != changed_principal.fingerprint
    assert baseline.fingerprint != changed_resource.fingerprint
    assert baseline.fingerprint != changed_scope.fingerprint
    assert (
        baseline.fingerprint
        != changed_source_revision.fingerprint
    )


def test_tenant_scope_requires_elevated_authority_basis() -> None:
    value = _evidence(
        scope=RecordScope.TENANT,
        basis=RecordAccessBasis.TENANT_ELEVATED_AUTHORITY,
        source_reference=(
            "tenant-authorization:"
            "crm_lead_read:principal-sales-executive"
        ),
    )

    assert value.scope is RecordScope.TENANT
    assert (
        value.basis
        is RecordAccessBasis.TENANT_ELEVATED_AUTHORITY
    )


def test_self_scope_is_distinct_from_record_ownership() -> None:
    self_scope = _evidence(
        scope=RecordScope.SELF,
        basis=RecordAccessBasis.SUBJECT_SELF,
        source_reference=(
            "employee-subject:employee-001:"
            "principal-sales-001"
        ),
    )

    owner_scope = _evidence()

    assert self_scope.scope is RecordScope.SELF
    assert owner_scope.scope is RecordScope.OWN
    assert self_scope.fingerprint != owner_scope.fingerprint


# ARTIFACT: test_record_scope_authority_domain.py
# VERSION: v1.0.0-P0-RECORD-SCOPE-AUTHORITY-DOMAIN-CERT
# AUTHORITY BOUNDARY: immutable relationship-scope evidence contract only
# TENANT POSTURE: principal and resource tenants must be exact and identical
# SENSITIVITY POSTURE: RESTRICTED is deliberately outside record-scope vocabulary
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
