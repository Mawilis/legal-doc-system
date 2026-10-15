"""
Append-only durable registry for historic P3 security-assurance evidence.

VERSION:
v1.0.0-P3-R2-A2-PRIVILEGED-SECURITY-ASSURANCE-EVIDENCE-REGISTRY

Frozen index contract:

1. UNIQUE assurance_evidence_id
2. UNIQUE principal_id + assurance_channel + assurance_purpose + idempotency_key
3. NONUNIQUE principal_id + assurance_purpose + evaluated_at
4. NONUNIQUE principal_id + assurance_channel + evaluated_at

No TTL.
No current pointer.
No sequence chain.
No update/delete/purge path.

Historic sufficient evidence never proves current assurance. The caller owns the
active transaction. This registry owns persistence only.
"""

from __future__ import annotations

from typing import (
    Any,
    Final,
)

from pymongo import ASCENDING
from pymongo.errors import (
    DuplicateKeyError,
    PyMongoError,
)

from tools.eos.auth.privileged_security_assurance_evidence import (
    PrivilegedSecurityAssuranceEvidence,
    PrivilegedSecurityAssuranceEvidenceError,
)


VERSION: Final[str] = (
    "v1.0.0-P3-R2-A2-"
    "PRIVILEGED-SECURITY-ASSURANCE-EVIDENCE-REGISTRY"
)

COLLECTION: Final[str] = (
    "privileged_security_assurance_evidence"
)

ASSURANCE_EVIDENCE_ID_INDEX: Final[str] = (
    "privileged_security_assurance_evidence_identity_unique"
)

SCOPE_IDEMPOTENCY_INDEX: Final[str] = (
    "privileged_security_assurance_scope_idempotency_unique"
)

PRINCIPAL_PURPOSE_TIMELINE_INDEX: Final[str] = (
    "privileged_security_assurance_principal_purpose_timeline"
)

PRINCIPAL_CHANNEL_TIMELINE_INDEX: Final[str] = (
    "privileged_security_assurance_principal_channel_timeline"
)


class PrivilegedSecurityAssuranceEvidenceRegistryError(
    RuntimeError
):
    """Base registry failure."""


class PrivilegedSecurityAssuranceEvidenceTransactionRequiredError(
    PrivilegedSecurityAssuranceEvidenceRegistryError
):
    """Caller did not provide one active transaction."""


class PrivilegedSecurityAssuranceEvidenceConflictError(
    PrivilegedSecurityAssuranceEvidenceRegistryError
):
    """Replay, identity, or concurrent insertion conflict."""


class PrivilegedSecurityAssuranceEvidenceNotFoundError(
    PrivilegedSecurityAssuranceEvidenceRegistryError
):
    """Requested evidence identity does not exist."""


class PrivilegedSecurityAssuranceEvidencePersistedInvalidError(
    PrivilegedSecurityAssuranceEvidenceRegistryError
):
    """Persisted row failed strict evidence hydration."""


class PrivilegedSecurityAssuranceEvidencePersistenceError(
    PrivilegedSecurityAssuranceEvidenceRegistryError
):
    """Persistence dependency unavailable or malformed."""


def _identifier(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
    ):
        raise (
            PrivilegedSecurityAssuranceEvidencePersistenceError(
                name + " is invalid"
            )
        )

    return value


def _active_transaction(
    session: object,
) -> object:
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
            PrivilegedSecurityAssuranceEvidenceTransactionRequiredError(
                "ACTIVE_TRANSACTION_REQUIRED"
            )
        )

    return session


def _hydrate(
    row: object,
) -> PrivilegedSecurityAssuranceEvidence:
    if not isinstance(
        row,
        dict,
    ):
        raise (
            PrivilegedSecurityAssuranceEvidencePersistedInvalidError(
                "PERSISTED_EVIDENCE_INVALID"
            )
        )

    clean = dict(row)
    clean.pop("_id", None)

    try:
        return (
            PrivilegedSecurityAssuranceEvidence
            .from_persisted(
                clean
            )
        )
    except (
        PrivilegedSecurityAssuranceEvidenceError,
        TypeError,
        ValueError,
    ) as error:
        raise (
            PrivilegedSecurityAssuranceEvidencePersistedInvalidError(
                "PERSISTED_EVIDENCE_INVALID"
            )
        ) from error


class PrivilegedSecurityAssuranceEvidenceRegistry:
    """Append-only persistence facade for historic P3 assurance evidence."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        if collection is None:
            raise (
                PrivilegedSecurityAssuranceEvidencePersistenceError(
                    "COLLECTION_REQUIRED"
                )
            )

        self._collection = collection

    def ensure_indexes(
        self,
    ) -> None:
        """Create exactly four sanctioned indexes and no TTL."""

        indexes = (
            (
                [
                    (
                        "assurance_evidence_id",
                        ASCENDING,
                    ),
                ],
                True,
                ASSURANCE_EVIDENCE_ID_INDEX,
            ),
            (
                [
                    (
                        "principal_id",
                        ASCENDING,
                    ),
                    (
                        "assurance_channel",
                        ASCENDING,
                    ),
                    (
                        "assurance_purpose",
                        ASCENDING,
                    ),
                    (
                        "idempotency_key",
                        ASCENDING,
                    ),
                ],
                True,
                SCOPE_IDEMPOTENCY_INDEX,
            ),
            (
                [
                    (
                        "principal_id",
                        ASCENDING,
                    ),
                    (
                        "assurance_purpose",
                        ASCENDING,
                    ),
                    (
                        "evaluated_at",
                        ASCENDING,
                    ),
                ],
                False,
                PRINCIPAL_PURPOSE_TIMELINE_INDEX,
            ),
            (
                [
                    (
                        "principal_id",
                        ASCENDING,
                    ),
                    (
                        "assurance_channel",
                        ASCENDING,
                    ),
                    (
                        "evaluated_at",
                        ASCENDING,
                    ),
                ],
                False,
                PRINCIPAL_CHANNEL_TIMELINE_INDEX,
            ),
        )

        try:
            for (
                keys,
                unique,
                name,
            ) in indexes:
                self._collection.create_index(
                    keys,
                    unique=unique,
                    name=name,
                )
        except AttributeError as error:
            raise (
                PrivilegedSecurityAssuranceEvidencePersistenceError(
                    "COLLECTION_INTERFACE_INVALID"
                )
            ) from error
        except PyMongoError as error:
            raise (
                PrivilegedSecurityAssuranceEvidencePersistenceError(
                    "INDEX_CREATION_FAILED"
                )
            ) from error

    def get(
        self,
        *,
        assurance_evidence_id: str,
        session: object = None,
    ) -> PrivilegedSecurityAssuranceEvidence:
        identity = _identifier(
            "assurance_evidence_id",
            assurance_evidence_id,
        )

        try:
            row = self._collection.find_one(
                {
                    "assurance_evidence_id":
                        identity,
                },
                session=session,
            )
        except AttributeError as error:
            raise (
                PrivilegedSecurityAssuranceEvidencePersistenceError(
                    "COLLECTION_INTERFACE_INVALID"
                )
            ) from error
        except PyMongoError as error:
            raise (
                PrivilegedSecurityAssuranceEvidencePersistenceError(
                    "PERSISTENCE_UNAVAILABLE"
                )
            ) from error

        if row is None:
            raise (
                PrivilegedSecurityAssuranceEvidenceNotFoundError(
                    "ASSURANCE_EVIDENCE_NOT_FOUND"
                )
            )

        value = _hydrate(
            row
        )

        if (
            value.assurance_evidence_id
            != identity
        ):
            raise (
                PrivilegedSecurityAssuranceEvidencePersistedInvalidError(
                    "PERSISTED_IDENTITY_MISMATCH"
                )
            )

        return value

    def get_by_scope_idempotency(
        self,
        *,
        principal_id: str,
        assurance_channel: str,
        assurance_purpose: str,
        idempotency_key: str,
        session: object = None,
    ) -> PrivilegedSecurityAssuranceEvidence | None:
        principal = _identifier(
            "principal_id",
            principal_id,
        )

        channel = _identifier(
            "assurance_channel",
            assurance_channel,
        )

        purpose = _identifier(
            "assurance_purpose",
            assurance_purpose,
        )

        replay_key = _identifier(
            "idempotency_key",
            idempotency_key,
        )

        try:
            row = self._collection.find_one(
                {
                    "principal_id":
                        principal,
                    "assurance_channel":
                        channel,
                    "assurance_purpose":
                        purpose,
                    "idempotency_key":
                        replay_key,
                },
                session=session,
            )
        except AttributeError as error:
            raise (
                PrivilegedSecurityAssuranceEvidencePersistenceError(
                    "COLLECTION_INTERFACE_INVALID"
                )
            ) from error
        except PyMongoError as error:
            raise (
                PrivilegedSecurityAssuranceEvidencePersistenceError(
                    "PERSISTENCE_UNAVAILABLE"
                )
            ) from error

        if row is None:
            return None

        value = _hydrate(
            row
        )

        if (
            value.principal_id
            != principal
            or value.assurance_channel.value
            != channel
            or value.assurance_purpose.value
            != purpose
            or value.idempotency_key
            != replay_key
        ):
            raise (
                PrivilegedSecurityAssuranceEvidencePersistedInvalidError(
                    "PERSISTED_SCOPE_MISMATCH"
                )
            )

        return value

    def _classify_existing(
        self,
        requested: PrivilegedSecurityAssuranceEvidence,
        *,
        session: object,
    ) -> PrivilegedSecurityAssuranceEvidence | None:
        replay = (
            self.get_by_scope_idempotency(
                principal_id=
                    requested.principal_id,
                assurance_channel=
                    requested
                    .assurance_channel
                    .value,
                assurance_purpose=
                    requested
                    .assurance_purpose
                    .value,
                idempotency_key=
                    requested.idempotency_key,
                session=session,
            )
        )

        if replay is not None:
            if replay == requested:
                return replay

            raise (
                PrivilegedSecurityAssuranceEvidenceConflictError(
                    "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
                )
            )

        try:
            identity_row = (
                self._collection.find_one(
                    {
                        "assurance_evidence_id":
                            requested
                            .assurance_evidence_id,
                    },
                    session=session,
                )
            )
        except AttributeError as error:
            raise (
                PrivilegedSecurityAssuranceEvidencePersistenceError(
                    "COLLECTION_INTERFACE_INVALID"
                )
            ) from error
        except PyMongoError as error:
            raise (
                PrivilegedSecurityAssuranceEvidencePersistenceError(
                    "PERSISTENCE_UNAVAILABLE"
                )
            ) from error

        if identity_row is not None:
            historic = _hydrate(
                identity_row
            )

            if historic == requested:
                return historic

            raise (
                PrivilegedSecurityAssuranceEvidenceConflictError(
                    "ASSURANCE_EVIDENCE_ID_COLLISION"
                )
            )

        return None

    def create_or_replay(
        self,
        value: PrivilegedSecurityAssuranceEvidence,
        *,
        session: object,
    ) -> PrivilegedSecurityAssuranceEvidence:
        """Insert immutable evidence or return exact historic replay."""

        tx = _active_transaction(
            session
        )

        if type(value) is not (
            PrivilegedSecurityAssuranceEvidence
        ):
            raise (
                PrivilegedSecurityAssuranceEvidencePersistenceError(
                    "EVIDENCE_REQUIRED"
                )
            )

        historic = (
            self._classify_existing(
                value,
                session=tx,
            )
        )

        if historic is not None:
            return historic

        try:
            self._collection.insert_one(
                value.to_persisted(),
                session=tx,
            )

            return value

        except DuplicateKeyError as error:
            if (
                getattr(
                    tx,
                    "in_transaction",
                    False,
                )
                is not True
            ):
                raise (
                    PrivilegedSecurityAssuranceEvidenceConflictError(
                        "WHOLE_TRANSACTION_RETRY_REQUIRED"
                    )
                ) from error

            historic = (
                self._classify_existing(
                    value,
                    session=tx,
                )
            )

            if historic is not None:
                return historic

            raise (
                PrivilegedSecurityAssuranceEvidenceConflictError(
                    "DUPLICATE_KEY_CONFLICT"
                )
            ) from error

        except AttributeError as error:
            raise (
                PrivilegedSecurityAssuranceEvidencePersistenceError(
                    "COLLECTION_INTERFACE_INVALID"
                )
            ) from error

        except PyMongoError as error:
            # Caller owns transaction lifecycle. PyMongo with_transaction()
            # can retry the whole callback only while the original
            # TransientTransactionError label remains intact. Never erase that
            # label behind a registry persistence classification.
            if error.has_error_label(
                "TransientTransactionError"
            ):
                raise

            raise (
                PrivilegedSecurityAssuranceEvidencePersistenceError(
                    "PERSISTENCE_UNAVAILABLE"
                )
            ) from error


__all__ = [
    "VERSION",
    "COLLECTION",
    "ASSURANCE_EVIDENCE_ID_INDEX",
    "SCOPE_IDEMPOTENCY_INDEX",
    "PRINCIPAL_PURPOSE_TIMELINE_INDEX",
    "PRINCIPAL_CHANNEL_TIMELINE_INDEX",
    "PrivilegedSecurityAssuranceEvidenceRegistry",
    "PrivilegedSecurityAssuranceEvidenceRegistryError",
    "PrivilegedSecurityAssuranceEvidenceTransactionRequiredError",
    "PrivilegedSecurityAssuranceEvidenceConflictError",
    "PrivilegedSecurityAssuranceEvidenceNotFoundError",
    "PrivilegedSecurityAssuranceEvidencePersistedInvalidError",
    "PrivilegedSecurityAssuranceEvidencePersistenceError",
]
