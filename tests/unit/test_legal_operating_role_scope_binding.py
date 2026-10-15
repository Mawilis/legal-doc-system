"""TITLE: CX27-C Legal operating-role scope binding unit certificate.

VERSION: v1.0.0-CX27-C-SCOPE-BINDING-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certifies immutable descriptive scope association and authority exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operating_role_scope_binding.py
COLLABORATION / OWNERSHIP: CX27-C pure-domain certificate only.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes the direct scope-binding unit certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no PII or credentials.
TENANT BOUNDARY: Exact synthetic tenant identities; cross-tenant authority is absent.
AUTHORITY BOUNDARY: Scope metadata only; no IAM, record, client, matter, workflow, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes or settles.
"""

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_operating_role_scope_binding import (
    LegalOperatingRoleScopeBinding,
    LegalOperatingRoleScopeBindingError,
)

NOW = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)


def scope(
    *,
    tenant_id: str = "tenant-a",
    scope_binding_id: str = "scope-binding-1",
    operating_role_id: str = "role-custom-1",
    operating_role_revision: int = 1,
    scope_binding_revision: int = 1,
    office_references: tuple[str, ...] = ("office:jhb",),
    practice_references: tuple[str, ...] = (),
    business_unit_references: tuple[str, ...] = (),
    jurisdiction_references: tuple[str, ...] = (),
    effective_from: datetime = NOW,
    supersedes_fingerprint: str | None = None,
) -> LegalOperatingRoleScopeBinding:
    return LegalOperatingRoleScopeBinding(
        tenant_id=tenant_id,
        scope_binding_id=scope_binding_id,
        operating_role_id=operating_role_id,
        operating_role_revision=operating_role_revision,
        scope_binding_revision=scope_binding_revision,
        office_references=office_references,
        practice_references=practice_references,
        business_unit_references=business_unit_references,
        jurisdiction_references=jurisdiction_references,
        effective_from=effective_from,
        supersedes_fingerprint=supersedes_fingerprint,
    )


def test_each_enterprise_scope_dimension() -> None:
    assert scope().office_references
    assert scope(
        office_references=(),
        practice_references=("practice:disputes",),
    ).practice_references
    assert scope(
        office_references=(),
        business_unit_references=("business-unit:africa",),
    ).business_unit_references
    assert scope(
        office_references=(),
        jurisdiction_references=("jurisdiction:ZA",),
    ).jurisdiction_references


def test_multi_scope_and_round_trip() -> None:
    value = scope(
        practice_references=("practice:disputes",),
        business_unit_references=("business-unit:africa",),
        jurisdiction_references=("jurisdiction:ZA",),
    )
    assert LegalOperatingRoleScopeBinding.from_dict(value.to_dict()) == value


def test_empty_scope_does_not_silently_mean_tenant_wide() -> None:
    with pytest.raises(LegalOperatingRoleScopeBindingError):
        scope(
            office_references=(),
            practice_references=(),
            business_unit_references=(),
            jurisdiction_references=(),
        )


def test_duplicate_reference_rejected() -> None:
    with pytest.raises(LegalOperatingRoleScopeBindingError):
        scope(office_references=("office:jhb", "office:jhb"))


def test_scope_is_not_record_authority_and_is_immutable() -> None:
    forbidden = {
        "permission", "authorization_role", "business_role", "record_access",
        "principal_id", "matter_role", "assignee_principal_id",
        "supervisor_principal_id",
    }
    assert forbidden.isdisjoint(
        LegalOperatingRoleScopeBinding.__dataclass_fields__
    )
    value = scope()
    with pytest.raises(FrozenInstanceError):
        setattr(cast(Any, value), "scope_binding_id", "mutated")


def test_scope_binding_revision_is_independent_of_role_revision() -> None:
    first = scope(
        operating_role_revision=9,
        scope_binding_revision=1,
    )
    second = scope(
        operating_role_revision=9,
        scope_binding_revision=2,
        supersedes_fingerprint=first.fingerprint,
        office_references=("office:cpt",),
    )
    assert first.operating_role_revision == second.operating_role_revision == 9
    assert first.scope_binding_revision == 1
    assert second.scope_binding_revision == 2


    assert second.supersedes_fingerprint == first.fingerprint


def test_scope_binding_revision_lineage_rules() -> None:
    with pytest.raises(LegalOperatingRoleScopeBindingError):
        scope(scope_binding_revision=2)

    first = scope()
    second = scope(
        scope_binding_revision=2,
        supersedes_fingerprint=first.fingerprint,
        jurisdiction_references=("jurisdiction:ZA",),
    )
    assert second.scope_binding_revision == 2


# ARTIFACT: test_legal_operating_role_scope_binding.py
# VERSION: v1.0.0-CX27-C-SCOPE-BINDING-UNIT-CERT
# AUTHORITY BOUNDARY: pure-domain descriptive scope association certificate only
# TENANT POSTURE: exact synthetic tenant isolation semantics
# FAIL-CLOSED POSTURE: malformed, duplicate, empty, and invalid lineage reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
