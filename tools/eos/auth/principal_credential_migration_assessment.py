"""Read-only assessment of one legacy tenant-bound credential for migration.

The assessor never writes, merges, creates principals or memberships, or changes
MFA/session state. Ambiguous or inconsistent legacy records are quarantined.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from tools.eos.auth.principal_credential import (
    MAX_CREDENTIAL_REVISION,
    PrincipalCredential,
    normalize_principal_email,
    validate_password_hash,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
    TenantMembershipRepository,
    TenantMembershipRepositoryError,
)
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry

VERSION = "v1.0.0-LEGACY-PRINCIPAL-CREDENTIAL-MIGRATION-ASSESSMENT"


@dataclass(frozen=True, slots=True)
class PrincipalCredentialMigrationAssessment:
    """Non-mutating outcome; credential verifier is hidden from repr."""

    disposition: str
    reason_code: str
    credential: PrincipalCredential | None = None
    tenant_id: str | None = None
    membership_revision: int | None = None


class PrincipalCredentialMigrationAssessmentUnavailable(RuntimeError):
    """A required canonical authority could not be read reliably."""


def assess_legacy_user_credential(
    *,
    document: Mapping[str, object],
    matching_email_record_count: int,
    principal_repository: Any = None,
    membership_repository: Any = None,
    tenant_resolver: Any = None,
    session: Any = None,
) -> PrincipalCredentialMigrationAssessment:
    """Assess one legacy users row without migrating or mutating any authority.

    Only an exactly unique email row with an exact ACTIVE global principal,
    canonical ACTIVE tenant and ACTIVE existing membership is eligible.
    Existing business roles and authorization assignments are not created or
    inferred here; workspace admission rechecks those independently later.
    """
    def quarantine(code: str) -> PrincipalCredentialMigrationAssessment:
        return PrincipalCredentialMigrationAssessment("QUARANTINE", code)

    if (
        not isinstance(matching_email_record_count, int)
        or isinstance(matching_email_record_count, bool)
        or matching_email_record_count != 1
    ):
        return quarantine("LEGACY_EMAIL_NOT_UNIQUE")
    principal_id = document.get("user_id")
    if not isinstance(principal_id, str) or not principal_id or principal_id != principal_id.strip():
        return quarantine("LEGACY_PRINCIPAL_ID_INVALID")
    try:
        email = normalize_principal_email(document.get("email"))
        password_hash = validate_password_hash(document.get("passwordHash"))
    except (TypeError, ValueError):
        return quarantine("LEGACY_CREDENTIAL_MATERIAL_INVALID")

    tenant_id = document.get("tenantId")
    if not isinstance(tenant_id, str) or not tenant_id or tenant_id != tenant_id.strip():
        return quarantine("LEGACY_TENANT_REFERENCE_INVALID")

    revision = document.get("credential_revision", 0)
    if (
        not isinstance(revision, int)
        or isinstance(revision, bool)
        or not 0 <= revision <= MAX_CREDENTIAL_REVISION
    ):
        return quarantine("LEGACY_CREDENTIAL_REVISION_INVALID")
    mfa_enabled = document.get("mfaRegistered")
    if not isinstance(mfa_enabled, bool):
        return quarantine("LEGACY_MFA_STATE_INVALID")

    principals = principal_repository or PrincipalAuthorityRepository()
    memberships = membership_repository or TenantMembershipRepository()
    resolve_tenant = tenant_resolver or TenantRegistry.resolve_canonical_tenant

    try:
        principal = principals.get(principal_id, session=session)
    except PrincipalAuthorityNotFoundError:
        return quarantine("LEGACY_PRINCIPAL_AUTHORITY_MISSING")
    except PrincipalAuthorityRepositoryError as error:
        raise PrincipalCredentialMigrationAssessmentUnavailable(
            "LEGACY_PRINCIPAL_AUTHORITY_UNAVAILABLE"
        ) from error
    if getattr(principal, "principal_id", None) != principal_id or getattr(principal, "status", None) is not PrincipalStatus.ACTIVE:
        return quarantine("LEGACY_PRINCIPAL_NOT_ACTIVE")

    try:
        tenant = resolve_tenant(tenant_id, session=session)
    except Exception as error:
        raise PrincipalCredentialMigrationAssessmentUnavailable(
            "LEGACY_CANONICAL_TENANT_UNAVAILABLE"
        ) from error
    if getattr(tenant, "tenant_id", None) != tenant_id:
        return quarantine("LEGACY_CANONICAL_TENANT_MISMATCH")

    try:
        membership = memberships.resolve(principal_id, tenant_id, session=session)
    except TenantMembershipNotFoundError:
        return quarantine("LEGACY_ACTIVE_MEMBERSHIP_MISSING")
    except TenantMembershipRepositoryError as error:
        raise PrincipalCredentialMigrationAssessmentUnavailable(
            "LEGACY_MEMBERSHIP_AUTHORITY_UNAVAILABLE"
        ) from error
    if (
        getattr(membership, "principal_id", None) != principal_id
        or getattr(membership, "tenant_id", None) != tenant_id
        or getattr(membership, "status", None) is not TenantMembershipStatus.ACTIVE
    ):
        return quarantine("LEGACY_ACTIVE_MEMBERSHIP_REQUIRED")

    credential = PrincipalCredential(
        principal_id=principal_id,
        normalized_email=email,
        password_hash=password_hash,
        credential_revision=revision,
        mfa_enabled=mfa_enabled,
    )
    return PrincipalCredentialMigrationAssessment(
        disposition="ELIGIBLE_FOR_GOVERNED_MIGRATION",
        reason_code="LEGACY_CREDENTIAL_AUTHORITIES_MATCH",
        credential=credential,
        tenant_id=tenant_id,
        membership_revision=membership.revision,
    )


__all__ = [
    "VERSION",
    "PrincipalCredentialMigrationAssessment",
    "PrincipalCredentialMigrationAssessmentUnavailable",
    "assess_legacy_user_credential",
]
