"""Wilsy OS durable tenant inbound provider-policy registry.

TITLE: Tenant Inbound Provider Policy Registry
VERSION: v1.1.0-M11-R8-R3B-P8-P3C-P2-R2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Tenant-scoped durable storage and exact replay for immutable inbound
         provider-policy facts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_inbound_provider_policy_registry.py
COLLABORATION / OWNERSHIP: SaaS persistence owner for the paired immutable
                            domain; callers own sessions and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.1.0-M11-R8-R3B-P8-P3C-P2-R2 adds the bounded tenant/policy
           predecessor read while preserving immutable persistence and replay.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references and fingerprints only; no raw
                             credentials, KMS calls, or provider transport.
TENANT BOUNDARY: Every identity lookup and uniqueness primitive includes tenant_id.
AUTHORITY BOUNDARY: Persistence and replay only; no authoring, activation,
                    currentness, binding, checkout, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
TRANSACTION BOUNDARY: The caller supplies an optional session and owns transaction,
                      commit, abort, and retry semantics.
FAIL-CLOSED DECLARATION: Corrupt documents, divergent replay, and persistence
                          failures reject without inference or repair.
"""
from __future__ import annotations

from typing import Any, Optional, Protocol, cast

from pymongo import ASCENDING
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.tenant_inbound_provider_policy import (
    TenantInboundProviderPolicy,
    TenantInboundProviderPolicyError,
)


VERSION = "v1.1.0-M11-R8-R3B-P8-P3C-P2-R2"
COLLECTION = "tenant_inbound_provider_policies"


class _CollectionLike(Protocol):
    """Structural collection surface shared by PyMongo and host-free fakes."""

    def create_index(self, keys: Any, **kwargs: Any) -> Any: ...
    def find_one(self, query: Any, **kwargs: Any) -> Any: ...
    def find(self, query: Any, **kwargs: Any) -> Any: ...
    def insert_one(self, document: Any, **kwargs: Any) -> Any: ...


class TenantInboundProviderPolicyRegistryError(RuntimeError):
    """Base fail-closed persistence error."""


class TenantInboundProviderPolicyNotFoundError(TenantInboundProviderPolicyRegistryError):
    """Exact tenant/policy/version identity is absent."""


class TenantInboundProviderPolicyPersistedRecordInvalidError(TenantInboundProviderPolicyRegistryError):
    """A durable document cannot be reconstructed as canonical policy evidence."""


class TenantInboundProviderPolicyReplayConflictError(TenantInboundProviderPolicyRegistryError):
    """An existing identity is bound to divergent immutable policy material."""


def _lookup_text(name: str, value: object) -> str:
    """Require an exact non-blank lookup component without normalization."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantInboundProviderPolicyRegistryError(f"M11R8_INVALID_LOOKUP_{name.upper()}")
    return value


def _lookup_version(value: object) -> int:
    """Require a positive, non-boolean policy version for an identity predicate."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise TenantInboundProviderPolicyRegistryError("M11R8_INVALID_LOOKUP_POLICY_VERSION")
    return value


def _lookup_predecessor_target_version(value: object) -> int:
    """Require a revision target strictly above the initial version."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 1:
        raise TenantInboundProviderPolicyRegistryError(
            "M11R8_INVALID_PREDECESSOR_TARGET_POLICY_VERSION"
        )
    return value


def _find_one(
    collection: _CollectionLike,
    query: dict[str, object],
    session: Optional[object],
) -> dict[str, object] | None:
    """Read one row while propagating the caller session exactly when supplied."""
    kwargs: dict[str, object] = {} if session is None else {"session": session}
    try:
        row = cast(Any, collection).find_one(query, **kwargs)
    except PyMongoError as error:
        raise TenantInboundProviderPolicyRegistryError("M11R8_POLICY_LOOKUP_FAILED") from error
    if row is None:
        return None
    if not isinstance(row, dict):
        raise TenantInboundProviderPolicyPersistedRecordInvalidError("M11R8_PERSISTED_RECORD_INVALID")
    return cast(dict[str, object], row)


def _find_predecessor(
    collection: _CollectionLike,
    query: dict[str, object],
    session: Optional[object],
) -> dict[str, object] | None:
    """Read the deterministic highest lower version with caller session scope."""
    kwargs: dict[str, object] = {} if session is None else {"session": session}
    try:
        cursor = cast(Any, collection).find(query, **kwargs)
        ordered = cursor.sort([("policy_version", -1)])
        limited = ordered.limit(1)
        rows = list(limited)
    except PyMongoError as error:
        raise TenantInboundProviderPolicyRegistryError(
            "M11R8_PREDECESSOR_LOOKUP_FAILED"
        ) from error
    except Exception as error:
        raise TenantInboundProviderPolicyRegistryError(
            "M11R8_PREDECESSOR_LOOKUP_FAILED"
        ) from error
    if not rows:
        return None
    row = rows[0]
    if not isinstance(row, dict):
        raise TenantInboundProviderPolicyPersistedRecordInvalidError(
            "M11R8_PERSISTED_RECORD_INVALID"
        )
    return cast(dict[str, object], row)


def _hydrate(document: dict[str, object]) -> TenantInboundProviderPolicy:
    """Strictly hydrate one row, removing only Mongo's transport ``_id`` field."""
    body = dict(document)
    body.pop("_id", None)
    try:
        return TenantInboundProviderPolicy.from_dict(body)
    except (TenantInboundProviderPolicyError, KeyError, TypeError, ValueError) as error:
        raise TenantInboundProviderPolicyPersistedRecordInvalidError(
            "M11R8_PERSISTED_RECORD_INVALID"
        ) from error


class TenantInboundProviderPolicyRegistry:
    """Persist immutable policy facts without issuing authority or owning transactions."""

    @staticmethod
    def ensure_indexes(collection: _CollectionLike) -> None:
        """Create the sole tenant/policy/version uniqueness primitive."""
        collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("provider_policy_id", ASCENDING),
                ("policy_version", ASCENDING),
            ],
            unique=True,
            name="tenant_inbound_provider_policy_identity_unique",
        )

    @staticmethod
    def create(
        policy: TenantInboundProviderPolicy,
        collection: _CollectionLike,
        *,
        session: Optional[object] = None,
    ) -> TenantInboundProviderPolicy:
        """Insert once or return an exact durable replay.

        Identity is read before insert. Equal immutable material returns the
        canonical hydrated row without writing; divergent material fails closed.
        DuplicateKeyError is deliberately propagated so the caller can restart
        the complete transaction and retry with fresh state.
        """
        if not isinstance(policy, TenantInboundProviderPolicy):
            raise TenantInboundProviderPolicyReplayConflictError("M11R8_INVALID_PROVIDER_POLICY")
        identity = {
            "tenant_id": policy.tenant_id,
            "provider_policy_id": policy.provider_policy_id,
            "policy_version": policy.policy_version,
        }
        existing = _find_one(collection, identity, session)
        if existing is not None:
            canonical = _hydrate(existing)
            if canonical == policy:
                return canonical
            raise TenantInboundProviderPolicyReplayConflictError("M11R8_DIVERGENT_PROVIDER_POLICY_REPLAY")
        kwargs: dict[str, object] = {} if session is None else {"session": session}
        try:
            cast(Any, collection).insert_one(policy.to_persisted(), **kwargs)
        except DuplicateKeyError:
            raise
        except PyMongoError as error:
            raise TenantInboundProviderPolicyRegistryError("M11R8_POLICY_PERSIST_FAILED") from error
        return policy

    @staticmethod
    def get(
        tenant_id: str,
        provider_policy_id: str,
        policy_version: int,
        collection: _CollectionLike,
        *,
        session: Optional[object] = None,
    ) -> TenantInboundProviderPolicy:
        """Read and strictly hydrate one exact tenant/policy/version identity."""
        query = {
            "tenant_id": _lookup_text("tenant_id", tenant_id),
            "provider_policy_id": _lookup_text("provider_policy_id", provider_policy_id),
            "policy_version": _lookup_version(policy_version),
        }
        row = _find_one(collection, query, session)
        if row is None:
            raise TenantInboundProviderPolicyNotFoundError("M11R8_PROVIDER_POLICY_NOT_FOUND")
        return _hydrate(row)

    @staticmethod
    def get_predecessor_policy(
        tenant_id: str,
        provider_policy_id: str,
        target_policy_version: int,
        collection: _CollectionLike,
        *,
        session: Optional[object] = None,
    ) -> TenantInboundProviderPolicy | None:
        """Return the highest strict predecessor for one tenant/policy identity.

        The read is deliberately narrower than a current or active-policy lookup:
        it queries only the same tenant and policy ID with ``policy_version <``
        the requested target, orders descending, limits to one row, and strictly
        hydrates that row.  A corrupt highest predecessor fails closed instead of
        falling back to an older immutable fact.  This method performs no
        authorization, currentness, activation, or transaction ownership work.
        """
        query = {
            "tenant_id": _lookup_text("tenant_id", tenant_id),
            "provider_policy_id": _lookup_text("provider_policy_id", provider_policy_id),
            "policy_version": {
                "$lt": _lookup_predecessor_target_version(target_policy_version)
            },
        }
        row = _find_predecessor(collection, query, session)
        if row is None:
            return None
        return _hydrate(row)


# ARTIFACT: tenant_inbound_provider_policy_registry.py
# VERSION: v1.1.0-M11-R8-R3B-P8-P3C-P2-R2
# AUTHORITY BOUNDARY: tenant-scoped immutable policy persistence and exact replay only.
# TENANT POSTURE: tenant_id participates in every read and the identity uniqueness index.
# FAIL-CLOSED POSTURE: strict hydration, divergent replay rejection, and raw race propagation.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
