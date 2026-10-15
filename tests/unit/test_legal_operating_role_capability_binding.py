"""TITLE: CX27-B Legal operating-role capability binding unit certificate.

VERSION: v1.0.0-CX27-B-CAPABILITY-BINDING-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certifies immutable capability association and authority exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operating_role_capability_binding.py
COLLABORATION / OWNERSHIP: CX27-B pure-domain certificate only.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes the direct capability-binding unit certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no PII or credentials.
TENANT BOUNDARY: Exact synthetic tenant identities; cross-tenant authority is absent.
AUTHORITY BOUNDARY: Association metadata only; no IAM, matter, workflow, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes or settles.
"""

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_operating_role_capability_binding import (
    LegalOperatingRoleCapabilityBinding,
    LegalOperatingRoleCapabilityBindingError,
)

NOW = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)
FP = "a" * 128


def binding(
    *,
    tenant_id: str = "tenant-a",
    capability_binding_id: str = "cap-binding-1",
    operating_role_id: str = "role-custom-1",
    operating_role_revision: int = 1,
    capability_binding_revision: int = 1,
    capability_ids: tuple[str, ...] = ("PRACTICE_DISPUTES",),
    effective_from: datetime = NOW,
    supersedes_fingerprint: str | None = None,
) -> LegalOperatingRoleCapabilityBinding:
    return LegalOperatingRoleCapabilityBinding(
        tenant_id=tenant_id,
        capability_binding_id=capability_binding_id,
        operating_role_id=operating_role_id,
        operating_role_revision=operating_role_revision,
        capability_binding_revision=capability_binding_revision,
        capability_ids=capability_ids,
        effective_from=effective_from,
        supersedes_fingerprint=supersedes_fingerprint,
    )


def test_known_capability_and_round_trip() -> None:
    value = binding()
    assert LegalOperatingRoleCapabilityBinding.from_dict(value.to_dict()) == value


def test_multiple_capabilities_are_canonical() -> None:
    value = binding(
        capability_ids=("PRACTICE_DISPUTES", "PRACTICE_CORPORATE")
    )
    assert value.capability_ids == (
        "PRACTICE_CORPORATE",
        "PRACTICE_DISPUTES",
    )


def test_unknown_and_duplicate_capabilities_reject() -> None:
    with pytest.raises(LegalOperatingRoleCapabilityBindingError):
        binding(capability_ids=("NOT_A_REAL_CAPABILITY",))
    with pytest.raises(LegalOperatingRoleCapabilityBindingError):
        binding(capability_ids=("PRACTICE_DISPUTES", "PRACTICE_DISPUTES"))


def test_lineage_rules() -> None:
    with pytest.raises(LegalOperatingRoleCapabilityBindingError):
        binding(supersedes_fingerprint=FP)
    with pytest.raises(LegalOperatingRoleCapabilityBindingError):
        binding(capability_binding_revision=2)
    assert binding(
        capability_binding_revision=2,
        supersedes_fingerprint=FP,
    ).supersedes_fingerprint == FP


def test_no_permission_grant_and_immutable() -> None:
    forbidden = {
        "permission", "authorization_role", "business_role", "principal_id",
        "matter_role", "assignee_principal_id", "supervisor_principal_id",
        "entitlement_id",
    }
    assert forbidden.isdisjoint(
        LegalOperatingRoleCapabilityBinding.__dataclass_fields__
    )
    value = binding()
    with pytest.raises(FrozenInstanceError):
        setattr(cast(Any, value), "capability_binding_id", "mutated")


def test_capability_binding_revision_is_independent_of_role_revision() -> None:
    first = binding(
        operating_role_revision=7,
        capability_binding_revision=1,
    )
    second = binding(
        operating_role_revision=7,
        capability_binding_revision=2,
        supersedes_fingerprint=first.fingerprint,
        capability_ids=("PRACTICE_CORPORATE",),
    )
    assert first.operating_role_revision == second.operating_role_revision == 7
    assert first.capability_binding_revision == 1
    assert second.capability_binding_revision == 2
    assert second.supersedes_fingerprint == first.fingerprint
# ARTIFACT: test_legal_operating_role_capability_binding.py
# VERSION: v1.0.0-CX27-B-CAPABILITY-BINDING-UNIT-CERT
# AUTHORITY BOUNDARY: pure-domain capability association certificate only
# TENANT POSTURE: exact synthetic tenant isolation semantics
# FAIL-CLOSED POSTURE: malformed, unknown, duplicate, and invalid lineage reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
