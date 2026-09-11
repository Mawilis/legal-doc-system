"""WILSY OS durable tenant inbound provider credential-security registry.

TITLE: Tenant Inbound Provider Credential Security Authority Registry
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P3-R2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Caller-transaction persistence for immutable credential-security facts,
         tenant-scoped replay, and an explicit current security slot.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_inbound_provider_credential_security_authority_registry.py
COLLABORATION / OWNERSHIP: SaaS credential-security persistence owner; P2 owns
                            the immutable fact and later P4 owns issuance.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P3-R2 repairs current-pointer stream identity
           to make tenant/provider/configuration/version uniqueness race-safe while
           retaining configuration fingerprint as an exact correlation fact.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references and fingerprints only; no secret,
                             KMS, provider transport, or network access.
TENANT BOUNDARY: Every fact, pointer, replay, and CAS predicate carries tenant_id.
AUTHORITY BOUNDARY: Persistence/currentness only; no fresh evaluation, issuance,
                    authorization lookup, binding, checkout, or secret use.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
TRANSACTION BOUNDARY: Caller supplies the active session and owns commit, abort,
                       and whole-transaction retry behavior.
FAIL-CLOSED DECLARATION: Corrupt facts, pointers, divergent replays, duplicate
                          identities, and stale CAS expectations reject.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, ClassVar, Mapping, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.tenant_inbound_provider_credential_security_authority import (
    TenantInboundProviderCredentialSecurityAuthority,
    TenantInboundProviderCredentialSecurityAuthorityError,
)


VERSION = "v1.0.0-M11-R8-R3B-P8-P3D-P3-R2"
CAMPAIGN_IDENTITY = "M11-R8-R3B-P8-P3D-P3-R2"
FACT_COLLECTION = "tenant_inbound_provider_credential_security_facts"
CURRENT_POINTER_COLLECTION = "tenant_inbound_provider_credential_security_current"
# Naming aliases keep the two-collection responsibility explicit for callers using
# event/slot terminology without creating parallel persistence surfaces.
EVENT_COLLECTION = FACT_COLLECTION
POINTER_COLLECTION = CURRENT_POINTER_COLLECTION
SLOT_COLLECTION = CURRENT_POINTER_COLLECTION
FIRST_SECURITY_REVISION = 0
SECURITY_REVISION_INCREMENT = 1
SECURITY_FACT_ID_FIELD = "security_fact_id"
IDEMPOTENCY_KEY_FIELD = "credential_security_idempotency_key"
FACT_IDENTITY_INDEX_NAME = "tenant_credential_security_fact_identity_unique"
IDEMPOTENCY_INDEX_NAME = "tenant_provider_configuration_credential_security_idempotency_unique"
REVISION_INDEX_NAME = "tenant_provider_configuration_security_revision_unique"
CURRENT_POINTER_INDEX_NAME = "tenant_provider_configuration_security_current_unique"


class TenantInboundProviderCredentialSecurityAuthorityRegistryError(RuntimeError):
    """Base fail-closed registry error."""


class TenantInboundProviderCredentialSecurityAuthorityRegistryTransactionError(
    TenantInboundProviderCredentialSecurityAuthorityRegistryError
):
    """Mutation or lookup lacked the caller-owned active transaction."""


class TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError(
    TenantInboundProviderCredentialSecurityAuthorityRegistryError
):
    """A durable fact or pointer cannot be reconstructed strictly."""


class TenantInboundProviderCredentialSecurityAuthorityRegistryReplayConflictError(
    TenantInboundProviderCredentialSecurityAuthorityRegistryError
):
    """A tenant-scoped idempotency identity has divergent immutable material."""


class TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError(
    TenantInboundProviderCredentialSecurityAuthorityRegistryError
):
    """The expected prior current pointer no longer matches."""


class TenantInboundProviderCredentialSecurityAuthorityRegistryPersistenceCorruptionError(
    TenantInboundProviderCredentialSecurityAuthorityRegistryError
):
    """Independent durable identities disagree and cannot be inferred safely."""


def _active_transaction(session: Any) -> Any:
    """Require a caller-owned active transaction without creating or ending one."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryTransactionError(
            "M11P3D_ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _collection(value: Any, name: str) -> Any:
    """Require an explicit collection; the registry never opens a database itself."""
    if value is None:
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryError(
            f"M11P3D_{name}_COLLECTION_REQUIRED"
        )
    return value


def _session_kwargs(session: Any) -> dict[str, object]:
    """Propagate the caller's session to every Mongo operation."""
    return {"session": session}


def _text(name: str, value: object) -> str:
    """Require an exact non-blank lookup string without normalization."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryError(
            f"M11P3D_INVALID_{name.upper()}"
        )
    return value


def _public(document: Mapping[str, object]) -> dict[str, object]:
    """Remove only Mongo's transport identity from a durable document."""
    return {key: value for key, value in document.items() if key != "_id"}


def _fact_document(
    value: TenantInboundProviderCredentialSecurityAuthority,
    security_fact_id: str,
    idempotency_key: str,
) -> dict[str, object]:
    """Serialize the exact P2 fact plus registry-owned replay metadata."""
    document = value.to_dict()
    document[SECURITY_FACT_ID_FIELD] = security_fact_id
    document[IDEMPOTENCY_KEY_FIELD] = idempotency_key
    return document


def _fact_payload(document: Mapping[str, object]) -> dict[str, object]:
    """Return only P2 fields for strict domain hydration."""
    payload = _public(document)
    payload.pop(SECURITY_FACT_ID_FIELD, None)
    payload.pop(IDEMPOTENCY_KEY_FIELD, None)
    return payload


def _hydrate_fact(document: Mapping[str, object]) -> TenantInboundProviderCredentialSecurityAuthority:
    """Hydrate through the P2 constructor; corrupt rows are never repaired."""
    if SECURITY_FACT_ID_FIELD not in document or IDEMPOTENCY_KEY_FIELD not in document:
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError(
            "M11P3D_FACT_REGISTRY_METADATA_MISSING"
        )
    try:
        _text(SECURITY_FACT_ID_FIELD, document[SECURITY_FACT_ID_FIELD])
        _text(IDEMPOTENCY_KEY_FIELD, document[IDEMPOTENCY_KEY_FIELD])
        fact = TenantInboundProviderCredentialSecurityAuthority.from_dict(_fact_payload(document))
        if document[SECURITY_FACT_ID_FIELD] != security_fact_id(fact):
            raise TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError(
                "M11P3D_FACT_IDENTITY_MISMATCH"
            )
        return fact
    except (TenantInboundProviderCredentialSecurityAuthorityError, TypeError, ValueError) as error:
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError(
            "M11P3D_CORRUPT_SECURITY_FACT"
        ) from error


def _canonical_identity_payload(
    value: TenantInboundProviderCredentialSecurityAuthority,
) -> dict[str, object]:
    """Expose deterministic P2 serialization used for durable fact identity."""
    return value.to_dict()


def security_fact_id(value: TenantInboundProviderCredentialSecurityAuthority) -> str:
    """Return a deterministic identity distinct from the domain fingerprint."""
    canonical = json.dumps(
        {"schema": "WILSY-TENANT-INBOUND-PROVIDER-CREDENTIAL-SECURITY-FACT-ID/V1", "fact": _canonical_identity_payload(value)},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(canonical).hexdigest()


@dataclass(frozen=True, slots=True)
class TenantInboundProviderCredentialSecurityCurrent:
    """Strict immutable projection of the explicit current security pointer."""

    tenant_id: str
    provider_id: str
    merchant_configuration_id: str
    merchant_configuration_version: int
    merchant_configuration_fingerprint: str
    security_fact_id: str
    security_revision: int
    credential_version: str
    security_fingerprint: str

    _FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "tenant_id",
            "provider_id",
            "merchant_configuration_id",
            "merchant_configuration_version",
            "merchant_configuration_fingerprint",
            "security_fact_id",
            "security_revision",
            "credential_version",
            "security_fingerprint",
        }
    )

    def __post_init__(self) -> None:
        for name in (
            "tenant_id",
            "provider_id",
            "merchant_configuration_id",
            "security_fact_id",
            "credential_version",
        ):
            _text(name, getattr(self, name))
        if (
            isinstance(self.merchant_configuration_version, bool)
            or not isinstance(self.merchant_configuration_version, int)
            or self.merchant_configuration_version < 1
        ):
            raise TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError(
                "M11P3D_INVALID_POINTER_CONFIGURATION_VERSION"
            )
        if (
            isinstance(self.security_revision, bool)
            or not isinstance(self.security_revision, int)
            or self.security_revision < 0
        ):
            raise TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError(
                "M11P3D_INVALID_POINTER_SECURITY_REVISION"
            )
        for name in ("merchant_configuration_fingerprint", "security_fingerprint"):
            fingerprint = getattr(self, name)
            if not isinstance(fingerprint, str) or len(fingerprint) != 128 or any(
                character not in "0123456789abcdef" for character in fingerprint
            ):
                raise TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError(
                    f"M11P3D_INVALID_POINTER_{name.upper()}"
                )

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact nine-field pointer projection."""
        return {
            "tenant_id": self.tenant_id,
            "provider_id": self.provider_id,
            "merchant_configuration_id": self.merchant_configuration_id,
            "merchant_configuration_version": self.merchant_configuration_version,
            "merchant_configuration_fingerprint": self.merchant_configuration_fingerprint,
            "security_fact_id": self.security_fact_id,
            "security_revision": self.security_revision,
            "credential_version": self.credential_version,
            "security_fingerprint": self.security_fingerprint,
        }


CurrentPointer = TenantInboundProviderCredentialSecurityCurrent


def _hydrate_pointer(document: Mapping[str, object]) -> TenantInboundProviderCredentialSecurityCurrent:
    """Strictly hydrate a pointer and reject every missing or unknown field."""
    raw = _public(document)
    if set(raw) != set(TenantInboundProviderCredentialSecurityCurrent._FIELDS):
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError(
            "M11P3D_INVALID_CURRENT_POINTER_SCHEMA"
        )
    try:
        return TenantInboundProviderCredentialSecurityCurrent(
            tenant_id=cast(str, raw["tenant_id"]),
            provider_id=cast(str, raw["provider_id"]),
            merchant_configuration_id=cast(str, raw["merchant_configuration_id"]),
            merchant_configuration_version=cast(int, raw["merchant_configuration_version"]),
            merchant_configuration_fingerprint=cast(str, raw["merchant_configuration_fingerprint"]),
            security_fact_id=cast(str, raw["security_fact_id"]),
            security_revision=cast(int, raw["security_revision"]),
            credential_version=cast(str, raw["credential_version"]),
            security_fingerprint=cast(str, raw["security_fingerprint"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        if isinstance(error, TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError):
            raise
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError(
            "M11P3D_CORRUPT_CURRENT_POINTER"
        ) from error


def ensure_indexes(fact_collection: Any, pointer_collection: Any) -> None:
    """Declare the four scalar, tenant-scoped uniqueness constraints explicitly."""
    facts = _collection(fact_collection, "FACT")
    pointers = _collection(pointer_collection, "POINTER")
    facts.create_index(
        [("tenant_id", ASCENDING), (SECURITY_FACT_ID_FIELD, ASCENDING)],
        unique=True,
        name=FACT_IDENTITY_INDEX_NAME,
    )
    facts.create_index(
        [
            ("tenant_id", ASCENDING),
            ("provider_id", ASCENDING),
            ("merchant_configuration_id", ASCENDING),
            ("merchant_configuration_version", ASCENDING),
            (IDEMPOTENCY_KEY_FIELD, ASCENDING),
        ],
        unique=True,
        name=IDEMPOTENCY_INDEX_NAME,
    )
    facts.create_index(
        [
            ("tenant_id", ASCENDING),
            ("provider_id", ASCENDING),
            ("merchant_configuration_id", ASCENDING),
            ("merchant_configuration_version", ASCENDING),
            ("security_revision", ASCENDING),
        ],
        unique=True,
        name=REVISION_INDEX_NAME,
    )
    pointers.create_index(
        [
            ("tenant_id", ASCENDING),
            ("provider_id", ASCENDING),
            ("merchant_configuration_id", ASCENDING),
            ("merchant_configuration_version", ASCENDING),
        ],
        unique=True,
        name=CURRENT_POINTER_INDEX_NAME,
    )


def _slot_query(value: TenantInboundProviderCredentialSecurityAuthority) -> dict[str, object]:
    """Build the four-field canonical stream-slot predicate.

    Configuration fingerprint is deliberately excluded from slot identity.  It
    remains a correlated immutable authority field validated after the one
    durable stream pointer is loaded.
    """
    return {
        "tenant_id": value.tenant_id,
        "provider_id": value.provider_id,
        "merchant_configuration_id": value.merchant_configuration_id,
        "merchant_configuration_version": value.merchant_configuration_version,
    }


def _stream_prefix_query(value: TenantInboundProviderCredentialSecurityAuthority) -> dict[str, object]:
    """Return the canonical stream identity used by legacy drift probes."""
    return _slot_query(value)


def _idempotency_query(
    value: TenantInboundProviderCredentialSecurityAuthority, key: str
) -> dict[str, object]:
    """Build the frozen tenant/provider/configuration/version/key replay scope."""
    return {
        "tenant_id": value.tenant_id,
        "provider_id": value.provider_id,
        "merchant_configuration_id": value.merchant_configuration_id,
        "merchant_configuration_version": value.merchant_configuration_version,
        IDEMPOTENCY_KEY_FIELD: key,
    }


def _fact_query(tenant_id: str, fact_id: str) -> dict[str, object]:
    """Build a tenant-scoped durable fact identity predicate."""
    return {"tenant_id": tenant_id, SECURITY_FACT_ID_FIELD: fact_id}


def _prior_pointer_query(
    value: TenantInboundProviderCredentialSecurityAuthority,
    expected_prior_revision: int,
    expected_prior_fact_id: str,
    expected_prior_security_fingerprint: str,
    expected_prior_configuration_fingerprint: str,
) -> dict[str, object]:
    """Build the complete expected-prior CAS antecedent."""
    query = _slot_query(value)
    query.update(
        {
            "merchant_configuration_fingerprint": expected_prior_configuration_fingerprint,
            "security_fact_id": expected_prior_fact_id,
            "security_revision": expected_prior_revision,
            "security_fingerprint": expected_prior_security_fingerprint,
        }
    )
    return query


def _pointer_for(
    value: TenantInboundProviderCredentialSecurityAuthority,
    fact_id: str,
) -> TenantInboundProviderCredentialSecurityCurrent:
    """Project a fresh fact into the explicit current pointer."""
    return TenantInboundProviderCredentialSecurityCurrent(
        tenant_id=value.tenant_id,
        provider_id=value.provider_id,
        merchant_configuration_id=value.merchant_configuration_id,
        merchant_configuration_version=value.merchant_configuration_version,
        merchant_configuration_fingerprint=value.merchant_configuration_fingerprint,
        security_fact_id=fact_id,
        security_revision=value.security_revision,
        credential_version=value.credential_version,
        security_fingerprint=value.fingerprint,
    )


def get_fact(
    tenant_id: str,
    security_fact_id_value: str,
    fact_collection: Any,
    *,
    session: Any,
) -> TenantInboundProviderCredentialSecurityAuthority | None:
    """Strictly read one tenant-scoped immutable fact inside the caller transaction."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    fact_id = _text(SECURITY_FACT_ID_FIELD, security_fact_id_value)
    row = _collection(fact_collection, "FACT").find_one(
        _fact_query(tenant, fact_id), **_session_kwargs(tx)
    )
    return None if row is None else _hydrate_fact(row)


def get_fact_by_idempotency_key(
    tenant_id: str,
    provider_id: str,
    merchant_configuration_id: str,
    merchant_configuration_version: int,
    idempotency_key: str,
    fact_collection: Any,
    *,
    session: Any,
) -> TenantInboundProviderCredentialSecurityAuthority | None:
    """Strictly read by the frozen tenant/provider/configuration/key replay scope."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    provider = _text("provider_id", provider_id)
    configuration = _text("merchant_configuration_id", merchant_configuration_id)
    key = _text(IDEMPOTENCY_KEY_FIELD, idempotency_key)
    if (
        isinstance(merchant_configuration_version, bool)
        or not isinstance(merchant_configuration_version, int)
        or merchant_configuration_version < 1
    ):
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryError(
            "M11P3D_INVALID_MERCHANT_CONFIGURATION_VERSION"
        )
    row = _collection(fact_collection, "FACT").find_one(
        {
            "tenant_id": tenant,
            "provider_id": provider,
            "merchant_configuration_id": configuration,
            "merchant_configuration_version": merchant_configuration_version,
            IDEMPOTENCY_KEY_FIELD: key,
        },
        **_session_kwargs(tx),
    )
    return None if row is None else _hydrate_fact(row)


def get_current_pointer(
    value: TenantInboundProviderCredentialSecurityAuthority,
    pointer_collection: Any,
    *,
    session: Any,
) -> TenantInboundProviderCredentialSecurityCurrent | None:
    """Read the explicit tenant/configuration current pointer, never latest fact."""
    tx = _active_transaction(session)
    pointers = _collection(pointer_collection, "POINTER")
    rows = _current_pointer_rows(pointers, _slot_query(value), tx)
    if len(rows) > 1:
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryPersistenceCorruptionError(
            "M11P3D_MULTIPLE_CURRENT_POINTERS"
        )
    if not rows:
        return None
    pointer = _hydrate_pointer(rows[0])
    if pointer.merchant_configuration_fingerprint != value.merchant_configuration_fingerprint:
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError(
            "M11P3D_CONFIGURATION_FINGERPRINT_MISMATCH"
        )
    return pointer


def _current_pointer_rows(
    pointer_collection: Any,
    query: dict[str, object],
    session: Any,
) -> list[Mapping[str, object]]:
    """Load every pointer in one stream so corrupt parallel rows fail closed."""
    if hasattr(pointer_collection, "find"):
        return [cast(Mapping[str, object], row) for row in pointer_collection.find(query, **_session_kwargs(session))]
    row = pointer_collection.find_one(query, **_session_kwargs(session))
    return [] if row is None else [cast(Mapping[str, object], row)]


def get_current_fact(
    tenant_id: str,
    provider_id: str,
    merchant_configuration_id: str,
    merchant_configuration_version: int,
    merchant_configuration_fingerprint: str,
    *,
    fact_collection: Any,
    pointer_collection: Any,
    session: Any,
) -> TenantInboundProviderCredentialSecurityAuthority | None:
    """Read pointer then referenced fact and prove every correlation field."""
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    provider = _text("provider_id", provider_id)
    configuration = _text("merchant_configuration_id", merchant_configuration_id)
    if (
        isinstance(merchant_configuration_version, bool)
        or not isinstance(merchant_configuration_version, int)
        or merchant_configuration_version < 1
    ):
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryError(
            "M11P3D_INVALID_MERCHANT_CONFIGURATION_VERSION"
        )
    _text("merchant_configuration_fingerprint", merchant_configuration_fingerprint)
    pointer_rows = _current_pointer_rows(
        _collection(pointer_collection, "POINTER"),
        {
            "tenant_id": tenant,
            "provider_id": provider,
            "merchant_configuration_id": configuration,
            "merchant_configuration_version": merchant_configuration_version,
        },
        tx,
    )
    if len(pointer_rows) > 1:
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryPersistenceCorruptionError(
            "M11P3D_MULTIPLE_CURRENT_POINTERS"
        )
    if not pointer_rows:
        return None
    pointer = _hydrate_pointer(pointer_rows[0])
    if pointer.merchant_configuration_fingerprint != merchant_configuration_fingerprint:
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError(
            "M11P3D_CONFIGURATION_FINGERPRINT_MISMATCH"
        )
    fact_row = _collection(fact_collection, "FACT").find_one(
        _fact_query(tenant, pointer.security_fact_id), **_session_kwargs(tx)
    )
    if fact_row is None:
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError(
            "M11P3D_POINTER_FACT_MISSING"
        )
    fact = _hydrate_fact(fact_row)
    if (
        pointer.tenant_id != fact.tenant_id
        or pointer.provider_id != fact.provider_id
        or pointer.merchant_configuration_id != fact.merchant_configuration_id
        or pointer.merchant_configuration_version != fact.merchant_configuration_version
        or pointer.merchant_configuration_fingerprint != fact.merchant_configuration_fingerprint
        or pointer.security_fact_id != security_fact_id(fact)
        or pointer.security_revision != fact.security_revision
        or pointer.credential_version != fact.credential_version
        or pointer.security_fingerprint != fact.fingerprint
    ):
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError(
            "M11P3D_POINTER_FACT_PROVENANCE_MISMATCH"
        )
    return fact


get_current = get_current_fact
get_current_security_fact = get_current_fact
get_by_id = get_fact
get_by_idempotency_key = get_fact_by_idempotency_key


def persist_fact_and_advance_current(
    value: TenantInboundProviderCredentialSecurityAuthority,
    credential_security_idempotency_key: str,
    expected_prior_revision: int | None,
    expected_prior_fact_id: str | None,
    expected_prior_security_fingerprint: str | None,
    *,
    expected_prior_configuration_fingerprint: str | None = None,
    fact_collection: Any,
    pointer_collection: Any,
    session: Any,
) -> TenantInboundProviderCredentialSecurityAuthority:
    """Persist one fact and advance its pointer inside the caller transaction.

    Replay is resolved before CAS.  A fresh transition validates the complete
    expected prior pointer before writing; Mongo duplicate/CAS failures propagate
    so the caller can abort and retry the whole transaction from fresh state.
    """
    tx = _active_transaction(session)
    if not isinstance(value, TenantInboundProviderCredentialSecurityAuthority):
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryError(
            "M11P3D_FACT_REQUIRED"
        )
    key = _text(IDEMPOTENCY_KEY_FIELD, credential_security_idempotency_key)
    facts = _collection(fact_collection, "FACT")
    pointers = _collection(pointer_collection, "POINTER")
    replay_row = facts.find_one(_idempotency_query(value, key), **_session_kwargs(tx))
    if replay_row is not None:
        replay_fact = _hydrate_fact(replay_row)
        if replay_fact.to_dict() == value.to_dict() and replay_row.get(SECURITY_FACT_ID_FIELD) == security_fact_id(value):
            return replay_fact
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryReplayConflictError(
            "M11P3D_DIVERGENT_REPLAY"
        )

    fact_id = security_fact_id(value)
    identity_row = facts.find_one(_fact_query(value.tenant_id, fact_id), **_session_kwargs(tx))
    if identity_row is not None:
        existing = _hydrate_fact(identity_row)
        if existing.to_dict() == value.to_dict():
            raise TenantInboundProviderCredentialSecurityAuthorityRegistryReplayConflictError(
                "M11P3D_FACT_ID_ALREADY_BOUND_TO_DIFFERENT_IDEMPOTENCY"
            )
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryReplayConflictError(
            "M11P3D_FACT_IDENTITY_CONFLICT"
        )

    current_rows = _current_pointer_rows(pointers, _slot_query(value), tx)
    if len(current_rows) > 1:
        raise TenantInboundProviderCredentialSecurityAuthorityRegistryPersistenceCorruptionError(
            "M11P3D_MULTIPLE_CURRENT_POINTERS"
        )
    current_row = current_rows[0] if current_rows else None
    if current_row is None:
        if (
            expected_prior_revision is not None
            or expected_prior_fact_id is not None
            or expected_prior_security_fingerprint is not None
            or expected_prior_configuration_fingerprint is not None
            or value.security_revision != FIRST_SECURITY_REVISION
        ):
            raise TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError(
                "M11P3D_INITIAL_POINTER_EXPECTED_NONE"
            )
    else:
        current = _hydrate_pointer(current_row)
        if current.merchant_configuration_fingerprint != value.merchant_configuration_fingerprint:
            raise TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError(
                "M11P3D_CONFIGURATION_FINGERPRINT_DRIFT"
            )
        if (
            expected_prior_revision is None
            or expected_prior_fact_id is None
            or expected_prior_security_fingerprint is None
            or expected_prior_configuration_fingerprint is None
        ):
            raise TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError(
                "M11P3D_EXPECTED_PRIOR_POINTER_REQUIRED"
            )
        if value.security_revision != expected_prior_revision + SECURITY_REVISION_INCREMENT:
            raise TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError(
                "M11P3D_SECURITY_REVISION_NOT_NEXT"
            )
        _text("expected_prior_configuration_fingerprint", expected_prior_configuration_fingerprint)
        if current.merchant_configuration_fingerprint != expected_prior_configuration_fingerprint:
            raise TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError(
                "M11P3D_EXPECTED_PRIOR_CONFIGURATION_FINGERPRINT_MISMATCH"
            )
        if current.merchant_configuration_fingerprint != value.merchant_configuration_fingerprint:
            raise TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError(
                "M11P3D_CONFIGURATION_FINGERPRINT_DRIFT"
            )
        if (
            current.security_revision != expected_prior_revision
            or current.security_fact_id != expected_prior_fact_id
            or current.security_fingerprint != expected_prior_security_fingerprint
        ):
            raise TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError(
                "M11P3D_EXPECTED_PRIOR_POINTER_MISMATCH"
            )

    facts.insert_one(_fact_document(value, fact_id, key), **_session_kwargs(tx))
    next_pointer = _pointer_for(value, fact_id)
    if current_row is None:
        pointers.insert_one(next_pointer.to_dict(), **_session_kwargs(tx))
    else:
        result = pointers.update_one(
            _prior_pointer_query(
                value,
                cast(int, expected_prior_revision),
                cast(str, expected_prior_fact_id),
                cast(str, expected_prior_security_fingerprint),
                cast(str, expected_prior_configuration_fingerprint),
            ),
            {"$set": next_pointer.to_dict()},
            **_session_kwargs(tx),
        )
        if getattr(result, "matched_count", 0) != 1:
            raise TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError(
                "M11P3D_POINTER_CAS_FAILED"
            )
    return value


append_fact_and_advance_current = persist_fact_and_advance_current
persist_and_advance = persist_fact_and_advance_current


class TenantInboundProviderCredentialSecurityAuthorityRegistry:
    """Static repository facade preserving caller-owned transaction authority."""

    ensure_indexes = staticmethod(ensure_indexes)
    get_fact = staticmethod(get_fact)
    get_by_id = staticmethod(get_fact)
    get_fact_by_idempotency_key = staticmethod(get_fact_by_idempotency_key)
    get_by_idempotency_key = staticmethod(get_fact_by_idempotency_key)
    get_current_pointer = staticmethod(get_current_pointer)
    get_current_fact = staticmethod(get_current_fact)
    get_current = staticmethod(get_current_fact)
    get_current_slot = staticmethod(get_current_pointer)
    get = staticmethod(get_fact)
    persist_fact_and_advance_current = staticmethod(persist_fact_and_advance_current)
    append_fact_and_advance_current = staticmethod(persist_fact_and_advance_current)
    append_fact_and_advance_pointer = staticmethod(persist_fact_and_advance_current)
    create = staticmethod(persist_fact_and_advance_current)


CredentialSecurityAuthorityRegistry = TenantInboundProviderCredentialSecurityAuthorityRegistry

__all__ = [
    "CAMPAIGN_IDENTITY",
    "CredentialSecurityAuthorityRegistry",
    "CURRENT_POINTER_COLLECTION",
    "CURRENT_POINTER_INDEX_NAME",
    "CurrentPointer",
    "EVENT_COLLECTION",
    "FACT_COLLECTION",
    "FACT_IDENTITY_INDEX_NAME",
    "FIRST_SECURITY_REVISION",
    "IDEMPOTENCY_INDEX_NAME",
    "IDEMPOTENCY_KEY_FIELD",
    "POINTER_COLLECTION",
    "REVISION_INDEX_NAME",
    "SECURITY_FACT_ID_FIELD",
    "SECURITY_REVISION_INCREMENT",
    "SLOT_COLLECTION",
    "TenantInboundProviderCredentialSecurityAuthorityRegistry",
    "TenantInboundProviderCredentialSecurityAuthorityRegistryCASConflictError",
    "TenantInboundProviderCredentialSecurityAuthorityRegistryError",
    "TenantInboundProviderCredentialSecurityAuthorityRegistryPersistenceCorruptionError",
    "TenantInboundProviderCredentialSecurityAuthorityRegistryRecordInvalidError",
    "TenantInboundProviderCredentialSecurityAuthorityRegistryReplayConflictError",
    "TenantInboundProviderCredentialSecurityAuthorityRegistryTransactionError",
    "TenantInboundProviderCredentialSecurityCurrent",
    "VERSION",
    "append_fact_and_advance_current",
    "ensure_indexes",
    "get_by_id",
    "get_by_idempotency_key",
    "get_current",
    "get_current_fact",
    "get_current_pointer",
    "get_current_security_fact",
    "get_fact",
    "get_fact_by_idempotency_key",
    "persist_and_advance",
    "persist_fact_and_advance_current",
    "security_fact_id",
]


# ARTIFACT: tenant_inbound_provider_credential_security_authority_registry.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P3-R2
# AUTHORITY BOUNDARY: immutable fact persistence, replay, explicit current pointer, and CAS only.
# TENANT POSTURE: all fact, pointer, replay, and CAS predicates include tenant_id.
# FAIL-CLOSED POSTURE: strict hydration and caller-owned transaction failures propagate.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
