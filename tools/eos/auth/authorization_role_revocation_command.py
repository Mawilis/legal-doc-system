"""WILSY OS governed authorization-role revocation command.

TITLE: Governed Authorization Role Revocation Command
VERSION: v1.0.0-P1-R3C-G1-GOVERNED-AUTHORIZATION-ROLE-REVOCATION-COMMAND
AUTHORITY: Wilsy OS Core Governance / Sovereign IAM Design
EPITOME: Compose replay-first current authorization, exact target validation,
         pure revocation policy, authorization evidence, assignment CAS, and
         immutable revocation evidence in one caller-owned transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/authorization_role_revocation_command.py
COLLABORATION / OWNERSHIP: The command composes certified IAM authorities but
                            owns none of their persistence or policy truth.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.0.0-P1-R3C-G1 establishes replay-before-authorization, complete
           pre-write validation, ordered three-write composition, deterministic
           dependency injection, and fail-closed ordinary-role boundaries.
COMPLIANCE: NIST privileged-access lifecycle principles; POPIA section 19;
            GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque bounded identifiers, exact tenant scope,
                             deterministic SHA3-512 subject evidence, no PII.
TENANT BOUNDARY: Actor, target, role assignment, authorization evidence, and
                 revocation evidence are bound to one explicit tenant.
AUTHORITY BOUNDARY: IAM orchestration only. Historic evidence is not current
                    authority; canonical tenant authorization is re-proved for
                    every new mutation. No root, break-glass, or JIT lifecycle.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial
                              execution and settlement.
TRANSACTION BOUNDARY: Caller owns active session, transaction, commit, abort,
                      retry, and uncertain-commit reconciliation.
FAIL-CLOSED DECLARATION: Invalid input, replay divergence, authorization denial,
                         target drift, policy denial, CAS loss, and evidence
                         failure propagate without a success claim.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha3_512
import json
from typing import Any, Callable, Final, NoReturn

from tools.eos.auth.authorization_role_revocation_evidence import (
    AuthorizationRoleRevocationEvidence,
)
from tools.eos.auth.authorization_role_revocation_policy import (
    ENTERPRISE_ADMIN,
    ROLE_REVOKE_OPERATION,
    AuthorizationRoleRevocationDecision,
    evaluate_authorization_role_revocation,
)
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_authorization_decision_evidence import (
    TenantAuthorizationDecisionEvidence,
)


VERSION: Final[str] = "v1.0.0-P1-R3C-G1-GOVERNED-AUTHORIZATION-ROLE-REVOCATION-COMMAND"
OPERATION: Final[str] = ROLE_REVOKE_OPERATION
PERMISSION: Final[str] = "tenant:role_assignment:write"


class AuthorizationRoleRevocationCommandError(RuntimeError):
    """Base bounded command failure containing one stable non-secret code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class AuthorizationRoleRevocationCommandTransactionRequiredError(
    AuthorizationRoleRevocationCommandError
):
    """Caller omitted an already-active transaction."""


class AuthorizationRoleRevocationCommandReplayConflictError(
    AuthorizationRoleRevocationCommandError
):
    """Historic idempotency identity binds divergent caller material."""


class AuthorizationRoleRevocationCommandAuthorizationDeniedError(
    AuthorizationRoleRevocationCommandError
):
    """Current canonical authorization did not permit ordinary revocation."""


class AuthorizationRoleRevocationCommandTargetInvalidError(
    AuthorizationRoleRevocationCommandError
):
    """Target assignment is absent, inactive, mismatched, or stale."""


class AuthorizationRoleRevocationCommandPolicyDeniedError(
    AuthorizationRoleRevocationCommandError
):
    """Pure ordinary-role revocation policy denied the requested edge."""


class AuthorizationRoleRevocationResultState(StrEnum):
    """Closed successful outcomes without partial or uncertain success."""

    NEWLY_REVOKED = "NEWLY_REVOKED"
    EXACT_REPLAY = "EXACT_REPLAY"


@dataclass(frozen=True, slots=True)
class AuthorizationRoleRevocationResult:
    """Immutable successful command result.

    On exact replay, ``resulting_role_assignment`` is a historical projection
    derived from the immutable revocation evidence. It is not a current-authority
    assertion and causes no persistence read or mutation.
    """

    state: AuthorizationRoleRevocationResultState
    revocation_evidence: AuthorizationRoleRevocationEvidence
    resulting_role_assignment: RoleAssignmentAuthority


def _raise(error_type: type[AuthorizationRoleRevocationCommandError], code: str) -> NoReturn:
    """Raise one bounded command error without leaking dependency material."""
    raise error_type(code)


def _active_transaction(session: Any) -> Any:
    """Require the caller's active transaction before any persistence operation."""
    if session is None:
        _raise(AuthorizationRoleRevocationCommandTransactionRequiredError, "ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        _raise(AuthorizationRoleRevocationCommandTransactionRequiredError, "ACTIVE_TRANSACTION_REQUIRED")
    if active is not True:
        _raise(AuthorizationRoleRevocationCommandTransactionRequiredError, "ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identifier(name: str, value: object) -> str:
    """Require one exact bounded identifier without normalization or inference."""
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 256:
        _raise(AuthorizationRoleRevocationCommandTargetInvalidError, f"{name.upper()}_INVALID")
    return value


def _expected_revision(value: object) -> int:
    """Require one non-negative, non-boolean expected revision."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _raise(AuthorizationRoleRevocationCommandTargetInvalidError, "EXPECTED_TARGET_ASSIGNMENT_REVISION_INVALID")
    return value


def _subject_material(assignment: RoleAssignmentAuthority) -> tuple[str, str]:
    """Bind authorization evidence to the exact validated target snapshot."""
    payload = {
        "principal_id": assignment.principal_id,
        "tenant_id": assignment.tenant_id,
        "role_id": assignment.role_id,
        "status": assignment.status.value,
        "revision": assignment.revision,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    reference = (
        f"role-assignment:{assignment.tenant_id}:{assignment.principal_id}:"
        f"{assignment.role_id}:revision:{assignment.revision}"
    )
    return reference, sha3_512(canonical).hexdigest()


def _historic_projection(
    evidence: AuthorizationRoleRevocationEvidence,
) -> RoleAssignmentAuthority:
    """Project the evidenced historical CAS result without asserting currentness."""
    return RoleAssignmentAuthority(
        principal_id=evidence.target_principal_id,
        tenant_id=evidence.tenant_id,
        role_id=evidence.target_role_id,
        status=RoleAssignmentStatus.REVOKED,
        revision=evidence.target_assignment_result_revision,
    )


class AuthorizationRoleRevocationCommand:
    """Replay-first ordinary authorization-role revocation orchestration.

    Dependencies are explicit. The command creates no client, session,
    transaction, retry loop, transport surface, or alternate authority path.
    """

    def __init__(
        self,
        *,
        principal_repository: Any,
        membership_repository: Any,
        role_assignment_repository: Any,
        business_role_repository: Any,
        role_assignment_collection: Any,
        authorization_evidence_registry: Any,
        revocation_evidence_registry: Any,
        clock: Callable[[], datetime],
        revocation_id_factory: Callable[[], str],
        authorization: Callable[..., TenantAuthorizationDecision] = authorize_tenant_operation,
        revocation_policy: Callable[..., AuthorizationRoleRevocationDecision] = evaluate_authorization_role_revocation,
        workforce_relationship_collection: Any = None,
    ) -> None:
        """Bind certified authorities and deterministic factories without I/O."""
        dependencies = (
            principal_repository,
            membership_repository,
            role_assignment_repository,
            business_role_repository,
            role_assignment_collection,
            authorization_evidence_registry,
            revocation_evidence_registry,
            clock,
            revocation_id_factory,
            authorization,
            revocation_policy,
        )
        if any(dependency is None for dependency in dependencies):
            _raise(AuthorizationRoleRevocationCommandTargetInvalidError, "COMMAND_DEPENDENCY_REQUIRED")
        self._principal_repository = principal_repository
        self._membership_repository = membership_repository
        self._role_assignment_repository = role_assignment_repository
        self._business_role_repository = business_role_repository
        self._role_assignment_collection = role_assignment_collection
        self._authorization_evidence_registry = authorization_evidence_registry
        self._revocation_evidence_registry = revocation_evidence_registry
        self._clock = clock
        self._revocation_id_factory = revocation_id_factory
        self._authorization = authorization
        self._revocation_policy = revocation_policy
        self._workforce_relationship_collection = workforce_relationship_collection

    def execute(
        self,
        *,
        actor_principal_id: str,
        tenant_id: str,
        target_principal_id: str,
        target_role_id: str,
        expected_target_assignment_revision: int,
        reason_reference: str,
        idempotency_key: str,
        session: Any,
    ) -> AuthorizationRoleRevocationResult:
        """Execute one governed revocation or return one exact historic replay.

        The caller owns transaction lifecycle and whole-transaction retry. All
        dependency reads and ordered writes receive the exact caller session.
        Revocation-evidence failure is propagated so the caller can abort.
        """
        tx = _active_transaction(session)
        actor = _identifier("actor_principal_id", actor_principal_id)
        tenant = _identifier("tenant_id", tenant_id)
        target_principal = _identifier("target_principal_id", target_principal_id)
        target_role = _identifier("target_role_id", target_role_id)
        expected_revision = _expected_revision(expected_target_assignment_revision)
        reason = _identifier("reason_reference", reason_reference)
        replay_key = _identifier("idempotency_key", idempotency_key)

        historic = self._revocation_evidence_registry.get_by_tenant_idempotency(
            tenant_id=tenant,
            idempotency_key=replay_key,
            session=tx,
        )
        if historic is not None:
            requested = (
                actor,
                tenant,
                target_principal,
                target_role,
                expected_revision,
                reason,
                replay_key,
            )
            durable = (
                historic.actor_principal_id,
                historic.tenant_id,
                historic.target_principal_id,
                historic.target_role_id,
                historic.target_assignment_prior_revision,
                historic.reason_reference,
                historic.idempotency_key,
            )
            if requested != durable:
                _raise(AuthorizationRoleRevocationCommandReplayConflictError, "IDEMPOTENCY_DIVERGENT_REPLAY")
            return AuthorizationRoleRevocationResult(
                state=AuthorizationRoleRevocationResultState.EXACT_REPLAY,
                revocation_evidence=historic,
                resulting_role_assignment=_historic_projection(historic),
            )

        decision = self._authorization(
            principal_id=actor,
            tenant_id=tenant,
            permission_id=PERMISSION,
            operation=OPERATION,
            principal_repository=self._principal_repository,
            membership_repository=self._membership_repository,
            role_assignment_repository=self._role_assignment_repository,
            business_role_repository=self._business_role_repository,
            session=tx,
            workforce_relationship_collection=self._workforce_relationship_collection,
        )
        if (
            type(decision) is not TenantAuthorizationDecision
            or not decision.authorized
            or decision.authorization_role != ENTERPRISE_ADMIN
        ):
            _raise(AuthorizationRoleRevocationCommandAuthorizationDeniedError, "CURRENT_AUTHORIZATION_DENIED")

        try:
            target = self._role_assignment_repository.resolve(
                target_principal,
                tenant,
                target_role,
                self._role_assignment_collection,
                session=tx,
            )
        except Exception as error:
            if isinstance(error, AuthorizationRoleRevocationCommandError):
                raise
            raise AuthorizationRoleRevocationCommandTargetInvalidError("TARGET_ASSIGNMENT_UNAVAILABLE") from error
        if (
            type(target) is not RoleAssignmentAuthority
            or target.principal_id != target_principal
            or target.tenant_id != tenant
            or target.role_id != target_role
            or target.status is not RoleAssignmentStatus.ACTIVE
            or target.revision != expected_revision
        ):
            _raise(AuthorizationRoleRevocationCommandTargetInvalidError, "TARGET_ASSIGNMENT_NOT_CURRENT")

        policy = self._revocation_policy(
            operation=OPERATION,
            actor_principal_id=actor,
            actor_tenant_id=tenant,
            actor_authorization_role=decision.authorization_role,
            target_principal_id=target.principal_id,
            target_tenant_id=target.tenant_id,
            target_authorization_role=target.role_id,
            target_assignment_status=target.status,
        )
        if type(policy) is not AuthorizationRoleRevocationDecision or not policy.allowed:
            _raise(AuthorizationRoleRevocationCommandPolicyDeniedError, "REVOCATION_POLICY_DENIED")

        subject_reference, subject_fingerprint = _subject_material(target)
        authorization_evidence = self._authorization_evidence_registry.issue(
            tenant_id=tenant,
            principal_id=actor,
            operation=OPERATION,
            permission=PERMISSION,
            subject_reference=subject_reference,
            subject_evidence_fingerprint=subject_fingerprint,
            idempotency_key=f"role-revocation-authorization:{replay_key}",
            session=tx,
        )
        if type(authorization_evidence) is not TenantAuthorizationDecisionEvidence:
            _raise(AuthorizationRoleRevocationCommandAuthorizationDeniedError, "AUTHORIZATION_EVIDENCE_INVALID")

        revoked = RoleAssignmentAuthority(
            principal_id=target.principal_id,
            tenant_id=target.tenant_id,
            role_id=target.role_id,
            status=RoleAssignmentStatus.REVOKED,
            revision=target.revision + 1,
        )
        persisted_assignment = self._role_assignment_repository.compare_and_swap(
            revoked,
            expected_revision,
            self._role_assignment_collection,
            session=tx,
        )
        if persisted_assignment != revoked:
            _raise(AuthorizationRoleRevocationCommandTargetInvalidError, "ROLE_ASSIGNMENT_CAS_RESULT_INVALID")

        evidence = AuthorizationRoleRevocationEvidence(
            revocation_id=_identifier("revocation_id", self._revocation_id_factory()),
            tenant_id=tenant,
            actor_principal_id=actor,
            target_principal_id=target.principal_id,
            target_role_id=target.role_id,
            target_assignment_prior_revision=target.revision,
            target_assignment_result_revision=revoked.revision,
            operation=OPERATION,
            reason_reference=reason,
            authorization_evidence_reference=authorization_evidence.authorization_evidence_reference,
            authorization_evidence_fingerprint=authorization_evidence.authorization_evidence_fingerprint,
            idempotency_key=replay_key,
            revoked_at=self._clock(),
        )
        persisted_evidence = self._revocation_evidence_registry.create_or_replay(
            evidence,
            session=tx,
        )
        if persisted_evidence != evidence:
            _raise(AuthorizationRoleRevocationCommandTargetInvalidError, "REVOCATION_EVIDENCE_RESULT_INVALID")
        return AuthorizationRoleRevocationResult(
            state=AuthorizationRoleRevocationResultState.NEWLY_REVOKED,
            revocation_evidence=persisted_evidence,
            resulting_role_assignment=persisted_assignment,
        )


__all__ = [
    "VERSION",
    "OPERATION",
    "PERMISSION",
    "AuthorizationRoleRevocationCommand",
    "AuthorizationRoleRevocationCommandError",
    "AuthorizationRoleRevocationCommandTransactionRequiredError",
    "AuthorizationRoleRevocationCommandReplayConflictError",
    "AuthorizationRoleRevocationCommandAuthorizationDeniedError",
    "AuthorizationRoleRevocationCommandTargetInvalidError",
    "AuthorizationRoleRevocationCommandPolicyDeniedError",
    "AuthorizationRoleRevocationResultState",
    "AuthorizationRoleRevocationResult",
]

# ARTIFACT: authorization_role_revocation_command.py
# VERSION: v1.0.0-P1-R3C-G1-GOVERNED-AUTHORIZATION-ROLE-REVOCATION-COMMAND
# AUTHORITY BOUNDARY: replay-first ordinary-role revocation orchestration only; no root, recovery, break-glass, JIT, transport, session revocation, or finance
# TENANT POSTURE: exact actor, target, role, assignment, authorization evidence, and revocation evidence tenant binding
# FAIL-CLOSED POSTURE: transaction absence, replay divergence, denial, target drift, policy denial, CAS loss, and evidence failure reject
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
