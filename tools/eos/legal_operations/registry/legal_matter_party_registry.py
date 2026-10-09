"""WILSY OS durable immutable legal matter-party registry.

TITLE: Legal Matter Party Registry
VERSION: v1.0.0-L8-8B-LEGAL-MATTER-PARTY-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persist exact L8-8A matter-party facts immutably with tenant-scoped
         uniqueness, strict hydration, caller-owned transactions and indexed
         subject-identity lookup for later conflict authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_matter_party_registry.py
COLLABORATION / OWNERSHIP: L8-8A owns party evidence semantics; L8-8B owns
                            immutable durable persistence and exact reads only.
                            A later orchestration must prove the referenced
                            CaseMatter is durable/current before admission, and
                            later conflict authority consumes subject matches.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-L8-8B-LEGAL-MATTER-PARTY-REGISTRY establishes exact replay,
           divergent conflict, strict envelope hydration, tenant/party identity
           uniqueness, tenant/matter/subject uniqueness, tenant+subject lookup,
           bounded matter/subject reads, transaction propagation and governed
           whole-transaction retry signaling.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists only L8-8A opaque party evidence; raw PII,
                             credentials, legal documents and financial data are
                             not added by the registry.
TENANT BOUNDARY: Every lookup/write/index key begins with exact tenant_id.
AUTHORITY BOUNDARY: Persistence only; no matter lifecycle, conflict conclusion,
                    client admission, representation or legal outcome authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Every operational read/write requires an already-active
                      caller-owned Mongo transaction. Registry owns no lifecycle.
FAIL-CLOSED DECLARATION: Missing transaction, malformed/corrupt envelope,
                         divergent replay, duplicate identities, query overflow,
                         races and persistence outages reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast
import hashlib
import json

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_matter_party import (
    PARTY_FIELDS,
    LegalMatterParty,
    LegalMatterPartyError,
)


VERSION: Final[str] = "v1.0.0-L8-8B-LEGAL-MATTER-PARTY-REGISTRY"
RECORD_SCHEMA: Final[str] = "WILSY-LEGAL-MATTER-PARTY-RECORD/V1"
COLLECTION: Final[str] = "legal_matter_parties"
PARTY_ID_INDEX_NAME: Final[str] = "legal_party_tenant_party_unique"
MATTER_SUBJECT_INDEX_NAME: Final[str] = "legal_party_tenant_matter_subject_unique"
MATTER_LOOKUP_INDEX_NAME: Final[str] = "legal_party_tenant_matter_lookup"
SUBJECT_LOOKUP_INDEX_NAME: Final[str] = "legal_party_tenant_subject_lookup"
MAX_MATTER_PARTIES: Final[int] = 500
MAX_SUBJECT_OCCURRENCES: Final[int] = 1000
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")

_RECORD_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "entity_type",
        "tenant_id",
        "party_id",
        "case_matter_id",
        "matter_fingerprint",
        "subject_identity_fingerprint",
        "party_fingerprint",
        "evidence_identity",
        "party_payload",
    }
)


class LegalMatterPartyRegistryError(RuntimeError):
    default_code = "L8_8B_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        self.code = code or self.default_code
        super().__init__(self.code)


class LegalMatterPartyRegistryInputError(LegalMatterPartyRegistryError):
    default_code = "L8_8B_INPUT_INVALID"


class LegalMatterPartyRegistryTransactionRequiredError(LegalMatterPartyRegistryError):
    default_code = "L8_8B_ACTIVE_TRANSACTION_REQUIRED"


class LegalMatterPartyRegistryNotFoundError(LegalMatterPartyRegistryError):
    default_code = "L8_8B_PARTY_NOT_FOUND"


class LegalMatterPartyRegistryConflictError(LegalMatterPartyRegistryError):
    default_code = "L8_8B_PARTY_CONFLICT"


class LegalMatterPartyRegistryPersistedRecordInvalidError(LegalMatterPartyRegistryError):
    default_code = "L8_8B_PERSISTED_RECORD_INVALID"


class LegalMatterPartyRegistryRetryRequiredError(LegalMatterPartyRegistryError):
    default_code = "L8_8B_WHOLE_TRANSACTION_RETRY_REQUIRED"


class LegalMatterPartyRegistryPersistenceUnavailableError(LegalMatterPartyRegistryError):
    default_code = "L8_8B_PERSISTENCE_UNAVAILABLE"


def _raise(
    error_type: type[LegalMatterPartyRegistryError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _raise_mongo(error: PyMongoError) -> NoReturn:
    if error.has_error_label("TransientTransactionError"):
        _raise(LegalMatterPartyRegistryRetryRequiredError, cause=error)
    _raise(LegalMatterPartyRegistryPersistenceUnavailableError, cause=error)


def _target(collection: Any) -> Any:
    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
        )
    except AttributeError:
        return collection


def _collection(value: Any) -> Any:
    if value is None:
        _raise(
            LegalMatterPartyRegistryInputError,
            "L8_8B_COLLECTION_REQUIRED",
        )
    return _target(value)


def _active_transaction(session: Any) -> Any:
    if session is None:
        _raise(LegalMatterPartyRegistryTransactionRequiredError)
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(LegalMatterPartyRegistryTransactionRequiredError)
    return session


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _raise(
            LegalMatterPartyRegistryInputError,
            f"L8_8B_{name.upper()}_INVALID",
        )
    return value


def _fingerprint(name: str, value: object) -> str:
    text = _text(name, value)
    if len(text) != 128 or any(character not in "0123456789abcdef" for character in text):
        _raise(
            LegalMatterPartyRegistryInputError,
            f"L8_8B_{name.upper()}_INVALID",
        )
    return text


def _sha3(value: object) -> str:
    return hashlib.sha3_512(
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _evidence_identity(party: LegalMatterParty) -> str:
    return _sha3(
        {
            "schema": RECORD_SCHEMA,
            "version": VERSION,
            "tenant_id": party.tenant_id,
            "party_id": party.party_id,
            "party_fingerprint": party.fingerprint,
        }
    )


def _record(party: LegalMatterParty) -> dict[str, object]:
    return {
        "schema": RECORD_SCHEMA,
        "version": VERSION,
        "entity_type": "LegalMatterPartyRecord",
        "tenant_id": party.tenant_id,
        "party_id": party.party_id,
        "case_matter_id": party.case_matter_id,
        "matter_fingerprint": party.matter_fingerprint,
        "subject_identity_fingerprint": party.subject_identity_fingerprint,
        "party_fingerprint": party.fingerprint,
        "evidence_identity": _evidence_identity(party),
        "party_payload": party.to_dict(),
    }


def _hydrate(document: Mapping[str, Any]) -> LegalMatterParty:
    if not isinstance(document, Mapping):
        _raise(LegalMatterPartyRegistryPersistedRecordInvalidError)
    raw = dict(document)
    raw.pop("_id", None)
    if set(raw) != _RECORD_FIELDS:
        _raise(
            LegalMatterPartyRegistryPersistedRecordInvalidError,
            "L8_8B_RECORD_SCHEMA_INVALID",
        )
    if (
        raw.get("schema") != RECORD_SCHEMA
        or raw.get("version") != VERSION
        or raw.get("entity_type") != "LegalMatterPartyRecord"
    ):
        _raise(
            LegalMatterPartyRegistryPersistedRecordInvalidError,
            "L8_8B_RECORD_VERSION_UNSUPPORTED",
        )
    payload = raw.get("party_payload")
    if not isinstance(payload, Mapping) or set(payload) != set(PARTY_FIELDS):
        _raise(
            LegalMatterPartyRegistryPersistedRecordInvalidError,
            "L8_8B_PARTY_PAYLOAD_SCHEMA_INVALID",
        )
    try:
        party = LegalMatterParty.from_dict(
            cast(Mapping[str, object], payload)
        )
    except (TypeError, ValueError, LegalMatterPartyError) as error:
        _raise(
            LegalMatterPartyRegistryPersistedRecordInvalidError,
            "L8_8B_PARTY_PAYLOAD_INVALID",
            error,
        )
    if (
        raw.get("tenant_id") != party.tenant_id
        or raw.get("party_id") != party.party_id
        or raw.get("case_matter_id") != party.case_matter_id
        or raw.get("matter_fingerprint") != party.matter_fingerprint
        or raw.get("subject_identity_fingerprint")
        != party.subject_identity_fingerprint
        or raw.get("party_fingerprint") != party.fingerprint
        or raw.get("evidence_identity") != _evidence_identity(party)
    ):
        _raise(
            LegalMatterPartyRegistryPersistedRecordInvalidError,
            "L8_8B_RECORD_CORRELATION_INVALID",
        )
    return party


def _rows(
    collection: Any,
    query: Mapping[str, object],
    *,
    session: Any,
    limit: int,
) -> list[Mapping[str, Any]]:
    target = _collection(collection)
    try:
        cursor = target.find(dict(query), session=session)
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(limit)
        return [cast(Mapping[str, Any], row) for row in cursor]
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _raise(
            LegalMatterPartyRegistryInputError,
            "L8_8B_COLLECTION_INTERFACE_INVALID",
            error,
        )


def ensure_indexes(collection: Any) -> None:
    target = _collection(collection)
    try:
        target.create_index(
            [("tenant_id", ASCENDING), ("party_id", ASCENDING)],
            unique=True,
            name=PARTY_ID_INDEX_NAME,
        )
        target.create_index(
            [
                ("tenant_id", ASCENDING),
                ("case_matter_id", ASCENDING),
                ("subject_identity_fingerprint", ASCENDING),
            ],
            unique=True,
            name=MATTER_SUBJECT_INDEX_NAME,
        )
        target.create_index(
            [("tenant_id", ASCENDING), ("case_matter_id", ASCENDING)],
            unique=False,
            name=MATTER_LOOKUP_INDEX_NAME,
        )
        target.create_index(
            [("tenant_id", ASCENDING), ("subject_identity_fingerprint", ASCENDING)],
            unique=False,
            name=SUBJECT_LOOKUP_INDEX_NAME,
        )
    except PyMongoError as error:
        _raise_mongo(error)
    except AttributeError as error:
        _raise(
            LegalMatterPartyRegistryInputError,
            "L8_8B_COLLECTION_INTERFACE_INVALID",
            error,
        )


def get_party(
    tenant_id: str,
    party_id: str,
    collection: Any,
    *,
    session: Any,
) -> LegalMatterParty:
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    identity = _text("party_id", party_id)
    rows = _rows(
        collection,
        {"tenant_id": tenant, "party_id": identity},
        session=tx,
        limit=2,
    )
    if not rows:
        _raise(LegalMatterPartyRegistryNotFoundError)
    if len(rows) > 1:
        _raise(
            LegalMatterPartyRegistryPersistedRecordInvalidError,
            "L8_8B_DUPLICATE_PARTY_ID",
        )
    return _hydrate(rows[0])


def list_matter_parties(
    tenant_id: str,
    case_matter_id: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[LegalMatterParty, ...]:
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    matter_id = _text("case_matter_id", case_matter_id)
    rows = _rows(
        collection,
        {"tenant_id": tenant, "case_matter_id": matter_id},
        session=tx,
        limit=MAX_MATTER_PARTIES + 1,
    )
    if len(rows) > MAX_MATTER_PARTIES:
        _raise(
            LegalMatterPartyRegistryPersistedRecordInvalidError,
            "L8_8B_MATTER_PARTY_LIMIT_EXCEEDED",
        )
    parties = tuple(_hydrate(row) for row in rows)
    if any(
        item.tenant_id != tenant or item.case_matter_id != matter_id
        for item in parties
    ):
        _raise(
            LegalMatterPartyRegistryPersistedRecordInvalidError,
            "L8_8B_MATTER_QUERY_CORRELATION_INVALID",
        )
    return tuple(sorted(parties, key=lambda item: item.party_id))


def find_subject_occurrences(
    tenant_id: str,
    subject_identity_fingerprint: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[LegalMatterParty, ...]:
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    fingerprint = _fingerprint(
        "subject_identity_fingerprint",
        subject_identity_fingerprint,
    )
    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "subject_identity_fingerprint": fingerprint,
        },
        session=tx,
        limit=MAX_SUBJECT_OCCURRENCES + 1,
    )
    if len(rows) > MAX_SUBJECT_OCCURRENCES:
        _raise(
            LegalMatterPartyRegistryPersistedRecordInvalidError,
            "L8_8B_SUBJECT_OCCURRENCE_LIMIT_EXCEEDED",
        )
    parties = tuple(_hydrate(row) for row in rows)
    if any(
        item.tenant_id != tenant
        or item.subject_identity_fingerprint != fingerprint
        for item in parties
    ):
        _raise(
            LegalMatterPartyRegistryPersistedRecordInvalidError,
            "L8_8B_SUBJECT_QUERY_CORRELATION_INVALID",
        )
    return tuple(
        sorted(
            parties,
            key=lambda item: (item.case_matter_id, item.party_id),
        )
    )


def persist_party(
    party: LegalMatterParty,
    collection: Any,
    *,
    session: Any,
) -> LegalMatterParty:
    tx = _active_transaction(session)
    if type(party) is not LegalMatterParty:
        _raise(
            LegalMatterPartyRegistryInputError,
            "L8_8B_PARTY_REQUIRED",
        )
    target = _collection(collection)
    existing = _rows(
        target,
        {"tenant_id": party.tenant_id, "party_id": party.party_id},
        session=tx,
        limit=2,
    )
    if len(existing) > 1:
        _raise(
            LegalMatterPartyRegistryPersistedRecordInvalidError,
            "L8_8B_DUPLICATE_PARTY_ID",
        )
    if existing:
        hydrated = _hydrate(existing[0])
        if hydrated.to_dict() == party.to_dict():
            return hydrated
        _raise(LegalMatterPartyRegistryConflictError)

    same_subject = _rows(
        target,
        {
            "tenant_id": party.tenant_id,
            "case_matter_id": party.case_matter_id,
            "subject_identity_fingerprint": party.subject_identity_fingerprint,
        },
        session=tx,
        limit=2,
    )
    if same_subject:
        hydrated = _hydrate(same_subject[0])
        if hydrated.to_dict() == party.to_dict():
            return hydrated
        _raise(
            LegalMatterPartyRegistryConflictError,
            "L8_8B_MATTER_SUBJECT_CONFLICT",
        )

    try:
        target.insert_one(_record(party), session=tx)
    except DuplicateKeyError as error:
        _raise(LegalMatterPartyRegistryRetryRequiredError, cause=error)
    except PyMongoError as error:
        _raise_mongo(error)

    persisted = get_party(
        party.tenant_id,
        party.party_id,
        target,
        session=tx,
    )
    if persisted.to_dict() != party.to_dict():
        _raise(
            LegalMatterPartyRegistryPersistedRecordInvalidError,
            "L8_8B_POST_WRITE_CORRELATION_INVALID",
        )
    return persisted


class LegalMatterPartyRegistry:
    ensure_indexes = staticmethod(ensure_indexes)
    get_party = staticmethod(get_party)
    list_matter_parties = staticmethod(list_matter_parties)
    find_subject_occurrences = staticmethod(find_subject_occurrences)
    persist_party = staticmethod(persist_party)


__all__ = [
    "COLLECTION",
    "MATTER_LOOKUP_INDEX_NAME",
    "MATTER_SUBJECT_INDEX_NAME",
    "MAX_MATTER_PARTIES",
    "MAX_SUBJECT_OCCURRENCES",
    "PARTY_ID_INDEX_NAME",
    "READ_CONCERN",
    "RECORD_SCHEMA",
    "SUBJECT_LOOKUP_INDEX_NAME",
    "VERSION",
    "WRITE_CONCERN",
    "LegalMatterPartyRegistry",
    "LegalMatterPartyRegistryConflictError",
    "LegalMatterPartyRegistryError",
    "LegalMatterPartyRegistryInputError",
    "LegalMatterPartyRegistryNotFoundError",
    "LegalMatterPartyRegistryPersistenceUnavailableError",
    "LegalMatterPartyRegistryPersistedRecordInvalidError",
    "LegalMatterPartyRegistryRetryRequiredError",
    "LegalMatterPartyRegistryTransactionRequiredError",
    "ensure_indexes",
    "find_subject_occurrences",
    "get_party",
    "list_matter_parties",
    "persist_party",
]


# ARTIFACT: legal_matter_party_registry.py
# VERSION: v1.0.0-L8-8B-LEGAL-MATTER-PARTY-REGISTRY
# AUTHORITY BOUNDARY: immutable matter-party persistence/read evidence only
# TENANT POSTURE: every lookup/write/index begins with exact tenant_id
# FAIL-CLOSED POSTURE: transaction absence, corruption, divergence, duplicates, overflow and persistence failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
