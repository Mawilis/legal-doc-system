"""WILSY OS durable credential-material metadata registry.

TITLE: Tenant Inbound Provider Credential Material Metadata Registry
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R5
AUTHORITY: Wilsy OS Core Governance
EPITOME: Caller-transaction persistence for immutable provider-neutral metadata
         generations and an explicit current pointer; no security authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_inbound_provider_credential_material_metadata_registry.py
COLLABORATION / OWNERSHIP: P5 metadata registry owner; P2/P3 security facts,
                            adapters, evidence, binding, checkout, and issuance
                            remain separate owners.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P5-R5 establishes the two-collection,
           caller-transaction, generation-identity and explicit-pointer contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references and fingerprints only; no raw or
                             decrypted secret, KMS, provider, network, or auth.
TENANT BOUNDARY: Every fact, idempotency lookup, pointer, replay, and CAS
                 predicate carries tenant_id.
AUTHORITY BOUNDARY: Durable metadata/currentness only; upstream provenance is
                    prevalidated and is never authenticated here.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Caller supplies the active session and owns commit,
                       abort, rollback, and whole-transaction retry.
FAIL-CLOSED DECLARATION: Schema drift, divergent identity, stale CAS, duplicate
                          generations, and broken pointer correlation reject.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, ClassVar, Mapping, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.tenant_inbound_provider_credential_material_metadata import (
    TenantInboundProviderCredentialMaterialMetadata,
    TenantInboundProviderCredentialMaterialMetadataError,
)


VERSION = "v1.0.0-M11-R8-R3B-P8-P3D-P5-R5"
CAMPAIGN_IDENTITY = "M11-R8-R3B-P8-P3D-P5-R5"
FACT_ID_SCHEMA = "WILSY-TENANT-INBOUND-PROVIDER-CREDENTIAL-MATERIAL-METADATA-FACT-ID/V1"
HASH_ALGORITHM = "SHA3-512"
FACT_COLLECTION = "tenant_inbound_provider_credential_material_metadata_facts"
CURRENT_POINTER_COLLECTION = "tenant_inbound_provider_credential_material_metadata_current"
EVENT_COLLECTION = FACT_COLLECTION
POINTER_COLLECTION = CURRENT_POINTER_COLLECTION
SLOT_COLLECTION = CURRENT_POINTER_COLLECTION
METADATA_FACT_ID_FIELD = "metadata_fact_id"
IDEMPOTENCY_KEY_FIELD = "credential_material_metadata_idempotency_key"
CREDENTIAL_MATERIAL_METADATA_IDEMPOTENCY_KEY_FIELD = IDEMPOTENCY_KEY_FIELD
IDEMPOTENCY_KEY_MAX_LENGTH = 256
CURRENT_STREAM_IDENTITY = (
    "tenant_id;provider_id;merchant_configuration_id;merchant_configuration_version"
)
FACT_IDENTITY_INDEX_NAME = "tenant_credential_material_metadata_fact_identity_unique"
METADATA_FACT_IDENTITY_INDEX_NAME = FACT_IDENTITY_INDEX_NAME
IDEMPOTENCY_INDEX_NAME = "tenant_provider_configuration_credential_material_metadata_idempotency_unique"
CREDENTIAL_VERSION_INDEX_NAME = "tenant_provider_configuration_credential_version_unique"
TENANT_CREDENTIAL_VERSION_INDEX_NAME = CREDENTIAL_VERSION_INDEX_NAME
CURRENT_POINTER_INDEX_NAME = "tenant_provider_configuration_credential_material_metadata_current_unique"
AUTHORITY_UNIQUE_INDEX_COUNT = 4


class TenantInboundProviderCredentialMaterialMetadataRegistryError(RuntimeError):
    """Base fail-closed registry error."""


class TenantInboundProviderCredentialMaterialMetadataRegistryTransactionRequiredError(
    TenantInboundProviderCredentialMaterialMetadataRegistryError
):
    """A caller-owned active transaction was not supplied."""


TenantInboundProviderCredentialMaterialMetadataRegistryTransactionError = TenantInboundProviderCredentialMaterialMetadataRegistryTransactionRequiredError


class TenantInboundProviderCredentialMaterialMetadataRegistryNotFoundError(
    TenantInboundProviderCredentialMaterialMetadataRegistryError
):
    """A requested tenant-scoped durable fact was absent."""


class TenantInboundProviderCredentialMaterialMetadataRegistryPersistedRecordInvalidError(
    TenantInboundProviderCredentialMaterialMetadataRegistryError
):
    """A durable fact or pointer failed strict hydration/correlation."""


TenantInboundProviderCredentialMaterialMetadataRegistryRecordInvalidError = TenantInboundProviderCredentialMaterialMetadataRegistryPersistedRecordInvalidError


class TenantInboundProviderCredentialMaterialMetadataRegistryReplayConflictError(
    TenantInboundProviderCredentialMaterialMetadataRegistryError
):
    """A replay identity carried divergent immutable structure."""


class TenantInboundProviderCredentialMaterialMetadataRegistryIdempotencyConflictError(
    TenantInboundProviderCredentialMaterialMetadataRegistryReplayConflictError
):
    """A scoped idempotency key was reused for a different request."""


class TenantInboundProviderCredentialMaterialMetadataRegistryCurrentPointerConflictError(
    TenantInboundProviderCredentialMaterialMetadataRegistryError
):
    """The explicit current pointer was absent, duplicated, or inconsistent."""


class TenantInboundProviderCredentialMaterialMetadataRegistryCASConflictError(
    TenantInboundProviderCredentialMaterialMetadataRegistryCurrentPointerConflictError
):
    """Expected prior pointer antecedents no longer match."""


class TenantInboundProviderCredentialMaterialMetadataRegistryDuplicateFactIdentityError(
    TenantInboundProviderCredentialMaterialMetadataRegistryError
):
    """A credential generation identity is already durably bound."""


class TenantInboundProviderCredentialMaterialMetadataRegistryGenerationConflictError(
    TenantInboundProviderCredentialMaterialMetadataRegistryDuplicateFactIdentityError
):
    """A credential-version generation conflicts with existing provenance."""


class TenantInboundProviderCredentialMaterialMetadataRegistryPersistenceCorruptionError(
    TenantInboundProviderCredentialMaterialMetadataRegistryPersistedRecordInvalidError
):
    """Multiple or mutually contradictory durable rows were observed."""


# Short aliases are intentionally additive and do not create another authority.
TransactionRequiredError = TenantInboundProviderCredentialMaterialMetadataRegistryTransactionRequiredError
NotFoundError = TenantInboundProviderCredentialMaterialMetadataRegistryNotFoundError
PersistedRecordInvalidError = TenantInboundProviderCredentialMaterialMetadataRegistryPersistedRecordInvalidError
ReplayConflictError = TenantInboundProviderCredentialMaterialMetadataRegistryReplayConflictError
IdempotencyConflictError = TenantInboundProviderCredentialMaterialMetadataRegistryIdempotencyConflictError
CurrentPointerConflictError = TenantInboundProviderCredentialMaterialMetadataRegistryCurrentPointerConflictError
CASConflictError = TenantInboundProviderCredentialMaterialMetadataRegistryCASConflictError
DuplicateFactIdentityError = TenantInboundProviderCredentialMaterialMetadataRegistryDuplicateFactIdentityError
GenerationConflictError = TenantInboundProviderCredentialMaterialMetadataRegistryGenerationConflictError


def _active_transaction(session: Any) -> Any:
    """Require an active caller transaction without creating or ending it."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise TransactionRequiredError("M11P5R5_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _collection(value: Any, label: str) -> Any:
    """Require an explicit collection supplied by the caller."""
    if value is None:
        raise TenantInboundProviderCredentialMaterialMetadataRegistryError(
            f"M11P5R5_{label}_COLLECTION_REQUIRED"
        )
    return value


def _session_kwargs(session: Any) -> dict[str, object]:
    """Propagate the caller session to every read and write."""
    return {"session": session}


def _text(name: str, value: object, *, maximum: int | None = None) -> str:
    """Require an exact non-blank text token."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantInboundProviderCredentialMaterialMetadataRegistryError(
            f"M11P5R5_INVALID_{name.upper()}"
        )
    if maximum is not None and len(value) > maximum:
        raise TenantInboundProviderCredentialMaterialMetadataRegistryError(
            f"M11P5R5_INVALID_{name.upper()}"
        )
    return value


def _configuration_version(value: object) -> int:
    """Validate the positive merchant configuration version."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise TenantInboundProviderCredentialMaterialMetadataRegistryError(
            "M11P5R5_INVALID_MERCHANT_CONFIGURATION_VERSION"
        )
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require a lowercase SHA3-512 hexadecimal digest."""
    if not isinstance(value, str) or len(value) != 128 or any(c not in "0123456789abcdef" for c in value):
        raise TenantInboundProviderCredentialMaterialMetadataRegistryError(
            f"M11P5R5_INVALID_{name.upper()}"
        )
    return value


def _public(document: Mapping[str, object]) -> dict[str, object]:
    """Remove Mongo transport identity only."""
    return {key: value for key, value in document.items() if key != "_id"}


def _generation_payload(value: TenantInboundProviderCredentialMaterialMetadata) -> dict[str, object]:
    """Map the R4D generation_identity tuple to its canonical named fields."""
    return dict(zip(value._GENERATION_SEMANTIC_FIELDS, value.generation_identity(), strict=True))


def metadata_fact_id(value: TenantInboundProviderCredentialMaterialMetadata) -> str:
    """Return deterministic SHA3-512 identity for one generation semantic payload."""
    if not isinstance(value, TenantInboundProviderCredentialMaterialMetadata):
        raise TenantInboundProviderCredentialMaterialMetadataRegistryError("M11P5R5_METADATA_REQUIRED")
    canonical = json.dumps(
        {"schema": FACT_ID_SCHEMA, "generation": _generation_payload(value)},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(canonical).hexdigest()


@dataclass(frozen=True, slots=True)
class TenantInboundProviderCredentialMaterialMetadataCurrent:
    """Strict explicit current pointer for one tenant/configuration stream."""

    tenant_id: str
    provider_id: str
    merchant_configuration_id: str
    merchant_configuration_version: int
    merchant_configuration_fingerprint: str
    metadata_fact_id: str
    credential_reference: str
    credential_version: str
    metadata_fingerprint: str

    _FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "tenant_id", "provider_id", "merchant_configuration_id",
            "merchant_configuration_version", "merchant_configuration_fingerprint",
            "metadata_fact_id", "credential_reference", "credential_version",
            "metadata_fingerprint",
        }
    )

    def __post_init__(self) -> None:
        for name in ("tenant_id", "provider_id", "merchant_configuration_id", "metadata_fact_id", "credential_reference", "credential_version"):
            _text(name, getattr(self, name))
        _configuration_version(self.merchant_configuration_version)
        _fingerprint("merchant_configuration_fingerprint", self.merchant_configuration_fingerprint)
        _fingerprint("metadata_fingerprint", self.metadata_fingerprint)

    def to_dict(self) -> dict[str, object]:
        """Serialize exactly the nine pointer fields."""
        return {
            "tenant_id": self.tenant_id,
            "provider_id": self.provider_id,
            "merchant_configuration_id": self.merchant_configuration_id,
            "merchant_configuration_version": self.merchant_configuration_version,
            "merchant_configuration_fingerprint": self.merchant_configuration_fingerprint,
            "metadata_fact_id": self.metadata_fact_id,
            "credential_reference": self.credential_reference,
            "credential_version": self.credential_version,
            "metadata_fingerprint": self.metadata_fingerprint,
        }


CurrentPointer = TenantInboundProviderCredentialMaterialMetadataCurrent


def _hydrate_pointer(document: Mapping[str, object]) -> TenantInboundProviderCredentialMaterialMetadataCurrent:
    """Strictly hydrate a pointer, rejecting unknown and missing fields."""
    raw = _public(document)
    if set(raw) != set(CurrentPointer._FIELDS):
        raise PersistedRecordInvalidError("M11P5R5_INVALID_CURRENT_POINTER_SCHEMA")
    try:
        return CurrentPointer(
            tenant_id=cast(str, raw["tenant_id"]),
            provider_id=cast(str, raw["provider_id"]),
            merchant_configuration_id=cast(str, raw["merchant_configuration_id"]),
            merchant_configuration_version=cast(int, raw["merchant_configuration_version"]),
            merchant_configuration_fingerprint=cast(str, raw["merchant_configuration_fingerprint"]),
            metadata_fact_id=cast(str, raw["metadata_fact_id"]),
            credential_reference=cast(str, raw["credential_reference"]),
            credential_version=cast(str, raw["credential_version"]),
            metadata_fingerprint=cast(str, raw["metadata_fingerprint"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        if isinstance(error, TenantInboundProviderCredentialMaterialMetadataRegistryError):
            raise
        raise PersistedRecordInvalidError("M11P5R5_CORRUPT_CURRENT_POINTER") from error


def _fact_document(value: TenantInboundProviderCredentialMaterialMetadata, fact_id: str, key: str) -> dict[str, object]:
    """Serialize exactly thirteen domain plus two registry-owned fields."""
    payload = value.to_dict()
    payload[METADATA_FACT_ID_FIELD] = fact_id
    payload[IDEMPOTENCY_KEY_FIELD] = key
    return payload


def _fact_payload(document: Mapping[str, object]) -> dict[str, object]:
    """Remove only the two registry fields before domain hydration."""
    payload = _public(document)
    payload.pop(METADATA_FACT_ID_FIELD, None)
    payload.pop(IDEMPOTENCY_KEY_FIELD, None)
    return payload


def _hydrate_fact(document: Mapping[str, object]) -> TenantInboundProviderCredentialMaterialMetadata:
    """Strictly hydrate and verify a durable fact identity and fingerprint."""
    raw = _public(document)
    expected = set(TenantInboundProviderCredentialMaterialMetadata._FIELDS) | {
        METADATA_FACT_ID_FIELD, IDEMPOTENCY_KEY_FIELD,
    }
    if set(raw) != expected:
        raise PersistedRecordInvalidError("M11P5R5_INVALID_FACT_SCHEMA")
    try:
        fact_id = _text(METADATA_FACT_ID_FIELD, raw[METADATA_FACT_ID_FIELD])
        _text(IDEMPOTENCY_KEY_FIELD, raw[IDEMPOTENCY_KEY_FIELD], maximum=IDEMPOTENCY_KEY_MAX_LENGTH)
        fact = TenantInboundProviderCredentialMaterialMetadata.from_dict(_fact_payload(raw))
    except (TenantInboundProviderCredentialMaterialMetadataError, TypeError, ValueError) as error:
        raise PersistedRecordInvalidError("M11P5R5_CORRUPT_METADATA_FACT") from error
    if fact_id != metadata_fact_id(fact):
        raise PersistedRecordInvalidError("M11P5R5_FACT_IDENTITY_MISMATCH")
    if not fact.verify_fingerprint():
        raise PersistedRecordInvalidError("M11P5R5_METADATA_FINGERPRINT_MISMATCH")
    return fact


def _stream_query(tenant_id: str, provider_id: str, configuration_id: str, configuration_version: int) -> dict[str, object]:
    """Build the exact four-field current stream identity."""
    return {
        "tenant_id": _text("tenant_id", tenant_id),
        "provider_id": _text("provider_id", provider_id),
        "merchant_configuration_id": _text("merchant_configuration_id", configuration_id),
        "merchant_configuration_version": _configuration_version(configuration_version),
    }


def _stream_query_for(value: TenantInboundProviderCredentialMaterialMetadata) -> dict[str, object]:
    """Build stream identity from a metadata value, excluding configuration fingerprint."""
    return _stream_query(value.tenant_id, value.provider_id, value.merchant_configuration_id, value.merchant_configuration_version)


def _idempotency_query(value: TenantInboundProviderCredentialMaterialMetadata, key: str) -> dict[str, object]:
    """Build tenant/provider/configuration/version/key idempotency scope."""
    query = _stream_query_for(value)
    query[IDEMPOTENCY_KEY_FIELD] = key
    return query


def _fact_query(tenant_id: str, fact_id: str) -> dict[str, object]:
    """Build tenant-scoped immutable fact identity predicate."""
    return {"tenant_id": _text("tenant_id", tenant_id), METADATA_FACT_ID_FIELD: _text(METADATA_FACT_ID_FIELD, fact_id)}


def _rows(collection: Any, query: Mapping[str, object], session: Any) -> list[Mapping[str, object]]:
    """Read all bounded matches so duplicate rows fail closed."""
    target = _collection(collection, "COLLECTION")
    if hasattr(target, "find"):
        cursor = target.find(dict(query), **_session_kwargs(session))
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(2)
        return [cast(Mapping[str, object], row) for row in cursor]
    row = target.find_one(dict(query), **_session_kwargs(session))
    return [] if row is None else [cast(Mapping[str, object], row)]


def ensure_indexes(fact_collection: Any, pointer_collection: Any) -> None:
    """Declare the four exact uniqueness primitives; no implicit DB access."""
    facts = _collection(fact_collection, "FACT")
    pointers = _collection(pointer_collection, "POINTER")
    facts.create_index(
        [("tenant_id", ASCENDING), (METADATA_FACT_ID_FIELD, ASCENDING)],
        unique=True, name=FACT_IDENTITY_INDEX_NAME,
    )
    facts.create_index(
        [("tenant_id", ASCENDING), ("provider_id", ASCENDING), ("merchant_configuration_id", ASCENDING),
         ("merchant_configuration_version", ASCENDING), (IDEMPOTENCY_KEY_FIELD, ASCENDING)],
        unique=True, name=IDEMPOTENCY_INDEX_NAME,
    )
    facts.create_index(
        [("tenant_id", ASCENDING), ("provider_id", ASCENDING), ("merchant_configuration_id", ASCENDING),
         ("merchant_configuration_version", ASCENDING), ("credential_version", ASCENDING)],
        unique=True, name=CREDENTIAL_VERSION_INDEX_NAME,
    )
    pointers.create_index(
        [("tenant_id", ASCENDING), ("provider_id", ASCENDING), ("merchant_configuration_id", ASCENDING),
         ("merchant_configuration_version", ASCENDING)],
        unique=True, name=CURRENT_POINTER_INDEX_NAME,
    )


def _pointer_for(value: TenantInboundProviderCredentialMaterialMetadata, fact_id: str) -> CurrentPointer:
    """Project a fact into the explicit current pointer."""
    return CurrentPointer(
        tenant_id=value.tenant_id,
        provider_id=value.provider_id,
        merchant_configuration_id=value.merchant_configuration_id,
        merchant_configuration_version=value.merchant_configuration_version,
        merchant_configuration_fingerprint=value.merchant_configuration_fingerprint,
        metadata_fact_id=fact_id,
        credential_reference=value.credential_reference,
        credential_version=value.credential_version,
        metadata_fingerprint=value.fingerprint,
    )


def _pointer_cas_query(pointer: CurrentPointer) -> dict[str, object]:
    """Build all three immutable CAS antecedents plus stream identity."""
    return {
        "tenant_id": pointer.tenant_id,
        "provider_id": pointer.provider_id,
        "merchant_configuration_id": pointer.merchant_configuration_id,
        "merchant_configuration_version": pointer.merchant_configuration_version,
        "merchant_configuration_fingerprint": pointer.merchant_configuration_fingerprint,
        "metadata_fact_id": pointer.metadata_fact_id,
        "metadata_fingerprint": pointer.metadata_fingerprint,
    }


def _validate_pointer_fact(pointer: CurrentPointer, fact: TenantInboundProviderCredentialMaterialMetadata) -> None:
    """Require exact tenant, stream, configuration, credential and digest correlation."""
    if (
        pointer.tenant_id != fact.tenant_id
        or pointer.provider_id != fact.provider_id
        or pointer.merchant_configuration_id != fact.merchant_configuration_id
        or pointer.merchant_configuration_version != fact.merchant_configuration_version
        or pointer.merchant_configuration_fingerprint != fact.merchant_configuration_fingerprint
        or pointer.metadata_fact_id != metadata_fact_id(fact)
        or pointer.credential_reference != fact.credential_reference
        or pointer.credential_version != fact.credential_version
        or pointer.metadata_fingerprint != fact.fingerprint
    ):
        raise PersistedRecordInvalidError("M11P5R5_POINTER_FACT_CORRELATION_MISMATCH")


def get_fact(tenant_id: str, metadata_fact_id_value: str, fact_collection: Any, *, session: Any) -> TenantInboundProviderCredentialMaterialMetadata | None:
    """Read one historical tenant-scoped fact; no currentness or source recheck."""
    tx = _active_transaction(session)
    rows = _rows(fact_collection, _fact_query(tenant_id, metadata_fact_id_value), tx)
    if len(rows) > 1:
        raise TenantInboundProviderCredentialMaterialMetadataRegistryPersistenceCorruptionError("M11P5R5_DUPLICATE_FACT_IDENTITY")
    return None if not rows else _hydrate_fact(rows[0])


def get_fact_by_idempotency_key(tenant_id: str, provider_id: str, merchant_configuration_id: str, merchant_configuration_version: int, idempotency_key: str, fact_collection: Any, *, session: Any) -> TenantInboundProviderCredentialMaterialMetadata | None:
    """Read one fact by the frozen tenant-wide idempotency scope."""
    tx = _active_transaction(session)
    key = _text(IDEMPOTENCY_KEY_FIELD, idempotency_key, maximum=IDEMPOTENCY_KEY_MAX_LENGTH)
    query = _stream_query(tenant_id, provider_id, merchant_configuration_id, merchant_configuration_version)
    query[IDEMPOTENCY_KEY_FIELD] = key
    rows = _rows(fact_collection, query, tx)
    if len(rows) > 1:
        raise TenantInboundProviderCredentialMaterialMetadataRegistryPersistenceCorruptionError("M11P5R5_DUPLICATE_IDEMPOTENCY")
    return None if not rows else _hydrate_fact(rows[0])


def get_current_pointer(tenant_id: str, provider_id: str, merchant_configuration_id: str, merchant_configuration_version: int, pointer_collection: Any, *, session: Any) -> CurrentPointer | None:
    """Read the sole explicit pointer for a stream, never infer latest."""
    tx = _active_transaction(session)
    rows = _rows(pointer_collection, _stream_query(tenant_id, provider_id, merchant_configuration_id, merchant_configuration_version), tx)
    if len(rows) > 1:
        raise TenantInboundProviderCredentialMaterialMetadataRegistryPersistenceCorruptionError("M11P5R5_MULTIPLE_CURRENT_POINTERS")
    return None if not rows else _hydrate_pointer(rows[0])


def get_current_metadata(tenant_id: str, provider_id: str, merchant_configuration_id: str, merchant_configuration_version: int, merchant_configuration_fingerprint: str, *, fact_collection: Any, pointer_collection: Any, session: Any) -> TenantInboundProviderCredentialMaterialMetadata | None:
    """Resolve stream pointer then return its exactly referenced durable fact."""
    tx = _active_transaction(session)
    config_fp = _fingerprint("merchant_configuration_fingerprint", merchant_configuration_fingerprint)
    pointer = get_current_pointer(tenant_id, provider_id, merchant_configuration_id, merchant_configuration_version, pointer_collection, session=tx)
    if pointer is None:
        return None
    if pointer.merchant_configuration_fingerprint != config_fp:
        raise CurrentPointerConflictError("M11P5R5_CURRENT_CONFIGURATION_FINGERPRINT_MISMATCH")
    fact_rows = _rows(fact_collection, _fact_query(tenant_id, pointer.metadata_fact_id), tx)
    if len(fact_rows) != 1:
        raise PersistedRecordInvalidError("M11P5R5_POINTER_FACT_MISSING")
    fact = _hydrate_fact(fact_rows[0])
    _validate_pointer_fact(pointer, fact)
    return fact


get_current = get_current_metadata
get_current_fact = get_current_metadata


def get_fact_by_id(tenant_id: str, metadata_fact_id_value: str, fact_collection: Any, *, session: Any) -> TenantInboundProviderCredentialMaterialMetadata | None:
    """Alias retaining the historical tenant-scoped read contract."""
    return get_fact(tenant_id, metadata_fact_id_value, fact_collection, session=session)


def persist_fact_and_advance_current(value: TenantInboundProviderCredentialMaterialMetadata, credential_material_metadata_idempotency_key: str, expected_prior_metadata_fact_id: str | None, expected_prior_metadata_fingerprint: str | None, *, expected_prior_configuration_fingerprint: str | None = None, fact_collection: Any, pointer_collection: Any, session: Any) -> TenantInboundProviderCredentialMaterialMetadata:
    """Persist/replay one generation and optionally advance explicit currentness.

    The caller owns the transaction. Replay is checked before writes; a
    same-generation re-observation under a new key returns the existing fact,
    while a same-key structural divergence fails closed. New generations require
    all three current-pointer CAS antecedents and insert/update atomically.
    """
    tx = _active_transaction(session)
    if not isinstance(value, TenantInboundProviderCredentialMaterialMetadata):
        raise TenantInboundProviderCredentialMaterialMetadataRegistryError("M11P5R5_METADATA_REQUIRED")
    key = _text(IDEMPOTENCY_KEY_FIELD, credential_material_metadata_idempotency_key, maximum=IDEMPOTENCY_KEY_MAX_LENGTH)
    facts = _collection(fact_collection, "FACT")
    pointers = _collection(pointer_collection, "POINTER")

    replay_rows = _rows(facts, _idempotency_query(value, key), tx)
    if len(replay_rows) > 1:
        raise TenantInboundProviderCredentialMaterialMetadataRegistryPersistenceCorruptionError("M11P5R5_DUPLICATE_IDEMPOTENCY")
    if replay_rows:
        existing = _hydrate_fact(replay_rows[0])
        if existing.to_dict() == value.to_dict() and replay_rows[0].get(METADATA_FACT_ID_FIELD) == metadata_fact_id(value):
            return existing
        raise IdempotencyConflictError("M11P5R5_IDEMPOTENCY_PAYLOAD_CONFLICT")

    # Generation lookup deliberately uses R4D generation_identity/same_generation,
    # never full Python equality (observed_at is descriptive re-observation data).
    generation_query = _stream_query_for(value)
    generation_query["credential_version"] = value.credential_version
    generation_rows = _rows(facts, generation_query, tx)
    if len(generation_rows) > 1:
        raise TenantInboundProviderCredentialMaterialMetadataRegistryPersistenceCorruptionError("M11P5R5_DUPLICATE_CREDENTIAL_GENERATION")
    if generation_rows:
        existing = _hydrate_fact(generation_rows[0])
        if existing.same_generation(value):
            return existing
        raise GenerationConflictError("M11P5R5_CREDENTIAL_VERSION_GENERATION_CONFLICT")

    fact_id = metadata_fact_id(value)
    identity_rows = _rows(facts, _fact_query(value.tenant_id, fact_id), tx)
    if identity_rows:
        existing = _hydrate_fact(identity_rows[0])
        if existing.same_generation(value):
            return existing
        raise DuplicateFactIdentityError("M11P5R5_FACT_IDENTITY_CONFLICT")

    pointer_rows = _rows(pointers, _stream_query_for(value), tx)
    if len(pointer_rows) > 1:
        raise TenantInboundProviderCredentialMaterialMetadataRegistryPersistenceCorruptionError("M11P5R5_MULTIPLE_CURRENT_POINTERS")
    current = None if not pointer_rows else _hydrate_pointer(pointer_rows[0])
    if current is None:
        if any(item is not None for item in (expected_prior_metadata_fact_id, expected_prior_metadata_fingerprint, expected_prior_configuration_fingerprint)):
            raise CASConflictError("M11P5R5_INITIAL_EXPECTED_PRIOR_MUST_BE_NONE")
    else:
        if expected_prior_metadata_fact_id is None or expected_prior_metadata_fingerprint is None or expected_prior_configuration_fingerprint is None:
            raise CASConflictError("M11P5R5_EXPECTED_PRIOR_POINTER_REQUIRED")
        _text("expected_prior_metadata_fact_id", expected_prior_metadata_fact_id)
        _fingerprint("expected_prior_metadata_fingerprint", expected_prior_metadata_fingerprint)
        _fingerprint("expected_prior_configuration_fingerprint", expected_prior_configuration_fingerprint)
        if current.metadata_fact_id != expected_prior_metadata_fact_id:
            raise CASConflictError("M11P5R5_EXPECTED_PRIOR_FACT_ID_MISMATCH")
        if current.metadata_fingerprint != expected_prior_metadata_fingerprint:
            raise CASConflictError("M11P5R5_EXPECTED_PRIOR_METADATA_FINGERPRINT_MISMATCH")
        if current.merchant_configuration_fingerprint != expected_prior_configuration_fingerprint or current.merchant_configuration_fingerprint != value.merchant_configuration_fingerprint:
            raise CASConflictError("M11P5R5_EXPECTED_PRIOR_CONFIGURATION_FINGERPRINT_MISMATCH")

    facts.insert_one(_fact_document(value, fact_id, key), **_session_kwargs(tx))
    next_pointer = _pointer_for(value, fact_id)
    try:
        if current is None:
            pointers.insert_one(next_pointer.to_dict(), **_session_kwargs(tx))
        else:
            result = pointers.update_one(
                _pointer_cas_query(current), {"$set": next_pointer.to_dict()}, **_session_kwargs(tx)
            )
            if getattr(result, "matched_count", 0) != 1:
                raise CASConflictError("M11P5R5_POINTER_CAS_FAILED")
    except DuplicateKeyError:
        raise
    except PyMongoError:
        raise
    return value


append_fact_and_advance_current = persist_fact_and_advance_current
persist_and_advance = persist_fact_and_advance_current


class TenantInboundProviderCredentialMaterialMetadataRegistry:
    """Static facade; no constructor, network, Mongo, or source authentication."""

    ensure_indexes = staticmethod(ensure_indexes)
    metadata_fact_id = staticmethod(metadata_fact_id)
    get_fact = staticmethod(get_fact)
    get_by_id = staticmethod(get_fact_by_id)
    get_fact_by_id = staticmethod(get_fact_by_id)
    get_fact_by_idempotency_key = staticmethod(get_fact_by_idempotency_key)
    get_by_idempotency_key = staticmethod(get_fact_by_idempotency_key)
    get_current_pointer = staticmethod(get_current_pointer)
    get_current_metadata = staticmethod(get_current_metadata)
    get_current_fact = staticmethod(get_current_metadata)
    get_current = staticmethod(get_current_metadata)
    persist_fact_and_advance_current = staticmethod(persist_fact_and_advance_current)
    append_fact_and_advance_current = staticmethod(persist_fact_and_advance_current)
    create = staticmethod(persist_fact_and_advance_current)


CredentialMaterialMetadataRegistry = TenantInboundProviderCredentialMaterialMetadataRegistry


__all__ = [
    "AUTHORITY_UNIQUE_INDEX_COUNT", "CAMPAIGN_IDENTITY", "CREDENTIAL_VERSION_INDEX_NAME", "TENANT_CREDENTIAL_VERSION_INDEX_NAME",
    "CREDENTIAL_MATERIAL_METADATA_IDEMPOTENCY_KEY_FIELD", "METADATA_FACT_IDENTITY_INDEX_NAME",
    "CURRENT_POINTER_COLLECTION", "CURRENT_POINTER_INDEX_NAME", "CURRENT_STREAM_IDENTITY",
    "CredentialMaterialMetadataRegistry", "CurrentPointer", "EVENT_COLLECTION", "FACT_COLLECTION",
    "FACT_IDENTITY_INDEX_NAME", "FACT_ID_SCHEMA", "HASH_ALGORITHM", "IDEMPOTENCY_INDEX_NAME",
    "IDEMPOTENCY_KEY_FIELD", "IDEMPOTENCY_KEY_MAX_LENGTH", "METADATA_FACT_ID_FIELD",
    "POINTER_COLLECTION", "SLOT_COLLECTION", "TenantInboundProviderCredentialMaterialMetadataCurrent",
    "TenantInboundProviderCredentialMaterialMetadataRegistry", "TenantInboundProviderCredentialMaterialMetadataRegistryCASConflictError",
    "TenantInboundProviderCredentialMaterialMetadataRegistryCurrentPointerConflictError", "TenantInboundProviderCredentialMaterialMetadataRegistryDuplicateFactIdentityError",
    "TenantInboundProviderCredentialMaterialMetadataRegistryError", "TenantInboundProviderCredentialMaterialMetadataRegistryGenerationConflictError",
    "TenantInboundProviderCredentialMaterialMetadataRegistryIdempotencyConflictError", "TenantInboundProviderCredentialMaterialMetadataRegistryNotFoundError",
    "TenantInboundProviderCredentialMaterialMetadataRegistryPersistedRecordInvalidError", "TenantInboundProviderCredentialMaterialMetadataRegistryRecordInvalidError", "TenantInboundProviderCredentialMaterialMetadataRegistryPersistenceCorruptionError",
    "TenantInboundProviderCredentialMaterialMetadataRegistryReplayConflictError", "TenantInboundProviderCredentialMaterialMetadataRegistryTransactionRequiredError", "TenantInboundProviderCredentialMaterialMetadataRegistryTransactionError",
    "VERSION", "append_fact_and_advance_current", "ensure_indexes", "get_current_metadata", "get_current_pointer", "get_fact", "get_fact_by_id", "get_fact_by_idempotency_key", "metadata_fact_id", "persist_fact_and_advance_current",
]


# ARTIFACT: tenant_inbound_provider_credential_material_metadata_registry.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R5
# AUTHORITY BOUNDARY: durable metadata facts and explicit current pointer only.
# TENANT POSTURE: tenant-scoped identity, idempotency, replay, and CAS.
# FAIL-CLOSED POSTURE: strict hydration, exact indexes, caller transaction required.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
