"""
Revisioned immutable registry for interactive privileged security proofs.

VERSION:
v1.0.0-P3-R3B-PRIVILEGED-INTERACTIVE-SECURITY-PROOF-REGISTRY

One logical proof is identified by proof_id.

Each lifecycle transition creates one immutable snapshot:

    revision 1 = VERIFIED

Allowed transitions:

    VERIFIED -> REVOKED
    VERIFIED -> INVALIDATED

REVOKED and INVALIDATED are terminal.

No snapshot is updated in place.
No TTL exists.
No current pointer exists.
Current snapshot means the highest valid revision in the verified fingerprint
chain.

Registry status alone never proves current P3 assurance. Credential revision,
session currentness, principal currentness, and authentication recency remain
external currentness checks.

Caller owns the active Mongo transaction.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import (
    datetime,
    timezone,
)
import hashlib
import hmac
import json
import re
from typing import (
    Any,
    Final,
)

from pymongo import (
    ASCENDING,
    DESCENDING,
)
from pymongo.errors import (
    DuplicateKeyError,
    PyMongoError,
)

from tools.eos.auth.privileged_interactive_security_proof import (
    PrivilegedInteractiveProofStatus,
    PrivilegedInteractiveSecurityProof,
    PrivilegedInteractiveSecurityProofError,
)


VERSION: Final[str] = (
    "v1.0.0-P3-R3B-"
    "PRIVILEGED-INTERACTIVE-SECURITY-PROOF-REGISTRY"
)

SCHEMA: Final[str] = (
    "WILSY-PRIVILEGED-INTERACTIVE-SECURITY-PROOF-SNAPSHOT/V1"
)

COLLECTION: Final[str] = (
    "privileged_interactive_security_proof_snapshots"
)

PROOF_REVISION_INDEX: Final[str] = (
    "privileged_interactive_proof_revision_unique"
)

PROOF_REFERENCE_REVISION_INDEX: Final[str] = (
    "privileged_interactive_proof_reference_revision_unique"
)

FACTOR_REFERENCE_REVISION_INDEX: Final[str] = (
    "privileged_interactive_factor_reference_revision_unique"
)

PROOF_IDEMPOTENCY_INDEX: Final[str] = (
    "privileged_interactive_proof_idempotency_unique"
)

PRINCIPAL_AUTHENTICATED_TIMELINE_INDEX: Final[str] = (
    "privileged_interactive_principal_authenticated_timeline"
)

SESSION_REVISION_INDEX: Final[str] = (
    "privileged_interactive_session_revision"
)

STATUS_CHANGED_TIMELINE_INDEX: Final[str] = (
    "privileged_interactive_status_changed_timeline"
)

_FINGERPRINT = re.compile(
    r"^[0-9a-f]{128}$"
)

PROOF_REFERENCE_INITIAL_IDENTITY_INDEX = "privileged_interactive_proof_reference_initial_identity"
FACTOR_REFERENCE_INITIAL_IDENTITY_INDEX = "privileged_interactive_factor_reference_initial_identity"


class PrivilegedInteractiveSecurityProofRegistryError(
    RuntimeError
):
    """Base registry failure."""


class PrivilegedInteractiveSecurityProofTransactionRequiredError(
    PrivilegedInteractiveSecurityProofRegistryError
):
    """Caller did not supply an active transaction."""


class PrivilegedInteractiveSecurityProofConflictError(
    PrivilegedInteractiveSecurityProofRegistryError
):
    """Identity, replay, lifecycle, or concurrency conflict."""


class PrivilegedInteractiveSecurityProofNotFoundError(
    PrivilegedInteractiveSecurityProofRegistryError
):
    """Requested proof snapshot does not exist."""


class PrivilegedInteractiveSecurityProofPersistedInvalidError(
    PrivilegedInteractiveSecurityProofRegistryError
):
    """Persisted snapshot or revision chain is invalid."""


class PrivilegedInteractiveSecurityProofPersistenceError(
    PrivilegedInteractiveSecurityProofRegistryError
):
    """Persistence dependency unavailable or malformed."""


def _identifier(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise (
            PrivilegedInteractiveSecurityProofPersistenceError(
                name + " is invalid"
            )
        )

    return value


def _timestamp(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise (
            PrivilegedInteractiveSecurityProofPersistenceError(
                name + " is invalid"
            )
        )

    return value.astimezone(
        timezone.utc
    )


def _revision(
    value: object,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        raise (
            PrivilegedInteractiveSecurityProofPersistenceError(
                "revision is invalid"
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
            PrivilegedInteractiveSecurityProofTransactionRequiredError(
                "ACTIVE_TRANSACTION_REQUIRED"
            )
        )

    return session


def _canonical_time(
    value: datetime,
) -> str:
    return (
        value
        .astimezone(timezone.utc)
        .isoformat(
            timespec="microseconds"
        )
    )


@dataclass(
    frozen=True,
    slots=True,
)
class PrivilegedInteractiveSecurityProofSnapshot:
    """One immutable lifecycle snapshot for one logical interactive proof."""

    proof: PrivilegedInteractiveSecurityProof

    revision: int

    status_changed_at: datetime

    idempotency_key: str

    previous_snapshot_fingerprint: str | None

    snapshot_fingerprint: str

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.proof,
            PrivilegedInteractiveSecurityProof,
        ):
            raise (
                PrivilegedInteractiveSecurityProofPersistedInvalidError(
                    "PROOF_INVALID"
                )
            )

        try:
            revision = _revision(
                self.revision
            )

            changed = _timestamp(
                "status_changed_at",
                self.status_changed_at,
            )

            idempotency = _identifier(
                "idempotency_key",
                self.idempotency_key,
            )
        except PrivilegedInteractiveSecurityProofRegistryError:
            raise
        except Exception as error:
            raise (
                PrivilegedInteractiveSecurityProofPersistedInvalidError(
                    "SNAPSHOT_METADATA_INVALID"
                )
            ) from error

        previous = (
            self.previous_snapshot_fingerprint
        )

        if revision == 1:
            if previous is not None:
                raise (
                    PrivilegedInteractiveSecurityProofPersistedInvalidError(
                        "INITIAL_PREVIOUS_FINGERPRINT_MUST_BE_NULL"
                    )
                )

            if (
                self.proof.proof_status
                is not
                PrivilegedInteractiveProofStatus
                .VERIFIED
            ):
                raise (
                    PrivilegedInteractiveSecurityProofPersistedInvalidError(
                        "INITIAL_STATUS_MUST_BE_VERIFIED"
                    )
                )

        else:
            if (
                not isinstance(previous, str)
                or _FINGERPRINT.fullmatch(
                    previous
                )
                is None
            ):
                raise (
                    PrivilegedInteractiveSecurityProofPersistedInvalidError(
                        "PREVIOUS_FINGERPRINT_INVALID"
                    )
                )

        if (
            not isinstance(
                self.snapshot_fingerprint,
                str,
            )
            or _FINGERPRINT.fullmatch(
                self.snapshot_fingerprint
            )
            is None
        ):
            raise (
                PrivilegedInteractiveSecurityProofPersistedInvalidError(
                    "SNAPSHOT_FINGERPRINT_INVALID"
                )
            )

        object.__setattr__(
            self,
            "revision",
            revision,
        )

        object.__setattr__(
            self,
            "status_changed_at",
            changed,
        )

        object.__setattr__(
            self,
            "idempotency_key",
            idempotency,
        )

    def semantic_payload(
        self,
    ) -> dict[str, object]:
        proof = self.proof

        return {
            "schema":
                SCHEMA,
            "proof_id":
                proof.proof_id,
            "principal_id":
                proof.principal_id,
            "factor_verification_reference":
                proof.factor_verification_reference,
            "authenticated_at":
                _canonical_time(
                    proof.authenticated_at
                ),
            "credential_revision":
                proof.credential_revision,
            "session_reference":
                proof.session_reference,
            "proof_status":
                proof.proof_status.value,
            "proof_reference":
                proof.proof_reference,
            "revision":
                self.revision,
            "status_changed_at":
                _canonical_time(
                    self.status_changed_at
                ),
            "idempotency_key":
                self.idempotency_key,
            "previous_snapshot_fingerprint":
                self.previous_snapshot_fingerprint,
        }

    def expected_fingerprint(
        self,
    ) -> str:
        encoded = json.dumps(
            self.semantic_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode(
            "utf-8"
        )

        return hashlib.sha3_512(
            encoded
        ).hexdigest()

    def assert_integrity(
        self,
    ) -> None:
        expected = (
            self.expected_fingerprint()
        )

        if not hmac.compare_digest(
            expected,
            self.snapshot_fingerprint,
        ):
            raise (
                PrivilegedInteractiveSecurityProofPersistedInvalidError(
                    "SNAPSHOT_FINGERPRINT_MISMATCH"
                )
            )

    def to_persisted(
        self,
    ) -> dict[str, object]:
        self.assert_integrity()

        return {
            **self.semantic_payload(),
            "snapshot_fingerprint":
                self.snapshot_fingerprint,
        }


def _snapshot(
    *,
    proof: PrivilegedInteractiveSecurityProof,
    revision: int,
    status_changed_at: datetime,
    idempotency_key: str,
    previous_snapshot_fingerprint: str | None,
) -> PrivilegedInteractiveSecurityProofSnapshot:
    placeholder = "0" * 128

    candidate = (
        PrivilegedInteractiveSecurityProofSnapshot(
            proof=proof,
            revision=revision,
            status_changed_at=
                status_changed_at,
            idempotency_key=
                idempotency_key,
            previous_snapshot_fingerprint=
                previous_snapshot_fingerprint,
            snapshot_fingerprint=
                placeholder,
        )
    )

    return (
        PrivilegedInteractiveSecurityProofSnapshot(
            proof=candidate.proof,
            revision=candidate.revision,
            status_changed_at=
                candidate.status_changed_at,
            idempotency_key=
                candidate.idempotency_key,
            previous_snapshot_fingerprint=
                candidate
                .previous_snapshot_fingerprint,
            snapshot_fingerprint=
                candidate.expected_fingerprint(),
        )
    )


def _hydrate(
    row: object,
) -> PrivilegedInteractiveSecurityProofSnapshot:
    if not isinstance(
        row,
        dict,
    ):
        raise (
            PrivilegedInteractiveSecurityProofPersistedInvalidError(
                "PERSISTED_SNAPSHOT_INVALID"
            )
        )

    clean = dict(row)
    clean.pop("_id", None)

    expected_fields = {
        "schema",
        "proof_id",
        "principal_id",
        "factor_verification_reference",
        "authenticated_at",
        "credential_revision",
        "session_reference",
        "proof_status",
        "proof_reference",
        "revision",
        "status_changed_at",
        "idempotency_key",
        "previous_snapshot_fingerprint",
        "snapshot_fingerprint",
    }

    if set(clean) != expected_fields:
        raise (
            PrivilegedInteractiveSecurityProofPersistedInvalidError(
                "PERSISTED_SHAPE_INVALID"
            )
        )

    if clean["schema"] != SCHEMA:
        raise (
            PrivilegedInteractiveSecurityProofPersistedInvalidError(
                "PERSISTED_SCHEMA_INVALID"
            )
        )

    try:
        authenticated_raw = clean[
            "authenticated_at"
        ]

        changed_raw = clean[
            "status_changed_at"
        ]

        if not isinstance(
            authenticated_raw,
            str,
        ):
            raise ValueError

        if not isinstance(
            changed_raw,
            str,
        ):
            raise ValueError

        authenticated = (
            datetime.fromisoformat(
                authenticated_raw
            )
        )

        changed = (
            datetime.fromisoformat(
                changed_raw
            )
        )

        if (
            _canonical_time(authenticated)
            != authenticated_raw
        ):
            raise ValueError

        if (
            _canonical_time(changed)
            != changed_raw
        ):
            raise ValueError

        proof = (
            PrivilegedInteractiveSecurityProof(
                proof_id=
                    clean["proof_id"],  # type: ignore[arg-type]
                principal_id=
                    clean["principal_id"],  # type: ignore[arg-type]
                factor_verification_reference=
                    clean["factor_verification_reference"],  # type: ignore[arg-type]
                authenticated_at=
                    authenticated,
                credential_revision=
                    clean["credential_revision"],  # type: ignore[arg-type]
                session_reference=
                    clean["session_reference"],  # type: ignore[arg-type]
                proof_status=
                    PrivilegedInteractiveProofStatus(
                        clean["proof_status"]  # type: ignore[arg-type]
                    ),
                proof_reference=
                    clean["proof_reference"],  # type: ignore[arg-type]
            )
        )

        snapshot = (
            PrivilegedInteractiveSecurityProofSnapshot(
                proof=proof,
                revision=
                    clean["revision"],  # type: ignore[arg-type]
                status_changed_at=
                    changed,
                idempotency_key=
                    clean["idempotency_key"],  # type: ignore[arg-type]
                previous_snapshot_fingerprint=
                    clean[
                        "previous_snapshot_fingerprint"
                    ],  # type: ignore[arg-type]
                snapshot_fingerprint=
                    clean[
                        "snapshot_fingerprint"
                    ],  # type: ignore[arg-type]
            )
        )

        snapshot.assert_integrity()

        return snapshot

    except (
        PrivilegedInteractiveSecurityProofError,
        PrivilegedInteractiveSecurityProofRegistryError,
        TypeError,
        ValueError,
    ) as error:
        if isinstance(
            error,
            PrivilegedInteractiveSecurityProofPersistedInvalidError,
        ):
            raise

        raise (
            PrivilegedInteractiveSecurityProofPersistedInvalidError(
                "PERSISTED_SNAPSHOT_INVALID"
            )
        ) from error


def _same_logical_proof(
    first: PrivilegedInteractiveSecurityProof,
    second: PrivilegedInteractiveSecurityProof,
) -> bool:
    return (
        first.proof_id
        == second.proof_id
        and first.principal_id
        == second.principal_id
        and first.factor_verification_reference
        == second.factor_verification_reference
        and first.authenticated_at
        == second.authenticated_at
        and first.credential_revision
        == second.credential_revision
        and first.session_reference
        == second.session_reference
        and first.proof_reference
        == second.proof_reference
    )


def _terminal(
    status: PrivilegedInteractiveProofStatus,
) -> bool:
    return status in {
        PrivilegedInteractiveProofStatus.REVOKED,
        PrivilegedInteractiveProofStatus.INVALIDATED,
    }


def _transient_or_raise(
    error: PyMongoError,
) -> None:
    if error.has_error_label(
        "TransientTransactionError"
    ):
        raise error


class PrivilegedInteractiveSecurityProofRegistry:
    """Immutable revision-chain registry for interactive security proofs."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        if collection is None:
            raise (
                PrivilegedInteractiveSecurityProofPersistenceError(
                    "COLLECTION_REQUIRED"
                )
            )

        self._collection = collection

    def ensure_indexes(
        self,
    ) -> None:
        indexes = (
            (
                [
                    (
                        "proof_id",
                        ASCENDING,
                    ),
                    (
                        "revision",
                        ASCENDING,
                    ),
                ],
                True,
                PROOF_REVISION_INDEX,
            ),
            (
                [
                    (
                        "proof_reference",
                        ASCENDING,
                    ),
                    (
                        "revision",
                        ASCENDING,
                    ),
                ],
                True,
                PROOF_REFERENCE_REVISION_INDEX,
            ),
            (
                [
                    (
                        "factor_verification_reference",
                        ASCENDING,
                    ),
                    (
                        "revision",
                        ASCENDING,
                    ),
                ],
                True,
                FACTOR_REFERENCE_REVISION_INDEX,
            ),
            (
                [
                    (
                        "proof_id",
                        ASCENDING,
                    ),
                    (
                        "idempotency_key",
                        ASCENDING,
                    ),
                ],
                True,
                PROOF_IDEMPOTENCY_INDEX,
            ),
            (
                [
                    (
                        "principal_id",
                        ASCENDING,
                    ),
                    (
                        "authenticated_at",
                        ASCENDING,
                    ),
                ],
                False,
                PRINCIPAL_AUTHENTICATED_TIMELINE_INDEX,
            ),
            (
                [
                    (
                        "session_reference",
                        ASCENDING,
                    ),
                    (
                        "revision",
                        ASCENDING,
                    ),
                ],
                False,
                SESSION_REVISION_INDEX,
            ),
            (
                [
                    (
                        "proof_status",
                        ASCENDING,
                    ),
                    (
                        "status_changed_at",
                        ASCENDING,
                    ),
                ],
                False,
                STATUS_CHANGED_TIMELINE_INDEX,
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
                PrivilegedInteractiveSecurityProofPersistenceError(
                    "COLLECTION_INTERFACE_INVALID"
                )
            ) from error
        except PyMongoError as error:
            _transient_or_raise(error)

            raise (
                PrivilegedInteractiveSecurityProofPersistenceError(
                    "INDEX_CREATION_FAILED"
                )
            ) from error

        # P3 logical source-reference identity guard.
        # Only revision 1 claims the global reference;
        # later revisions remain valid same-proof history.
        self._collection.create_index(
            [("proof_reference", ASCENDING)],
            unique=True,
            name=PROOF_REFERENCE_INITIAL_IDENTITY_INDEX,
            partialFilterExpression={
                "revision": 1,
            },
        )
        self._collection.create_index(
            [("factor_verification_reference", ASCENDING)],
            unique=True,
            name=FACTOR_REFERENCE_INITIAL_IDENTITY_INDEX,
            partialFilterExpression={
                "revision": 1,
            },
        )

    def _find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
        sort: list[tuple[str, int]] | None = None,
    ) -> object:
        try:
            if sort is None:
                return self._collection.find_one(
                    query,
                    session=session,
                )

            return self._collection.find_one(
                query,
                session=session,
                sort=sort,
            )

        except AttributeError as error:
            raise (
                PrivilegedInteractiveSecurityProofPersistenceError(
                    "COLLECTION_INTERFACE_INVALID"
                )
            ) from error
        except PyMongoError as error:
            _transient_or_raise(error)

            raise (
                PrivilegedInteractiveSecurityProofPersistenceError(
                    "PERSISTENCE_UNAVAILABLE"
                )
            ) from error

    def _current_query(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> PrivilegedInteractiveSecurityProofSnapshot | None:
        row = self._find_one(
            query,
            session=session,
            sort=[
                (
                    "revision",
                    DESCENDING,
                ),
            ],
        )

        if row is None:
            return None

        snapshot = _hydrate(
            row
        )

        self._assert_chain(
            snapshot.proof.proof_id,
            session=session,
        )

        return snapshot

    def get_current_by_proof_id(
        self,
        *,
        proof_id: str,
        session: object = None,
    ) -> PrivilegedInteractiveSecurityProofSnapshot | None:
        identity = _identifier(
            "proof_id",
            proof_id,
        )

        value = self._current_query(
            {
                "proof_id":
                    identity,
            },
            session=session,
        )

        if (
            value is not None
            and value.proof.proof_id
            != identity
        ):
            raise (
                PrivilegedInteractiveSecurityProofPersistedInvalidError(
                    "PROOF_ID_BINDING_MISMATCH"
                )
            )

        return value

    def get_current_by_proof_reference(
        self,
        *,
        proof_reference: str,
        session: object = None,
    ) -> PrivilegedInteractiveSecurityProofSnapshot | None:
        reference = _identifier(
            "proof_reference",
            proof_reference,
        )

        value = self._current_query(
            {
                "proof_reference":
                    reference,
            },
            session=session,
        )

        if (
            value is not None
            and value.proof.proof_reference
            != reference
        ):
            raise (
                PrivilegedInteractiveSecurityProofPersistedInvalidError(
                    "PROOF_REFERENCE_BINDING_MISMATCH"
                )
            )

        return value

    def get_current_by_factor_reference(
        self,
        *,
        factor_verification_reference: str,
        session: object = None,
    ) -> PrivilegedInteractiveSecurityProofSnapshot | None:
        reference = _identifier(
            "factor_verification_reference",
            factor_verification_reference,
        )

        value = self._current_query(
            {
                "factor_verification_reference":
                    reference,
            },
            session=session,
        )

        if (
            value is not None
            and value.proof.factor_verification_reference
            != reference
        ):
            raise (
                PrivilegedInteractiveSecurityProofPersistedInvalidError(
                    "FACTOR_REFERENCE_BINDING_MISMATCH"
                )
            )

        return value

    def get_history_by_proof_id(
        self,
        *,
        proof_id: str,
        session: object = None,
    ) -> tuple[
        PrivilegedInteractiveSecurityProofSnapshot,
        ...,
    ]:
        identity = _identifier(
            "proof_id",
            proof_id,
        )

        try:
            cursor = self._collection.find(
                {
                    "proof_id":
                        identity,
                },
                session=session,
            ).sort(
                "revision",
                ASCENDING,
            )

            rows = list(
                cursor
            )

        except AttributeError as error:
            raise (
                PrivilegedInteractiveSecurityProofPersistenceError(
                    "COLLECTION_INTERFACE_INVALID"
                )
            ) from error
        except PyMongoError as error:
            _transient_or_raise(error)

            raise (
                PrivilegedInteractiveSecurityProofPersistenceError(
                    "PERSISTENCE_UNAVAILABLE"
                )
            ) from error

        values = tuple(
            _hydrate(row)
            for row in rows
        )

        self._validate_chain(
            values
        )

        for value in values:
            if (
                value.proof.proof_id
                != identity
            ):
                raise (
                    PrivilegedInteractiveSecurityProofPersistedInvalidError(
                        "PROOF_HISTORY_BINDING_MISMATCH"
                    )
                )

        return values

    def _validate_chain(
        self,
        values: tuple[
            PrivilegedInteractiveSecurityProofSnapshot,
            ...,
        ],
    ) -> None:
        if not values:
            return

        first = values[0]

        if first.revision != 1:
            raise (
                PrivilegedInteractiveSecurityProofPersistedInvalidError(
                    "REVISION_CHAIN_MUST_START_AT_ONE"
                )
            )

        if (
            first.previous_snapshot_fingerprint
            is not None
        ):
            raise (
                PrivilegedInteractiveSecurityProofPersistedInvalidError(
                    "INITIAL_CHAIN_FINGERPRINT_INVALID"
                )
            )

        first.assert_integrity()

        baseline = first.proof

        previous = first

        for expected_revision, current in enumerate(
            values[1:],
            start=2,
        ):
            current.assert_integrity()

            if (
                current.revision
                != expected_revision
            ):
                raise (
                    PrivilegedInteractiveSecurityProofPersistedInvalidError(
                        "REVISION_CHAIN_GAP"
                    )
                )

            if (
                current
                .previous_snapshot_fingerprint
                != previous.snapshot_fingerprint
            ):
                raise (
                    PrivilegedInteractiveSecurityProofPersistedInvalidError(
                        "REVISION_CHAIN_FINGERPRINT_MISMATCH"
                    )
                )

            if not _same_logical_proof(
                baseline,
                current.proof,
            ):
                raise (
                    PrivilegedInteractiveSecurityProofPersistedInvalidError(
                        "LOGICAL_PROOF_BINDING_CHANGED"
                    )
                )

            if (
                previous.proof.proof_status
                is PrivilegedInteractiveProofStatus
                .VERIFIED
            ):
                if (
                    current.proof.proof_status
                    not in {
                        PrivilegedInteractiveProofStatus.REVOKED,
                        PrivilegedInteractiveProofStatus.INVALIDATED,
                    }
                ):
                    raise (
                        PrivilegedInteractiveSecurityProofPersistedInvalidError(
                            "ILLEGAL_STATUS_TRANSITION"
                        )
                    )
            else:
                raise (
                    PrivilegedInteractiveSecurityProofPersistedInvalidError(
                        "TERMINAL_STATUS_HAS_SUCCESSOR"
                    )
                )

            previous = current

    def _assert_chain(
        self,
        proof_id: str,
        *,
        session: object = None,
    ) -> None:
        self.get_history_by_proof_id(
            proof_id=proof_id,
            session=session,
        )

    def _idempotent_snapshot(
        self,
        *,
        proof_id: str,
        idempotency_key: str,
        session: object,
    ) -> PrivilegedInteractiveSecurityProofSnapshot | None:
        row = self._find_one(
            {
                "proof_id":
                    proof_id,
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

    def _insert(
        self,
        snapshot: PrivilegedInteractiveSecurityProofSnapshot,
        *,
        session: object,
    ) -> None:
        try:
            self._collection.insert_one(
                snapshot.to_persisted(),
                session=session,
            )

        except DuplicateKeyError as error:
            if error.has_error_label(
                "TransientTransactionError"
            ):
                raise

            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "DUPLICATE_KEY_CONFLICT"
                )
            ) from error

        except AttributeError as error:
            raise (
                PrivilegedInteractiveSecurityProofPersistenceError(
                    "COLLECTION_INTERFACE_INVALID"
                )
            ) from error

        except PyMongoError as error:
            _transient_or_raise(error)

            raise (
                PrivilegedInteractiveSecurityProofPersistenceError(
                    "PERSISTENCE_UNAVAILABLE"
                )
            ) from error

    def create_or_replay(
        self,
        proof: PrivilegedInteractiveSecurityProof,
        *,
        status_changed_at: datetime,
        idempotency_key: str,
        session: object,
    ) -> PrivilegedInteractiveSecurityProofSnapshot:
        tx = _active_transaction(
            session
        )

        if type(proof) is not (
            PrivilegedInteractiveSecurityProof
        ):
            raise (
                PrivilegedInteractiveSecurityProofPersistenceError(
                    "PROOF_REQUIRED"
                )
            )

        if (
            proof.proof_status
            is not
            PrivilegedInteractiveProofStatus
            .VERIFIED
        ):
            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "INITIAL_STATUS_MUST_BE_VERIFIED"
                )
            )

        changed = _timestamp(
            "status_changed_at",
            status_changed_at,
        )

        replay_key = _identifier(
            "idempotency_key",
            idempotency_key,
        )

        replay = self._idempotent_snapshot(
            proof_id=proof.proof_id,
            idempotency_key=replay_key,
            session=tx,
        )

        desired = _snapshot(
            proof=proof,
            revision=1,
            status_changed_at=
                changed,
            idempotency_key=
                replay_key,
            previous_snapshot_fingerprint=
                None,
        )

        if replay is not None:
            if replay == desired:
                return replay

            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
                )
            )

        current = self.get_current_by_proof_id(
            proof_id=proof.proof_id,
            session=tx,
        )

        if current is not None:
            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "PROOF_ID_COLLISION"
                )
            )

        by_reference = (
            self.get_current_by_proof_reference(
                proof_reference=
                    proof.proof_reference,
                session=tx,
            )
        )

        if by_reference is not None:
            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "PROOF_REFERENCE_COLLISION"
                )
            )

        by_factor = (
            self.get_current_by_factor_reference(
                factor_verification_reference=
                    proof
                    .factor_verification_reference,
                session=tx,
            )
        )

        if by_factor is not None:
            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "FACTOR_REFERENCE_COLLISION"
                )
            )

        self._insert(
            desired,
            session=tx,
        )

        return desired

    def transition_status(
        self,
        *,
        proof_id: str,
        target_status: PrivilegedInteractiveProofStatus,
        status_changed_at: datetime,
        idempotency_key: str,
        expected_revision: int,
        expected_snapshot_fingerprint: str,
        session: object,
    ) -> PrivilegedInteractiveSecurityProofSnapshot:
        tx = _active_transaction(
            session
        )

        identity = _identifier(
            "proof_id",
            proof_id,
        )

        if not isinstance(
            target_status,
            PrivilegedInteractiveProofStatus,
        ):
            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "TARGET_STATUS_INVALID"
                )
            )

        if target_status not in {
            PrivilegedInteractiveProofStatus.REVOKED,
            PrivilegedInteractiveProofStatus.INVALIDATED,
        }:
            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "TARGET_STATUS_NOT_TERMINAL"
                )
            )

        changed = _timestamp(
            "status_changed_at",
            status_changed_at,
        )

        replay_key = _identifier(
            "idempotency_key",
            idempotency_key,
        )

        revision = _revision(
            expected_revision
        )

        fingerprint = _identifier(
            "expected_snapshot_fingerprint",
            expected_snapshot_fingerprint,
        )

        if (
            _FINGERPRINT.fullmatch(
                fingerprint
            )
            is None
        ):
            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "EXPECTED_FINGERPRINT_INVALID"
                )
            )

        replay = self._idempotent_snapshot(
            proof_id=identity,
            idempotency_key=replay_key,
            session=tx,
        )

        if replay is not None:
            if (
                replay.revision
                == revision + 1
                and replay.proof.proof_status
                is target_status
                and replay.status_changed_at
                == changed
                and replay
                .previous_snapshot_fingerprint
                == fingerprint
            ):
                return replay

            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
                )
            )

        current = self.get_current_by_proof_id(
            proof_id=identity,
            session=tx,
        )

        if current is None:
            raise (
                PrivilegedInteractiveSecurityProofNotFoundError(
                    "PROOF_NOT_FOUND"
                )
            )

        if current.revision != revision:
            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "STALE_EXPECTED_REVISION"
                )
            )

        if (
            current.snapshot_fingerprint
            != fingerprint
        ):
            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "STALE_EXPECTED_FINGERPRINT"
                )
            )

        if _terminal(
            current.proof.proof_status
        ):
            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "TERMINAL_STATUS"
                )
            )

        if (
            current.proof.proof_status
            is not
            PrivilegedInteractiveProofStatus
            .VERIFIED
        ):
            raise (
                PrivilegedInteractiveSecurityProofConflictError(
                    "CURRENT_STATUS_INVALID"
                )
            )

        next_proof = (
            PrivilegedInteractiveSecurityProof(
                proof_id=
                    current.proof.proof_id,
                principal_id=
                    current.proof.principal_id,
                factor_verification_reference=
                    current
                    .proof
                    .factor_verification_reference,
                authenticated_at=
                    current.proof.authenticated_at,
                credential_revision=
                    current
                    .proof
                    .credential_revision,
                session_reference=
                    current
                    .proof
                    .session_reference,
                proof_status=
                    target_status,
                proof_reference=
                    current
                    .proof
                    .proof_reference,
            )
        )

        next_snapshot = _snapshot(
            proof=next_proof,
            revision=
                current.revision + 1,
            status_changed_at=
                changed,
            idempotency_key=
                replay_key,
            previous_snapshot_fingerprint=
                current.snapshot_fingerprint,
        )

        self._insert(
            next_snapshot,
            session=tx,
        )

        return next_snapshot


__all__ = [
    "VERSION",
    "SCHEMA",
    "COLLECTION",
    "PROOF_REVISION_INDEX",
    "PROOF_REFERENCE_REVISION_INDEX",
    "FACTOR_REFERENCE_REVISION_INDEX",
    "PROOF_IDEMPOTENCY_INDEX",
    "PRINCIPAL_AUTHENTICATED_TIMELINE_INDEX",
    "SESSION_REVISION_INDEX",
    "STATUS_CHANGED_TIMELINE_INDEX",
    "PrivilegedInteractiveSecurityProofSnapshot",
    "PrivilegedInteractiveSecurityProofRegistry",
    "PrivilegedInteractiveSecurityProofRegistryError",
    "PrivilegedInteractiveSecurityProofTransactionRequiredError",
    "PrivilegedInteractiveSecurityProofConflictError",
    "PrivilegedInteractiveSecurityProofNotFoundError",
    "PrivilegedInteractiveSecurityProofPersistedInvalidError",
    "PrivilegedInteractiveSecurityProofPersistenceError",
]
