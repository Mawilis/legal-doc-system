"""WILSY OS — Legal Evidence Provider Cleanup Command Registry.

TITLE: Legal Evidence Provider Cleanup Command Registry
VERSION: v1.0.1-L10A2R-C4D6E-A3-P3-P2-CLEANUP-COMMAND-REGISTRY
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Durably preserve one immutable cleanup command intent per exact
         tenant/provider/storage/object-version cleanup boundary.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_evidence_provider_cleanup_command_registry.py
COLLABORATION / OWNERSHIP: Legal Operations / Legal Evidence
CERTIFICATION / UPDATE DATE: 2026-10-02
CHANGELOG:
    v1.0.1 classifies Mongo TransientTransactionError conditions as requiring
    caller abort plus fresh whole-transaction restart, preserving the same
    fail-closed retry boundary already required for duplicate-key races.
    v1.0.0 establishes caller-transaction-owned durable persistence for the
    certified cleanup-command domain, with strict domain hydration, exact
    tenant-scoped replay, immutable command/fingerprint/object uniqueness,
    no TTL deletion and whole-transaction retry requirements for duplicate
    races.
COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE:
    Persists only the canonical cleanup-command document: opaque identities,
    exact provider-object references and SHA3-512 evidence fingerprints.
    Corrupt, divergent or cross-identity durable state rejects fail closed.
TENANT BOUNDARY:
    Every durable identity, replay reconciliation and lookup is explicitly
    tenant scoped. No global lookup or cross-tenant existence oracle exists.
AUTHORITY BOUNDARY:
    Durable cleanup-command intent only. Persistence does not authorize or
    execute provider deletion, mutate provider storage, prove deletion,
    release retention/legal-hold constraints or create financial authority.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains the exclusive financial execution authority.

TRANSACTION CONTRACT:
    The caller owns start / commit / abort. Every durable read and write
    requires one already-active caller transaction.

IDEMPOTENCY CONTRACT:
    Same tenant-scoped command identity, command fingerprint, cleanup-
    authorization identity or exact provider-object identity may replay only
    the exact same immutable command. Divergence fails closed.

RETRY CONTRACT:
    A Mongo duplicate-key race invalidates the current transaction. The
    registry never reconciles inside the failed transaction; the caller must
    abort and restart the whole transaction from fresh state.

TTL CONTRACT:
    Cleanup command evidence is immutable command evidence. No TTL deletion
    index is created.

FAIL-CLOSED DECLARATION:
    Missing/inactive transaction, wrong domain type, malformed or corrupt
    durable data, identity divergence, collection failure and duplicate races
    reject without inventing command, provider-execution or settlement truth.
"""

from __future__ import annotations

from typing import Any, Final

from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_command import (
    LegalEvidenceProviderCleanupCommand,
    LegalEvidenceProviderCleanupCommandError,
)


VERSION: Final[str] = (
    "v1.0.1-L10A2R-C4D6E-A3-P3-P2-CLEANUP-COMMAND-REGISTRY"
)

COLLECTION: Final[str] = "legal_evidence_provider_cleanup_commands"

INDEX_TENANT_COMMAND_ID: Final[str] = (
    "legal_evidence_cleanup_command_tenant_command_id_unique"
)
INDEX_TENANT_FINGERPRINT: Final[str] = (
    "legal_evidence_cleanup_command_tenant_fingerprint_unique"
)
INDEX_TENANT_CLEANUP_AUTHORIZATION: Final[str] = (
    "legal_evidence_cleanup_command_tenant_cleanup_authorization_unique"
)
INDEX_TENANT_PROVIDER_OBJECT: Final[str] = (
    "legal_evidence_cleanup_command_tenant_provider_object_unique"
)


class LegalEvidenceProviderCleanupCommandRegistryError(RuntimeError):
    """Base fail-closed durable cleanup-command registry error."""


class LegalEvidenceProviderCleanupCommandRegistryTransactionError(
    LegalEvidenceProviderCleanupCommandRegistryError
):
    """Caller did not provide one already-active transaction."""


class LegalEvidenceProviderCleanupCommandRegistryIntegrityError(
    LegalEvidenceProviderCleanupCommandRegistryError
):
    """Persisted command evidence is corrupt, divergent or inconsistent."""


class LegalEvidenceProviderCleanupCommandRegistryPersistenceError(
    LegalEvidenceProviderCleanupCommandRegistryError
):
    """Mongo-style persistence or collection interaction failed."""


class LegalEvidenceProviderCleanupCommandRegistryRetryRequiredError(
    LegalEvidenceProviderCleanupCommandRegistryIntegrityError
):
    """Failed Mongo transaction must abort and restart from fresh state."""


def _active_transaction(
    session: Any,
) -> Any:
    """Require one already-active caller-owned transaction."""
    if session is None:
        raise LegalEvidenceProviderCleanupCommandRegistryTransactionError(
            "L10A2R_C4D6E_A3_P3_P2_ACTIVE_TRANSACTION_REQUIRED"
        )

    marker = getattr(session, "in_transaction", False)

    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False

    if active is not True:
        raise LegalEvidenceProviderCleanupCommandRegistryTransactionError(
            "L10A2R_C4D6E_A3_P3_P2_ACTIVE_TRANSACTION_REQUIRED"
        )

    return session


def _target(
    collection: Any,
) -> Any:
    """Require one collection-like durable persistence target."""
    if collection is None:
        raise LegalEvidenceProviderCleanupCommandRegistryPersistenceError(
            "L10A2R_C4D6E_A3_P3_P2_COLLECTION_REQUIRED"
        )
    return collection


def _value(
    command: LegalEvidenceProviderCleanupCommand,
) -> LegalEvidenceProviderCleanupCommand:
    """Require the exact certified cleanup-command domain type."""
    if type(command) is not LegalEvidenceProviderCleanupCommand:
        raise LegalEvidenceProviderCleanupCommandRegistryIntegrityError(
            "L10A2R_C4D6E_A3_P3_P2_COMMAND_REQUIRED"
        )
    return command


def _document(
    command: LegalEvidenceProviderCleanupCommand,
) -> dict[str, object]:
    """Return one strict round-tripped durable cleanup-command document."""
    try:
        document = command.to_document()
        hydrated = LegalEvidenceProviderCleanupCommand.from_dict(
            dict(document)
        )
    except LegalEvidenceProviderCleanupCommandError as error:
        raise LegalEvidenceProviderCleanupCommandRegistryIntegrityError(
            "L10A2R_C4D6E_A3_P3_P2_COMMAND_INVALID"
        ) from error

    if (
        hydrated != command
        or hydrated.fingerprint != command.fingerprint
        or hydrated.to_document() != document
    ):
        raise LegalEvidenceProviderCleanupCommandRegistryIntegrityError(
            "L10A2R_C4D6E_A3_P3_P2_COMMAND_ROUND_TRIP_INVALID"
        )

    return document


def _hydrate(
    row: object,
) -> LegalEvidenceProviderCleanupCommand:
    """Strictly hydrate one Mongo-style row and reject corruption."""
    if not isinstance(row, dict):
        raise LegalEvidenceProviderCleanupCommandRegistryIntegrityError(
            "L10A2R_C4D6E_A3_P3_P2_PERSISTED_DOCUMENT_INVALID"
        )

    document = dict(row)
    document.pop("_id", None)

    try:
        return LegalEvidenceProviderCleanupCommand.from_dict(
            document
        )
    except (
        LegalEvidenceProviderCleanupCommandError,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        raise LegalEvidenceProviderCleanupCommandRegistryIntegrityError(
            "L10A2R_C4D6E_A3_P3_P2_PERSISTED_DOCUMENT_CORRUPT"
        ) from error


def _same(
    left: LegalEvidenceProviderCleanupCommand,
    right: LegalEvidenceProviderCleanupCommand,
) -> bool:
    """Compare exact immutable command evidence."""
    return (
        left == right
        and left.fingerprint == right.fingerprint
        and left.to_document() == right.to_document()
    )


def _whole_transaction_retry_required(
    error: BaseException,
) -> bool:
    """Recognize Mongo conditions requiring fresh whole-transaction restart.

    Duplicate-key races and driver-labelled transient transaction failures
    cannot be reconciled inside the failed transaction. The caller must abort
    and restart the whole transaction from fresh state.
    """
    if error.__class__.__name__ == "DuplicateKeyError":
        return True

    label_check = getattr(
        error,
        "has_error_label",
        None,
    )

    if callable(label_check):
        try:
            if label_check("TransientTransactionError") is True:
                return True
        except (AttributeError, TypeError, ValueError):
            pass

    details = getattr(
        error,
        "details",
        None,
    )

    if isinstance(details, dict):
        labels = details.get("errorLabels")
        if (
            isinstance(labels, list)
            and "TransientTransactionError" in labels
        ):
            return True

    return False


class LegalEvidenceProviderCleanupCommandRegistry:
    """Durable immutable cleanup-command intent registry.

    Transaction ownership:
        The caller owns one already-active transaction. This registry never
        starts, commits, aborts or retries transaction lifecycle.

    Tenant boundary:
        Every durable identity and lookup includes tenant_id.

    Mutation semantics:
        Append-once immutable cleanup command evidence only.

    Replay semantics:
        Any command-id, fingerprint, cleanup-authorization or provider-object
        collision may replay only when all durable command bytes are exact.

    Provider authority:
        None. Persistence does not authorize or execute provider deletion.

    Financial authority:
        None. Kennel EOS remains exclusive financial execution authority.
    """

    def __init__(
        self,
        collection: Any,
    ) -> None:
        """Bind one registry instance to one collection-like target."""
        self._collection = _target(collection)

    def ensure_indexes(self) -> None:
        """Create exact unique durable indexes and never create TTL."""
        try:
            self._collection.create_index(
                [
                    ("tenant_id", 1),
                    ("command_id", 1),
                ],
                unique=True,
                name=INDEX_TENANT_COMMAND_ID,
            )
            self._collection.create_index(
                [
                    ("tenant_id", 1),
                    ("fingerprint", 1),
                ],
                unique=True,
                name=INDEX_TENANT_FINGERPRINT,
            )
            self._collection.create_index(
                [
                    ("tenant_id", 1),
                    ("cleanup_authorization_id", 1),
                ],
                unique=True,
                name=INDEX_TENANT_CLEANUP_AUTHORIZATION,
            )
            self._collection.create_index(
                [
                    ("tenant_id", 1),
                    ("provider_name", 1),
                    ("storage_reference", 1),
                    ("object_version_reference", 1),
                ],
                unique=True,
                name=INDEX_TENANT_PROVIDER_OBJECT,
            )
        except (AttributeError, TypeError, ValueError) as error:
            raise LegalEvidenceProviderCleanupCommandRegistryPersistenceError(
                "L10A2R_C4D6E_A3_P3_P2_INDEX_CREATION_FAILED"
            ) from error

    def _existing(
        self,
        command: LegalEvidenceProviderCleanupCommand,
        *,
        session: Any,
    ) -> tuple[LegalEvidenceProviderCleanupCommand, ...]:
        """Read every immutable identity used for replay reconciliation."""
        queries = (
            {
                "tenant_id": command.tenant_id,
                "command_id": command.command_id,
            },
            {
                "tenant_id": command.tenant_id,
                "fingerprint": command.fingerprint,
            },
            {
                "tenant_id": command.tenant_id,
                "cleanup_authorization_id":
                    command.cleanup_authorization_id,
            },
            {
                "tenant_id": command.tenant_id,
                "provider_name": command.provider_name,
                "storage_reference": command.storage_reference,
                "object_version_reference":
                    command.object_version_reference,
            },
        )

        hydrated: list[LegalEvidenceProviderCleanupCommand] = []

        try:
            for query in queries:
                row = self._collection.find_one(
                    query,
                    session=session,
                )
                if row is not None:
                    hydrated.append(_hydrate(row))
        except LegalEvidenceProviderCleanupCommandRegistryError:
            raise
        except (AttributeError, TypeError, ValueError) as error:
            raise LegalEvidenceProviderCleanupCommandRegistryPersistenceError(
                "L10A2R_C4D6E_A3_P3_P2_COLLECTION_INTERFACE_INVALID"
            ) from error

        return tuple(hydrated)

    @staticmethod
    def _resolve_replay(
        requested: LegalEvidenceProviderCleanupCommand,
        existing: tuple[LegalEvidenceProviderCleanupCommand, ...],
    ) -> LegalEvidenceProviderCleanupCommand | None:
        """Return exact replay or reject any divergent durable identity."""
        if not existing:
            return None

        first = existing[0]

        if not _same(first, requested):
            raise LegalEvidenceProviderCleanupCommandRegistryIntegrityError(
                "L10A2R_C4D6E_A3_P3_P2_REPLAY_CONFLICT"
            )

        if any(
            not _same(first, item)
            for item in existing[1:]
        ):
            raise LegalEvidenceProviderCleanupCommandRegistryIntegrityError(
                "L10A2R_C4D6E_A3_P3_P2_DURABLE_IDENTITY_CONFLICT"
            )

        return first

    def create_or_replay(
        self,
        command: LegalEvidenceProviderCleanupCommand,
        *,
        session: Any,
    ) -> LegalEvidenceProviderCleanupCommand:
        """Persist once or return exact replay in caller transaction.

        Same tenant-scoped immutable identity may replay only exact command
        evidence. Divergence rejects. Duplicate-key races require the caller
        to abort the failed transaction and restart the whole transaction.
        """
        tx = _active_transaction(session)
        requested = _value(command)
        document = _document(requested)

        existing = self._existing(
            requested,
            session=tx,
        )
        replay = self._resolve_replay(
            requested,
            existing,
        )

        if replay is not None:
            return replay

        try:
            self._collection.insert_one(
                document,
                session=tx,
            )
        except Exception as error:
            if not _whole_transaction_retry_required(error):
                raise LegalEvidenceProviderCleanupCommandRegistryPersistenceError(
                    "L10A2R_C4D6E_A3_P3_P2_INSERT_FAILED"
                ) from error

            raise LegalEvidenceProviderCleanupCommandRegistryRetryRequiredError(
                "L10A2R_C4D6E_A3_P3_P2_WHOLE_TRANSACTION_RETRY_REQUIRED"
            ) from error

        return requested

    def get_by_command_id(
        self,
        *,
        tenant_id: str,
        command_id: str,
        session: Any,
    ) -> LegalEvidenceProviderCleanupCommand | None:
        """Read one exact tenant-scoped cleanup command identity."""
        tx = _active_transaction(session)

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant_id,
                    "command_id": command_id,
                },
                session=tx,
            )
        except (AttributeError, TypeError, ValueError) as error:
            raise LegalEvidenceProviderCleanupCommandRegistryPersistenceError(
                "L10A2R_C4D6E_A3_P3_P2_COLLECTION_INTERFACE_INVALID"
            ) from error

        if row is None:
            return None

        value = _hydrate(row)

        if (
            value.tenant_id != tenant_id
            or value.command_id != command_id
        ):
            raise LegalEvidenceProviderCleanupCommandRegistryIntegrityError(
                "L10A2R_C4D6E_A3_P3_P2_LOOKUP_IDENTITY_MISMATCH"
            )

        return value

    def get_by_fingerprint(
        self,
        *,
        tenant_id: str,
        fingerprint: str,
        session: Any,
    ) -> LegalEvidenceProviderCleanupCommand | None:
        """Read one exact tenant-scoped command fingerprint."""
        tx = _active_transaction(session)

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant_id,
                    "fingerprint": fingerprint,
                },
                session=tx,
            )
        except (AttributeError, TypeError, ValueError) as error:
            raise LegalEvidenceProviderCleanupCommandRegistryPersistenceError(
                "L10A2R_C4D6E_A3_P3_P2_COLLECTION_INTERFACE_INVALID"
            ) from error

        if row is None:
            return None

        value = _hydrate(row)

        if (
            value.tenant_id != tenant_id
            or value.fingerprint != fingerprint
        ):
            raise LegalEvidenceProviderCleanupCommandRegistryIntegrityError(
                "L10A2R_C4D6E_A3_P3_P2_LOOKUP_IDENTITY_MISMATCH"
            )

        return value

    def get_by_cleanup_authorization_id(
        self,
        *,
        tenant_id: str,
        cleanup_authorization_id: str,
        session: Any,
    ) -> LegalEvidenceProviderCleanupCommand | None:
        """Read command intent for one exact tenant cleanup authorization."""
        tx = _active_transaction(session)

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant_id,
                    "cleanup_authorization_id":
                        cleanup_authorization_id,
                },
                session=tx,
            )
        except (AttributeError, TypeError, ValueError) as error:
            raise LegalEvidenceProviderCleanupCommandRegistryPersistenceError(
                "L10A2R_C4D6E_A3_P3_P2_COLLECTION_INTERFACE_INVALID"
            ) from error

        if row is None:
            return None

        value = _hydrate(row)

        if (
            value.tenant_id != tenant_id
            or value.cleanup_authorization_id
            != cleanup_authorization_id
        ):
            raise LegalEvidenceProviderCleanupCommandRegistryIntegrityError(
                "L10A2R_C4D6E_A3_P3_P2_LOOKUP_IDENTITY_MISMATCH"
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
    ) -> LegalEvidenceProviderCleanupCommand | None:
        """Read command for one exact tenant/provider/object version."""
        tx = _active_transaction(session)

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant_id,
                    "provider_name": provider_name,
                    "storage_reference": storage_reference,
                    "object_version_reference":
                        object_version_reference,
                },
                session=tx,
            )
        except (AttributeError, TypeError, ValueError) as error:
            raise LegalEvidenceProviderCleanupCommandRegistryPersistenceError(
                "L10A2R_C4D6E_A3_P3_P2_COLLECTION_INTERFACE_INVALID"
            ) from error

        if row is None:
            return None

        value = _hydrate(row)

        if (
            value.tenant_id != tenant_id
            or value.provider_name != provider_name
            or value.storage_reference != storage_reference
            or value.object_version_reference
            != object_version_reference
        ):
            raise LegalEvidenceProviderCleanupCommandRegistryIntegrityError(
                "L10A2R_C4D6E_A3_P3_P2_LOOKUP_IDENTITY_MISMATCH"
            )

        return value


__all__ = [
    "COLLECTION",
    "INDEX_TENANT_COMMAND_ID",
    "INDEX_TENANT_FINGERPRINT",
    "INDEX_TENANT_CLEANUP_AUTHORIZATION",
    "INDEX_TENANT_PROVIDER_OBJECT",
    "VERSION",
    "LegalEvidenceProviderCleanupCommandRegistry",
    "LegalEvidenceProviderCleanupCommandRegistryError",
    "LegalEvidenceProviderCleanupCommandRegistryIntegrityError",
    "LegalEvidenceProviderCleanupCommandRegistryPersistenceError",
    "LegalEvidenceProviderCleanupCommandRegistryRetryRequiredError",
    "LegalEvidenceProviderCleanupCommandRegistryTransactionError",
]


# ARTIFACT: legal_evidence_provider_cleanup_command_registry.py
# VERSION: v1.0.1-L10A2R-C4D6E-A3-P3-P2-CLEANUP-COMMAND-REGISTRY
# AUTHORITY BOUNDARY: durable immutable cleanup-command intent evidence only
# TENANT POSTURE: every durable identity and lookup is exact tenant scoped
# TRANSACTION POSTURE: caller owns one already-active transaction
# IDEMPOTENCY POSTURE: exact immutable command evidence may replay; divergence rejects
# RETRY POSTURE: duplicate-key failure requires abort + fresh whole-transaction retry
# TTL POSTURE: no TTL deletion index
# PROVIDER MUTATION POSTURE: none
# DELETION EXECUTION POSTURE: none
# FAIL-CLOSED POSTURE: corrupt/divergent durable evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
