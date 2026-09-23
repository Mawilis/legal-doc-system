"""Sovereign provisioning orchestration for Legal client matter visibility.

TITLE: WILSY OS Legal Client Matter Visibility Provisioning Orchestrator
VERSION: v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING
AUTHORITY: Current-IAM and canonical-matter composition before L8-7A/L8-7B grant/revoke persistence.
EPITOME: Inside one caller-owned active transaction, prove the law-firm actor
         through the canonical C3B operation/permission decision, prove the
         target principal is an ACTIVE same-tenant LEGAL_CLIENT, resolve the
         exact current canonical P1 CaseMatter, then create or revoke only the
         explicit L8-7A relation through append-only L8-7B persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_client_matter_visibility_orchestrator.py
COLLABORATION / OWNERSHIP: Tenant authorization owns actor authority; current
                            principal/membership/business-role/final-role readers
                            own target-client IAM; P1/P2/L8-0/L8-5 own current
                            CaseMatter truth; L8-7A owns relation semantics;
                            L8-7B owns persistence/currentness; this module owns
                            transaction-required provisioning composition only.
                            HTTP admission and client projection remain later gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING
           establishes active-transaction enforcement, exact C3B actor
           authorization, independent ACTIVE target LEGAL_CLIENT IAM proof,
           canonical current CaseMatter resolution, session propagation, L8-7A
           grant/revoke construction, and L8-7B append-only persistence with
           stable fail-closed error translation. No client read route is opened.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque principal/tenant/matter identifiers and
                             evidence references only. No credentials, JWT/header
                             trust, document body, GPS, AI, provider, billing,
                             payment, or settlement payload is admitted.
TENANT BOUNDARY: Actor, target client, CaseMatter and visibility persistence all
                 use one explicit tenant and the same caller-owned transaction.
                 Foreign or missing scope is ordinary denial/absence.
AUTHORITY BOUNDARY: Provisioning composition only. A persisted ACTIVE relation
                    is not itself authentication, current client-read permission,
                    HTTP authorization, lifecycle mutation, service proof, return,
                    invoice, payment, execution, or settlement truth.
FINANCIAL AUTHORITY BOUNDARY: No financial semantics or execution authority;
                              Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: One already-active caller-owned transaction is mandatory
                      before every authority read. This module never starts,
                      commits, aborts, retries, or owns a session/transaction.
FAIL-CLOSED DECLARATION: Missing/inactive/malformed actor or target IAM, denied
                         C3B authorization, absent/corrupt matter, visibility
                         conflict/corruption, missing current ACTIVE visibility,
                         invalid value evidence, persistence failure, or inactive
                         transaction rejects without grant, revoke, fallback, or healing.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final, NoReturn, Protocol, cast

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
    TenantMembershipRepositoryError,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.legal_operations.domain.legal_client_matter_visibility_binding import (
    LegalClientMatterVisibilityBinding,
    LegalClientMatterVisibilityBindingError,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    LegalOperationsReadModelError,
    get_entity_read_model,
)
from tools.eos.legal_operations.registry.legal_client_matter_visibility_registry import (
    LegalClientMatterVisibilityConflictError,
    LegalClientMatterVisibilityNotFoundError,
    LegalClientMatterVisibilityPersistedRecordInvalidError,
    LegalClientMatterVisibilityRegistry,
    LegalClientMatterVisibilityRegistryError,
)


VERSION: Final[str] = (
    "v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING"
)
PERMISSION: Final[str] = "legal_operations:client_visibility:write"
OPERATION: Final[str] = "legal_client_visibility_write"


class LegalClientMatterVisibilityProvisioningError(RuntimeError):
    """Stable fail-closed C3C provisioning composition failure."""

    def __init__(self, code: str) -> None:
        """Create one bounded provisioning failure code."""
        self.code = code
        super().__init__(code)


class LegalClientMatterVisibilityTransactionRequiredError(
    LegalClientMatterVisibilityProvisioningError
):
    """Caller did not provide one already-active transaction."""


class PrincipalReader(Protocol):
    """Read current principal authority without mutation or transaction ownership."""

    def resolve(
        self,
        principal_id: str,
        *,
        session: Any = None,
    ) -> object: ...


class MembershipReader(Protocol):
    """Read current exact principal/tenant membership authority."""

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> object: ...


class RoleReader(Protocol):
    """Read current exact principal/tenant/role authority."""

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> object: ...


def _fail(
    code: str,
    cause: BaseException | None = None,
    *,
    error_type: type[LegalClientMatterVisibilityProvisioningError] = (
        LegalClientMatterVisibilityProvisioningError
    ),
) -> NoReturn:
    """Raise one stable C3C error while retaining the technical root cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _active_transaction(session: object) -> object:
    """Require one caller-owned active transaction before any authority read."""
    if session is None:
        _fail(
            "L8_7C3C_ACTIVE_TRANSACTION_REQUIRED",
            error_type=LegalClientMatterVisibilityTransactionRequiredError,
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(
            "L8_7C3C_ACTIVE_TRANSACTION_REQUIRED",
            error,
            error_type=LegalClientMatterVisibilityTransactionRequiredError,
        )
    if active is not True:
        _fail(
            "L8_7C3C_ACTIVE_TRANSACTION_REQUIRED",
            error_type=LegalClientMatterVisibilityTransactionRequiredError,
        )
    return session


def _actor_authorized(
    *,
    tenant_id: str,
    actor_principal_id: str,
    principal_repository: PrincipalReader,
    membership_repository: MembershipReader,
    business_role_repository: RoleReader,
    role_assignment_repository: RoleReader,
    session: Any,
) -> None:
    """Require the exact current C3B law-firm provisioning authorization."""
    decision = authorize_tenant_operation(
        principal_id=actor_principal_id,
        tenant_id=tenant_id,
        permission_id=PERMISSION,
        operation=OPERATION,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=session,
    )
    if (
        decision.authorized is not True
        or decision.reason is not TenantAuthorizationReason.AUTHORIZED
        or decision.business_role
        not in {
            "tenant_legal_partner",
            "tenant_legal_attorney",
            "tenant_legal_paralegal",
        }
        or decision.authorization_role
        not in {
            "LEGAL_PARTNER",
            "LEGAL_ATTORNEY",
            "LEGAL_PARALEGAL",
        }
    ):
        _fail(
            "L8_7C3C_ACTOR_AUTHORIZATION_DENIED_"
            + decision.reason.value
        )


def _target_client(
    *,
    tenant_id: str,
    client_principal_id: str,
    principal_repository: PrincipalReader,
    membership_repository: MembershipReader,
    business_role_repository: RoleReader,
    role_assignment_repository: RoleReader,
    session: Any,
) -> None:
    """Require independently current ACTIVE same-tenant LEGAL_CLIENT IAM."""
    try:
        principal = principal_repository.resolve(
            client_principal_id,
            session=session,
        )
    except PrincipalAuthorityNotFoundError as error:
        _fail("L8_7C3C_CLIENT_PRINCIPAL_NOT_FOUND", error)
    except PrincipalAuthorityRepositoryError as error:
        _fail("L8_7C3C_CLIENT_PRINCIPAL_AUTHORITY_UNAVAILABLE", error)
    if getattr(principal, "status", None) is not PrincipalStatus.ACTIVE:
        _fail("L8_7C3C_CLIENT_PRINCIPAL_INACTIVE")

    try:
        membership = membership_repository.resolve(
            client_principal_id,
            tenant_id,
            session=session,
        )
    except TenantMembershipNotFoundError as error:
        _fail("L8_7C3C_CLIENT_MEMBERSHIP_NOT_FOUND", error)
    except TenantMembershipRepositoryError as error:
        _fail("L8_7C3C_CLIENT_MEMBERSHIP_AUTHORITY_UNAVAILABLE", error)
    if getattr(membership, "status", None) is not TenantMembershipStatus.ACTIVE:
        _fail("L8_7C3C_CLIENT_MEMBERSHIP_INACTIVE")

    try:
        business_role = business_role_repository.resolve(
            client_principal_id,
            tenant_id,
            "tenant_legal_client",
            session=session,
        )
    except RoleAssignmentNotFoundError as error:
        _fail("L8_7C3C_CLIENT_BUSINESS_ROLE_NOT_FOUND", error)
    except RoleAssignmentRepositoryError as error:
        _fail("L8_7C3C_CLIENT_BUSINESS_ROLE_UNAVAILABLE", error)
    if (
        getattr(business_role, "status", None)
        is not TenantBusinessRoleStatus.ACTIVE
    ):
        _fail("L8_7C3C_CLIENT_BUSINESS_ROLE_REQUIRED")

    try:
        authorization_role = role_assignment_repository.resolve(
            client_principal_id,
            tenant_id,
            "LEGAL_CLIENT",
            session=session,
        )
    except RoleAssignmentNotFoundError as error:
        _fail("L8_7C3C_CLIENT_AUTHORIZATION_ROLE_NOT_FOUND", error)
    except RoleAssignmentRepositoryError as error:
        _fail("L8_7C3C_CLIENT_AUTHORIZATION_ROLE_UNAVAILABLE", error)
    if (
        getattr(authorization_role, "status", None)
        is not RoleAssignmentStatus.ACTIVE
    ):
        _fail("L8_7C3C_CLIENT_AUTHORIZATION_ROLE_REQUIRED")


def _case_matter(
    *,
    tenant_id: str,
    case_matter_id: str,
    lifecycle_collection: Any,
    session: Any,
) -> CaseMatter:
    """Resolve one exact canonical current P1 CaseMatter through L8-5."""
    try:
        model = get_entity_read_model(
            tenant_id=tenant_id,
            entity_type="CaseMatter",
            entity_identity=case_matter_id,
            lifecycle_collection=lifecycle_collection,
            session=session,
        )
    except LegalOperationsReadModelError as error:
        if error.code == "L8_5_ENTITY_NOT_FOUND":
            _fail("L8_7C3C_CASE_MATTER_NOT_FOUND", error)
        _fail("L8_7C3C_CASE_MATTER_EVIDENCE_UNAVAILABLE", error)
    if (
        model.tenant_id != tenant_id
        or model.entity_type != "CaseMatter"
        or model.entity_identity != case_matter_id
        or type(model.current) is not CaseMatter
    ):
        _fail("L8_7C3C_CASE_MATTER_EVIDENCE_INVALID")
    return cast(CaseMatter, model.current)


def _prove_common_authority(
    *,
    tenant_id: str,
    actor_principal_id: str,
    client_principal_id: str,
    case_matter_id: str,
    lifecycle_collection: Any,
    principal_repository: PrincipalReader,
    membership_repository: MembershipReader,
    business_role_repository: RoleReader,
    role_assignment_repository: RoleReader,
    session: Any,
) -> tuple[object, CaseMatter]:
    """Prove actor, target-client and canonical matter under one active session."""
    active_session = _active_transaction(session)
    _actor_authorized(
        tenant_id=tenant_id,
        actor_principal_id=actor_principal_id,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=active_session,
    )
    _target_client(
        tenant_id=tenant_id,
        client_principal_id=client_principal_id,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=active_session,
    )
    matter = _case_matter(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        lifecycle_collection=lifecycle_collection,
        session=active_session,
    )
    return active_session, matter


def grant_client_matter_visibility(
    *,
    tenant_id: str,
    actor_principal_id: str,
    client_principal_id: str,
    case_matter_id: str,
    granted_at: datetime,
    evidence_reference: str,
    lifecycle_collection: Any,
    visibility_collection: Any,
    principal_repository: PrincipalReader,
    membership_repository: MembershipReader,
    business_role_repository: RoleReader,
    role_assignment_repository: RoleReader,
    session: Any,
) -> LegalClientMatterVisibilityBinding:
    """Create or exactly replay one sovereign client-to-matter visibility grant.

    The actor and target client are independently re-evaluated from current IAM
    under the caller's already-active transaction. The relation tenant/matter
    scope is derived from current canonical CaseMatter evidence; caller tenant
    and matter identifiers select scope but do not create authority. Only after
    all current facts pass may L8-7A construct the ACTIVE relation and L8-7B
    append or exactly replay it.

    The returned ACTIVE value is relation evidence only. It is not a client read
    authorization and cannot bypass the still-closed client projection policy.
    """
    active_session, matter = _prove_common_authority(
        tenant_id=tenant_id,
        actor_principal_id=actor_principal_id,
        client_principal_id=client_principal_id,
        case_matter_id=case_matter_id,
        lifecycle_collection=lifecycle_collection,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=session,
    )
    try:
        value = LegalClientMatterVisibilityBinding.grant(
            client_principal_id=client_principal_id,
            case_matter=matter,
            granted_by_principal_id=actor_principal_id,
            granted_at=granted_at,
            evidence_reference=evidence_reference,
        )
    except LegalClientMatterVisibilityBindingError as error:
        _fail("L8_7C3C_VISIBILITY_VALUE_INVALID", error)

    try:
        return LegalClientMatterVisibilityRegistry.grant(
            value,
            visibility_collection,
            session=active_session,
        )
    except LegalClientMatterVisibilityConflictError as error:
        _fail("L8_7C3C_VISIBILITY_CONFLICT", error)
    except LegalClientMatterVisibilityPersistedRecordInvalidError as error:
        _fail("L8_7C3C_VISIBILITY_PERSISTED_RECORD_INVALID", error)
    except LegalClientMatterVisibilityRegistryError as error:
        _fail("L8_7C3C_VISIBILITY_PERSISTENCE_UNAVAILABLE", error)


def revoke_client_matter_visibility(
    *,
    tenant_id: str,
    actor_principal_id: str,
    client_principal_id: str,
    case_matter_id: str,
    revoked_at: datetime,
    evidence_reference: str,
    lifecycle_collection: Any,
    visibility_collection: Any,
    principal_repository: PrincipalReader,
    membership_repository: MembershipReader,
    business_role_repository: RoleReader,
    role_assignment_repository: RoleReader,
    session: Any,
) -> LegalClientMatterVisibilityBinding:
    """Revoke one exact currently ACTIVE client-to-matter visibility relation.

    Actor authorization, target LEGAL_CLIENT IAM and canonical current CaseMatter
    are all re-proven under the same active transaction before current visibility
    is resolved. Revocation then appends one immutable REVOKED successor through
    L8-7B. Already-revoked or absent relations are explicit non-visibility rather
    than inferred success; no reactivation or delete path exists.
    """
    active_session, _ = _prove_common_authority(
        tenant_id=tenant_id,
        actor_principal_id=actor_principal_id,
        client_principal_id=client_principal_id,
        case_matter_id=case_matter_id,
        lifecycle_collection=lifecycle_collection,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        role_assignment_repository=role_assignment_repository,
        session=session,
    )
    try:
        active = LegalClientMatterVisibilityRegistry.resolve_current_active(
            tenant_id,
            client_principal_id,
            case_matter_id,
            visibility_collection,
            session=active_session,
        )
    except LegalClientMatterVisibilityNotFoundError as error:
        _fail("L8_7C3C_ACTIVE_VISIBILITY_NOT_FOUND", error)
    except LegalClientMatterVisibilityPersistedRecordInvalidError as error:
        _fail("L8_7C3C_VISIBILITY_PERSISTED_RECORD_INVALID", error)
    except LegalClientMatterVisibilityRegistryError as error:
        _fail("L8_7C3C_VISIBILITY_PERSISTENCE_UNAVAILABLE", error)

    try:
        revoked = active.revoke(
            revoked_by_principal_id=actor_principal_id,
            revoked_at=revoked_at,
            evidence_reference=evidence_reference,
        )
    except LegalClientMatterVisibilityBindingError as error:
        _fail("L8_7C3C_VISIBILITY_VALUE_INVALID", error)

    try:
        return LegalClientMatterVisibilityRegistry.revoke(
            revoked,
            visibility_collection,
            session=active_session,
        )
    except LegalClientMatterVisibilityConflictError as error:
        _fail("L8_7C3C_VISIBILITY_CONFLICT", error)
    except LegalClientMatterVisibilityPersistedRecordInvalidError as error:
        _fail("L8_7C3C_VISIBILITY_PERSISTED_RECORD_INVALID", error)
    except LegalClientMatterVisibilityRegistryError as error:
        _fail("L8_7C3C_VISIBILITY_PERSISTENCE_UNAVAILABLE", error)


__all__ = [
    "OPERATION",
    "PERMISSION",
    "VERSION",
    "LegalClientMatterVisibilityProvisioningError",
    "LegalClientMatterVisibilityTransactionRequiredError",
    "grant_client_matter_visibility",
    "revoke_client_matter_visibility",
]


# ARTIFACT: legal_client_matter_visibility_orchestrator.py
# VERSION: v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING
# AUTHORITY BOUNDARY: current actor IAM + target LEGAL_CLIENT IAM + canonical CaseMatter before L8-7A/L8-7B persistence only
# TENANT POSTURE: one explicit tenant and caller-owned active transaction span every authority read and visibility write
# FAIL-CLOSED POSTURE: denied/inactive IAM, absent/corrupt matter, invalid relation, conflict, persistence failure or inactive transaction rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
