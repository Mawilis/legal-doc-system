"""Sovereign durable Mongo registry for WILSY OS CRM Lead truth.

TITLE: WILSY OS CRM Lead Durable Registry
VERSION: v1.0.0-CRM-LEAD-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME:
    Persists exact immutable tenant-bound CRM Lead truth with deterministic
    indexes, caller-owned Mongo sessions, tenant-local idempotent creation,
    strict corruption-rejecting hydration, and no business-orchestration or
    financial execution authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/crm/persistence/crm_lead_registry.py
COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy OS Core Engineering
CERTIFICATION / UPDATE DATE:
    2026-10-06
CHANGELOG:
    v1.0.0-CRM-LEAD-REGISTRY introduces durable tenant-scoped Lead persistence,
    deterministic indexes, SHA3-512 command fingerprints, exact replay,
    caller-session forwarding, strict domain hydration and fail-closed reads.
COMPLIANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
SECURITY / PRIVACY POSTURE:
    Persists only canonical CRM Lead truth plus registry idempotency evidence.
    No secrets, authentication tokens, payment credentials or provider keys.
TENANT BOUNDARY:
    Every identity and idempotency read is exact tenant-scoped. Blank, padded,
    MASTER, global and sovereign-root aliases fail closed.
TRANSACTION BOUNDARY:
    Caller owns ClientSession and transaction lifecycle. This registry never
    starts, commits or aborts a transaction.
AUTHORITY BOUNDARY:
    Durable CRM Lead persistence only. Roles, permissions, subscription
    entitlements, quotas, lifecycle orchestration, enrichment, scoring models,
    campaigns, AI decisions, account conversion and transport are separate.
FINANCIAL AUTHORITY BOUNDARY:
    No quote, invoice, payment, settlement, revenue or accounting execution.
    Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any, Final

from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.crm.domain.crm_lead import CrmLead, CrmLeadDomainError


CRM_LEAD_REGISTRY_VERSION: Final[str] = "v1.0.0-CRM-LEAD-REGISTRY"
COLLECTION: Final[str] = "crm_leads"

WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)
READ_CONCERN: Final[ReadConcern] = ReadConcern("majority")

_FORBIDDEN_TENANT_IDENTITIES: Final[frozenset[str]] = frozenset(
    {
        "MASTER",
        "GLOBAL_ROOT",
        "SOVEREIGN_ROOT",
        "WILSY-SOVEREIGN-ROOT",
    }
)

_LEAD_FIELDS: Final[tuple[str, ...]] = (
    "lead_id",
    "tenant_id",
    "full_name",
    "company_name",
    "email",
    "phone",
    "mobile",
    "status",
    "owner_id",
    "source_channel",
    "priority",
    "consent_basis",
    "score",
    "industry",
    "due_at",
    "notes",
    "created_at",
    "updated_at",
)


class CrmLeadRegistryError(RuntimeError):
    """Base failure for durable CRM Lead persistence."""


class CrmLeadRegistryConflictError(CrmLeadRegistryError):
    """Reject divergent replay, duplicate identity or competing persistence."""


class CrmLeadRegistryNotFoundError(CrmLeadRegistryError):
    """Exact tenant-scoped Lead identity is absent."""


def _target(collection: Any) -> Any:
    """Bind majority durability concerns while retaining testable collection seams."""

    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
        )
    except AttributeError:
        return collection


def _exact_text(value: object, code: str) -> str:
    """Require one non-empty unpadded exact textual identifier."""

    if not isinstance(value, str):
        raise CrmLeadRegistryError(code)

    if not value or not value.strip() or value != value.strip():
        raise CrmLeadRegistryError(code)

    return value


def _tenant_id(value: object) -> str:
    """Require exact tenant scope and reject global/default aliases."""

    tenant = _exact_text(value, "CRM_LEAD_REGISTRY_TENANT_ID_INVALID")

    if tenant.upper() in _FORBIDDEN_TENANT_IDENTITIES:
        raise CrmLeadRegistryError("CRM_LEAD_REGISTRY_TENANT_ID_INVALID")

    return tenant


def _session(value: object) -> object:
    """Require caller-owned Mongo session without owning transaction lifecycle."""

    if value is None:
        raise CrmLeadRegistryError("CRM_LEAD_REGISTRY_SESSION_REQUIRED")

    return value


def _idempotency_key(value: object) -> str:
    """Require exact caller-owned idempotency key."""

    return _exact_text(
        value,
        "CRM_LEAD_REGISTRY_IDEMPOTENCY_KEY_INVALID",
    )


def _command_fingerprint(lead: CrmLead, key: str) -> str:
    """Return deterministic SHA3-512 fingerprint for one create command."""

    material = {
        "tenant_id": lead.tenant_id,
        "idempotency_key": key,
        "lead": lead.to_dict(),
    }

    encoded = json.dumps(
        material,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha3_512(encoded).hexdigest()


def _hydrate(document: Mapping[str, object]) -> CrmLead:
    """Project only canonical Lead truth and reject durable corruption."""

    try:
        projected = {field: document[field] for field in _LEAD_FIELDS}
        return CrmLead.from_dict(projected)
    except (KeyError, TypeError, CrmLeadDomainError) as error:
        raise CrmLeadRegistryError(
            "CRM_LEAD_REGISTRY_CORRUPT_DOCUMENT"
        ) from error


def ensure_indexes(collection: Any) -> None:
    """Create deterministic tenant-scoped indexes; never create TTL indexes."""

    if collection is None:
        raise CrmLeadRegistryError(
            "CRM_LEAD_REGISTRY_COLLECTION_REQUIRED"
        )

    target = _target(collection)

    try:
        target.create_index(
            [("tenant_id", 1), ("lead_id", 1)],
            unique=True,
            name="crm_lead_tenant_identity_unique",
        )
        target.create_index(
            [("tenant_id", 1), ("idempotency_key", 1)],
            unique=True,
            name="crm_lead_tenant_idempotency_unique",
        )
        target.create_index(
            [("tenant_id", 1), ("status", 1), ("updated_at", -1)],
            unique=False,
            name="crm_lead_tenant_status_updated_at",
        )
        target.create_index(
            [("tenant_id", 1), ("owner_id", 1), ("updated_at", -1)],
            unique=False,
            name="crm_lead_tenant_owner_updated_at",
        )
    except PyMongoError as error:
        raise CrmLeadRegistryError(
            "CRM_LEAD_REGISTRY_PERSISTENCE_UNAVAILABLE"
        ) from error


class CrmLeadRegistry:
    """Caller-session durable registry for canonical tenant-scoped Lead truth."""

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        """Bind one Mongo collection without starting any transaction."""

        if collection is None:
            raise CrmLeadRegistryError(
                "CRM_LEAD_REGISTRY_COLLECTION_REQUIRED"
            )

        self._collection = _target(collection)

    def create_or_replay(
        self,
        lead: CrmLead,
        *,
        idempotency_key: str,
        session: Any,
    ) -> CrmLead:
        """Insert once or return exact tenant-local durable replay.

        The caller owns the supplied session and transaction lifecycle.
        Divergent reuse of the same tenant/idempotency coordinate fails closed.
        Duplicate Lead identity under another idempotency coordinate also fails
        closed rather than mutating existing durable truth.
        """

        if not isinstance(lead, CrmLead):
            raise CrmLeadRegistryError(
                "CRM_LEAD_REGISTRY_LEAD_REQUIRED"
            )

        key = _idempotency_key(idempotency_key)
        caller_session = _session(session)

        fingerprint = _command_fingerprint(lead, key)

        replay_query = {
            "tenant_id": lead.tenant_id,
            "idempotency_key": key,
        }

        try:
            existing = self._collection.find_one(
                replay_query,
                session=caller_session,
            )
        except PyMongoError as error:
            raise CrmLeadRegistryError(
                "CRM_LEAD_REGISTRY_PERSISTENCE_UNAVAILABLE"
            ) from error

        if existing is not None:
            if existing.get("command_fingerprint") != fingerprint:
                raise CrmLeadRegistryConflictError(
                    "CRM_LEAD_REGISTRY_DIVERGENT_IDEMPOTENCY"
                )

            return _hydrate(existing)

        document = lead.to_dict()
        document.update(
            {
                "idempotency_key": key,
                "command_fingerprint": fingerprint,
            }
        )

        try:
            self._collection.insert_one(
                document,
                session=caller_session,
            )
        except DuplicateKeyError as error:
            try:
                raced = self._collection.find_one(
                    replay_query,
                    session=caller_session,
                )
            except PyMongoError as read_error:
                raise CrmLeadRegistryError(
                    "CRM_LEAD_REGISTRY_PERSISTENCE_UNAVAILABLE"
                ) from read_error

            if (
                raced is not None
                and raced.get("command_fingerprint") == fingerprint
            ):
                return _hydrate(raced)

            if raced is not None:
                raise CrmLeadRegistryConflictError(
                    "CRM_LEAD_REGISTRY_DIVERGENT_IDEMPOTENCY"
                ) from error

            raise CrmLeadRegistryConflictError(
                "CRM_LEAD_REGISTRY_DUPLICATE_IDENTITY"
            ) from error
        except PyMongoError as error:
            raise CrmLeadRegistryError(
                "CRM_LEAD_REGISTRY_PERSISTENCE_UNAVAILABLE"
            ) from error

        return lead

    def get(
        self,
        *,
        tenant_id: str,
        lead_id: str,
        session: Any,
    ) -> CrmLead:
        """Hydrate one exact tenant-scoped Lead; cross-tenant reads are absent."""

        tenant = _tenant_id(tenant_id)
        identity = _exact_text(
            lead_id,
            "CRM_LEAD_REGISTRY_LEAD_ID_INVALID",
        )
        caller_session = _session(session)

        try:
            row = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "lead_id": identity,
                },
                session=caller_session,
            )
        except PyMongoError as error:
            raise CrmLeadRegistryError(
                "CRM_LEAD_REGISTRY_PERSISTENCE_UNAVAILABLE"
            ) from error

        if row is None:
            raise CrmLeadRegistryNotFoundError(
                "CRM_LEAD_REGISTRY_NOT_FOUND"
            )

        return _hydrate(row)


__all__ = [
    "COLLECTION",
    "CRM_LEAD_REGISTRY_VERSION",
    "READ_CONCERN",
    "WRITE_CONCERN",
    "CrmLeadRegistry",
    "CrmLeadRegistryConflictError",
    "CrmLeadRegistryError",
    "CrmLeadRegistryNotFoundError",
    "ensure_indexes",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: crm_lead_registry.py
# VERSION: v1.0.0-CRM-LEAD-REGISTRY
# AUTHORITY BOUNDARY: durable tenant-scoped CRM Lead persistence only
# TENANT POSTURE: exact tenant scope; no MASTER/global/root/default fallback
# TRANSACTION POSTURE: caller owns session and transaction lifecycle
# REPLAY POSTURE: SHA3-512 exact tenant-local idempotency evidence
# TTL POSTURE: no TTL deletion index
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
# =============================================================================
