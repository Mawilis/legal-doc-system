"""WILSY OS development-only legal persona provisioning orchestrator.

TITLE: WILSY OS Developer Legal Persona Provisioner
VERSION: v1.0.1-D15G-DEV-LEGAL-PERSONA-PROVISIONER
AUTHORITY: Wilsy OS Core Governance
EPITOME: Development-only, owner-authorized orchestration that atomically creates
         one ordinary-login legal test principal without mutating the founder
         owner identity or weakening canonical authentication/authorization.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/developer_persona_provisioner.py
COLLABORATION / OWNERSHIP: Python EOS auth orchestration owns the transaction;
                           AuthRegistry and authority repositories remain
                           bounded transaction participants.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG:
  v1.0.1-D15G-DEV-LEGAL-PERSONA-PROVISIONER — Repairs static type narrowing in the bounded request validator by
    validating each string input explicitly before returning the typed tuple.
    Runtime acceptance, authority, tenant, transaction, password, MFA, and
    financial semantics are unchanged.
  v1.0.0-D15G-DEV-LEGAL-PERSONA-PROVISIONER — Establishes an explicitly
    non-production legal-persona provisioning boundary for eight canonical
    Legal OS personas. Requires an exact ACTIVE tenant owner plus ACTIVE
    ENTERPRISE_ADMIN assignment, validates the prospective password through
    the canonical password-policy contract before transaction entry, and
    atomically composes credential, PrincipalAuthority, TenantMembership,
    TenantBusinessRole, and RoleAssignment state through one caller-owned
    Mongo transaction. No session, JWT, refresh token, MFA bypass, browser
    role assertion, cross-tenant authority, or financial authority is created.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001 awareness.
SECURITY / PRIVACY POSTURE: Disabled unless both an explicit non-production
                            ENV and WILSY_DEVELOPER_PERSONA_PROVISIONING=1 are
                            present. Passwords remain transient, are never
                            logged or returned, and must pass the canonical
                            fail-closed blocklist-backed password policy.
TENANT BOUNDARY: The authenticated owner projection, durable ACTIVE membership,
                 durable tenant_owner business role, and target tenant must
                 match exactly. Cross-tenant provisioning is prohibited.
AUTHORITY BOUNDARY: Development-only persona admission orchestration. It does
                    not create production impersonation, alter the owner,
                    bypass login/MFA, issue tokens, or broaden role policy.
FINANCIAL AUTHORITY BOUNDARY: No financial authority. Kennel EOS remains the
                              exclusive financial execution authority.
TRANSACTION BOUNDARY: This orchestrator owns exactly one PyMongo session and
                      with_transaction lifecycle. Every participating authority
                      read/write receives the transaction ClientSession.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import os
from types import MappingProxyType
from typing import Final

from pymongo.client_session import ClientSession
from pymongo.errors import PyMongoError

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityAlreadyExistsError,
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentAlreadyExistsError,
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleAlreadyExistsError,
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipAlreadyExistsError,
    TenantMembershipNotFoundError,
    TenantMembershipRepository,
    TenantMembershipRepositoryError,
)
from tools.eos.kernel.db import get_client
from tools.eos.saas.auth.auth_registry import AuthRegistry, AuthRegistryTenantError
from tools.eos.saas.auth.password_policy import (
    PasswordBlocklistChecker,
    PasswordPolicyViolation,
    validate_password,
)
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry, TenantRegistryError


VERSION: Final[str] = "v1.0.1-D15G-DEV-LEGAL-PERSONA-PROVISIONER"
_ENABLE_ENV: Final[str] = "WILSY_DEVELOPER_PERSONA_PROVISIONING"
_ALLOWED_ENVIRONMENTS: Final[frozenset[str]] = frozenset(
    {"development", "dev", "local", "test", "testing"}
)
_TRUE_VALUES: Final[frozenset[str]] = frozenset({"1", "true", "yes", "on"})


class DeveloperLegalPersona(StrEnum):
    """Canonical development personas mapped to existing Legal OS authorities."""

    LEGAL_PARTNER = "LEGAL_PARTNER"
    LEGAL_ATTORNEY = "LEGAL_ATTORNEY"
    LEGAL_PARALEGAL = "LEGAL_PARALEGAL"
    LEGAL_SECRETARY = "LEGAL_SECRETARY"
    LEGAL_FINANCE = "LEGAL_FINANCE"
    SHERIFF = "SHERIFF"
    DEPUTY = "DEPUTY"
    LEGAL_CLIENT = "LEGAL_CLIENT"


_PERSONA_AUTHORITY = MappingProxyType(
    {
        DeveloperLegalPersona.LEGAL_PARTNER: (
            "tenant_legal_partner",
            "LEGAL_PARTNER",
        ),
        DeveloperLegalPersona.LEGAL_ATTORNEY: (
            "tenant_legal_attorney",
            "LEGAL_ATTORNEY",
        ),
        DeveloperLegalPersona.LEGAL_PARALEGAL: (
            "tenant_legal_paralegal",
            "LEGAL_PARALEGAL",
        ),
        DeveloperLegalPersona.LEGAL_SECRETARY: (
            "tenant_legal_secretary",
            "LEGAL_SECRETARY",
        ),
        DeveloperLegalPersona.LEGAL_FINANCE: (
            "tenant_legal_finance",
            "LEGAL_FINANCE",
        ),
        DeveloperLegalPersona.SHERIFF: (
            "tenant_sheriff",
            "SHERIFF",
        ),
        DeveloperLegalPersona.DEPUTY: (
            "tenant_deputy",
            "DEPUTY",
        ),
        DeveloperLegalPersona.LEGAL_CLIENT: (
            "tenant_legal_client",
            "LEGAL_CLIENT",
        ),
    }
)


class DeveloperPersonaProvisioningCode(StrEnum):
    """Stable, secret-free denial classifications for provisioning."""

    ENVIRONMENT_DENIED = "DEVELOPER_PERSONA_ENVIRONMENT_DENIED"
    INVALID_REQUEST = "DEVELOPER_PERSONA_INVALID_REQUEST"
    OWNER_SCOPE_MISMATCH = "DEVELOPER_PERSONA_OWNER_SCOPE_MISMATCH"
    OWNER_PRINCIPAL_NOT_FOUND = "DEVELOPER_PERSONA_OWNER_PRINCIPAL_NOT_FOUND"
    OWNER_PRINCIPAL_INACTIVE = "DEVELOPER_PERSONA_OWNER_PRINCIPAL_INACTIVE"
    OWNER_MEMBERSHIP_NOT_FOUND = "DEVELOPER_PERSONA_OWNER_MEMBERSHIP_NOT_FOUND"
    OWNER_MEMBERSHIP_INACTIVE = "DEVELOPER_PERSONA_OWNER_MEMBERSHIP_INACTIVE"
    OWNER_BUSINESS_ROLE_NOT_FOUND = "DEVELOPER_PERSONA_OWNER_BUSINESS_ROLE_NOT_FOUND"
    OWNER_BUSINESS_ROLE_INVALID = "DEVELOPER_PERSONA_OWNER_BUSINESS_ROLE_INVALID"
    OWNER_AUTHORIZATION_ROLE_NOT_FOUND = (
        "DEVELOPER_PERSONA_OWNER_AUTHORIZATION_ROLE_NOT_FOUND"
    )
    OWNER_AUTHORIZATION_ROLE_INACTIVE = (
        "DEVELOPER_PERSONA_OWNER_AUTHORIZATION_ROLE_INACTIVE"
    )
    TENANT_INVALID = "DEVELOPER_PERSONA_TENANT_INVALID"
    PASSWORD_REJECTED = "DEVELOPER_PERSONA_PASSWORD_REJECTED"
    CREDENTIAL_CONFLICT = "DEVELOPER_PERSONA_CREDENTIAL_CONFLICT"
    AUTHORITY_CONFLICT = "DEVELOPER_PERSONA_AUTHORITY_CONFLICT"
    PERSISTENCE_FAILURE = "DEVELOPER_PERSONA_PERSISTENCE_FAILURE"


class DeveloperPersonaProvisioningError(RuntimeError):
    """Bounded provisioning failure that never retains password material."""

    def __init__(self, code: DeveloperPersonaProvisioningCode) -> None:
        """Create one stable secret-free orchestration failure."""
        if not isinstance(code, DeveloperPersonaProvisioningCode):
            raise TypeError("developer persona provisioning code is invalid")
        self.code = code
        super().__init__(code.value)

    def __str__(self) -> str:
        """Return only the stable bounded failure code."""
        return self.code.value

    def __repr__(self) -> str:
        """Return deterministic diagnostics without credentials or PII."""
        return f"DeveloperPersonaProvisioningError(code={self.code.value!r})"


@dataclass(frozen=True, slots=True)
class DeveloperPersonaProvisioningResult:
    """Non-secret result for one committed development persona admission.

    Authority: reports identifiers and canonical role facts created by this
    orchestrator; it is not a login token, impersonation handle, audit ledger,
    or authorization decision.

    Tenant scope: all fields describe one exact committed tenant principal.

    Mutation/idempotency: provisioning is create-only. Reusing an existing
    credential or authority identity fails closed rather than replaying.

    Financial boundary: contains no financial authority or execution state.
    """

    principal_id: str
    tenant_id: str
    persona: DeveloperLegalPersona
    business_role: str
    authorization_role: str
    credential_revision: int
    mfa_enrollment_required: bool


def _require_enabled_nonproduction_environment() -> None:
    """Fail closed unless explicit development/test enablement is present."""
    environment = os.getenv("ENV", "").strip().lower()
    enabled = os.getenv(_ENABLE_ENV, "").strip().lower()
    if environment not in _ALLOWED_ENVIRONMENTS or enabled not in _TRUE_VALUES:
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.ENVIRONMENT_DENIED
        )


def _require_request(
    *,
    owner_identity: SovereignIdentity,
    tenant_id: object,
    email: object,
    first_name: object,
    last_name: object,
    persona: object,
) -> tuple[str, str, str, str, DeveloperLegalPersona]:
    """Validate non-secret request shape without normalizing authority."""
    if not isinstance(owner_identity, SovereignIdentity):
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.INVALID_REQUEST
        )
    if (
        not isinstance(tenant_id, str)
        or not tenant_id
        or tenant_id != tenant_id.strip()
        or not isinstance(email, str)
        or not email
        or email != email.strip()
        or not isinstance(first_name, str)
        or not first_name
        or first_name != first_name.strip()
        or not isinstance(last_name, str)
        or not last_name
        or last_name != last_name.strip()
    ):
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.INVALID_REQUEST
        )
    if not isinstance(persona, DeveloperLegalPersona):
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.INVALID_REQUEST
        )
    if (
        owner_identity.tenant_id != tenant_id
        or not owner_identity.identity_id
        or owner_identity.identity_id != owner_identity.identity_id.strip()
    ):
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.OWNER_SCOPE_MISMATCH
        )
    return tenant_id, email, first_name, last_name, persona


def _require_owner_authority(
    *,
    owner_identity: SovereignIdentity,
    tenant_id: str,
    session: ClientSession,
) -> None:
    """Re-resolve exact durable owner authority inside the provisioning transaction."""
    try:
        principal = PrincipalAuthorityRepository.resolve(
            owner_identity.identity_id,
            session=session,
        )
    except PrincipalAuthorityNotFoundError as error:
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.OWNER_PRINCIPAL_NOT_FOUND
        ) from error
    if principal.status is not PrincipalStatus.ACTIVE:
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.OWNER_PRINCIPAL_INACTIVE
        )

    try:
        membership = TenantMembershipRepository.resolve(
            principal.principal_id,
            tenant_id,
            session=session,
        )
    except TenantMembershipNotFoundError as error:
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.OWNER_MEMBERSHIP_NOT_FOUND
        ) from error
    if membership.status is not TenantMembershipStatus.ACTIVE:
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.OWNER_MEMBERSHIP_INACTIVE
        )

    try:
        business_role = TenantBusinessRoleRepository.resolve(
            principal.principal_id,
            tenant_id,
            session=session,
        )
    except TenantBusinessRoleNotFoundError as error:
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.OWNER_BUSINESS_ROLE_NOT_FOUND
        ) from error
    if (
        business_role.status is not TenantBusinessRoleStatus.ACTIVE
        or business_role.business_role != "tenant_owner"
    ):
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.OWNER_BUSINESS_ROLE_INVALID
        )

    try:
        authorization_role = RoleAssignmentRepository.resolve(
            principal.principal_id,
            tenant_id,
            "ENTERPRISE_ADMIN",
            session=session,
        )
    except RoleAssignmentNotFoundError as error:
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.OWNER_AUTHORIZATION_ROLE_NOT_FOUND
        ) from error
    if authorization_role.status is not RoleAssignmentStatus.ACTIVE:
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.OWNER_AUTHORIZATION_ROLE_INACTIVE
        )


def provision_developer_legal_persona(
    *,
    owner_identity: SovereignIdentity,
    tenant_id: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    persona: DeveloperLegalPersona,
    password_blocklist_checker: PasswordBlocklistChecker,
    auth_registry: AuthRegistry | None = None,
) -> DeveloperPersonaProvisioningResult:
    """Atomically create one development-only Legal OS test principal.

    Authority:
        Requires explicit development/test enablement and re-resolves the
        authenticated owner as ACTIVE principal + ACTIVE membership +
        ACTIVE tenant_owner business role + ACTIVE ENTERPRISE_ADMIN assignment
        inside the same transaction used for all target writes.

    Tenant scope:
        tenant_id must exactly equal owner_identity.tenant_id and must resolve
        as one ACTIVE canonical tenant inside the transaction. No alias or
        cross-tenant provisioning authority is accepted here.

    Mutation semantics:
        Creates exactly one authentication credential row, one ACTIVE
        PrincipalAuthority revision 0, one ACTIVE TenantMembership revision 0,
        one ACTIVE TenantBusinessRole revision 0, and one ACTIVE RoleAssignment
        revision 0. The legacy credential role is the matching canonical
        authorization-role identifier; browser workspace authority remains
        derived from the dedicated TenantBusinessRole repository.

    Password/security semantics:
        The complete prospective password is validated before transaction entry
        through the canonical fail-closed password policy and caller-supplied
        blocklist capability. Password text and bcrypt hash are never returned
        by this function. The created account remains mfaRegistered=False so
        ordinary authentication must perform the established MFA enrollment
        path rather than receiving a bypass.

    Transaction/idempotency:
        This orchestrator owns one PyMongo with_transaction lifecycle. PyMongo
        may restart the complete callback from fresh transaction state for
        transient transaction errors. All authority reads/writes receive the
        callback ClientSession. The operation is create-only: credential or
        authority conflicts fail closed rather than being treated as replay.

    Failure semantics:
        Raises DeveloperPersonaProvisioningError for bounded environment,
        authority, policy, conflict, tenant, or persistence failures. Unknown
        programming failures are not swallowed.

    Financial boundary:
        No payment, release, execution, settlement, billing, or Kennel authority
        is created or inferred.

    Audit/evidence boundary:
        The returned immutable result is operational confirmation only. No
        canonical durable auth-audit registry was discovered for this domain, so
        this version does not claim durable provisioning-audit evidence.
    """
    _require_enabled_nonproduction_environment()
    tenant_id, email, first_name, last_name, persona = _require_request(
        owner_identity=owner_identity,
        tenant_id=tenant_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        persona=persona,
    )

    if not isinstance(password, str):
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.INVALID_REQUEST
        )
    try:
        validate_password(
            password,
            checker=password_blocklist_checker,
            context_terms=(email, first_name, last_name),
        )
    except PasswordPolicyViolation as error:
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.PASSWORD_REJECTED
        ) from error

    business_role, authorization_role = _PERSONA_AUTHORITY[persona]
    registry = auth_registry if auth_registry is not None else AuthRegistry()
    if not isinstance(registry, AuthRegistry):
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.INVALID_REQUEST
        )

    client = get_client()
    if client is None:
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.PERSISTENCE_FAILURE
        )

    def transaction_callback(
        session: ClientSession,
    ) -> DeveloperPersonaProvisioningResult:
        try:
            canonical_tenant = TenantRegistry.resolve_canonical_tenant(
                tenant_id,
                session=session,
            )
        except TenantRegistryError as error:
            raise DeveloperPersonaProvisioningError(
                DeveloperPersonaProvisioningCode.TENANT_INVALID
            ) from error
        if canonical_tenant.tenant_id != tenant_id:
            raise DeveloperPersonaProvisioningError(
                DeveloperPersonaProvisioningCode.TENANT_INVALID
            )

        _require_owner_authority(
            owner_identity=owner_identity,
            tenant_id=tenant_id,
            session=session,
        )

        try:
            user = registry.register_user(
                email,
                password,
                first_name,
                last_name,
                authorization_role,
                tenant_id,
                session=session,
            )
        except ValueError as error:
            if str(error) == "Email already exists":
                raise DeveloperPersonaProvisioningError(
                    DeveloperPersonaProvisioningCode.CREDENTIAL_CONFLICT
                ) from error
            raise DeveloperPersonaProvisioningError(
                DeveloperPersonaProvisioningCode.INVALID_REQUEST
            ) from error
        except AuthRegistryTenantError as error:
            raise DeveloperPersonaProvisioningError(
                DeveloperPersonaProvisioningCode.TENANT_INVALID
            ) from error

        principal = PrincipalAuthority(
            user.id,
            PrincipalStatus.ACTIVE,
            0,
        )
        membership = TenantMembershipAuthority(
            user.id,
            tenant_id,
            TenantMembershipStatus.ACTIVE,
            0,
        )
        effective_at = datetime.now(timezone.utc)
        tenant_business_role = TenantBusinessRoleAuthority(
            user.id,
            tenant_id,
            business_role,
            TenantBusinessRoleStatus.ACTIVE,
            0,
            effective_at,
            None,
        )
        role_assignment = RoleAssignmentAuthority(
            user.id,
            tenant_id,
            authorization_role,
            RoleAssignmentStatus.ACTIVE,
            0,
        )

        try:
            PrincipalAuthorityRepository.create(
                principal,
                session=session,
            )
            TenantMembershipRepository.insert(
                membership,
                session=session,
            )
            TenantBusinessRoleRepository.insert(
                tenant_business_role,
                session=session,
            )
            RoleAssignmentRepository.insert(
                role_assignment,
                session=session,
            )
        except (
            PrincipalAuthorityAlreadyExistsError,
            TenantMembershipAlreadyExistsError,
            TenantBusinessRoleAlreadyExistsError,
            RoleAssignmentAlreadyExistsError,
        ) as error:
            raise DeveloperPersonaProvisioningError(
                DeveloperPersonaProvisioningCode.AUTHORITY_CONFLICT
            ) from error

        return DeveloperPersonaProvisioningResult(
            principal_id=user.id,
            tenant_id=tenant_id,
            persona=persona,
            business_role=business_role,
            authorization_role=authorization_role,
            credential_revision=0,
            mfa_enrollment_required=True,
        )

    try:
        with client.start_session() as session:
            result = session.with_transaction(transaction_callback)
    except DeveloperPersonaProvisioningError:
        raise
    except (
        PrincipalAuthorityRepositoryError,
        TenantMembershipRepositoryError,
        TenantBusinessRoleRepositoryError,
        RoleAssignmentRepositoryError,
        TenantRegistryError,
        PyMongoError,
    ) as error:
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.PERSISTENCE_FAILURE
        ) from error

    if not isinstance(result, DeveloperPersonaProvisioningResult):
        raise DeveloperPersonaProvisioningError(
            DeveloperPersonaProvisioningCode.PERSISTENCE_FAILURE
        )
    return result


__all__ = [
    "DeveloperLegalPersona",
    "DeveloperPersonaProvisioningCode",
    "DeveloperPersonaProvisioningError",
    "DeveloperPersonaProvisioningResult",
    "VERSION",
    "provision_developer_legal_persona",
]


# ARTIFACT: tools/eos/auth/developer_persona_provisioner.py
# VERSION: v1.0.1-D15G-DEV-LEGAL-PERSONA-PROVISIONER
# AUTHORITY BOUNDARY: development-only owner-authorized legal test-principal admission
# TENANT POSTURE: exact owner principal + tenant + membership + tenant_owner + ENTERPRISE_ADMIN scope; no cross-tenant provisioning
# FAIL-CLOSED POSTURE: production, disabled flag, malformed request, policy rejection, authority drift, conflicts, and persistence failure deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
