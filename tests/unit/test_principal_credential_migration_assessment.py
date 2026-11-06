"""Read-only legacy credential migration assessment tests."""
from types import SimpleNamespace

import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.principal_credential_migration_assessment import (
    PrincipalCredentialMigrationAssessmentUnavailable,
    assess_legacy_user_credential,
)

PASSWORD_HASH = "$2b$12$" + "c" * 53


class PrincipalRepository:
    def __init__(self, status=PrincipalStatus.ACTIVE, failure=None):
        self.status = status
        self.failure = failure

    def get(self, principal_id, *, session=None):
        if self.failure:
            raise self.failure
        return SimpleNamespace(principal_id=principal_id, status=self.status)


class MembershipRepository:
    def __init__(self, status=TenantMembershipStatus.ACTIVE, failure=None):
        self.status = status
        self.failure = failure

    def resolve(self, principal_id, tenant_id, *, session=None):
        if self.failure:
            raise self.failure
        return SimpleNamespace(
            principal_id=principal_id,
            tenant_id=tenant_id,
            status=self.status,
            revision=4,
        )


def assess(document=None, **overrides):
    value = {
        "user_id": "principal-1",
        "email": "Owner@Example.com",
        "passwordHash": PASSWORD_HASH,
        "credential_revision": 8,
        "mfaRegistered": True,
        "tenantId": "tenant-a",
    }
    if document:
        value.update(document)
    args = {
        "document": value,
        "matching_email_record_count": 1,
        "principal_repository": PrincipalRepository(),
        "membership_repository": MembershipRepository(),
        "tenant_resolver": lambda tenant_id, session=None: SimpleNamespace(tenant_id=tenant_id),
    }
    args.update(overrides)
    return assess_legacy_user_credential(**args)


def test_only_exact_active_legacy_credential_is_eligible_without_mutation():
    result = assess()
    assert result.disposition == "ELIGIBLE_FOR_GOVERNED_MIGRATION"
    assert result.reason_code == "LEGACY_CREDENTIAL_AUTHORITIES_MATCH"
    assert result.credential.normalized_email == "owner@example.com"
    assert result.credential.credential_revision == 8
    assert result.credential.mfa_enabled is True
    assert result.membership_revision == 4
    assert PASSWORD_HASH not in repr(result)
    assert PASSWORD_HASH not in repr(result.credential)


@pytest.mark.parametrize(
    ("count", "reason"),
    [
        (0, "LEGACY_EMAIL_NOT_UNIQUE"),
        (2, "LEGACY_EMAIL_NOT_UNIQUE"),
    ],
)
def test_duplicate_or_missing_email_rows_are_quarantined(count, reason):
    result = assess(matching_email_record_count=count)
    assert result.disposition == "QUARANTINE"
    assert result.reason_code == reason


def test_inactive_principal_and_membership_are_quarantined():
    result = assess(principal_repository=PrincipalRepository(PrincipalStatus.SUSPENDED))
    assert result.reason_code == "LEGACY_PRINCIPAL_NOT_ACTIVE"
    result = assess(membership_repository=MembershipRepository(TenantMembershipStatus.SUSPENDED))
    assert result.reason_code == "LEGACY_ACTIVE_MEMBERSHIP_REQUIRED"


def test_invalid_credential_or_mfa_material_is_quarantined():
    result = assess({"passwordHash": "not-a-hash"})
    assert result.reason_code == "LEGACY_CREDENTIAL_MATERIAL_INVALID"
    result = assess({"mfaRegistered": "true"})
    assert result.reason_code == "LEGACY_MFA_STATE_INVALID"


def test_authority_outage_is_not_misclassified_as_quarantine():
    from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepositoryError
    with pytest.raises(PrincipalCredentialMigrationAssessmentUnavailable):
        assess(principal_repository=PrincipalRepository(failure=PrincipalAuthorityRepositoryError("unavailable")))
