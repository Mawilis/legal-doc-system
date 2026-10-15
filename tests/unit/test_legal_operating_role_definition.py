from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_operating_role_definition import (
    LegalOperatingRoleDefinition,
    LegalOperatingRoleDefinitionError,
)

NOW = datetime(2026, 10, 13, 12, 0, 0, 123456, tzinfo=timezone.utc)
FP = "a" * 128


def role(
    *,
    tenant_id: str = "tenant-a",
    operating_role_id: str = "role-bespoke-cross-border-disputes",
    role_revision: int = 1,
    display_name: str = "Bespoke Cross-Border Disputes Lead",
    description: str | None = "Tenant-defined role.",
    effective_from: datetime = NOW,
    supersedes_fingerprint: str | None = None,
) -> LegalOperatingRoleDefinition:
    return LegalOperatingRoleDefinition(
        tenant_id=tenant_id,
        operating_role_id=operating_role_id,
        role_revision=role_revision,
        display_name=display_name,
        description=description,
        effective_from=effective_from,
        supersedes_fingerprint=supersedes_fingerprint,
    )


def test_arbitrary_tenant_role_name_and_round_trip() -> None:
    value = role(display_name="Global Arbitration Knowledge Partner")
    assert value.display_name == "Global Arbitration Knowledge Partner"
    assert len(value.fingerprint) == 128
    assert LegalOperatingRoleDefinition.from_dict(value.to_dict()) == value


def test_stable_identity_revision_lineage() -> None:
    value = role(role_revision=2, supersedes_fingerprint=FP)
    assert value.operating_role_id == "role-bespoke-cross-border-disputes"
    assert value.role_revision == 2


@pytest.mark.parametrize("tenant", ("", "global", "root", "*"))
def test_pseudo_tenant_rejected(tenant: str) -> None:
    with pytest.raises(LegalOperatingRoleDefinitionError):
        role(tenant_id=tenant)


def test_lineage_rules() -> None:
    with pytest.raises(LegalOperatingRoleDefinitionError):
        role(supersedes_fingerprint=FP)
    with pytest.raises(LegalOperatingRoleDefinitionError):
        role(role_revision=2)


def test_strict_schema_and_fingerprint() -> None:
    value = role()
    payload = value.to_dict()
    payload["fingerprint"] = "b" * 128
    with pytest.raises(LegalOperatingRoleDefinitionError):
        LegalOperatingRoleDefinition.from_dict(payload)

    payload = value.to_dict()
    payload["permission"] = "forbidden"
    with pytest.raises(LegalOperatingRoleDefinitionError):
        LegalOperatingRoleDefinition.from_dict(payload)


def test_immutability_and_no_authority_fields() -> None:
    forbidden = {
        "permission", "business_role", "authorization_role", "job_title",
        "matter_role", "assignee_principal_id", "supervisor_principal_id",
        "entitlement_id", "payment", "settlement",
    }
    assert forbidden.isdisjoint(LegalOperatingRoleDefinition.__dataclass_fields__)
    value = role()
    with pytest.raises(FrozenInstanceError):
        setattr(cast(Any, value), "display_name", "mutated")
