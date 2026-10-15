"""TITLE: CX27-D principal operating-role occupancy unit certificate.

VERSION: v1.0.0-CX27-D-PRINCIPAL-OCCUPANCY-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certifies immutable effective-dated occupancy and authority exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_principal_operating_role_binding.py
COLLABORATION / OWNERSHIP: CX27-D pure-domain certificate only.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes the direct principal-occupancy unit certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque principal identifiers; no PII or credentials.
TENANT BOUNDARY: Exact synthetic tenant identities; cross-tenant authority is absent.
AUTHORITY BOUNDARY: Occupancy metadata only; no authentication, IAM, access, workforce, matter, workflow, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes or settles.
"""

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_principal_operating_role_binding import (
    LegalPrincipalOperatingRoleBinding,
    LegalPrincipalOperatingRoleBindingError,
)

NOW = datetime(2026, 10, 13, 12, 0, 0, 123456, tzinfo=timezone.utc)
FP = "a" * 128


def binding(
    *,
    tenant_id: str = "tenant-a",
    principal_operating_role_binding_id: str = "principal-role-binding-1",
    binding_revision: int = 1,
    principal_id: str = "principal-1",
    operating_role_id: str = "role-custom-1",
    operating_role_revision: int = 1,
    effective_from: datetime = NOW,
    effective_until: datetime | None = None,
    source_reference: str = "tenant-admin:role-binding-1",
    source_evidence_fingerprint: str = FP,
    supersedes_fingerprint: str | None = None,
) -> LegalPrincipalOperatingRoleBinding:
    return LegalPrincipalOperatingRoleBinding(
        tenant_id=tenant_id,
        principal_operating_role_binding_id=principal_operating_role_binding_id,
        binding_revision=binding_revision,
        principal_id=principal_id,
        operating_role_id=operating_role_id,
        operating_role_revision=operating_role_revision,
        effective_from=effective_from,
        effective_until=effective_until,
        source_reference=source_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
        supersedes_fingerprint=supersedes_fingerprint,
    )


def test_open_ended_and_closed_binding_round_trip() -> None:
    open_value = binding()
    assert open_value.effective_until is None
    assert LegalPrincipalOperatingRoleBinding.from_dict(
        open_value.to_dict()
    ) == open_value

    closed = binding(effective_until=NOW + timedelta(days=30))
    assert closed.effective_until == NOW + timedelta(days=30)


def test_invalid_window_rejected() -> None:
    with pytest.raises(LegalPrincipalOperatingRoleBindingError):
        binding(effective_until=NOW)


def test_binding_lineage() -> None:
    with pytest.raises(LegalPrincipalOperatingRoleBindingError):
        binding(supersedes_fingerprint=FP)
    with pytest.raises(LegalPrincipalOperatingRoleBindingError):
        binding(binding_revision=2)
    assert binding(
        binding_revision=2,
        supersedes_fingerprint=FP,
    ).supersedes_fingerprint == FP


def test_pseudo_tenant_rejected() -> None:
    with pytest.raises(LegalPrincipalOperatingRoleBindingError):
        binding(tenant_id="global")


def test_occupancy_is_not_authority_and_is_immutable() -> None:
    forbidden = {
        "permission", "authorization_role", "business_role", "job_title",
        "workforce_relationship_id", "matter_role", "case_matter_id",
        "assignee_principal_id", "supervisor_principal_id", "entitlement_id",
    }
    assert forbidden.isdisjoint(
        LegalPrincipalOperatingRoleBinding.__dataclass_fields__
    )
    value = binding()
    with pytest.raises(FrozenInstanceError):
        setattr(cast(Any, value), "principal_id", "mutated")


# ARTIFACT: test_legal_principal_operating_role_binding.py
# VERSION: v1.0.0-CX27-D-PRINCIPAL-OCCUPANCY-UNIT-CERT
# AUTHORITY BOUNDARY: pure-domain effective-dated occupancy certificate only
# TENANT POSTURE: exact synthetic tenant isolation semantics
# FAIL-CLOSED POSTURE: malformed identity, window, tenant, and lineage reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
