"""WILSY P9-R105-P4G-P4-R2B append-only ethical-wall restriction registry.

Documentary immutable restriction persistence only. No lifting, waiver,
clearance, issuer permission, operational access or financial authority.
"""
from __future__ import annotations

from typing import Any, Final, Mapping

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_practitioner_ethical_wall_restriction import (
    LegalPractitionerEthicalWallRestriction as Restriction,
)

VERSION: Final[str] = "v1.0.0-P9-R105-P4G-P4-R2B"
IDENTITY_INDEX: Final[str] = "p9_wall_tenant_restriction_identity_unique"
FINGERPRINT_INDEX: Final[str] = "p9_wall_tenant_fingerprint_unique"
SCOPE_INDEX: Final[str] = "p9_wall_tenant_matter_practitioner_history"
MAX_HISTORY_READS: Final[int] = 500


class EthicalWallRegistryError(RuntimeError):
    pass


class EthicalWallTransactionRequired(EthicalWallRegistryError):
    pass


class EthicalWallConflict(EthicalWallRegistryError):
    pass


class EthicalWallPersistedInvalid(EthicalWallRegistryError):
    pass


class EthicalWallPersistenceUnavailable(EthicalWallRegistryError):
    pass


class EthicalWallHistoryIncomplete(EthicalWallRegistryError):
    pass


def _transaction(session: Any) -> None:
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise EthicalWallTransactionRequired("P9_WALL_ACTIVE_TRANSACTION_REQUIRED")


def _id(value: object) -> str:
    if (
        type(value) is not str or not value or len(value) > 200
        or value != value.strip()
        or any(ord(c) < 32 or ord(c) == 127 for c in value)
    ):
        raise EthicalWallRegistryError("P9_WALL_REGISTRY_IDENTITY_INVALID")
    return value


def _hydrate(record: Mapping[str, object]) -> Restriction:
    if not isinstance(record, Mapping):
        raise EthicalWallPersistedInvalid("P9_WALL_PERSISTED_SHAPE_INVALID")
    raw = dict(record)
    raw.pop("_id", None)
    try:
        item = Restriction.from_dict(raw)
    except (ValueError, TypeError, KeyError) as exc:
        raise EthicalWallPersistedInvalid(
            "P9_WALL_PERSISTED_INTEGRITY_INVALID"
        ) from exc
    if item.to_dict() != raw:
        raise EthicalWallPersistedInvalid("P9_WALL_PERSISTED_NONCANONICAL")
    return item


def ensure_indexes(collection: Any) -> None:
    collection.create_index(
        [("tenant_id", ASCENDING), ("restriction_id", ASCENDING)],
        name=IDENTITY_INDEX, unique=True,
    )
    collection.create_index(
        [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
        name=FINGERPRINT_INDEX, unique=True,
    )
    collection.create_index(
        [("tenant_id", ASCENDING), ("case_matter_id", ASCENDING),
         ("restricted_practitioner_principal_id", ASCENDING),
         ("effective_from", ASCENDING)],
        name=SCOPE_INDEX,
    )


def get_by_id(
    *, tenant_id: str, restriction_id: str,
    collection: Any, session: Any,
) -> Restriction | None:
    _transaction(session)
    tenant = _id(tenant_id)
    identity = _id(restriction_id)
    try:
        record = collection.find_one(
            {"tenant_id": tenant, "restriction_id": identity},
            session=session,
        )
    except Exception as exc:
        raise EthicalWallPersistenceUnavailable(
            "P9_WALL_LOOKUP_UNAVAILABLE"
        ) from exc
    if record is None:
        return None
    item = _hydrate(record)
    if item.tenant_id != tenant or item.restriction_id != identity:
        raise EthicalWallPersistedInvalid("P9_WALL_LOOKUP_IDENTITY_MISMATCH")
    return item


def append_restriction(
    *, restriction: Restriction, collection: Any, session: Any,
) -> Restriction:
    _transaction(session)
    if not isinstance(restriction, Restriction):
        raise EthicalWallRegistryError("P9_WALL_RESTRICTION_TYPE_INVALID")
    try:
        canonical = Restriction.from_dict(restriction.to_dict())
    except (ValueError, TypeError, KeyError) as exc:
        raise EthicalWallRegistryError(
            "P9_WALL_RESTRICTION_INVALID"
        ) from exc
    if canonical != restriction:
        raise EthicalWallRegistryError("P9_WALL_RESTRICTION_DIVERGENT")
    existing = get_by_id(
        tenant_id=restriction.tenant_id,
        restriction_id=restriction.restriction_id,
        collection=collection, session=session,
    )
    if existing is not None:
        if existing == restriction:
            return existing
        raise EthicalWallConflict("P9_WALL_DIVERGENT_REPLAY")
    try:
        collection.insert_one(dict(canonical.to_dict()), session=session)
    except DuplicateKeyError as exc:
        raise EthicalWallConflict(
            "P9_WALL_UNIQUE_COLLISION_RETRY_REQUIRED"
        ) from exc
    except Exception as exc:
        raise EthicalWallPersistenceUnavailable(
            "P9_WALL_INSERT_UNAVAILABLE"
        ) from exc
    return canonical


def list_restrictions_for_scope(
    *, tenant_id: str, case_matter_id: str,
    restricted_practitioner_principal_id: str,
    collection: Any, session: Any,
) -> tuple[Restriction, ...]:
    _transaction(session)
    query = {
        "tenant_id": _id(tenant_id),
        "case_matter_id": _id(case_matter_id),
        "restricted_practitioner_principal_id":
            _id(restricted_practitioner_principal_id),
    }
    try:
        # MAX+1 detects truncation; a truncated history cannot be interpreted
        # as proof that no active restriction exists.
        cursor = collection.find(query, session=session)
        records = tuple(cursor.limit(MAX_HISTORY_READS + 1))
    except Exception as exc:
        raise EthicalWallPersistenceUnavailable(
            "P9_WALL_HISTORY_UNAVAILABLE"
        ) from exc
    if len(records) > MAX_HISTORY_READS:
        raise EthicalWallHistoryIncomplete("P9_WALL_HISTORY_TOO_LARGE")
    result: list[Restriction] = []
    identities: dict[str, Restriction] = {}
    for record in records:
        item = _hydrate(record)
        if any(item.to_dict()[name] != value for name, value in query.items()):
            raise EthicalWallPersistedInvalid("P9_WALL_HISTORY_SCOPE_MISMATCH")
        prior = identities.get(item.restriction_id)
        if prior is not None:
            if prior != item:
                raise EthicalWallPersistedInvalid(
                    "P9_WALL_HISTORY_IDENTITY_DIVERGENT"
                )
            raise EthicalWallPersistedInvalid(
                "P9_WALL_HISTORY_DUPLICATE_ROW"
            )
        identities[item.restriction_id] = item
        result.append(item)
    return tuple(sorted(result, key=lambda x: (
        x.effective_from, x.restriction_id, x.fingerprint,
    )))


__all__ = (
    "VERSION", "IDENTITY_INDEX", "FINGERPRINT_INDEX", "SCOPE_INDEX",
    "MAX_HISTORY_READS",
    "EthicalWallRegistryError", "EthicalWallTransactionRequired",
    "EthicalWallConflict", "EthicalWallPersistedInvalid",
    "EthicalWallPersistenceUnavailable", "EthicalWallHistoryIncomplete",
    "ensure_indexes", "get_by_id", "append_restriction",
    "list_restrictions_for_scope",
)

# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P4-R2B
# APPEND ONLY. WAIVER / LIFT / ACCESS GRANT / FINANCE: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
