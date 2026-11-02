"""Fail-closed ownership lifecycle orchestration over canonical authorities.

This command composes the existing tenant ownership verifier and append-only
registry. It owns no Mongo transaction lifecycle, role/membership mutation,
HTTP transport, or independent legal authority.
"""
from __future__ import annotations

from typing import Any, Callable, Final, Protocol

from tools.eos.auth.tenant_ownership_evidence_registry import (
    TenantOwnershipCurrent,
    TenantOwnershipEvidenceEvent,
    TenantOwnershipEvidenceRegistry,
)
from tools.eos.auth.tenant_ownership_verifier import (
    TenantOwnershipEvidenceVerifier,
    TenantOwnershipOperation,
    TenantOwnershipVerificationError,
    TenantOwnershipVerificationRequest,
    VerifiedTenantOwnershipEvidence,
)

VERSION: Final[str] = "v1.0.0-ISSUE-300-OWNERSHIP-LIFECYCLE-COMMAND"


class TenantOwnershipLifecycleCommandError(RuntimeError):
    """Bounded lifecycle command denial."""


class TenantOwnershipGenesisRequestAuthorizer(Protocol):
    """Adapter to the existing deployment-rooted pretenant provisioner gate."""

    def authorize_pretenant_provisioner(
        self,
        *,
        principal_id: str,
        tenant_id: str,
        session: Any,
    ) -> object:
        """Return the canonical positive pretenant decision; never a caller Boolean."""
        ...


class TenantOwnershipTransferActorAuthorizer(Protocol):
    """Adapter to the canonical tenant IAM decision for ownership transfer."""

    def authorize_current_owner(
        self,
        *,
        principal_id: str,
        tenant_id: str,
        session: Any,
    ) -> object:
        """Return the canonical TenantAuthorizationDecision; never a caller Boolean."""
        ...


class TenantOwnershipLifecycleCommand:
    """Coordinate verification, current-owner admission and one atomic registry append.

    Transfer admission requires the actor to be the exact current owner and an
    injected adapter to return the canonical authorization decision. Recovery
    does not use ordinary tenant-admin or current-owner authority: its separate
    independent recovery proof is validated by the ownership verifier.
    """

    def __init__(
        self,
        *,
        verifier: TenantOwnershipEvidenceVerifier,
        registry: TenantOwnershipEvidenceRegistry,
        transfer_actor_authorizer: TenantOwnershipTransferActorAuthorizer,
        genesis_request_authorizer: TenantOwnershipGenesisRequestAuthorizer,
    ) -> None:
        if verifier is None or registry is None or transfer_actor_authorizer is None or genesis_request_authorizer is None:
            raise TenantOwnershipLifecycleCommandError("LIFECYCLE_DEPENDENCY_REQUIRED")
        self._verifier = verifier
        self._registry = registry
        self._transfer_actor_authorizer = transfer_actor_authorizer
        self._genesis_request_authorizer = genesis_request_authorizer

    @staticmethod
    def _active_transaction(session: Any) -> None:
        marker = getattr(session, "in_transaction", None) if session is not None else None
        try:
            active = marker() if callable(marker) else marker
        except (AttributeError, TypeError) as error:
            raise TenantOwnershipLifecycleCommandError("ACTIVE_TRANSACTION_REQUIRED") from error
        if active is not True:
            raise TenantOwnershipLifecycleCommandError("ACTIVE_TRANSACTION_REQUIRED")

    @staticmethod
    def _authorized(decision: object) -> bool:
        """Accept only the canonical positive decision shape, never truthy objects."""
        return getattr(decision, "authorized", None) is True

    def execute(
        self,
        *,
        request: TenantOwnershipVerificationRequest,
        actor_principal_id: str,
        command_id: str,
        expected_revision: int,
        session: Any,
    ) -> TenantOwnershipEvidenceEvent:
        """Verify one exact genesis, transfer or recovery and append in caller transaction."""
        self._active_transaction(session)
        if type(request) is not TenantOwnershipVerificationRequest:
            raise TenantOwnershipLifecycleCommandError("VERIFICATION_REQUEST_REQUIRED")
        if (
            not isinstance(actor_principal_id, str)
            or not actor_principal_id
            or actor_principal_id != actor_principal_id.strip()
        ):
            raise TenantOwnershipLifecycleCommandError("ACTOR_PRINCIPAL_INVALID")
        if request.operation is TenantOwnershipOperation.TENANT_GENESIS:
            pretenant_decision = self._genesis_request_authorizer.authorize_pretenant_provisioner(
                principal_id=actor_principal_id,
                tenant_id=request.tenant_id,
                session=session,
            )
            if not self._authorized(pretenant_decision):
                raise TenantOwnershipLifecycleCommandError("PRETENANT_PROVISIONER_AUTHORIZATION_DENIED")
        current = self._registry.current(tenant_id=request.tenant_id, session=session)
        if request.operation is TenantOwnershipOperation.TENANT_GENESIS:
            if current is not None or expected_revision != 0:
                raise TenantOwnershipLifecycleCommandError("TENANT_GENESIS_NOT_AVAILABLE")
        elif request.operation is TenantOwnershipOperation.OWNERSHIP_TRANSFER:
            self._require_current_owner(
                current=current,
                actor_principal_id=actor_principal_id,
                request=request,
                session=session,
            )
        elif request.operation is TenantOwnershipOperation.GOVERNED_RECOVERY:
            if type(expected_revision) is not int or expected_revision < 1:
                raise TenantOwnershipLifecycleCommandError("RECOVERY_HISTORY_REVISION_REQUIRED")
        else:
            raise TenantOwnershipLifecycleCommandError("OWNERSHIP_OPERATION_INVALID")

        try:
            evidence = self._verifier.verify(request)
        except TenantOwnershipVerificationError:
            raise
        if type(evidence) is not VerifiedTenantOwnershipEvidence:
            raise TenantOwnershipVerificationError(
                "VERIFIED_OWNERSHIP_EVIDENCE_REQUIRED"
            )
        if evidence.request != request:
            raise TenantOwnershipVerificationError("VERIFIED_OWNERSHIP_REQUEST_MISMATCH")
        return self._registry.append(
            evidence=evidence,
            command_id=command_id,
            expected_revision=expected_revision,
            session=session,
        )

    def _require_current_owner(
        self,
        *,
        current: TenantOwnershipCurrent | None,
        actor_principal_id: str,
        request: TenantOwnershipVerificationRequest,
        session: Any,
    ) -> None:
        if current is None:
            raise TenantOwnershipLifecycleCommandError("CURRENT_OWNER_REQUIRED")
        if current.principal_id != actor_principal_id:
            raise TenantOwnershipLifecycleCommandError("ONLY_CURRENT_OWNER_MAY_PROPOSE_TRANSFER")
        if current.tenant_id != request.tenant_id:
            raise TenantOwnershipLifecycleCommandError("TENANT_SCOPE_MISMATCH")
        decision = self._transfer_actor_authorizer.authorize_current_owner(
            principal_id=actor_principal_id,
            tenant_id=request.tenant_id,
            session=session,
        )
        if not self._authorized(decision):
            raise TenantOwnershipLifecycleCommandError("CURRENT_OWNER_TRANSFER_AUTHORIZATION_DENIED")


__all__ = [
    "VERSION",
    "TenantOwnershipLifecycleCommand",
    "TenantOwnershipLifecycleCommandError",
    "TenantOwnershipGenesisRequestAuthorizer",
    "TenantOwnershipTransferActorAuthorizer",
]
