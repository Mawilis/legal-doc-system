"""
TITLE:
    WILSY OS Privileged Activation Revocation Command Service

VERSION:
    v1.0.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-SERVICE

AUTHORITY:
    Wilsy OS IAM P6 explicit supervisory privileged-activation revocation
    command authority.

EPITOME:
    Revoke one exact current privileged activation only when a distinct
    supervising principal currently possesses the canonical SYSTEM permission
    ``privileged_activation:revoke`` and the supplied immutable command evidence
    exactly binds that current permission assignment lineage and activation.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/
    privileged_activation_revocation_command_service.py

COLLABORATION / OWNERSHIP:
    P6 composes the sealed current SYSTEM-permission possession resolver,
    immutable P6 command evidence and registry, and sealed P4 privileged
    activation registry. It creates no parallel activation or permission truth.

CERTIFICATION / UPDATE DATE:
    2026-10-15

CHANGELOG:
    v1.0.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-SERVICE
        Initial explicit supervisory privileged-activation revocation service
        with current actor permission recheck, exact assignment lineage,
        exact target binding, durable replay and caller-owned transaction
        atomicity.

COMPLIANCE:
    Fail closed; explicit SYSTEM permission authority; immutable durable command
    evidence; deterministic replay; no role-derived authority; exact scope;
    caller-owned Mongo transaction propagation.

SECURITY / PRIVACY POSTURE:
    Consumes opaque identifiers, cryptographic lineage fingerprints and opaque
    reason references only. No credentials, proof secrets, raw review narrative
    or financial execution truth are represented.

TENANT BOUNDARY:
    The target activation's existing scope is authoritative. Tenant-scoped
    evidence must match that exact tenant; platform-root evidence requires no
    tenant. Cross-scope rebinding fails closed.

AUTHORITY BOUNDARY:
    Supervisory revocation of one exact privileged activation only. No
    permission assignment, role assignment, eligibility creation, assurance
    creation, activation issuance, break-glass, HTTP or financial authority.

FINANCIAL AUTHORITY BOUNDARY:
    NONE.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from pymongo.client_session import ClientSession

from tools.eos.auth.current_system_permission_possession import (
    CurrentSystemPermissionPossessionError,
    CurrentSystemPermissionPossessionResolver,
)
from tools.eos.auth.privileged_activation import (
    PrivilegedActivation,
    PrivilegedActivationError,
    PrivilegedActivationStatus,
)
from tools.eos.auth.privileged_activation_registry import (
    PrivilegedActivationConflictError,
    PrivilegedActivationNotFoundError,
    PrivilegedActivationPersistedInvalidError,
    PrivilegedActivationPersistenceError,
    PrivilegedActivationRegistry,
    PrivilegedActivationRegistryError,
    PrivilegedActivationTransactionRequiredError,
)
from tools.eos.auth.privileged_activation_revocation_command_evidence import (
    PRIVILEGED_ACTIVATION_REVOKE_PERMISSION,
    PrivilegedActivationRevocationCommandEvidence,
)
from tools.eos.auth.privileged_activation_revocation_command_evidence_registry import (
    PrivilegedActivationRevocationCommandEvidenceConflictError,
    PrivilegedActivationRevocationCommandEvidencePersistedInvalidError,
    PrivilegedActivationRevocationCommandEvidenceRegistry,
    PrivilegedActivationRevocationCommandEvidenceRegistryError,
    PrivilegedActivationRevocationCommandEvidenceTransactionRequiredError,
)
from tools.eos.auth.privileged_eligibility import (
    PrivilegedTargetClass,
)


VERSION: Final[str] = (
    "v1.0.0-P6-PRIVILEGED-ACTIVATION-"
    "REVOCATION-COMMAND-SERVICE"
)


class PrivilegedActivationRevocationCommandError(
    RuntimeError
):
    """Structured fail-closed P6 supervisory revocation failure."""

    def __init__(
        self,
        code: str,
    ) -> None:
        """Create one stable institutional command-boundary error."""

        super().__init__(
            code
        )
        self.code = code


@dataclass(
    frozen=True,
    slots=True,
)
class PrivilegedActivationRevocationCommandResult:
    """Durable result of one exact P6 supervisory revocation command.

    The result contains immutable command evidence plus the terminal privileged
    activation revision. It represents no authority beyond the completed
    revocation and performs no persistence itself.
    """

    evidence: PrivilegedActivationRevocationCommandEvidence
    activation: PrivilegedActivation


class PrivilegedActivationRevocationCommandService:
    """Execute one explicit P6 supervisory activation-revocation command.

    The caller owns and starts the transaction. This service never starts,
    commits, aborts or retries transactions. Every read and write receives the
    exact caller session.

    New commands require:
      - immutable P6 command evidence;
      - current actor possession of ``privileged_activation:revoke``;
      - exact current permission-assignment lineage;
      - one exact ACTIVE/current target activation;
      - actor and target principal separation;
      - exact target identity and tenant/class scope.

    Exact durable replay remains available after the target becomes terminal,
    but the actor's revoke permission is still revalidated at replay time.
    """

    def __init__(
        self,
        *,
        possession_resolver: CurrentSystemPermissionPossessionResolver,
        activation_registry: PrivilegedActivationRegistry,
        evidence_registry:
            PrivilegedActivationRevocationCommandEvidenceRegistry,
    ) -> None:
        """Bind sealed currentness and persistence dependencies."""

        if (
            type(possession_resolver)
            is not CurrentSystemPermissionPossessionResolver
        ):
            raise PrivilegedActivationRevocationCommandError(
                "POSSESSION_RESOLVER_REQUIRED"
            )

        if (
            type(activation_registry)
            is not PrivilegedActivationRegistry
        ):
            raise PrivilegedActivationRevocationCommandError(
                "ACTIVATION_REGISTRY_REQUIRED"
            )

        if (
            type(evidence_registry)
            is not PrivilegedActivationRevocationCommandEvidenceRegistry
        ):
            raise PrivilegedActivationRevocationCommandError(
                "EVIDENCE_REGISTRY_REQUIRED"
            )

        self._possession = possession_resolver
        self._activations = activation_registry
        self._evidence = evidence_registry

    @staticmethod
    def _require_transaction(
        session: ClientSession,
    ) -> None:
        """Require the already-active caller-owned transaction."""

        if (
            session is None
            or getattr(
                session,
                "in_transaction",
                False,
            )
            is not True
        ):
            raise PrivilegedActivationRevocationCommandError(
                "ACTIVE_TRANSACTION_REQUIRED"
            )

    @staticmethod
    def _target_class(
        evidence: PrivilegedActivationRevocationCommandEvidence,
    ) -> PrivilegedTargetClass:
        """Return the exact sealed target-class enum or fail closed."""

        try:
            return PrivilegedTargetClass(
                evidence.target_class
            )
        except ValueError as error:
            raise PrivilegedActivationRevocationCommandError(
                "TARGET_CLASS_INVALID"
            ) from error

    @staticmethod
    def _validate_assignment_lineage(
        evidence: PrivilegedActivationRevocationCommandEvidence,
        assignment: object,
    ) -> None:
        """Require exact equality with the live SYSTEM assignment lineage."""

        if (
            getattr(
                assignment,
                "assignment_id",
                None,
            )
            != evidence.actor_permission_assignment_id
            or getattr(
                assignment,
                "principal_id",
                None,
            )
            != evidence.actor_principal_id
            or getattr(
                assignment,
                "permission_id",
                None,
            )
            != PRIVILEGED_ACTIVATION_REVOKE_PERMISSION
            or getattr(
                assignment,
                "revision",
                None,
            )
            != evidence.actor_permission_assignment_revision
            or getattr(
                assignment,
                "assignment_fingerprint",
                None,
            )
            != evidence.actor_permission_assignment_fingerprint
        ):
            raise PrivilegedActivationRevocationCommandError(
                "ACTOR_PERMISSION_LINEAGE_MISMATCH"
            )

    @staticmethod
    def _validate_target_binding(
        evidence: PrivilegedActivationRevocationCommandEvidence,
        activation: PrivilegedActivation,
    ) -> PrivilegedTargetClass:
        """Require immutable evidence to bind the exact activation target."""

        expected_class = (
            PrivilegedActivationRevocationCommandService
            ._target_class(
                evidence
            )
        )

        if (
            activation.activation_id
            != evidence.target_activation_id
        ):
            raise PrivilegedActivationRevocationCommandError(
                "TARGET_ACTIVATION_ID_MISMATCH"
            )

        if (
            activation.principal_id
            != evidence.target_principal_id
        ):
            raise PrivilegedActivationRevocationCommandError(
                "TARGET_PRINCIPAL_MISMATCH"
            )

        if (
            activation.target_class
            is not expected_class
        ):
            raise PrivilegedActivationRevocationCommandError(
                "TARGET_CLASS_MISMATCH"
            )

        if (
            activation.tenant_id
            != evidence.target_tenant_id
        ):
            raise PrivilegedActivationRevocationCommandError(
                "TARGET_TENANT_SCOPE_MISMATCH"
            )

        if (
            evidence.actor_principal_id
            == activation.principal_id
        ):
            raise PrivilegedActivationRevocationCommandError(
                "SELF_REVOCATION_FORBIDDEN"
            )

        return expected_class

    @staticmethod
    def _require_new_command_currentness(
        evidence: PrivilegedActivationRevocationCommandEvidence,
        activation: PrivilegedActivation,
        target_class: PrivilegedTargetClass,
    ) -> None:
        """Require ACTIVE half-open currentness for a new revocation command."""

        if (
            activation.status
            is not PrivilegedActivationStatus.ACTIVE
        ):
            raise PrivilegedActivationRevocationCommandError(
                "TARGET_ACTIVATION_NOT_ACTIVE"
            )

        if not activation.is_current(
            at=evidence.authorized_at,
            tenant_id=activation.tenant_id,
            principal_id=activation.principal_id,
            privileged_role_id=activation.privileged_role_id,
            target_class=target_class,
        ):
            raise PrivilegedActivationRevocationCommandError(
                "CURRENT_TARGET_ACTIVATION_REQUIRED"
            )

    @staticmethod
    def _validate_exact_replay_activation(
        evidence: PrivilegedActivationRevocationCommandEvidence,
        activation: PrivilegedActivation,
    ) -> None:
        """Require one exact terminal activation corresponding to durable replay."""

        if (
            activation.status
            is not PrivilegedActivationStatus.REVOKED
            or activation.revoked_at
            != evidence.authorized_at
        ):
            raise PrivilegedActivationRevocationCommandError(
                "DURABLE_REPLAY_TARGET_STATE_INVALID"
            )

    def revoke(
        self,
        evidence: PrivilegedActivationRevocationCommandEvidence,
        *,
        session: ClientSession,
    ) -> PrivilegedActivationRevocationCommandResult:
        """Revoke one exact current activation or return its exact replay.

        The actor's exact current P6 permission is re-resolved on every call,
        including durable replay. New commands persist immutable P6 evidence and
        the terminal P4 activation successor in the same caller-owned active
        transaction.
        """

        self._require_transaction(
            session
        )

        if not isinstance(
            evidence,
            PrivilegedActivationRevocationCommandEvidence,
        ):
            raise PrivilegedActivationRevocationCommandError(
                "REVOCATION_COMMAND_EVIDENCE_REQUIRED"
            )

        if (
            evidence.actor_permission_id
            != PRIVILEGED_ACTIVATION_REVOKE_PERMISSION
        ):
            raise PrivilegedActivationRevocationCommandError(
                "REVOCATION_PERMISSION_REQUIRED"
            )

        try:
            assignment = self._possession.resolve(
                principal_id=(
                    evidence.actor_principal_id
                ),
                permission_id=(
                    PRIVILEGED_ACTIVATION_REVOKE_PERMISSION
                ),
                session=session,
            )
        except CurrentSystemPermissionPossessionError as error:
            raise PrivilegedActivationRevocationCommandError(
                "CURRENT_REVOCATION_AUTHORITY_UNAVAILABLE"
            ) from error

        if assignment is None:
            raise PrivilegedActivationRevocationCommandError(
                "CURRENT_REVOCATION_AUTHORITY_REQUIRED"
            )

        self._validate_assignment_lineage(
            evidence,
            assignment,
        )

        try:
            history = self._activations.get_history(
                evidence.target_activation_id,
                session=session,
            )
        except (
            PrivilegedActivationPersistedInvalidError,
            PrivilegedActivationPersistenceError,
            PrivilegedActivationRegistryError,
        ) as error:
            raise PrivilegedActivationRevocationCommandError(
                "TARGET_ACTIVATION_CURRENTNESS_UNAVAILABLE"
            ) from error

        if not history:
            raise PrivilegedActivationRevocationCommandError(
                "TARGET_ACTIVATION_NOT_FOUND"
            )

        target = history[-1]

        target_class = self._validate_target_binding(
            evidence,
            target,
        )

        try:
            prior_evidence = (
                self._evidence
                .get_by_actor_idempotency(
                    actor_principal_id=(
                        evidence.actor_principal_id
                    ),
                    idempotency_key=(
                        evidence.idempotency_key
                    ),
                    session=session,
                )
            )
        except (
            PrivilegedActivationRevocationCommandEvidencePersistedInvalidError,
            PrivilegedActivationRevocationCommandEvidenceRegistryError,
        ) as error:
            raise PrivilegedActivationRevocationCommandError(
                "DURABLE_COMMAND_EVIDENCE_UNAVAILABLE"
            ) from error

        if prior_evidence is not None:
            if prior_evidence != evidence:
                raise PrivilegedActivationRevocationCommandError(
                    "DIVERGENT_IDEMPOTENCY_REPLAY"
                )

            self._validate_exact_replay_activation(
                evidence,
                target,
            )

            return PrivilegedActivationRevocationCommandResult(
                evidence=prior_evidence,
                activation=target,
            )

        self._require_new_command_currentness(
            evidence,
            target,
            target_class,
        )

        try:
            revoked = target.revoke(
                revoked_at=evidence.authorized_at
            )
        except PrivilegedActivationError as error:
            raise PrivilegedActivationRevocationCommandError(
                "TARGET_ACTIVATION_REVOCATION_INVALID"
            ) from error

        try:
            durable_evidence = (
                self._evidence
                .create_or_replay(
                    evidence,
                    session=session,
                )
            )
        except (
            PrivilegedActivationRevocationCommandEvidenceTransactionRequiredError,
            PrivilegedActivationRevocationCommandEvidenceConflictError,
            PrivilegedActivationRevocationCommandEvidencePersistedInvalidError,
            PrivilegedActivationRevocationCommandEvidenceRegistryError,
        ) as error:
            raise PrivilegedActivationRevocationCommandError(
                "COMMAND_EVIDENCE_PERSISTENCE_FAILED"
            ) from error

        if durable_evidence != evidence:
            raise PrivilegedActivationRevocationCommandError(
                "COMMAND_EVIDENCE_PERSISTENCE_MISMATCH"
            )

        try:
            durable_activation = (
                self._activations
                .revoke_or_replay(
                    revoked,
                    revocation_idempotency_key=(
                        evidence.idempotency_key
                    ),
                    session=session,
                )
            )
        except (
            PrivilegedActivationTransactionRequiredError,
            PrivilegedActivationConflictError,
            PrivilegedActivationNotFoundError,
            PrivilegedActivationPersistedInvalidError,
            PrivilegedActivationPersistenceError,
            PrivilegedActivationRegistryError,
        ) as error:
            raise PrivilegedActivationRevocationCommandError(
                "ACTIVATION_REVOCATION_PERSISTENCE_FAILED"
            ) from error

        if durable_activation != revoked:
            raise PrivilegedActivationRevocationCommandError(
                "ACTIVATION_REVOCATION_PERSISTENCE_MISMATCH"
            )

        return PrivilegedActivationRevocationCommandResult(
            evidence=durable_evidence,
            activation=durable_activation,
        )


__all__ = [
    "VERSION",
    "PrivilegedActivationRevocationCommandError",
    "PrivilegedActivationRevocationCommandResult",
    "PrivilegedActivationRevocationCommandService",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: privileged_activation_revocation_command_service.py
# VERSION: v1.0.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-SERVICE
# AUTHORITY BOUNDARY: ONE EXACT SUPERVISORY PRIVILEGED-ACTIVATION REVOCATION ONLY
# TENANT POSTURE: TARGET ACTIVATION SCOPE IS AUTHORITATIVE; REBINDING FORBIDDEN
# FAIL-CLOSED POSTURE: CURRENT ACTOR PERMISSION + EXACT LINEAGE + TARGET + DURABLE EVIDENCE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
