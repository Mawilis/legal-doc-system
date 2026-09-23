"""Canonical orchestration for principal-to-Deputy identity binding.

TITLE: WILSY OS Deputy Principal Binding Orchestrator
VERSION: v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-ORCHESTRATION
AUTHORITY: L8-6B current-authority composition before immutable identity binding.
EPITOME: Inside one caller-owned active transaction, prove current ACTIVE
         principal, ACTIVE tenant membership, ACTIVE tenant_deputy business
         role, ACTIVE DEPUTY authorization assignment, and exact canonical P1
         Deputy truth before persisting one immutable principal/deputy binding.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/deputy_principal_binding_orchestrator.py
COLLABORATION / OWNERSHIP: Principal/membership/business-role/role-assignment
                            repositories own current IAM facts; P1/P2/L8-0/L8-5
                            own Deputy truth; L8-6B binding domain/registry own
                            relation semantics/persistence; this module owns
                            composition only. HTTP actor admission is separate.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-ORCHESTRATION
           establishes transaction-required five-authority validation, exact
           tenant/deputy resolution, immutable binding persistence/replay,
           session propagation, and explicit non-authorizing identity linkage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Uses only opaque authority/deputy identifiers and
                             binding evidence; no credentials, JWT/header trust,
                             location, client, AI, provider, or payment data.
TENANT BOUNDARY: Every authority read, Deputy read, and binding write uses the
                 same explicit tenant_id and caller-owned transaction session.
AUTHORITY BOUNDARY: Composition proves prerequisites for identity linkage only.
                    It does not authenticate the caller, grant membership/roles,
                    authorize queue access, mutate service lifecycle, or create
                    service/return/billing/payment/settlement truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller must provide one already-active transaction; this
                      module never starts, commits, aborts, or retries it.
FAIL-CLOSED DECLARATION: Missing/inactive/wrong IAM authority, absent/corrupt
                         Deputy truth, inactive transaction, binding conflict,
                         persistence failure, or scope drift rejects before any
                         invented identity or authorization is returned.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final, NoReturn, cast

from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
    TenantMembershipRepository,
    TenantMembershipRepositoryError,
)
from tools.eos.legal_operations.domain.deputy_principal_binding import (
    DeputyPrincipalBinding,
    DeputyPrincipalBindingError,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import Deputy
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    LegalOperationsReadModelError,
    get_entity_read_model,
)
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    DeputyPrincipalBindingConflictError,
    DeputyPrincipalBindingRegistry,
    DeputyPrincipalBindingRegistryError,
)


VERSION: Final[str] = "v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-ORCHESTRATION"


class DeputyPrincipalBindingOrchestrationError(RuntimeError):
    """Stable fail-closed L8-6B composition failure."""

    def __init__(self, code: str) -> None:
        """Create one bounded orchestration failure code."""
        self.code = code
        super().__init__(code)


class DeputyPrincipalBindingTransactionRequiredError(
    DeputyPrincipalBindingOrchestrationError
):
    """Caller did not provide one already-active transaction."""


def _fail(
    code: str,
    cause: BaseException | None = None,
    *,
    error_type: type[DeputyPrincipalBindingOrchestrationError] = (
        DeputyPrincipalBindingOrchestrationError
    ),
) -> NoReturn:
    """Raise one stable L8-6B orchestration error with retained cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _active_transaction(session: object) -> object:
    """Require one caller-owned active transaction before any authority read."""
    if session is None:
        _fail(
            "L8_6B_ACTIVE_TRANSACTION_REQUIRED",
            error_type=DeputyPrincipalBindingTransactionRequiredError,
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(
            "L8_6B_ACTIVE_TRANSACTION_REQUIRED",
            error,
            error_type=DeputyPrincipalBindingTransactionRequiredError,
        )
    if active is not True:
        _fail(
            "L8_6B_ACTIVE_TRANSACTION_REQUIRED",
            error_type=DeputyPrincipalBindingTransactionRequiredError,
        )
    return session


def _principal(
    principal_id: str,
    collection: Any,
    *,
    session: Any,
) -> object:
    """Require exact current ACTIVE principal authority."""
    try:
        value = PrincipalAuthorityRepository.get(
            principal_id,
            collection,
            session=session,
        )
    except PrincipalAuthorityNotFoundError as error:
        _fail("L8_6B_PRINCIPAL_NOT_FOUND", error)
    except PrincipalAuthorityRepositoryError as error:
        _fail("L8_6B_PRINCIPAL_AUTHORITY_UNAVAILABLE", error)
    if value.status is not PrincipalStatus.ACTIVE:
        _fail("L8_6B_PRINCIPAL_INACTIVE")
    return value


def _membership(
    principal_id: str,
    tenant_id: str,
    collection: Any,
    *,
    session: Any,
) -> object:
    """Require exact current ACTIVE tenant membership."""
    try:
        value = TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            collection,
            session=session,
        )
    except TenantMembershipNotFoundError as error:
        _fail("L8_6B_MEMBERSHIP_NOT_FOUND", error)
    except TenantMembershipRepositoryError as error:
        _fail("L8_6B_MEMBERSHIP_AUTHORITY_UNAVAILABLE", error)
    if value.status is not TenantMembershipStatus.ACTIVE:
        _fail("L8_6B_MEMBERSHIP_INACTIVE")
    return value


def _business_role(
    principal_id: str,
    tenant_id: str,
    collection: Any,
    *,
    session: Any,
) -> object:
    """Require exact current ACTIVE tenant_deputy business-role evidence."""
    try:
        value = TenantBusinessRoleRepository.resolve(
            principal_id,
            tenant_id,
            collection,
            session=session,
        )
    except TenantBusinessRoleNotFoundError as error:
        _fail("L8_6B_DEPUTY_BUSINESS_ROLE_NOT_FOUND", error)
    except TenantBusinessRoleRepositoryError as error:
        _fail("L8_6B_DEPUTY_BUSINESS_ROLE_UNAVAILABLE", error)
    if (
        value.status is not TenantBusinessRoleStatus.ACTIVE
        or value.business_role != "tenant_deputy"
    ):
        _fail("L8_6B_DEPUTY_BUSINESS_ROLE_REQUIRED")
    return value


def _authorization_role(
    principal_id: str,
    tenant_id: str,
    collection: Any,
    *,
    session: Any,
) -> object:
    """Require exact current ACTIVE DEPUTY authorization-role assignment."""
    try:
        value = RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            "DEPUTY",
            collection,
            session=session,
        )
    except RoleAssignmentNotFoundError as error:
        _fail("L8_6B_DEPUTY_AUTHORIZATION_ROLE_NOT_FOUND", error)
    except RoleAssignmentRepositoryError as error:
        _fail("L8_6B_DEPUTY_AUTHORIZATION_ROLE_UNAVAILABLE", error)
    if value.status is not RoleAssignmentStatus.ACTIVE:
        _fail("L8_6B_DEPUTY_AUTHORIZATION_ROLE_REQUIRED")
    return value


def _deputy(
    tenant_id: str,
    deputy_id: str,
    lifecycle_collection: Any,
    *,
    session: Any,
) -> Deputy:
    """Resolve exact canonical current Deputy evidence through L8-5."""
    try:
        model = get_entity_read_model(
            tenant_id=tenant_id,
            entity_type="Deputy",
            entity_identity=deputy_id,
            lifecycle_collection=lifecycle_collection,
            session=session,
        )
    except LegalOperationsReadModelError as error:
        if error.code == "L8_5_ENTITY_NOT_FOUND":
            _fail("L8_6B_DEPUTY_NOT_FOUND", error)
        _fail("L8_6B_DEPUTY_EVIDENCE_UNAVAILABLE", error)
    if (
        model.tenant_id != tenant_id
        or model.entity_type != "Deputy"
        or model.entity_identity != deputy_id
        or type(model.current) is not Deputy
    ):
        _fail("L8_6B_DEPUTY_EVIDENCE_INVALID")
    return cast(Deputy, model.current)


def bind_deputy_principal_identity(
    *,
    tenant_id: str,
    principal_id: str,
    deputy_id: str,
    bound_at: datetime,
    evidence_reference: str,
    lifecycle_collection: Any,
    binding_collection: Any,
    principal_collection: Any,
    membership_collection: Any,
    business_role_collection: Any,
    role_assignment_collection: Any,
    session: Any,
) -> DeputyPrincipalBinding:
    """Create or exactly replay one canonical principal/Deputy identity binding.

    One active caller-owned transaction is required before any read. Current
    principal lifecycle, tenant membership, tenant_deputy business role, DEPUTY
    authorization assignment, and canonical Deputy evidence are independently
    resolved under the exact tenant and same session. Only after all five facts
    pass is the immutable binding factory invoked and its registry allowed to
    create or exactly replay the one-to-one relation.

    The returned binding is not authorization. Every future deputy-personal
    queue or command must re-evaluate current IAM independently and then resolve
    this binding; inactive/revoked IAM therefore remains authoritative even
    though immutable identity-link evidence continues to exist.
    """
    active_session = _active_transaction(session)
    _principal(principal_id, principal_collection, session=active_session)
    _membership(
        principal_id,
        tenant_id,
        membership_collection,
        session=active_session,
    )
    _business_role(
        principal_id,
        tenant_id,
        business_role_collection,
        session=active_session,
    )
    _authorization_role(
        principal_id,
        tenant_id,
        role_assignment_collection,
        session=active_session,
    )
    deputy = _deputy(
        tenant_id,
        deputy_id,
        lifecycle_collection,
        session=active_session,
    )

    try:
        value = DeputyPrincipalBinding.from_deputy(
            principal_id=principal_id,
            deputy=deputy,
            bound_at=bound_at,
            evidence_reference=evidence_reference,
        )
    except DeputyPrincipalBindingError as error:
        _fail("L8_6B_BINDING_VALUE_INVALID", error)

    try:
        return DeputyPrincipalBindingRegistry.create(
            value,
            binding_collection,
            session=active_session,
        )
    except DeputyPrincipalBindingConflictError as error:
        _fail("L8_6B_BINDING_CONFLICT", error)
    except DeputyPrincipalBindingRegistryError as error:
        _fail("L8_6B_BINDING_PERSISTENCE_UNAVAILABLE", error)


__all__ = [
    "VERSION",
    "DeputyPrincipalBindingOrchestrationError",
    "DeputyPrincipalBindingTransactionRequiredError",
    "bind_deputy_principal_identity",
]


# ARTIFACT: deputy_principal_binding_orchestrator.py
# VERSION: v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-ORCHESTRATION
# AUTHORITY BOUNDARY: current IAM + canonical Deputy validation before immutable identity-link persistence only
# TENANT POSTURE: exact same tenant/session across principal, membership, roles, Deputy, and binding
# FAIL-CLOSED POSTURE: inactive/missing/wrong IAM, absent/corrupt Deputy, conflict, persistence, or transaction failure rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
