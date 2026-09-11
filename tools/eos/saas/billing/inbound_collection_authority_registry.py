"""WILSY OS M11 R8-R4 durable inbound collection authority registry with authorization provenance.
TITLE: Inbound Collection Authority Registry
VERSION: v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Tenant-scoped durable storage, exact-one cardinality, and fail-closed replay for immutable collection authorities.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/inbound_collection_authority_registry.py
COLLABORATION / OWNERSHIP: SaaS persistence owner for InboundCollectionAuthority; callers own issuance and transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE persists and strictly hydrates the domain's authorization_evidence_fingerprint without deriving or indexing it; v1.0.0-M11-R8-R3 established three tenant-scoped uniqueness indexes, strict hydration, and pre-insert replay precedence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Every lookup is tenant-scoped; only immutable opaque authority data is persisted.
TENANT BOUNDARY: Tenant ID participates in identity, family/receivable cardinality, and idempotency predicates.
AUTHORITY BOUNDARY: Persistence and replay only; this registry does not issue, select, execute, settle, or mutate business records.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns outbound financial execution truth.
TRANSACTION BOUNDARY: Caller supplies the session and owns active transaction, commit, abort, and whole-transaction retry.
FAIL-CLOSED DECLARATION: Corrupt hydration, conflicting durable identities, and divergent replay reject without inference.
"""
from __future__ import annotations

from typing import Any, Optional

from pymongo import ASCENDING
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.commercial_receivable import ReceivableFamily
from tools.eos.saas.domain.inbound_collection_authority import (
    ClientCollectionSource,
    InboundCollectionAuthority,
    InboundCollectionAuthorityError,
    PlatformCollectionSource,
)


VERSION = "v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE"
COLLECTION = "inbound_collection_authorities"


class InboundCollectionAuthorityRegistryError(RuntimeError):
    """Base fail-closed registry error."""


class InboundCollectionAuthorityPersistedRecordInvalidError(InboundCollectionAuthorityRegistryError):
    """Persisted data cannot be reconstructed as canonical authority."""


class InboundCollectionAuthorityReplayConflictError(InboundCollectionAuthorityRegistryError):
    """A durable identity exists but immutable material diverges."""


class InboundCollectionAuthorityPersistenceCorruptionError(InboundCollectionAuthorityRegistryError):
    """Independent canonical lookups disagree about durable authority."""


def _require_lookup_text(name: str, value: object) -> str:
    """Require the exact canonical text used by a tenant-scoped predicate."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise InboundCollectionAuthorityRegistryError(f"M11R8_INVALID_LOOKUP_{name.upper()}")
    return value


def _family(value: object) -> ReceivableFamily:
    """Require the closed commercial family enum; never infer or normalize family."""
    if not isinstance(value, ReceivableFamily):
        raise InboundCollectionAuthorityRegistryError("M11R8_INVALID_SOURCE_AUTHORITY_KIND")
    return value


def _idempotency(value: object) -> str:
    """Apply the authority domain's conservative idempotency trimming convention."""
    if not isinstance(value, str):
        raise InboundCollectionAuthorityRegistryError("M11R8_INVALID_IDEMPOTENCY_KEY")
    canonical = value.strip()
    if not canonical:
        raise InboundCollectionAuthorityRegistryError("M11R8_INVALID_IDEMPOTENCY_KEY")
    return canonical


def _query_rows(
    collection: Collection,
    query: dict[str, object],
    *,
    session: Optional[ClientSession],
) -> list[dict[str, Any]]:
    """Read at most two rows so duplicate durable records fail closed."""
    try:
        cursor = collection.find(query, session=session)
        limited = cursor.limit(2) if hasattr(cursor, "limit") else cursor
        return [dict(row) for row in list(limited)[:2]]
    except PyMongoError as error:
        raise InboundCollectionAuthorityRegistryError("M11R8_LOOKUP_FAILED") from error
    except Exception as error:
        raise InboundCollectionAuthorityRegistryError("M11R8_LOOKUP_FAILED") from error


def _hydrate(document: dict[str, Any]) -> InboundCollectionAuthority:
    """Remove only Mongo transport identity and delegate all semantic checks to the domain.

    The authorization evidence fingerprint is persisted and reconstructed exactly
    through ``InboundCollectionAuthority.from_dict``; this registry never derives,
    defaults, or independently indexes that provenance value.
    """
    body = dict(document)
    body.pop("_id", None)
    try:
        return InboundCollectionAuthority.from_dict(body)
    except (InboundCollectionAuthorityError, KeyError, TypeError, ValueError) as error:
        raise InboundCollectionAuthorityPersistedRecordInvalidError(
            "M11R8_PERSISTED_RECORD_INVALID"
        ) from error


def _one(
    collection: Collection,
    query: dict[str, object],
    *,
    session: Optional[ClientSession],
) -> InboundCollectionAuthority | None:
    """Resolve one exact query or reject multiple durable rows."""
    rows = _query_rows(collection, query, session=session)
    if len(rows) > 1:
        raise InboundCollectionAuthorityPersistenceCorruptionError("M11R8_MULTIPLE_DURABLE_AUTHORITIES")
    return None if not rows else _hydrate(rows[0])


def _source_query(
    tenant_id: str,
    source_authority_kind: ReceivableFamily,
    commercial_receivable_id: str,
) -> dict[str, object]:
    """Build the constitutional tenant/family/receivable cardinality predicate."""
    return {
        "tenant_id": tenant_id,
        "source_authority_kind": source_authority_kind.value,
        "source_authority.commercial_receivable_id": commercial_receivable_id,
    }


def _authority_identity(value: InboundCollectionAuthority) -> tuple[str, str, str, str]:
    """Return the three durable identities plus tenant for conflict comparison."""
    return (
        value.tenant_id,
        value.collection_authority_id,
        value.source_authority_kind.value,
        value.source_authority.commercial_receivable_id,
    )


class InboundCollectionAuthorityRegistry:
    """Persist immutable collection authority without owning issuance or transactions."""

    @staticmethod
    def _require_active_transaction(session: Optional[ClientSession]) -> ClientSession:
        """Require the caller-owned active transaction without creating one."""
        if session is None or getattr(session, "in_transaction", False) is not True:
            raise InboundCollectionAuthorityRegistryError("M11R8_ACTIVE_TRANSACTION_REQUIRED")
        return session

    @staticmethod
    def _hydrate(document: dict[str, Any]) -> InboundCollectionAuthority:
        """Expose the strict internal hydrator for registry-local certificate tests."""
        return _hydrate(document)

    @staticmethod
    def ensure_indexes(collection: Collection) -> None:
        """Create exactly the three tenant-scoped V1 uniqueness constraints."""
        collection.create_index(
            [("tenant_id", ASCENDING), ("collection_authority_id", ASCENDING)],
            unique=True,
            name="tenant_collection_authority_identity_unique",
        )
        collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("source_authority_kind", ASCENDING),
                ("source_authority.commercial_receivable_id", ASCENDING),
            ],
            unique=True,
            name="tenant_family_receivable_collection_authority_unique",
        )
        collection.create_index(
            [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
            unique=True,
            name="tenant_collection_authority_idempotency_unique",
        )

    @staticmethod
    def get(
        tenant_id: str,
        collection_authority_id: str,
        collection: Collection,
        *,
        session: Optional[ClientSession] = None,
    ) -> InboundCollectionAuthority | None:
        """Return the exact tenant-scoped authority ID, or ``None`` when absent."""
        tx = InboundCollectionAuthorityRegistry._require_active_transaction(session)
        tenant = _require_lookup_text("tenant_id", tenant_id)
        authority_id = _require_lookup_text("collection_authority_id", collection_authority_id)
        return _one(
            collection,
            {"tenant_id": tenant, "collection_authority_id": authority_id},
            session=tx,
        )

    @staticmethod
    def get_by_source_receivable(
        tenant_id: str,
        source_authority_kind: ReceivableFamily,
        commercial_receivable_id: str,
        collection: Collection,
        *,
        session: Optional[ClientSession] = None,
    ) -> InboundCollectionAuthority | None:
        """Return the exact tenant/family/receivable authority, or ``None``."""
        tx = InboundCollectionAuthorityRegistry._require_active_transaction(session)
        tenant = _require_lookup_text("tenant_id", tenant_id)
        family = _family(source_authority_kind)
        receivable_id = _require_lookup_text("commercial_receivable_id", commercial_receivable_id)
        return _one(collection, _source_query(tenant, family, receivable_id), session=tx)

    @staticmethod
    def get_by_idempotency_key(
        tenant_id: str,
        idempotency_key: str,
        collection: Collection,
        *,
        session: Optional[ClientSession] = None,
    ) -> InboundCollectionAuthority | None:
        """Return the exact tenant-scoped idempotency authority, or ``None``."""
        tx = InboundCollectionAuthorityRegistry._require_active_transaction(session)
        tenant = _require_lookup_text("tenant_id", tenant_id)
        key = _idempotency(idempotency_key)
        return _one(collection, {"tenant_id": tenant, "idempotency_key": key}, session=tx)

    @staticmethod
    def create(
        value: InboundCollectionAuthority,
        collection: Collection,
        *,
        session: Optional[ClientSession] = None,
    ) -> InboundCollectionAuthority:
        """Persist once, replay only exact canonical material, and propagate races.

        All three canonical identities are read before insert. If a concurrent
        transaction wins the insert, ``DuplicateKeyError`` propagates directly;
        the caller must restart its complete transaction and invoke this method
        again, allowing fresh pre-insert reconciliation to resolve the winner.
        """
        tx = InboundCollectionAuthorityRegistry._require_active_transaction(session)
        if not isinstance(value, InboundCollectionAuthority):
            raise InboundCollectionAuthorityReplayConflictError("M11R8_INVALID_AUTHORITY")

        tenant = value.tenant_id
        source = value.source_authority
        identity_row = _one(
            collection,
            {"tenant_id": tenant, "collection_authority_id": value.collection_authority_id},
            session=tx,
        )
        source_row = _one(
            collection,
            _source_query(tenant, value.source_authority_kind, source.commercial_receivable_id),
            session=tx,
        )
        idempotency_row = _one(
            collection,
            {"tenant_id": tenant, "idempotency_key": value.idempotency_key},
            session=tx,
        )

        existing = [row for row in (identity_row, source_row, idempotency_row) if row is not None]
        if existing:
            identities = {_authority_identity(row) for row in existing}
            if len(identities) != 1:
                raise InboundCollectionAuthorityPersistenceCorruptionError(
                    "M11R8_DISAGREEING_CANONICAL_EXISTING_FACTS"
                )
            durable = existing[0]
            if durable == value:
                return durable
            raise InboundCollectionAuthorityReplayConflictError("M11R8_DIVERGENT_REPLAY")

        try:
            collection.insert_one(value.to_dict(), session=tx)
        except DuplicateKeyError:
            raise
        except PyMongoError as error:
            raise InboundCollectionAuthorityRegistryError("M11R8_INSERT_FAILED") from error
        return value


__all__ = [
    "COLLECTION",
    "InboundCollectionAuthorityPersistedRecordInvalidError",
    "InboundCollectionAuthorityPersistenceCorruptionError",
    "InboundCollectionAuthorityRegistry",
    "InboundCollectionAuthorityRegistryError",
    "InboundCollectionAuthorityReplayConflictError",
    "VERSION",
]


# ARTIFACT: inbound_collection_authority_registry.py
# VERSION: v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE
# AUTHORITY BOUNDARY: Durable immutable authority persistence and replay only.
# TENANT POSTURE: Every identity and source predicate carries tenant_id.
# FAIL-CLOSED POSTURE: Strict reconstruction, authorization-provenance validation, conflict detection, and race propagation.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
