"""Durable pre-tenant request-density gate for Legal Storefront public intent.

TITLE: Legal Storefront Public Intent Rate Limit Gate
VERSION: v1.0.0-L8-9C0-LEGAL-STOREFRONT-PUBLIC-INTENT-RATE-LIMIT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Apply one durable fixed-window abuse-control budget to opaque
         pre-tenant Storefront request subjects without persisting raw email,
         IP address, tenant identity, credentials, Legal lifecycle or commerce
         authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_storefront_public_intent_rate_limit.py
COLLABORATION / OWNERSHIP: L8-9C0 owns request-density capability only.
                            L8-9A owns immutable Storefront intent semantics;
                            L8-9B owns durable public-intent persistence; a later
                            HTTP admission adapter owns request derivation and
                            transport. Mongo provides atomic counter capability
                            only and does not become Storefront authority.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-9C0-LEGAL-STOREFRONT-PUBLIC-INTENT-RATE-LIMIT
           establishes deterministic fifteen-minute pre-tenant rate buckets,
           five-request default admission, SHA3-512 opaque subject identity,
           atomic upsert/increment, TTL cleanup metadata, strict persisted-state
           validation and fail-closed Mongo dependency behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Accepts and persists only a lowercase SHA3-512
                             subject digest. Raw email, IP address, hostname,
                             credential, cookie, token and principal identity
                             are neither accepted nor persisted.
TENANT BOUNDARY: Pre-tenant by definition. No tenant_id is accepted, persisted,
                 queried, inferred or created by this capability.
AUTHORITY BOUNDARY: Request-density capability only. Admission allowance is not
                    Storefront intent acceptance, identity verification, user
                    creation, tenant genesis, membership, role, subscription,
                    entitlement or Legal Operations admission.
TRANSACTION BOUNDARY: Each rate admission is one atomic Mongo find/update.
                      No caller transaction is required or created.
RETENTION BOUNDARY: TTL applies only to ephemeral abuse-control buckets and does
                    not delete or govern durable Storefront intent evidence.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority.
FAIL-CLOSED DECLARATION: Mongo/index failure, invalid digest/time/configuration,
                         malformed persisted state or bucket mismatch rejects;
                         dependency failure never bypasses throttling.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Final, NoReturn

from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import PyMongoError


VERSION: Final[str] = (
    "v1.0.0-L8-9C0-LEGAL-STOREFRONT-PUBLIC-INTENT-RATE-LIMIT"
)
COLLECTION: Final[str] = "legal_storefront_public_intent_rate_limits"

DEFAULT_WINDOW: Final[timedelta] = timedelta(minutes=15)
DEFAULT_MAX_REQUESTS: Final[int] = 5
DEFAULT_NAMESPACE: Final[str] = "legal-storefront-public-intent"

INDEX_LOOKUP: Final[str] = (
    "legal_storefront_public_intent_rate_lookup"
)
INDEX_TTL: Final[str] = (
    "legal_storefront_public_intent_rate_ttl"
)


class LegalStorefrontPublicIntentRateLimitError(RuntimeError):
    """Base stable code-only L8-9C0 rate-limit failure.

    This error conveys request-density capability state only and grants no
    identity, tenant, Storefront admission, Legal lifecycle, commercial,
    retention or financial authority.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalStorefrontPublicIntentRateLimitedError(
    LegalStorefrontPublicIntentRateLimitError
):
    """The durable request-density budget rejected this public request."""


class LegalStorefrontPublicIntentRateLimitDependencyError(
    LegalStorefrontPublicIntentRateLimitError
):
    """Mongo or persisted rate-limit state failed closed."""


def _fail(code: str) -> NoReturn:
    """Raise one bounded L8-9C0 validation failure."""
    raise LegalStorefrontPublicIntentRateLimitError(code)


def _target(collection: Any) -> Any:
    """Require an injected Mongo collection without opening infrastructure."""
    if collection is None:
        _fail("L8_9C0_COLLECTION_REQUIRED")
    return collection


def _utc(value: object) -> datetime:
    """Require one explicit timezone-aware UTC observation timestamp."""
    if not isinstance(value, datetime):
        _fail("L8_9C0_TIME_INVALID")
    if (
        value.tzinfo is None
        or value.utcoffset() != timezone.utc.utcoffset(value)
    ):
        _fail("L8_9C0_TIME_INVALID")
    return value.astimezone(timezone.utc)


def _persisted_utc(value: object) -> datetime:
    """Normalize only valid BSON UTC datetime representations.

    PyMongo commonly decodes BSON UTC datetimes as naive values unless a
    timezone-aware codec is configured. Only that documented naive form is
    interpreted as UTC; malformed or non-UTC-aware state fails closed.
    """
    if not isinstance(value, datetime):
        raise LegalStorefrontPublicIntentRateLimitDependencyError(
            "L8_9C0_STATE_INVALID"
        )
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    if value.utcoffset() != timezone.utc.utcoffset(value):
        raise LegalStorefrontPublicIntentRateLimitDependencyError(
            "L8_9C0_STATE_INVALID"
        )
    return value.astimezone(timezone.utc)


def _digest(value: object) -> str:
    """Validate one lowercase SHA3-512 opaque request-subject digest."""
    if (
        not isinstance(value, str)
        or len(value) != 128
        or value != value.lower()
    ):
        _fail("L8_9C0_SUBJECT_DIGEST_INVALID")
    try:
        raw = bytes.fromhex(value)
    except ValueError as error:
        raise LegalStorefrontPublicIntentRateLimitError(
            "L8_9C0_SUBJECT_DIGEST_INVALID"
        ) from error
    if len(raw) != 64:
        _fail("L8_9C0_SUBJECT_DIGEST_INVALID")
    return value


def _namespace(value: object) -> str:
    """Validate one bounded rate-policy namespace."""
    if not isinstance(value, str):
        _fail("L8_9C0_NAMESPACE_INVALID")
    normalized = value.strip()
    if (
        not normalized
        or normalized != value
        or len(normalized) > 64
        or any(
            not (
                character.isalnum()
                or character in {"-", "_"}
            )
            for character in normalized
        )
    ):
        _fail("L8_9C0_NAMESPACE_INVALID")
    return normalized


def _window(value: object) -> timedelta:
    """Validate one bounded fixed-window duration."""
    if (
        not isinstance(value, timedelta)
        or value < timedelta(minutes=1)
        or value > timedelta(hours=24)
    ):
        _fail("L8_9C0_WINDOW_INVALID")
    return value


def _max_requests(value: object) -> int:
    """Validate one bounded positive request allowance."""
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 1 <= value <= 100
    ):
        _fail("L8_9C0_LIMIT_INVALID")
    return value


def _window_start(
    observed_at: datetime,
    window: timedelta,
) -> datetime:
    """Floor one UTC observation to its deterministic fixed-window boundary."""
    seconds = int(window.total_seconds())
    epoch_seconds = int(observed_at.timestamp())
    floored = epoch_seconds - (epoch_seconds % seconds)
    return datetime.fromtimestamp(
        floored,
        tz=timezone.utc,
    )


def _bucket_id(
    namespace: str,
    subject_digest: str,
    bucket_start: datetime,
) -> str:
    """Derive one opaque deterministic SHA3-512 Mongo bucket identity."""
    canonical = (
        f"{namespace}|{subject_digest}|{bucket_start.isoformat()}"
    )
    return hashlib.sha3_512(
        canonical.encode("utf-8")
    ).hexdigest()


def ensure_indexes(collection: Any) -> None:
    """Create deterministic rate lookup and ephemeral TTL indexes.

    TTL governs only abuse-control bucket cleanup. This function creates no
    Storefront intent, identity, tenant, Legal lifecycle or financial truth.
    """
    target = _target(collection)
    try:
        target.create_index(
            [
                ("namespace", ASCENDING),
                ("subject_digest", ASCENDING),
                ("bucket_start", ASCENDING),
            ],
            name=INDEX_LOOKUP,
        )
        target.create_index(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=0,
            name=INDEX_TTL,
        )
    except PyMongoError as error:
        raise LegalStorefrontPublicIntentRateLimitDependencyError(
            "L8_9C0_INDEX_CREATION_FAILED"
        ) from error


class LegalStorefrontPublicIntentRateLimit:
    """Mongo-backed pre-tenant public-intent request-density capability.

    The gate knows only an opaque SHA3-512 request-subject digest and UTC time.
    It has no email, IP, principal, tenant, Storefront-intent, Legal lifecycle,
    subscription, entitlement, billing, payment or settlement lookup authority.
    """

    __slots__ = (
        "_collection",
        "_window",
        "_max_requests",
        "_namespace",
    )

    def __init__(
        self,
        collection: Any,
        *,
        window: timedelta = DEFAULT_WINDOW,
        max_requests: int = DEFAULT_MAX_REQUESTS,
        namespace: str = DEFAULT_NAMESPACE,
    ) -> None:
        """Bind one collection and bounded fixed-window security policy."""
        self._collection = _target(collection)
        self._window = _window(window)
        self._max_requests = _max_requests(max_requests)
        self._namespace = _namespace(namespace)

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create L8-9C0 indexes outside request execution."""
        ensure_indexes(collection)

    def require_allowed(
        self,
        *,
        subject_digest: str,
        observed_at: datetime,
    ) -> None:
        """Atomically consume one public Storefront request allowance.

        The counter increments before the admission decision so blocked attempts
        remain durable abuse-control evidence for the current fixed window.

        ``subject_digest`` must already be a lowercase SHA3-512 digest derived
        by a later transport/admission owner. This gate never accepts raw email
        or network address material.

        Exceeding the configured budget raises a stable rate-limited error.
        Mongo/state failure raises a dependency error and never bypasses the
        gate. Successful allowance conveys request-density capability only.
        """
        digest = _digest(subject_digest)
        observed = _utc(observed_at)
        start = _window_start(
            observed,
            self._window,
        )
        expires_at = (
            start
            + self._window
            + timedelta(minutes=1)
        )
        bucket_id = _bucket_id(
            self._namespace,
            digest,
            start,
        )

        try:
            row = self._collection.find_one_and_update(
                {"_id": bucket_id},
                {
                    "$setOnInsert": {
                        "namespace": self._namespace,
                        "subject_digest": digest,
                        "bucket_start": start,
                        "expires_at": expires_at,
                    },
                    "$inc": {
                        "count": 1,
                    },
                },
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        except PyMongoError as error:
            raise LegalStorefrontPublicIntentRateLimitDependencyError(
                "L8_9C0_WRITE_FAILED"
            ) from error

        if not isinstance(row, dict):
            raise LegalStorefrontPublicIntentRateLimitDependencyError(
                "L8_9C0_STATE_INVALID"
            )

        persisted_start = _persisted_utc(
            row.get("bucket_start")
        )

        if (
            row.get("namespace") != self._namespace
            or row.get("subject_digest") != digest
            or persisted_start != start
        ):
            raise LegalStorefrontPublicIntentRateLimitDependencyError(
                "L8_9C0_STATE_MISMATCH"
            )

        count = row.get("count")
        if (
            isinstance(count, bool)
            or not isinstance(count, int)
            or count < 1
        ):
            raise LegalStorefrontPublicIntentRateLimitDependencyError(
                "L8_9C0_STATE_INVALID"
            )

        if count > self._max_requests:
            raise LegalStorefrontPublicIntentRateLimitedError(
                "L8_9C0_RATE_LIMITED"
            )


__all__ = [
    "COLLECTION",
    "DEFAULT_MAX_REQUESTS",
    "DEFAULT_NAMESPACE",
    "DEFAULT_WINDOW",
    "INDEX_LOOKUP",
    "INDEX_TTL",
    "VERSION",
    "LegalStorefrontPublicIntentRateLimit",
    "LegalStorefrontPublicIntentRateLimitDependencyError",
    "LegalStorefrontPublicIntentRateLimitError",
    "LegalStorefrontPublicIntentRateLimitedError",
    "ensure_indexes",
]


# ARTIFACT: legal_storefront_public_intent_rate_limit.py
# VERSION: v1.0.0-L8-9C0-LEGAL-STOREFRONT-PUBLIC-INTENT-RATE-LIMIT
# AUTHORITY BOUNDARY: durable pre-tenant request-density capability only; allowance is not Storefront intent acceptance, identity, tenant, Legal lifecycle, subscription, entitlement, billing or financial authority
# TENANT POSTURE: pre-tenant; tenant_id is neither accepted nor persisted
# TRANSACTION POSTURE: one atomic Mongo find/update per admission; no caller transaction is created or required
# RETENTION POSTURE: TTL applies only to ephemeral rate buckets, never durable Storefront intent evidence
# PRIVACY POSTURE: only opaque SHA3-512 subject digest is accepted/persisted; no raw email/IP/credential/token
# FAIL-CLOSED POSTURE: invalid configuration/input, Mongo failure or persisted-state drift never bypasses throttling
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
