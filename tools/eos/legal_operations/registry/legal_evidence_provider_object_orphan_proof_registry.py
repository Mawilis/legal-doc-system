"""WILSY OS — durable Legal Evidence provider-object orphan-proof registry.

TITLE: Legal Evidence Provider Object Orphan Proof Registry
VERSION: v1.0.0-L10A2R-C4D6D-B2-ORPHAN-PROOF-REGISTRY
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Persist one immutable, positively proved orphan fact for one exact
         tenant-scoped provider object version, with exact replay only.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_evidence_provider_object_orphan_proof_registry.py
COLLABORATION / OWNERSHIP:
    C4D6D-B1 owns the immutable positive orphan-proof domain fact and its
    deterministic fingerprint. C4D6D-B2 owns only durable persistence,
    strict hydration, exact replay and exact tenant-scoped retrieval of that
    already-proved fact. Later retention, legal-hold, disposition, deletion
    authorization and provider-mutation gates remain separate.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.0-L10A2R-C4D6D-B2 establishes immutable tenant-scoped orphan-proof
    durability, exact reference/fingerprint/provider-object uniqueness,
    active caller-owned transaction enforcement, strict B1 hydration,
    exact replay, divergent re-proof rejection, corruption rejection and
    zero TTL.

COMPLIANCE:
    Evidence durability only. Persistence does not itself prove orphan status;
    only a valid C4D6D-B1 LegalEvidenceProviderObjectOrphanProof may enter this
    registry. Registry absence is never orphan evidence and registry presence
    is never deletion authority.

SECURITY / PRIVACY POSTURE:
    Exact tenant-scoped durable forensic evidence. Cross-tenant absence remains
    indistinguishable from not-found. No provider credentials, raw file bytes,
    financial truth, retention conclusion, legal-hold release, delete command
    or provider mutation is accepted or produced.

TENANT BOUNDARY:
    Every operational identity and lookup is exact tenant scoped.

AUTHORITY BOUNDARY:
    Durable persistence and replay of already-proved B1 orphan evidence only.
    This registry does not create orphan proof from absence, does not re-prove
    provider state, and does not authorize retention disposition, legal-hold
    release, abort, deletion or provider mutation.

TRANSACTION BOUNDARY:
    Caller owns one already-active Mongo transaction. This registry never
    starts, commits, aborts or retries a transaction. Duplicate-key write races
    require the caller to abort and retry the whole transaction from fresh
    state.

TTL POSTURE:
    No TTL index is permitted. Forensic evidence is not wall-clock disposable.

FINANCIAL AUTHORITY BOUNDARY:
    No pricing, billing, payment, execution or settlement authority.
    Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_evidence_provider_object_orphan_proof import (
    LegalEvidenceProviderObjectOrphanProof,
    LegalEvidenceProviderObjectOrphanProofError,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D6D-B2-ORPHAN-PROOF-REGISTRY"
)

COLLECTION: Final[str] = (
    "legal_evidence_provider_object_orphan_proofs"
)

INDEX_TENANT_REFERENCE: Final[str] = (
    "legal_evidence_orphan_proof_tenant_reference_unique"
)

INDEX_TENANT_FINGERPRINT: Final[str] = (
    "legal_evidence_orphan_proof_tenant_fingerprint_unique"
)

INDEX_TENANT_PROVIDER_OBJECT: Final[str] = (
    "legal_evidence_orphan_proof_tenant_provider_object_unique"
)


class LegalEvidenceProviderObjectOrphanProofRegistryError(
    RuntimeError
):
    """Base durable orphan-proof registry failure."""


class LegalEvidenceProviderObjectOrphanProofTransactionRequiredError(
    LegalEvidenceProviderObjectOrphanProofRegistryError
):
    """Caller did not provide one already-active Mongo transaction."""


class LegalEvidenceProviderObjectOrphanProofConflictError(
    LegalEvidenceProviderObjectOrphanProofRegistryError
):
    """Immutable orphan-proof identity was reused for divergent evidence."""


class LegalEvidenceProviderObjectOrphanProofNotFoundError(
    LegalEvidenceProviderObjectOrphanProofRegistryError
):
    """Exact tenant-scoped durable orphan proof was not found."""


class LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError(
    LegalEvidenceProviderObjectOrphanProofRegistryError
):
    """Persisted orphan-proof evidence is malformed, corrupt or divergent."""


class LegalEvidenceProviderObjectOrphanProofPersistenceError(
    LegalEvidenceProviderObjectOrphanProofRegistryError
):
    """Mongo persistence or collection interaction failed."""


def _raise(
    error_type: type[LegalEvidenceProviderObjectOrphanProofRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable structured B2 registry error."""

    error = error_type(code)

    if cause is None:
        raise error

    raise error from cause


def _active_transaction(
    session: Any,
) -> Any:
    """Return caller session only when one active transaction already exists."""

    if session is None:
        _raise(
            LegalEvidenceProviderObjectOrphanProofTransactionRequiredError,
            "L10A2R_C4D6D_B2_ACTIVE_TRANSACTION_REQUIRED",
        )

    try:
        active = getattr(
            session,
            "in_transaction",
        )
    except (AttributeError, TypeError) as error:
        _raise(
            LegalEvidenceProviderObjectOrphanProofTransactionRequiredError,
            "L10A2R_C4D6D_B2_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )

    if active is not True:
        _raise(
            LegalEvidenceProviderObjectOrphanProofTransactionRequiredError,
            "L10A2R_C4D6D_B2_ACTIVE_TRANSACTION_REQUIRED",
        )

    return session


def _target(
    collection: Any,
) -> Any:
    """Return one collection-like target or fail closed."""

    if collection is None:
        _raise(
            LegalEvidenceProviderObjectOrphanProofPersistenceError,
            "L10A2R_C4D6D_B2_COLLECTION_INTERFACE_INVALID",
        )

    return collection


def _document(
    value: LegalEvidenceProviderObjectOrphanProof,
) -> dict[str, object]:
    """Return exact durable B1 document after strict self-hydration validation."""

    if not isinstance(
        value,
        LegalEvidenceProviderObjectOrphanProof,
    ):
        _raise(
            LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
            "L10A2R_C4D6D_B2_VALUE_REQUIRED",
        )

    try:
        document = value.to_dict()
        hydrated = LegalEvidenceProviderObjectOrphanProof.from_dict(
            document
        )
    except LegalEvidenceProviderObjectOrphanProofError as error:
        _raise(
            LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
            "L10A2R_C4D6D_B2_VALUE_INVALID",
            error,
        )
    except (AttributeError, TypeError, ValueError) as error:
        _raise(
            LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
            "L10A2R_C4D6D_B2_VALUE_INVALID",
            error,
        )

    if hydrated != value:
        _raise(
            LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
            "L10A2R_C4D6D_B2_VALUE_DIVERGED",
        )

    return dict(document)


def _hydrate(
    row: object,
) -> LegalEvidenceProviderObjectOrphanProof:
    """Hydrate exactly one persisted B1 proof without healing corruption."""

    if not isinstance(
        row,
        dict,
    ):
        _raise(
            LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
            "L10A2R_C4D6D_B2_PERSISTED_RECORD_INVALID",
        )

    document = {
        key: value
        for key, value in row.items()
        if key != "_id"
    }

    try:
        return LegalEvidenceProviderObjectOrphanProof.from_dict(
            document
        )
    except LegalEvidenceProviderObjectOrphanProofError as error:
        _raise(
            LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
            "L10A2R_C4D6D_B2_PERSISTED_RECORD_INVALID",
            error,
        )
    except (AttributeError, TypeError, ValueError) as error:
        _raise(
            LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
            "L10A2R_C4D6D_B2_PERSISTED_RECORD_INVALID",
            error,
        )


def _same(
    expected: LegalEvidenceProviderObjectOrphanProof,
    row: object,
) -> LegalEvidenceProviderObjectOrphanProof:
    """Require one persisted row to equal one exact immutable B1 proof."""

    actual = _hydrate(
        row
    )

    if actual != expected:
        _raise(
            LegalEvidenceProviderObjectOrphanProofConflictError,
            "L10A2R_C4D6D_B2_IMMUTABLE_DIVERGENCE",
        )

    return actual


class LegalEvidenceProviderObjectOrphanProofRegistry:
    """Immutable tenant-scoped durable B1 orphan-proof evidence registry."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        """Bind this registry to one collection-like persistence target."""

        self._collection = _target(
            collection
        )

    def ensure_indexes(
        self,
    ) -> None:
        """Create exact immutable identities; never create TTL deletion."""

        try:
            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "orphan_proof_reference",
                        ASCENDING,
                    ),
                ],
                unique=True,
                name=INDEX_TENANT_REFERENCE,
            )

            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "fingerprint",
                        ASCENDING,
                    ),
                ],
                unique=True,
                name=INDEX_TENANT_FINGERPRINT,
            )

            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "provider_name",
                        ASCENDING,
                    ),
                    (
                        "storage_reference",
                        ASCENDING,
                    ),
                    (
                        "object_version_reference",
                        ASCENDING,
                    ),
                ],
                unique=True,
                name=INDEX_TENANT_PROVIDER_OBJECT,
            )
        except PyMongoError as error:
            _raise(
                LegalEvidenceProviderObjectOrphanProofPersistenceError,
                "L10A2R_C4D6D_B2_INDEX_CREATION_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceProviderObjectOrphanProofPersistenceError,
                "L10A2R_C4D6D_B2_COLLECTION_INTERFACE_INVALID",
                error,
            )

    def _find_identity_rows(
        self,
        value: LegalEvidenceProviderObjectOrphanProof,
        *,
        session: Any,
    ) -> tuple[object | None, object | None, object | None]:
        """Read all immutable identity surfaces for replay/conflict adjudication."""

        try:
            by_reference = self._collection.find_one(
                {
                    "tenant_id":
                        value.tenant_id,
                    "orphan_proof_reference":
                        value.orphan_proof_reference,
                },
                session=session,
            )

            by_fingerprint = self._collection.find_one(
                {
                    "tenant_id":
                        value.tenant_id,
                    "fingerprint":
                        value.fingerprint,
                },
                session=session,
            )

            by_provider_object = self._collection.find_one(
                {
                    "tenant_id":
                        value.tenant_id,
                    "provider_name":
                        value.provider_name,
                    "storage_reference":
                        value.storage_reference,
                    "object_version_reference":
                        value.object_version_reference,
                },
                session=session,
            )
        except PyMongoError as error:
            _raise(
                LegalEvidenceProviderObjectOrphanProofPersistenceError,
                "L10A2R_C4D6D_B2_READ_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceProviderObjectOrphanProofPersistenceError,
                "L10A2R_C4D6D_B2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        return (
            by_reference,
            by_fingerprint,
            by_provider_object,
        )

    def create_or_replay(
        self,
        value: LegalEvidenceProviderObjectOrphanProof,
        *,
        session: Any,
    ) -> LegalEvidenceProviderObjectOrphanProof:
        """Persist once or return one exact immutable B1 replay.

        The caller must already own an active Mongo transaction. Exact replay
        is permitted only when every occupied immutable identity resolves to
        the same B1 value. Any divergent reference, fingerprint or exact
        provider-object identity fails closed. Duplicate-key races require a
        whole-transaction retry by the caller.
        """

        tx = _active_transaction(
            session
        )

        document = _document(
            value
        )

        rows = self._find_identity_rows(
            value,
            session=tx,
        )

        present = tuple(
            row
            for row in rows
            if row is not None
        )

        if present:
            hydrated = tuple(
                _same(
                    value,
                    row,
                )
                for row in present
            )

            first = hydrated[0]

            if any(
                item != first
                for item in hydrated[1:]
            ):
                _raise(
                    LegalEvidenceProviderObjectOrphanProofConflictError,
                    "L10A2R_C4D6D_B2_IDENTITY_ROWS_DIVERGE",
                )

            return first

        try:
            result = self._collection.insert_one(
                document,
                session=tx,
            )

            if getattr(
                result,
                "acknowledged",
                False,
            ) is not True:
                _raise(
                    LegalEvidenceProviderObjectOrphanProofPersistenceError,
                    "L10A2R_C4D6D_B2_INSERT_NOT_ACKNOWLEDGED",
                )

        except DuplicateKeyError as error:
            _raise(
                LegalEvidenceProviderObjectOrphanProofConflictError,
                "L10A2R_C4D6D_B2_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )
        except LegalEvidenceProviderObjectOrphanProofRegistryError:
            raise
        except PyMongoError as error:
            _raise(
                LegalEvidenceProviderObjectOrphanProofPersistenceError,
                "L10A2R_C4D6D_B2_INSERT_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceProviderObjectOrphanProofPersistenceError,
                "L10A2R_C4D6D_B2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        return value

    def get_by_reference(
        self,
        *,
        tenant_id: str,
        orphan_proof_reference: str,
        session: Any,
    ) -> LegalEvidenceProviderObjectOrphanProof:
        """Return exact tenant+orphan-proof-reference durable evidence."""

        tx = _active_transaction(
            session
        )

        if (
            not isinstance(
                tenant_id,
                str,
            )
            or not tenant_id
            or not isinstance(
                orphan_proof_reference,
                str,
            )
            or not orphan_proof_reference
        ):
            _raise(
                LegalEvidenceProviderObjectOrphanProofNotFoundError,
                "L10A2R_C4D6D_B2_NOT_FOUND",
            )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id":
                        tenant_id,
                    "orphan_proof_reference":
                        orphan_proof_reference,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                LegalEvidenceProviderObjectOrphanProofPersistenceError,
                "L10A2R_C4D6D_B2_READ_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceProviderObjectOrphanProofPersistenceError,
                "L10A2R_C4D6D_B2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if row is None:
            _raise(
                LegalEvidenceProviderObjectOrphanProofNotFoundError,
                "L10A2R_C4D6D_B2_NOT_FOUND",
            )

        value = _hydrate(
            row
        )

        if (
            value.tenant_id != tenant_id
            or value.orphan_proof_reference
            != orphan_proof_reference
        ):
            _raise(
                LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
                "L10A2R_C4D6D_B2_PERSISTED_SCOPE_MISMATCH",
            )

        return value

    def get_by_provider_object(
        self,
        *,
        tenant_id: str,
        provider_name: str,
        storage_reference: str,
        object_version_reference: str,
        session: Any,
    ) -> LegalEvidenceProviderObjectOrphanProof:
        """Return one exact tenant-scoped provider-object orphan-proof fact."""

        tx = _active_transaction(
            session
        )

        identity = (
            tenant_id,
            provider_name,
            storage_reference,
            object_version_reference,
        )

        if any(
            not isinstance(
                item,
                str,
            )
            or not item
            for item in identity
        ):
            _raise(
                LegalEvidenceProviderObjectOrphanProofNotFoundError,
                "L10A2R_C4D6D_B2_NOT_FOUND",
            )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id":
                        tenant_id,
                    "provider_name":
                        provider_name,
                    "storage_reference":
                        storage_reference,
                    "object_version_reference":
                        object_version_reference,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                LegalEvidenceProviderObjectOrphanProofPersistenceError,
                "L10A2R_C4D6D_B2_READ_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceProviderObjectOrphanProofPersistenceError,
                "L10A2R_C4D6D_B2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if row is None:
            _raise(
                LegalEvidenceProviderObjectOrphanProofNotFoundError,
                "L10A2R_C4D6D_B2_NOT_FOUND",
            )

        value = _hydrate(
            row
        )

        if (
            value.tenant_id != tenant_id
            or value.provider_name != provider_name
            or value.storage_reference != storage_reference
            or value.object_version_reference
            != object_version_reference
        ):
            _raise(
                LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError,
                "L10A2R_C4D6D_B2_PERSISTED_SCOPE_MISMATCH",
            )

        return value


__all__ = [
    "COLLECTION",
    "INDEX_TENANT_FINGERPRINT",
    "INDEX_TENANT_PROVIDER_OBJECT",
    "INDEX_TENANT_REFERENCE",
    "VERSION",
    "LegalEvidenceProviderObjectOrphanProofConflictError",
    "LegalEvidenceProviderObjectOrphanProofNotFoundError",
    "LegalEvidenceProviderObjectOrphanProofPersistedRecordInvalidError",
    "LegalEvidenceProviderObjectOrphanProofPersistenceError",
    "LegalEvidenceProviderObjectOrphanProofRegistry",
    "LegalEvidenceProviderObjectOrphanProofRegistryError",
    "LegalEvidenceProviderObjectOrphanProofTransactionRequiredError",
]


# ARTIFACT: legal_evidence_provider_object_orphan_proof_registry.py
# VERSION: v1.0.0-L10A2R-C4D6D-B2-ORPHAN-PROOF-REGISTRY
# AUTHORITY BOUNDARY: durable persistence/replay of already-proved B1 orphan evidence only
# TENANT POSTURE: all durable identities and reads are exact tenant scoped
# PROVIDER OBJECT POSTURE: one immutable orphan-proof fact per exact object version
# TRANSACTION POSTURE: caller owns one already-active Mongo transaction
# REPLAY POSTURE: exact immutable replay only; divergent re-proof fails closed
# CORRUPTION POSTURE: strict B1 hydration; persisted corruption is never healed
# TTL POSTURE: no TTL index or wall-clock deletion
# ORPHAN POSTURE: registry persistence does not infer or create orphan proof
# RETENTION / HOLD POSTURE: no retention satisfaction or legal-hold release authority
# DELETION POSTURE: no abort, delete authorization, update/delete mutator or provider mutation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# FAIL-CLOSED POSTURE: transaction absence, divergence, corruption and Mongo failure reject
# END OF WILSY OS SOVEREIGN ARTIFACT
