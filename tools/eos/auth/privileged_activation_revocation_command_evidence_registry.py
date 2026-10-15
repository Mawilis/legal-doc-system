"""
TITLE:
    WILSY OS Privileged Activation Revocation Command Evidence Registry

VERSION:
    v1.0.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-EVIDENCE-REGISTRY

AUTHORITY:
    Wilsy OS IAM P6 durable supervisory privileged-activation revocation
    command-evidence persistence authority.

EPITOME:
    Persist immutable P6 revocation command evidence with deterministic unique
    identities, exact replay, divergent-replay rejection, corruption rejection,
    caller-owned active transactions and no TTL/delete authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/
    privileged_activation_revocation_command_evidence_registry.py

COLLABORATION / OWNERSHIP:
    IAM owns this registry. The P6 command service composes it with the existing
    privileged-activation registry inside one caller-owned transaction.
    Activation state remains authoritative in PrivilegedActivationRegistry.

CERTIFICATION / UPDATE DATE:
    2026-10-15

CHANGELOG:
    v1.0.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-EVIDENCE-REGISTRY
        Initial immutable P6 durable command-evidence registry.

COMPLIANCE:
    Deterministic unique indexes, fail-closed hydration, caller-owned active
    transactions, immutable evidence rows, exact replay only and no TTL.

SECURITY / PRIVACY POSTURE:
    Stores only validated P6 evidence fields. Raw review narrative, credentials,
    secrets, payment data and execution truth are excluded.

TENANT BOUNDARY:
    Exact target tenant scope is persisted from immutable command evidence.
    Platform scope remains tenant_id=None. Cross-scope rebinding is rejected by
    evidence hydration and divergent-replay checks.

AUTHORITY BOUNDARY:
    Persistence authority for immutable P6 command evidence only. This registry
    cannot revoke activations, assign permissions or roles, create eligibility,
    issue activations, grant break-glass authority or expose HTTP commands.

FINANCIAL AUTHORITY BOUNDARY:
    NONE.
"""

from __future__ import annotations

from typing import Any, Final

from pymongo.errors import DuplicateKeyError

from tools.eos.auth.privileged_activation_revocation_command_evidence import (
    PrivilegedActivationRevocationCommandEvidence,
    PrivilegedActivationRevocationCommandEvidenceError,
)


VERSION: Final[str] = (
    "v1.0.0-P6-PRIVILEGED-ACTIVATION-"
    "REVOCATION-COMMAND-EVIDENCE-REGISTRY"
)

COLLECTION: Final[str] = (
    "privileged_activation_revocation_command_evidence"
)

EVIDENCE_ID_INDEX: Final[str] = (
    "privileged_activation_revocation_evidence_id_unique"
)

FINGERPRINT_INDEX: Final[str] = (
    "privileged_activation_revocation_fingerprint_unique"
)

ACTOR_IDEMPOTENCY_INDEX: Final[str] = (
    "privileged_activation_revocation_actor_idempotency_unique"
)

TARGET_HISTORY_INDEX: Final[str] = (
    "privileged_activation_revocation_target_history"
)


class PrivilegedActivationRevocationCommandEvidenceRegistryError(
    RuntimeError
):
    """Base error for the P6 durable command-evidence registry."""


class PrivilegedActivationRevocationCommandEvidenceTransactionRequiredError(
    PrivilegedActivationRevocationCommandEvidenceRegistryError
):
    """Raised when a write is attempted without an active caller transaction."""


class PrivilegedActivationRevocationCommandEvidenceNotFoundError(
    PrivilegedActivationRevocationCommandEvidenceRegistryError
):
    """Raised when an exact evidence identifier does not exist."""


class PrivilegedActivationRevocationCommandEvidenceConflictError(
    PrivilegedActivationRevocationCommandEvidenceRegistryError
):
    """Raised for divergent replay, uniqueness conflict or identity collision."""


class PrivilegedActivationRevocationCommandEvidencePersistedInvalidError(
    PrivilegedActivationRevocationCommandEvidenceRegistryError
):
    """Raised when durable evidence cannot be safely rehydrated."""


def _require_active_transaction(
    session: object,
) -> None:
    if session is None:
        raise (
            PrivilegedActivationRevocationCommandEvidenceTransactionRequiredError(
                "ACTIVE_TRANSACTION_REQUIRED"
            )
        )

    in_transaction = getattr(
        session,
        "in_transaction",
        None,
    )

    if in_transaction is not True:
        raise (
            PrivilegedActivationRevocationCommandEvidenceTransactionRequiredError(
                "ACTIVE_TRANSACTION_REQUIRED"
            )
        )


def _hydrate(
    row: object,
) -> PrivilegedActivationRevocationCommandEvidence:
    if not isinstance(
        row,
        dict,
    ):
        raise (
            PrivilegedActivationRevocationCommandEvidencePersistedInvalidError(
                "PERSISTED_RECORD_INVALID"
            )
        )

    payload = {
        key: value
        for key, value in row.items()
        if key != "_id"
    }

    try:
        return (
            PrivilegedActivationRevocationCommandEvidence.from_document(
                payload
            )
        )
    except PrivilegedActivationRevocationCommandEvidenceError as exc:
        raise (
            PrivilegedActivationRevocationCommandEvidencePersistedInvalidError(
                "PERSISTED_RECORD_INVALID"
            )
        ) from exc


def _same(
    left: PrivilegedActivationRevocationCommandEvidence,
    right: PrivilegedActivationRevocationCommandEvidence,
) -> bool:
    return left == right


class PrivilegedActivationRevocationCommandEvidenceRegistry:
    """Persist immutable P6 supervisory revocation command evidence.

    Writes require a caller-owned active transaction. The registry never opens,
    commits, aborts or retries transactions. Exact actor+idempotency replay
    returns the existing immutable value; divergent replay fails closed.

    The registry has no delete, update, TTL or activation-state authority.
    """

    def __init__(
        self,
        collection: Any,
    ) -> None:
        """Bind the registry to the supplied Mongo-compatible collection."""

        self._collection = collection

    def ensure_indexes(
        self,
    ) -> None:
        """Create deterministic non-TTL indexes for immutable P6 evidence."""

        self._collection.create_index(
            [
                (
                    "revocation_command_evidence_id",
                    1,
                ),
            ],
            unique=True,
            name=EVIDENCE_ID_INDEX,
        )

        self._collection.create_index(
            [
                (
                    "fingerprint",
                    1,
                ),
            ],
            unique=True,
            name=FINGERPRINT_INDEX,
        )

        self._collection.create_index(
            [
                (
                    "actor_principal_id",
                    1,
                ),
                (
                    "idempotency_key",
                    1,
                ),
            ],
            unique=True,
            name=ACTOR_IDEMPOTENCY_INDEX,
        )

        self._collection.create_index(
            [
                (
                    "target_activation_id",
                    1,
                ),
                (
                    "authorized_at",
                    1,
                ),
            ],
            unique=False,
            name=TARGET_HISTORY_INDEX,
        )

    def get(
        self,
        *,
        revocation_command_evidence_id: str,
        session: object = None,
    ) -> PrivilegedActivationRevocationCommandEvidence:
        """Return exact immutable evidence or fail closed when absent/corrupt."""

        if (
            not isinstance(
                revocation_command_evidence_id,
                str,
            )
            or not revocation_command_evidence_id
            or (
                revocation_command_evidence_id
                != revocation_command_evidence_id.strip()
            )
        ):
            raise (
                PrivilegedActivationRevocationCommandEvidenceNotFoundError(
                    "REVOCATION_COMMAND_EVIDENCE_NOT_FOUND"
                )
            )

        row = self._collection.find_one(
            {
                "revocation_command_evidence_id": (
                    revocation_command_evidence_id
                ),
            },
            session=session,
        )

        if row is None:
            raise (
                PrivilegedActivationRevocationCommandEvidenceNotFoundError(
                    "REVOCATION_COMMAND_EVIDENCE_NOT_FOUND"
                )
            )

        return _hydrate(
            row
        )

    def get_by_actor_idempotency(
        self,
        *,
        actor_principal_id: str,
        idempotency_key: str,
        session: object = None,
    ) -> PrivilegedActivationRevocationCommandEvidence | None:
        """Resolve one existing actor+idempotency command, if present."""

        if (
            not isinstance(
                actor_principal_id,
                str,
            )
            or not actor_principal_id
            or actor_principal_id != actor_principal_id.strip()
            or not isinstance(
                idempotency_key,
                str,
            )
            or not idempotency_key
            or idempotency_key != idempotency_key.strip()
        ):
            return None

        row = self._collection.find_one(
            {
                "actor_principal_id": actor_principal_id,
                "idempotency_key": idempotency_key,
            },
            session=session,
        )

        if row is None:
            return None

        return _hydrate(
            row
        )

    def create_or_replay(
        self,
        value: PrivilegedActivationRevocationCommandEvidence,
        *,
        session: object,
    ) -> PrivilegedActivationRevocationCommandEvidence:
        """Persist one immutable command or return an exact durable replay.

        The caller must own an active transaction. Existing actor+idempotency
        evidence is returned only when it is byte-semantic equivalent to the
        supplied immutable value. Divergence, identity collision and persisted
        corruption fail closed.
        """

        _require_active_transaction(
            session
        )

        if not isinstance(
            value,
            PrivilegedActivationRevocationCommandEvidence,
        ):
            raise (
                PrivilegedActivationRevocationCommandEvidenceConflictError(
                    "COMMAND_EVIDENCE_TYPE_INVALID"
                )
            )

        existing = self.get_by_actor_idempotency(
            actor_principal_id=(
                value.actor_principal_id
            ),
            idempotency_key=(
                value.idempotency_key
            ),
            session=session,
        )

        if existing is not None:
            if _same(
                existing,
                value,
            ):
                return existing

            raise (
                PrivilegedActivationRevocationCommandEvidenceConflictError(
                    "DIVERGENT_IDEMPOTENCY_REPLAY"
                )
            )

        document = value.to_document()

        try:
            self._collection.insert_one(
                document,
                session=session,
            )

        except DuplicateKeyError as exc:
            replay = self.get_by_actor_idempotency(
                actor_principal_id=(
                    value.actor_principal_id
                ),
                idempotency_key=(
                    value.idempotency_key
                ),
                session=session,
            )

            if (
                replay is not None
                and _same(
                    replay,
                    value,
                )
            ):
                return replay

            by_id = self._collection.find_one(
                {
                    "revocation_command_evidence_id": (
                        value.revocation_command_evidence_id
                    ),
                },
                session=session,
            )

            if by_id is not None:
                hydrated = _hydrate(
                    by_id
                )

                if _same(
                    hydrated,
                    value,
                ):
                    return hydrated

            raise (
                PrivilegedActivationRevocationCommandEvidenceConflictError(
                    "COMMAND_EVIDENCE_UNIQUENESS_CONFLICT"
                )
            ) from exc

        persisted = self.get(
            revocation_command_evidence_id=(
                value.revocation_command_evidence_id
            ),
            session=session,
        )

        if not _same(
            persisted,
            value,
        ):
            raise (
                PrivilegedActivationRevocationCommandEvidenceConflictError(
                    "PERSISTED_COMMAND_EVIDENCE_MISMATCH"
                )
            )

        return persisted


__all__ = [
    "VERSION",
    "COLLECTION",
    "EVIDENCE_ID_INDEX",
    "FINGERPRINT_INDEX",
    "ACTOR_IDEMPOTENCY_INDEX",
    "TARGET_HISTORY_INDEX",
    "PrivilegedActivationRevocationCommandEvidenceRegistryError",
    "PrivilegedActivationRevocationCommandEvidenceTransactionRequiredError",
    "PrivilegedActivationRevocationCommandEvidenceNotFoundError",
    "PrivilegedActivationRevocationCommandEvidenceConflictError",
    "PrivilegedActivationRevocationCommandEvidencePersistedInvalidError",
    "PrivilegedActivationRevocationCommandEvidenceRegistry",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: privileged_activation_revocation_command_evidence_registry.py
# VERSION: v1.0.0-P6-PRIVILEGED-ACTIVATION-REVOCATION-COMMAND-EVIDENCE-REGISTRY
# AUTHORITY BOUNDARY: IMMUTABLE P6 COMMAND-EVIDENCE PERSISTENCE ONLY
# TENANT POSTURE: EXACT TARGET SCOPE PRESERVED; CROSS-SCOPE REBINDING FORBIDDEN
# FAIL-CLOSED POSTURE: ACTIVE TX, EXACT REPLAY, CORRUPTION/CONFLICT REJECTION, NO TTL
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
