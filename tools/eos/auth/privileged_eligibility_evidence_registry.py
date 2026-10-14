"""
Append-only privileged-eligibility evidence registry.

VERSION:
v1.0.0-P2-R2-A2-PRIVILEGED-ELIGIBILITY-EVIDENCE-REGISTRY

BOUNDARY:
Stores immutable P2 eligibility evidence only.

The caller owns the active Mongo transaction. This registry never starts,
commits, aborts, or retries a transaction. It performs no role assignment,
privileged activation, authentication, session mutation, break-glass action,
security-assurance decision, or financial execution.

PAST ELIGIBILITY != CURRENT ELIGIBILITY.
"""

from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from tools.eos.auth.privileged_eligibility_evidence import (
    PrivilegedEligibilityEvidence,
    PrivilegedEligibilityEvidencePersistedRecordInvalidError,
)


VERSION: Final[str] = (
    "v1.0.0-P2-R2-A2-"
    "PRIVILEGED-ELIGIBILITY-EVIDENCE-REGISTRY"
)

COLLECTION: Final[str] = (
    "privileged_eligibility_evidence"
)

ELIGIBILITY_ID_INDEX: Final[str] = (
    "privileged_eligibility_evidence_identity_unique"
)

SCOPE_IDEMPOTENCY_INDEX: Final[str] = (
    "privileged_eligibility_scope_idempotency_unique"
)

ROLE_TIMELINE_INDEX: Final[str] = (
    "privileged_eligibility_role_timeline"
)

PRINCIPAL_TIMELINE_INDEX: Final[str] = (
    "privileged_eligibility_principal_timeline"
)


class PrivilegedEligibilityEvidenceRegistryError(
    RuntimeError
):
    """Base registry failure."""

    def __init__(
        self,
        code: str,
    ) -> None:
        super().__init__(
            code
        )
        self.code = code


class PrivilegedEligibilityEvidenceTransactionRequiredError(
    PrivilegedEligibilityEvidenceRegistryError
):
    """Caller did not supply one active transaction."""


class PrivilegedEligibilityEvidenceConflictError(
    PrivilegedEligibilityEvidenceRegistryError
):
    """Identity or idempotency collision with divergent material."""


class PrivilegedEligibilityEvidenceNotFoundError(
    PrivilegedEligibilityEvidenceRegistryError
):
    """Requested exact evidence is absent."""


class PrivilegedEligibilityEvidencePersistedInvalidError(
    PrivilegedEligibilityEvidenceRegistryError
):
    """Durable BSON failed strict domain hydration."""


def _tenant_scope_key(
    value: str | None,
) -> str:
    # Platform/system-root evidence has no tenant. Mongo compound indexes
    # require one deterministic value to keep tenant and platform replay
    # identities exact and non-overlapping.
    return (
        value
        if value is not None
        else ""
    )


def _require_transaction(
    session: object,
) -> None:
    if (
        session is None
        or getattr(
            session,
            "in_transaction",
            False,
        )
        is not True
    ):
        raise (
            PrivilegedEligibilityEvidenceTransactionRequiredError(
                "ACTIVE_TRANSACTION_REQUIRED"
            )
        )


def _hydrate(
    row: object,
) -> PrivilegedEligibilityEvidence:
    if not isinstance(
        row,
        dict,
    ):
        raise (
            PrivilegedEligibilityEvidencePersistedInvalidError(
                "PERSISTED_RECORD_INVALID"
            )
        )

    material = dict(row)
    material.pop(
        "_id",
        None,
    )
    material.pop(
        "_scope_tenant_key",
        None,
    )

    try:
        return (
            PrivilegedEligibilityEvidence
            .from_persisted(
                material
            )
        )
    except (
        PrivilegedEligibilityEvidencePersistedRecordInvalidError
    ) as error:
        raise (
            PrivilegedEligibilityEvidencePersistedInvalidError(
                "PERSISTED_RECORD_INVALID"
            )
        ) from error


class PrivilegedEligibilityEvidenceRegistry:
    """Strict append-only persistence for immutable P2 evidence."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = collection

    def ensure_indexes(
        self,
    ) -> None:
        self._collection.create_index(
            [
                (
                    "eligibility_evidence_id",
                    ASCENDING,
                )
            ],
            unique=True,
            name=ELIGIBILITY_ID_INDEX,
        )

        self._collection.create_index(
            [
                (
                    "target_class",
                    ASCENDING,
                ),
                (
                    "_scope_tenant_key",
                    ASCENDING,
                ),
                (
                    "principal_id",
                    ASCENDING,
                ),
                (
                    "privileged_role_id",
                    ASCENDING,
                ),
                (
                    "idempotency_key",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=SCOPE_IDEMPOTENCY_INDEX,
        )

        self._collection.create_index(
            [
                (
                    "target_class",
                    ASCENDING,
                ),
                (
                    "_scope_tenant_key",
                    ASCENDING,
                ),
                (
                    "principal_id",
                    ASCENDING,
                ),
                (
                    "privileged_role_id",
                    ASCENDING,
                ),
                (
                    "evaluated_at",
                    ASCENDING,
                ),
            ],
            name=ROLE_TIMELINE_INDEX,
        )

        self._collection.create_index(
            [
                (
                    "target_class",
                    ASCENDING,
                ),
                (
                    "_scope_tenant_key",
                    ASCENDING,
                ),
                (
                    "principal_id",
                    ASCENDING,
                ),
                (
                    "evaluated_at",
                    ASCENDING,
                ),
            ],
            name=PRINCIPAL_TIMELINE_INDEX,
        )

    def get(
        self,
        *,
        eligibility_evidence_id: str,
        session: object = None,
    ) -> PrivilegedEligibilityEvidence:
        row = self._collection.find_one(
            {
                "eligibility_evidence_id":
                    eligibility_evidence_id,
            },
            session=session,
        )

        if row is None:
            raise (
                PrivilegedEligibilityEvidenceNotFoundError(
                    "ELIGIBILITY_EVIDENCE_NOT_FOUND"
                )
            )

        return _hydrate(
            row
        )

    def get_by_scope_idempotency(
        self,
        *,
        target_class: str,
        tenant_id: str | None,
        principal_id: str,
        privileged_role_id: str,
        idempotency_key: str,
        session: object = None,
    ) -> PrivilegedEligibilityEvidence | None:
        row = self._collection.find_one(
            {
                "target_class":
                    target_class,
                "_scope_tenant_key":
                    _tenant_scope_key(
                        tenant_id
                    ),
                "principal_id":
                    principal_id,
                "privileged_role_id":
                    privileged_role_id,
                "idempotency_key":
                    idempotency_key,
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
        value: PrivilegedEligibilityEvidence,
        *,
        session: object,
    ) -> PrivilegedEligibilityEvidence:
        _require_transaction(
            session
        )

        if not isinstance(
            value,
            PrivilegedEligibilityEvidence,
        ):
            raise TypeError(
                "value must be PrivilegedEligibilityEvidence"
            )

        replay = (
            self.get_by_scope_idempotency(
                target_class=
                    value.target_class.value,
                tenant_id=
                    value.tenant_id,
                principal_id=
                    value.principal_id,
                privileged_role_id=
                    value.privileged_role_id,
                idempotency_key=
                    value.idempotency_key,
                session=session,
            )
        )

        if replay is not None:
            if replay == value:
                return replay

            raise (
                PrivilegedEligibilityEvidenceConflictError(
                    "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
                )
            )

        identity_row = self._collection.find_one(
            {
                "eligibility_evidence_id":
                    value.eligibility_evidence_id,
            },
            session=session,
        )

        if identity_row is not None:
            historic = _hydrate(
                identity_row
            )

            if historic == value:
                return historic

            raise (
                PrivilegedEligibilityEvidenceConflictError(
                    "ELIGIBILITY_EVIDENCE_ID_COLLISION"
                )
            )

        row = value.to_persisted()
        row["_scope_tenant_key"] = (
            _tenant_scope_key(
                value.tenant_id
            )
        )

        try:
            self._collection.insert_one(
                row,
                session=session,
            )

            return value

        except DuplicateKeyError as error:
            # Mongo may invalidate a transaction after duplicate-key failure.
            # Never invent success. The host owns whole-transaction retry.
            if (
                getattr(
                    session,
                    "in_transaction",
                    False,
                )
                is not True
            ):
                raise (
                    PrivilegedEligibilityEvidenceConflictError(
                        "WHOLE_TRANSACTION_RETRY_REQUIRED"
                    )
                ) from error

            replay_after_race = (
                self.get_by_scope_idempotency(
                    target_class=
                        value.target_class.value,
                    tenant_id=
                        value.tenant_id,
                    principal_id=
                        value.principal_id,
                    privileged_role_id=
                        value.privileged_role_id,
                    idempotency_key=
                        value.idempotency_key,
                    session=session,
                )
            )

            if (
                replay_after_race is not None
                and replay_after_race == value
            ):
                return replay_after_race

            identity_after_race = (
                self._collection.find_one(
                    {
                        "eligibility_evidence_id":
                            value.eligibility_evidence_id,
                    },
                    session=session,
                )
            )

            if (
                identity_after_race is not None
                and _hydrate(
                    identity_after_race
                )
                == value
            ):
                return value

            if replay_after_race is not None:
                raise (
                    PrivilegedEligibilityEvidenceConflictError(
                        "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
                    )
                ) from error

            if identity_after_race is not None:
                raise (
                    PrivilegedEligibilityEvidenceConflictError(
                        "ELIGIBILITY_EVIDENCE_ID_COLLISION"
                    )
                ) from error

            raise (
                PrivilegedEligibilityEvidenceConflictError(
                    "WHOLE_TRANSACTION_RETRY_REQUIRED"
                )
            ) from error


__all__ = [
    "VERSION",
    "COLLECTION",
    "ELIGIBILITY_ID_INDEX",
    "SCOPE_IDEMPOTENCY_INDEX",
    "ROLE_TIMELINE_INDEX",
    "PRINCIPAL_TIMELINE_INDEX",
    "PrivilegedEligibilityEvidenceRegistryError",
    "PrivilegedEligibilityEvidenceTransactionRequiredError",
    "PrivilegedEligibilityEvidenceConflictError",
    "PrivilegedEligibilityEvidenceNotFoundError",
    "PrivilegedEligibilityEvidencePersistedInvalidError",
    "PrivilegedEligibilityEvidenceRegistry",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: privileged_eligibility_evidence_registry.py
# VERSION: v1.0.0-P2-R2-A2-PRIVILEGED-ELIGIBILITY-EVIDENCE-REGISTRY
# COLLECTION: privileged_eligibility_evidence
# MUTATION: append-only immutable insert; no update/delete/upsert
# TRANSACTION: caller-owned active transaction required
# REPLAY: exact returns existing; divergent conflicts
# ROOT/TENANT: exact scope discriminator, no cross-scope replay
# TTL: none
# AUTHORITY: no assignment, activation, sessions, break glass, or finance
# FINANCIAL EXECUTION AUTHORITY: None
# END OF WILSY OS SOVEREIGN ARTIFACT
