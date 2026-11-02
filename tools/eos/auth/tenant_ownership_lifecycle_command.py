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

VERSION: Final[str] = "v1.1.0-ISSUE-300-TWO-PHASE-LIFECYCLE-COMMAND"


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


class TenantOwnershipTrustRootCurrentness(Protocol):
    """Read-only transaction-bound trust-root currentness authority."""

    def current(
        self, trust_root_reference: str, *, at: Any, session: Any
    ) -> object | None:
        """Return the exact current enrolled root or None when revoked/unknown."""
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
        trust_root_currentness: TenantOwnershipTrustRootCurrentness,
    ) -> None:
        if verifier is None or registry is None or transfer_actor_authorizer is None or genesis_request_authorizer is None or trust_root_currentness is None:
            raise TenantOwnershipLifecycleCommandError("LIFECYCLE_DEPENDENCY_REQUIRED")
        self._verifier = verifier
        self._registry = registry
        self._transfer_actor_authorizer = transfer_actor_authorizer
        self._genesis_request_authorizer = genesis_request_authorizer
        self._trust_root_currentness = trust_root_currentness

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

    def prepare(
        self, request: TenantOwnershipVerificationRequest
    ) -> VerifiedTenantOwnershipEvidence:
        """Run independent evidence/provider verification before opening a Mongo transaction."""
        if type(request) is not TenantOwnershipVerificationRequest:
            raise TenantOwnershipLifecycleCommandError("VERIFICATION_REQUEST_REQUIRED")
        try:
            evidence = self._verifier.verify(request)
        except TenantOwnershipVerificationError:
            raise
        if type(evidence) is not VerifiedTenantOwnershipEvidence:
            raise TenantOwnershipVerificationError("VERIFIED_OWNERSHIP_EVIDENCE_REQUIRED")
        if evidence.request != request:
            raise TenantOwnershipVerificationError("VERIFIED_OWNERSHIP_REQUEST_MISMATCH")
        return evidence

    def execute(
        self,
        *,
        request: TenantOwnershipVerificationRequest,
        evidence: VerifiedTenantOwnershipEvidence,
        actor_principal_id: str,
        command_id: str,
        expected_revision: int,
        session: Any,
    ) -> TenantOwnershipEvidenceEvent:
        """Revalidate mutable authority and append prepared evidence in caller transaction."""
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

        if type(evidence) is not VerifiedTenantOwnershipEvidence:
            raise TenantOwnershipVerificationError("VERIFIED_OWNERSHIP_EVIDENCE_REQUIRED")
        if evidence.request != request:
            raise TenantOwnershipVerificationError("VERIFIED_OWNERSHIP_REQUEST_MISMATCH")

        # Provider signatures are checked in prepare(); the authoritative
        # revocation/currentness state is re-read from Mongo inside this commit
        # transaction to close the preflight-to-commit race.
        issuer = evidence.issuer_authority
        issuer_root = self._trust_root_currentness.current(
            issuer.trust_root_reference, at=request.evaluated_at, session=session
        )
        if (
            issuer_root is None
            or getattr(issuer_root, "fingerprint", None) != issuer.trust_root_fingerprint
            or getattr(issuer_root, "key_id", None) != issuer.key_id
            or getattr(issuer_root, "key_revision", None) != issuer.key_revision
            or getattr(issuer_root, "authority_scope", None) != issuer.authority_scope
            or getattr(issuer_root, "issuer_identity", None) != issuer.issuer_identity
            or issuer.authority_scope != "TENANT_OWNERSHIP_ISSUER"
            or issuer.not_revoked is not True
        ):
            raise TenantOwnershipVerificationError("OWNERSHIP_ISSUER_TRUST_ROOT_NOT_CURRENT")
        if request.operation is TenantOwnershipOperation.GOVERNED_RECOVERY:
            recovery = evidence.recovery_authorization
            if recovery is None:
                raise TenantOwnershipVerificationError("GOVERNED_RECOVERY_AUTHORIZATION_REQUIRED")
            recovery_root = self._trust_root_currentness.current(
                recovery.trust_root_reference, at=request.evaluated_at, session=session
            )
            if (
                recovery_root is None
                or getattr(recovery_root, "fingerprint", None) != recovery.trust_root_fingerprint
                or getattr(recovery_root, "authority_scope", None) != recovery.authority_scope
                or getattr(recovery_root, "authority_scope", None) != "TENANT_OWNERSHIP_GOVERNED_RECOVERY"
                or getattr(recovery_root, "issuer_identity", None) != recovery.recovery_authority_identity
                or recovery.not_revoked is not True
            ):
                raise TenantOwnershipVerificationError("GOVERNED_RECOVERY_TRUST_ROOT_NOT_CURRENT")
        elif evidence.recovery_authorization is not None:
            raise TenantOwnershipVerificationError("UNEXPECTED_GOVERNED_RECOVERY_AUTHORIZATION")
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
    "TenantOwnershipTrustRootCurrentness",
]
