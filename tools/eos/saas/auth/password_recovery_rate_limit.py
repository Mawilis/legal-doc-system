"""Durable request-density gate for WILSY OS password recovery.

TITLE: WILSY OS Password Recovery Rate Limit Gate
VERSION: v1.1.0-R10E18-NAMESPACED-RECOVERY-RATE-LIMIT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Applies one deterministic tenant/address-digest fixed-window request
         limit before password-recovery contact lookup or issuance.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/password_recovery_rate_limit.py
COLLABORATION / OWNERSHIP: R10E3 invokes this gate equally for existent and
                           absent contacts. Mongo provides atomic counter
                           capability only; it does not become recovery authority.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.1.0-R10E18-NAMESPACED-RECOVERY-RATE-LIMIT adds a validated namespace to bucket identity and
           persisted/query metadata so anonymous reset requests and authenticated
           recovery-contact verification maintain independent security budgets.
           v1.0.0-R10E6-PASSWORD-RECOVERY-RATE-LIMIT introduces deterministic
           15-minute buckets, five-request default admission, SHA3-512 bucket
           identities, atomic upsert/increment, TTL cleanup metadata, stable
           rate-limit rejection, and fail-closed persistence errors.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No raw email, token, password, principal identity,
                            or recovery capability is accepted or stored.
TENANT BOUNDARY: Counter identity includes exact tenant_id and address digest.
AUTHORITY BOUNDARY: Request-density capability only; no account existence,
                    contact verification, recovery issuance, password, delivery,
                    session, JWT, or MFA authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Each admission is one atomic Mongo find/update; no caller
                      transaction is required or created.
FAIL-CLOSED POSTURE: Mongo/index/state corruption rejects rather than bypassing
                     recovery throttling.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Final

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import PyMongoError

from .password_recovery_request_service import (
    PasswordRecoveryRequestDependencyError,
    PasswordRecoveryRequestRateLimitedError,
)

VERSION: Final[str] = "v1.1.0-R10E18-NAMESPACED-RECOVERY-RATE-LIMIT"
COLLECTION: Final[str] = "password_recovery_request_limits"
DEFAULT_WINDOW: Final[timedelta] = timedelta(minutes=15)
DEFAULT_MAX_REQUESTS: Final[int] = 5
DEFAULT_NAMESPACE: Final[str] = "password-reset"


def _target(collection: Any | None) -> Any:
    """Resolve injected collection or canonical Kernel database lazily."""

    if collection is not None:
        return collection
    from tools.eos.kernel import db as kernel_db

    database = kernel_db.get_database()
    if database is None:
        raise PasswordRecoveryRequestDependencyError("RECOVERY_RATE_DATABASE_UNAVAILABLE")
    return database[COLLECTION]


def _utc(value: object) -> datetime:
    """Require one timezone-aware UTC timestamp."""

    if not isinstance(value, datetime):
        raise PasswordRecoveryRequestDependencyError("RECOVERY_RATE_TIME_INVALID")
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise PasswordRecoveryRequestDependencyError("RECOVERY_RATE_TIME_INVALID")
    return value


def _validated_tenant(value: object) -> str:
    """Validate exact tenant identity without alias inference."""

    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 256:
        raise PasswordRecoveryRequestDependencyError("RECOVERY_RATE_TENANT_INVALID")
    return value


def _validated_digest(value: object) -> str:
    """Validate one lowercase SHA3-512 contact digest."""

    if not isinstance(value, str) or len(value) != 128 or value != value.lower():
        raise PasswordRecoveryRequestDependencyError("RECOVERY_RATE_DIGEST_INVALID")
    try:
        if len(bytes.fromhex(value)) != 64:
            raise ValueError
    except ValueError as error:
        raise PasswordRecoveryRequestDependencyError("RECOVERY_RATE_DIGEST_INVALID") from error
    return value


def _window_start(observed_at: datetime, window: timedelta) -> datetime:
    """Floor one UTC observation to a deterministic fixed-window boundary."""

    seconds = int(window.total_seconds())
    epoch_seconds = int(observed_at.timestamp())
    floored = epoch_seconds - (epoch_seconds % seconds)
    return datetime.fromtimestamp(floored, tz=timezone.utc)


def _namespace(value: object) -> str:
    """Validate one bounded rate-policy namespace."""

    if not isinstance(value, str):
        raise PasswordRecoveryRequestDependencyError("RECOVERY_RATE_NAMESPACE_INVALID")
    normalized = value.strip()
    if (
        not normalized
        or normalized != value
        or len(normalized) > 64
        or any(not (character.isalnum() or character in {"-", "_"}) for character in normalized)
    ):
        raise PasswordRecoveryRequestDependencyError("RECOVERY_RATE_NAMESPACE_INVALID")
    return normalized


def _bucket_id(
    namespace: str,
    tenant_id: str,
    address_digest: str,
    bucket_start: datetime,
) -> str:
    """Derive opaque deterministic bucket identity without raw address material."""

    canonical = f"{namespace}|{tenant_id}|{address_digest}|{bucket_start.isoformat()}"
    return hashlib.sha3_512(canonical.encode("utf-8")).hexdigest()


class PasswordRecoveryRateLimit:
    """Mongo-backed R10E3 request-density gate.

    The gate has no account lookup and therefore applies identical persistence
    work to existent and absent addresses. A deterministic bucket _id makes
    concurrent upsert atomic without duplicate-window ambiguity.
    """

    def __init__(
        self,
        collection: Any | None = None,
        *,
        window: timedelta = DEFAULT_WINDOW,
        max_requests: int = DEFAULT_MAX_REQUESTS,
        namespace: str = DEFAULT_NAMESPACE,
    ) -> None:
        """Bind one collection, bounded fixed-window policy, and security namespace."""

        if (
            not isinstance(window, timedelta)
            or window < timedelta(minutes=1)
            or window > timedelta(hours=24)
        ):
            raise PasswordRecoveryRequestDependencyError("RECOVERY_RATE_WINDOW_INVALID")
        if isinstance(max_requests, bool) or not isinstance(max_requests, int) or not 1 <= max_requests <= 100:
            raise PasswordRecoveryRequestDependencyError("RECOVERY_RATE_LIMIT_INVALID")
        self._collection = collection
        self._window = window
        self._max_requests = max_requests
        self._namespace = _namespace(namespace)

    def _source(self) -> Any:
        """Return configured or canonical rate-limit collection."""

        return _target(self._collection)

    def ensure_indexes(self) -> None:
        """Create query and TTL cleanup indexes outside request execution."""

        source = self._source()
        try:
            source.create_index(
                [("namespace", ASCENDING), ("tenant_id", ASCENDING), ("address_digest", ASCENDING), ("bucket_start", ASCENDING)],
                unique=False,
                name="password_recovery_rate_lookup",
            )
            source.create_index(
                [("expires_at", ASCENDING)],
                expireAfterSeconds=0,
                name="password_recovery_rate_ttl",
            )
        except PyMongoError as error:
            raise PasswordRecoveryRequestDependencyError(
                "RECOVERY_RATE_INDEX_CREATION_FAILED"
            ) from error

    def require_allowed(
        self,
        *,
        tenant_id: str,
        address_digest: str,
        observed_at: datetime,
    ) -> None:
        """Atomically consume one recovery-request allowance.

        The counter is incremented before admission is decided, so blocked
        attempts remain durable evidence for the current window. Exceeding the
        configured limit raises the same error regardless of account existence.
        """

        tenant = _validated_tenant(tenant_id)
        digest = _validated_digest(address_digest)
        observed = _utc(observed_at)
        start = _window_start(observed, self._window)
        expires_at = start + self._window + timedelta(minutes=1)
        bucket_id = _bucket_id(self._namespace, tenant, digest, start)

        try:
            row = self._source().find_one_and_update(
                {"_id": bucket_id},
                {
                    "$setOnInsert": {
                        "namespace": self._namespace,
                        "tenant_id": tenant,
                        "address_digest": digest,
                        "bucket_start": start,
                        "expires_at": expires_at,
                    },
                    "$inc": {"count": 1},
                },
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        except PyMongoError as error:
            raise PasswordRecoveryRequestDependencyError(
                "RECOVERY_RATE_WRITE_FAILED"
            ) from error

        if not isinstance(row, dict):
            raise PasswordRecoveryRequestDependencyError("RECOVERY_RATE_STATE_INVALID")
        if (
            row.get("namespace") != self._namespace
            or row.get("tenant_id") != tenant
            or row.get("address_digest") != digest
            or row.get("bucket_start") != start
        ):
            raise PasswordRecoveryRequestDependencyError("RECOVERY_RATE_STATE_MISMATCH")
        count = row.get("count")
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise PasswordRecoveryRequestDependencyError("RECOVERY_RATE_STATE_INVALID")
        if count > self._max_requests:
            raise PasswordRecoveryRequestRateLimitedError("RECOVERY_REQUEST_RATE_LIMITED")


__all__ = [
    "COLLECTION",
    "DEFAULT_MAX_REQUESTS",
    "DEFAULT_NAMESPACE",
    "DEFAULT_WINDOW",
    "PasswordRecoveryRateLimit",
    "VERSION",
]


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: password_recovery_rate_limit.py
# VERSION: v1.1.0-R10E18-NAMESPACED-RECOVERY-RATE-LIMIT
# AUTHORITY BOUNDARY: durable request-density capability only
# TENANT POSTURE: namespace + exact tenant/address-digest bucket identity
# FAIL-CLOSED POSTURE: persistence/state failure never bypasses throttling
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
