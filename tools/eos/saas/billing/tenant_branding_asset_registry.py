"""WILSY OS durable immutable tenant branding asset byte registry.

TITLE: Tenant Branding Asset Registry
VERSION: v1.0.0-D21B5B-TENANT-BRANDING-ASSET-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist bounded D21B5A branding bytes immutably and resolve them only
         through exact tenant/reference/content-fingerprint/kind correlation
         inside caller-owned Mongo transactions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_branding_asset_registry.py
COLLABORATION / OWNERSHIP: D21B5A owns canonical asset metadata/content identity;
                            this registry owns immutable durable bytes and exact
                            resolution. D21B3 owns approved profile references;
                            later runtime composition must correlate them. Callers
                            own Mongo sessions/transactions.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B5B-TENANT-BRANDING-ASSET-REGISTRY establishes immutable
           tenant/reference persistence, exact replay, content SHA3-512 recheck
           on every hydration, profile-supplied expected fingerprint/kind
           correlation, deterministic indexes and whole-transaction retry
           signaling without URL or browser authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Stores only D21B5A metadata plus bounded safe image
                             bytes. No public URL, filesystem path, cloud key,
                             credential, HTML/CSS/JS or browser state.
TENANT BOUNDARY: Every read/write/resolve predicate binds exact tenant_id and
                 asset_reference. Foreign evidence is indistinguishable from
                 absence.
AUTHORITY BOUNDARY: Durable branding bytes and exact resolution only. This does
                    not approve a D21B3 profile, select current branding, prove
                    entitlement freshness, grant IAM or authorize presentation.
FINANCIAL AUTHORITY BOUNDARY: No commercial, payment, execution or settlement
                               truth. Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Every operational read/write requires an already-active
                      caller-owned transaction. Registry owns no lifecycle.
FAIL-CLOSED DECLARATION: Missing transactions, schema/content corruption,
                         tenant/reference/fingerprint/kind divergence, duplicate
                         identities, races and persistence outages reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.tenant_branding_asset import (
    ASSET_FIELDS,
    TenantBrandingAsset,
    TenantBrandingAssetError,
    TenantBrandingAssetKind,
    content_fingerprint,
)


VERSION: Final[str] = "v1.0.0-D21B5B-TENANT-BRANDING-ASSET-REGISTRY"
RECORD_SCHEMA: Final[str] = "WILSY-TENANT-BRANDING-ASSET-RECORD/V1"
COLLECTION: Final[str] = "tenant_branding_assets"
IDENTITY_INDEX_NAME: Final[str] = "tenant_branding_asset_tenant_reference_unique"
CONTENT_INDEX_NAME: Final[str] = "tenant_branding_asset_tenant_content"
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")

_RECORD_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "entity_type",
        "tenant_id",
        "asset_reference",
        "asset_fingerprint",
        "content_fingerprint",
        "asset_payload",
        "content_bytes",
    }
)


class TenantBrandingAssetRegistryError(RuntimeError):
    """Base fail-closed D21B5B durable registry error with stable code."""

    default_code = "D21B5B_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        """Create one governed registry failure."""
        self.code = code or self.default_code
        super().__init__(self.code)


class TenantBrandingAssetRegistryInputError(TenantBrandingAssetRegistryError):
    """Caller input or collection dependency is invalid."""

    default_code = "D21B5B_INPUT_INVALID"


class TenantBrandingAssetRegistryTransactionRequiredError(
    TenantBrandingAssetRegistryError
):
    """An already-active caller-owned Mongo transaction is required."""

    default_code = "D21B5B_ACTIVE_TRANSACTION_REQUIRED"


class TenantBrandingAssetRegistryNotFoundError(TenantBrandingAssetRegistryError):
    """Exact tenant/reference asset evidence is absent."""

    default_code = "D21B5B_ASSET_NOT_FOUND"


class TenantBrandingAssetRegistryConflictError(TenantBrandingAssetRegistryError):
    """One tenant/reference is already bound to divergent immutable evidence."""

    default_code = "D21B5B_ASSET_CONFLICT"


class TenantBrandingAssetRegistryPersistedRecordInvalidError(
    TenantBrandingAssetRegistryError
):
    """Persisted metadata or bytes failed strict integrity hydration."""

    default_code = "D21B5B_PERSISTED_RECORD_INVALID"


class TenantBrandingAssetRegistryRetryRequiredError(
    TenantBrandingAssetRegistryError
):
    """Caller must abort and restart the whole transaction from fresh state."""

    default_code = "D21B5B_WHOLE_TRANSACTION_RETRY_REQUIRED"


class TenantBrandingAssetRegistryPersistenceUnavailableError(
    TenantBrandingAssetRegistryError
):
    """Mongo persistence is unavailable without a governed retry label."""

    default_code = "D21B5B_PERSISTENCE_UNAVAILABLE"


def _raise(
    error_type: type[TenantBrandingAssetRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable registry error while preserving technical cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo_operational_error(error: PyMongoError) -> NoReturn:
    """Translate only explicit transient-transaction evidence to caller retry."""
    if error.has_error_label("TransientTransactionError"):
        _raise(TenantBrandingAssetRegistryRetryRequiredError, cause=error)
    _raise(TenantBrandingAssetRegistryPersistenceUnavailableError, cause=error)


def _target(collection: Any) -> Any:
    """Apply majority/journal durability when collection options are available."""
    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
        )
    except AttributeError:
        return collection


def _collection(value: Any) -> Any:
    """Require one collection-like dependency without creating a Mongo client."""
    if value is None:
        _raise(
            TenantBrandingAssetRegistryInputError,
            "D21B5B_COLLECTION_REQUIRED",
        )
    return _target(value)


def _active_transaction(session: Any) -> Any:
    """Require an active caller-owned transaction; registry owns no lifecycle."""
    if session is None:
        _raise(TenantBrandingAssetRegistryTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(TenantBrandingAssetRegistryTransactionRequiredError)
    return session


def _text(name: str, value: object) -> str:
    """Require one exact non-empty stripped string at registry boundaries."""
    if not isinstance(value, str) or not value or value != value.strip():
        _raise(
            TenantBrandingAssetRegistryInputError,
            f"D21B5B_{name.upper()}_INVALID",
        )
    return value


def _record(
    asset: TenantBrandingAsset,
    content: bytes,
) -> dict[str, object]:
    """Build the exact immutable persisted asset envelope."""
    if not isinstance(content, bytes):
        _raise(
            TenantBrandingAssetRegistryInputError,
            "D21B5B_CONTENT_BYTES_REQUIRED",
        )
    try:
        digest = content_fingerprint(content)
    except TenantBrandingAssetError as error:
        _raise(
            TenantBrandingAssetRegistryInputError,
            "D21B5B_CONTENT_INVALID",
            error,
        )
    if (
        len(content) != asset.content_length
        or digest != asset.content_fingerprint
    ):
        _raise(
            TenantBrandingAssetRegistryInputError,
            "D21B5B_CONTENT_EVIDENCE_MISMATCH",
        )
    return {
        "schema": RECORD_SCHEMA,
        "version": VERSION,
        "entity_type": "TenantBrandingAssetRecord",
        "tenant_id": asset.tenant_id,
        "asset_reference": asset.asset_reference,
        "asset_fingerprint": asset.fingerprint,
        "content_fingerprint": asset.content_fingerprint,
        "asset_payload": asset.to_dict(),
        "content_bytes": content,
    }


@dataclass(frozen=True, slots=True)
class TenantBrandingResolvedAsset:
    """Strictly hydrated immutable D21B5A evidence plus exact durable bytes."""

    asset: TenantBrandingAsset
    content: bytes

    def __post_init__(self) -> None:
        """Require exact byte identity and declared content length."""
        if type(self.asset) is not TenantBrandingAsset:
            _raise(
                TenantBrandingAssetRegistryInputError,
                "D21B5B_ASSET_REQUIRED",
            )
        if not isinstance(self.content, bytes):
            _raise(
                TenantBrandingAssetRegistryInputError,
                "D21B5B_CONTENT_BYTES_REQUIRED",
            )
        try:
            digest = content_fingerprint(self.content)
        except TenantBrandingAssetError as error:
            _raise(
                TenantBrandingAssetRegistryPersistedRecordInvalidError,
                "D21B5B_CONTENT_INVALID",
                error,
            )
        if (
            len(self.content) != self.asset.content_length
            or digest != self.asset.content_fingerprint
        ):
            _raise(
                TenantBrandingAssetRegistryPersistedRecordInvalidError,
                "D21B5B_CONTENT_EVIDENCE_MISMATCH",
            )


def _hydrate(document: Mapping[str, Any]) -> TenantBrandingResolvedAsset:
    """Strictly hydrate persisted metadata and re-hash durable bytes."""
    if not isinstance(document, Mapping):
        _raise(TenantBrandingAssetRegistryPersistedRecordInvalidError)
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _RECORD_FIELDS:
        _raise(
            TenantBrandingAssetRegistryPersistedRecordInvalidError,
            "D21B5B_RECORD_SCHEMA_INVALID",
        )
    if (
        raw.get("schema") != RECORD_SCHEMA
        or raw.get("version") != VERSION
        or raw.get("entity_type") != "TenantBrandingAssetRecord"
    ):
        _raise(
            TenantBrandingAssetRegistryPersistedRecordInvalidError,
            "D21B5B_RECORD_VERSION_UNSUPPORTED",
        )
    payload = raw.get("asset_payload")
    if not isinstance(payload, Mapping) or set(payload) != set(ASSET_FIELDS):
        _raise(
            TenantBrandingAssetRegistryPersistedRecordInvalidError,
            "D21B5B_ASSET_PAYLOAD_SCHEMA_INVALID",
        )
    try:
        asset = TenantBrandingAsset.from_dict(
            cast(Mapping[str, object], payload)
        )
    except (TypeError, ValueError, TenantBrandingAssetError) as error:
        _raise(
            TenantBrandingAssetRegistryPersistedRecordInvalidError,
            "D21B5B_ASSET_PAYLOAD_INVALID",
            error,
        )
    stored = raw.get("content_bytes")
    if not isinstance(stored, (bytes, bytearray)):
        _raise(
            TenantBrandingAssetRegistryPersistedRecordInvalidError,
            "D21B5B_CONTENT_BYTES_INVALID",
        )
    content = bytes(stored)
    resolved = TenantBrandingResolvedAsset(asset=asset, content=content)
    if (
        raw.get("tenant_id") != asset.tenant_id
        or raw.get("asset_reference") != asset.asset_reference
        or raw.get("asset_fingerprint") != asset.fingerprint
        or raw.get("content_fingerprint") != asset.content_fingerprint
    ):
        _raise(
            TenantBrandingAssetRegistryPersistedRecordInvalidError,
            "D21B5B_RECORD_CORRELATION_INVALID",
        )
    return resolved


def ensure_indexes(collection: Any) -> None:
    """Create immutable tenant/reference uniqueness plus content lookup index."""
    target = _collection(collection)
    try:
        target.create_index(
            [("tenant_id", ASCENDING), ("asset_reference", ASCENDING)],
            unique=True,
            name=IDENTITY_INDEX_NAME,
        )
        target.create_index(
            [("tenant_id", ASCENDING), ("content_fingerprint", ASCENDING)],
            unique=False,
            name=CONTENT_INDEX_NAME,
        )
    except (AttributeError, PyMongoError) as error:
        _raise(
            TenantBrandingAssetRegistryPersistenceUnavailableError,
            cause=error,
        )


def _read(
    tenant_id: str,
    asset_reference: str,
    collection: Any,
    *,
    session: Any,
) -> TenantBrandingResolvedAsset:
    """Read one exact tenant/reference record; foreign scope is absence."""
    tenant = _text("tenant_id", tenant_id)
    reference = _text("asset_reference", asset_reference)
    target = _collection(collection)
    try:
        rows = list(
            target.find(
                {"tenant_id": tenant, "asset_reference": reference},
                session=session,
            ).limit(2)
        )
    except PyMongoError as error:
        _raise_mongo_operational_error(error)
    except (AttributeError, TypeError) as error:
        _raise(
            TenantBrandingAssetRegistryInputError,
            "D21B5B_COLLECTION_INTERFACE_INVALID",
            error,
        )
    if not rows:
        _raise(TenantBrandingAssetRegistryNotFoundError)
    if len(rows) != 1:
        _raise(
            TenantBrandingAssetRegistryPersistedRecordInvalidError,
            "D21B5B_DUPLICATE_ASSET_REFERENCE",
        )
    resolved = _hydrate(cast(Mapping[str, Any], rows[0]))
    if (
        resolved.asset.tenant_id != tenant
        or resolved.asset.asset_reference != reference
    ):
        _raise(
            TenantBrandingAssetRegistryPersistedRecordInvalidError,
            "D21B5B_SCOPE_MISMATCH",
        )
    return resolved


def create_or_replay(
    asset: TenantBrandingAsset,
    content: bytes,
    collection: Any,
    *,
    session: Any,
) -> TenantBrandingResolvedAsset:
    """Persist one immutable asset or return an exact tenant/reference replay."""
    tx = _active_transaction(session)
    if type(asset) is not TenantBrandingAsset:
        _raise(TenantBrandingAssetRegistryInputError, "D21B5B_ASSET_REQUIRED")
    target = _collection(collection)
    record = _record(asset, content)
    try:
        existing = target.find_one(
            {
                "tenant_id": asset.tenant_id,
                "asset_reference": asset.asset_reference,
            },
            session=tx,
        )
    except PyMongoError as error:
        _raise_mongo_operational_error(error)
    except (AttributeError, TypeError) as error:
        _raise(
            TenantBrandingAssetRegistryInputError,
            "D21B5B_COLLECTION_INTERFACE_INVALID",
            error,
        )
    if existing is not None:
        resolved = _hydrate(cast(Mapping[str, Any], existing))
        if (
            resolved.asset.to_dict() == asset.to_dict()
            and resolved.content == content
        ):
            return resolved
        _raise(TenantBrandingAssetRegistryConflictError)

    try:
        target.insert_one(record, session=tx)
    except DuplicateKeyError as error:
        _raise(TenantBrandingAssetRegistryRetryRequiredError, cause=error)
    except PyMongoError as error:
        _raise_mongo_operational_error(error)

    persisted = _read(
        asset.tenant_id,
        asset.asset_reference,
        target,
        session=tx,
    )
    if (
        persisted.asset.to_dict() != asset.to_dict()
        or persisted.content != content
    ):
        _raise(
            TenantBrandingAssetRegistryPersistedRecordInvalidError,
            "D21B5B_CREATE_CORRELATION_INVALID",
        )
    return persisted


def resolve(
    tenant_id: str,
    asset_reference: str,
    *,
    expected_content_fingerprint: str,
    expected_kind: TenantBrandingAssetKind | str,
    collection: Any,
    session: Any,
) -> TenantBrandingResolvedAsset:
    """Resolve exact durable bytes only when caller evidence matches D21B5A.

    This method creates no URL and performs no browser authorization. Runtime
    branding callers must separately prove current profile and ACTIVE entitlement
    authority before invoking it.
    """
    tx = _active_transaction(session)
    resolved = _read(
        tenant_id,
        asset_reference,
        collection,
        session=tx,
    )
    try:
        kind = TenantBrandingAssetKind(expected_kind)
    except (TypeError, ValueError) as error:
        _raise(
            TenantBrandingAssetRegistryInputError,
            "D21B5B_ASSET_KIND_INVALID",
            error,
        )
    fingerprint = _text(
        "expected_content_fingerprint",
        expected_content_fingerprint,
    )
    if (
        resolved.asset.asset_kind is not kind
        or resolved.asset.content_fingerprint != fingerprint
    ):
        _raise(
            TenantBrandingAssetRegistryConflictError,
            "D21B5B_EXPECTED_ASSET_MISMATCH",
        )
    return resolved


class TenantBrandingAssetRegistry:
    """Static immutable byte registry; owns no client or transaction lifecycle."""

    ensure_indexes = staticmethod(ensure_indexes)
    create_or_replay = staticmethod(create_or_replay)
    resolve = staticmethod(resolve)


__all__ = [
    "COLLECTION",
    "CONTENT_INDEX_NAME",
    "IDENTITY_INDEX_NAME",
    "READ_CONCERN",
    "RECORD_SCHEMA",
    "TenantBrandingAssetRegistry",
    "TenantBrandingAssetRegistryConflictError",
    "TenantBrandingAssetRegistryError",
    "TenantBrandingAssetRegistryInputError",
    "TenantBrandingAssetRegistryNotFoundError",
    "TenantBrandingAssetRegistryPersistedRecordInvalidError",
    "TenantBrandingAssetRegistryPersistenceUnavailableError",
    "TenantBrandingAssetRegistryRetryRequiredError",
    "TenantBrandingAssetRegistryTransactionRequiredError",
    "TenantBrandingResolvedAsset",
    "VERSION",
    "WRITE_CONCERN",
    "create_or_replay",
    "ensure_indexes",
    "resolve",
]

# ARTIFACT: tenant_branding_asset_registry.py
# VERSION: v1.0.0-D21B5B-TENANT-BRANDING-ASSET-REGISTRY
# AUTHORITY BOUNDARY: immutable bounded branding-byte persistence and exact resolution only; no profile/currentness/entitlement/browser/IAM/financial authority
# TENANT POSTURE: every persisted/read/resolved asset is exact tenant/reference scoped
# FAIL-CLOSED POSTURE: active caller transaction, exact metadata/content hash/kind/fingerprint correlation; corruption/races/outages reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
