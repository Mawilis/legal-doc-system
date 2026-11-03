"""Atomic EOS tenant-owner genesis provisioning.

Composes independently verified ownership evidence with canonical tenant,
membership, IAM-role and multi-capacity repositories. The caller owns the
Mongo transaction; any raised exception must abort that transaction.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.tenant_ownership_lifecycle_command import TenantOwnershipLifecycleCommand
from tools.eos.auth.tenant_ownership_verifier import (
    TenantOwnershipOperation,
    TenantOwnershipVerificationRequest,
    VerifiedTenantOwnershipEvidence,
)

VERSION = "v1.0.0-EOS-ATOMIC-TENANT-OWNER-GENESIS"
TENANT_OWNER_ROLE_ID = "TENANT_OWNER"
TENANT_OWNER_BUSINESS_ROLE = "tenant_owner"


class TenantOwnerGenesisProvisioningError(RuntimeError):
    """Bounded failure; caller-owned transaction must roll back."""


@dataclass(frozen=True, slots=True)
class TenantOwnerGenesisResult:
    tenant: Any
    membership: TenantMembershipAuthority
    authorization_role: RoleAssignmentAuthority
    business_role: TenantBusinessRoleAuthority
    ownership_revision: int


class TenantOwnerGenesisProvisioningCommand:
    """Atomically provision tenant authority after independent evidence verification."""

    def __init__(
        self,
        *,
        lifecycle: TenantOwnershipLifecycleCommand,
        tenant_create: Callable[..., Mapping[str, Any]],
    ) -> None:
        if lifecycle is None or not callable(tenant_create):
            raise TenantOwnerGenesisProvisioningError("GENESIS_DEPENDENCIES_REQUIRED")
        self._lifecycle = lifecycle
        self._tenant_create = tenant_create

    @staticmethod
    def _require_active_transaction(session: Any) -> None:
        marker = getattr(session, "in_transaction", None) if session is not None else None
        try:
            active = marker() if callable(marker) else marker
        except (AttributeError, TypeError) as error:
            raise TenantOwnerGenesisProvisioningError("ACTIVE_CALLER_TRANSACTION_REQUIRED") from error
        if active is not True:
            raise TenantOwnerGenesisProvisioningError("ACTIVE_CALLER_TRANSACTION_REQUIRED")

    def prepare(
        self, request: TenantOwnershipVerificationRequest
    ) -> VerifiedTenantOwnershipEvidence:
        """Verify issuer evidence before any tenant transaction is opened.

        Authentication proves the principal's login only. This explicit
        pre-transaction phase obtains the independent ownership result and
        cannot create tenant or IAM state.
        """
        if type(request) is not TenantOwnershipVerificationRequest:
            raise TenantOwnerGenesisProvisioningError("VERIFICATION_REQUEST_REQUIRED")
        if request.operation is not TenantOwnershipOperation.TENANT_GENESIS:
            raise TenantOwnerGenesisProvisioningError("TENANT_GENESIS_REQUEST_REQUIRED")
        # Preserve the verifier's stable denial code at the orchestration boundary.
        evidence = self._lifecycle.prepare(request)
        if type(evidence) is not VerifiedTenantOwnershipEvidence or evidence.request != request:
            raise TenantOwnerGenesisProvisioningError("VERIFIED_OWNERSHIP_EVIDENCE_REQUIRED")
        return evidence

    def execute(
        self,
        *,
        request: TenantOwnershipVerificationRequest,
        evidence: VerifiedTenantOwnershipEvidence,
        actor_principal_id: str,
        command_id: str,
        tenant_payload: Mapping[str, Any],
        database: Any,
        session: Any,
    ) -> TenantOwnerGenesisResult:
        """Create all genesis records in one caller-owned Mongo transaction."""
        self._require_active_transaction(session)
        if request.operation is not TenantOwnershipOperation.TENANT_GENESIS:
            raise TenantOwnerGenesisProvisioningError("TENANT_GENESIS_REQUEST_REQUIRED")
        if type(evidence) is not VerifiedTenantOwnershipEvidence or evidence.request != request:
            raise TenantOwnerGenesisProvisioningError("VERIFIED_OWNERSHIP_EVIDENCE_REQUIRED")
        if actor_principal_id != request.principal_id:
            raise TenantOwnerGenesisProvisioningError("ACTOR_PRINCIPAL_SCOPE_MISMATCH")
        if not isinstance(command_id, str) or not command_id or command_id != command_id.strip():
            raise TenantOwnerGenesisProvisioningError("COMMAND_ID_INVALID")
        if not isinstance(tenant_payload, Mapping) or database is None:
            raise TenantOwnerGenesisProvisioningError("GENESIS_INPUT_INVALID")

        payload = dict(tenant_payload)
        supplied_tenant_id = payload.get("tenant_id")
        if supplied_tenant_id is not None and supplied_tenant_id != request.tenant_id:
            raise TenantOwnerGenesisProvisioningError("TENANT_ID_SCOPE_MISMATCH")
        payload["tenant_id"] = request.tenant_id

        tenant_result = self._tenant_create(payload, session=session)
        if not isinstance(tenant_result, Mapping) or tenant_result.get("success") is not True:
            raise TenantOwnerGenesisProvisioningError("TENANT_REGISTRY_CREATE_FAILED")
        tenant = tenant_result.get("tenant")
        if tenant is None or getattr(tenant, "tenant_id", None) != request.tenant_id:
            raise TenantOwnerGenesisProvisioningError("TENANT_REGISTRY_SCOPE_MISMATCH")

        ownership_event = self._lifecycle.execute(
            request=request, evidence=evidence, actor_principal_id=actor_principal_id,
            command_id=command_id, expected_revision=0, session=session,
        )
        if (
            ownership_event.tenant_id != request.tenant_id
            or ownership_event.legal_entity_reference != request.legal_entity_reference
            or ownership_event.principal_id != request.principal_id
            or ownership_event.operation is not request.operation
            or ownership_event.command_id != command_id
            or ownership_event.revision != 1
        ):
            raise TenantOwnerGenesisProvisioningError("OWNERSHIP_GENESIS_RESULT_MISMATCH")

        membership = TenantMembershipAuthority(
            request.principal_id, request.tenant_id, TenantMembershipStatus.ACTIVE, 0
        )
        TenantMembershipRepository.insert(membership, session=session)

        authorization_role = RoleAssignmentAuthority(
            request.principal_id, request.tenant_id, TENANT_OWNER_ROLE_ID,
            RoleAssignmentStatus.ACTIVE, 0,
        )
        RoleAssignmentRepository.insert(authorization_role, session=session)

        existing = TenantBusinessRoleRepository.resolve_all(
            request.principal_id, request.tenant_id, session=session
        )
        if any(item.business_role == TENANT_OWNER_BUSINESS_ROLE for item in existing):
            raise TenantOwnerGenesisProvisioningError("TENANT_OWNER_CAPACITY_ALREADY_EXISTS")

        business_role = TenantBusinessRoleAuthority(
            principal_id=request.principal_id, tenant_id=request.tenant_id,
            business_role=TENANT_OWNER_BUSINESS_ROLE, status=TenantBusinessRoleStatus.ACTIVE,
            revision=0, effective_at=request.evaluated_at, revoked_at=None,
        )
        TenantBusinessRoleRepository.record_capacity_revision(
            business_role, expected_revision=None, database=database, session=session
        )
        return TenantOwnerGenesisResult(
            tenant, membership, authorization_role, business_role, ownership_event.revision
        )


__all__ = [
    "VERSION", "TENANT_OWNER_ROLE_ID", "TENANT_OWNER_BUSINESS_ROLE",
    "TenantOwnerGenesisProvisioningError", "TenantOwnerGenesisResult",
    "TenantOwnerGenesisProvisioningCommand",
]
