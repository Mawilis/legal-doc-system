"""
Revisioned immutable registry for noninteractive privileged security proofs.

VERSION:
v1.0.0-P3-R3E-PRIVILEGED-NONINTERACTIVE-SECURITY-PROOF-REGISTRY

One logical proof is identified by proof_id.

Each lifecycle transition creates one immutable snapshot.

Initial:
    revision 1 = VERIFIED

Allowed:
    VERIFIED -> REVOKED
    VERIFIED -> INVALIDATED

REVOKED and INVALIDATED are terminal.

No in-place status mutation.
No TTL.
No current pointer.
Current snapshot = highest valid revision in one verified SHA3-512 chain.

Registry status alone never proves current P3 assurance.

Trusted-source currentness, principal currentness,
credential/attestation currentness, and proof-reference trust resolution
remain external to this registry.

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

from tools.eos.auth.privileged_noninteractive_security_proof import (
    PrivilegedNoninteractiveProofStatus,
    PrivilegedNoninteractiveSecurityProof,
    PrivilegedNoninteractiveSecurityProofError,
)


VERSION: Final[str] = (
    "v1.0.0-P3-R3E-"
    "PRIVILEGED-NONINTERACTIVE-SECURITY-PROOF-REGISTRY"
)

SCHEMA: Final[str] = (
    "WILSY-PRIVILEGED-NONINTERACTIVE-SECURITY-PROOF-SNAPSHOT/V1"
)

COLLECTION: Final[str] = (
    "privileged_noninteractive_security_proof_snapshots"
)

PROOF_REVISION_INDEX: Final[str] = (
    "privileged_noninteractive_proof_revision_unique"
)

PROOF_REFERENCE_REVISION_INDEX: Final[str] = (
    "privileged_noninteractive_proof_reference_revision_unique"
)

CREDENTIAL_ATTESTATION_REFERENCE_REVISION_INDEX: Final[str] = (
    "privileged_noninteractive_credential_attestation_revision_unique"
)

PROOF_IDEMPOTENCY_INDEX: Final[str] = (
    "privileged_noninteractive_proof_idempotency_unique"
)

PRINCIPAL_OBSERVED_TIMELINE_INDEX: Final[str] = (
    "privileged_noninteractive_principal_observed_timeline"
)

STATUS_CHANGED_TIMELINE_INDEX: Final[str] = (
    "privileged_noninteractive_status_changed_timeline"
)

_FINGERPRINT = re.compile(
    r"^[0-9a-f]{128}$"
)

PROOF_REFERENCE_INITIAL_IDENTITY_INDEX = "privileged_noninteractive_proof_reference_initial_identity"
CREDENTIAL_REFERENCE_INITIAL_IDENTITY_INDEX = "privileged_noninteractive_credential_reference_initial_identity"


class PrivilegedNoninteractiveSecurityProofRegistryError(
    RuntimeError
):
    """Base registry failure."""


class PrivilegedNoninteractiveSecurityProofTransactionRequiredError(
    PrivilegedNoninteractiveSecurityProofRegistryError
):
    """Caller did not supply an active transaction."""


class PrivilegedNoninteractiveSecurityProofConflictError(
    PrivilegedNoninteractiveSecurityProofRegistryError
):
    """Identity, replay, lifecycle, or concurrency conflict."""


class PrivilegedNoninteractiveSecurityProofNotFoundError(
    PrivilegedNoninteractiveSecurityProofRegistryError
):
    """Requested proof does not exist."""


class PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
    PrivilegedNoninteractiveSecurityProofRegistryError
):
    """Persisted snapshot or chain is invalid."""


class PrivilegedNoninteractiveSecurityProofPersistenceError(
    PrivilegedNoninteractiveSecurityProofRegistryError
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
            PrivilegedNoninteractiveSecurityProofPersistenceError(
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
            PrivilegedNoninteractiveSecurityProofPersistenceError(
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
            PrivilegedNoninteractiveSecurityProofPersistenceError(
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
            PrivilegedNoninteractiveSecurityProofTransactionRequiredError(
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
class PrivilegedNoninteractiveSecurityProofSnapshot:
    """One immutable lifecycle snapshot for one noninteractive proof."""

    proof: PrivilegedNoninteractiveSecurityProof
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
            PrivilegedNoninteractiveSecurityProof,
        ):
            raise (
                PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                    "PROOF_INVALID"
                )
            )

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

        previous = (
            self.previous_snapshot_fingerprint
        )

        if revision == 1:
            if previous is not None:
                raise (
                    PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                        "INITIAL_PREVIOUS_FINGERPRINT_MUST_BE_NULL"
                    )
                )

            if (
                self.proof.proof_status
                is not
                PrivilegedNoninteractiveProofStatus
                .VERIFIED
            ):
                raise (
                    PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
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
                    PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
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
                PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
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
            "proof_reference":
                proof.proof_reference,
            "credential_or_attestation_reference":
                proof
                .credential_or_attestation_reference,
            "observed_at":
                _canonical_time(
                    proof.observed_at
                ),
            "proof_status":
                proof.proof_status.value,
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
                PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
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
    proof: PrivilegedNoninteractiveSecurityProof,
    revision: int,
    status_changed_at: datetime,
    idempotency_key: str,
    previous_snapshot_fingerprint: str | None,
) -> PrivilegedNoninteractiveSecurityProofSnapshot:
    placeholder = "0" * 128

    candidate = (
        PrivilegedNoninteractiveSecurityProofSnapshot(
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
        PrivilegedNoninteractiveSecurityProofSnapshot(
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
) -> PrivilegedNoninteractiveSecurityProofSnapshot:
    if not isinstance(
        row,
        dict,
    ):
        raise (
            PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                "PERSISTED_SNAPSHOT_INVALID"
            )
        )

    clean = dict(row)
    clean.pop("_id", None)

    expected_fields = {
        "schema",
        "proof_id",
        "principal_id",
        "proof_reference",
        "credential_or_attestation_reference",
        "observed_at",
        "proof_status",
        "revision",
        "status_changed_at",
        "idempotency_key",
        "previous_snapshot_fingerprint",
        "snapshot_fingerprint",
    }

    if set(clean) != expected_fields:
        raise (
            PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                "PERSISTED_SHAPE_INVALID"
            )
        )

    if clean["schema"] != SCHEMA:
        raise (
            PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                "PERSISTED_SCHEMA_INVALID"
            )
        )

    try:
        observed_raw = clean[
            "observed_at"
        ]

        changed_raw = clean[
            "status_changed_at"
        ]

        if not isinstance(
            observed_raw,
            str,
        ):
            raise ValueError

        if not isinstance(
            changed_raw,
            str,
        ):
            raise ValueError

        observed = datetime.fromisoformat(
            observed_raw
        )

        changed = datetime.fromisoformat(
            changed_raw
        )

        if (
            _canonical_time(observed)
            != observed_raw
        ):
            raise ValueError

        if (
            _canonical_time(changed)
            != changed_raw
        ):
            raise ValueError

        proof = (
            PrivilegedNoninteractiveSecurityProof(
                proof_id=
                    clean["proof_id"],  # type: ignore[arg-type]
                principal_id=
                    clean["principal_id"],  # type: ignore[arg-type]
                proof_reference=
                    clean["proof_reference"],  # type: ignore[arg-type]
                credential_or_attestation_reference=
                    clean[
                        "credential_or_attestation_reference"
                    ],  # type: ignore[arg-type]
                observed_at=
                    observed,
                proof_status=
                    PrivilegedNoninteractiveProofStatus(
                        clean["proof_status"]  # type: ignore[arg-type]
                    ),
            )
        )

        snapshot = (
            PrivilegedNoninteractiveSecurityProofSnapshot(
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
        PrivilegedNoninteractiveSecurityProofError,
        PrivilegedNoninteractiveSecurityProofRegistryError,
        TypeError,
        ValueError,
    ) as error:
        if isinstance(
            error,
            PrivilegedNoninteractiveSecurityProofPersistedInvalidError,
        ):
            raise

        raise (
            PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                "PERSISTED_SNAPSHOT_INVALID"
            )
        ) from error


def _same_logical_proof(
    first: PrivilegedNoninteractiveSecurityProof,
    second: PrivilegedNoninteractiveSecurityProof,
) -> bool:
    return (
        first.proof_id
        == second.proof_id
        and first.principal_id
        == second.principal_id
        and first.proof_reference
        == second.proof_reference
        and first
        .credential_or_attestation_reference
        == second
        .credential_or_attestation_reference
        and first.observed_at
        == second.observed_at
    )


def _terminal(
    status: PrivilegedNoninteractiveProofStatus,
) -> bool:
    return status in {
        PrivilegedNoninteractiveProofStatus.REVOKED,
        PrivilegedNoninteractiveProofStatus.INVALIDATED,
    }


def _transient_or_raise(
    error: PyMongoError,
) -> None:
    if error.has_error_label(
        "TransientTransactionError"
    ):
        raise error


class PrivilegedNoninteractiveSecurityProofRegistry:
    """Immutable revision-chain registry for noninteractive security proofs."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        if collection is None:
            raise (
                PrivilegedNoninteractiveSecurityProofPersistenceError(
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
                        "credential_or_attestation_reference",
                        ASCENDING,
                    ),
                    (
                        "revision",
                        ASCENDING,
                    ),
                ],
                True,
                CREDENTIAL_ATTESTATION_REFERENCE_REVISION_INDEX,
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
                        "observed_at",
                        ASCENDING,
                    ),
                ],
                False,
                PRINCIPAL_OBSERVED_TIMELINE_INDEX,
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
                PrivilegedNoninteractiveSecurityProofPersistenceError(
                    "COLLECTION_INTERFACE_INVALID"
                )
            ) from error

        except PyMongoError as error:
            _transient_or_raise(
                error
            )

            raise (
                PrivilegedNoninteractiveSecurityProofPersistenceError(
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
            [("credential_or_attestation_reference", ASCENDING)],
            unique=True,
            name=CREDENTIAL_REFERENCE_INITIAL_IDENTITY_INDEX,
            partialFilterExpression={
                "revision": 1,
            },
        )

    def _find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
        sort: list[
            tuple[str, int]
        ] | None = None,
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
                PrivilegedNoninteractiveSecurityProofPersistenceError(
                    "COLLECTION_INTERFACE_INVALID"
                )
            ) from error

        except PyMongoError as error:
            _transient_or_raise(
                error
            )

            raise (
                PrivilegedNoninteractiveSecurityProofPersistenceError(
                    "PERSISTENCE_UNAVAILABLE"
                )
            ) from error

    def _current_query(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> (
        PrivilegedNoninteractiveSecurityProofSnapshot
        | None
    ):
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
    ) -> (
        PrivilegedNoninteractiveSecurityProofSnapshot
        | None
    ):
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
                PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                    "PROOF_ID_BINDING_MISMATCH"
                )
            )

        return value

    def get_current_by_proof_reference(
        self,
        *,
        proof_reference: str,
        session: object = None,
    ) -> (
        PrivilegedNoninteractiveSecurityProofSnapshot
        | None
    ):
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
                PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                    "PROOF_REFERENCE_BINDING_MISMATCH"
                )
            )

        return value

    def get_current_by_credential_or_attestation_reference(
        self,
        *,
        credential_or_attestation_reference: str,
        session: object = None,
    ) -> (
        PrivilegedNoninteractiveSecurityProofSnapshot
        | None
    ):
        reference = _identifier(
            "credential_or_attestation_reference",
            credential_or_attestation_reference,
        )

        value = self._current_query(
            {
                "credential_or_attestation_reference":
                    reference,
            },
            session=session,
        )

        if (
            value is not None
            and value.proof
            .credential_or_attestation_reference
            != reference
        ):
            raise (
                PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                    "CREDENTIAL_ATTESTATION_REFERENCE_BINDING_MISMATCH"
                )
            )

        return value

    def get_history_by_proof_id(
        self,
        *,
        proof_id: str,
        session: object = None,
    ) -> tuple[
        PrivilegedNoninteractiveSecurityProofSnapshot,
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
                PrivilegedNoninteractiveSecurityProofPersistenceError(
                    "COLLECTION_INTERFACE_INVALID"
                )
            ) from error

        except PyMongoError as error:
            _transient_or_raise(
                error
            )

            raise (
                PrivilegedNoninteractiveSecurityProofPersistenceError(
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
                    PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                        "PROOF_HISTORY_BINDING_MISMATCH"
                    )
                )

        return values

    def _validate_chain(
        self,
        values: tuple[
            PrivilegedNoninteractiveSecurityProofSnapshot,
            ...,
        ],
    ) -> None:
        if not values:
            return

        first = values[0]

        if first.revision != 1:
            raise (
                PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                    "REVISION_CHAIN_MUST_START_AT_ONE"
                )
            )

        if (
            first.previous_snapshot_fingerprint
            is not None
        ):
            raise (
                PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
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
                    PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                        "REVISION_CHAIN_GAP"
                    )
                )

            if (
                current.previous_snapshot_fingerprint
                != previous.snapshot_fingerprint
            ):
                raise (
                    PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                        "REVISION_CHAIN_FINGERPRINT_MISMATCH"
                    )
                )

            if not _same_logical_proof(
                baseline,
                current.proof,
            ):
                raise (
                    PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                        "LOGICAL_PROOF_BINDING_CHANGED"
                    )
                )

            if (
                previous.proof.proof_status
                is PrivilegedNoninteractiveProofStatus
                .VERIFIED
            ):
                if (
                    current.proof.proof_status
                    not in {
                        PrivilegedNoninteractiveProofStatus.REVOKED,
                        PrivilegedNoninteractiveProofStatus.INVALIDATED,
                    }
                ):
                    raise (
                        PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
                            "ILLEGAL_STATUS_TRANSITION"
                        )
                    )
            else:
                raise (
                    PrivilegedNoninteractiveSecurityProofPersistedInvalidError(
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
    ) -> (
        PrivilegedNoninteractiveSecurityProofSnapshot
        | None
    ):
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
        snapshot: PrivilegedNoninteractiveSecurityProofSnapshot,
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
                PrivilegedNoninteractiveSecurityProofConflictError(
                    "DUPLICATE_KEY_CONFLICT"
                )
            ) from error

        except AttributeError as error:
            raise (
                PrivilegedNoninteractiveSecurityProofPersistenceError(
                    "COLLECTION_INTERFACE_INVALID"
                )
            ) from error

        except PyMongoError as error:
            _transient_or_raise(
                error
            )

            raise (
                PrivilegedNoninteractiveSecurityProofPersistenceError(
                    "PERSISTENCE_UNAVAILABLE"
                )
            ) from error

    def create_or_replay(
        self,
        proof: PrivilegedNoninteractiveSecurityProof,
        *,
        status_changed_at: datetime,
        idempotency_key: str,
        session: object,
    ) -> PrivilegedNoninteractiveSecurityProofSnapshot:
        tx = _active_transaction(
            session
        )

        if type(proof) is not (
            PrivilegedNoninteractiveSecurityProof
        ):
            raise (
                PrivilegedNoninteractiveSecurityProofPersistenceError(
                    "PROOF_REQUIRED"
                )
            )

        if (
            proof.proof_status
            is not
            PrivilegedNoninteractiveProofStatus
            .VERIFIED
        ):
            raise (
                PrivilegedNoninteractiveSecurityProofConflictError(
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
            idempotency_key=
                replay_key,
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
                PrivilegedNoninteractiveSecurityProofConflictError(
                    "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
                )
            )

        current = self.get_current_by_proof_id(
            proof_id=
                proof.proof_id,
            session=tx,
        )

        if current is not None:
            raise (
                PrivilegedNoninteractiveSecurityProofConflictError(
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
                PrivilegedNoninteractiveSecurityProofConflictError(
                    "PROOF_REFERENCE_COLLISION"
                )
            )

        by_credential = (
            self
            .get_current_by_credential_or_attestation_reference(
                credential_or_attestation_reference=
                    proof
                    .credential_or_attestation_reference,
                session=tx,
            )
        )

        if by_credential is not None:
            raise (
                PrivilegedNoninteractiveSecurityProofConflictError(
                    "CREDENTIAL_ATTESTATION_REFERENCE_COLLISION"
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
        target_status: PrivilegedNoninteractiveProofStatus,
        status_changed_at: datetime,
        idempotency_key: str,
        expected_revision: int,
        expected_snapshot_fingerprint: str,
        session: object,
    ) -> PrivilegedNoninteractiveSecurityProofSnapshot:
        tx = _active_transaction(
            session
        )

        identity = _identifier(
            "proof_id",
            proof_id,
        )

        if not isinstance(
            target_status,
            PrivilegedNoninteractiveProofStatus,
        ):
            raise (
                PrivilegedNoninteractiveSecurityProofConflictError(
                    "TARGET_STATUS_INVALID"
                )
            )

        if target_status not in {
            PrivilegedNoninteractiveProofStatus.REVOKED,
            PrivilegedNoninteractiveProofStatus.INVALIDATED,
        }:
            raise (
                PrivilegedNoninteractiveSecurityProofConflictError(
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
                PrivilegedNoninteractiveSecurityProofConflictError(
                    "EXPECTED_FINGERPRINT_INVALID"
                )
            )

        replay = self._idempotent_snapshot(
            proof_id=identity,
            idempotency_key=
                replay_key,
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
                and replay.previous_snapshot_fingerprint
                == fingerprint
            ):
                return replay

            raise (
                PrivilegedNoninteractiveSecurityProofConflictError(
                    "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
                )
            )

        current = self.get_current_by_proof_id(
            proof_id=identity,
            session=tx,
        )

        if current is None:
            raise (
                PrivilegedNoninteractiveSecurityProofNotFoundError(
                    "PROOF_NOT_FOUND"
                )
            )

        if current.revision != revision:
            raise (
                PrivilegedNoninteractiveSecurityProofConflictError(
                    "STALE_EXPECTED_REVISION"
                )
            )

        if (
            current.snapshot_fingerprint
            != fingerprint
        ):
            raise (
                PrivilegedNoninteractiveSecurityProofConflictError(
                    "STALE_EXPECTED_FINGERPRINT"
                )
            )

        if _terminal(
            current.proof.proof_status
        ):
            raise (
                PrivilegedNoninteractiveSecurityProofConflictError(
                    "TERMINAL_STATUS"
                )
            )

        if (
            current.proof.proof_status
            is not
            PrivilegedNoninteractiveProofStatus
            .VERIFIED
        ):
            raise (
                PrivilegedNoninteractiveSecurityProofConflictError(
                    "CURRENT_STATUS_INVALID"
                )
            )

        next_proof = (
            PrivilegedNoninteractiveSecurityProof(
                proof_id=
                    current.proof.proof_id,
                principal_id=
                    current.proof.principal_id,
                proof_reference=
                    current.proof.proof_reference,
                credential_or_attestation_reference=
                    current
                    .proof
                    .credential_or_attestation_reference,
                observed_at=
                    current.proof.observed_at,
                proof_status=
                    target_status,
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
    "CREDENTIAL_ATTESTATION_REFERENCE_REVISION_INDEX",
    "PROOF_IDEMPOTENCY_INDEX",
    "PRINCIPAL_OBSERVED_TIMELINE_INDEX",
    "STATUS_CHANGED_TIMELINE_INDEX",
    "PrivilegedNoninteractiveSecurityProofSnapshot",
    "PrivilegedNoninteractiveSecurityProofRegistry",
    "PrivilegedNoninteractiveSecurityProofRegistryError",
    "PrivilegedNoninteractiveSecurityProofTransactionRequiredError",
    "PrivilegedNoninteractiveSecurityProofConflictError",
    "PrivilegedNoninteractiveSecurityProofNotFoundError",
    "PrivilegedNoninteractiveSecurityProofPersistedInvalidError",
    "PrivilegedNoninteractiveSecurityProofPersistenceError",
]
